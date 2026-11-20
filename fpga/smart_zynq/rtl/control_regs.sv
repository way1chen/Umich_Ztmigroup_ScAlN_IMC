module control_regs (
    input  logic        s_axi_aclk,
    input  logic        s_axi_aresetn,
    input  logic [7:0]  s_axi_awaddr,
    input  logic        s_axi_awvalid,
    output logic        s_axi_awready,
    input  logic [31:0] s_axi_wdata,
    input  logic [3:0]  s_axi_wstrb,
    input  logic        s_axi_wvalid,
    output logic        s_axi_wready,
    output logic [1:0]  s_axi_bresp,
    output logic        s_axi_bvalid,
    input  logic        s_axi_bready,
    input  logic [7:0]  s_axi_araddr,
    input  logic        s_axi_arvalid,
    output logic        s_axi_arready,
    output logic [31:0] s_axi_rdata,
    output logic [1:0]  s_axi_rresp,
    output logic        s_axi_rvalid,
    input  logic        s_axi_rready,
    output logic [31:0] spi_tx_data,
    output logic [15:0] spi_half_cycles,
    output logic        spi_start,
    input  logic        spi_busy, spi_done,
    input  logic [31:0] spi_rx_data,
    output logic        software_reset,
    output logic        inference_enable,
    output logic [31:0] active_reset_cycles,
    input  logic [31:0] spike_counts [0:3]
);
    localparam logic [7:0] ADDR_SCRATCH = 8'h08, ADDR_COMMAND = 8'h0C,
        ADDR_STATUS = 8'h10, ADDR_ERROR = 8'h14, ADDR_RESET_CYCLES = 8'h28,
        ADDR_DAC_FRAME = 8'h40, ADDR_SPI_HALF = 8'h44, ADDR_DAC_RX = 8'h88;
    localparam logic [31:0] CMD_DAC = 2, CMD_START = 7, CMD_STOP = 8, CMD_RESET = 9;
    localparam logic [1:0] ERR_NONE = 0, ERR_BUSY = 1, ERR_COMMAND = 2, ERR_CONFIG = 3;

    logic        aw_pending;
    logic [7:0]  awaddr_hold;
    logic        w_pending;
    logic [31:0] wdata_hold;
    logic [3:0]  wstrb_hold;
    logic        write_commit;
    logic [31:0] read_value;
    logic [31:0] scratch, tx_word, divider, reset_cycles, rx_word;
    logic [31:0] requested_command;
    logic done, busy;
    logic [1:0] error_code;

    function automatic logic [31:0] merge_wstrb(
        input logic [31:0] old_value,
        input logic [31:0] new_value,
        input logic [3:0]  strobe
    );
        logic [31:0] merged;
        merged = old_value;
        for (int byte_index = 0; byte_index < 4; byte_index++) begin
            if (strobe[byte_index])
                merged[8*byte_index +: 8] = new_value[8*byte_index +: 8];
        end
        return merged;
    endfunction

    // SPI engine shifts from bit 31. The DAC transaction contains 24 bits.
    assign spi_tx_data = {tx_word[23:0], 8'b0};
    assign spi_half_cycles = divider[15:0];
    assign busy = spi_busy || spi_start;
    assign requested_command = merge_wstrb(0, wdata_hold, wstrb_hold);

    assign s_axi_awready = !aw_pending && !s_axi_bvalid && !s_axi_rvalid;
    assign s_axi_wready  = !w_pending  && !s_axi_bvalid && !s_axi_rvalid;
    assign s_axi_arready = !aw_pending && !w_pending && !s_axi_bvalid &&
                           !s_axi_rvalid && !s_axi_awvalid && !s_axi_wvalid;
    assign s_axi_bresp = 2'b00;
    assign s_axi_rresp = 2'b00;
    assign write_commit = aw_pending && w_pending && !s_axi_bvalid;

    always_ff @(posedge s_axi_aclk) begin
        if (!s_axi_aresetn) begin
            aw_pending   <= 1'b0;
            awaddr_hold  <= 8'b0;
            w_pending    <= 1'b0;
            wdata_hold   <= 32'b0;
            wstrb_hold   <= 4'b0;
            s_axi_bvalid <= 1'b0;
            s_axi_rvalid <= 1'b0;
            s_axi_rdata  <= 32'b0;
        end else begin
            if (s_axi_awvalid && s_axi_awready) begin
                awaddr_hold <= s_axi_awaddr;
                aw_pending  <= 1'b1;
            end
            if (s_axi_wvalid && s_axi_wready) begin
                wdata_hold <= s_axi_wdata;
                wstrb_hold <= s_axi_wstrb;
                w_pending  <= 1'b1;
            end
            if (write_commit) begin
                aw_pending   <= 1'b0;
                w_pending    <= 1'b0;
                s_axi_bvalid <= 1'b1;
            end else if (s_axi_bvalid && s_axi_bready) begin
                s_axi_bvalid <= 1'b0;
            end
            if (s_axi_arvalid && s_axi_arready) begin
                s_axi_rdata  <= read_value;
                s_axi_rvalid <= 1'b1;
            end else if (s_axi_rvalid && s_axi_rready) begin
                s_axi_rvalid <= 1'b0;
            end
        end
    end

    always_ff @(posedge s_axi_aclk) begin
        if (!s_axi_aresetn) begin
            scratch <= 0;
            tx_word <= 0;
            divider <= 10;
            reset_cycles <= 0;
            active_reset_cycles <= 0;
            rx_word <= 0;
            spi_start <= 0;
            software_reset <= 0;
            inference_enable <= 0;
            done <= 0;
            error_code <= ERR_NONE;
        end else begin
            spi_start <= 0;
            software_reset <= 0;
            // Ignore completion from a transaction cancelled by software reset
            if (spi_done && !software_reset) begin
                rx_word <= spi_rx_data;
                done <= 1;
            end
            if (write_commit) begin
                case (awaddr_hold)
                    ADDR_SCRATCH: scratch <= merge_wstrb(scratch, wdata_hold, wstrb_hold);
                    ADDR_DAC_FRAME: tx_word <= merge_wstrb(tx_word, wdata_hold, wstrb_hold);
                    ADDR_SPI_HALF: divider <= merge_wstrb(divider, wdata_hold, wstrb_hold);
                    ADDR_RESET_CYCLES: reset_cycles <= merge_wstrb(reset_cycles, wdata_hold, wstrb_hold);
                    ADDR_COMMAND: if (requested_command != 0) begin
                        // Software reset leaves the AXI response intact.
                        if (requested_command == CMD_RESET) begin
                            scratch <= 0;
                            tx_word <= 0;
                            divider <= 10;
                            reset_cycles <= 0;
                            active_reset_cycles <= 0;
                            rx_word <= 0;
                            spi_start <= 0;
                            software_reset <= 1;
                            inference_enable <= 0;
                            done <= 1;
                            error_code <= ERR_NONE;
                        end else if (busy) error_code <= ERR_BUSY;
                        else begin
                            done <= 1;
                            error_code <= ERR_NONE;
                            case (requested_command)
                                CMD_DAC: if (tx_word[31:24] != 0 || divider < 5 || divider > 65535)
                                    error_code <= ERR_CONFIG;
                                else begin spi_start <= 1; done <= 0; end
                                CMD_START: if (inference_enable) error_code <= ERR_BUSY;
                                else if (reset_cycles == 0) error_code <= ERR_CONFIG;
                                else begin
                                    active_reset_cycles <= reset_cycles;
                                    inference_enable <= 1;
                                end
                                CMD_STOP: inference_enable <= 0;
                                default: error_code <= ERR_COMMAND;
                            endcase
                        end
                    end
                    default: ; // Read-only and unmapped writes have no effect.
                endcase
            end
        end
    end

    always_comb begin
        read_value = 0;
        case (s_axi_araddr)
            ADDR_SCRATCH: read_value = scratch;
            ADDR_STATUS: read_value = {28'b0, inference_enable, (error_code != ERR_NONE), done, busy};
            ADDR_ERROR: read_value = {30'b0, error_code};
            ADDR_RESET_CYCLES: read_value = reset_cycles;
            ADDR_DAC_FRAME: read_value = tx_word;
            ADDR_SPI_HALF: read_value = divider;
            8'h54: read_value = spike_counts[0];
            8'h58: read_value = spike_counts[1];
            8'h5C: read_value = spike_counts[2];
            8'h60: read_value = spike_counts[3];
            ADDR_DAC_RX: read_value = rx_word;
            default: ;
        endcase
    end
endmodule

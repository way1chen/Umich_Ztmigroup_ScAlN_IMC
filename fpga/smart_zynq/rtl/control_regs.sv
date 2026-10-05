// inside imc_top, handles all axi4-lite protocol.
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
    output logic [31:0] control,
    input  logic [31:0] status
);
    localparam logic [7:0] ADDR_CONTROL   = 8'h00;
    localparam logic [7:0] ADDR_STATUS    = 8'h04;
    localparam logic [7:0] ADDR_SCRATCH   = 8'h08;
    localparam logic [7:0] ADDR_DESIGN_ID = 8'hFC;
    // future register addresses

    logic        aw_pending;
    logic [7:0]  awaddr_hold;
    logic        w_pending;
    logic [31:0] wdata_hold;
    logic [3:0]  wstrb_hold;
    logic        write_commit;
    logic [31:0] read_value;
    logic [31:0] scratch;

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
    endfunction // helper function for valid data streaming, only make bytes defined by strobe legal

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
    end // standard axi4-lite

    always_ff @(posedge s_axi_aclk) begin
        if (!s_axi_aresetn) begin
            control <= 32'b0;
            scratch <= 32'b0;
        end else if (write_commit) begin
            // new register logic goes here
            case (awaddr_hold)
                ADDR_CONTROL: control <= merge_wstrb(control, wdata_hold, wstrb_hold);
                ADDR_SCRATCH: scratch <= merge_wstrb(scratch, wdata_hold, wstrb_hold);
                default: ; // Read-only and unmapped addresses ignore writes
            endcase
        end
    end

    always_comb begin
        read_value = 32'b0;
        // axi4-lite reads, add logic for new stuff
        case (s_axi_araddr)
            ADDR_CONTROL:   read_value = control;
            ADDR_STATUS:    read_value = status;
            ADDR_SCRATCH:   read_value = scratch;
            ADDR_DESIGN_ID: read_value = 32'h494D_4301; // "IMC", revision 1
            default:        read_value = 32'b0;
        endcase
    end
endmodule

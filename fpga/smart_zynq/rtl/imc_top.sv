module imc_top (
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
    output logic [3:0]  integrator_rst_n,
    input  logic [3:0]  spike,
    output logic        dac_cs_n, dac_sclk, dac_mosi,
    input  logic        dac_miso
);
    logic [31:0] spi_tx_data, spi_rx_data, active_reset_cycles;
    logic [15:0] spi_half_cycles;
    logic spi_start, spi_busy, spi_done, software_reset, inference_enable;
    logic [31:0] spike_counts [0:3];

    control_regs u_control_regs (.*);
    spi_master u_spi (
        .clk(s_axi_aclk), .resetn(s_axi_aresetn), .start(spi_start),
        .cancel(software_reset), .tx_data(spi_tx_data), .bit_count(6'd24),
        .half_cycles(spi_half_cycles), .miso(dac_miso), .cs_n(dac_cs_n),
        .sclk(dac_sclk), .mosi(dac_mosi), .busy(spi_busy), .done(spi_done),
        .rx_data(spi_rx_data)
    );

    for (genvar g = 0; g < 4; g++) begin : channels
        spike_channel u_channel (
            .clk(s_axi_aclk), .resetn(s_axi_aresetn), .clear(software_reset),
            .enable(inference_enable), .spike_async(spike[g]),
            .reset_cycles(active_reset_cycles), .count(spike_counts[g]),
            .integrator_rst_n(integrator_rst_n[g])
        );
    end
endmodule

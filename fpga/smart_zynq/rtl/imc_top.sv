// Portable IMC shell. Add your experiment hardware here later.
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
    input  logic        s_axi_rready
);
    logic [31:0] control;
    logic [31:0] status;

    assign status = control;
    // future experiment hardware connects to control and status here

    control_regs u_control_regs (.*);
endmodule

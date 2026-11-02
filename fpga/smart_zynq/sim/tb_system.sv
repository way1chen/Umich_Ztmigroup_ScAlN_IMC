`timescale 1ns/1ps
module tb_system;
    localparam logic [31:0] CMD_DAC=2, CMD_START=7, CMD_STOP=8, CMD_RESET=9;
    localparam logic [31:0] ERR_BUSY=1, ERR_COMMAND=2, ERR_CONFIG=3;
    logic s_axi_aclk = 0;
    always #5 s_axi_aclk = !s_axi_aclk;
    logic s_axi_aresetn = 0;
    logic [7:0] s_axi_awaddr = 0, s_axi_araddr = 0;
    logic s_axi_awvalid = 0, s_axi_wvalid = 0, s_axi_arvalid = 0;
    wire s_axi_awready, s_axi_wready, s_axi_arready;
    logic [31:0] s_axi_wdata = 0;
    logic [3:0] s_axi_wstrb = 0;
    wire [1:0] s_axi_bresp, s_axi_rresp;
    wire s_axi_bvalid, s_axi_rvalid;
    logic s_axi_bready = 0, s_axi_rready = 0;
    wire [31:0] s_axi_rdata;
    wire [3:0] integrator_rst_n;
    logic [3:0] spike = 0;
    wire dac_cs_n, dac_sclk, dac_mosi;
    logic dac_miso = 0;
    imc_axi_wrapper dut (.*);

    integer command_count = 0, dac_frames = 0, dac_bits = 0;
    integer half_cycles_expected = 10, frame_half_cycles;
    logic [23:0] miso_pattern = 24'hC3A55A, frame_miso;
    logic [31:0] dac_shift = 0, dac_last = 0;
    logic allow_partial = 0;
    time last_edge;
    logic [31:0] value;

    task automatic ticks(input integer n);
        repeat (n) @(negedge s_axi_aclk);
    endtask
    // Independent AW and W and deliberately exercise both orderings and B stalls (basic axi tests)
    task automatic write_reg(input logic [7:0] addr, input logic [31:0] data,
                             input logic [3:0] strobes = 15, input integer skew = 0);
        fork
            begin
                if (skew > 0) ticks(skew);
                @(negedge s_axi_aclk); s_axi_awaddr = addr; s_axi_awvalid = 1;
                do @(posedge s_axi_aclk); while (!s_axi_awready);
                @(negedge s_axi_aclk); s_axi_awvalid = 0;
            end
            begin
                if (skew < 0) ticks(-skew);
                @(negedge s_axi_aclk); s_axi_wdata = data; s_axi_wstrb = strobes; s_axi_wvalid = 1;
                do @(posedge s_axi_aclk); while (!s_axi_wready);
                @(negedge s_axi_aclk); s_axi_wvalid = 0;
            end
        join
        wait (s_axi_bvalid); ticks(2);
        if (!s_axi_bvalid || s_axi_bresp != 0) $fatal(1, "B response/backpressure");
        s_axi_bready = 1; ticks(1); s_axi_bready = 0;
    endtask
    task automatic read_reg(input logic [7:0] addr, output logic [31:0] data);
        @(negedge s_axi_aclk); s_axi_araddr = addr; s_axi_arvalid = 1;
        do @(posedge s_axi_aclk); while (!s_axi_arready);
        @(negedge s_axi_aclk); s_axi_arvalid = 0;
        wait (s_axi_rvalid); data = s_axi_rdata;
        ticks(2);
        if (!s_axi_rvalid || s_axi_rdata !== data || s_axi_rresp != 0) $fatal(1, "R response/backpressure");
        s_axi_rready = 1; ticks(1); s_axi_rready = 0;
    endtask
    task automatic expect_reg(input logic [7:0] addr, input logic [31:0] expected);
        logic [31:0] observed;
        read_reg(addr, observed);
        if (observed !== expected) $fatal(1, "register %h got %h expected %h", addr, observed, expected);
    endtask
    task automatic command(input logic [31:0] opcode);
        write_reg(8'h0C, opcode);
        command_count++;
    endtask
    task automatic wait_done(input logic [31:0] expected_error = 0);
        logic [31:0] result;
        integer attempts;
        attempts = 0;
        read_reg(8'h10, result);
        while (result[0] || !result[1]) begin
            if (attempts > 1000) $fatal(1, "command timeout status=%h", result);
            read_reg(8'h10, result); attempts++;
        end
        expect_reg(8'h14, expected_error);
    endtask
    task automatic output_events(input logic [3:0] mask);
        #2 spike = mask; ticks(10); spike = 0; ticks(15);
    endtask

    always @(negedge dac_cs_n) if (s_axi_aresetn) begin
        if (dac_sclk !== 0) $fatal(1, "DAC CPOL");
        dac_bits = 0; dac_shift = 0; last_edge = $time;
        frame_half_cycles = half_cycles_expected;
        frame_miso = miso_pattern; dac_miso = frame_miso[23];
    end
    always @(posedge dac_sclk) if (s_axi_aresetn) begin
        if (dac_cs_n || $time-last_edge != frame_half_cycles*10)
            $fatal(1, "SPI setup/low time");
        dac_shift = {dac_shift[30:0], dac_mosi}; dac_bits++;
        last_edge = $time;
    end
    always @(negedge dac_sclk) if (!dac_cs_n && s_axi_aresetn && !allow_partial) begin
        if ($time-last_edge != frame_half_cycles*10) $fatal(1, "SPI high time");
        last_edge = $time;
        if (dac_bits < 24) dac_miso = frame_miso[23-dac_bits];
    end
    always @(posedge dac_cs_n) if (s_axi_aresetn && dac_bits > 0 && !allow_partial) begin
        if (dac_bits != 24 || dac_sclk || $time-last_edge != frame_half_cycles*10)
            $fatal(1, "SPI frame/CS hold");
        dac_frames++; dac_last = dac_shift;
    end

    initial begin
        ticks(5); s_axi_aresetn = 1; ticks(3);
        if (!dac_cs_n || dac_sclk || integrator_rst_n != 0) $fatal(1, "reset outputs");
        expect_reg(8'h08, 0); expect_reg(8'h10, 0); expect_reg(8'h28, 0);
        expect_reg(8'h40, 0); expect_reg(8'h44, 10); expect_reg(8'h88, 0);
        write_reg(8'h08, 32'h11223344, 15, 3);
        write_reg(8'h08, 32'hAABBCCDD, 5, -3); expect_reg(8'h08, 32'h11BB33DD);
        write_reg(8'h08, 0, 0); expect_reg(8'h08, 32'h11BB33DD);
        write_reg(8'hFC, 32'hFFFFFFFF); expect_reg(8'hFC, 0);
        write_reg(8'h41, 32'hFFFFFFFF); expect_reg(8'h41, 0); expect_reg(8'h40, 0);
        write_reg(8'h10, 32'hFFFFFFFF); write_reg(8'h54, 32'hFFFFFFFF);
        expect_reg(8'h10, 0); expect_reg(8'h54, 0);
        write_reg(8'h0C, CMD_DAC, 0); write_reg(8'h0C, 0); expect_reg(8'h0C, 0);
        expect_reg(8'h10, 0);
        command(32'h100); wait_done(ERR_COMMAND);
        command(CMD_START); wait_done(ERR_CONFIG);


        write_reg(8'h40, 32'h308001); command(CMD_DAC);
        read_reg(8'h10, value); if (!value[0] || value[1]) $fatal(1, "SPI busy/done");
        write_reg(8'h40, 32'h338002); write_reg(8'h44, 5);
        command(CMD_DAC); expect_reg(8'h14, ERR_BUSY); expect_reg(8'h88, 0);
        wait_done(ERR_BUSY);
        if (dac_frames != 1 || dac_last != 32'h308001) $fatal(1, "SPI stable transaction");
        expect_reg(8'h88, 32'h00C3A55A);
        half_cycles_expected = 5; miso_pattern = 24'h800001;
        command(CMD_DAC); wait_done();
        if (dac_frames != 2 || dac_last != 32'h338002) $fatal(1, "back-to-back SPI");
        expect_reg(8'h88, 32'h00800001);
        repeat (3) expect_reg(8'h0C, 0);
        if (dac_frames != 2) $fatal(1, "read retrigger");
        write_reg(8'h44, 4); command(CMD_DAC); wait_done(ERR_CONFIG);
        write_reg(8'h44, 5); write_reg(8'h40, 32'h01000000);
        command(CMD_DAC); wait_done(ERR_CONFIG);
        if (dac_frames != 2) $fatal(1, "invalid SPI configuration launched");


        write_reg(8'h40, 32'h308001); command(CMD_DAC);
        @(posedge dac_cs_n); ticks(3); command(CMD_RESET); wait_done();
        expect_reg(8'h88, 0); expect_reg(8'h40, 0); expect_reg(8'h44, 10);
        half_cycles_expected = 10;

        write_reg(8'h28, 4); command(CMD_START); wait_done(); ticks(12);
        if (integrator_rst_n !== 15) $fatal(1, "start releases initial reset");
        #2 spike = 1; ticks(3);
        if (integrator_rst_n !== 14) $fatal(1, "independent channel 1 reset");
        spike = 3; ticks(3);
        if (integrator_rst_n[1] || integrator_rst_n[3:2] != 3) $fatal(1, "overlapping channel resets");
        ticks(20); expect_reg(8'h54, 1); expect_reg(8'h58, 1);
        spike = 0; ticks(6); output_events(15);
        expect_reg(8'h54, 2); expect_reg(8'h58, 2); expect_reg(8'h5C, 1); expect_reg(8'h60, 1);
        write_reg(8'h60, 999); expect_reg(8'h60, 1);
        write_reg(8'h28, 1000);
        fork
            output_events(8);
            begin : measure_reset
                time asserted_at;
                @(negedge integrator_rst_n[3]); asserted_at = $time;
                @(posedge integrator_rst_n[3]);
                if ($time-asserted_at != 40) $fatal(1, "reset duration changed during inference");
            end
        join
        expect_reg(8'h60, 2);
        command(CMD_START); wait_done(ERR_BUSY);
        command(CMD_STOP); wait_done();
        if (integrator_rst_n != 0) $fatal(1, "stop holds reset");
        output_events(15); expect_reg(8'h54, 2); expect_reg(8'h60, 2);
        write_reg(8'h28, 4); command(CMD_START); ticks(12);
        expect_reg(8'h54, 2); // Start preserves counts
        // RESET cancels SPI while completing its AXI response
        allow_partial = 1;
        write_reg(8'h44, 65535); write_reg(8'h40, 32'h338000);
        half_cycles_expected = 65535;
        command(CMD_DAC); spike = 15; command(CMD_RESET); wait_done();
        if (!dac_cs_n || dac_sclk || integrator_rst_n != 0) $fatal(1, "software reset outputs");
        expect_reg(8'h08, 0); expect_reg(8'h28, 0); expect_reg(8'h40, 0);
        expect_reg(8'h44, 10); expect_reg(8'h88, 0); expect_reg(8'h10, 2);
        for (int i=0; i<4; i++) expect_reg(8'(8'h54+4*i), 0);
        ticks(10); expect_reg(8'h54, 0);
        command(CMD_START); wait_done(ERR_CONFIG);
        spike = 0;

        // Hardware reset clears a pending AW without W, then permits reuse
        @(negedge s_axi_aclk); s_axi_awaddr = 8'h08; s_axi_awvalid = 1;
        do @(posedge s_axi_aclk); while (!s_axi_awready);
        @(negedge s_axi_aclk); s_axi_awvalid = 0; s_axi_aresetn = 0;
        ticks(3); s_axi_aresetn = 1; ticks(2); expect_reg(8'h08, 0); expect_reg(8'h10, 0);
        // Same for a pending W, plus an active SPI frame
        @(negedge s_axi_aclk); s_axi_wdata = 32'hDEADBEEF; s_axi_wstrb = 15; s_axi_wvalid = 1;
        do @(posedge s_axi_aclk); while (!s_axi_wready);
        @(negedge s_axi_aclk); s_axi_wvalid = 0; s_axi_aresetn = 0;
        ticks(3); s_axi_aresetn = 1; ticks(2); expect_reg(8'h08, 0);
        half_cycles_expected = 10;
        command(CMD_DAC); ticks(10); s_axi_aresetn = 0; ticks(3);
        s_axi_aresetn = 1; ticks(3);
        expect_reg(8'h10, 0); expect_reg(8'h54, 0); expect_reg(8'h44, 10);
        if (!dac_cs_n || dac_sclk || integrator_rst_n != 0) $fatal(1, "hardware reset outputs");
        $display("PASS tb_system: AXI/WSTRB/reset, SPI TX/RX/busy, four live counters and integrator resets; %0d commands, %0d complete DAC frames", command_count, dac_frames);
        $finish;
    end
    initial begin #1000000; $fatal(1, "system watchdog"); end
endmodule

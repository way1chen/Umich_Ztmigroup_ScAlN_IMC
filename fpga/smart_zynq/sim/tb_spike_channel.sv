`timescale 1ns/1ps
module tb_spike_channel;
    logic clk = 0;
    always #5 clk = !clk;
    logic resetn = 0, enable = 0, clear = 0, spike_async = 0;
    logic [31:0] reset_cycles = 4;
    wire [31:0] count;
    wire integrator_rst_n;
    spike_channel dut (.*);

    task automatic ticks(input integer n);
        repeat (n) @(negedge clk);
    endtask
    task automatic expect_count(input logic [31:0] n);
        if (count !== n) $fatal(1, "count %h expected %h", count, n);
    endtask
    task automatic pulse;
        #2 spike_async = 1; ticks(9); spike_async = 0; ticks(6);
    endtask
    initial begin
        ticks(3); resetn = 1; ticks(2);
        if (integrator_rst_n !== 0) $fatal(1, "disabled reset must be closed");
        enable = 1; ticks(10);
        if (!integrator_rst_n) $fatal(1, "initial reset not released");
        #2 spike_async = 1;
        @(posedge clk); #1;
        expect_count(0);
        if (!integrator_rst_n) $fatal(1, "first synchronizer stage leaked");
        @(posedge clk); #1;
        expect_count(0);
        if (!integrator_rst_n) $fatal(1, "reset before synchronized acceptance");
        @(posedge clk); #1;
        expect_count(1);
        if (integrator_rst_n) $fatal(1, "reset must assert with accepted event");
        repeat (3) begin
            @(posedge clk); #1;
            if (integrator_rst_n) $fatal(1, "short reset");
        end
        @(posedge clk); #1;
        if (!integrator_rst_n) $fatal(1, "reset must last four cycles");
        ticks(20); expect_count(1); // HIGH remains asserted after reset release.
        spike_async = 0; ticks(5); pulse(); expect_count(2);
        // Transitions during reset do not constitute independent events.
        #2 spike_async = 1; ticks(3); expect_count(3);
        spike_async = 0; ticks(1); spike_async = 1;
        ticks(15); expect_count(3);
        spike_async = 0; ticks(6); pulse(); expect_count(4);
        // Stop preserves counts and holds the integrator reset closed.
        enable = 0; ticks(1);
        if (integrator_rst_n) $fatal(1, "stop must hold reset");
        pulse(); expect_count(4);
        spike_async = 1; enable = 1; ticks(20); expect_count(4);
        spike_async = 0; ticks(6); pulse(); expect_count(5);
        // Clear coincides with the would-be acceptance edge and must win.
        #2 spike_async = 1;
        @(posedge clk); @(posedge clk); @(negedge clk); clear = 1;
        ticks(1); expect_count(0);
        if (integrator_rst_n) $fatal(1, "clear must assert reset");
        clear = 0; spike_async = 0; ticks(12); pulse(); expect_count(1);
        // Digital minimum: one reset clock. This is not an analog timing claim.
        enable = 0; reset_cycles = 1; ticks(2); enable = 1; ticks(8);
        #2 spike_async = 1; ticks(3);
        if (integrator_rst_n) $fatal(1, "one-cycle reset missing");
        ticks(1); if (!integrator_rst_n) $fatal(1, "one-cycle reset too long");
        spike_async = 0; ticks(6);
        // Preload only in this test to exercise the fixed 32-bit boundary.
        force dut.count = 32'hFFFFFFFE;
        ticks(1); release dut.count;
        pulse(); expect_count(32'hFFFFFFFF);
        pulse(); expect_count(32'hFFFFFFFF);
        resetn = 0; ticks(2); expect_count(0);
        if (integrator_rst_n) $fatal(1, "hardware reset");
        $display("PASS tb_spike_channel: CDC, single counting, reset width, re-arm, stop, clear priority, saturation");
        $finish;
    end
    initial begin #100000; $fatal(1, "watchdog"); end
endmodule

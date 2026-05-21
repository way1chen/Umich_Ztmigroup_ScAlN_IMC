`timescale 1ns/1ps

module timing_tb;

    // Use small value for simulation.
    // Change to 100000 if you want to test the real 2ms timing.
    parameter TEST_COUNT = 10;

    reg clk;
    reg reset;
    wire ready;

    integer i;
    integer errors;

    // Instantiate DUT
    timing #(
        .countMax(TEST_COUNT)
    ) dut (
        .clk(clk),
        .reset(reset),
        .ready(ready)
    );

    // 50 MHz clock: period = 20 ns
    initial begin
        clk = 0;
        forever #10 clk = ~clk;
    end

    initial begin
        errors = 0;

        // Optional waveform dump
        $dumpfile("timing_tb.vcd");
        $dumpvars(0, timing_tb);

        // Reset
        reset = 1;
        repeat (3) @(posedge clk);
        #1;
        reset = 0;

        $display("Reset released at time %0t", $time);

        // First ready pulse check
        for (i = 0; i < TEST_COUNT - 1; i = i + 1) begin
            @(posedge clk);
            #1;
            if (ready !== 0) begin
                $display("ERROR: ready went high too early at cycle %0d, time %0t", i, $time);
                errors = errors + 1;
            end
        end

        @(posedge clk);
        #1;
        if (ready !== 1) begin
            $display("ERROR: ready did not go high after %0d cycles at time %0t", TEST_COUNT, $time);
            errors = errors + 1;
        end else begin
            $display("PASS: ready went high after %0d cycles at time %0t", TEST_COUNT, $time);
        end

        // Check that ready is only high for one clock cycle
        @(posedge clk);
        #1;
        if (ready !== 0) begin
            $display("ERROR: ready stayed high for more than one cycle at time %0t", $time);
            errors = errors + 1;
        end else begin
            $display("PASS: ready pulse is one clock cycle wide");
        end

        // Second ready pulse check
        for (i = 0; i < TEST_COUNT - 1; i = i + 1) begin
            @(posedge clk);
            #1;
            if (ready !== 0) begin
                $display("ERROR: ready went high too early before second pulse at cycle %0d, time %0t", i, $time);
                errors = errors + 1;
            end
        end

        @(posedge clk);
        #1;
        if (ready !== 1) begin
            $display("ERROR: second ready pulse did not occur at time %0t", $time);
            errors = errors + 1;
        end else begin
            $display("PASS: second ready pulse occurred correctly at time %0t", $time);
        end

        if (errors == 0) begin
            $display("ALL TESTS PASSED");
        end else begin
            $display("TEST FAILED with %0d errors", errors);
        end

        $finish;
    end

endmodule
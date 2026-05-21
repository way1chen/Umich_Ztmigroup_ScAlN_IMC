`timescale 1ns/1ps

module testDAC;

    reg clk;
    reg reset;
    reg start;
    reg [1:0] dacSel;
    reg [15:0] dacCode;

    wire dacSyncN;
    wire dacSCLK;
    wire dacIn;
    wire busy;
    wire done;

    // Use a smaller sclkHalfPeriod for faster simulation.
    DAC #(
        .sclkHalfPeriod(3)
    ) dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .dacSel(dacSel),
        .dacCode(dacCode),
        .dacSyncN(dacSyncN),
        .dacSCLK(dacSCLK),
        .dacIn(dacIn),
        .busy(busy),
        .done(done)
    );

    // 100 MHz clock: 10 ns period
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    task pulseStart;
        input [1:0] sel;
        input [15:0] code;

        begin
            @(negedge clk);
            dacSel = sel;
            dacCode = code;
            start = 1'b1;

            @(negedge clk);
            start = 1'b0;

            wait(done == 1'b1);
            @(negedge clk);
        end
    endtask

    initial begin
        reset = 1'b1;
        start = 1'b0;
        dacSel = 2'd0;
        dacCode = 16'h0000;

        repeat (5) @(negedge clk);
        reset = 1'b0;

        repeat (5) @(negedge clk);

        // DAC A, midscale
        // Expected serial word: 24'h318000
        pulseStart(2'd0, 16'h8000);

        repeat (10) @(negedge clk);

        // DAC B, full scale
        // Expected serial word: 24'h38FFFF
        pulseStart(2'd1, 16'hFFFF);

        repeat (10) @(negedge clk);

        // Both DACs, zero scale
        // Expected serial word: 24'h390000
        pulseStart(2'd2, 16'h0000);

        repeat (50) @(negedge clk);

        $stop;
    end

endmodule
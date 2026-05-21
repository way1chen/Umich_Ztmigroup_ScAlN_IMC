`timescale 1ns/100ps

module testRowCol();

    reg  [1:0] col;
    reg        colEN;
    wire       cc1;
    wire       cc2;
    wire       cc3;

    reg  [4:0] row;
    reg        rowEN;
    reg        infEN;
    wire [15:0] rowOut;

    // Instantiate column selector
    colSel dut_col (
        .col(col),
        .enable(colEN),
        .cc1(cc1),
        .cc2(cc2),
        .cc3(cc3)
    );

    // Instantiate row selector
    rowSel dut_row (
        .row(row),
        .enable(rowEN),
        .inference(infEN),
        .out(rowOut)
    );

    initial begin
        $display("Starting row/column selector testbench...");
        $display("time\tcolEN col | cc1 cc2 cc3 || rowEN infEN row | rowOut");

        $monitor("%0t\t%b     %0d   |  %b   %b   %b  ||   %b     %b    %0d  | %h",
                 $time, colEN, col, cc1, cc2, cc3, rowEN, infEN, row, rowOut);

        // Initial safe state
        col   = 2'd0;
        colEN = 1'b0;

        row   = 5'd0;
        rowEN = 1'b0;
        infEN = 1'b0;
        #10;

        // -------------------------
        // Column select tests
        // -------------------------

        // Disabled: all CC outputs should be 0
        colEN = 1'b0;
        col   = 2'd1;
        #10;

        col   = 2'd2;
        #10;

        col   = 2'd3;
        #10;

        // Enabled column 1
        colEN = 1'b1;
        col   = 2'd1;
        #10;

        // Enabled column 2
        col = 2'd2;
        #10;

        // Enabled column 3
        col = 2'd3;
        #10;

        // Invalid column 0: all CC outputs should stay 0
        col = 2'd0;
        #10;

        // -------------------------
        // Row select tests
        // -------------------------

        // Disabled: all rows off = FFFF
        rowEN = 1'b0;
        infEN = 1'b0;
        row   = 5'd1;
        #10;

        // Enabled row 1: expect FFFE
        rowEN = 1'b1;
        infEN = 1'b0;
        row   = 5'd1;
        #10;

        // Enabled row 2: expect FFFD
        row = 5'd2;
        #10;

        // Enabled row 3: expect FFFB
        row = 5'd3;
        #10;

        // Enabled row 12: expect F7FF
        row = 5'd12;
        #10;

        // Invalid row 0: expect FFFF
        row = 5'd0;
        #10;

        // Invalid row 13: expect FFFF
        row = 5'd13;
        #10;

        // -------------------------
        // Inference mode test
        // -------------------------

        // Inference enabled: expect F000
        // rows 1-12 selected, rows 13-16 off
        rowEN = 1'b1;
        infEN = 1'b1;
        row   = 5'd5; // row should not matter during inference
        #10;

        // Disable again: expect FFFF
        rowEN = 1'b0;
        infEN = 1'b1;
        #10;

        $display("Testbench complete.");
        $finish;
    end

endmodule
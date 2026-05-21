`timescale 1ns/1ns

module testRead();

	reg CLK;
	reg timerReset;

	reg [31:0] value;
	reg [4:0]  row;
	reg [1:0]  col;

	reg colEn;
	reg rowEn;
	reg inference;

	wire [15:0] rowOut;
	wire cc1, cc2, cc3;

	// 1 ms = 1,000,000 ns with `timescale 1ns/1ps
	localparam integer NS_PER_MS = 1000000;

read dut (
		.clk(CLK),
		.timerReset(timerReset),
		.value(value),
		.row(row),
		.col(col),
		.colEn(colEn),
		.rowEn(rowEn),
		.inference(inference),
		.rowOut(rowOut),
		.cc1(cc1),
		.cc2(cc2),
		.cc3(cc3)
	);

// 50 MHz clock: 20 ns period
initial begin
		CLK = 0;
		forever #10 CLK = ~CLK;
	end

initial begin
		$monitor("t=%0t ns | reset=%b value=%0d row=%0d col=%0d | rowOut=%h cc1=%b cc2=%b cc3=%b",
		         $time, timerReset, value, row, col, rowOut, cc1, cc2, cc3);
	end

initial begin
		// Initialize read configuration
		value = 32'd3;      // 3 ms
		row = 5'd3;         // expect FFFB
		col = 2'd2;         // expect cc2 = 1
		rowEn = 1'b1;
		colEn = 1'b1;
		inference = 1'b0;

		// Clear expired register / restart timer
		timerReset = 1'b1;
		#100;
		timerReset = 1'b0;

		// Let outputs settle after reset
		#100;

		// ===============================
		// Check at 1 ms: should still be active
		// ===============================
		#(1 * NS_PER_MS);

		if (rowOut == 16'hFFFB && cc1 == 1'b0 && cc2 == 1'b1 && cc3 == 1'b0)
			$display("PASS at 1 ms: row 3 and column 2 active");
		else
			$display("FAIL at 1 ms: expected rowOut=FFFB cc1=0 cc2=1 cc3=0");

		// ===============================
		// Check at 2.9 ms total: still active
		// Already waited 1 ms, so wait 1.9 ms more
		// ===============================
		#1_900_000;

		if (rowOut == 16'hFFFB && cc1 == 1'b0 && cc2 == 1'b1 && cc3 == 1'b0)
			$display("PASS at 2.9 ms: row 3 and column 2 still active");
		else
			$display("FAIL at 2.9 ms: expected rowOut=FFFB cc1=0 cc2=1 cc3=0");

		// ===============================
		// Check at 3.2 ms total: should be off
		// Already waited 2.9 ms, so wait 0.3 ms more
		// ===============================
		#300_000;

		if (rowOut == 16'hFFFF && cc1 == 1'b0 && cc2 == 1'b0 && cc3 == 1'b0)
			$display("PASS at 3.2 ms: row and column outputs turned off");
		else
			$display("FAIL at 3.2 ms: expected rowOut=FFFF cc1=0 cc2=0 cc3=0");

		// ===============================
		// Check later: should stay off
		// ===============================
		#1_000_000;

		if (rowOut == 16'hFFFF && cc1 == 1'b0 && cc2 == 1'b0 && cc3 == 1'b0)
			$display("PASS later: outputs stayed off after timer expired");
		else
			$display("FAIL later: outputs turned back on unexpectedly");

		#100;
		$finish;
	end

endmodule
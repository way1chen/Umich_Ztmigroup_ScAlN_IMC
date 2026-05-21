module DAC(
    input clk,
    input reset,
    input start,
    input [1:0] dacSel,
    input [15:0] dacCode,
    output reg dacSyncN,
    output reg dacSCLK,
    output reg dacIn,
    output reg busy,
    output reg done
);

localparam idleState     = 3'd0;
localparam setupBitState = 3'd1;
localparam sclkLowState  = 3'd2;
localparam finishState   = 3'd3;

parameter sclkHalfPeriod = 25;

reg [2:0] state;
reg [23:0] shiftReg;
reg [4:0] bitIndex;
reg [15:0] divCount;
reg [3:0] dacAddr;

always @* begin
    case (dacSel)
        2'd0: dacAddr = 4'b0001; // DAC A
        2'd1: dacAddr = 4'b1000; // DAC B
        2'd2: dacAddr = 4'b1001; // both
        default: dacAddr = 4'b0001;
    endcase
end

always @(posedge clk) begin
    if (reset) begin
        state <= idleState;

        dacSyncN <= 1'b1;
        dacSCLK  <= 1'b1;
        dacIn    <= 1'b0;

        busy <= 1'b0;
        done <= 1'b0;

        shiftReg <= 24'd0;
        bitIndex <= 5'd0;
        divCount <= 16'd0;
    end else begin
        done <= 1'b0;

        case (state)

            idleState: begin
                dacSyncN <= 1'b1;
                dacSCLK  <= 1'b1;
                dacIn    <= 1'b0;
                busy     <= 1'b0;
                divCount <= 16'd0;

                if (start) begin
                    shiftReg <= {4'b0011, dacAddr, dacCode};
                    bitIndex <= 5'd23;

                    dacSyncN <= 1'b0;
                    busy     <= 1'b1;

                    state <= setupBitState;
                end
            end

            setupBitState: begin
                dacSCLK <= 1'b1;
                dacIn   <= shiftReg[bitIndex];

                if (divCount == sclkHalfPeriod - 1) begin
                    divCount <= 16'd0;
                    state    <= sclkLowState;
                end else begin
                    divCount <= divCount + 1'b1;
                end
            end

            sclkLowState: begin
                dacSCLK <= 1'b0;

                if (divCount == sclkHalfPeriod - 1) begin
                    divCount <= 16'd0;

                    if (bitIndex == 5'd0) begin
                        state <= finishState;
                    end else begin
                        bitIndex <= bitIndex - 1'b1;
                        state    <= setupBitState;
                    end
                end else begin
                    divCount <= divCount + 1'b1;
                end
            end

            finishState: begin
                dacSyncN <= 1'b1;
                dacSCLK  <= 1'b1;
                dacIn    <= 1'b0;

                busy <= 1'b0;
                done <= 1'b1;

                state <= idleState;
            end

            default: begin
                state <= idleState;
            end

        endcase
    end
end

endmodule
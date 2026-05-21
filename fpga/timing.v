// outputs ready pulse once every 2ms; tuned for 50mhz clk freq
module timing (
    input clk,
    input reset,
    input [31:0] ms, // time / clk pd
    output reg ready
);

wire [31:0] countMax;
reg [31:0] counter;

parameter clkFreq = 50000000; // 50 mhz
assign countMax = (clkFreq / 1000) * ms;

    always @(posedge clk) begin
        if (reset) begin
        counter <= 0;
        ready <= 0;
        end
        else begin
            if (counter == countMax - 1) begin
                counter <= 0;
                ready <= 1;
            end
            else begin
            counter <= counter + 1;
            ready <= 0;
        end
    end
end


endmodule
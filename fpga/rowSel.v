// Takes integer value in, outputs active low 16b output

module rowSel(
    input [4:0] row,     // supports 32 rows
    input enable,
    input inference,
    output reg [15:0] out // active low
);

always @* begin
    out = 16'hFFFF; 
    if (enable && row >= 5'd1 && row <= 5'd12 && !inference) begin // change when scaling up
        out = ~(16'h0001 << (row - 5'd1));
    end
    else if (enable && inference) begin
        out = 16'hF000; // 0-11 open
    end

end

endmodule
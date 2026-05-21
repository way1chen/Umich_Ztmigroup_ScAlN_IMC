// input decimal col#, output ccx -> 1

module colSel(
    input [1:0] col,
    input enable,
    output reg cc1,
    output reg cc2,
    output reg cc3
);

always @* begin
    cc1 = 1'b0;
    cc2 = 1'b0;
    cc3 = 1'b0;

    if (enable) begin 
        case (col)
        2'd1: cc1 = 1'b1;
        2'd2: cc2 = 1'b1;
        2'd3: cc3 = 1'b1;
        endcase
    end
end


endmodule

module read (
    input clk,
    input timerReset,
    input [31:0] value,
    input [4:0] row,
    input [1:0] col,
    input colEn,
    input rowEn,
    input inference,
    output [15:0] rowOut,
    output cc1, cc2, cc3
);

wire [15:0] rowOutInt;
wire cc1Int, cc2Int, cc3Int;

wire ready;
reg expired;

wire rowActive;
wire colActive;

assign rowActive = rowEn && !expired;
assign colActive = colEn && !expired;

timing timer (
    .clk(clk),
    .reset(timerReset),
    .ms(value),
    .ready(ready)
);

always @(posedge clk) begin
    if (timerReset) begin
        expired <= 1'b0;
    end
    else if (ready) begin
        expired <= 1'b1;
    end
end

rowSel rows (
    .row(row),
    .enable(rowActive),
    .inference(inference),
    .out(rowOutInt)
);

colSel cols (
    .col(col),
    .enable(colActive),
    .cc1(cc1Int),
    .cc2(cc2Int),
    .cc3(cc3Int)
);

assign rowOut = rowActive ? rowOutInt : 16'hFFFF;
assign cc1 = colActive ? cc1Int : 1'b0;
assign cc2 = colActive ? cc2Int : 1'b0;
assign cc3 = colActive ? cc3Int : 1'b0;

endmodule
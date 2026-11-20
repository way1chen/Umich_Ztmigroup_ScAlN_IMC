// Mode 0, MSB first. The parent validates the divider before start.
module spi_master (
    input  logic clk, resetn, start, cancel,
    input  logic [31:0] tx_data,
    input  logic [5:0] bit_count,
    input  logic [15:0] half_cycles,
    input  logic miso,
    output logic cs_n, sclk, mosi, busy, done,
    output logic [31:0] rx_data
);
    typedef enum logic [1:0] {IDLE, SHIFT, HOLD, GAP} state_t;
    state_t state;
    logic [30:0] tx_shift;
    logic [5:0] bits_left;
    logic [15:0] ticks, half_hold;

    always_ff @(posedge clk) begin
        if (!resetn || cancel) begin
            state <= IDLE;
            cs_n <= 1;
            sclk <= 0;
            mosi <= 0;
            busy <= 0;
            done <= 0;
            rx_data <= 0;
            tx_shift <= 0;
            bits_left <= 0;
            ticks <= 0;
            half_hold <= 0;
        end else begin
            done <= 0;
            case (state)
                IDLE: if (start) begin
                    tx_shift <= tx_data[30:0];
                    mosi <= tx_data[31];
                    bits_left <= bit_count;
                    half_hold <= half_cycles;
                    ticks <= half_cycles - 1'b1;
                    rx_data <= 0;
                    cs_n <= 0;
                    busy <= 1;
                    state <= SHIFT;
                end
                SHIFT: if (ticks != 0) ticks <= ticks - 1'b1;
                else begin
                    ticks <= half_hold - 1'b1;
                    sclk <= !sclk;
                    if (!sclk) begin
                        rx_data <= {rx_data[30:0], miso};
                    end else if (bits_left == 1) begin
                        state <= HOLD;
                    end else begin
                        bits_left <= bits_left - 1'b1;
                        tx_shift <= {tx_shift[29:0], 1'b0};
                        mosi <= tx_shift[30];
                    end
                end
                HOLD: if (ticks != 0) ticks <= ticks - 1'b1;
                else begin
                    cs_n <= 1;
                    mosi <= 0;
                    ticks <= half_hold - 1'b1;
                    state <= GAP;
                end
                GAP: if (ticks != 0) ticks <= ticks - 1'b1;
                else begin
                    busy <= 0;
                    done <= 1;
                    state <= IDLE;
                end
                default: state <= IDLE;
            endcase
        end
    end
endmodule

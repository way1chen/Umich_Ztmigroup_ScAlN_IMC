module spike_channel (
    input  logic clk, resetn, enable, clear,
    input  logic spike_async,
    input  logic [31:0] reset_cycles,
    output logic [31:0] count,
    output logic integrator_rst_n
);
    (* ASYNC_REG = "TRUE", SHREG_EXTRACT = "NO" *) logic spike_meta; // async set for no timing analysis problem
    (* ASYNC_REG = "TRUE", SHREG_EXTRACT = "NO" *) logic spike_sync;
    typedef enum logic [1:0] {DISABLED, RESETTING, WAIT_LOW, ARMED} state_t;
    state_t state;
    logic [31:0] remaining;

    always_ff @(posedge clk) begin
        if (!resetn || clear) begin
            spike_meta <= 0;
            spike_sync <= 0;
        end else begin
            spike_meta <= spike_async;
            spike_sync <= spike_meta;
        end
    end
    // Accept HIGH once after LOW; sampled capture can miss short pulses (unlikely given fpga clk likely much faster)
    always_ff @(posedge clk) begin
        if (!resetn || clear) begin
            count <= 0;
            state <= DISABLED;
            integrator_rst_n <= 0;
            remaining <= 0;
        end else if (!enable) begin
            state <= DISABLED;
            integrator_rst_n <= 0;
            remaining <= 0;
        end else begin
            case (state)
                DISABLED: begin
                    integrator_rst_n <= 0;
                    remaining <= reset_cycles - 1'b1;
                    state <= RESETTING;
                end
                RESETTING: if (remaining != 0) remaining <= remaining - 1'b1;
                else begin
                    integrator_rst_n <= 1;
                    state <= WAIT_LOW;
                end
                WAIT_LOW: if (!spike_sync) state <= ARMED;
                ARMED: if (spike_sync) begin
                    if (count != 32'hFFFF_FFFF) count <= count + 1'b1;
                    integrator_rst_n <= 0;
                    remaining <= reset_cycles - 1'b1;
                    state <= RESETTING;
                end
                default: state <= DISABLED;
            endcase
        end
    end
endmodule

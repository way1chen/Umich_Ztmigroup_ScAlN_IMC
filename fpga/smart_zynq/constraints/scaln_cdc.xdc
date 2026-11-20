# Cut only asynchronous arrivals; keep the synchronizer's second stage timed.
set_false_path -to [get_pins -of_objects [get_cells -hier -regexp {.*spike_meta_reg}] -filter {REF_PIN_NAME == D}]

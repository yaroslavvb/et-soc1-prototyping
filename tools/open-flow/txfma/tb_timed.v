// Q126(e): the timed pass. Replays the pins tb_gate.sv recorded into the same gate netlist,
// in plain Verilog-2001, so Icarus can run it and annotate the post-CTS SDF.
//
// Why a second bench. The glitch question needs a simulator with a delay model, and the only
// one here that has one is Icarus. Icarus cannot compile tb_gate.sv: core-et's rtl/inc headers
// use SystemVerilog "inside" expressions and assertion properties, and the vector types the
// bench builds come from those headers. Replaying a recorded waveform needs none of it.
//
//   +vectors=<file>   lines of "clock clock_txfma reset lane_valid in_data_hex", one per step
//   +sdf=<file>       annotate this SDF onto the unit (leave it out for the zero-delay run)
//   +vcd=<file>       where to write the waveform the toggle counter reads
`timescale 1ns/10ps
module tbt;
  reg        clock = 0, clk_g = 0, rst = 1, valid = 0;
  reg [166:0] din = 0;
  wire [37:0] out_data_res;
  wire        out_comp_res;

  txfma_top dut (.clock(clk_g), .reset(rst), .in_valid(valid), .in_data(din),
                 .trans_coefficients(58'b0),
                 .out_data_res(out_data_res), .out_comp_res(out_comp_res));

  integer f, n, steps;
  reg [1023:0] vectors, sdf, vcd;
  reg c, cg, r, v;
  reg [166:0] d;

  initial begin
    if (!$value$plusargs("vectors=%s", vectors)) begin $display("need +vectors"); $finish; end
    // Icarus asserts in vpi_scan when $sdf_annotate is given an explicit scope here, so the
    // call takes the file alone and annotates from this module down.
    if ($value$plusargs("sdf=%s", sdf)) $sdf_annotate(sdf);
    if (!$value$plusargs("vcd=%s", vcd)) vcd = "timed.vcd";
    $dumpfile(vcd);
    $dumpvars(0, tbt);
    f = $fopen(vectors, "r");
    if (f == 0) begin $display("cannot open %0s", vectors); $finish; end
    steps = 0;
    n = $fscanf(f, "%b %b %b %b %h\n", c, cg, r, v, d);
    while (n == 5) begin
      #1;
      clock = c; clk_g = cg; rst = r; valid = v; din = d;
      steps = steps + 1;
      n = $fscanf(f, "%b %b %b %b %h\n", c, cg, r, v, d);
    end
    #2;
    $display("TIMED steps=%0d", steps);
    $finish;
  end
endmodule

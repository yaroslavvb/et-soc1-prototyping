// One FMADD_PS through one txfma_top, traced, for flip_stages.py: run it twice with b differing in one bit and diff the two traces.
`include "soc.vh"
module tb;
  logic clock = 0, reset = 1;
  always #1 clock = ~clock;
  vpu_ctrl_sigs_t S;
  vpu_input_t in_data;
  vpu_output_t out_data;
  logic out_comp, in_valid = 0;
  txfma_top dut (.clock(clock), .reset(reset), .in_valid(in_valid), .in_data(in_data), .trans_coefficients('0),
                 .out_data_res(out_data), .out_comp_res(out_comp));
  logic [31:0] a = 32'h40490fdb, b = 32'h3f9e0651, c = 32'h42c80000;
  string dump;
  initial begin
    in_data = '0;
    S = '{`VPU_FCMD_MADD, `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`Y,`N, `N,`N,`N, `Y,`VPU_DTYPE_F32, `N,`N,`Y,`N,`N, `N,`N,`Y,`Y};
    void'($value$plusargs("a=%h", a));
    void'($value$plusargs("b=%h", b));
    void'($value$plusargs("c=%h", c));
    if (!$value$plusargs("dump=%s", dump)) $fatal(1, "need +dump");
    repeat (8) @(posedge clock);
    @(negedge clock) reset = 0;
    repeat (4) @(negedge clock);
    $dumpfile(dump);
    $dumpvars();
    @(negedge clock);
    in_valid = 1;
    in_data.sigs = S; in_data.in1 = a; in_data.in2 = b; in_data.in3 = c;
    @(negedge clock);
    in_valid = 0;
    in_data = '0;
    repeat (12) @(negedge clock);
    $display("RES %08x", out_data.data);
    $finish;
  end
  always @(posedge clock) if (!reset && out_data.data != 0) $display("OUT %08x", out_data.data);
endmodule

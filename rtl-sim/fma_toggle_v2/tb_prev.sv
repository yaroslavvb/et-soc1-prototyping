// Is use_prev_sigs what breaks MADD? One lane, three runs of the same ten operand triples: flag held off, flag on after the first
// valid, built with and without -fno-dfg by the caller. Public RTL only: vpu_ctrl.v:849-861 sets the flag only after a micro-op
// with all eight lanes valid and the same control word; txfma_c0.v:222 stops the local control flops from loading while it is set.
`include "soc.vh"
module tb;
  logic clock = 0, reset = 1;
  always #1 clock = ~clock;
  vpu_ctrl_sigs_t SIGS_FMUL, SIGS_FMADD;
  vpu_input_t in_data;
  vpu_output_t out_data;
  logic out_comp, in_valid = 0;
  txfma_top dut (.clock(clock), .reset(reset), .in_valid(in_valid), .in_data(in_data), .trans_coefficients('0),
                 .out_data_res(out_data), .out_comp_res(out_comp));
  logic [31:0] a[3] = '{32'h3FC00000, 32'h40000000, 32'h3F800000};
  logic [31:0] b[3] = '{32'h40200000, 32'h40400000, 32'h3F800000};
  logic [31:0] c[3] = '{32'h3F800000, 32'h3F800000, 32'h40A00000};
  int prevmode = 0;
  always @(posedge clock) if (!reset && out_data.data != 0) $display("prevmode=%0d out=%08x", prevmode, out_data.data);
  initial begin
    in_data = '0;
    SIGS_FMADD = '{`VPU_FCMD_MADD, `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`Y,`N, `N,`N,`N, `Y,`VPU_DTYPE_F32, `N,`N,`Y,`N,`N, `N,`N,`Y,`Y};
    void'($value$plusargs("prev=%d", prevmode));
    repeat (8) @(posedge clock);
    @(negedge clock) reset = 0;
    repeat (4) @(negedge clock);
    for (int i = 0; i < 3; i++) begin
      @(negedge clock);
      in_valid = 1;
      in_data = '0;
      in_data.use_prev_sigs = (prevmode != 0) && (i != 0);
      in_data.sigs = SIGS_FMADD;
      in_data.in1 = a[i]; in_data.in2 = b[i]; in_data.in3 = c[i];
    end
    @(negedge clock) in_valid = 0;
    repeat (10) @(negedge clock);
    $finish;
  end
endmodule

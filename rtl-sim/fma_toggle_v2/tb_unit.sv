// One txfma_top driven back to back with arbitrary (a, b, c) triples: the fused multiply-add's arithmetic alone,
// with no stream, no gate and no register file around it. fcheck_unit.py writes the triples and judges the results.
//
//   +vec=<hex file>   one "aaaaaaaa bbbbbbbb cccccccc" per line (three 32-bit words)
//   +n=<lines>        how many lines
//   +fmt=fp32|fp16    the dtype (vpu_uinst_decoder.v FMADD_PS / TFMA_PH_PS)
//   +mul=1            the MUL row instead of the MADD row (the C operand is not read)
//
// Prints "R <index> <result> <flags>" for every result, in order.
`include "soc.vh"
module tb;
  localparam int LAT = 7;
  logic clock = 0, reset = 1;
  always #1 clock = ~clock;
  vpu_ctrl_sigs_t sigs_row;
  vpu_input_t in_data;
  vpu_output_t out_data;
  logic out_comp;
  logic in_valid = 0;
  txfma_top dut (.clock(clock), .reset(reset), .in_valid(in_valid), .in_data(in_data),
                 .trans_coefficients('0), .out_data_res(out_data), .out_comp_res(out_comp));
  logic [31:0] vec [0:3000000];
  string vecf, fmt = "fp32";
  int n = 0, mul = 0, fd, got = 0;
  logic [LAT:0] vq = '0;
  logic [LAT:0][31:0] idxq = '0;
  int idx = 0;
  always @(posedge clock) begin
    if (vq[LAT]) begin
      $display("R %0d %08x %02x", idxq[LAT], out_data.data, out_data.exc);
      got++;
    end
  end
  initial begin
    in_data = '0;
    if (!$value$plusargs("vec=%s", vecf)) $fatal(1, "need +vec");
    void'($value$plusargs("n=%d", n));
    void'($value$plusargs("fmt=%s", fmt));
    void'($value$plusargs("mul=%d", mul));
    $readmemh(vecf, vec);
    begin
      logic [`VPU_CTRL_SIGS_DTYPE_SZ-1:0] dt;
      dt = (fmt == "fp16") ? `VPU_DTYPE_F16_F32 : `VPU_DTYPE_F32;
      sigs_row = mul != 0
        ? '{`VPU_FCMD_MUL,  `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`N,`N, `N,`N,`N, `Y,dt, `N,`N,`N,`N,`N, `N,`Y,`Y,`Y}
        : '{`VPU_FCMD_MADD, `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`Y,`N, `N,`N,`N, `Y,dt, `N,`N,`Y,`N,`N, `N,`N,`Y,`Y};
    end
    repeat (8) @(posedge clock);
    @(negedge clock) reset = 0;
    repeat (4) begin @(negedge clock); vq = {vq[LAT-1:0], 1'b0}; idxq = {idxq[LAT-1:0], 32'b0}; end
    for (int i = 0; i < n; i++) begin
      @(negedge clock);
      in_valid = 1;
      in_data = '0;
      in_data.use_prev_sigs = (i != 0);
      in_data.sigs = sigs_row;
      in_data.rm = (fmt == "fp16") ? RTZ : 3'b000;
      in_data.in1 = vec[3 * i];
      in_data.in2 = vec[3 * i + 1];
      in_data.in3 = vec[3 * i + 2];
      vq = {vq[LAT-1:0], 1'b1};
      idxq = {idxq[LAT-1:0], 32'(i)};
    end
    @(negedge clock);
    in_valid = 0;
    repeat (LAT + 2) begin vq = {vq[LAT-1:0], 1'b0}; idxq = {idxq[LAT-1:0], 32'b0}; @(negedge clock); end
    $display("DONE got=%0d of %0d", got, n);
    $finish;
  end
endmodule

// Switching activity of the ET-SoC-1 fused multiply-add unit under one TensorFMA32 data pattern.
//
// Eight copies of core-et's txfma_top (one per vector lane) are driven with the micro-op stream that the
// tensor state machine issues for a 16x16x16 TensorFMA32: for each B row k, for each A row i, two micro-ops
// (C columns 0-7 and 8-15), each computing c = a*b + c on 8 lanes (PRM 9.4; vpu_tensorfma.v). The lane valid
// is gated the way vpu_ctrl.v gates it: on an accumulate pass a lane whose A or B operand word is zero gets
// no valid. The unit's clock is gated as in vpu_lane.v: on while micro-ops arrive, off 7 cycles after the last.
//
//   +tiles=<hex file>  768 words: A[i][k] row-major, B[k][j] row-major, initial C[i][j] row-major
//   +ops=<n>           TensorFMA ops to measure (after +warm=<n> unmeasured ops)
//   +mul=<0|1>         1: the first op is a MUL pass (C = A*B), as in the first op of a launch
//   +gap=<n>           idle cycles between ops (the card measures 546 cycles per 512-micro-op op)
//   +check=<n>         print the first n micro-op results as "CHK a b c r" for checking against software
`include "soc.vh"
module tb;
  import "DPI-C" function void acct_reset();
  import "DPI-C" function longint acct_get(input int which);

  localparam int LANES = 8;
  localparam int LAT = `FMA_TB_LATENCY;  // cycles from a micro-op in EX to its result on out_data_res

  logic clock = 0, reset = 1;
  always #1 clock = ~clock;

  logic [31:0] mem [0:767];
  logic [31:0] A [16][16];
  logic [31:0] B [16][16];
  logic [31:0] C [16][16];

  // control words for the two micro-ops (vpu_decoder.v rows FMUL_PS and FMADD_PS)
  vpu_ctrl_sigs_t SIGS_FMUL, SIGS_FMADD;
  initial begin
    SIGS_FMUL  = '{`VPU_FCMD_MUL,  `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`N,`N, `N,`N,`N, `Y,`VPU_DTYPE_F32, `N,`N,`N,`N,`N, `N,`Y,`Y,`Y};
    SIGS_FMADD = '{`VPU_FCMD_MADD, `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`Y,`N, `N,`N,`N, `Y,`VPU_DTYPE_F32, `N,`N,`Y,`N,`N, `N,`N,`Y,`Y};
  end

  // the micro-op in EX
  logic                   uop_valid = 0, uop_mul = 0, uop_prev = 0;
  logic [31:0]            uop_a = 0;
  logic [LANES-1:0][31:0] uop_b = '0, uop_c = '0;
  logic [LANES-1:0]       lane_valid;
  vpu_input_t             in_data [LANES];
  vpu_output_t            out_data [LANES];
  logic [LANES-1:0]       out_comp;

  // lane clock gate (vpu_lane.v, VPU_EN_RCG_2)
  logic [6:0] clk_dly = '0;
  logic       clock_en, clock_txfma;
  assign clock_en = uop_valid | clk_dly[6];
  always @(posedge clock)
    if (reset) clk_dly <= '0;
    else if (uop_valid | clk_dly[6]) clk_dly <= uop_valid ? '1 : {clk_dly[5:0], 1'b0};
  et_clk_gate cgate_txfma (.enclk(clock_txfma), .en(clock_en | reset), .clk(clock), .te(1'b0));

  for (genvar l = 0; l < LANES; l++) begin : lane
    assign lane_valid[l] = uop_valid & (uop_mul | ((uop_a != 32'b0) & (uop_b[l] != 32'b0)));
    always_comb begin
      in_data[l] = '0;
      in_data[l].use_prev_sigs = uop_prev;
      in_data[l].sigs = uop_mul ? SIGS_FMUL : SIGS_FMADD;
      in_data[l].rm  = 3'b000;
      in_data[l].in1 = uop_a;
      in_data[l].in2 = uop_b[l];
      in_data[l].in3 = uop_c[l];
    end
    txfma_top txfma (.clock(clock_txfma), .reset(reset), .in_valid(lane_valid[l]), .in_data(in_data[l]),
                     .trans_coefficients('0), .out_data_res(out_data[l]), .out_comp_res(out_comp[l]));
  end

  // results return to C after LAT cycles
  logic [LAT:0][LANES-1:0] q_valid = '0;
  logic [LAT:0][3:0]       q_i = '0;
  logic [LAT:0]            q_h = '0;
  logic [LAT:0][31:0]      q_a = '0;
  logic [LAT:0][LANES-1:0][31:0] q_b = '0, q_c = '0;
  int unsigned checks = 0, check_max = 0;

  longint unsigned cycles = 0, clock_on = 0, lane_valid_cycles = 0, uop_cycles = 0;
  longint unsigned bus_toggles = 0;  // operand words presented to the lanes (in1, in2, in3), all 8 lanes
  logic [31:0] pa = 0; logic [LANES-1:0][31:0] pb = '0, pc = '0;
  bit measuring = 0;

  task automatic issue(input bit valid, input bit mul, input int k, input int i, input int h);
    @(negedge clock);
    uop_prev  = valid & uop_valid & (mul == uop_mul);
    uop_valid = valid;
    if (valid) begin
      uop_mul = mul;
      uop_a = A[i][k];
      for (int l = 0; l < LANES; l++) begin
        uop_b[l] = B[k][8 * h + l];
        uop_c[l] = C[i][8 * h + l];
      end
    end
    q_valid = {q_valid[LAT-1:0], valid ? lane_valid_now(mul) : 8'b0};
    q_i = {q_i[LAT-1:0], 4'(i)};
    q_h = {q_h[LAT-1:0], 1'(h)};
    q_a = {q_a[LAT-1:0], uop_a};
    q_b = {q_b[LAT-1:0], uop_b};
    q_c = {q_c[LAT-1:0], uop_c};
  endtask

  function automatic logic [LANES-1:0] lane_valid_now(input bit mul);
    for (int l = 0; l < LANES; l++) lane_valid_now[l] = mul | ((uop_a != 0) & (uop_b[l] != 0));
  endfunction

  // write-back and accounting, sampled just before the next micro-op is driven
  always @(posedge clock) begin
    for (int l = 0; l < LANES; l++)
      if (q_valid[LAT][l]) begin
        C[q_i[LAT]][8 * q_h[LAT] + l] <= out_data[l].data;
        if (checks < check_max) begin
          $display("CHK %08x %08x %08x %08x", q_a[LAT], q_b[LAT][l], q_c[LAT][l], out_data[l].data);
          checks++;
        end
      end
    if (measuring) begin
      cycles++;
      clock_on += longint'(clock_en);
      uop_cycles += longint'(uop_valid);
      lane_valid_cycles += longint'($countones(lane_valid));
      bus_toggles += longint'(LANES * $countones(uop_a ^ pa)) + longint'($countones(uop_b ^ pb)) + longint'($countones(uop_c ^ pc));
    end
    pa <= uop_a; pb <= uop_b; pc <= uop_c;
  end

  task automatic one_op(input bit mul, input int gap);
    for (int k = 0; k < 16; k++)
      for (int i = 0; i < 16; i++)
        for (int h = 0; h < 2; h++) issue(1, mul, k, i, h);
    for (int g = 0; g < gap; g++) issue(0, 0, 0, 0, 0);
  endtask

  string tiles;
  int n_ops = 4, n_warm = 1, first_mul = 0, gap = 34;
  initial begin
    if (!$value$plusargs("tiles=%s", tiles)) begin $display("need +tiles=<hex>"); $finish; end
    void'($value$plusargs("ops=%d", n_ops));
    void'($value$plusargs("warm=%d", n_warm));
    void'($value$plusargs("mul=%d", first_mul));
    void'($value$plusargs("gap=%d", gap));
    void'($value$plusargs("check=%d", check_max));
    $readmemh(tiles, mem);
    for (int i = 0; i < 16; i++)
      for (int j = 0; j < 16; j++) begin
        A[i][j] = mem[16 * i + j];
        B[i][j] = mem[256 + 16 * i + j];
        C[i][j] = mem[512 + 16 * i + j];
      end
    repeat (8) @(posedge clock);
    @(negedge clock) reset = 0;
    repeat (4) issue(0, 0, 0, 0, 0);
    for (int n = 0; n < n_warm; n++) one_op(first_mul != 0 && n == 0, gap);
    @(negedge clock);
    acct_reset();
    measuring = 1;
    for (int n = 0; n < n_ops; n++) one_op(first_mul != 0 && n_warm == 0 && n == 0, gap);
    @(negedge clock);
    measuring = 0;
    $display("ACCT {\"ops\":%0d,\"cycles\":%0d,\"clock_on\":%0d,\"uop_cycles\":%0d,\"lane_valid\":%0d,\"bus_toggles\":%0d,\"ff_clocked_bits\":%0d,\"ff_toggles\":%0d}",
             n_ops, cycles, clock_on, uop_cycles, lane_valid_cycles, bus_toggles, acct_get(0), acct_get(1));
    for (int i = 0; i < 16; i++)
      for (int j = 0; j < 16; j++) $display("C %0d %0d %08x", i, j, C[i][j]);
    $finish;
  end
endmodule

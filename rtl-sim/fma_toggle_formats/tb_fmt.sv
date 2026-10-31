// Switching activity of the ET-SoC-1 tensor multiply-add units for ONE data pattern in ONE number format.
//
// This is rtl-sim/fma_toggle's bench carried to the other two formats. It does NOT replace it: fp32 here
// reproduces that bench exactly (same unit, same stream, same gate) and is kept only as the cross-check.
//
//   +fmt=fp32   8 x txfma_top, dtype VPU_DTYPE_F32     (vpu_uinst_decoder.v FMUL_PS / FMADD_PS)
//   +fmt=fp16   8 x txfma_top, dtype VPU_DTYPE_F16_F32 (vpu_uinst_decoder.v:83-84 TMUL_PH_PS / TFMA_PH_PS)
//   +fmt=int8  16 x tima_top                           (vpu_lane_tima.v, 2 per lane x 8 lanes)
//
// The three streams are NOT the same (vpu_tensorfma.v):
//   fp32/fp16  for k in 0..15, for i in 0..15, for h in 0,1:   512 micro-ops of 8 lanes
//                A = Aword[i][k] broadcast to 8 lanes;  B of lane l = Bword[k][8*h+l]
//              (two half passes per A row because fma_exec_b_col walks 0,1 - vpu_tensorfma.v:718)
//   int8       for p in 0..15, for i in 0..15:                 256 micro-ops of 16 column slots
//                A = Aword[i][p] broadcast to 16 slots;  B of slot j = Bword[p][j]
//              (fma_exec_last_b_col is forced by req_int8 at vpu_tensorfma.v:412, and
//               fma_exec_b_col never advances, ":717-718 for INT8, we do all B cols at once")
//
// The zero gate follows vpu_ctrl.v:802-840, which is NOT the same width in the three formats:
//   fp32/fp16  lane l is gated when A word == 0 or B word of lane l == 0          (one 32-bit test)
//   int8       lane l (BOTH its TIMAs, i.e. column slots l and l+8) is gated when
//              A word == 0 or (B word of slot l == 0 AND B word of slot l+8 == 0) (two 32-bit tests ANDed:
//              ex_tensorb_zero_mask_tima0 & ex_tensorb_zero_mask_tima1, vpu_ctrl.v:808-818, with
//              ex_tima_tenb_raddr / raddr|1 the two 32-byte halves of one 64-byte B line, vpu_tensorfma.v:863)
//
//   +tiles=<hex file>  768 words: A then B then the initial C, each 16x16, row-major, one 32-bit word a cell
//   +ops=<n>           ops to measure (after +warm=<n> unmeasured ops)
//   +mul=<0|1>         1: the first op is a MUL / first_pass op (never zero-gated: vpu_ctrl.v:837 for
//                      txfma, :827's ex_tima_ren3 for TIMA)
//   +gap=<n>           idle cycles between ops (the card: 546 cycles per fp32/fp16 op, 318 per int8 op)
//   +nogate=1          run with the zero gate off, to price the gate itself
//   +check=<n>         print the first n micro-op results as "CHK a b c r"
`include "soc.vh"
module tb;
  import "DPI-C" function void acct_reset();
  import "DPI-C" function longint acct_get(input int which);

  localparam int LANES = 8;                 // VPU_LANE_NUM (minion_defines.vh:189)
  localparam int SLOTS = 16;                // LANES * VPU_NUM_TIMA (vpu_defines.vh:210), int8 only
  localparam int LAT   = `FMA_TB_LATENCY;

  logic clock = 0, reset = 1;
  always #1 clock = ~clock;

  logic [31:0] mem [0:767];
  logic [31:0] A [16][16];
  logic [31:0] B [16][16];
  logic [31:0] C [16][16];

  string fmt = "fp32";
  bit    is_int8 = 0, is_fp16 = 0, nogate = 0;
  int    N_SLOT = LANES;                    // column slots per micro-op: 8 for txfma, 16 for TIMA

  vpu_ctrl_sigs_t SIGS_MUL, SIGS_MADD;

  // the micro-op in EX
  logic                   uop_valid = 0, uop_mul = 0, uop_prev = 0;
  logic [31:0]            uop_a = 0;
  logic [SLOTS-1:0][31:0] uop_b = '0, uop_c = '0;
  logic [SLOTS-1:0]       slot_valid;       // the zero gate, per column slot
  logic [LANES-1:0]       lane_gate;        // ex_tensor_zero_mask, per lane (8 bits in every format)

  vpu_input_t  in_data [LANES];
  vpu_output_t out_data [LANES];
  logic [LANES-1:0] out_comp;
  logic [SLOTS-1:0][31:0] tima_out;

  // ---- the gate, exactly as vpu_ctrl.v:802-818 forms it -------------------------------------------
  // ex_tensor_zero_mask = A_zero | (tenB_zero[raddr] & tenB_zero[raddr|1]); for fp32/fp16
  // ex_tima_valid_unqual is 0, both terms address the same TENB row and the AND is a no-op.
  always_comb begin
    for (int l = 0; l < LANES; l++)
      lane_gate[l] = (uop_a == 32'b0) |
                     (is_int8 ? ((uop_b[l] == 32'b0) & (uop_b[l + 8] == 32'b0))
                              :  (uop_b[l] == 32'b0));
    for (int s = 0; s < SLOTS; s++)
      slot_valid[s] = uop_valid & (s < N_SLOT) &
                      (uop_mul | nogate | ~lane_gate[is_int8 ? (s % 8) : s]);
  end

  // ---- clock gate (vpu_lane.v:185-226 txfma, :213-215 + vpu_lane_tima.v cgate_tima) ---------------
  // Both are enabled by the op, not by the data: a gated lane still gets its clock.
  logic [6:0] clk_dly = '0;
  logic       clock_en, clock_unit;
  assign clock_en = uop_valid | clk_dly[6];
  always @(posedge clock)
    if (reset) clk_dly <= '0;
    else if (uop_valid | clk_dly[6]) clk_dly <= uop_valid ? '1 : {clk_dly[5:0], 1'b0};
  et_clk_gate cgate_unit (.enclk(clock_unit), .en(clock_en | reset), .clk(clock), .te(1'b0));

  // ---- fp32 / fp16: eight txfma_top ---------------------------------------------------------------
  for (genvar l = 0; l < LANES; l++) begin : lane
    always_comb begin
      in_data[l] = '0;
      in_data[l].use_prev_sigs = uop_prev;
      in_data[l].sigs = uop_mul ? SIGS_MUL : SIGS_MADD;
      in_data[l].rm  = is_fp16 ? RTZ : 3'b000;   // vpu_tensorfma.v:693: FP1632 ops only support RTZ
      in_data[l].in1 = uop_a;
      in_data[l].in2 = uop_b[l];
      in_data[l].in3 = uop_c[l];
    end
    txfma_top txfma (.clock(is_int8 ? 1'b0 : clock_unit), .reset(reset),
                     .in_valid(is_int8 ? 1'b0 : slot_valid[l]), .in_data(in_data[l]),
                     .trans_coefficients('0), .out_data_res(out_data[l]), .out_comp_res(out_comp[l]));
  end

  // ---- int8: sixteen tima_top (vpu_lane_tima.v: 2 per lane, 4 int8 multipliers each) --------------
  // f1_mul_en is ex_tima_valid[l][t] (vpu_lane.v:427), the per-slot gate; f2_tima_en is its pipelined
  // copy; f2_zap_opd3 = !f2_tima_ren3 zeroes the accumulator on a first pass (tima_top.v f3_in3_zapped).
  logic [SLOTS-1:0] slot_valid_f2 = '0;
  logic             mul_f2 = 0;
  always @(posedge clock) begin slot_valid_f2 <= slot_valid; mul_f2 <= uop_mul; end
  for (genvar s = 0; s < SLOTS; s++) begin : slot
    tima_top tima (.clock(is_int8 ? clock_unit : 1'b0),
                   .f1_mul_en(is_int8 & slot_valid[s]), .f1_in1(uop_a), .f1_in2(uop_b[s]),
                   .f1_in1_signed(1'b1), .f1_in2_signed(1'b1),
                   .f3_in3(uop_c[s]), .f2_zap_opd3(~mul_f2), .f2_tima_en(is_int8 & slot_valid_f2[s]),
                   .f3_out(tima_out[s]));
  end

  // ---- write-back and accounting ------------------------------------------------------------------
  logic [LAT:0][SLOTS-1:0] q_valid = '0;
  logic [LAT:0][3:0]       q_i = '0;
  logic [LAT:0]            q_h = '0;
  logic [LAT:0][31:0]      q_a = '0;
  logic [LAT:0][SLOTS-1:0][31:0] q_b = '0, q_c = '0;
  int unsigned checks = 0, check_max = 0;

  longint unsigned cycles = 0, clock_on = 0, slot_valid_cycles = 0, uop_cycles = 0;
  longint unsigned bus_ab = 0, bus_c = 0;   // operand bits presented, A counted once per column slot
  logic [31:0] pa = 0; logic [SLOTS-1:0][31:0] pb = '0, pc = '0;
  bit measuring = 0;
  int TIMA_LAT = 3;                         // tima_top: F1 -> F3

  task automatic issue(input bit valid, input bit mul, input int k, input int i, input int h);
    @(negedge clock);
    uop_prev  = valid & uop_valid & (mul == uop_mul);
    uop_valid = valid;
    if (valid) begin
      uop_mul = mul;
      uop_a = A[i][k];
      for (int s = 0; s < N_SLOT; s++) begin
        uop_b[s] = B[k][is_int8 ? s : (8 * h + s)];
        uop_c[s] = C[i][is_int8 ? s : (8 * h + s)];
      end
    end
    q_valid = {q_valid[LAT-1:0], valid ? slot_valid : {SLOTS{1'b0}}};
    q_i = {q_i[LAT-1:0], 4'(i)};
    q_h = {q_h[LAT-1:0], 1'(h)};
    q_a = {q_a[LAT-1:0], uop_a};
    q_b = {q_b[LAT-1:0], uop_b};
    q_c = {q_c[LAT-1:0], uop_c};
  endtask

  always @(posedge clock) begin
    for (int s = 0; s < SLOTS; s++) begin
      if (!is_int8 && s < LANES && q_valid[LAT][s]) begin
        C[q_i[LAT]][8 * q_h[LAT] + s] <= out_data[s].data;
        if (checks < check_max) begin
          $display("CHK %08x %08x %08x %08x", q_a[LAT], q_b[LAT][s], q_c[LAT][s], out_data[s].data);
          checks++;
        end
      end
      if (is_int8 && q_valid[TIMA_LAT][s]) begin
        C[q_i[TIMA_LAT]][s] <= tima_out[s];
        if (checks < check_max) begin
          $display("CHK %08x %08x %08x %08x", q_a[TIMA_LAT], q_b[TIMA_LAT][s], q_c[TIMA_LAT][s], tima_out[s]);
          checks++;
        end
      end
    end
    if (measuring) begin
      cycles++;
      clock_on += longint'(clock_en);
      uop_cycles += longint'(uop_valid);
      slot_valid_cycles += longint'($countones(slot_valid));
      // the convention of tools/claims-v3/hl/make_hl.py fma_flips and fma_toggle/tb.sv:131:
      // the one broadcast A word is counted once per column slot
      bus_ab += longint'(N_SLOT * $countones(uop_a ^ pa));
      for (int s = 0; s < N_SLOT; s++) begin
        bus_ab += longint'($countones(uop_b[s] ^ pb[s]));
        bus_c  += longint'($countones(uop_c[s] ^ pc[s]));
      end
    end
    pa <= uop_a; pb <= uop_b; pc <= uop_c;
  end

  task automatic one_op(input bit mul, input int gap);
    if (is_int8) begin
      for (int p = 0; p < 16; p++)
        for (int i = 0; i < 16; i++) issue(1, mul, p, i, 0);
    end else begin
      for (int k = 0; k < 16; k++)
        for (int i = 0; i < 16; i++)
          for (int h = 0; h < 2; h++) issue(1, mul, k, i, h);
    end
    for (int g = 0; g < gap; g++) issue(0, 0, 0, 0, 0);
  endtask

  task automatic report(input int n);
    $display("ACCT {\"fmt\":\"%s\",\"ops\":%0d,\"cycles\":%0d,\"clock_on\":%0d,\"uop_cycles\":%0d,\"slot_valid\":%0d,\"bus_ab\":%0d,\"bus_c\":%0d,\"ff_clocked_bits\":%0d,\"ff_toggles\":%0d,\"ff_present_bits\":%0d,\"slots\":%0d,\"nogate\":%0d}",
             fmt, n, cycles, clock_on, uop_cycles, slot_valid_cycles, bus_ab, bus_c,
             acct_get(0), acct_get(1), acct_get(2), N_SLOT, nogate);
  endtask

  string tiles;
  int n_ops = 4, n_warm = 1, first_mul = 0, gap = 34, ng = 0;
  initial begin
    if (!$value$plusargs("tiles=%s", tiles)) begin $display("need +tiles=<hex>"); $finish; end
    void'($value$plusargs("fmt=%s", fmt));
    is_int8 = (fmt == "int8");
    is_fp16 = (fmt == "fp16");
    N_SLOT  = is_int8 ? SLOTS : LANES;
    void'($value$plusargs("nogate=%d", ng)); nogate = (ng != 0);
    void'($value$plusargs("ops=%d", n_ops));
    void'($value$plusargs("warm=%d", n_warm));
    void'($value$plusargs("mul=%d", first_mul));
    void'($value$plusargs("gap=%d", gap));
    void'($value$plusargs("check=%d", check_max));
    // vpu_uinst_decoder.v:83-84 (fp16) and vpu_decoder.v:87,90 (fp32): the rows differ in dtype alone
    SIGS_MUL  = '{`VPU_FCMD_MUL,  `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`N,`N, `N,`N,`N, `Y,
                  is_fp16 ? `VPU_DTYPE_F16_F32 : `VPU_DTYPE_F32, `N,`N,`N,`N,`N, `N,`Y,`Y,`Y};
    SIGS_MADD = '{`VPU_FCMD_MADD, `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`Y,`N, `N,`N,`N, `Y,
                  is_fp16 ? `VPU_DTYPE_F16_F32 : `VPU_DTYPE_F32, `N,`N,`Y,`N,`N, `N,`N,`Y,`Y};
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
    report(n_ops);
    for (int i = 0; i < 16; i++)
      for (int j = 0; j < 16; j++) $display("C %0d %0d %08x", i, j, C[i][j]);
    $finish;
  end
endmodule

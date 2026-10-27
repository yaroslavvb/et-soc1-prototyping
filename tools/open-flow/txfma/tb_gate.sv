// Q126(e): the fma_toggle stimulus driven into a GATE-LEVEL txfma_top.
//
// Same micro-op stream as rtl-sim/fma_toggle/tb.sv (PRM 9.4, vpu_tensorfma.v): for each B row k,
// for each A row i, two micro-ops (C columns 0-7, then 8-15), each c = a*b + c; the lane valid is
// gated as vpu_ctrl.v gates it, and the unit's clock is gated as vpu_lane.v gates it. What differs:
//
//   - the unit under test is the synthesized netlist, not the RTL, so there is no DPI accounting
//     and no ff_acct.sv: activity is read out of the SAIF the simulator writes;
//   - FMA_TB_LANES (default 1) copies, not 8. The as-built census is per lane, so one lane is the
//     comparable unit and the netlist is large;
//   - $dumpon/$dumpoff bracket the measured ops, so warm-up and reset are outside the SAIF window.
//
//   +tiles=<hex>  768 words: A row-major, B row-major, the initial C
//   +ops=<n>      measured ops   +warm=<n> unmeasured ops before them
//   +mul=<0|1>    the first op is a MUL pass   +gap=<n> idle cycles between ops
//   +saif=<file>  where to write the activity file
`include "soc.vh"
`ifndef FMA_TB_LANES
 `define FMA_TB_LANES 1
`endif
module tb;
  localparam int LANES = `FMA_TB_LANES;
  localparam int LAT = `FMA_TB_LATENCY;

  logic clock = 0, reset = 1;
  always #1 clock = ~clock;

  logic [31:0] mem [0:767];
  logic [31:0] A [16][16];
  logic [31:0] B [16][16];
  logic [31:0] C [16][16];

  vpu_ctrl_sigs_t SIGS_FMUL, SIGS_FMADD;
  initial begin
    SIGS_FMUL  = '{`VPU_FCMD_MUL,  `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`N,`N, `N,`N,`N, `Y,`VPU_DTYPE_F32, `N,`N,`N,`N,`N, `N,`Y,`Y,`Y};
    SIGS_FMADD = '{`VPU_FCMD_MADD, `Y,`N,`N, `N,`N,`N,`N, `N,`N,`N,`N, `N,`Y,`N,`N,`N, `Y,`Y,`Y,`Y,`N, `N,`N,`N, `Y,`VPU_DTYPE_F32, `N,`N,`Y,`N,`N, `N,`N,`Y,`Y};
  end

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

  logic [LAT:0][LANES-1:0] q_valid = '0;
  logic [LAT:0][3:0]       q_i = '0;
  logic [LAT:0]            q_h = '0;
  logic [LAT:0][31:0]      q_a = '0;
  logic [LAT:0][LANES-1:0][31:0] q_b = '0, q_c = '0;
  int unsigned checks = 0, check_max = 0;
  longint unsigned cycles = 0, clock_on = 0, uop_cycles = 0, lane_valid_cycles = 0, bus_toggles = 0;
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
    q_valid = {q_valid[LAT-1:0], valid ? lane_valid_now(mul) : {LANES{1'b0}}};
    q_i = {q_i[LAT-1:0], 4'(i)};
    q_h = {q_h[LAT-1:0], 1'(h)};
    q_a = {q_a[LAT-1:0], uop_a};
    q_b = {q_b[LAT-1:0], uop_b};
    q_c = {q_c[LAT-1:0], uop_c};
  endtask

  function automatic logic [LANES-1:0] lane_valid_now(input bit mul);
    for (int l = 0; l < LANES; l++) lane_valid_now[l] = mul | ((uop_a != 0) & (uop_b[l] != 0));
  endfunction

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

  // +vectors=<file>: every time step of the unit's own pins, so a plain-Verilog bench can
  // replay exactly this stimulus into the same netlist with delays annotated (tb_timed.v).
  string vectors = "";
  integer vf = 0;
  always @(clock or clock_txfma or reset or lane_valid or in_data)
    if (vf) $fwrite(vf, "%b %b %b %b %h\n", clock, clock_txfma, reset, lane_valid[0], in_data[0]);

  string tiles, saif = "activity.saif";
  int n_ops = 1, n_warm = 1, first_mul = 0, gap = 34;
  initial begin
    if (!$value$plusargs("tiles=%s", tiles)) begin $display("need +tiles=<hex>"); $finish; end
    void'($value$plusargs("ops=%d", n_ops));
    void'($value$plusargs("warm=%d", n_warm));
    void'($value$plusargs("mul=%d", first_mul));
    void'($value$plusargs("gap=%d", gap));
    void'($value$plusargs("check=%d", check_max));
    void'($value$plusargs("saif=%s", saif));
    if ($value$plusargs("vectors=%s", vectors)) vf = $fopen(vectors, "w");
    $readmemh(tiles, mem);
    for (int i = 0; i < 16; i++)
      for (int j = 0; j < 16; j++) begin
        A[i][j] = mem[16 * i + j];
        B[i][j] = mem[256 + 16 * i + j];
        C[i][j] = mem[512 + 16 * i + j];
      end
`ifdef FMA_TB_SDF
    // the timed pass: annotate the post-CTS delays onto the one lane
    $sdf_annotate(`FMA_TB_SDF, lane[0].txfma);
`endif
    $dumpfile(saif);
    $dumpvars(0, tb);
    $dumpoff;
    repeat (8) @(posedge clock);
    @(negedge clock) reset = 0;
    repeat (4) issue(0, 0, 0, 0, 0);
    for (int n = 0; n < n_warm; n++) one_op(first_mul != 0 && n == 0, gap);
    @(negedge clock);
    measuring = 1;
    $dumpon;
    for (int n = 0; n < n_ops; n++) one_op(first_mul != 0 && n_warm == 0 && n == 0, gap);
    @(negedge clock);
    $dumpoff;
    measuring = 0;
    if (vf) $fclose(vf);
    $display("ACCT {\"lanes\":%0d,\"ops\":%0d,\"cycles\":%0d,\"clock_on\":%0d,\"uop_cycles\":%0d,\"lane_valid\":%0d,\"bus_toggles\":%0d}",
             LANES, n_ops, cycles, clock_on, uop_cycles, lane_valid_cycles, bus_toggles);
    $finish;
  end
endmodule

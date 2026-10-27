// Q129: the per-lane blocks a TensorFMA32 multiply-add exercises BESIDES txfma_top.
//
// Q128 section 3 says the bottom-up ledger "covers one lane's arithmetic while the board pays
// for the register file's read ports, the operand bus, the result path and leakage". This file
// is that scope, assembled out of the public core-et RTL (branch erbium, the sha
// tools/open-flow/txfma/setup.sh pins) so the open flow can synthesize, place, extract and
// price it the same way it priced txfma_top.
//
// WHAT A FP32 TensorFMA32 MULTIPLY-ADD TOUCHES, per lane, read out of the RTL:
//
//   operand A   vpu_tensora_rf  (rf_latch_1r_1w, 32 b x `VPU_TENA_SIZE = 2) - instantiated ONCE
//               in vpu_ctrl.v (l. 1806), so its read is shared by all `VPU_LANE_NUM = 8 lanes
//   operand B   vpu_tensorb_rf  (rf_latch_1r_1w, 32 b x `VPU_TENB_SIZE/2 = 4) - per lane AND per
//               TIMA, `VPU_NUM_TIMA = 2 of them in vpu_lane_tima.v (l. 42); vpu_lane.v l. 315
//               picks one of the two by raddr[0]
//   operand C   the accumulator. For FP32 it is the VPU register file, read on port 3 and
//               written back at F8 (vpu_lane.v l. 283 'vpu_rf rf', vpu_tensorfma.v's header:
//               "accumulates the result in the FP registers (C matrix)")
//   the bus     vpu_bypass.v - three 32-bit 13-way source muxes (EX), the F4..F8 pipeline of
//               vpu_output_t with per-stage clock enables, and the F8 result mux that selects
//               the TXFMA result and drives f8_wdata back at the register file
//   tmp         vpu_tensortmp_rf (rf_latch_1r_1w, 32 b x 8) - once in vpu_ctrl.v (l. 1832)
//   TENC        vpu_tensorc_rf is the TIMA (int8) accumulator, vpu_lane_tima.v l. 60. It is NOT
//               on the fp32 path; it is built and priced here so that claim is a measurement.
//
// TWO BLOCKS ARE COMPILED MACROS AND THE OPEN LIBRARY CANNOT BUILD THEM. Each gets a MODEL,
// named as such, built from core-et's OWN latch-array register files in rtl/libs/rf_latches:
//
//   vpu_64x32_3r2w_vpurf       -> q129_vpu_rf_model, rf_latch_3r_2w #(32, 64)
//   vpu_tensorc_rf_buffer_array-> q129_tenc_rf_model, rf_latch_1r_1w #(32, 16)
//
// A latch array is what the same RTL library offers for the same job at the same geometry, so
// this is a like-for-like substitution of an open implementation for a closed one - not a
// guess at the macro's own capacitance. Every number taken from these two blocks is labelled
// "model" in the results, and the README states the direction of the bias.
//
// SPDX-License-Identifier: Apache-2.0 (the core-et modules this file instantiates are
// Apache-2.0; the collision-bypass logic in q129_vpu_rf_model is copied from vpu_rf.v).

`include "soc.vh"

////////////////////////////////////////////////////////////////////////////////
// MODEL 1 - the VPU/FP register file: 64 entries x 32 bits, 3 read, 2 write.
// vpu_rf.v verbatim, with core-et's own rf_latch_3r_2w in place of the macro.
////////////////////////////////////////////////////////////////////////////////
module q129_vpu_rf_model (
  input  logic                           clock,
  input  logic [2:0]                     rd_en,
  input  logic [2:0]                     rd_thrid,
  input  logic [2:0][`FREG_ADDR_RANGE]   rd_addr,
  output logic [2:0][`VPU_DATA_S_SZ-1:0] rd_data,
  input  logic [1:0]                     wr_en,
  input  logic [1:0]                     wr_thrid,
  input  logic [1:0]                     wr_mask,
  input  logic [1:0][`FREG_ADDR_RANGE]   wr_addr,
  input  logic [1:0][`VPU_DATA_S_SZ-1:0] wr_data
);
  wire wr_en_masked_0 = wr_en[0] & wr_mask[0];
  wire wr_en_masked_1 = wr_en[1] & wr_mask[1];

  // --- vpu_rf.v: bypass on read/write collisions (verbatim) --------------------
  logic [2:0][`VPU_DATA_S_SZ-1:0] ram_rd_data;
  logic [2:0]                     bypass_sel;
  logic [2:0][`VPU_DATA_S_SZ-1:0] bypass_data;
  logic [2:0]                     match0, match1;
  logic [2:0]                     bypass_sel_next;
  logic [2:0][`VPU_DATA_S_SZ-1:0] bypass_data_next;

  always_comb begin
    for (int i = 0; i < 3; i++) begin
      match0[i] = wr_en_masked_0 && rd_en[i] && ({wr_thrid[0], wr_addr[0]} == {rd_thrid[i], rd_addr[i]});
      match1[i] = wr_en_masked_1 && rd_en[i] && ({wr_thrid[1], wr_addr[1]} == {rd_thrid[i], rd_addr[i]});
      bypass_sel_next[i]  = match1[i] | match0[i];
      bypass_data_next[i] = match1[i] ? wr_data[1] : wr_data[0];
    end
  end
  for (genvar i = 0; i < 3; i++) begin : bp
    `FF( clock, bypass_sel[i],  bypass_sel_next[i] )
    `FF( clock, bypass_data[i], bypass_data_next[i] )
  end
  assign rd_data[0] = bypass_sel[0] ? bypass_data[0] : ram_rd_data[0];
  assign rd_data[1] = bypass_sel[1] ? bypass_data[1] : ram_rd_data[1];
  assign rd_data[2] = bypass_sel[2] ? bypass_data[2] : ram_rd_data[2];

  // --- the array itself: the MODEL for vpu_64x32_3r2w_vpurf -------------------
  rf_latch_3r_2w #(
    .WIDTH           ( `VPU_DATA_S_SZ ),
    .ENTRIES         ( 64             ),
    .LEVEL2_CLK_GATE ( 1              )
  ) arr (
    .clk             ( clock          ),
    .test_en         ( 1'b0           ),
    .rd_addr_a       ( {rd_thrid[0], rd_addr[0]} ),
    .rd_data_a       ( ram_rd_data[0] ),
    .rd_addr_b       ( {rd_thrid[1], rd_addr[1]} ),
    .rd_data_b       ( ram_rd_data[1] ),
    .rd_addr_c       ( {rd_thrid[2], rd_addr[2]} ),
    .rd_data_c       ( ram_rd_data[2] ),
    .wr_en_a         ( wr_en_masked_0 ),
    .wr_addr_a       ( {wr_thrid[0], wr_addr[0]} ),
    .wr_data_a_en_1p ( wr_en_masked_0 ),
    .wr_data_a       ( wr_data[0]     ),
    .wr_en_b         ( wr_en_masked_1 ),
    .wr_addr_b       ( {wr_thrid[1], wr_addr[1]} ),
    .wr_data_b_en_1p ( wr_en_masked_1 ),
    .wr_data_b       ( wr_data[1]     )
  );
endmodule

////////////////////////////////////////////////////////////////////////////////
// MODEL 2 - the TIMA accumulator file, 16 x 32. vpu_tensorc_rf.v's ports, with
// core-et's own rf_latch_1r_1w in place of vpu_tensorc_rf_buffer_array.
////////////////////////////////////////////////////////////////////////////////
module q129_tenc_rf_model (
  input  logic                      clock,
  input  logic [`VPU_TENC_ADDR]     rd_addr,
  output logic [`VPU_DATA_S_SZ-1:0] rd_data,
  input  logic                      rd_en,
  input  logic                      wr_en,
  input  logic [`VPU_TENC_ADDR]     wr_addr,
  input  logic [`VPU_DATA_S_SZ-1:0] wr_data
);
  rf_latch_1r_1w #(
    .WIDTH           ( `VPU_DATA_S_SZ   ),
    .ENTRIES         ( `VPU_TENC_SIZE   ),
    .LEVEL2_CLK_GATE ( 1                )
  ) arr (
    .clk             ( clock   ),
    .test_en         ( 1'b0    ),
    .rd_addr_a       ( rd_addr ),
    .rd_data_a       ( rd_data ),
    .wr_en_a         ( wr_en   ),
    .wr_data_a_en_1p ( wr_en   ),
    .wr_addr_a       ( wr_addr ),
    .wr_data_a       ( wr_data )
  );
endmodule

////////////////////////////////////////////////////////////////////////////////
// MODEL 3 - the per-lane control pipeline that feeds vpu_bypass.
// vpu_lane.v carries {waddr[4:0], wmask, thread_id} and a clock enable down F3..F8
// and gates the lane's clocks (VPU_EN_RCG_2, l. 218-250) out of logic that lives in
// vpu_ctrl.v, shared across the 8 lanes. This module is the per-lane half of it,
// declared at exactly vpu_lane.v's widths with core-et's own `FF / `EN_FF macros and
// et_clk_gate. It is a MODEL: the index bits and enables are the real ones, the logic
// that computes them upstream is not in it.
////////////////////////////////////////////////////////////////////////////////
module q129_lane_ctl (
  input  logic                                clock,
  input  logic                                reset,
  input  logic                                uop_valid,
  input  logic [$clog2(`VPU_REGFILE_NUM)-1:0] ex_waddr,
  input  logic                                ex_wmask,
  input  logic                                ex_thread_id,
  output logic                                clock_txfma,
  output logic                                clock_bypass,
  output logic [$clog2(`VPU_REGFILE_NUM)-1:0] f3_waddr, f4_waddr, f5_waddr,
                                              f6_waddr, f7_waddr, f8_waddr,
  output logic                                f3_wmask, f4_wmask, f5_wmask,
                                              f6_wmask, f7_wmask, f8_wmask,
  output logic                                f3_thrid, f4_thrid, f5_thrid,
                                              f6_thrid, f7_thrid, f8_thrid,
  output logic                                f3_clk_en, f4_clk_en, f5_clk_en,
                                              f6_clk_en, f7_clk_en
);
  // the TXFMA_CLOCK_EN_DELAY = 7 clock-valid delay chain of vpu_tensorfma.v / vpu_lane.v
  logic [`TXFMA_CLOCK_EN_DELAY-1:0] dly;
  logic clock_en;
  assign clock_en = uop_valid | dly[`TXFMA_CLOCK_EN_DELAY-1];
  always @(posedge clock)
    if (reset) dly <= '0;
    else if (uop_valid | dly[`TXFMA_CLOCK_EN_DELAY-1])
      dly <= uop_valid ? '1 : {dly[`TXFMA_CLOCK_EN_DELAY-2:0], 1'b0};

  et_clk_gate cgate_txfma  (.enclk(clock_txfma),  .en(clock_en | reset), .clk(clock), .te(1'b0));
  et_clk_gate cgate_bypass (.enclk(clock_bypass), .en(clock_en | reset), .clk(clock), .te(1'b0));

  // the index / mask / thread pipeline. The first two stages are the EX->F3 pair the
  // lane registers before the bypass network sees them.
  logic [1:0] v;
  `FF (clock, v[0], uop_valid)
  `FF (clock, v[1], v[0])
  `FF (clock, f3_waddr, ex_waddr)   `FF (clock, f3_wmask, ex_wmask)   `FF (clock, f3_thrid, ex_thread_id)
  `FF (clock, f4_waddr, f3_waddr)   `FF (clock, f4_wmask, f3_wmask)   `FF (clock, f4_thrid, f3_thrid)
  `FF (clock, f5_waddr, f4_waddr)   `FF (clock, f5_wmask, f4_wmask)   `FF (clock, f5_thrid, f4_thrid)
  `FF (clock, f6_waddr, f5_waddr)   `FF (clock, f6_wmask, f5_wmask)   `FF (clock, f6_thrid, f5_thrid)
  `FF (clock, f7_waddr, f6_waddr)   `FF (clock, f7_wmask, f6_wmask)   `FF (clock, f7_thrid, f6_thrid)
  `FF (clock, f8_waddr, f7_waddr)   `FF (clock, f8_wmask, f7_wmask)   `FF (clock, f8_thrid, f7_thrid)
  assign f3_clk_en = v[1] | uop_valid;
  assign f4_clk_en = f3_clk_en;
  assign f5_clk_en = f3_clk_en;
  assign f6_clk_en = f3_clk_en;
  assign f7_clk_en = f3_clk_en;
endmodule

////////////////////////////////////////////////////////////////////////////////
// The scope top. One lane's worth of everything above, wired the way vpu_lane.v
// wires it for an FP32 TensorFMA32 micro-op: A out of TENA, B out of TENB, the
// accumulator out of the VPU RF's third read port, all three through vpu_bypass's
// source muxes to the FMA lane's in1/in2/in3, and the FMA result back through
// vpu_bypass's F8 mux into the RF's write port.
//
// The arithmetic itself is NOT here - txfma_top is priced in
// docs/reports/data/2026-10-26-open-netlist/. The bench presents the result the
// arithmetic would have produced at txfma_res.
////////////////////////////////////////////////////////////////////////////////
module q129_scope_top (
  input  logic                           clock,
  input  logic                           reset,
  // the micro-op, as vpu_ctrl.v issues it to the lane
  input  logic                           uop_valid,
  input  logic [$clog2(`VPU_TENA_SIZE)-1:0]       tena_raddr,
  input  logic [$clog2(`VPU_TENB_SIZE)-1:0]       tenb_raddr,
  input  logic [`FREG_ADDR_RANGE]        acc_raddr,     // the accumulator's register index
  input  logic                           acc_thrid,
  // loads: the scratchpad filling TENA / TENB, and the TMP / TENC writes
  input  logic                           tena_wen,
  input  logic [$clog2(`VPU_TENA_SIZE)-1:0]       tena_waddr,
  input  logic [`VPU_DATA_S_SZ-1:0]      tena_wdata,
  input  logic                           tenb_wen,
  input  logic [$clog2(`VPU_TENB_SIZE)-1:0]       tenb_waddr,
  input  logic [`VPU_DATA_S_SZ-1:0]      tenb_wdata,
  input  logic                           tentmp_wen,
  input  logic [`VPU_TENTMP_ADDR]        tentmp_waddr,
  input  logic [`VPU_TENTMP_ADDR]        tentmp_raddr,
  input  logic [`VPU_DATA_S_SZ-1:0]      tentmp_wdata,
  input  logic                           tenc_wen,
  input  logic                           tenc_ren,
  input  logic [`VPU_TENC_ADDR]          tenc_waddr,
  input  logic [`VPU_TENC_ADDR]          tenc_raddr,
  input  logic [`VPU_DATA_S_SZ-1:0]      tenc_wdata,
  // the arithmetic's answer, coming back at F8
  input  logic [`VPU_DATA_S_SZ-1:0]      txfma_res_data,
  input  logic [`VPU_FLAGS_SZ-1:0]       txfma_res_exc,
  // what reaches the FMA lane, and what the register file is written with
  output logic [`VPU_DATA_S_SZ-1:0]      op_in1, op_in2, op_in3,
  output logic [`VPU_DATA_S_SZ-1:0]      wb_data,
  output logic [`VPU_DATA_S_SZ-1:0]      tentmp_rdata,
  output logic [`VPU_DATA_S_SZ-1:0]      tenc_rdata
);

  localparam int WA = $clog2(`VPU_REGFILE_NUM);

  logic                                clock_txfma, clock_bypass;
  logic [WA-1:0] f3_waddr, f4_waddr, f5_waddr, f6_waddr, f7_waddr, f8_waddr;
  logic          f3_wmask, f4_wmask, f5_wmask, f6_wmask, f7_wmask, f8_wmask;
  logic          f3_thrid, f4_thrid, f5_thrid, f6_thrid, f7_thrid, f8_thrid;
  logic          f3_clk_en, f4_clk_en, f5_clk_en, f6_clk_en, f7_clk_en;

  q129_lane_ctl ctl (
    .clock(clock), .reset(reset), .uop_valid(uop_valid),
    .ex_waddr(acc_raddr[WA-1:0]), .ex_wmask(uop_valid), .ex_thread_id(acc_thrid),
    .clock_txfma(clock_txfma), .clock_bypass(clock_bypass),
    .f3_waddr(f3_waddr), .f4_waddr(f4_waddr), .f5_waddr(f5_waddr),
    .f6_waddr(f6_waddr), .f7_waddr(f7_waddr), .f8_waddr(f8_waddr),
    .f3_wmask(f3_wmask), .f4_wmask(f4_wmask), .f5_wmask(f5_wmask),
    .f6_wmask(f6_wmask), .f7_wmask(f7_wmask), .f8_wmask(f8_wmask),
    .f3_thrid(f3_thrid), .f4_thrid(f4_thrid), .f5_thrid(f5_thrid),
    .f6_thrid(f6_thrid), .f7_thrid(f7_thrid), .f8_thrid(f8_thrid),
    .f3_clk_en(f3_clk_en), .f4_clk_en(f4_clk_en), .f5_clk_en(f5_clk_en),
    .f6_clk_en(f6_clk_en), .f7_clk_en(f7_clk_en)
  );

  // ---- operand A: vpu_tensora_rf, the real core-et module --------------------
  logic [`VPU_DATA_S_SZ-1:0] tena_rdata;
  vpu_tensora_rf tena_rf (
    .clock(clock), .rd_addr(tena_raddr), .rd_data(tena_rdata),
    .wr_en(tena_wen), .wr_en_early(tena_wen), .wr_addr(tena_waddr), .wr_data(tena_wdata)
  );

  // ---- operand B: two vpu_tensorb_rf, one per TIMA, picked by raddr[0] -------
  logic [`VPU_NUM_TIMA-1:0][`VPU_DATA_S_SZ-1:0] tenb_rdata;
  for (genvar t = 0; t < `VPU_NUM_TIMA; t++) begin : LANE_TIMA
    logic wen_t;
    assign wen_t = tenb_wen & ((t == 0) ? ~tenb_waddr[0] : tenb_waddr[0]);
    vpu_tensorb_rf tenb_rf (
      .clock(clock),
      .rd_addr(tenb_raddr[$clog2(`VPU_TENB_SIZE)-1:1]),
      .rd_data(tenb_rdata[t]),
      .wr_en(wen_t), .wr_en_early(wen_t),
      .wr_addr(tenb_waddr[$clog2(`VPU_TENB_SIZE)-1:1]),
      .wr_data(tenb_wdata)
    );
  end
  // vpu_lane.v l. 315
  logic [`VPU_DATA_S_SZ-1:0] tenb_rdata_sel;
  assign tenb_rdata_sel = tenb_raddr[0] ? tenb_rdata[1] : tenb_rdata[0];

  // ---- the TMP file (vpu_ctrl.v l. 1832) and the TIMA accumulator ------------
  vpu_tensortmp_rf tentmp_rf (
    .clock(clock), .rd_addr(tentmp_raddr), .rd_data(tentmp_rdata),
    .wr_en(tentmp_wen), .wr_en_early(tentmp_wen),
    .wr_addr(tentmp_waddr), .wr_data(tentmp_wdata)
  );
  q129_tenc_rf_model tenc_rf (
    .clock(clock), .rd_addr(tenc_raddr), .rd_data(tenc_rdata), .rd_en(tenc_ren),
    .wr_en(tenc_wen), .wr_addr(tenc_waddr), .wr_data(tenc_wdata)
  );

  // ---- the accumulator: the VPU register file -------------------------------
  logic [2:0]                     rf_rd_en;
  logic [2:0]                     rf_rd_thrid;
  logic [2:0][`FREG_ADDR_RANGE]   rf_rd_addr;
  logic [2:0][`VPU_DATA_S_SZ-1:0] rf_rd_data;
  logic [1:0]                     rf_wr_en, rf_wr_thrid, rf_wr_mask;
  logic [1:0][`FREG_ADDR_RANGE]   rf_wr_addr;
  logic [1:0][`VPU_DATA_S_SZ-1:0] rf_wr_data;

  // Sources 1 and 2 come from TENA / TENB, so only the third read port carries the
  // accumulator; vpu_ctrl.v still presents all three addresses, which is what the
  // read-port and index energy below is measured against.
  assign rf_rd_en    = {uop_valid, uop_valid, uop_valid};
  assign rf_rd_thrid = {acc_thrid, acc_thrid, acc_thrid};
  assign rf_rd_addr  = {acc_raddr, acc_raddr, acc_raddr};
  assign rf_wr_en    = {1'b0, f8_wmask};
  assign rf_wr_thrid = {1'b0, f8_thrid};
  assign rf_wr_mask  = {1'b0, f8_wmask};
  assign rf_wr_addr  = {{`FREG_ADDR_SIZE{1'b0}}, {{(`FREG_ADDR_SIZE-WA){1'b0}}, f8_waddr}};
  assign rf_wr_data  = {{`VPU_DATA_S_SZ{1'b0}}, wb_data};

  q129_vpu_rf_model vrf (
    .clock(clock), .rd_en(rf_rd_en), .rd_thrid(rf_rd_thrid), .rd_addr(rf_rd_addr),
    .rd_data(rf_rd_data),
    .wr_en(rf_wr_en), .wr_thrid(rf_wr_thrid), .wr_mask(rf_wr_mask),
    .wr_addr(rf_wr_addr), .wr_data(rf_wr_data)
  );

  // ---- the operand bus and the result path: vpu_bypass, the real module ------
  vpu_input_t            ex_req_lane, ex_req;
  vpu_output_t           f3_sh_sw_bits, f8_txfma_res;
  vpu_bypass_force_ctrl  force_ctrl;
  logic [`VPU_FLAGS_SZ-1:0] f8_wflags_o;
  logic [`VPU_DATA_S_SZ-1:0] f8_sh_sw_wdata_o;
  logic                      f3_maskop_bit_o;

  always_comb begin
    ex_req_lane                = '0;
    ex_req_lane.sigs.fma       = 1'b1;
    ex_req_lane.sigs.txfma     = 1'b1;
    ex_req_lane.sigs.vector    = 1'b1;
    ex_req_lane.sigs.dtype     = `VPU_DTYPE_F32;
    ex_req_lane.rm             = 3'b000;
    force_ctrl                 = '0;
    f3_sh_sw_bits              = '0;
    f8_txfma_res.data          = txfma_res_data;
    f8_txfma_res.exc           = txfma_res_exc;
  end

  vpu_bypass bypass (
    .lane_id                   ( '0                 ),
    .clock                     ( clock_bypass       ),
    .ex_rf_raddr               ( rf_rd_addr         ),
    .ex_regfile_thread_id      ( rf_rd_thrid        ),
    .ex_rf_rdata               ( rf_rd_data         ),
    .ex_req_lane               ( ex_req_lane        ),
    .ex_fromint_data           ( '0                 ),
    .ex_tena_rf_rdata          ( tena_rdata         ),
    .ex_tenb_rf_rdata          ( tenb_rdata_sel     ),
    .ex_tena_regfile_bypass_en ( uop_valid          ),
    .ex_tenb_regfile_bypass_en ( uop_valid          ),
    .ex_bypass_force_ctrl      ( force_ctrl         ),
    .f3_sh_sw_bits             ( f3_sh_sw_bits      ),
    .f3_regfile_waddr          ( f3_waddr           ),
    .f3_regfile_wmask          ( f3_wmask           ),
    .f3_thread_id              ( f3_thrid           ),
    .f3_bypass_clk_en          ( f3_clk_en          ),
    .f3_data_vector            ( 1'b1               ),
    .f4_regfile_waddr          ( f4_waddr           ),
    .f4_regfile_wmask          ( f4_wmask           ),
    .f4_thread_id              ( f4_thrid           ),
    .f4_bypass_clk_en          ( f4_clk_en          ),
    .f4_regfile_waddr_l        ( f4_waddr           ),
    .f4_regfile_wmask_l        ( {1'b0, 1'b0}       ),
    .f4_regfile_thrid_l        ( f4_thrid           ),
    .f4_regfile_wdata_l        ( '0                 ),
    .f5_regfile_waddr          ( f5_waddr           ),
    .f5_regfile_wmask          ( f5_wmask           ),
    .f5_thread_id              ( f5_thrid           ),
    .f5_bypass_clk_en          ( f5_clk_en          ),
    .f6_regfile_waddr          ( f6_waddr           ),
    .f6_regfile_wmask          ( f6_wmask           ),
    .f6_thread_id              ( f6_thrid           ),
    .f6_bypass_clk_en          ( f6_clk_en          ),
    .f7_regfile_waddr          ( f7_waddr           ),
    .f7_regfile_wmask          ( f7_wmask           ),
    .f7_thread_id              ( f7_thrid           ),
    .f7_bypass_clk_en          ( f7_clk_en          ),
    .f8_regfile_waddr          ( f8_waddr           ),
    .f8_regfile_wmask          ( f8_wmask           ),
    .f8_thread_id              ( f8_thrid           ),
    .f8_txfma_res              ( f8_txfma_res       ),
    .f8_data_vector            ( 1'b1               ),
    .f8_txfma_op               ( 1'b1               ),
    .ex_req                    ( ex_req             ),
    .f3_maskop_bit             ( f3_maskop_bit_o    ),
    .f8_wflags                 ( f8_wflags_o        ),
    .f8_wdata                  ( wb_data            ),
    .f8_sh_sw_wdata            ( f8_sh_sw_wdata_o   )
  );

  assign op_in1 = ex_req.in1;
  assign op_in2 = ex_req.in2;
  assign op_in3 = ex_req.in3;

endmodule

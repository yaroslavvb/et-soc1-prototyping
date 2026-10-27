// Behavioural stand-ins for the three ASAP7 sequential cells the scope netlist uses, on the
// pattern of tools/open-flow/txfma/asap7_seq_behav.v. ASAP7's own models build all three out of
// the altos_latch / altos_dff sequential UDPs, which the zero-delay simulator refuses
// ("Unsupported: Blocking and non-blocking assignments to potentially overlapping bits of same
// packed variable"). A comment line here must not begin with the simulator's own name, or it is
// read as a pragma. The functions are copied from those models:
//
//   DLLx1:   not (int_clk, CLK); altos_latch (IQ, notifier, int_clk, D) -> transparent while CLK LOW
//   DHLx1:                       altos_latch (IQ, notifier, CLK, D)     -> transparent while CLK HIGH
//   DFFHQx4: altos_dff (IQ, notifier, CLK, D, ...)                      -> rising-edge flip-flop
//
// DHLx1 is the cell the latch arrays in rtl/libs/rf_latches map to (3,143 of them in this
// netlist): rf_latch_1r_1w / rf_latch_3r_2w hold each entry in `always @(gated_clk or data) if
// (gated_clk) ...`, which is an active-high latch behind a per-entry clock gate.
//
// Only for the zero-delay pass.
`timescale 1ns/10ps
`celldefine
module DLLx1_ASAP7_75t_R (Q, D, CLK);
  output reg Q;
  input D, CLK;
  initial Q = 1'b0;
  always @* if (CLK === 1'b0) Q = D;
endmodule
`endcelldefine

`celldefine
module DHLx1_ASAP7_75t_R (Q, D, CLK);
  output reg Q;
  input D, CLK;
  initial Q = 1'b0;
  always @* if (CLK === 1'b1) Q = D;
endmodule
`endcelldefine

`celldefine
module DFFHQx4_ASAP7_75t_R (Q, D, CLK);
  output reg Q;
  input D, CLK;
  initial Q = 1'b0;
  always @(posedge CLK) Q <= D;
endmodule
`endcelldefine

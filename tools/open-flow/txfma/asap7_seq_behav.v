// Behavioural stand-ins for the only two ASAP7 sequential cells this netlist uses.
//
// ASAP7's own models build both out of the `altos_latch` / `altos_dff` sequential UDPs, which
// the zero-delay simulator refuses ("Unsupported: Blocking and non-blocking assignments to
// potentially overlapping bits of same packed variable"). A comment line here must not begin
// with the simulator's own name, or it is read as a pragma. The functions are copied from
// those models:
//
//   DLLx1:   not (int_clk, CLK); altos_latch (IQ, notifier, int_clk, D)  -> transparent while CLK is LOW
//   DFFHQx4: altos_dff (IQ, notifier, CLK, D, ...)                       -> rising-edge D flip-flop
//
// Only for the zero-delay pass. The timed pass uses ASAP7's own models with SDF, under Icarus,
// which handles the UDPs and the specify blocks these models carry.
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
module DFFHQx4_ASAP7_75t_R (Q, D, CLK);
  output reg Q;
  input D, CLK;
  initial Q = 1'b0;
  always @(posedge CLK) Q <= D;
endmodule
`endcelldefine

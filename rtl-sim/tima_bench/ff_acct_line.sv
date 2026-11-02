// Q136(c): rtl-sim/fma_toggle_v2/ff_acct.sv with two changes. It includes macros_line.vh (the macro registers report their source
// line too), and its package declares acct_ff_l beside acct_ff_u. The four libs/registers modules below are ff_acct.sv's, unchanged.
`include "macros_line.vh"
package acct_pkg;
  import "DPI-C" function void acct_ff_u(input string where, input int width, input int toggles, input int enabled);
  import "DPI-C" function void acct_ff_l(input string where, input int line, input int width, input int toggles, input int enabled);
endpackage

module ff #(parameter width=32) (input clock, input [width-1:0] D, output reg [width-1:0] Q);
  string me; initial me = $sformatf("%m");
  always @(posedge clock) begin
    acct_pkg::acct_ff_u(me, width, $countones(Q ^ D), 1);
    Q <= D;
  end
endmodule

module en_ff #(parameter width=32) (input clock, input en, input [width-1:0] D, output reg [width-1:0] Q);
  string me; initial me = $sformatf("%m");
  always @(posedge clock) begin
    acct_pkg::acct_ff_u(me, width, en ? $countones(Q ^ D) : 0, en ? 1 : 0);
    if (en) Q <= D;
  end
endmodule

module rst_ff #(parameter width=32) (input clock, input reset, input [width-1:0] D, output reg [width-1:0] Q);
  string me; initial me = $sformatf("%m");
  always @(posedge clock) begin
    acct_pkg::acct_ff_u(me, width, reset ? 0 : $countones(Q ^ D), 1);
    if (reset) Q <= '{default:0};
    else       Q <= D;
  end
endmodule

module rst_en_ff #(parameter width=32) (input clock, input reset, input en, input [width-1:0] D,
                                         output reg [width-1:0] Q);
  string me; initial me = $sformatf("%m");
  always @(posedge clock) begin
    acct_pkg::acct_ff_u(me, width, (!reset && en) ? $countones(Q ^ D) : 0, (reset || en) ? 1 : 0);
    if (reset) Q <= '{default:0};
    else if (en) Q <= D;
  end
endmodule

// Drop-in copies of core-et's libs/registers modules that also report their activity (rtl-sim/fma_toggle/ff_acct.sv,
// with the instance path added so the counts split by unit), plus the package the macro versions in macros_acct.vh call.
// `macros_acct.vh` is included here so that it is defined before any RTL file is read.
`include "macros_acct.vh"
package acct_pkg;
  import "DPI-C" function void acct_ff_u(input string where, input int width, input int toggles, input int enabled);
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

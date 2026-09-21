// Drop-in copies of core-et's libs/registers modules that also report their activity:
// how many register bits received a clock edge with their enable high, and how many of them changed.
// A register bank with an enable is assumed to sit behind a synthesis-inserted clock gate, so it only
// counts as clocked in cycles where the enable is high.
package acct_pkg;
  import "DPI-C" function void acct_ff(input int width, input int toggles);
endpackage

module ff #(parameter width=32) (input clock, input [width-1:0] D, output reg [width-1:0] Q);
  always @(posedge clock) begin
    acct_pkg::acct_ff(width, $countones(Q ^ D));
    Q <= D;
  end
endmodule

module en_ff #(parameter width=32) (input clock, input en, input [width-1:0] D, output reg [width-1:0] Q);
  always @(posedge clock)
    if (en) begin
      acct_pkg::acct_ff(width, $countones(Q ^ D));
      Q <= D;
    end
endmodule

module rst_ff #(parameter width=32) (input clock, input reset, input [width-1:0] D, output reg [width-1:0] Q);
  always @(posedge clock) begin
    acct_pkg::acct_ff(width, reset ? 0 : $countones(Q ^ D));
    if (reset) Q <= '{default:0};
    else       Q <= D;
  end
endmodule

module rst_en_ff #(parameter width=32) (input clock, input reset, input en, input [width-1:0] D,
                                         output reg [width-1:0] Q);
  always @(posedge clock)
    if (reset) Q <= '{default:0};
    else if (en) begin
      acct_pkg::acct_ff(width, $countones(Q ^ D));
      Q <= D;
    end
endmodule

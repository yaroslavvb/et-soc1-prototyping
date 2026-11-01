// The DFG optimiser of Verilator 5.052 computes `al` wrong. With the default flags this prints al=0000; with -fno-dfg it prints
// al=4000, which is what the source says. Reduced from core-et's txfma_f3.v (lines 160-170), the mux in front of the fused
// multiply-add's alignment shifter, on Sat 31 Oct 2026. Nothing here depends on that RTL.
//
//     run: verilator --binary --timing -Wno-fatal -Wno-lint --top-module tb <this file> && ./obj_dir/Vtb
//     run: verilator --binary --timing -Wno-fatal -Wno-lint --top-module tb -fno-dfg <this file> && ./obj_dir/Vtb
//
// It needs the casez with its wildcard arm: the same block with `case ... default`, or with if/else, comes out right.
module dut (input clk, input [1:0] sel_d, input p1c_d, input [7:0] fc_d, input [7:0] fa_d, input [15:0] prod_d,
            output logic [15:0] al);
  logic [1:0] sel; logic p1c; logic [7:0] fc, fa; logic [15:0] prod;
  always @(posedge clk) begin sel <= sel_d; p1c <= p1c_d; fc <= fc_d; fa <= fa_d; prod <= prod_d; end
  always_comb begin
    casez (sel)
      2'b00: al[15:7] = {1'b0, fc[7:0]};
      2'b01: al[15:7] = {1'b0, fa[7:0]};
      2'b1?: al[15:7] = prod[15:7];
    endcase
    al[6:0] = prod[6:0] & {7{p1c}};
  end
endmodule
module tb;
  logic clk = 0; always #1 clk = ~clk;
  logic [1:0] sel = 0; logic p1c = 0; logic [7:0] fc = 0, fa = 0; logic [15:0] prod = 0;
  wire [15:0] al;
  dut d (.clk(clk), .sel_d(sel), .p1c_d(p1c), .fc_d(fc), .fa_d(fa), .prod_d(prod), .al(al));
  initial begin
    @(negedge clk); fc = 8'h80; sel = 0;
    @(negedge clk); @(negedge clk);
    $display("al=%04x", al);
    $finish;
  end
endmodule

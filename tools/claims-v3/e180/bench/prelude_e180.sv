// E180 bench prelude, read after rtl-sim/fma_toggle_v2/ff_acct.sv (which defines the instrumented register macros):
// core-et's two latch macros (rtl/inc/macros.vh) with an explicit 4-state net type. Verilator 5.052 refuses
// `wire T _din` when T = type(a || b) is the 2-state bit (IEEE 1800-2023 6.7.1, at dcache_buffer_array.v:203); the
// latch's behaviour is unchanged. The whole minion_top then lints with no error (167 modules).
// SPDX-License-Identifier: Apache-2.0
`include "soc.vh"
`undef LATCH
`define LATCH(CLK, DOUT, DIN) \
      if (1) begin \
          wire logic [$bits(DIN)-1:0] _din = DIN; \
          always @(CLK or _din) \
              if(CLK) DOUT <= _din; \
      end
`undef LATCH_P2
`define LATCH_P2(CLK, DOUT, DIN) \
    if (1) begin \
        wire logic [$bits(DIN)-1:0] _din = DIN; \
        always @(CLK or _din) \
            if(~CLK) DOUT <= _din; \
    end

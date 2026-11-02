// Q136(c): core-et's register macros (rtl/inc/macros.vh), instrumented as rtl-sim/fma_toggle_v2/macros_acct.vh does, with the source
// line added, so that each macro register can be named by file and line (the TIMA controls are the registers on tima_clk_en in
// vpu_tensorfma.v). Same behaviour; same unit tallies as macros_acct.vh (acct_ff_l adds to them exactly what acct_ff_u would).
`include "macros.vh"
`undef FF
`define FF(CLK, DATAOUT, DATAIN) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_l(`__FILE__, `__LINE__, $bits(DATAOUT), $countones(DATAOUT ^ (DATAIN)), 1); \
        DATAOUT <= DATAIN; \
    end
`undef RST_FF
`define RST_FF(CLK, RST, DATAOUT, DATAIN, DEF) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_l(`__FILE__, `__LINE__, $bits(DATAOUT), (RST) ? 0 : $countones(DATAOUT ^ (DATAIN)), 1); \
        if(RST) DATAOUT <= DEF; \
        else    DATAOUT <= DATAIN; \
    end
`undef EN_FF
`define EN_FF(CLK, EN, DATAOUT, DATAIN) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_l(`__FILE__, `__LINE__, $bits(DATAOUT), (EN) ? $countones(DATAOUT ^ (DATAIN)) : 0, (EN) ? 1 : 0); \
        if(EN) DATAOUT <= DATAIN; \
    end
`undef RST_EN_FF
`define RST_EN_FF(CLK, RST, EN, DATAOUT, DATAIN, DEF) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_l(`__FILE__, `__LINE__, $bits(DATAOUT), (!(RST) && (EN)) ? $countones(DATAOUT ^ (DATAIN)) : 0, ((RST) || (EN)) ? 1 : 0); \
        if(RST)     DATAOUT <= DEF; \
        else if(EN) DATAOUT <= DATAIN; \
    end

// core-et's register macros (rtl/inc/macros.vh), instrumented. The first toggle recount could not see these bits: 1,233
// of the txfma unit's 2,071 register bits are declared with them, and its README names this as "the obvious next pass".
// Same behaviour; each edge also reports the file, the width and the bits that change.
`include "macros.vh"
`undef FF
`define FF(CLK, DATAOUT, DATAIN) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_u(`__FILE__, $bits(DATAOUT), $countones(DATAOUT ^ (DATAIN)), 1); \
        DATAOUT <= DATAIN; \
    end
`undef RST_FF
`define RST_FF(CLK, RST, DATAOUT, DATAIN, DEF) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_u(`__FILE__, $bits(DATAOUT), (RST) ? 0 : $countones(DATAOUT ^ (DATAIN)), 1); \
        if(RST) DATAOUT <= DEF; \
        else    DATAOUT <= DATAIN; \
    end
`undef EN_FF
`define EN_FF(CLK, EN, DATAOUT, DATAIN) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_u(`__FILE__, $bits(DATAOUT), (EN) ? $countones(DATAOUT ^ (DATAIN)) : 0, (EN) ? 1 : 0); \
        if(EN) DATAOUT <= DATAIN; \
    end
`undef RST_EN_FF
`define RST_EN_FF(CLK, RST, EN, DATAOUT, DATAIN, DEF) \
    always @ (posedge CLK) begin \
        acct_pkg::acct_ff_u(`__FILE__, $bits(DATAOUT), (!(RST) && (EN)) ? $countones(DATAOUT ^ (DATAIN)) : 0, ((RST) || (EN)) ? 1 : 0); \
        if(RST)     DATAOUT <= DEF; \
        else if(EN) DATAOUT <= DATAIN; \
    end

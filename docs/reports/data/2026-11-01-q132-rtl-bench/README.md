# Q132(b): the RTL bench returns correct multiply-adds, and what it now counts

*Sun 1 Nov 2026 (week 44), desk compute on the mini. No card opened. This first commit pins the bench's prediction for E92 before any
E92 measurement exists; the full write-up follows in this file.*

**The fault was the simulator, not the stimulus.** Verilator 5.052's DFG optimiser miscompiles core-et's `casez` blocks with a wildcard
arm and part-select targets, among them the mux in front of the alignment shifter (`txfma_f3.v:160-170`). The shifter's input reads 0, so
a multiply-add returns only its larger operand: c alone, or a·b alone when c = 0, as Q130(b) §0 row 1 reported. `-fno-dfg` fixes it. The
20-line reproducer is [`rtl-sim/fma_toggle_v2/verilator_dfg_reproducer.sv`](../../../../rtl-sim/fma_toggle_v2/verilator_dfg_reproducer.sv).

**The new bench is core-et's `vpu_top`, whole**, so the micro-op stream, the zero gate, `use_prev_sigs`, the clock gates and the write-back
are the RTL's own. Functional check ([`fcheck/`](fcheck/)): fp32 40,000 of 40,000 corner vectors exact; fp16 39,701 of 40,000 on the unit's
own fixed-point window, a named residue of 299 near-total cancellations; all three formats exact on every accumulator word of 60 whole
TensorFMA runs, and the zero gate's slot count equal to the rule in all 60.

**The prediction ([`e92-bench-prediction.json`](e92-bench-prediction.json), written by [`predict_e92.py`](predict_e92.py)).** Fitted on E78's
fp32 and fp16 kinds alone: D = rate × (1.827 fJ × merged-net toggles + 1.082 fJ × clocked register bits), rms 0.283 W on E78. Run on E92's
frozen tiles (`6b8f23f1`), that says, in watts:

| contrast | predicted | adder and normaliser: net toggles an op |
|---|---:|---:|
| fp32 `h_sub` − `h_add` (the adder alternates) | **+3.22** | +1,364,416 |
| fp16 `h_sub` − `h_add` | **+6.45** | +1,792,069 |
| fp32 `c_alt` − `c_abs` | **+3.85** | +1,360,576 |
| fp16 `c_alt` − `c_abs` | **+6.80** | +1,771,589 |
| fp32 `h_allsub` − `h_add` (a steady subtract) | **+0.12** | +12,933 |
| fp16 `h_allsub` − `h_add` | **+0.21** | +9,741 |
| fp32 `c_neg` − `c_abs` | **+0.02** | +5,253 |
| fp32 `h_add` − `c_abs` | +0.42 | 0 |
| fp32 `s_abs` − `c_abs` | +2.00 | +735,474 |

Every other registered contrast, and the recount's merge beside this one, is in the JSON.

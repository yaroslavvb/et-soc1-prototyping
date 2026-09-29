# tau: the rails' averaging filter (hub rung 4), validation on aifoundry3, 29 September 2026 00:34-00:45 PDT

Frozen pre-registration: `tools/claims-v3/tau/PREREG.md` (sha256 `7d4fabad…`, frozen after development on aifoundry1's
card 1: `../2026-09-29-tau-aifoundry1-c1/`, whose result is in the README's development log). Code:
`tools/claims-v3/tau/`, the deconvolution `tools/ettelem/deconv.py`. `smoke/p101` then passes `p101-p103` through the
unmodified `queue.sh`; `report.json` from `reduce.py report p101 p102 p103 --card aifoundry3`.

**Result:** 94 PASS, 2 FAIL. Fitted time constants (P1, all PASS against the card's registered values): minion 1.06 s,
SRAM 1.01, NoC 1.04, board_avg 1.05. T1 (each reading is one linear first-order average), T2 and T3 survive on
aifoundry3; T4 is falsified by P5d (the flat-top scatter of the deconvolved 2 s minion bursts, 0.084 against <= 0.06).
P0 (reported): the SP's pass under a 20 Hz sampler 0.296 s against 0.321 +- 0.02. On aifoundry1's card 1 in
development T1 fell instead (the minion rail rose with 1.32 s and fell with 1.02 s) and the SRAM rail's constant was
0.54 s, against 1.01 here: the cards' SRAM meters differ.

# E180: dated note M1's arm, read (october-forecast-model; REPORTED, never a verdict)

*REPORTED (october-forecast-model, E180's dated notes M1 and M2): read beside E180's verdicts, never one of them; it changes no rule, statistic, threshold or verdict. Read by `arm_m1_e180.py` (E180.md.dated-note-M2.md section 1) from `reduced-e180-v3.json` and `scored-e180.json`; aifoundry3, 6 kept pass(es) (18010, 18011, 18012, 18013, 18014, 18015).*

| reading | statistic per kept pass | mean (W) | 95% interval (W) | the arm (W) | words |
|---|---|---:|---|---:|---|
| E180-H, the board | D(fadd.ps/f_5) - D(fadd.ps/f_4) in each kept pass (E180-H's, on the board) | +0.0270 | -0.0503 to +0.1043 | +0.0042 | **PASS** |
| RA2, the net minion rail | R(fadd.ps/f_5) - R(fadd.ps/f_4) in each kept pass with a rail reading (A1's RA2, the net minion rail) | -0.0160 | -0.0773 to +0.0452 | +0.0042 | **PASS** |
| 4s above zeros, the board | D(fadd.ps/f_4) - D(fadd.ps/zeros) in each kept pass (the scorer's footing for every kind) | +0.0221 | -0.0985 to +0.1427 | +0.0298 | **PASS** |
| 5s above zeros, the board | D(fadd.ps/f_5) - D(fadd.ps/zeros) in each kept pass (the scorer's footing for every kind) | +0.0491 | -0.0602 to +0.1583 | +0.0340 | **PASS** |

- **Beside E180-H:** against 0 it reads NOT RESOLVED (E180-H's SIGN; the scorer's E180-H: NOT RESOLVED, SIZE FAIL HIGH). Placed as the arm is, no difference (0 W) reads PASS and the arm PASS: they read alike (they read differently only when an end of the interval falls between 0 and the arm). The half-width, 0.0773 W, is 19x the arm.
- **The 00:00:55 frozen sentence's bracket** (5s - 4s 8.8 to 10.4 fJ, +0.0040 to +0.0048 W): PASS at its low end, PASS at its high end; the same words across it as at M1's value.
- **The footing:** each kind is read as D(kind) - D(fadd.ps/zeros). D(4s) alone averages 10.7969 W over idle and is never compared with the arm.
- **Beside the arm:** the arm is a near-cancellation: the bubble term, 3x the net (+27.38 fJ against +9.09 fJ), is labelled 'assumed' in the model's ledger ('modelled' in its per-instruction table), and the model gives no band; 10% on the bubble term moves the arm by 30%, 10% on the leakage term by 20%.
- **The power, as the records quote it:** A1 section 2: with no difference E180-H reads POSITIVE 0.02 at 6 passes at every noise level; its half-width is 0.103-0.198 W at 6 passes (0.121-0.232 W at 5), 25-48x the arm (29-56x at 5).


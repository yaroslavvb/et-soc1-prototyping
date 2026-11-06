# M11's scorer v3 (E181's kit round, Fri 6 Nov 2026): v2 unchanged, plus A6-A8's precedence, the start gate read whole, and FL5(c) in both die coordinates

*Desk only, on the Intel, before any E181 datum. [`score_m11.py`](score_m11.py) (`03582d2f`) and [`score_m11_v2.py`](score_m11_v2.py)
(`ebdbb35c`) stay as committed; [`score_m11_v3.py`](score_m11_v3.py) imports v2 unchanged, and every reading and decision v2 makes is v3's. For
the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8. E181's step 22
(`../e181/rb/s22_collect_e181.sh`) runs it through `../e181/score_e181.sh`, only after every gate.*

## What v3 adds

| item | from | what |
|---|---|---|
| P | A6 `95c75047`, A7 `65a93fbb`, A8 `80b92990` | the blind precedence counts them beside the registration and A1-A5 |
| G | A6-2 with A8-4 | each session's `start_gate` mark read whole (the room and its 53.9 °C line, F0, the residue, A8's frozen 0.414 °C, the residue less it and its 0.50 °C line, `passed`); the gate re-computed from the mark's own numbers, and the score REFUSED when `passed` disagrees or a line differs from A6-2's and A8-4's; a pre-A6 mark (E176's kit) read as that kit's own G0; an excluded session carries its mark's reason |
| F | A6-5 with A7-1 and the footing law's dated note 1 (N1) | FL5(c) on each session that passed its gate, from its rests after its holds (R1-R5, rule F): the primary per whole firmware degree in FL1's band (52-66 °C, at least 100 samples a degree) against FL1 by the same weighted line, PASS within 0.02 W/°C, NOT SCORED under 300 samples; beside it, on the 34 codes in E97's 0.5 °C bins against E97's law; and the primary on the degrees 52-58 alone (N1's dry-run range). Reported, never a gate |

## The self-test ([`selftest-score-m11-v3.txt`](selftest-score-m11-v3.txt), `.json`; 40 s): 12 of 12 PASS

- **G1-G3:** the gate's constants equal `run_e181.py`'s (read from its source); A8-4's 0.414 °C is `residue-a8.json`'s prediction; `gate_reading` on
  six synthetic marks: a pass, the room line, the residue line, a mark that lies, a looser line, and the line's edge (an excess of 0.50 °C exactly,
  0.5000000000000016 in floating point, passes through the 10⁻⁹ °C tolerance both files carry).
- **F1-F2:** FL5(c) on synthetic rests with a known slope: FL1's own law PASS, 0.05 W/°C above it FAIL, 250 samples NOT SCORED. The estimator on
  E97's committed rests, degrees 52-58, reproduces N1's committed dry run exactly (0.3196 against 0.3106 W/°C, +0.0090).
- **S1-S5:** whole sessions on E154's committed pass with its holds renamed to M11's (v2's own stand-in): a passing session scored (5 holds, its gate
  read whole, FL5(c) on its rests); the room line and the residue line refusing, NOT SCORED with the mark's reason; a pre-A6 mark read as that
  kit's G0; a lying mark refused; E176's committed pass beside a passing one, excluded with its own G0's reason (53.582 °C > 53.0 °C).
- **P1:** a first launch now reads blind; one second before A8's commit, post hoc.

These are checks of the code on seen and synthetic data, never a reading of a session.

SPDX-License-Identifier: Apache-2.0

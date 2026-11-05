# Dated note A3 beside REGISTRATION.md (Wed 4 Nov 2026, about 21:35-21:45 PST; Q142(m)) - section 7's readings by A2's rules: term (d) is not wanted, and every other entry stands

*REGISTRATION.md, A1 and A2 (`ef74dd0d`, 21:23:36 PST) stay as committed. This note records what A2's rules read. They were
computed by `docs/reports/data/2026-11-04-q142m-m10/section7_m10.py` at 21:30:36-21:30:53 PST, after A2's commit. It ran
after a re-run of `fit_m10.py`, unchanged, which reproduced every committed output (held-out errors within 8.5e-14). The full
readings are in that directory's `section7-m10.json`, and the table with its sources is in `README.md.dated-note-1.md` there.
No pool 8 exists, and no prediction has been made with M10.*

| term | entered by § 6 | § 7 | the reading that decides it |
|---|---|---|---|
| (a) floats | yes | not met | The sessions' float scales spread 2.9 times (aifoundry3) and 2.2 times (card 1) what their anchors' own errors give. Pool 7's bias falls toward 0 on both cards (+0.178 → +0.090 W, +0.192 → +0.101 W). Nothing over-corrects. |
| (b) | yes | not met | The S rows improve on both cards (0.497 → 0.287 W, 0.507 → 0.223 W). Only 4 of 13 tiles have \|3pt − N\| ≤ e(N). |
| (c2) | yes | not met | The leave-one-tile-out k runs 0.2407-0.2433, against 0.14004. |
| **(d)** | **yes (one γ)** | **met** | **E144's one large rise reads 0.015 → 0.547 °C with its fold's γ.** γ's sign agrees across card kinds (0.0235, 0.0451). |
| (a) int8, (c1), (e) | no | reported | Met (int8 over-corrects pool 7 on aifoundry3; c1's gain is not resolved on aifoundry3; e's board error is not resolved). They stay out either way. |

**By A2-1:**
- **The primary.** M10's primary entries are (a) floats, (b) and (c2). Term (d) is out:
  `docs/reports/data/2026-11-04-q142m-m10/m10-s7.json` says so, beside an unchanged `m10.json`.
- **Heat over minutes.** M10 carries Q138(t)'s chain unscaled (factor 1), with γ = 0.03199 (factor 1.032) as a reported arm.
- **Pool 8's registration.** It names the chain unscaled as its heat-over-minutes primary, with the 1.032 arm beside it. It
  states its rate per format: in pool 6's and pool 7's sessions, fp32 ran 0.33-0.36%, fp16 0.33-0.35% and int8 0.23-0.28%
  below the nominal.
- **The next model's registration.** Its input list adds the 62 files the chain opens that no hash list names.

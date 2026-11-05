# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 21:50 PST: two figures in `README.md.dated-note-q142s.md` corrected (Q142(s))

*Written beside [`README.md`](README.md) and [`README.md.dated-note-q142s.md`](README.md.dated-note-q142s.md), and not inside them:
both stay as committed. The watcher fix's verifier found two figures in that note wrong. They are corrected in the fix's second dated
note, [`run_hpl.py.dated-note-2.md`](../../../../tools/claims-v3/hpl/run_hpl.py.dated-note-2.md), and here. Nothing in E165 changes:
no file of this directory, no burst, no verdict, no number. Desk only.*

- **The end's timing.** The note set the self-test's "8.4 s into that run's sampler" beside "this session's signature: 8.1 s". The two
  are counted from different points. Counted the same way, this session and the self-test end alike.
  - From BURST-158's first telemetry line, `s1` ended 8.375 s in, W5a's 8.4 s.
  - From its `sampler_start` mark, `s1` ended 8.126 s in: D2's 8.1 s above.

  Source: [`posthoc-watcher-q142s.txt`](../../../../tools/claims-v3/hpl/posthoc-watcher-q142s.txt) § 4.
- **The incidence.** The note said "1,745 run boundaries". The committed data's 99 measured run_hpl sessions hold 1,771 `follow()`
  calls and 1,672 run boundaries. This session's end is the only `telemetry_stale` one among them: 1 in 1,672, about 0.06% per boundary
  (95%: 0.0015% to 0.33%), and about 9% for a session of 150-170 boundaries. That is a one-event estimate (§§ 1-2 of the same file).

The same read finds that **no gate in the committed data read only the previous run's last reading**: 1,640 of 1,669 read their own
run's file, and 29 are undecidable (§ 3). This session's 157 recorded gates after its first run are among them. 155 read their own
run's file. Two are undecidable: BURST-03 and BURST-117, whose idle readings match the previous run's last line exactly, and each
passed at once.

SPDX-License-Identifier: Apache-2.0

# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 20:00 PST: D2's watcher race, reproduced at the desk and fixed for later runs (Q142(s))

*Written beside [`README.md`](README.md) and not inside it, as the link back from this complaint to its fix (the owner's rule of 29 Oct
2026: a fix always links the original complaint). Nothing in E165 changes: no file of this directory, no burst, no verdict, no number.
Desk only.*

§ Registered against what happened, **D2**, reads the end of `s1` at run 159 (`error:telemetry_stale`, 13 bursts short) as *consistent
with a race in `run_hpl.py`'s telemetry watcher (post hoc, not proven)*. The fix is
[`tools/claims-v3/hpl/watcher_q142s.py`](../../../../tools/claims-v3/hpl/watcher_q142s.py), with its dated amendment
[`run_hpl.py.dated-note.md`](../../../../tools/claims-v3/hpl/run_hpl.py.dated-note.md) beside the frozen `run_hpl.py`, which stays as committed.

- **The mechanism, reproduced at the desk.** The self-test
  ([`selftest-watcher-q142s.txt`](../../../../tools/claims-v3/hpl/selftest-watcher-q142s.txt)) forces a `follow()` between the watcher's
  read of its path and its read of the file. In a dry session of `run_hpl.py`'s own `Session`, the committed watcher then ends the session
  `error:telemetry_stale` in the next run's cool gate, 8.4 s into that run's sampler, before any launch. That is this session's signature:
  8.1 s, run 159's cool gate. The new watcher runs the same session to its end. On aifoundry2 the reading stays post hoc, because nothing
  recorded the watcher's position there.
- **Incidence.** This is the only `telemetry_stale` end among the 1,745 run boundaries of the 99 measured run_hpl sessions committed
  (E64 to E170): about 0.06% per boundary, about 9% per session of this size.
- **Which runs use the fix.** Runs registered after the amendment whose runner imports `run_hpl.py`: the next card day's governed runs on
  aifoundry2 (this run's successors among them) and on aifoundry1 card 0. No past run changes. This session's 158 counted bursts stay as
  counted, and the 13 are not re-run.

SPDX-License-Identifier: Apache-2.0

# Dated note beside REGISTRATION.md (Wed 4 Nov 2026, about 10:05 PST; Q141(t))

*Written after the 27-point counts and before any pool-7 measurement. REGISTRATION.md (`0830f65b`, 09:11:50 PST) stays as
committed; this note adds what happened while it ran. No registered rule, reading, threshold or tile changes, and nothing counted
changes.*

1. **The bench ran at nice 20, not 10.**
   - The registered driver started `run_kinds.py` at `nice -n 10` (observed at about 09:12:30 PST: the driver at 0, `run_kinds.py`
     and its `Vtb` workers at 10).
   - By about 09:20 PST every process of the run read nice 20. This session's background commands are reniced to 20 while they run,
     as Q140(x)'s pool-7 count also recorded.
   - So the bench ran gentler than the brief's nice 10, and slower: 2,720 s for 216 points at 4 jobs (50.4 s a point on one core,
     against the pilot's 29.4 s), with the Intel's load at 11-31 from other lanes.
   - It changes no count: the bench is deterministic. D1 and D2 hold, so every repeated point equals its committed count exactly.
2. **The driver crashed after the bench had finished, and its run record is reconstructed.**
   - `bench_s7.py` writes its run record with `os.nice(0)`. After the renice, that call raised `PermissionError` (EPERM) at
     09:57:31 PST, so the driver exited 1 without writing `counts-s7-27-run.json`.
   - By then `run_kinds.py` had already written `counts-s7-27.json` and `bench-s7-27.log` (both at 09:57:31) and exited 0. It writes
     its JSON only after every point has returned, and the file holds all 8 tiles × 27 points with every `check_mismatch` 0.
   - `counts-s7-27-run.json` is therefore **reconstructed**, and marked so:
     - the start, 09:12:11, is the runner script's line printed just before the driver started;
     - the end is the counts file's write time;
     - the exit is `run_kinds.py`'s.
   - `bench_s7.py` is a committed file and is not edited. The 81-point step runs its `main()` unchanged through the new
     [`bench_s7_run.py`](bench_s7_run.py), which replaces only `os.nice(0)` with a read of the process's priority
     (`os.getpriority`).
3. **A fifth core, briefly.** The arm's builder (`make_arm_s7.py`, 13 s on one core) and the scorer's self-test (a few seconds)
   ran at nice 10 while the 81-point step's 4 bench jobs were running. For about half a minute the lane used five cores, not four.
4. **Nothing else departs.** REGISTRATION.md section 2's three departures from RECOUNT-RULE.md section 6 (timing, N fixed at 27,
   the standard points counted again) were registered before the counts. Every check of section 1 passed (`arm-s7.json`
   `checks`).

# Dated amendment beside `run_hpl.py`, Wed 4 Nov 2026 (week 45), about 20:00 PST: the telemetry watcher's follow() race (Q142(s))

*Written beside [`run_hpl.py`](run_hpl.py) and not inside it. `run_hpl.py` is frozen as committed (`1a899d8f`, 23 Oct 2026; sha256
`68493295504fba5d4e9056b4f7e7387179d555e4157bbae32075b4197f3df227`), and every session that ran it recorded that hash (`session.json` ›
`sha256.runner`, and the E119 chain's `run_hpl_sha256`). So its bytes stay as they are. The fix is a new kit file,
[`watcher_q142s.py`](watcher_q142s.py), that future runs install over the imported module. **No past run changes.** Desk only: no card, no
device command, no lab box. It answers the card half's critic (Q141's card half, 4 Nov 2026), whose next step 4 asks to make the next
card day's runbook safe, and the complaint it fixes is E165's D2
([`2026-11-04-e165-blind7-aifoundry2/README.md`](../../../docs/reports/data/2026-11-04-e165-blind7-aifoundry2/README.md), § Registered
against what happened). That README is linked back to this fix by a dated note beside it (`README.md.dated-note-q142s.md`).*

## What happened (E165's D2)

E165's session `s1` on aifoundry2 ended 13 bursts short at 15:10:12 PST on 4 Nov: at run 159, a pass-3 burst still in its 55 °C cool
gate before any launch, `run_hpl.py`'s guard found no reading newer than 5 s and ended the session `error:telemetry_stale`, 8.1 s into
the run's sampler. The sampler never stalled: that run's file holds 83 lines at 100-101 ms spacing, with die and board fields. The
README read it, post hoc and not proven, as a race in the watcher: the previous run's file was 90,896 B, this run's 58,432 B when the
guard fired.

## The race

`Watcher.run()` (line 338) reads `self.path` (line 344) and `self.pos` (line 348, `f.seek(self.pos)`) outside the watcher's lock.
`Watcher.follow()` (line 329) resets both under the lock, and `Session.start_sampler` calls it at every run boundary (line 534).

**Case 1: follow() between the path read and the file read.** `run()` then reads the old file from the new position 0. It re-reads the
whole old file and adds its length to the new file's position. It also stamps the old file's last line as a fresh reading. From then
on:
- the watcher reads nothing from the new file until that file grows past the old file's length;
- for 3 s, `reading()` hands the gates the previous run's last reading as live;
- the guard (line 683) then ends the session with `error:telemetry_stale` once that reading is 5 s old and the sampler 8 s old.

**Case 2: follow() between the file read and the position update.** The old chunk's length moves the new file's position instead.

The window is the few tens of microseconds between line 344 and line 348, in each 50 ms loop. In the committed data, 99 measured
sessions ran this `run_hpl.py` (28 data directories, E64 to E170). They hold 1,745 run boundaries, and E165's is the only
`telemetry_stale` end among them. That is about 0.06% per run boundary, or about 9% for a session of 150-170 runs. Every
run_hpl-based queue can hit it: in the card half's chain, E158-E161, E165 and E167-E170.

## Reproduced at the desk (post hoc)

[`selftest_watcher_q142s.py`](selftest_watcher_q142s.py) forces the interleaving, deterministically, from inside the watcher's own
thread; [`selftest-watcher-q142s.txt`](selftest-watcher-q142s.txt) has the output: **15 of 15 expectations hold**.

| case | what is forced | the committed watcher | the new watcher |
|---|---|---|---|
| W1 | follow() between the path read and the file read | **fails**: its position is left at 23,000 B on a 575 B file, and the old file's last line shows as the new reading | passes |
| W2 | follow() between the file read and the position update | **fails**: position 1,150 on a 575 B file | passes |
| W3 | as W1, with an unread sample at the die stop in the old file | fires the stop | fires the stop; the sample is never the new file's reading |
| W4 | a follow() at a quiet moment (the control) | passes | passes |
| W5a | a dry `run_hpl` Session of two runs; the second run's gate below the first run's last die | **ends `error:telemetry_stale:NEXT-… cool gate`, 8.4 s into the second run's sampler, before any launch**: E165's s1 signature | runs to `done` |
| W5b | the same, the gate above the first run's last die | **the gate admits the launch on the first run's last reading**; the stops are blind for that launch | the gate reads its own run's telemetry |
| W6 | `install()` | | replaces the class for Sessions built after it, is idempotent, and refuses a `run_hpl.py` with other bytes |

So E165's D2 reading is the mechanism, now reproduced. On the box it stays post hoc: nothing there recorded the watcher's position.

W5b is a second consequence, found here. When the next run's gate is above the previous run's last die, the committed watcher lets
the gate pass on that stale reading. The registered stops then cannot see that launch: at most one 10 s launch process, after which
the guard between processes ends the session. The committed records cannot show whether this ever happened, because a gate's
reading carries no timestamp. The card's own governor and the PMIC limits act regardless.

## The fix: [`watcher_q142s.py`](watcher_q142s.py)

One rule: what an iteration of `run()` reads is applied only if no follow() came after the iteration took its snapshot.
- `run()` takes the path, position, generation and board count under the lock, and reads the file outside it.
- Under the lock again, it applies the position and the readings only if the generation is unchanged. `follow()` bumps the generation
  under the lock.
- A chunk read across a follow() is never a reading of the new file and never moves its position.
- Its lines still pass through the same stops (W3): every line is checked once, as before.

Nothing else changes:
- the same parse (`run_hpl.parse_tel`);
- the same stops: `safety.abs_stop_c` on the die mean or the hottest sensor on one sample, and `board_cap_w` on `cap_consecutive`
  samples;
- the same `fire()`, the same 50 ms loop, the same `snapshot()` and `reading()`;
- a followed file is still read from its start.

It sends no device command and opens no device: `dmcmd_audit.py` finds 0 send sites. Every number used here comes from committed files
and from the self-test's output.

## Which future runs use it

Every session runner **registered after this note** uses it if it imports `run_hpl.py`, directly or through the E119 chain:
`kspeed/run_kspeed.py`, `run_e101s.py`, `kspeed/e105/run_e105.py`, `e119/run_e119.py`, `e146/run_e146.py`, `kspeed/e84/run_e84.py`,
and `e167/run_e167.py`'s import of `run_kspeed`. Each such runner:
1. calls `watcher_q142s.install(H)` before it builds a Session (`H` is the imported `run_hpl` module, the chain's `R119.H`, `RE.H` or
   `R84.H`);
2. records the returned record in its own session record (its `eNNN.json`);
3. lists `tools/claims-v3/hpl/watcher_q142s.py` in its frozen hash list and in its `dmcmd_audit` file set;
4. runs its kit's dry pass with the watcher installed.

That covers the next card day's governed runs:
- **aifoundry2**, the successors of E165 (governed bursts), E167 (heat holds; the card-half critic's next step 5), E168 (G4's clock,
  step 6) and E169 (the stride term's size, step 7);
- **aifoundry1 card 0**, E170's successor (the burst heat with a coefficient per card, step 5).

`install()` refuses, before any device is opened, a module whose file is not the committed `run_hpl.py`.

**Not concerned.** The 600 MHz kinds runs (`kinds/run_e78.py`: E163, E164 and the critic's step 3) and E166's heat holds
(`e97/run_e97b.py`) have no run_hpl Watcher.

**Not covered.** `e77/run_e77.py`, `e120/run_e120.py` and `knob/run_knob.py` each read their path and position outside the lock in the
same way, in their own Watcher (the history form). This note does not change them. A run on one of them needs its own amendment,
with the same rule.

## What does not change

No past run changes:
- E64 to E170's sessions ran the committed watcher, and their data, registrations, frozen hash lists and verdicts stand;
- E165's 158 counted bursts stay as counted, and its 13 uncounted bursts are not re-run;
- E165's D2 stays as written.

No registered stop, cap, admission rule, prediction or device command of any run changes.

## What it does to predicting power and heat

Nothing to any number. It removes a harness end that cuts a governed session short at random, about 9% per session of 150-170 runs;
E165 lost 13 bursts to it, and with them the third pass on 13 tiles. So a governed blind test keeps its registered pass count, and with
it the intervals the clock and board rules are scored on. It also closes the path by which a gate passes on the previous run's reading,
so each gate decides on its own run's telemetry and the registered stops watch every launch.

SPDX-License-Identifier: Apache-2.0

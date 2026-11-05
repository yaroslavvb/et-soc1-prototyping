# Dated note 2 beside `run_hpl.py`'s amendment, Wed 4 Nov 2026 (week 45), about 21:50 PST: five corrections after its verifier (Q142(s))

*Written beside [`run_hpl.py.dated-note.md`](run_hpl.py.dated-note.md), the first dated amendment (lab `abe6b0f2`, 20:13:55 PST), and
not inside it: that file stays as committed. The verifier of `abe6b0f2` (4 Nov 2026, about 20:18-21:05 PST) found the fix sound and
five statements in the amendment wrong or too strong. Each is corrected below and re-derived from committed files. No code changes:
[`watcher_q142s.py`](watcher_q142s.py), its self-test and every rule of the amendment stand, and `run_hpl.py` stays as committed
(sha256 `68493295…f227`). Desk only: no card, no device command, no lab box.*

The figures below come from two new post hoc files, written after the verifier:
- [`posthoc_watcher_q142s.py`](posthoc_watcher_q142s.py), output [`posthoc-watcher-q142s.txt`](posthoc-watcher-q142s.txt): a read of
  the committed data;
- [`selftest_watcher_q142s_w5c.py`](selftest_watcher_q142s_w5c.py), output
  [`selftest-watcher-q142s-w5c.txt`](selftest-watcher-q142s-w5c.txt): a dry test, **W5c**.

## 1. The blind window is every launch process that starts in the run's first 8 s

The amendment (§ Reproduced at the desk) said that when a gate passes on the previous run's reading, the stops cannot see "at most
one 10 s launch process, after which the guard between processes ends the session". That holds only for launches of 8 s or more.

The guard is checked before each launch process. It ends the session only once the reading is over 5 s old **and** the sampler over
8 s old (`run_hpl.py:683`). So every process that starts within 8 s of the run's sampler start runs with the watcher off its own run's
file. With launches of 8 s or more that is one process. With shorter ones it is more.

**W5c** is W5b's dry two-run session (the same gate, above the first run's last die, and the same forced `follow()`), with the second
run at 3 launch processes of 3 s. At each work launch it records what the stops were watching.

| | the committed watcher | `watcher_q142s.py` |
|---|---|---|
| the gate's reading | the first run's (0.14 s before the run's first line) | its own run's (1.29 s after) |
| process 0, 1.3-4.9 s | **blind**: last reading the first run's, position 18,550 B in a 1,545 B file | on its own run |
| process 1, 4.9-8.4 s | **blind**: position 18,550 B in a 5,471 B file | on its own run |
| process 2, from 8.4 s | not started: `error:telemetry_stale` | on its own run |
| end | `error:telemetry_stale:NEXT-00-fp32-zeros-1024-r1` | `done` |

4 of 4 expectations hold. So the window is *every launch process that starts before the guard's 8 s rule fires: one or more (two of
3 s in W5c)*. The fix removes the path whatever the launch length.

## 2. The committed records do bound it: no gate passed on only the previous run's reading

The amendment said: *"The committed records cannot show whether this ever happened, because a gate's reading carries no timestamp."*
That is too strong. A gate's recorded reading (`run_hpl.Session.reading()`: die mean, die high, board W and MHz) has no time of its
own, but its four values can be matched against the telemetry lines.

`posthoc-watcher-q142s.txt` § 3 does this for every run whose gate recorded a reading after a run of the same session: 1,669 runs,
1,666 of them cool gates and 3 hot ones.

| the gate's reading | runs |
|---|---|
| a line of its own run's telemetry before the first work launch, and not the previous run's last line | **1,640** |
| the previous run's last line only: a gate that passed on the previous run's reading (W5b) | **0** |
| both: the two files hold the same reading, so it cannot be told apart | 29 |
| neither | 0 |

The 29 undecidable runs are identical idle readings. Each gate passed at once (held 0.0-0.2 s), so timing does not separate them
either. In the committed data, then, no gate read only the previous run's last line; 1,640 of 1,669 read their own run's file; and 29
are undecidable.

## 3. The incidence: 1 in 1,672 run boundaries, with an interval

The amendment gave "1,745 run boundaries" and called them one `follow()` each. That is neither count: it is the sessions' `runs.jsonl`
records plus E165's unrecorded run. Here are the counts (`posthoc-watcher-q142s.txt` §§ 1-2):
- `Session.start_sampler` calls `follow()` once per run it starts (`run_hpl.py:534`): **1,771 `follow()` calls** in the 99 measured
  sessions (28 data directories). A session that ended inside a run counts that run by its telemetry file.
- A run boundary is a `follow()` with an earlier file to race. Each session's first has none, so there are **1,672 run boundaries**.
- E165's is the only `telemetry_stale` end: **1 in 1,672, about 0.06% per boundary** (exact 95% Poisson interval 0.0015% to 0.33%).
- For a session of 150-170 boundaries that is **about 9%** (8.6-9.7%; at 160, 95%: 0.2% to 41%).

It rests on one event. So "about 9% per session" is a one-event estimate, not a measured rate.

## 4. 8.4 s and 8.1 s are one end, timed from two points

The amendment's table compared W5a's end, "8.4 s into the second run's sampler", with E165's "8.1 s". The two count from different
points:
- W5a counts from the run's first telemetry line (`selftest_watcher_q142s.py`'s `first_t`);
- E165's README (§ Registered against what happened, D2) and this amendment count from the `sampler_start` mark.

Timed from the same point, E165's s1 and W5a end alike (`posthoc-watcher-q142s.txt` § 4). BURST-158's first line is at
1793833803923 ms, its `sampler_start` mark at 1793833804172 and the end at 1793833812298:
- from the first telemetry line, E165's end is **8.375 s**, W5a's 8.4 s;
- from the mark it is **8.126 s**, the 8.1 s quoted.

## 5. A path

The list of runners in § Which future runs use it names `run_e101s.py`. Its path is `kspeed/e101/run_e101s.py`.

## What does not change

- The fix, its rule, `install()` and the four steps a future runner takes.
- The runs that use it: aifoundry2's governed runs and aifoundry1 card 0's.
- Every past run, registration, frozen hash list and verdict. E165's 158 counted bursts stay as counted, and its D2 stays as written.

The dated note beside E165's README, `README.md.dated-note-q142s.md`, repeats the wording that items 3 and 4 correct. A second note
beside it, `README.md.dated-note-q142s-2.md`, points here.

## What it does to predicting power and heat

Nothing changes to any number, prediction, band, stop or verdict. It says two things about the record:
- In the committed data, no gate is shown to have passed on the previous run's reading. 1,640 of the 1,669 gates read their own run.
  The other 29 read values their own run's telemetry also holds before its launch, so an unraced gate would have passed on the same
  values.
- The race's cost to a future governed blind test is uncertain from one event: from 0.2% to 41% of 160-run sessions cut short at 95%,
  about 9% at the point estimate. The fix makes that 0, along with the blind launches of item 1.

SPDX-License-Identifier: Apache-2.0

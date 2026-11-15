# E193 sitting A's data README, dated note 1 (Sun 15 Nov 2026; after the data verifier): the owner waived the day's post in his own words at 10:22:36 PST, 2 min 41 s before the sitting's first card command; "first card command" names two moments (43.08 card-minutes from the session's holder check, as registered, and 43.43 from step 7's read, both under the cap of 60); the die's peak of 51 C was read 151 times; the device output files hold the last device process only; the anchor drift by the block it crosses (post hoc); no reading changes

*Written on aifoundry2 from about 13:05 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e193d` of Q182, after E193's data verifier `verify-e193d` (Sun 15 Nov 2026, 12:24-12:52 PST: holds with fixes;
one minor finding, about this README, and three nits, all of them records lines, beside four notes; none is a fault in a datum, a price
or a check; its own reduction, written from E193.md 7 and importing nothing from the kit, equals the registered reducer's output for this
sitting in all 6,619 fields it compared, to 8.6e-8 relative). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `fe08ed67`,
git 11:13:37 PST Sun 15 Nov 2026) stay as committed. **No number, rule, price, check or gate reading changes, and nothing is scored. The
forecasts stay sealed: no forecast number is here.** The figures of §§ 1-4 come from [`posthoc_note1_e193.py`](posthoc_note1_e193.py),
the same bytes as in sitting B's directory. It reads only this directory's data commit: the 28 files `SHA256SUMS` lists (28 of 28 OK),
`README.md` and `SHA256SUMS`. Its output is [`posthoc-note1-e193-a.txt`](posthoc-note1-e193-a.txt) and
[`posthoc-note1-e193-a.json`](posthoc-note1-e193-a.json) ("output §" below), and a re-run from this tree writes both byte for byte. § 5's
figures are read from the registered reducer's output for this sitting, `x04-e193-A.json` (sha256 `e1e536e8...`, the bytes verify-e193d
re-derived), which the records lane commits into this directory after this note. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note,
the script, its two outputs, `README.md` and `SHA256SUMS`, so the line numbers below refer to their committed bytes. The registration's
and the kit's files named below are under `tools/claims-v3/e193/`, unchanged since they were committed: `E193.md` (`61f0c2df...`), the
runner `proposal/src/run_x04.py` (`26d08862...`) and the reducer `proposal/src/reduce_x04.py` (`98bbc174...`) in
`SHA256SUMS-e193-registration` (`b17d58a4`); `KIT.md` (`7e6b83ae...`) in `SHA256SUMS-e193-kit` (`45d45c12`). Interpreter:
`/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E193.md and the kit as committed), **measured** (the session's committed
files), **post hoc** (desk readings after the data, deciding nothing).*

## 1. The owner waived the day's post in his own words at 10:22:36 PST (the verifier's finding 1, minor)

**What README.md records.** The day's post route "not named, read by the orchestrator as no post (with his Saturday words "it's fine not
to announce, the cards are unused")" (lines 17-18). Departure 3 adds "he can still ask for one" (lines 99-103), and the table's post row
reads "none: the route not named, read as no post" (line 85).

**What happened.** At **10:22:36 PST on Sun 15 Nov 2026** the owner waived the post in his own words, verbatim: "don't worry about discord
post, just use the machines, nobody is using them". He was answering the orchestrator's status message, which said the day would run with
no post, read from his Saturday words, and asked him to say if he wanted one (the round's log, section 115). It is a standing waiver, for
that day and later days until he says otherwise. Sitting B's README quotes the same words with their time (its lines 108-111, `96ef447c`).

**When, against this sitting** (measured; output § 1):
- 95 s before k6's look (10:24:11 PST, README.md line 102). The kit's order of steps puts step 3, "the day's post, or the owner's
  waiver", after the look (KIT.md lines 82-83).
- 140 s (2 min 20 s) before step 7's config read (10:24:56 PST, line 69), the first command any step sent to the card that day.
- 161 s (2 min 41 s) before the session's first card command, its holder check (10:25:17 PST, `session/first-card-command.txt`). So it
  came before the sampler, the smoke and the main run (10:25:17-11:08:22 PST), and before this directory's data commit (11:13:37 PST).

**What it closes.** E193.md 12 (lines 313-315): "His go must name: ... the day's post in the lab's channel, or his waiver of it for that
day". His go of 10:05:42 named the registered items through the message it answered, but not the post route (README.md departures 1 and
3), and the orchestrator's reading filled that item. From 10:22:36 his own words filled it, before this sitting's first card command by
either of § 2's two moments. E193.md 11 counts the post route among the gates before the sampler (line 303: "no sitting: no data"); it
was met in his own words before the sampler started. As the round's log asks every card lane to record it: **the owner waived the post:
his words, Sun 15 Nov 2026 10:22:36 PST.** Step 3 and step 11's release were skipped (README.md lines 100-101), and no post was made.
Every other etiquette check stood (lines 101-103).

**What changes.** README.md's departure 3 and its post row now read with this section beside them. No reading changes: no post was made
under either record, and the gate was met under both.

## 2. "First card command" names two moments in README.md (the verifier's nit 2)

The two moments (measured; output § 1):
- **The session's holder check, 10:25:17 PST** (T0 1794767117; `session/first-card-command.txt`; `session/session.log` line 6: "the
  first card command (the holder check)"). README.md uses the words for this moment in lines 11, 33, 70 and 73, and it is the registered
  one. E193.md 6 counts each sitting's cap "from the sitting's first card command (its first holder check)" (line 196). The kit named it
  before any datum: "**The first card command** is the session's holder check (`et-who --check`), before the start config read: the cap
  counts from it, **its time stamped as the check starts**" (KIT.md line 107; the session's step 2, line 43). The runner's deadline
  counts from it (KIT.md line 44; `session/session.log` line 8: 11:23:17 PST, T0 + 3,480 s).
- **Step 7's config read, 10:24:56 PST** (README.md lines 69, 102 and 129; k6's `s09_a3_reads_k6.sh`, reads through E128's guard,
  nothing set). Lines 112-113 call it "the card lane's first card command of the day": no step before it sent anything to the card. It
  came 21 s before the holder check.

Counted to the session's end (11:08:22 PST, `session/session.log` line 15):
- from the holder check, **43.08 card-minutes** (2,585 s), as line 33 gives it: the registered count;
- from step 7's read, **43.43** (2,606 s).

Both are under the cap of 60. Had the deadline counted from step 7's read, it would have come 21 s earlier, at 11:22:56 PST. The main run
ended at 11:08:22: 14 min 55 s before the deadline as set, and 14 min 34 s before that earlier one. Sitting B's note 1 gives its own
figures: 27.83 and 28.10 card-minutes against its cap of 50.

**Not counted from: k6's look** (step 4, 10:24:11 PST, line 102). It runs `et-who`, `ps`, `who` and `uptime` on the box. `et-who` runs
`et-holders`, which "never opens /dev/et*: fuser only stats the node and the /proc/<pid>/fd links" (`tools/lab/et-holders` line 4), so
the look sent nothing to the card. It is a runbook step before the session (KIT.md line 82; E193.md 17 lists "the look (`et-who`, `who`,
`uptime`, `ps`) before and after" apart from the sitting, lines 450-451), not the sitting's holder check; sitting B's note 1 § 3 states
the kit's reading in full. Counted from the look, the span to the session's end is 44.18 minutes, under the cap too.

**What changes.** Nothing. The words in lines 112-113 name the first command sent to the card that day; the cap, the card-minutes and the
deadline count from the session's holder check, as lines 33 and 73 give them.

## 3. The die's peak was read many times; README.md gives its last time (the verifier's nit 3)

README.md line 40 gives the main run's die peak as "51 C (11:07:54; lowest 49 C)", and line 61 the smoke's as "die 50 C (lowest 48 C)".
From each runner call's telemetry (measured; output § 2; `temp_c.minshire[0]`, whole degrees, ten samples a second; times PST):

| runner call | the die's peak | samples at it | first | last | the lowest |
|---|---|---|---|---|---|
| main run, `x04/` (24,771 samples) | 51 C | **151** | 10:35:33.385 | 11:07:54.929 | 49 C: 18,946 samples, 10:27:01.784 to 11:07:49.824 |
| smoke, `smoke/` (1,035 samples) | 50 C | **6** | 10:26:45.785 | 10:26:46.285 | 48 C: 337 samples, 10:25:17.953 to 10:26:11.636 |

README.md's 11:07:54 is the last sample at 51 C. The board's peaks are single samples, at the times README.md gives: 32.47 W at
11:02:38.170 (the main run; its lowest, 22.33 W, one sample at 11:07:39.112) and 32.06 W at 10:26:46.085 (the smoke; its lowest, 22.29 W,
one sample at 10:25:56.013).

## 4. The device output files hold the last device process only (the verifier's nit 4)

README.md's Files table (line 162) lists each runner call's `device-stdout.txt` and `device-stderr.txt`. The registered runner opens both
afresh, for writing, for each device process (`proposal/src/run_x04.py` lines 279-280), so each file holds only the last device
process's output (measured; output § 3):
- `x04/device-stdout.txt`: 10 X04 lines. Each equals exactly one record of `x04/runs.jsonl`, and they are its last 10: the main run's
  last device process, pass 8, block T, `spin2` at position 7 (`x04/run.log`: "pass 8 block T spin2: 10 launches, exit 0", then "done").
- `smoke/device-stdout.txt`: 5 X04 lines, the last 5 records of `smoke/runs.jsonl`: the smoke's tenth and last device process, block C's
  `spin2`.
- Each `device-stderr.txt`: 47 lines and 3,686 bytes with one "PCIe target:" line, the device layer's report from one process.

Every launch's record is in `runs.jsonl`: the runner writes one line per launch (`run_x04.py` line 64; the file opened for appending,
line 484), 2,808 for the main run and 57 for the smoke.

## 5. The anchor drift by the block it crosses (the verifier's note 7; post hoc, deciding nothing)

E193.md 8's check 3 (line 241): "Anchor drift between block boundaries under 0.1 W; a block above is flagged". Within each measured pass,
the registered reducer takes the next `spin2` anchor's watts over idle less this one's, keyed by this anchor's block (`reduce_x04.py`
lines 367-376). In this sitting the blocks ran S, D, W, T in every pass, with an anchor at each block's position 0 and a closing one at
T's position 7, so each key is the drift across one block. The kit's checker read check 3 as FLAGGED, 16 of 32 boundaries
(`checks-e193-A.json`, which the records lane commits beside the reducer's output). By the block crossed (post hoc, from
`x04-e193-A.json`; the SD over the 8 measured passes):

| across block | mean | SD | lowest | highest | flagged |
|---|---|---|---|---|---|
| S (to D's anchor) | +0.059 W | 0.169 W | -0.285 W | +0.276 W | 5 of 8 |
| D (to W's anchor) | **-0.106 W** | 0.103 W | -0.269 W | +0.021 W | 3 of 8 |
| W (to T's anchor) | +0.059 W | 0.083 W | -0.029 W | +0.236 W | 1 of 8 |
| T (to the closing anchor) | +0.059 W | 0.196 W | -0.307 W | +0.231 W | 7 of 8 |

So the drift has a pattern by position rather than one steady trend: across block D the anchor fell by 0.106 W on average, and across
each of the other three blocks it rose by 0.059 W. The reducer reports the anchor-detrended values beside the plain ones (E193.md 7 and
8); nothing here changes either, or check 3's verdict.

## 6. What needs no change

- **The reducer's seconds** (the verifier's note 8): the registered reducer holds epoch seconds as float64, so `wall_s` and the rates
  built on it differ from an exact millisecond computation by at most 8.6e-8 relative in this sitting; 16 samples sit exactly on a window
  edge, and the reducer included each of them, as the exact reading does (verify-e193d's re-derivation). No printed digit moves. No
  change.
- The verifier's notes 5 and 6 are about sitting B's README; sitting B's note 1 answers them.

## 7. What this note does not change

`README.md` and `SHA256SUMS` stay as committed. Nothing changes in any datum, in the registered reducer's prices or in E193.md 8's checks:
both are computed after the data commit and committed into this directory by the records lane. The seal is kept: no forecast number is
here, and nothing here scores E193. The gates read as README.md gives them, with § 1's record of the post.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `posthoc_note1_e193.py` | the post hoc reader, the same bytes as in sitting B's directory: standard library only, it reads only committed files |
| `posthoc-note1-e193-a.txt`, `posthoc-note1-e193-a.json` | its output for this sitting |
| `SHA256SUMS-note1` | the sha256 of the four files above, `README.md` and `SHA256SUMS` (6 entries) |

Re-run from the repository's top (a re-run under `/usr/bin/python3` 3.12.3 writes both outputs byte for byte):

```
D=docs/reports/data/2026-11-15-e193-x04-clock-sitting-a-aifoundry3
/usr/bin/python3 -I -B $D/posthoc_note1_e193.py --out /tmp/e193n1a
cmp /tmp/e193n1a/posthoc-note1-e193-a.json $D/posthoc-note1-e193-a.json && cmp /tmp/e193n1a/posthoc-note1-e193-a.txt $D/posthoc-note1-e193-a.txt
(cd $D && sha256sum -c SHA256SUMS-note1 && sha256sum -c SHA256SUMS)
```

SPDX-License-Identifier: Apache-2.0

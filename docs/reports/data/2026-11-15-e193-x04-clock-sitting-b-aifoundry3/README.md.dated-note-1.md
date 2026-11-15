# E193 sitting B's data README, dated note 1 (Sun 15 Nov 2026; after the data verifier): the kit's reading of "the sitting's first card command" is the session's holder check, not k6's look, so the rest after sitting A held (40 min 29 s; 40 min 13 s to step 7's read); 27.83 card-minutes as registered and 28.10 from step 7's read, both under the cap of 50; the die's peak of 52 C was read 1,338 times; the device output files hold the last device process only; the per-op prices over spin2 are negative at the sparse ends, as computed, and the class lines' slopes do not use spin2 (post hoc); no reading changes

*Written on aifoundry2 from about 13:05 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e193d` of Q182, after E193's data verifier `verify-e193d` (Sun 15 Nov 2026, 12:24-12:52 PST: holds with fixes;
one minor finding, about sitting A's README, and three nits, all of them records lines, beside four notes; none is a fault in a datum, a
price or a check; its own reduction, written from E193.md 7 and importing nothing from the kit, equals the registered reducer's output for
this sitting in all 4,189 fields it compared, to 5.1e-8 relative). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab
`96ef447c`, git 12:20:41 PST Sun 15 Nov 2026) stay as committed. **No number, rule, price, check or gate reading changes, and nothing is
scored. The forecasts stay sealed: no forecast number is here.** The figures of §§ 1-4 come from
[`posthoc_note1_e193.py`](posthoc_note1_e193.py), the same bytes as in sitting A's directory. It reads only this directory's data commit
(the 28 files `SHA256SUMS` lists, 28 of 28 OK, `README.md` and `SHA256SUMS`) and sitting A's `session/session.log`, at its entry in A's
`SHA256SUMS`. Its output is [`posthoc-note1-e193-b.txt`](posthoc-note1-e193-b.txt) and
[`posthoc-note1-e193-b.json`](posthoc-note1-e193-b.json) ("output §" below), and a re-run from this tree writes both byte for byte. § 5's
figures are read from the registered reducer's output for this sitting, `x04-e193-B.json` (sha256 `75c23d05...`, the bytes verify-e193d
re-derived), which the records lane commits into this directory after this note. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note,
the script, its two outputs, `README.md` and `SHA256SUMS`, so the line numbers below refer to their committed bytes. The registration's
and the kit's files named below are under `tools/claims-v3/e193/`, unchanged since they were committed: `E193.md` (`61f0c2df...`), the
runner `proposal/src/run_x04.py` (`26d08862...`) and the reducer `proposal/src/reduce_x04.py` (`98bbc174...`) in
`SHA256SUMS-e193-registration` (`b17d58a4`); `KIT.md` (`7e6b83ae...`) in `SHA256SUMS-e193-kit` (`45d45c12`). Interpreter:
`/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E193.md and the kit as committed), **measured** (the session's committed
files), **post hoc** (desk readings after the data, deciding nothing).*

## 1. The two moments, and the card-minutes (the verifier's nit 2)

README.md names both moments (line 78): step 7's config read at 11:48:35 PST, "this lane's first card command", and the session's holder
check at 11:48:51, "the session's first card command" (T0 1794772131; `session/first-card-command.txt`; `session/session.log` line 6).
The registered one is the second: E193.md 6 counts the cap "from the sitting's first card command (its first holder check)" (line 196),
and the kit names the session's holder check (KIT.md line 107). Counted to the session's end (12:16:41 PST, `session/session.log` line
15; measured, output § 1):
- from the holder check, **27.83 card-minutes** (1,670 s), as line 37 gives it: the registered count;
- from step 7's read, **28.10** (1,686 s).

Both are under the cap of 50. Had the deadline (12:36:51 PST, T0 + 2,880 s, `session/session.log` line 8) counted from step 7's read, it
would have come 16 s earlier, at 12:36:35. The main run ended at 12:16:41: 20 min 10 s before the deadline as set, and 19 min 54 s before
that earlier one. Sitting A's note 1 gives its own figures: 43.08 and 43.43 card-minutes against its cap of 60.

## 2. The die's peak was read many times; README.md gives its last time (the verifier's nit 3)

README.md line 44 gives the main run's die peak as "52 C (12:16:23; lowest 49 C)", and line 69 the smoke's as "die 50 C (11:50:26; lowest
49 C)". From each runner call's telemetry (measured; output § 2; `temp_c.minshire[0]`, whole degrees, ten samples a second; times PST):

| runner call | the die's peak | samples at it | first | last | the lowest |
|---|---|---|---|---|---|
| main run, `x04/` (15,638 samples) | 52 C | **1,338** | 11:52:45.957 | 12:16:23.218 | 49 C: 506 samples, 11:50:35.185 to 11:51:37.376 |
| smoke, `smoke/` (1,035 samples) | 50 C | **41** | 11:50:18.173 | 11:50:26.986 | 49 C: 994 samples, 11:48:51.339 to 11:50:34.898 |

README.md's 12:16:23 and 11:50:26 are the last samples at each peak. The board's peaks are two samples each, 0.1 s apart, in the second
README.md gives: 32.84 W at 12:16:10.100 and 12:16:10.200 (the main run; its lowest, 22.60 W, at 11:50:53.917 and 11:50:54.017) and
32.19 W at 11:50:19.574 and 11:50:19.674 (the smoke; its lowest, 22.47 W, at 11:49:22.393 and 11:49:22.493).

## 3. The rest after sitting A, and the kit's reading of "the sitting's first card command" (the verifier's note 6)

**What is registered.** E193.md 6 asks for "at least 40 minutes between sitting 1's end and sitting 2's first card command" (line 193),
and counts each sitting's cap "from the sitting's first card command (its first holder check) to its sampler's stop" (lines 196-197). Its
table names the sittings "session A" and "session B" (line 180). E193.md 17 asks the kit for "the look (`et-who`, `who`, `uptime`, `ps`)
before and after", apart from the sitting (lines 450-451). The kit, committed in `45d45c12` before any datum, reads the term: "**The first
card command** is the session's holder check (`et-who --check`), before the start config read: the cap counts from it, **its time
stamped as the check starts**" (KIT.md line 107; the session's step 2, line 43).

**What ran before the session:**
- **k6's look** (step 4) at **11:22:29 PST** (README.md line 113), 14 min 7 s after sitting A's end. It runs `et-who`, `ps`, `who` and
  `uptime` on the box. `et-who` runs `et-holders`, which "never opens /dev/et*: fuser only stats the node and the /proc/<pid>/fd links"
  (`tools/lab/et-holders` line 4). Like the session's own `et-who --check`, which "sends no device command" (KIT.md line 203), it sent
  nothing to the card. It is a runbook step before the session (KIT.md line 82), as are the sync, the build's wait, step 7's reads and the
  dry pass; it is not the sitting's holder check.
- **Step 7's config read** at **11:48:35 PST** (line 77): reads through E128's guard, nothing set. It was the first command any step sent
  to the card for this sitting: README.md line 123 says steps 0 to 6 "send no card command".

**Measured** (output § 1). Sitting A's session ended at 11:08:22 PST (A's `session/session.log` line 15), so the rest opened at 11:48:22.
- To step 7's config read (11:48:35): 2,413 s, **40 min 13 s**.
- To the session's holder check (11:48:51): 2,429 s, **40 min 29 s**.

Step 9's rest rule read the same on the box: "rest: 40 minutes since E193's session end" (line 78).

**Both readings:**
- **The kit's** (stated before any datum): the rest runs to the session's holder check, 40 min 29 s, and is **met**. It is met too if the
  first command sent to the card is taken instead: step 7's read, 40 min 13 s.
- **The look's `et-who` read as the sitting's "first holder check":** the rest would be 847 s (14 min 7 s), short of 40 minutes, and the
  cap would count from 11:22:29, giving 54.20 card-minutes against 50. E193.md 11 would then read the rest, a gate before the sampler, as
  "no sitting: no data" (line 303).

**What decides** is E193.md's own text, with the reading it leaves to the kit. E193.md 17 lists the look before and after the sitting,
apart from it, and E193.md 6 counts from the sitting's own holder check. The kit named that check before any datum as the session's
(KIT.md lines 43 and 107). Under that reading the look is a step before the sitting, not its first card command. So **the as-run reading
is the registered one: the rest was met, by 29 s, and by 13 s to step 7's read.** README.md's rest row (line 78) stands as written.
Nothing departed from the registration, so no amendment was owed.

## 4. The device output files hold the last device process only (the verifier's nit 4)

README.md's Files table (line 172) lists each runner call's `device-stdout.txt` and `device-stderr.txt`. The registered runner opens both
afresh, for writing, for each device process (`proposal/src/run_x04.py` lines 279-280), so each file holds only the last device
process's output (measured; output § 3):
- `x04/device-stdout.txt`: 10 X04 lines. Each equals exactly one record of `x04/runs.jsonl`, and they are its last 10: the main run's
  last device process, pass 8, block C, `spin2` at position 14 (`x04/run.log`: "pass 8 block C spin2: 10 launches, exit 0", then "done").
- `smoke/device-stdout.txt`: 5 X04 lines, the last 5 records of `smoke/runs.jsonl`: the smoke's tenth and last device process, block C's
  `spin2`.
- Each `device-stderr.txt`: 47 lines and 3,686 bytes with one "PCIe target:" line, the device layer's report from one process.

Every launch's record is in `runs.jsonl`: the runner writes one line per launch (`run_x04.py` line 64; the file opened for appending,
line 484), 1,350 for the main run and 57 for the smoke.

## 5. The per-op prices over spin2 are negative at the sparse ends, as computed (the verifier's note 7; post hoc, deciding nothing)

E193.md 7 registers "the `fadd.ps` and `fsgnj.s` density lines (W against class instructions a second, with the per-op pJ over `spin2` on
the board and the minion rail)" (lines 229-230). The registered reducer computes each price as the arm's watts over idle less `spin2`'s,
divided by the arm's class instructions a second (`reduce_x04.py` lines 348-354). From `x04-e193-B.json` (post hoc):

| arm | class instructions a second | board W over idle | per op over `spin2`, board | per op over `spin2`, minion rail |
|---|---|---|---|---|
| `faddps_p16` | 2.570e10 | 2.401 | **-4.53 pJ** | **-5.75 pJ** |
| `faddps_p8` | 5.142e10 | 3.081 | 10.96 pJ | 9.56 pJ |
| `faddps_p4` | 1.028e11 | 4.261 | 16.96 pJ | 15.17 pJ |
| `faddps_p2` | 2.056e11 | 6.200 | 17.91 pJ | 15.67 pJ |
| `faddps_p1` | 4.118e11 | 8.785 | 15.22 pJ | 13.39 pJ |
| `fsgnjs_p8` | 5.147e10 | 2.312 | **-4.00 pJ** | **-4.62 pJ** |
| `fsgnjs_p4` | 1.030e11 | 2.902 | 3.74 pJ | 2.58 pJ |
| `fsgnjs_p2` | 2.059e11 | 3.696 | 5.72 pJ | 4.94 pJ |
| `fsgnjs_p1` | 4.119e11 | 4.625 | 5.12 pJ | 4.53 pJ |

`spin2` read 2.518 W over idle on the board (16 runs) and 2.163 W on the minion rail. Three sparse arms sit below it on the board:
`faddps_p16` (2.401 W), `fadds_p16` (2.372 W) and `fsgnjs_p8` (2.312 W). Their prices over it therefore come out negative, as computed,
and their anchor-detrended values (the reducer's `board_detrended_w`: 2.393, 2.384 and 2.317 W) sit below it too. Both lines' intercepts,
their watts at no class instructions, are below `spin2`: 2.346 W for `fadd.ps` and 2.191 W for `fsgnj.s`, 0.172 W and 0.327 W under it.
**The slopes do not use `spin2`:** 16.31 pJ an instruction on the `fadd.ps` line and 6.18 pJ on the `fsgnj.s` line (the fits
`ladder_faddps` and `ladder_fsgnjs`: board watts against class instructions a second, fitted through each ladder's own arms only). The
values are reported as computed. No rule changes, and the reducer's output stands as written.

## 6. What needs no change

- **The word in departure 3** (the verifier's note 5): line 110 quotes the owner's words, which name the lab's chat service; one of the
  round's public-text classes matches that word (the word alone, no id). It names no account, login, credential or access path, and
  E189's and E192's READMEs carry it too. The verifier asks no fix. No change. Sitting A's note 1 quotes the same words.
- **The reducer's seconds** (the verifier's note 8): the registered reducer holds epoch seconds as float64, so `wall_s` and the rates
  built on it differ from an exact millisecond computation by at most 5.1e-8 relative in this sitting; 18 samples sit exactly on a window
  edge, and the reducer included each of them, as the exact reading does (verify-e193d's re-derivation). No printed digit moves. No
  change.

## 7. What this note does not change

`README.md` and `SHA256SUMS` stay as committed. Nothing changes in any datum, in the registered reducer's prices or in E193.md 8's checks:
both are computed after the data commit and committed into this directory by the records lane. The seal is kept: no forecast number is
here, and nothing here scores E193. The gates read as README.md gives them, with § 3's reading of the rest.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `posthoc_note1_e193.py` | the post hoc reader, the same bytes as in sitting A's directory: standard library only, it reads only committed files |
| `posthoc-note1-e193-b.txt`, `posthoc-note1-e193-b.json` | its output for this sitting |
| `SHA256SUMS-note1` | the sha256 of the four files above, `README.md` and `SHA256SUMS` (6 entries) |

Re-run from the repository's top (a re-run under `/usr/bin/python3` 3.12.3 writes both outputs byte for byte):

```
D=docs/reports/data/2026-11-15-e193-x04-clock-sitting-b-aifoundry3
/usr/bin/python3 -I -B $D/posthoc_note1_e193.py --out /tmp/e193n1b
cmp /tmp/e193n1b/posthoc-note1-e193-b.json $D/posthoc-note1-e193-b.json && cmp /tmp/e193n1b/posthoc-note1-e193-b.txt $D/posthoc-note1-e193-b.txt
(cd $D && sha256sum -c SHA256SUMS-note1 && sha256sum -c SHA256SUMS)
```

SPDX-License-Identifier: Apache-2.0

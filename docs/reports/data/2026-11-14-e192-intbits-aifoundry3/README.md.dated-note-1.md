# E192's data README, dated note 1 (Sat 14 Nov 2026; after the data verifier): step 7's config read came 31 min 28 s after E189's end, inside the 40 minutes, and the rest as registered and kitted runs to the session's first card command, met by 7 s; the launch output is here as the bytes of `session/session.log`; the sizes behind checks 2 and 3 (post hoc); no reading changes

*Written on aifoundry2 from about 22:49 PST on Sat 14 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e192d` of Q179, after E192's data verifier `verify-e192d` (Sat 14 Nov 2026, 22:20-22:48 PST: holds with fixes;
one low finding and three nits, none of them a fault in a datum, a price or a check; the registered reduction re-derived from the raw
files by its own code, equal to the reducer's output in all 8,233 fields). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab
`a6e17e83`, git 22:16:26 PST Sat 14 Nov 2026) stay as committed. **No number, rule, price, check or gate reading changes, and nothing is
scored. The forecasts stay sealed: no forecast number is here.** The figures come from
[`posthoc_note1_e192.py`](posthoc_note1_e192.py). It reads only committed files: the 29 files of this directory's data commit, the
registration's list `SHA256SUMS-e192-registration` (30 of 30 OK) and the kit's list `SHA256SUMS-e192-kit` (35 of 35 OK) with the nine
files it reads as text, each pinned by one of them, and E189's session log, at its data directory's `SHA256SUMS`. The registration's and
the kit's files named below (E192.md, KIT.md, the kit's scripts and logs, `proposal/`) are under `tools/claims-v3/e192/`. The script's
output is [`posthoc-note1-e192.txt`](posthoc-note1-e192.txt) and [`posthoc-note1-e192.json`](posthoc-note1-e192.json) ("output §"
below), and a re-run from this tree writes both byte for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note, the script, its two outputs,
`README.md` and `SHA256SUMS`, so the line numbers below refer to their committed bytes. Interpreter: `/usr/bin/python3` 3.12.3 on
aifoundry2. Labels: **registered** (E192.md and the kit as committed), **measured** (the session's committed files), **desk check of
code**, **post hoc** (desk readings after the data, deciding nothing).*

## 1. The rest, and step 7's config read (the verifier's finding 1, low)

**What is registered.** E192.md section 10, line 256: "E192's first card command at least 40 minutes after the end of the previous
session of ours on that card", and line 257: "the next session of ours there at least 40 minutes after E192's end". Two lines above,
line 254: "The cap is 65 card-minutes from the session's first card command". The kit names that command (KIT.md lines 67-68): "the
first card command, the per-sensor probe ... the session's card time and its cap count from it". Its rest rule (line 177) is that "no
E192 session starts within 40 minutes of the end of our last real session on the card", read on the box at step 9 (line 166), which
comes after step 7, k6's reads (line 164).

**What happened** (measured; output § 1):
- **E189's session end:** 20:27:30 PST (E189's `session/session.log` line 67, its data commit `fa9098c4`). The rest opened at 21:07:30.
- **Step 7's config read** (`ettelem config` through E128's guard: five READs by the kit's audit, `logs/dmcmd-audit-e192.txt` lines
  12-16; TDP 0 W / 65 °C / max_power / 600 MHz / 523 mV; nothing set): 20:58:58 PST by README.md lines 72 and 97. The step ran
  20:58:57-20:58:58 by the card lane's step log on the desk, which is not committed. That is **1,888 s (31 min 28 s) after E189's end**,
  inside the 40 minutes.
- **The session's first card command, the per-sensor probe:** 21:07:37 PST (`session/first-card-command.txt`, T0 1794719257;
  `session/session.log` line 4). That is **2,407 s (40 min 7 s) after E189's end**, 7 s after the rest opened and 519 s after step 7's
  read.
- **The die** read 49 °C at the session's first sample (21:07:38.022 PST), the lowest of the session. Thermally the read was immaterial,
  as the verifier found: five reads, no load.

README.md's rest row (line 81) gives the session's rest, "40 minutes after E189's session end", and line 72 lists the read "before the
session (20:58:58 PST)", but no line sets the read against the rest. A management read came inside the 40 minutes, 8 min 39 s before the
session's first card command. This note adds that.

**Both readings:**
- **As run (the kit's reading, stated before any datum):** the rest runs from our previous session's end to the session's first card
  command, the probe: 2,407 s against 2,400 s, **met by 7 s**. Step 7's read is a read before the session, outside the rest as kitted.
- **Line 256's sentence alone, word for word:** if "E192's first card command" means the first command sent to the card for E192 at
  all, that was step 7's read, **512 s (8 min 32 s) short** of the 40 minutes. Section 11 (line 265) then reads the rest, a gate before
  the sampler, as failed: "no session: no data".

Neither reading moves the card time. The cap counts from the session's first card command (line 254; KIT.md line 189): 3,571 s of
3,900 s. From step 7's read to the session's end is 4,090 s, a span no registered rule counts.

**The rule that decides** is E192.md's own text, read whole, with the reading it leaves to the kit: section 17 asks the kit for "the
40-minute rest rule read on the box (every session-log form of ours there)" (line 394). E192.md places the rest between sessions:
- section 10 counts the card time from "the session's first card command" two lines above the rest (line 254), and ends the rest's
  other side at "the next session" after "E192's end" (line 257);
- section 12 orders the runs "after the session(s) of ours already on aifoundry3 that day, with the rest between" (line 277);
- section 11 counts the rest among the gates "before the sampler" (line 265);
- its protocol knows the session's commands only: "every device command the session's chain sends (host, heater, sampler,
  `et-who`)" (section 3, line 130). It registers no config read; that is k6's step 7, which the kit adds.

The kit, committed in `a6fe5c20` before any datum, reads the term the same way. The probe is "the first card command", from which "the
session's card time and its cap count" (KIT.md lines 67-68 and 189), and the rest rule refuses an E192 session within 40 minutes (lines
166 and 177; section 7, line 291). So **the as-run reading is the registered one: the rest was met, by 7 s, and section 11's row does not
apply.** Nothing departed from the registration, so no amendment was owed (E192.md line 16). README.md's rest row was incomplete, not
wrong, and this note completes it.

## 2. A line for the records: the next sessions of ours on aifoundry3

E193's kit has E192's order: its step 7, k6's reads, then its rest rule at step 9 (`tools/claims-v3/e193/KIT.md` lines 86 and 88, kit
`45d45c12`). Until a kit orders them otherwise, a card day of ours on aifoundry3 runs step 7 after the rest has opened, or its data
README sets step 7's time against the previous session's end and states the reading of section 1. The next session of ours on the card
rests until 22:47:08 PST (README.md line 121), which had passed when this note was written.

## 3. The launch output is here as the bytes of `session/session.log` (the verifier's nit 2)

`box-manifest.txt` lists 26 box files (output § 2). 25 of them are files here at the box's sha256; `run/telemetry.jsonl` is checked
through the uncompressed bytes of `run/telemetry.jsonl.gz`. The 26th, `build/e192/launch-T1794719257.out` (line 21), is not a file here:
- **What it is:** the wrapper's output. Step 9 started the wrapper with its stdout and stderr sent to that file
  (`rb/s11_a3_session_e192.sh` lines 37 and 39).
- **Why it is not a file here:** `collect_e192.py`'s assemble step copies the session's directory `build/e192/T<T0>/` into `run/` and
  `session/` (line 111), the build record into `build/` (line 137), and `box-manifest.txt` (line 146), and nothing else.
- **Why no byte is lost:** its sha256, `8a53b924...`, is that of `build/e192/T1794719257/session.log` (line 19), which is
  `session/session.log` here (1,098 bytes, 8 lines). The wrapper's `say()` writes each line to its session log and to its output
  (`session_e192.sh` line 53), and the equal bytes show that nothing else wrote there.

So README.md lines 128-129 read: the copy back was COPY EXACT against the box's manifest (26 files at the box's sha256, nothing else);
the data directory keeps 25 of them as files, and the launch output as the identical bytes of `session/session.log`.

## 4. The sizes behind checks 2 and 3 (the verifier's nit 3; post hoc, deciding nothing)

Registered: check 2 (E192.md line 206) includes "L1 data misses 0"; check 3 (line 207) reads "Instruction-cache misses per iteration
equal across arms (the 1 KB loop stays resident)". The kit's checker, `check_e192.py`, decides them after the data commit; its output is
committed by a later lane, beside this directory. The sizes below come from `run/runs.jsonl` (output § 3). The counters are neighbourhood
sums, read before and after the timed loop, with each of the 128 neighbourhoods counted once (`proposal/src/host/main.cpp` line 399;
`proposal/src/intbits_args.h` lines 49-50). The iterations are summed over the 1,024 participants: about 3.67e8 a launch (main.cpp line
392).

- **L1 data misses:** no launch of passes 0-8 reads 0 (0 of 3,240), so no run (0 of 324) meets check 2's "0".
  - A launch reads 8,096-8,585 (mean 8,314.8, about 65 a neighbourhood).
  - The 32 arms' means are 8,281.4-8,329.7 over passes 0-8, and 8,282.5-8,333.2 over the measured passes without the burn-ins.
  - Per iteration: about 2.26e-5.
- **Instruction-cache misses** (the measured passes 1-8 without the burn-ins, as check 3 counts them):
  - The arms' means are 4,612.7-4,621.2 a launch in 30 arms, and 4,480.6 in `xor.z` and in `xor.a.f2`.
  - Single launches read 4,484-4,638 in the 30 arms (22 of 2,560 below 4,600) and 4,480-4,485 in the two `xor` arms; about 36 a
    neighbourhood a launch.
  - Check 3's own quantity runs from 1.21971e-05 (`xor.z`) to 1.25798e-05 (`add.cr.l0`) per iteration: a spread of 3.1% of the lowest.
- **What the sizes say (post hoc):** both counts are thousands a launch (about 4,600 and 8,300) against about 3.67e8 iterations, far
  below one a loop body.
  Every launch runs the same window of 240,000,000 cycles, so these records cannot tell a count that comes once a launch from a slow
  rate. Check 3 registers no threshold, so its checker reads EQUAL as identical (`check_e192.py` lines 10-11), and a 3.1% spread is not
  identical. Check 2's "0" has no tolerance. These sizes stand beside the checker's verdicts and change neither.

## 5. The account label (the verifier's nit 4)

README.md lines 16 and 116 name the orchestrating session's account label. It is in no class the lab keeps out of public text: not a
lab login, a credential or an access path. The verifier asks no fix. **No change.**

## 6. What this note does not change

`README.md` and `SHA256SUMS` stay as committed. Nothing changes in any datum, in the registered reducer's prices, or in the section 7
checks: both are computed after the data commit and committed by a later lane. The seal is kept: no forecast number is here, and nothing
here scores E192. The gates read as section 1 gives them.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `posthoc_note1_e192.py` | the post hoc reader: standard library only, it reads only committed files |
| `posthoc-note1-e192.txt`, `posthoc-note1-e192.json` | its output |
| `SHA256SUMS-note1` | the sha256 of the four files above, `README.md` and `SHA256SUMS` (6 entries) |

Re-run from the repository's top (a re-run under `/usr/bin/python3` 3.12.3 writes both outputs byte for byte):

```
D=docs/reports/data/2026-11-14-e192-intbits-aifoundry3
/usr/bin/python3 -I -B $D/posthoc_note1_e192.py --out /tmp/e192n1
cmp /tmp/e192n1/posthoc-note1-e192.json $D/posthoc-note1-e192.json && cmp /tmp/e192n1/posthoc-note1-e192.txt $D/posthoc-note1-e192.txt
(cd $D && sha256sum -c SHA256SUMS-note1 && sha256sum -c SHA256SUMS)
```

SPDX-License-Identifier: Apache-2.0

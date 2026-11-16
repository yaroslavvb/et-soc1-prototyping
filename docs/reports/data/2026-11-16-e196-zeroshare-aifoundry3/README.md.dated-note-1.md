# E196's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): the leakage slope is a registered input, not a measured price; the approach as it ran; two nits answered (post hoc)

*Written on aifoundry2 from about 05:46 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e196d` of Q191, after this directory's data verifier `verify-e196d` (holds with fixes: one low finding and three
nits, none of them a fault in a datum, a check or a verdict; with its own reduction code, written from E196.md and run on the committed
raw files, it matched the registered reduction's output on all 4,211 numeric values exactly, and the registered reducer re-run on its
copy gave a byte-equal file). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `4bc7a07a`, 05:13:21 PST Mon 16 Nov 2026)
stay as committed. **No number, rule, verdict or check reading changes, nothing is scored, and no forecast number is here** (the model
session scores its sealed forecast privately). **Every figure below is post hoc to the data commit.** Where the figures come from: (a)
the registered reducer [`reduce_e196.py`](../../../../tools/claims-v3/e196/reduce_e196.py) (sha256 `c58c6690...`) and the section 8
checker [`check_e196.py`](../../../../tools/claims-v3/e196/check_e196.py) (`e1038e44...`), run by the README's section 5 lines on this
directory: this lane re-ran both from the repository's tree at `4bc7a07a` and got step 13's bytes (section 5); (b) this directory's raw
files (`run/runs.jsonl`, `run/marks.jsonl`, `run/telemetry.jsonl.gz`), read at the desk with this lane's own code; (c) desk checks of
the registered code, by line number at the sha256 listed in section 5; (d) verify-e196d's readings where named. Interpreter:
`/usr/bin/python3` 3.12.3 with numpy 1.26.4 on aifoundry2, for step 13 and for this lane's re-run and counts. Labels: **registered**
([`E196.md`](../../../../tools/claims-v3/e196/E196.md), the kit), **measured** (the session's records, and the registered reducer's and
checker's outputs from them), **desk check of code**, **post hoc** (desk arithmetic after the data, deciding nothing), **REPORTED**
(verify-e196d's, not re-run here).*

## 1. The leakage slope, 0.1994 W/°C, is a registered input, not a measured price (verify-e196d's finding 1, low)

E196.md 7 (registered) runs the reducer with "its defaults otherwise (leakage slope 0.1994 W/C, E78's fit; ...)". The slope enters each
pass run's S ("less the leakage slope times the die difference") and Bc ("the busy mean less the slope times (die - 58 C)"), and "every
result also at leakage slopes 0 and 0.3803 W/C". E196.md 14: "the leakage slope is registered (0.1994 W/C), with the reduction's
sensitivity arms at 0 and 0.3803 W/C beside every result." The reducer fits no slope: `--leak` is a fixed input with that default
(`reduce_e196.py` line 133; desk check of code).

- **The label: 0.1994 W/°C is registered, an input to the reduction (E78's fitted slope), not an E196 measurement.** It stands beside the
  two sensitivity slopes, 0 and 0.3803 W/°C, and it is not in the list of measured, reduced prices.
- **Where it shows:** the reducer writes the slope it used as its output's top-level `leak_W_per_C` (0.1994), and the results at the two
  other slopes under `sensitivity` (`leak_0` and `leak_0.3803`, each with `arms_D_W` and `derived`). The prices in that output are
  measured, at the registered slope; the slope itself is the input.
- **What carried the wrong label:** the card lane's own report (not committed) listed "leak: 0.199 W/C" among its measured, reduced
  prices, and its working list of prices did the same. Nothing committed in this directory names a leakage slope (desk check: every
  text file of `4bc7a07a`'s directory, and the unpacked telemetry). The reduction's dated note, which publishes the prices, is to list
  the slope under the reduction's registered inputs.

## 2. The approach as it ran (verify-e196d's finding 2, nit; post hoc desk reading)

**The registered words** (E196.md 5, "quoted; E60's and E78's"): "heater launches ... while the die reads below 59 C, at most 15; then
idle until it reads 58 C or less; then at least 2 s with no device process, the reading in [57.5, 58]; at most 120 s of waiting. A run
is on protocol only when that approach was kept".

**As the kit's runner runs it** (desk check of code, `run_block_e196.py` lines 288-289 and 314-350; the runner is on the kit's box
list, which the box check read OK):

1. heater launches while the reading is below 59 C (at most 15);
2. idle until the reading is 58 C or less (at most 120 s);
3. then wait only until 2 s have passed **since the end of the last device process** (the last heater launch, or the run before),
   leaving the wait early if the reading leaves [57.5, 58];
4. if the reading fell below 57.5 C, heat again and start over.

A run is on protocol when the preheat was reached, nothing timed out, **the reading at the close** is in [57.5, 58], and at least 2 s
have passed since the last device process ended. The 2 s therefore count from the previous process's end and take in the idle of step
2: the band is required at the close, not through the 2 s. The proposal's runner (`proposal/src/run_block.py` lines 267-301) has the
same logic, and so has E78's ([`run_e78.py`](../../../../tools/claims-v3/kinds/run_e78.py) lines 196-232), whose head (lines 10-14)
gives the rule's purpose: no device process in front of the idle bracket [t0 - 1.2, t0 - 0.2) s (E79's amendment A7 had found brackets
that began before the previous process ended).

**What the readings show** (post hoc: this lane's own count from `run/runs.jsonl`, `run/marks.jsonl` and `run/telemetry.jsonl.gz`,
the die reading as the runner and the reducer read it, `temp_c.minshire[0]`; equal to verify-e196d's count):

| runs | how many | the highest die reading in the 2 s before the device process started | a reading outside [57.5, 58] in the reduction's idle bracket |
|---|---|---|---|
| pass runs (7 passes: the arms and each pass's first and last `K.pi` anchor) | 210 | 58 °C in 12, 59 °C in 132, 60 °C in 66: **198 of 210 at 59-60 °C** | **132 of the 209 kept runs** (59 °C each time; no other value) |
| train anchors (the first and last `K.pi` anchor of T1 and of T2) | 4 | 59 °C in 4 | 0 of 4 |

Every run's recorded closing reading (`start_c`) is 58 °C but one: pass 5 seq 22 (`I.Z.m0FFF`) closed at 59 °C; it is the one run not
on protocol and the reducer's one run set aside ("approach off protocol"). Each device process started 0.181-0.384 s (median 0.184 s)
before its first launch.

**Both readings, and which rule decides.** (a) The sentence read alone, the reading in [57.5, 58] through the whole 2 s, would put
198 of the 210 pass runs and all 4 train anchors off protocol (each of them read 59 or 60 °C during those 2 s; no run read below
57.5 °C there). (b) The rule as the kit's runner codes it (the band at the close; the 2 s counted from the last device process's
end) puts 209 of the 210 pass runs and 4 of 4 train anchors on protocol, as recorded. **The registered code decides:** E196.md 5 quotes
E60's and E78's approach, and E78's runner runs it as (b); the kit's runner writes each run's `on_protocol` by (b); and the registered
reducer, run unchanged (E196.md 7), reads the approach through that recorded flag alone (`reduce_e196.py` lines 257-258: a run whose
flag is false is set aside). Nothing is re-read or re-scored under (a), and no reading changes.

**What the bracket's 59 °C readings touch** (desk check of code, `reduce_e196.py` lines 29-31): S subtracts the slope times (the die
reading in the window less the die reading in the bracket), so a 59 °C reading in the bracket enters S through the registered slope
(section 1); the primary form, D over the leak-corrected busy means (Bc = B - slope x (die - 58 C)), does not read the bracket. Reported;
nothing re-computed.

## 3. The two nits

1. **The data commit's message** (round-wide, not E196's). The round's commit helper appends two standard trailer lines (a session
   reference and the co-author line) after the card lane's scans have read the subject and body; read over the full message, the
   network class finds the session link and the e-mail class the co-author address (REPORTED).
   [E188's data note 1](../2026-11-15-e188-one-number-r4-aifoundry3/README.md.dated-note-1.md), section 1, and
   [E195's data note 1](../2026-11-16-e195-x09-dramtoggle-aifoundry3/README.md.dated-note-1.md), section 3 item 4, are the same case. A
   round convention, for the orchestrator to decide; nothing in E196 changes. This note's commit carries the same two lines, and this
   lane's scans read its full message, trailer included, and name those two hits.
2. **One outcome word.** The registered word is **RAN WHOLE** (the kit's README form,
   [`DATA-README-FORM-e196.md`](../../../../tools/claims-v3/e196/DATA-README-FORM-e196.md) line 21: "RAN WHOLE (the smoke, T1, T2, <6|7>
   passes)"), and the data commit's subject and the README's title use it. The card lane's report said RAN FULL, the round's word for a
   card lane that ran its plan. Both name one outcome: the smoke, T1, T2 and 7 passes, with no stop. The lab's records for E196 use
   RAN WHOLE.

## 4. What stays

`README.md` and `SHA256SUMS` stay as committed in `4bc7a07a`, and no committed data file changed. Every check word stands as the
registered checker prints it (measured): "CHECKS-E196: 1 8 of 8 REPRODUCE (0 not computed); 2 EQUAL; 3 STRAIGHT; 4 PASS (108 of 108 ok;
108 at the full plan); 5 PASS (209 kept runs, 672 train launches, 0 deviations); 6 T1 AGREE T2 AGREE". The reduction's dated note is to
publish them with the prices. Nothing is scored here, and no forecast number is in this note.

## 5. Files

| path | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` |

The code this note cites by line number, at these sha256 (each pinned by E196's registration or kit sums, but `run_e78.py`, unchanged
since E78's registration):

| file | sha256 |
|---|---|
| `tools/claims-v3/e196/E196.md` | `89cf0460fbb6e8189a9ffdeb9e166dd14441a68f48d1d5038a55e6f9a4f18235` |
| `tools/claims-v3/e196/run_block_e196.py` (the kit's runner) | `f01d3989309dddcbfe067f9684de4b047630873865184a23800e214525f857bf` |
| `tools/claims-v3/e196/reduce_e196.py` (the registered reducer) | `c58c6690016f18e5dac62ba620086f3cefda812cab9e93d2a929cb1aa207f3f7` |
| `tools/claims-v3/e196/check_e196.py` (the section 8 checker) | `e1038e4449214bd8137b71c585bb13f4e5d4420680b7b9a0a3809d0853c15477` |
| `tools/claims-v3/e196/proposal/src/run_block.py` (the proposal's runner) | `3d94ba62fa7682989f359eb50553ac33ffb0830275a9c803991e5aca8c456b99` |
| `tools/claims-v3/e196/DATA-README-FORM-e196.md` | `814b36232f82a3cc1ad1a3ccc6d9dbf9587f39a3d96a5d5bbffb11f97a16da64` |
| `tools/claims-v3/kinds/run_e78.py` (E78's runner) | `f3efd7838686dbd158c8f45a82ab59f4beda68479d792d73a36265e48784bb73` |

Step 13's four outputs (measured), which the reduction's dated note is to commit, and this lane's re-run of the README's section 5 lines:

| output | sha256 (step 13) | this lane's re-run |
|---|---|---|
| the reducer's JSON (`x14-e196.json`) | `3a020dc8b43fd1402c825cc8fc63f0069bfe9dabaa5c262ec6a5237b6dae3bad` | the same bytes |
| its printed lines (`x14-e196.txt`) | `39e6571460cbebaaca5ab4b3712b4348ff62bcf03bf8a39a90d6f3f37b9191d8` | the same bytes but the end of line 1, where each run prints the folder it wrote its JSON to |
| the checker's JSON (`checks-e196.json`) | `1c1db76b7090efa801f3931ebf8558d69cccbfbb20eb228c622193e7f215f0d8` | the same bytes |
| its printed lines (`checks-e196.txt`) | `222342b55930f4979f9eb2b84ec5507a0fafbdd8f240815372fa908f0d58498f` | the same bytes |

SPDX-License-Identifier: Apache-2.0

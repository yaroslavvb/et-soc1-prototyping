# Ledger v3: the ledger's repair after the blind days, frozen before E201 (Q193)

**The freeze line.** `tools/ledger/frozen-v3.json`, sha256 **`4b43f510fdf2f1df1f940303247a523b0b6fb409eb853161c7621b458635014b`**
(also in `tools/ledger/frozen-v3.json.sha256`), frozen Mon 16 Nov 2026 04:44 PST by `tools/ledger/freeze_ledger_v3.py` under
`/usr/bin/python3` 3.12.3 on aifoundry2, on GitHub main `250f825b`. Beside every constant it pins, by sha256, the model code
(`ledger_v3.py` and the five files it rests on: `measured_ledger_v3.py`, `programs_ledger_v3.py`, `freeze_ledger_v3.py`,
`tools/counter/l1_model.py`, `tools/counter/ledger_interp.py`), every input it was made from, what a new configuration's counts
and lines are computed from (the kernel's committed disassembly, `workloads/ledger/ledger_desk.py`) and every measured day it
reads. E201, the fix's test day, freezes its forecasts from this file, with ledger v2 beside it as frozen, before any E201
datum. **It supersedes a first freeze** (sha256 `bd6e71cae962972437d5b2c7827f4dd9a43b613a89669e48afeba60c30ef2304`, 03:40 PST
the same day), which was never landed: v3 was re-frozen before the land, before any E201 datum, to answer the adversarial
verify's findings (the last section here). No printed reading moved.

*Desk only: no card, no device, no simulator run, nothing sent to a card. Labels: **measured** (the cards' committed records),
**registered** (frozen forecasts and rules), **desk check of code** (this commit's scripts over committed files), **a priori**
(from records older than the blind days), **POST HOC** (fitted to, chosen after, or read against a day whose data came first),
**REPORTED** (read, never scored).* **Every reading of E189, E191 and E194 in this directory is POST HOC: ledger v3 was written
after their data, two of its constants are fitted on E189's and E191's, and its rule 7 took its form after E194's. The blind
scores stand; nothing here changes a frozen number.**

## What it is

Step 5 of the owner's private checkpoint of Wed 11 Nov 2026 asks the lab to repair whichever part of the ledger the blind day
points at, and then to check the repair in one card session. The blind days (E189 on aifoundry3 card 0, E191 on aifoundry1 card
1) pointed at two parts: the seconds (about 30% off for the copy, SHA-256 and the sort) and the bytes by level (J over idle short
for SHA-256 and the sorts, by the price of the lines past the L1). The two step-5 diagnoses (Q193, one from the ledger's terms and
the rails, one from the cycle counters and the counter's counts) agreed, and neither found the data columns too coarse. Ledger v3
is ledger v2 with seven rules, each switchable; with all seven off it is v2, number for number. `tools/ledger/V2-TO-V3.md` has them
term by term.

| rule | what changes | rests on | label |
|---|---|---|---|
| r1 | seconds of scalar code: 2.0 hart-cycles an instruction whose own row is a one-cycle row, c_br = 13.579 a taken branch or jump, any other instruction (here mul and csrr) at its own row | the catalogue's rows less their measuring loop; the blind days' cycle counters | a priori; c_br FITTED, POST HOC |
| r2 | seconds of memory code: the longest of issue, the L2's line time and the DRAM traffic (3 B a byte copied) at R_dram = 49.69 GB/s (aifoundry3; 49.70 card 1) | E48's line cycles; the blind days' copies | a priori; R_dram FITTED, POST HOC |
| r3 | lines past the L1 from a 512 B L1 model at each card's own E48 line prices; the level by the working set | facts-l1.json; E48 | a priori |
| r4 | the DRAM copy at its card's own catalogue rows, plus 1.19 W for its time past the store probe's own | the catalogue; E23 (the band down to E193's stall price, 0.292 W) | a priori |
| r5 | the forecast die 50 C; wall seconds = seconds + 1.5 ms | the blind days' measured T0 and launch overhead | POST HOC (inputs) |
| r6 | rules 2-4 read the card's own column, never aifoundry3's | E191's copies | rule |
| r7 | a governed card above its idle clock: its clock-state base for the time at the busy clock, the governor's climb done at the idle clock | E136's relation (aifoundry2); E190's climb | numbers a priori; FORM POST HOC |

**Fitted on the blind days: two constants**, c_br (13.579; each card alone 13.579; one program left out 13.320-13.992; a priori
16.578) and R_dram. **Chosen after the blind days** (POST HOC, in `frozen-v3.json` > `post_hoc_choices`): the forecast die and
the 1.5 ms a launch; the max() of rule 2; rule 4's awake analog and its point; rule 7's form; the structure of rules 1-4.
**Unchanged:** every instruction price, the card at rest and the leakage rise, the tensor, scratchpad, L2-stream and mesh terms,
sparse parity's whole load, the clock scaling of prices, and the multiply-add (no refit).

## The round trip: with all seven rules off, v3 is v2 (desk check of code)

`roundtrip-v3.txt`: v3 with no rule on against the three frozen v2 forecasts (E189 aifoundry3, E191 card 1, E194 aifoundry2 at
800 MHz) and their frozen scorers, **291 numbers, every one the same** at the files' 6 significant digits (within 5e-6 relative,
the rounding's bound): for each plain configuration the seconds' point and two-sided band, J over idle and its band, J with the
card at rest and its band, the instruction and byte terms, and the given-seconds J over idle and J at rest of each of the 4 passes;
sparse parity's J over idle and J at rest. So the code paths that v3 does not change reproduce v2 exactly, on three cards and two
clocks.

## The readings (POST HOC; `readings-v3.txt`, every number in `readings-v3.json`)

Errors are forecast / measured - 1 by E189's registered rules, applied pass by pass: S1 J over idle given the measured seconds;
S1T J with the card at rest given the measured seconds and die; S2 the seconds, E189's test in full (the mean t_k inside the
forecast's two-sided band and within 15% of its point); S2T J with the card at rest at the forecast seconds and v3's 50 C die; S2I
J over idle at the forecast seconds. Sparse parity's S1, S1T and S2 are its frozen scorer's (v3 = v2 there).

**In sample, and held out across cards** (c_br and R_dram from the other card only: the same numbers, because the two cards count
the same cycles and stream at the same rate, so this hold-out cannot discriminate the seconds):

| card | configuration | seconds | S1 | S1T | S2T |
|---|---|---|---|---|---|
| aifoundry3 | copy, zeros | +0.1% | -5.2% | -0.8% | -1.3% |
| aifoundry3 | copy, random | -0.1% | -3.2% | -0.8% | -1.2% |
| aifoundry3 | SHA-256 | -1.3% | +0.6% | +0.0% | -1.5% |
| aifoundry3 | sort, sorted | +1.2% | +2.4% | +0.1% | +0.6% |
| aifoundry3 | sort, shuffled | -1.1% | -2.0% | -0.2% | -1.8% |
| aifoundry3 | sparse parity (v2's load) | +0.3% | -3.4% | -1.9% | -1.7% |
| card 1 | copy, zeros | -0.0% | +4.2% | +0.3% | -0.5% |
| card 1 | copy, random | +0.0% | -3.1% | -0.9% | -1.7% |
| card 1 | SHA-256 | -1.3% | +4.4% | +0.2% | -2.1% |
| card 1 | sort, sorted | +1.2% | +2.4% | -0.2% | -0.1% |
| card 1 | sort, shuffled | -1.1% | +5.7% | -0.1% | -1.9% |
| card 1 | sparse parity (v2's load) | +0.4% | -6.5% | -2.5% | -3.2% |

E189's rules over the six: aifoundry3 S1 6/6 (rms 3.1%), S1T 6/6, S2 6/6, S2T 6/6; card 1 S1 6/6 (rms 4.6%), S1T 6/6, S2 6/6,
S2T 6/6. The blind scores, which stand: aifoundry3 S1 3/6, S1T 6/6, S2 1/6, S2T 1/6; card 1 S1 1/6, S1T 5/6, S2 1/6, S2T 1/6.

**The hold-outs that can discriminate:**

| hold-out | reading |
|---|---|
| each scalar program, c_br fitted on the other two (both cards) | seconds: SHA-256 -1.3% (c_br 13.540), sort sorted +2.7% (13.992), sort shuffled -1.9% (13.320); S2T -2.6..+1.7% |
| each copy, R_dram from the other copy on the other card | seconds -0.1..+0.1% |
| no blind-day constant (c_br a priori 16.578; R_dram twice the store stream, no skew) | seconds +0.9 / +12.1 / +8.5 / -7.7 / -7.8% (SHA-256, sorted, shuffled, copy zeros, random; card 1 the same); S2 5/5, S2T 5/5 on both cards |
| every price of rules 2-4 from the other card | aifoundry3 S1 4/5 (copy zeros +15.3%); card 1 S1 3/5 (copies -14.3 / -12.5%): the copy needs each card's own DRAM rows (rule 6) |

The J-over-idle gains rest on September prices (E48, the catalogue) and the documented L1, not on blind-day fits; the seconds rest
on c_br for scalar code and R_dram for the copy. E201 is the blind test.

**Each rule alone on v2, and v3 less each rule** (the rms over the five plain programs; `readings-v3.json` has every
configuration):

| day | v2 | v3 | what moves it |
|---|---|---|---|
| E189 (aifoundry3) | S1 14.4%, seconds 30.0% | S1 3.1%, seconds 0.9% | S1: r3 alone 4.8% (v3 less r3 13.9%), r4 alone 13.9% (v3 less r4 4.8%); seconds: r1 alone 17.6%, r2 alone 24.3%, both 0.9% |
| E191 s2 (card 1) | S1 17.8%, seconds 30.0% | S1 4.1%, seconds 0.9% | S1: r3 alone 9.8% (v3 less r3 15.1%), v3 less r4 10.2%, v3 less r6 8.7%; seconds as on aifoundry3 |
| E194 (aifoundry2, 800 MHz) | S1 47.4%, seconds 29.9% | S1 2.9%, seconds 0.9% | S1: r7 alone 6.7%, v3 less r7 40.3%, v3 less r3 6.8%; v3 less r6 2.5% |

**E191's third session (REPORTED, a repeat):** S1 +0.8 / -3.4 / +1.0 / -0.7 / +0.8% (copy zeros, random, SHA-256, sorted,
shuffled), sparse parity -8.4%; S1T -0.8..+0.6%; S2T -3.7..-5.7% at v3's 50 C (that session started its passes at 53.5-54.0 C).

**E194, aifoundry2 under its governor at 800 MHz** (data 72514ce5, frozen scores 5fc8cc27; rule 7's base 8.154 W, E136's):

| configuration | seconds | S1 without r7 | S1 with r7 | S1T with r7 | S2T with r7, 50 C / 55 C | S2I: r7 as frozen; the design's arithmetic; the registered form; lines x (V800/V600)^2 |
|---|---|---|---|---|---|---|
| copy, zeros | +0.0% | -51.5% | +4.2% | +1.2% | +2.4 / +6.5% | +4.2; +1.7; +12.1; +4.2% |
| copy, random | +0.2% | -43.7% | +2.3% | +0.7% | +2.3 / +6.2% | +3.3; +1.2; +9.9; +3.3% |
| SHA-256 | -1.3% | -29.3% | +4.5% | +2.4% | +2.7 / +6.5% | +3.8; +7.6; +18.8; +5.9% |
| sort, sorted | +1.2% | -35.9% | -0.2% | +0.3% | +2.3 / +6.2% | +0.4; +3.2; +12.1; +6.3% |
| sort, shuffled | -1.1% | -37.3% | +0.3% | -0.1% | +0.9 / +4.7% | -0.3; +2.3; +10.8; +4.6% |
| sparse parity (v2's load) | | | | | | -32.9% without r7; -15.2% with it |

v3's seconds transport to a third card at a governed 800 MHz, the copies' DRAM time not following the clock. Rule 7 **as frozen**
takes the climb's share of each burst from v3's own forecast seconds; **the design's arithmetic** (the step-5 design lane's
reading) took it from E194's frozen REPORTED reading, made with v2's seconds, and priced the copies at the idle clock as at 800
MHz. **The registered form** is the base over each launch's whole forecast seconds, as E194.md registered its REPORTED reading
before the data (v2 in that form, E194's own reading: -9.8 / -11.1 / +29.0 / +15.7 / +16.5%). Rule 7's form was chosen after
E194's data: **E194 gives it no support; its blind test is a later aifoundry2 day.**

## What v3 cannot fix (stated before any E201 datum)

1. **Lines past the L2 for scalar code** other than a DRAM copy: no rule (v2 had none). Such a program is flagged outside v3.
2. **Latency-bound code** (a dependent miss chain, a pointer chase): the issue model ignores miss latency beyond what c_br absorbs;
   the L2's line time is a throughput rule.
3. **One hart a minion**: the catalogue has no lone-hart taken-branch row.
4. **The clock transport of the L2's line cycles**: assumed clock-free (E48 measured them at 600 MHz only); R_dram read clock-free on
   E194 (post hoc); a later aifoundry2 day tests the L2's.
5. **The copies' residual on the minion rail** beyond the awake term: stall time or the loads' L1-fill path from DRAM (E48's DRAM
   line, about 136.6 pJ a byte on aifoundry3 against the tensor-load row's 127.3; frozen as `line_prices_pj` > `dram_line_pj_b`,
   the other candidate for the copy's read path).
6. **Awake energy counted twice** between the catalogue's rows (awake at their measuring rate) and E48's line prices: small here,
   larger for a program with more stalls a line.
7. **Card 1's catalogue zeros rows** and its rail split.
8. **Sparse parity's residual** (-3% and -6% on the blind days), and an awake-time price for its other hart and its closing code
   taken from the cycle counts: the registered arm v2c priced those parts that way and read further low, so v3 leaves sparse
   parity's load as v2 froze it. Its operand kind's price
   (int8.pm1) exists for aifoundry3 only: on another card it is carried from aifoundry3, as E191 and E194 registered; rule 6 cannot
   change that.
9. **The integer rows' two offsetting biases** (each row carries its loop's instructions; its random operands are 24-bit): not
   separable on these days.
10. **Data between the two columns** (zeros, random): untested; the blind days did not call the columns too coarse.
11. **The copy's slowest-minion skew** (max over mean 1.048): measured inside R_dram, not explained.
12. **Sparse parity at a governed clock**: -15.2% in J over idle on E194 even with rule 7.
13. **Rule 7's climb** is a median (0.014-1.325 s a burst), and a governed card that leaves its top point (heat, the 65 W board
    limit) is outside rule 7.
14. **The slowest minion against the mean participant**: v3's counts are the mean of the counter's 64 logged participants and the
    seconds score reads the slowest minion; c_br was fitted that way (mean counts against the slowest minion's cycles), so it
    absorbs the blind days' 0.4-0.5% at 512 keys. A configuration whose count spreads more (a 16-key shuffled sort) should
    forecast its slowest participant (`tools/counter/ledger_interp.py` counts every participant) or register the bias.

## The adversarial verify's findings (Q193 verify5), answered

| # | finding | here |
|---|---|---|
| 1 | E201's separation overstated (two forecasts within th of one measurement iff their ratio is at most (1+th)/(1-th)) | E201's text is reg-e201's; v3 ships the test (`ledger_v3.both_can_pass`, checked in `selftest-v3.txt`: 1.105, 1.222, 1.353 at 5, 10, 15%) and every rule's switch for its per-configuration comparison |
| 2 | E193's awake price not used | `p_stall_w`: point E23's 1.19 W (v2's own awake price; a stall on the memory side, as a copy waits on DRAM), band down to E193's stall price 0.292 W for 1,024 minions (`tr_tk_stall2`, a stalled pipeline); E193's spin price (2.53 W) beside it, outside the band; the loads' L1-fill path named (item 5 above); E201's DRAM copy at both ends of the band through the awake term's band |
| 3 | rule 7's form is post hoc | labelled POST HOC in `frozen-v3.json` and here; the registered form and the scaled-lines reading beside it in `readings-v3`; no support claimed from E194 |
| 4 | E201 lacks the per-term readings, a taken-branch test, a full-width integer row | every rule switches on its own (`rules=`); the blind days' per-rule readings are here; E201's own per-term readings and its new arms are reg-e201's |
| 5 | the counters arm can still be dropped | the 512 B L1 model is frozen here (`tools/counter/l1_model.py`, tested on hand-made traces and on the 512-key sort's 640 + 2.75 fills), so v3's lines past the L1 have a frozen count whether or not E201 builds its counters arm |
| 6 | the level rule left out v3's own 512-key sorts | the L2 level is bounded by the L2 (512 KiB a shire), 384 KiB a shire the largest validated; the 512-key sorts are priced (`selftest-v3.txt`) |
| 7 | the slowest minion against the mean participant | item 14 above; `ledger_interp.py` counts every participant |
| 8 | the drafts quoted the checkpoint | no copied text here: the checkpoint is cited by name and paraphrased, with no number from it |
| 9, 10 | what two E201 configurations test; the fitted-constant count | E201's (reg-e201); the post hoc choices are listed beside the two constants |

## The verify of the first freeze (Q193 verify-ledger3), answered before the land

The adversarial verify of the first freeze (bd6e71ca...) re-derived every reading here with its own code from the committed
records (no code shared with v3 or v2; c_br bit-equal, every reading within 1.3e-6) and held with one minor finding and six nits.
Each is answered below; v3 was re-frozen once for all of them (the freeze line above). `tools/ledger/V2-TO-V3.md` has the same
list.

| # | finding | here |
|---|---|---|
| 1 (minor) | rule 1's a-set held mul and csrr, so they issued at a = 2.0 (their catalogue rows read 21.32 and 5.94 hart-cycles after delta); a loop that is 5% mul would read 48% fast | the a-set is the programs' one-cycle mnemonics only (each one's own row within 0.5 hart-cycles of a after delta; andi the widest at +0.14), computed in the freeze; mul and csrr issue at their own rows and c_br is refitted with them there (-8.4e-7 relative). No printed reading moved; in `readings-v3.json` the largest change in an error is 1.0e-6 |
| 2 | no self-test pinned a v3 number | 30 readings (E189 and E191 in sample: seconds and S1; E194: seconds and S1 with rule 7) are pinned at 1e-4 against the verify's independent re-derivation; v3 matches within 1.3e-6 (`selftest-v3.txt`) |
| 3 | S2 was scored by the 15% test alone | S2 is E189's registered test in full, the band and 15% (`readings_ledger_v3.ok_s2`); the 15% test alone is kept as S2-15, a reading only; no verdict changed. E201's scorer registers its own rules |
| 4 | the model's citation; item 8 kept most of a checkpoint phrase | the prescribed citation, and item 8 reworded |
| 5 | run-time inputs not pinned | the kernel's disassembly, `ledger_desk.py` and E191 s3's and E194's `SHA256SUMS` are pinned; the self-test re-hashes every file every pinned `SHA256SUMS` lists |
| 6 | two scripts wrote here by default | both require `--out` (the reproduce line below) |
| 7 | the DRAM copy's byte-row bands not widened at another clock | their high ends take x (V/V600)^2, as rule 3's (no 600 MHz number moves) |

Carried, not new: the simulator-log reader in `tools/counter/l1_model.py` (`--log`) has NOT been run on a real simulator log
(v3's frozen line counts come from the sort interpreter's and the structural traces, which the verify reproduced with its own
LRU cache); rule 7's form is POST HOC (above); and the interpreter's counts at 16, 64 and 256 keys have no counter run of their
own yet: E201's registration freezes its forecasts from the counter's counts of its own configurations.

## Files

| file | what | label |
|---|---|---|
| `../../../../tools/ledger/ledger_v3.py` | the model | |
| `../../../../tools/ledger/frozen-v3.json`, `frozen-v3.json.sha256` | the constants, each with source, label and band; the freeze line | |
| `../../../../tools/ledger/freeze_ledger_v3.py` | writes them from committed sources; `--check` recomputes byte for byte | |
| `../../../../tools/ledger/measured_ledger_v3.py` | the blind days' committed passes | measured |
| `../../../../tools/ledger/programs_ledger_v3.py` | the plain programs from the counts v2 priced and the L1 model's lines | desk check of code |
| `../../../../tools/ledger/readings_ledger_v3.py` | writes the four reading files into the directory its `--out` names (required) | |
| `../../../../tools/ledger/selftest_ledger_v3.py` | writes the two self-test files into the directory its `--out` names (required) | |
| `../../../../tools/ledger/V2-TO-V3.md` | v2 and v3, term by term | |
| `../../../../tools/counter/l1_model.py`, `ledger_interp.py`, `test_l1_model.py` | the L1 model, the sort interpreter (the counter's per-sort counts at 512 keys, exactly), their test | desk check of code |
| `roundtrip-v3.txt`, `roundtrip-v3.json` | v3 with no rule on against v2's frozen forecasts and scorers | desk check of code |
| `readings-v3.txt`, `readings-v3.json` | the readings above | POST HOC |
| `selftest-v3.txt`, `selftest-v3.json` | the self-tests | desk check of code |
| `SHA256SUMS` | this directory's files | |

Reproduce from the repository's top, `/usr/bin/python3 -I -B`, standard library only (a minute or less each on aifoundry2), with
`OUT` a new scratch directory outside the repository: `tools/ledger/freeze_ledger_v3.py --check` (FREEZE CHECK PASS),
`tools/ledger/readings_ledger_v3.py --out OUT` (its four files the same bytes as the four here: `cmp OUT/readings-v3.json
docs/reports/data/2026-11-16-ledger-v3/readings-v3.json` and so on), `tools/ledger/selftest_ledger_v3.py --out OUT` (SELFTEST PASS,
27 of 27; its two files the same as here), `tools/counter/test_l1_model.py` (L1 MODEL TEST PASS, 24 of 24),
`tools/counter/ledger_interp.py --check` (INTERP CHECK PASS); `sha256sum -c SHA256SUMS` from this directory.

SPDX-License-Identifier: Apache-2.0

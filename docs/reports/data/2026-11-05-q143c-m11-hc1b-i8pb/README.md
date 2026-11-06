# M11's HC1-B and I8P-B, read blind on E172 (with E171) by the v2 reader frozen before the data: card 1's session heat scale reads BETTER (−0.016 °C [−0.028, −0.002] over 31 new kinds, h₁ 1.021); the paired int8 term reads NOT RESOLVED (+0.017 W [−0.022, +0.047] over 12, k 0.988), as forecast. Both are reported only: neither term enters M11

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**items 9 and 8** (heat) and **item 6** (a power model across kinds). Thu 5 Nov 2026 (week 45), PST, desk only on the Intel: no card, no
device command, no lab box, no post in the lab's channel, no Modal, no archive. It answers the pool-8 card day's critic, `next` **rank 3**:
"the HC1-B and I8P-B reading on E172's and E171's committed data dirs, with `read_hc1b_i8pb_v2.py` (never v1), into a new data dir that
records committed_files and the precedence block". It is step 4 of section 13 in M11's
[`REGISTRATION.md`](../../../../tools/claims-v3/m11/REGISTRATION.md) (`3c31a91d`, 07:41:57 PST), read by the reader that
[`README-h2-reader.md.dated-note-1.md`](../../../../tools/claims-v3/m11/README-h2-reader.md.dated-note-1.md) names, exactly as its "On the
card day" gives the command. The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of
numeric computations as accurately as possible.*

**Nothing frozen changes.** M11's registration and its amendments, the v1 and v2 readers and their self-tests, part 2's refit
(`2b33103c`: neither (c) HC1 nor (d) I8P enters), M10, M9, pool 8, the P8 scorer and its v2 and v3, and E171's and E172's data
directories stay as committed. This directory holds new files only. Its readings change no P8 rule, line, set or verdict (REGISTRATION.md
section 11).

## Results

| reading | set | label | verdict | d (with − without) | 95% interval | scale | rms without → with | bias without → with |
|---|---|---|---|---:|---|---:|---|---|
| **M11-HC1-B**, card 1's 4.5 s heat scale | E172's N1, 31 tiles, C-gated (none left out) | **blind** | **BETTER** | **−0.0158 °C** | [−0.0279, −0.0019] | h₁ = 1.02066 | 0.1696 → 0.1538 °C | +0.0593 → +0.0226 °C |
| **M11-I8P-B**, card 1's paired-anchor int8 term | E172's I1, 12 tiles, C-gated (none left out), paired with E171 | **blind** | **NOT RESOLVED** | **+0.0167 W** | [−0.0224, +0.0468] | k = 0.98752 | 0.1245 → 0.1412 W | +0.0047 → +0.0802 W |

([`m11-hc1b-i8pb.json`](m11-hc1b-i8pb.json) › `HC1-B` and `I8P-B`; [`m11-hc1b-i8pb.md`](m11-hc1b-i8pb.md).) Each d is the registered
paired bootstrap over the set's tiles (20,000 draws; seeds 80,519 and 80,540). BETTER means the interval's upper end is below 0.

**In plain words.** Card 1's 4.5 s die rise was predicted by M10's law, frozen before E172 ran. Scaling that law by one number per
session, read from the session's own nine random anchors, made the prediction of the 31 new kinds better. The gain is small but resolved:
the rms fell from 0.170 to 0.154 °C, and the bias from +0.059 to +0.023 °C. The paired int8 term, read from three int8 anchors measured
on both cards, scaled card 1's int8 power by 0.988. On the 12 int8 kinds it did not resolve, and its point estimate was worse. Neither
term enters M11. Part 2's refit decided that on the committed rows before this session, and by REGISTRATION.md section 10's "one way only"
a blind reading cannot bring a term in. So M11's card-1 predictions stay M10's: its 4.5 s law, and int8's B with the 0.9616 card term.

### Reported beside each reading (never a verdict)

**HC1-B** (`HC1-B` in the JSON):
- **At M10's primary D** (the footing P8-H1-H3 read, the scorer's `M10_heat_c`): d **−0.0242 °C [−0.0336, −0.0133]**, rms 0.1906 →
  0.1664 °C. The 0.1906 °C is P8-H1-H3's 0.214 / 0.250 / 0.101 °C pooled over the 31 tiles.
- **By format** (rms without → with h₁, °C): fp32 (11) 0.184 → 0.157; fp16 (8) 0.225 → 0.201; **int8 (12) 0.097 → 0.107**.
- **The anchors.** Nine, every one C all PASS, and none with a run over 5.0 s, so the C-clean arm equals h₁. Each ratio is dT_win over
  the law: `fp32.randn` 1.0669, `fp32.anchor8_randn_a_989b8a` 1.0938, `_b_833ac3` 1.0326; `fp16.randn` 1.0305,
  `fp16.anchor8_randn_a_8c7827` 1.0207, `_b_3a0fef` 1.0071; `int8.full` 0.9718, `int8.anchor8_full_a_4aac84` 0.8647, `_b_935710` 0.9884.
  h₁ is their median.
- **The check anchors' errors** (measured − predicted, °C, without → with h₁): `fp32.anchor8_check_randn_319f73` −0.037 → −0.101
  (larger); `fp16.anchor8_check_randn_84631a` +0.099 → +0.042 (smaller); `int8.anchor8_check_full_d8b6c8` +0.214 → +0.190 (smaller).
- **The control h₃ on E171** (aifoundry3, computed the same way and not applied): **0.98019**. Applied, it would read NOT RESOLVED
  (+0.0011 °C [−0.0132, +0.0143]). aifoundry3 keeps h = 1.
- **The not-wanted clauses** (REGISTRATION.md section 8): **not met**. HC1-B is not WORSE, and the bias keeps its sign and falls in size,
  so h₁ does not over-correct.

**I8P-B** (`I8P-B` in the JSON):
- **k** is the median of three anchors' [D₁₇₂ / D̂₁₇₂] / [D₁₇₁ / D̂₁₇₁]: `int8.anchor8_full_a_4aac84` 0.97431,
  `int8.anchor8_full_b_935710` 0.98752 and `int8.full` 0.98756. Each is C all PASS in both sessions, and none was left out.
- **The check anchor** `int8.anchor8_check_full_d8b6c8`: |e| 0.2727 → 0.1847 W. That is inside M10's int8 band about k × M10
  (half-width 0.3435 W), so it is "better" by the registered words.
- **I1's bias**: +0.0047 → +0.0802 W. It keeps its sign and grows, so it is not "over-corrects" in the registration's words, but k
  pulls I1 away from level.
- **The not-wanted clause** (I8P-B WORSE): **not met**.

### Precedence and committed files (the two blocks the critic asked this directory to record)

- **Precedence** (`HC1-B` › `precedence` and `I8P-B` › `precedence`): M11's registration `3c31a91d` (07:41:57 PST) is in HEAD's
  history. It precedes E172's first launch record, 11:40:34.369 PST (`t_start_ms` 1793907634369), and E171's, 11:38:31.127 PST
  (1793907511127). So both readings are labelled **blind**. The v2 reader's first commit, `ea12f108` (11:13:51 PST), precedes both
  launch records too (`reader_frozen_before_the_data`: true). The card day launched from a tree at `ea12f108`.
- **Committed files** (`committed_files`; `departure`: none). Each session's five inputs were tracked and unchanged at HEAD `04159d14`:
  - E172's `scored.json`, `e172.json`, `runs.csv`, `ccheck/ccheck-session.json.gz` and `aifoundry1-c1/`, latest commit `b3255af1`
    (13:44:22 PST);
  - E171's `scored.json`, `e171.json`, `runs.csv`, `ccheck/ccheck-all.json` and `aifoundry3/`, latest commit `91f8ae40` (13:10:18 PST).
- **The reader's other checks**, as registered. The pair passed `score_p8_600_v3.pair_check` (1)-(7), unchanged: 64 rows each, and 0 of
  the 64 shared nonzero D bit-identical. The C-session gate was re-run on each raw copy (`ccsessions_p8.check`, no `--since`): ok, 5 of 5
  listed sessions with the same record as the scored file, stop-path test OK. The runs tables passed checks (a)-(e) in reduce_e78's form:
  - E172: 333 rows, 249 kept in 17210-17212, and 17213 set aside (84 rows);
  - E171: 335 rows, all four passes kept.

  P8-KC as the scorer's own blocks read it: E172 1,900 of 1,900, E171 2,550 of 2,550. (Those count the pool-8 tiles' launch records in the
  kept passes. The C checks' 3,470 and 3,490 count every C record. E172's data README, dated note 2, has the accounting.)

## Registered against what happened

| | registered (REGISTRATION.md sections 8, 9, 11; the reader's note 1) | happened |
|---|---|---|
| reader | `read_hc1b_i8pb_v2.py`, never v1 | v2, sha256 `5605aa5b…`, its list `SHA256SUMS-h2-reader-v2` 129 of 129 OK; v1's list 16 of 16; M11's lists 58, 6 and 9 OK |
| its self-test first | `selftest_read_hc1b_i8pb_v2.py`, 24 parts | **24 of 24 PASS** (16:31:04-16:33:35 PST). It differs from the committed output in one part only: H1f now accepts 47 committed reductions, 15 of which set a pass aside. E171's `e171.json` and E172's `e172.json` (17213 set aside) were added to the tree after the self-test was committed ([`selftest-rerun-diff.txt`](selftest-rerun-diff.txt)) |
| inputs | E171's and E172's committed files, after their own scoring | both data dirs committed and unchanged at HEAD; no departure |
| statistic, sets, seeds | paired bootstrap, 20,000 draws, seeds 80,519 and 80,540; N1 31 (minimum 10), I1 12 (minimum 6), each C-gated as P8-KC | as registered; no tile left out of either set |
| label | blind only if `3c31a91d` precedes every first launch record read | blind, both |
| forecast | I8P-B: "NOT RESOLVED" (section 9). HC1-B: no point forecast. Section 8 put the half-width at about 0.082 °C. A1-4 said that if E172's h₁ read near 1, HC1-B would read NOT RESOLVED even with the term right | **I8P-B NOT RESOLVED, as forecast.** **HC1-B BETTER**, with h₁ 2.1% from 1 and a half-width of 0.013 °C, about a sixth of section 8's pooled estimate. To first order, both the effect and its interval scale with \|h₁ − 1\|, so a scale near 1 can still resolve. A1-4's "NOT RESOLVED" did not hold here |
| entry | neither term enters (part 2, `2b33103c`); section 10's "one way only" | unchanged: both readings are reported only |

## What it does to predicting power and heat

- **The terms tested:** (c) HC1, a 4.5 s heat scale for card 1, read from the session's own random anchors; (d) I8P, a paired-anchor int8
  power term for card 1. Each was tested blind on 31 and 12 new kinds that no model had seen.
- **Before.** M11 is M10 on card 1, with figures held out, not blind:
  - card 1's 4.5 s heat 0.2855 °C rms over 448 rows, and 0.1731 °C with each session's own scale;
  - card-1 int8 power 0.1849 W over 108 rows.

  E172's blind 4.5 s heat under M10's law at its primary D: 0.214 / 0.250 / 0.101 °C (P8-H1-H3), 0.191 °C pooled.
- **After** (blind, reported, not carried):
  - With h₁, E172's 31 new kinds read 0.170 → 0.154 °C at the measured S, and 0.191 → 0.166 °C at M10's primary D. That is a resolved
    0.016-0.024 °C gain from one number per session.
  - With k, E172's 12 int8 kinds read 0.125 → 0.141 W: not resolved, and the point estimate is worse.
- **What it changes:** nothing in M11. Neither term enters, and a blind reading cannot bring one in. Two things go to the next
  registration as evidence, not as results:
  1. A per-session heat scale helped blind on card 1, with h₁ 2.1% from 1. Part 2 named the next candidate: "a heat scale applied only
     when a session's scale departs from 1 by more than its own noise". This session gives one blind case for it.
  2. **Post hoc**, from the reported numbers above: the nine anchors split by family. The six float anchors read 1.007-1.094 against the
     law, and the three int8 anchors 0.865-0.988. One scale for both families helped the floats (fp32 0.184 → 0.157, fp16 0.225 → 0.201 °C)
     and hurt int8 (0.097 → 0.107 °C). That points to a scale per family as a candidate. It is not registered, and nothing here fits one.

  The paired int8 term again shows no use: its k (0.988) moved I1's bias from +0.005 to +0.080 W. That agrees with part 2's finding that
  the pairs' k vary more than their noise and over-correct on the committed rows.

## Files

| file | what |
|---|---|
| [`m11-hc1b-i8pb.json`](m11-hc1b-i8pb.json) | the reader's output, unchanged: both readings with every tile, the anchors, the checks, `precedence`, `committed_files` and `departure` |
| [`m11-hc1b-i8pb.md`](m11-hc1b-i8pb.md) | the reader's `--md` page |
| [`read-stdout.txt`](read-stdout.txt) | the reader's printed line |
| [`selftest-read-hc1b-i8pb-v2.rerun.txt`](selftest-read-hc1b-i8pb-v2.rerun.txt), [`.json`](selftest-read-hc1b-i8pb-v2.rerun.json) | the self-test, run first, at HEAD `04159d14` |
| [`selftest-rerun-diff.txt`](selftest-rerun-diff.txt) | its diff against the committed `tools/claims-v3/m11/selftest-read-hc1b-i8pb-v2.txt` and `.json` (H1f's counts only) |
| [`SHA256SUMS`](SHA256SUMS) | these files |

## How to reproduce

From the top of a clean clone of the lab's main at `04159d14` (or any later commit that leaves these paths unchanged):

```bash
python3 -B tools/claims-v3/m11/selftest_read_hc1b_i8pb_v2.py --out <dir>/selftest-read-hc1b-i8pb-v2.rerun.json \
  --txt <dir>/selftest-read-hc1b-i8pb-v2.rerun.txt
python3 -B tools/claims-v3/m11/read_hc1b_i8pb_v2.py read \
  --e172-dir docs/reports/data/2026-11-05-e172-blind8-card1 --e171-dir docs/reports/data/2026-11-05-e171-blind8-aifoundry3 \
  --json <dir>/m11-hc1b-i8pb.json --md <dir>/m11-hc1b-i8pb.md
```

Both ran with `/usr/bin/python3` (3.9.6). The self-test's H1f reads every committed reduction in the tree, so its count grows as sessions
are committed. The clone this lane ran in left the evening's E175-E177 paths out of its working tree: this lane does not read them, and
the self-test's committed output was made before any of them existed. The reading's output is the same in any tree where E171's and E172's
paths are unchanged.

## Compute

Desk only, on the Intel, through the round's local CPU slots at nice 10, one core each:
- a shared clone of the lab's main, 16:30:21-16:30:37 PST;
- the self-test, 16:31:04-16:33:35;
- the reading, 16:33:59-16:34:07.

Outside the slots there were only git and file reads and the public-text scan. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0

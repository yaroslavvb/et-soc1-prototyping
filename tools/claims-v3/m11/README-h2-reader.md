# Q142(h2), part 1: M11's HC1-B and I8P-B reader, frozen before E171's and E172's data

*Thu 5 Nov 2026 (week 45), PST, desk only: no card, no device command, no lab box, no post in the lab's channel, no Modal, no archive.
Written from about 09:50 PST and committed at the time git records. **No E171 or E172 data exists**: at 10:04 PST `git log --all`
showed no commit that opens `E171` or `E172` data and no path under `docs/reports/data/*e17[1-4]*` in any ref or in the tree. So this
reader and its self-test are committed **before the data they read**. It answers the critic of Q142(v2), (r2) and (h)
(`critic-q142v2rh`): its `next` **rank 2** ("the HC1-B and I8P-B reader, committed and self-tested on E163's and E164's committed
sessions") and its **fault 4** ("the code that reads them will not be frozen before the data"). It is
[`REGISTRATION.md`](REGISTRATION.md) section 13 step 4's reader, for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8 (heat) and 6 (the power
model). The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of numeric
computations as accurately as possible.*

**Nothing frozen changes.** REGISTRATION.md, `registration.json`, A1 (`REGISTRATION.md.dated-note-1.md`), `registration-a1.json`, the
power code and its outputs, and the lists `SHA256SUMS` (58), `SHA256SUMS-m11` (6) and `SHA256SUMS-a1` (9) stay as committed in
`3c31a91d` and `f49b7ddd`; so do the P8 scorer and its v2 and v3, E171's and E172's registrations and notes, pool 8 and M10. This adds
new files only.

## What it does to predicting power and heat

It removes the last implementation choice between M11's registration and its two blind readings on card 1. HC1-B tests a heat
scale for card 1 alone: M10's 4.5 s law held out reads card 1's heat to 0.2855 °C, and to 0.1731 °C with each session's own scale
(M10's committed held-out figures, not blind). I8P-B tests a paired-anchor int8 term for card 1, expected not to be wanted (section 9).
With this reader committed first, both readings on E172 (and E171) are blind by code as well as by registration: the statistic, the
sets, the seeds and every form the text leaves open are fixed in code before any launch. Nothing is measured here, and no prediction,
line or verdict changes.

## Files

| file | what |
|---|---|
| [`read_hc1b_i8pb.py`](read_hc1b_i8pb.py) | the reader: `read --e172-dir <E172's data dir> [--e171-dir <E171's data dir>] --json <out> [--md <out>]` (or each file by name). Python 3.9, standard library only |
| [`selftest_read_hc1b_i8pb.py`](selftest_read_hc1b_i8pb.py) → [`selftest-read-hc1b-i8pb.json`](selftest-read-hc1b-i8pb.json), [`.txt`](selftest-read-hc1b-i8pb.txt) | its self-test: 15 of 15 parts PASS |
| [`SHA256SUMS-h2-reader`](SHA256SUMS-h2-reader) | this part's files and the self-test's inputs that M11's lists do not pin |

## What it reads and computes (REGISTRATION.md sections 8, 9 and 11, unchanged)

It reads E171's and E172's scored sessions in the committed P8 scorer's output format (`tools/claims-v3/p8-600/score_p8_600.py`,
`a518aa11`), with the files the collectors put beside them: the registered primary reduction (`e17N.json`) and its runs table
(`runs.csv`), the check of C, and the session's directories.

- **HC1-B**, on E172's N1 (31 tiles), C-gated as P8-KC. Per tile: dT_win (the mean over the kept passes) against h₁(E172) × M10's 4.5 s
  law (`m10.json`'s coefficients, no refit) at the tile's measured S and run length, and against the law unscaled. h₁ is the median,
  over E172's random anchors (E78's `fp32.randn`, `fp16.randn` and `int8.full`, plus pool 8's six scale-role anchors; never a check
  or a zeros anchor), of dT_win / the law. The statistic is d = rms(dT − h₁ L) − rms(dT − L), a paired bootstrap over the tiles with
  20,000 draws and seed 80,000 + the character codes of `M11-HC1-B` (80,519). BETTER if the interval's upper end is below 0, WORSE if
  its lower end is above 0, else NOT RESOLVED.
  - Reported beside, never a verdict:
    - the same at M10's primary D (the scorer's `M10_heat_c`, as P8-H1-H3 read it);
    - the three check anchors' errors with and without h₁;
    - h₃(E171), computed the same way on aifoundry3 and not applied (a control);
    - each anchor's C status, and h₁ without any anchor that is not C all PASS;
    - the rms per format.
  - Read as section 8's not-wanted clauses: HC1-B reads WORSE; h₁ over-corrects on E172's N1 (the bias changes sign and grows in
    size).
- **I8P-B**, on E172 paired with E171. k is the median, over `int8.full`, `int8.anchor8_full_a_4aac84` and
  `int8.anchor8_full_b_935710` measured in both sessions' registered primary reductions and C all PASS in both, of
  [D₁₇₂(a) / D̂₁₇₂(a)] / [D₁₇₁(a) / D̂₁₇₁(a)]. D̂ is M10's int8 prediction (the B form, with card term 0.9616 on card 1) at each
  session's measured rate. The check anchor `int8.anchor8_check_full_d8b6c8` never enters k. On I1 (12 tiles), C-gated:
  d = rms(D − k × M10 primary) − rms(D − M10 primary), the same paired bootstrap, with seed 80,000 + the codes of `M11-I8P-B`
  (80,540).
  - Reported beside:
    - the check anchor's |e| with and without k, "better" if smaller with k and inside M10's int8 band about k × M10;
    - I1's bias with and without k ("over-corrects" if its sign changes and its size grows).
  - Read as section 9's not-wanted clause: I8P-B reads WORSE.
- **Blind or post hoc** (section 11). A reading counts as blind only if `3c31a91d` is in the tree's history and its commit time
  (07:41:57 PST) precedes the first launch record of every session it reads. The first launch record is the earliest `t_start_ms`
  of every `runs.jsonl` under the session's directories. Otherwise the reading is labelled post hoc. Beside it, the reader says
  whether its own first commit precedes the same launch records.
- **Refusals** (nothing written):
  - 9: a frozen input differs (M11's three lists, the predictor's pin of `pool8-registration.json`, the freeze's predictions, or the
    committed scorer, v2 or v3);
  - 4: a C log is missing (a scored file not scored through the C gate, or no check of C beside it);
  - 6: an identity check fails. The file is not E172 on aifoundry1c1, or not E171 on aifoundry3; the pair is swapped, relabelled,
    the same file, or the same measured D under two names (`score_p8_600_v3.pair_check`, unchanged); the reduction or the check of
    C is not the one the session was scored with; the runs table is not that reduction's;
  - 5: an anchor list holds a check or a zeros anchor;
  - 2: a usage error.

## Where the text leaves a form open: the one it implies, taken here

1. **The paired bootstrap** is the P8 scorer's (`score_p8_600.paired`, E163's `compare_rule` form), called unchanged. The set is in
   sorted name order; each draw takes as many tiles as the set holds, with replacement, from `random.Random(seed)`; the interval is
   the sorted draws' [int(0.025 × 20,000)] and [int(0.975 × 20,000) − 1]. The registration's seed formula is P8's, 80,000 plus the
   character codes of the rule's name, and section 9 says "as HC1-B's".
2. **A set's minimum** is the P8 paired rule's on the same set (`pool8-registration.json` › `scoring.minimum_tiles`): M1's 10 on N1
   and M1i's 6 on I1. With fewer, the reading is NOT SCORED.
3. **The measured S** is the mean over the kept passes of the reduction's per-pass S (the scorer's own `measured`, as for dT_win).
   **The run length** is `fit_m6.heat_rows`' rule, which built the rows M10's law was fitted on: the median, over the item's runs in
   the runs table, of (the next run's `prev_end_ms` − its `t0_ms`) / 1000, within a pass. A tile longer than 5.0 s (M10's heat rows
   leave such rows out) is named, never dropped: the registered set is N1.
4. **h₁'s anchors enter whatever their C status**, as the session's float scale s does (E171.md and E172.md dated notes 1, N2, which
   registered that for s). h₁ without any anchor that is not C all PASS is reported beside. **I8P's anchors are C-gated**, as section
   9 says: an anchor that is not C all PASS in either session leaves k, and is named.
5. **No anchor**: with no random anchor measured, h₁ = 1 (M10's rule) and HC1-B reads NOT SCORED. With no int8 anchor that is C-clean
   in both sessions, k cannot be read and I8P-B reads NOT SCORED. A session that kept fewer than 2 passes makes both NOT SCORED (the
   registrations' rule for every rule). Without E171, I8P-B reads NOT SCORED.
6. **"The same at M10's primary D"** keeps E172's h₁ (a session property, read once from the anchors at their measured S). It evaluates
   only the N1 tiles' law at the scorer's `M10_heat_c`, which is M10's 4.5 s rise at its primary D plus the zeros S, at 4.5 s.
7. **"Inside M10's int8 band"** for the check anchor uses M10's own 95% half-width (the scorer's `M10_primary_95`) about the
   k-scaled prediction.

## The self-test: 15 of 15 parts PASS

It ran at 10:05:13-10:07:02 PST (a first run at 09:59:56-10:01:41 gave the same printout; one variable was then renamed for the public-text scan): one local slot job, at nice 10, on one core. Its output is masked (the repo, the temporary
directory).

| part | what | result |
|---|---|---|
| H0 | M11's lists pass (58, 6, 9); the anchor list is `fit_m10.ANCHORS`; seeds 80,519 and 80,540; minimums 10 and 6 | PASS |
| H1a | E163's and E164's committed sessions: the reader's S, dT_win and run length against `fit_m6.heat_rows`' rows for both (reached through fit_m10's chain) | 152 rows, every difference 0.0 |
| H1b | h on E164 and E163, with `m10.json`'s coefficients and M10's anchor list, against `heldout-m10.json` › `heat_c1` › `session_heat_scales_all_rows` | 1.05995 against 1.06; 1.00474 against 1.0047 (within 5e-5) |
| H1c | the int8 pair E164 / E163: each pool-7 int8 anchor's D ratio against RK4's committed `anchor_ratio`; the three-anchor median against RK4's E78 arm | both differences 0.0; 0.938230 equal; k = 0.97630, equal to the rate-adjusted ratios over the card term to 1e-15 |
| H1d | both readings computed on the stand-ins (pool 7's priority-1 tiles for N1 and I1). **In-sample and post hoc**: both sessions are in M10's training rows | HC1-B on E164: h 1.060, d −0.060 °C [−0.081, −0.039], BETTER. I8P-B on E164 / E163: k 0.9763, d −0.0008 W [−0.043, +0.057], NOT RESOLVED; I1's bias −0.077 → +0.061 W (the sign changes, the size falls) |
| H2-D1 | synthetic E171 and E172 (each scored by the committed scorer, in-process, as the collectors call it), h₁ 0.90 and k 0.97 by design, launches after the registration | HC1-B BETTER, h₁ 0.900; I8P-B BETTER, k 0.970; both blind; h₃ 1.000; the interval re-derived from the registration's words is identical |
| H2-D2 | h₁ 0.90 on the anchors with tiles at 1.00; k 0.97 with I1 at 1.00; launches before the registration | both WORSE, both post hoc; HC1's not-wanted clause met |
| H2-D3 | h₁ and k exactly 1 (exact in floating point) | both NOT RESOLVED, d = 0 in every draw |
| H2-D4 | h₁ 1.10 with tiles at 1.02; k 1.05 with I1 at 1.01 | HC1-B WORSE and over-corrects on N1; I8P-B WORSE and I1's bias over-corrects |
| H2-D5 | E172's `int8.anchor8_full_a` and E171's `int8.full` judged C FAIL | k from the one anchor left (0.970), both named; h₁ keeps nine anchors (0.900), its C-clean arm eight (0.8991) |
| H2-D6 | 22 N1 and 7 I1 tiles of E172 judged C FAIL | HC1-B NOT SCORED (9 tiles, fewer than 10); I8P-B NOT SCORED (5, fewer than 6) |
| H2-D7 | E172 kept one pass | both NOT SCORED (the committed scorer's own mark) |
| H2-D8 | E172's heat anchors carry no dT_win; E171's three int8 anchors judged C FAIL | both NOT SCORED (no anchor) |
| H2-D9 | the collectors' data-dir layout (`--e172-dir`, `--e171-dir`) | reads as D1 by name |
| H3 | refusals, each from the command line, with nothing written | usage 2; E171 given as E172 6; the pair swapped 6; E171's file relabelled as E172's 6; E172 twice 6; no `c_sessions` 4; no check of C 4; another reduction 6; a runs table short by one run 6; another session's check of C 6; M11's `SHA256SUMS-a1` changed 9 (in-process) |

## On the card day (after his go): how to read

After step 22 v3 has collected and scored E171 and E172 (`s22_collect_k6_v3.sh e171`, then `e172`), and only then (section 11: the
readings change no P8 rule, line, set or verdict):

    python3 -B tools/claims-v3/m11/read_hc1b_i8pb.py read \
      --e172-dir docs/reports/data/<day>-e172-blind8-card1 --e171-dir docs/reports/data/<day>-e171-blind8-aifoundry3 \
      --json <a new data dir>/m11-hc1b-i8pb.json --md <a new data dir>/m11-hc1b-i8pb.md

It reads the collector's directories as they are in the build tree (`build/e17N-out/<day>-…`) or once committed under
`docs/reports/data/`. If E171 never runs, give `--e172-dir` alone: HC1-B is read, and I8P-B reads NOT SCORED. If E172 never runs, the
registration moves HC1-B to the next card-1 session that runs random anchors. That needs its own reader. Which terms M11 then carries,
and as what, is part 2's frozen entry (`README-h2-refit.md`, the next commit) read with these clauses, by section 10's "one way only".

## Compute

On the Intel, desk only. Two local slot jobs ran the self-test, at 09:59:56-10:01:41 and 10:05:13-10:07:02 PST (the committed output; the printouts are byte-identical), at nice 10 on one core. Outside the slot
there were sub-second reads of committed JSON, git, `shasum` and the public-text scan. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0

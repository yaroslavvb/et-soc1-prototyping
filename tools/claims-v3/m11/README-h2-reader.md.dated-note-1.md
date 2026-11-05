# Dated note 1 beside README-h2-reader.md: the reader's v2, before any E171 or E172 data

*Thu 5 Nov 2026 (week 45), PST, desk only: no card, no device command, no lab box, no post in the lab's channel, no Modal, no archive.
Written from about 10:47 PST and committed at the time git records. **No E171 or E172 data exists**: at 10:46 and 11:07 PST
`git log --all` showed no commit that opens E171-E174 data and no path under `docs/reports/data/*e17[1-4]*` in any ref or in the tree,
so the v2 below is committed before the data it reads. This note answers the verifier of Q142(h2) (`verify-desk-q142h2-card1-readers`,
about 10:20-10:45 PST), whose verdict was **holds with fixes**: part 2, the refit (`2b33103c`), holds in full; part 1, the reader
(`21666b23`), holds in its statistics, sets and seeds, with one major fault and three smaller findings. It is for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8 (heat) and 6 (the power
model), as README-h2-reader.md is.*

**What stays as committed.** README-h2-reader.md, `read_hc1b_i8pb.py`, its self-test and output, and `SHA256SUMS-h2-reader` (16 of 16
still pass); REGISTRATION.md, A1 and A2 (no registration matter is changed here: every change is in the reader's code or in the forms
its README took where the registration's text leaves one open); part 2's refit, `refit-m11-cd.json` and its entry (neither (c) HC1 nor
(d) I8P enters); M10, M9, the P8 scorer and its v2 and v3, E171's and E172's registrations and notes, and pool 8. This note adds new files
only.

## What the card day runs

**HC1-B and I8P-B are read with `read_hc1b_i8pb_v2.py`, never with v1.** v1 refuses (exit 6, nothing written) any E171 or E172 session
whose registered primary reduction set a pass aside, flagged one for its configuration reads, or failed a run, and such sessions are
common. v2 reads them, and on every session v1 reads it gives the same readings, number for number (self-test V1).

## The verifier's findings, and what this note does

| # | the verifier's finding | here |
|---|---|---|
| 1 | **Major.** v1's runs-table check requires `runs.csv` to hold exactly the reduction's kept runs, but `reduce_e78.py` (which `reduce_e171.py` and `reduce_e172.py` run unchanged) writes every run of every pass it reduces and counts `kept` without failed runs and set-aside passes; the committed scorer scores such a session normally | **change 1**: the table checked in reduce_e78's own form |
| 2 | Minor. Refusal 4 is narrower than 21666b23's message says: v1 never re-runs the C-log gate, so a C log deleted after scoring reads normally, and a scored file missing because the scorer refused for a C log reads 2 | **change 2**: the committed scorer's C gate re-run |
| 3 | Nit. An anchor whose run is longer than 5.0 s enters h₁ silently, where M10's heat_c1 reads h only from heat rows | **change 3**: named and left out, reported beside |
| 4 | Nit. README-h2-reader.md lets the reader read the collector's output in the build tree "or once committed"; REGISTRATION.md sections 8 and 11 compute the readings from the committed files | **change 4** and *On the card day* below |
| 5 | Carried, not this lane's: `docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/sha256.txt` names a README that has changed since 8ab2ed9d | nothing owed here |

## The four changes (each marked "v2 (note 1, change N)" in `read_hc1b_i8pb_v2.py`)

1. **The runs table in reduce_e78's form.** v2 refuses (6) unless all of:
   - (a) `runs.csv`'s rows number the reduction's `runs`;
   - (b) every kept pass (the reduction's `passes`) has rows in it;
   - (c) the kept passes' rows without a fail number exactly the reduction's `kept`;
   - (d) every other pass in it is named in `passes_set_aside` or `passes_config_flags`, or every one of its runs failed (the
     complement of reduce_e78's kept set);
   - (e) the runs it marks failed are, as (pass, item, position), the reduction's `failed` list.

   The run length stays `fit_m6.heat_rows`' rule over the whole table, every pass and run in it. That is the rule M10's heat rows were
   built with, and v1 applied it to the same table. Of the 45 committed reductions in this form, 14 set a pass aside: E82, E86, E88,
   E91, E92, E95, E104, E109, E115, E116, E137, E140, E141 and E157 (the verifier's evidence counted 15). v2 accepts all 45. On the 30
   sessions M10's heat rows read, v1 refuses exactly the 12 that set a pass aside, and v2's table equals `fit_m6.heat_rows`' rows on
   all 902 rows that can be compared (the other 30 of M10's 932 come from sessions or tiles with fewer than 2 kept passes, which
   `measured` does not read). The largest difference is 1.8e-15, and it is 0.0 on E157, E141 and E82.
2. **The C-session check, re-run.** After the identity checks and before any table is read, v2 calls `ccsessions_p8.check(run, raw,
   ccheck)`, the committed scorer's own C gate, unchanged and without `--since`, as the collectors call the scorer. It runs on the raw
   copy and the check of C given. If it is not ok, v2 refuses with 4 and writes nothing.
   - A C log deleted after scoring is refused, a pass's or the smoke's (v1 read both).
   - A scored file that is missing while that check is not ok now reads 4, not 2 (the scorer refuses with 4 and writes nothing when a
     C log is missing). A scored file missing with every C log in place still reads 2.
   - Beside it, reported and never a refusal: whether each session the check lists has the same record in the scored file's
     `c_sessions` block. A data dir renames a pass that is not ok to `notok-<pass>`, so it can list fewer sessions than the scorer did.
   - The check's own code is checked first (refusal 9): `ccsessions_p8.py` against `p8-600/SHA256SUMS`, `ccdone_q142s.py` against
     `k6/SHA256SUMS-drivers-v3`, and `ccheck.py` against the sha256 E163's collection recorded (`2f806fe6`).
   - On E163's committed data dir (the collectors' layout, gzipped C logs) the check reads ok, 7 of 7 sessions.
3. **Anchors with long runs.** An anchor whose run length exceeds 5.0 s (`fit_m6.HEAT_TRUN_MAX`) is named and left out of h: h₁ on
   E172, the control h₃ on E171, and the C-clean arm. This follows M10's `heat_c1`, which reads a session's scale from heat rows only,
   and heat rows leave such runs out. h with those anchors included is reported beside, never applied. The kinds harness runs about
   4.5 s at 600 MHz, so this is not expected to bite. N1 tiles are unchanged: a tile longer than 5.0 s is named, never dropped (the
   registered set is N1). README-h2-reader.md's form 3 is amended to read so.
4. **Committed files.** The reading records, per session, whether every file it read is tracked and unchanged at HEAD, and the latest
   commit among them. If any is not, `departure` names the files and the departure from REGISTRATION.md sections 8 and 11, and so do
   both readings' blocks, the `--md` page and the command's last line. The label (blind or post hoc) still comes from precedence alone.

Nothing else changes: the statistics, the sets, the seeds (80,519 and 80,540), the 20,000 draws, the minimums (10 on N1, 6 on I1), the
C-gating, the precedence rule, the identity checks and the other refusals are v1's, in v1's order.

## README-h2-reader.md, as amended by this note

- **Refusals:**
  - 4 also covers the C-session check re-run here, and a missing scored file while that check is not ok;
  - 6 covers the runs table outside reduce_e78's form, checks (a)-(e);
  - 9 also covers the C-session check's code.
- **Form 3:** the run length is fit_m6's rule over the whole runs table. An anchor over 5.0 s leaves h, and is named; h with it is
  reported beside. A tile over 5.0 s stays in N1, and is named.
- **On the card day** (this replaces that section's "as they are in the build tree ... or once committed"). After step 22 v3 has
  collected and scored E171 and E172, and after their data directories are committed, read the committed directories:

      python3 -B tools/claims-v3/m11/read_hc1b_i8pb_v2.py read \
        --e172-dir docs/reports/data/<day>-e172-blind8-card1 --e171-dir docs/reports/data/<day>-e171-blind8-aifoundry3 \
        --json <a new data dir>/m11-hc1b-i8pb.json --md <a new data dir>/m11-hc1b-i8pb.md

  The output's `committed_files` gives each session's latest commit; record it with the readings. A reading taken before the commit
  (in `build/e17N-out/`, say) records its departure. The records then say so, and should take the reading again once the data is
  committed. The rest of that section stands: E171 never run, then I8P-B is NOT SCORED; E172 never run, then a new reader is needed.

## The self-test: 24 of 24 parts PASS

`selftest_read_hc1b_i8pb_v2.py` → `selftest-read-hc1b-i8pb-v2.json` and `.txt`. It runs v1's parts again against v2, and adds parts for
each change:

| part | what | result |
|---|---|---|
| H0 | M11's lists (58, 6, 9); v1's list (16); the C-session check's three files; the anchors, seeds, minimums and 5.0 s | PASS |
| H1a-d | v1's stand-in parts on E163 and E164 | the same results: 152 rows at 0 difference; h 1.05995 and 1.00474; k 0.97630; HC1-B BETTER and I8P-B NOT RESOLVED, in-sample and post hoc |
| H1e | change 1 on the 30 sessions M10's heat rows read | v2 accepts all 30, equal to `heat_rows` on 902 rows (largest difference 1.8e-15); v1 refuses exactly the 12 that set a pass aside |
| H1f | change 1 on every committed reduction in reduce_e78's form | 45 of 45 accepted, 14 setting a pass aside |
| H1g | change 4 on E163's committed files, and on a copy outside the repository | all committed, at 4293d151; the copy is not |
| H1h | change 2 on E163's committed data dir | ok, 7 of 7 sessions, stop-path test clean |
| H2-D1-D9 | v1's synthetic cases, through the committed scorer | each as in v1's self-test |
| H2-V1 | v1 and v2 on D1's pair | every number of both readings equal |
| H2-D10 | E172 with five passes: the fourth set aside, the fifth flagged for its configuration reads, one run in a kept pass failed | the committed scorer exits 0; v2 reads exactly D1's readings; v1 refuses it with 6 and writes nothing |
| H2-D11 | C logs: a pass's and the smoke's removed after scoring; one missing before scoring; the scored file missing with every C log in place | v2: 4, 4, 4 (the scorer itself exits 4 and writes nothing) and 2. v1: 0, 0, 2 |
| H2-D12 | `fp32.randn` at 5.5 s with dT at half the law, and an N1 tile at 5.5 s | the anchor is named and left out: h₁ 0.8991, the median of the other eight. With it, 0.8982, reported beside. The tile is named and kept (n 31) |
| H2-D13 | files outside the repository | the departure is recorded |
| H3 | refusals, from the command line, nothing written | v1's ten cases. Then a runs table with another pass's rows (d), a kept run marked failed (c), a kept pass relabelled (b): each 6. E157's committed table cut to its kept runs (v1's form) is refused at (a). M11's list changed, and the C-session check's list changed: each 9 |

## What it does to predicting power and heat

Nothing is measured here, and no prediction, line or verdict changes. It makes card 1's two blind readings, HC1-B (heat) and I8P-B
(int8 power), computable by code frozen before the data on any normally reduced E171 and E172 session. That includes a session that
sets a pass aside, as 14 of the 45 committed reductions did. Without it, such a session would be read by code written after the data.
Part 2's entry stands, so neither term is in M11: card 1's 4.5 s heat stays M10's law (0.2855 °C held out over 448 rows), and card-1
int8 stays M10's B with its 0.9616 card term (0.1849 W over 108 rows). These readings are reported, and by section 10's "one way only"
they cannot bring either term in.

## Files

| file | what |
|---|---|
| [`read_hc1b_i8pb_v2.py`](read_hc1b_i8pb_v2.py) | the reader, v2: `read --e172-dir <dir> [--e171-dir <dir>] --json <out> [--md <out>]`; Python 3.9, standard library only |
| [`selftest_read_hc1b_i8pb_v2.py`](selftest_read_hc1b_i8pb_v2.py) → [`selftest-read-hc1b-i8pb-v2.json`](selftest-read-hc1b-i8pb-v2.json), [`.txt`](selftest-read-hc1b-i8pb-v2.txt) | its self-test, 24 of 24 |
| [`SHA256SUMS-h2-reader-v2`](SHA256SUMS-h2-reader-v2) | these files, v1's reader and list, and every input of the self-test that M11's lists and v1's list do not pin |

## Compute

Desk only, local slot jobs at nice 10 on one core, one at a time:
- three read-only sweeps of the committed reductions and E163's C logs, at 10:52:37-10:52:39, 10:53:02-10:53:03 and 10:59:57-10:59:58
  PST;
- the self-test, at 11:04:20-11:06:43 PST, then again for the committed output at 11:09:31-11:11:51 PST, byte-identical to the first
  run.

Outside the slot there were sub-second reads of committed files, git, `shasum` and the public-text scan. No lab box, no remote host, no
card.

SPDX-License-Identifier: Apache-2.0

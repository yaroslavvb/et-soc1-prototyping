# Dated note 1 beside README.md, Thu 5 Nov 2026 (week 45), about 15:10 PST: the verifier's five corrections (every arm's verdicts, so M1, M1f, A1 and KA move with the footing too; the first blind score's wording; what the public-text scan covered; the session log's first two lines; the first launch's time and what the reproduction route gives)

*This note sits beside [`README.md`](README.md), not inside it: the README stays as committed in `91f8ae40` (13:10:18 PST). It answers the
verifier of E171's card lane (`verify-card-a3-e171`, Thu 5 Nov 2026, about 14:20-14:55 PST), whose verdict was "holds with fixes": the data
and every registered verdict hold, with one major fault and four minor ones, all in the words. Desk only. **No number, line, rule, verdict,
prediction, data file or frozen file changes, and nothing is re-scored.** The verifier re-ran the registered collector from this directory
and recomputed every registered verdict independently, with no fault. The figures below come from
[`posthoc_note1_e171.py`](posthoc_note1_e171.py), which reads only this directory's committed files and imports no scorer, with its output in
[`posthoc-note1-e171.txt`](posthoc-note1-e171.txt). The note answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, with items 8 and 9.*

## 1. Every arm's verdicts: M1, M1f, A1 and KA move with the footing too (fault 1, the major one)

The README's paragraph on the arms (lines 105-109) gives part of what each reported arm reads and ends "So P2's and B1's verdicts, and LG's,
move with the footing". That is incomplete. In full, from [`scored.json`](scored.json) › `arms`, each arm scored by the same code with its own
scale and "reported beside, never the verdict" ([E171.md](../../../../tools/claims-v3/e171/E171.md) line 75); the leakage and the runs kept are
the first line of each footing's committed `reduce*.log`:

| footing | leakage (W/°C) | passes kept | s | P1 fp32 | P2 fp16 | B1 floats | B2 int8 | M1 (M10 − M9) | M1f (floats) | A1 (scale − a priori) | KA | LG | P8-G fails on |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **the registered primary**: Q139(u)'s footing, dips removed | 0.2056 (frozen) | 4 | 1.0061 | 0.176 PASS | 0.2381 **FAIL** | +0.092 **FAIL LOW** | +0.035 PASS | −0.065 [−0.122, −0.012] **BETTER** | −0.091 [−0.164, −0.020] **BETTER** | −0.062 [−0.093, −0.033] **BETTER** | **PASS** | NOT SEPARATED | P2, B1 |
| leakage fitted on the session, dips removed | 0.2850 (fitted) | 4 | 0.9961 | 0.172 PASS | 0.2227 PASS | +0.086 FAIL LOW | −0.016 PASS | −0.035 [−0.081, +0.008] NOT RESOLVED | −0.051 [−0.111, +0.010] NOT RESOLVED | +0.013 [−0.010, +0.035] NOT RESOLVED | FAIL | GAIN | B1 |
| the session-own footing: leakage fitted on the session, dips kept | 0.2898 (fitted) | 2 (17110, 17113) | 0.9957 | 0.459 FAIL | 0.2137 PASS | +0.015 PASS | −0.052 PASS | −0.013 [−0.073, +0.018] NOT RESOLVED | −0.020 [−0.115, +0.023] NOT RESOLVED | −0.003 [−0.020, +0.037] NOT RESOLVED | PASS | NOT SEPARATED | P1 |
| the frozen slope, dips kept | 0.2056 (frozen) | 2 (17110, 17113) | 1.0058 | 0.453 FAIL | 0.2259 PASS | +0.026 PASS | −0.001 PASS | −0.018 [−0.104, +0.038] NOT RESOLVED | −0.026 [−0.153, +0.049] NOT RESOLVED | −0.025 [−0.090, +0.010] NOT RESOLVED | FAIL | NOT SEPARATED | P1 |
| leakage 0.1994, dips removed | 0.1994 | 4 | 1.0069 | 0.176 PASS | 0.2393 FAIL | +0.093 FAIL LOW | +0.039 PASS | −0.071 [−0.128, −0.016] BETTER | −0.098 [−0.172, −0.026] BETTER | −0.072 [−0.106, −0.040] BETTER | PASS | NOT SEPARATED | P2, B1 |
| leakage 0.3803, dips removed | 0.3803 | 3 (17110-17112) | 0.9831 | 0.163 PASS | 0.2111 PASS | +0.077 FAIL LOW | −0.108 FAIL HIGH | −0.122 [−0.187, −0.055] BETTER | −0.175 [−0.259, −0.083] BETTER | −0.113 [−0.189, −0.030] BETTER | PASS | BOTH | B1, B2 |
| leakage 0, dips removed | 0 | 4 | 1.0317 | 0.198 PASS | 0.2815 FAIL | +0.117 FAIL LOW | +0.168 FAIL LOW | −0.332 [−0.431, −0.227] BETTER | −0.459 [−0.564, −0.350] BETTER | −0.468 [−0.580, −0.362] BETTER | PASS | GAIN | P2, B1, B2 |
| E78's pass gates opened | 0.2056 (frozen) | 4 | 1.0061 | as the primary | as the primary | as the primary | as the primary | as the primary | as the primary | as the primary | PASS | NOT SEPARATED | P2, B1 |

W throughout. P1 and P2 are rms against the registered lines [0.098, 0.300] and [0.063, 0.2374]; B1 and B2 the mean of measured − M10 against
[−0.097, +0.064] and [−0.105, +0.089]; M1, M1f and A1 the paired rms difference with its 95% interval. The arms record KA and LG as verdicts
only. The two dips-kept footings score 30 tiles, not 31: `int8.l8_cycle3_d3p3c15_c6d5`, skipped in pass 17110 by E78's rule, has one kept
pass there, and the scorer takes a tile from two kept passes (`score_p8_600.py` line 334), so P3, B2, M1i and H3 have n 11 and C1, M1 and H4
n 30.

**What moves, rule by rule** (the arms, of 7, whose verdict differs from the primary's):
- **M1, M1f and A1: 3 of 7**, NOT RESOLVED with the leakage fitted on the session (dips removed or kept) and with the frozen slope and the
  dips kept. M1's difference is negative in all eight footings (−0.013 to −0.332 W): M10 reads better than M9 in sign everywhere, resolved in
  five of the eight. A1's is +0.013 W with the leakage fitted on the session and the dips removed: there the session's anchors give
  s = 0.996, so the session scale and the a-priori arm (s = 1) nearly coincide. At the registered slope they give s = 1.006.
- **KA: 2 of 7**, FAIL with the leakage fitted on the session and the dips removed, and with the frozen slope and the dips kept.
- **P2: 4 of 7** (PASS); **P1: 2 of 7** (FAIL, the two dips-kept footings, which keep two passes); **B1: 2 of 7** (PASS, the same two; it
  reads FAIL LOW in the other six footings); **B2: 2 of 7** (FAIL HIGH at 0.3803 W/°C, FAIL LOW at 0); **LG: 3 of 7** (GAIN, BOTH, GAIN).
- **The same in all eight:** P3 (PASS, 0.125-0.245 W), C1 (PASS), M1i (NOT RESOLVED), H1-H4 (PASS) and HM (NOT SCORED). **P8-G reads FAIL in
  every footing**, on the rules in the table's last column. KC reads the launches, not the footing, so the arms do not score it.

**The registered verdicts stand.** The primary is the footing frozen before the data (Q139(u)'s, registered before any row was re-read);
the arms are reported beside it and never decide a verdict, as E171.md registered. But these words carry no caveat:
- the README's title;
- its plain-words paragraph: "clearly better than M9's 0.245 W on the same tiles (resolved by the paired bootstrap)" (lines 32-33) and "that
  scale improves the new float kinds over the a-priori arm and carries to the two check anchors it never read" (lines 34-35);
- "So P2's and B1's verdicts, and LG's, move with the footing" (line 109);
- "the float scale term generalises to kinds and draws it never read" (line 121);
- the data commit's subject, "its float scale term carries blind (A1 BETTER, KA PASS)".

**The records quote:** "M1 BETTER, A1 BETTER and KA PASS on the registered footing (Q139(u)'s, frozen beforehand); with the leakage fitted
on the session and the dips removed (all four passes), M1, M1f and A1 are NOT RESOLVED and KA FAILS. M10 reads better than M9 in sign in
every reported footing, resolved in five of eight; P8-G FAILS in every footing."

## 2. The first blind score of M10 at 600 MHz in its own form (fault 2)

"For the blog material and the hub" (line 128) says "this is the first blind score of M10". As worded, it is not: **E173 scored M10 blind
first**, carried by rule E to aifoundry2's governed bursts at s = 1 (its session s1 11:40:24-12:16:17 PST,
[E173's README](../2026-11-05-e173-blind8-aifoundry2/README.md) line 97; its data `ed8b5761`, 12:47:48 PST). E171 is **the first blind score
of M10 at 600 MHz in its own form**, with term a read from the session's own anchors: its session 11:38:12-12:35:33 PST, scored in the
collection of 12:36:56-12:56:59, committed in `91f8ae40` at 13:10:18. The other 600 MHz run, E172 on aifoundry1 card 1, ended its session
earlier (11:40:14-12:33:55 PST), but was collected after E174 (13:19:36-13:35:38) and committed at 13:44:22 (`b3255af1`;
[E172's README](../2026-11-05-e172-blind8-card1/README.md) lines 17 and 140-142). **The records quote:** "the first blind score of M10 at
600 MHz in its own form (E173, committed first, scored M10 carried to aifoundry2 by rule E at s = 1)".

## 3. What the public-text scan covered (fault 3)

The lane's public-text scan of this directory used the lab's fixed list of patterns (`tools/timeline/sanitize_extracts.py`'s) and the
round's extras (private network addresses, Mac home and scratch paths, mail domains). No table of the other lab users' login names was loaded at the
desk, so no scan matched those names one by one. What stands for them:
- the logs' scrub check (`--check`, 0 left), which the verifier re-ran on `logs/` and on the whole directory;
- the verifier's sweep of all 443 committed files, with the 16 `.gz` files read decompressed. It found no home path but the owner's own
  box path, and no other account's holder, `who` or terminal line. The binary files it skipped are all tile files (`tiles/*.bin`, the
  operands' bytes): no other committed file is binary.

**The records state the coverage:** "the public-text scan: the fixed list and the scrub check, with no name table; the verifier's sweep
found no other login".

## 4. The first two lines of `logs/session.log` are the dry pass's start-gate test (fault 4)

[`logs/session.log`](logs/session.log) opens with two lines at 11:37:56 PST:

```
2026-11-05 11:37:56 PST session start (budget anchor T0 11:37:56 PST; plan FULL)
2026-11-05 11:37:56 PST no new card session after 2026-11-05 10:37:00 PST: no device opened
```

**They are not the session.** They come from the V3_DRY pass's start-gate test (the README's box steps, 11:37:39-11:37:56). The k6 runbook's
step 10 ([`s10_a3_dry_k6.sh`](../../../../tools/claims-v3/q141k-runbook/k6/s10_a3_dry_k6.sh) lines 23-25) runs
[`session_e171.sh`](../../../../tools/claims-v3/e171/session_e171.sh) with `V3_DRY=1` and `E171_LATEST_START` set an hour back, and wants
exit 8. `session_e171.sh` writes to the same `build/e171/session.log` as the session (its line 28), says "session start" first (line 36),
and refuses at the past start gate before any device opens (line 45, exit 8). The step's wait read `E171 start gate rc=8 (want 8)` at
11:38:00 (in the card day's runbook capture, outside the repo). The session itself starts at line 3, 11:38:12 PST, the T0 every figure
uses.

## 5. Two exact facts (fault 5)

- **The first kernel launch in the smoke was at 11:38:31.127 PST**, not "about 11:38:27" (the table "Registered against what happened", row
  "order"). It is the first launch record of
  [`aifoundry3/e171-smoke/p17101/runs.jsonl`](aifoundry3/e171-smoke/p17101/runs.jsonl): `anchor_pi`'s calibration launch (launch −1, 20,000
  iterations). 11:38:27 is the smoke block's start: `logs/session.log` line 25 ("e171-smoke p17101 begins"), with its `block.json` `t0_ms`
  at 11:38:26.471.
- **What "How to reproduce" gives.** Its code block runs the collector and the C-session gate. `scale-c.json` and `scale-c.md` come from a
  third command, which step 22 v3 runs and the paragraph under the block names
  ([`s22_collect_k6_v3.sh`](../../../../tools/claims-v3/q141k-runbook/k6/s22_collect_k6_v3.sh) lines 56-61 and 101):

  ```bash
  O=build/e171-out/2026-11-05-e171-blind8-aifoundry3
  python3 -B tools/claims-v3/p8-600/score_p8_600_v2.py scale-c --run E171 --scored $O/scored.json --reduction $O/e171.json \
    --raw build/e171-raw --ccheck $O/ccheck/ccheck-all.json --json $O/scale-c.json --md $O/scale-c.md --work $O/scale-c
  ```

  With it, the route gives 434 of this directory's 442 collected files byte for byte (the verifier ran it in a clean clone at `91f8ae40`,
  14:21:18-14:22:19 PST). They include every verdict, figure, reduction and arm, and `ccheck-all.json` and `ccheck.txt`. Eight files differ,
  none in a figure:
  - `scored.json`, in five strings: `c_sessions.sessions[0-4].c_log` end `c-log.jsonl.gz`. This directory's passes hold their C logs
    gzipped; the box copy the card day's collection read held them plain;
  - so `scale-c.json`'s `scored_sha256` (`c4ff55a7…` against `f3deaf08…`), and `scale-c.md` line 3, which quotes its first 12 digits;
  - the five `ccheck/c-log-p171NN.jsonl.gz`, in the gzip header's time stamp only (the time each was written; 12:37:02 PST here). Their
    contents are equal.

  `posthoc_note1_e171.py --rerun <the route's output directory>` prints this comparison (its part 5).

SPDX-License-Identifier: Apache-2.0

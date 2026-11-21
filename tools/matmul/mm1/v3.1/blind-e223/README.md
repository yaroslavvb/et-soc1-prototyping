# blind-e223: the lab's BLIND test of its frozen matmul models on E223, declared and frozen before any E223 datum

E223 is the model session's seventh matmul sweep (1121-mmsweep7; proposal #16 on the coordination Discussion): E136's rgm136 unchanged over 299 gemmL arms of the lab's kinds and an anchor in nine sessions (aifoundry1 card 1 S1-S3 at 600 MHz, aifoundry1 card 0 S1-S3 at low power, aifoundry2 card 0 S1-S3 under its governor), no designed tiles: the core-group placements first (the proposal's held-out placements in 15 sets), then the held-walk edge, the L3 region, the wide-B wait and the masked energy cases. This folder holds the lab's declaration of how it will score its frozen models on E223, MM1's domain stated first, and the forecasts frozen at nominal conditions, all made at the desk on aifoundry2 before any E223 datum. Nothing here is a measurement.

**Label:** BLIND (sessions whose first datum follows the freeze post); UNREAD (any whose first datum precedes it).

**MM1's domain first** (DOMAIN-e223.md, domain-e223.csv): EVERY E223 case is IN MM1's domain: all 299 arms and the anchor are rgm136's cooperative gemmL<MB>x<NB>x<KB> loop (no gemmLnc, no block, stream or TenB arm; arms.json and every schedule checked) at the lab's kinds (zeros, ones, random; fp32, fp16, int8) on the three cards MM1-v3.2 has per-card constants for; NO case is OUT OF DOMAIN, so none is left unforecast.

## The order of hashes and times (Pacific, Sat 21 Nov 2026; logs/progress.txt)

- Sat 21 Nov 2026 02:04:15 PST step 00a setup lab (rc 0): git archive of GitHub main c661275c (= LAB HEAD) under the lab-git lock into work/lab (tools/matmul/mm1 whole, E215's rules, kinds, e136, e214, e213 points, e221, e222, e224): MM1-v2 eafb6558 114/114, v3 c24efc14 170/170, v3.1 f6840d2d 64/64, v3.2 d52c9cce 58/58 (4e386f75), Q234 posimb 34/34 + note1 2/2, gemmlnc-af4 43/43 + 1/1, l3s 32/32 + 2/2; E222 registration 30/30 and kit 54/54, E224 registration 31/31 and kit 120/120 (from the repo root); Q238 mask-posimb (posted FROZEN.txt 0cd8e9da = on disk) copied into work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask: 46/46 files equal FROZEN.txt's lines, SHA256SUMS 47/47; mask-mesh: posted #1.30.1.2.1.1.1.1.1.1 02:03:18 FROZEN.txt 3d4942fa..., but the file on disk (rewritten 02:03:37) reads 487188c7...: NOT the posted sha256, so not included unless a posted line matches at the freeze; mask-ceiling: no FROZEN.txt
- Sat 21 Nov 2026 02:04:34 PST step 00b kit copy (rc 0): the orchestrator's copy (COPIED.txt 01:57:27 PST) into work/e223-src: SRC-SHA256SUMS.txt 627b622e 53/53 OK; the kit's own src/SRC-SHA256SUMS 52/52 OK from the kit root; no session data in the copy (session_mms.sh is the kit's session script); all 9 tile files are the lab's kinds byte for byte (E223 designs no tile)
- Sat 21 Nov 2026 02:14:03 PST probe p02 (a code test of s02b_nominal.py, before the declaration): second try 02:12:31-02:14:03 rc 0: check A 2,431 of E224's frozen forecast rows (the lab's kinds, both arms, every clock) re-made by E224's own Models.forecast at this work copy, worst relative difference 0.0; check B 294 of posimb-mask's frozen E222/E224 rows re-made, worst 0.0; 695 cases x 13 models finite, energy FORECAST 695/695 each; MM1-v3.3 equals MM1-v3.2 on every case (AF4 0 off gemmLnc); only summary lines printed (checks, counts, scopes, the factor ranges); its output (in the scratchpad) deleted unread
- Sat 21 Nov 2026 02:19:31 PST step 01 DECLARED (rc 0): DECLARED-blind-e223.md f2795ec352ca6244e8af2167b5b9742e1c2dad7fa6e844eb6035957b8398b3c7, DECLARED-blind-e223.json c74dc54746780a8d9a952e871a81510913b5e33c6934bdf6a23ee5124ee76e02 (written 02:19:24 PST, the third draft; the drafts of 02:18:00 and 02:19:06 were never hashed and were deleted); q238-frozen-posts.txt read at 02:19:24: mask-posimb INCLUDED (0cd8e9da), mask-mesh NOT INCLUDED (posted 3d4942fa, on disk 487188c7), mask-ceiling no FROZEN.txt; every step-0/1 file and script in logs/step1-sha256.txt (sha256 ab0ae70cbd41d40ece9c32b66063e390f3266c5c7b0412ac711fbb5496144102); no E223 datum read
- Sat 21 Nov 2026 02:22:09 PST step 02 FORECAST (rc 0): nominal forecasts made 02:19:40-02:21:38 PST in one slot job (fc-nominal.json ce01e77fec05f13c6bf95464e289bf0bd1ac785e97aa935b8201850b44dd4b50; 695 cases x 13 models, energy FORECAST 695/695 each; checks before any output: E224's 2,431 frozen rows and posimb-mask's 294 frozen rows re-made exactly (worst 0.0); MM1-v3.3 = MM1-v3.2 on every case; scopes posimb 513, L3S 182, AF4 0, posimb-mask 513); forecasts-nominal-e223.csv dc47385df5af5db0bf6ba4dcdc49f453506f8df88eb07ee488e3527d3bd32082 (9,035 rows), forecasts-nominal-e223.json aeb174a7ea93a73b0baeac3d404fe57013694118dfb39e2963fe1fc388aa424f (written 02:21:39); step-2 files in logs/step2-sha256.txt (sha256 b11a802475ae85c1b576af1ab8e48936a6bc42a87bf51a1a6822e25899995e49); no E223 datum read
- Sat 21 Nov 2026 02:22:09 PST step 03 FROZEN.txt written (rc 0) at 02:22:09 PST: 5551c2d7b7b6b5bc40526997a2d8bcbfe62fc8b1468da514781fa59d7543b850 FROZEN.txt; the freeze line = DECLARED-blind-e223.md f2795ec3..., DECLARED-blind-e223.json c74dc547..., forecasts-nominal-e223.csv dc47385d..., forecasts-nominal-e223.json aeb174a7...; msg/to-orchestrator-frozen.txt written (one line) for the orchestrator to post on #16; the five frozen files made read-only (444); q238-frozen-posts.txt read again at 02:22:09: mask-posimb IN; mask-mesh NOT (on disk 487188c7, posted 3d4942fa); mask-ceiling NOT (posted 02:21:44, after the declaration's 02:19:24 read; "a nonparametric REFERENCE, REPORTED, never a model candidate"; its FROZEN.txt then rewritten at 02:22:21); step 4 (counts) NOT NEEDED: E223 designs no tile
- Sat 21 Nov 2026 02:24:29 PST recheck (after the freeze, rc 0, 02:22:5x-02:24:29): s02b_nominal.py re-run in a process of its own (--test into work/recheck) and compared with the frozen fc-nominal.json: 193,210 fields, 0 differing; its checks equal (work/recheck/recheck.json)

## The freeze line (FROZEN.txt)

FROZEN.txt names the lane's own paths: here `work/step1/` is `inputs/step1/`, `work/step2/` is `inputs/step2/`; every file keeps its bytes. The scripts under `scripts/` carry the box's paths replaced (<W>, <LAB>, <SCRATCH>, ~), so their sha256 differ from the as-run hashes in logs/step1-sha256.txt / step2-sha256.txt; the declaration, the forecasts and the inputs keep their bytes. The work copy the forecasts were made from is a git archive of GitHub main c661275c (inputs/lab-commit.txt) plus Q238's frozen posimb-mask folder at its own land path tools/matmul/mm1/v3.4-cands/posimb-mask/ (every file equal to its FROZEN.txt lines, inputs/mask-posimb-FROZEN.txt).

```
# decl-e223 (round Q239): FROZEN at Sat 21 Nov 2026 02:22:09 PST (Pacific): the lab's declaration and nominal forecasts for its BLIND test of E223, before any E223 datum
# the freeze line (post these on #16): the declaration, then the nominal forecasts
f2795ec352ca6244e8af2167b5b9742e1c2dad7fa6e844eb6035957b8398b3c7  DECLARED-blind-e223.md
c74dc54746780a8d9a952e871a81510913b5e33c6934bdf6a23ee5124ee76e02  DECLARED-blind-e223.json
dc47385df5af5db0bf6ba4dcdc49f453506f8df88eb07ee488e3527d3bd32082  forecasts-nominal-e223.csv
aeb174a7ea93a73b0baeac3d404fe57013694118dfb39e2963fe1fc388aa424f  forecasts-nominal-e223.json
# the order: the declaration hashed Sat 21 Nov 2026 02:19:31 (logs/step1-sha256.txt ab0ae70cbd41d40e...), then the nominal forecasts made 02:19:40-02:21:38 PST and hashed (logs/step2-sha256.txt b11a802475ae85c1...), then this file
ab0ae70cbd41d40ece9c32b66063e390f3266c5c7b0412ac711fbb5496144102  logs/step1-sha256.txt
b11a802475ae85c1b576af1ab8e48936a6bc42a87bf51a1a6822e25899995e49  logs/step2-sha256.txt
ce01e77fec05f13c6bf95464e289bf0bd1ac785e97aa935b8201850b44dd4b50  work/step2/fc-nominal.json
# models: MM1-v3.2 (the registered baseline, 4e386f75), MM1-v3.3 = 'MM1-v3.2 + AF4' (E222's SEL; equal to MM1-v3.2 on every E223 case), MM1-v3.1 (2c971828), MM1-v3 (b1493082), MM1-v2; REPORTED: Q234's posimb and L3S, the compositions by E222's and E224's construction, Q238's 'MM1-v3.2 + posimb-mask' and 'MM1-v3.2 + AF4 + posimb-mask'
# W/out/orch/q238-frozen-posts.txt read again at Sat 21 Nov 2026 02:22:09 PST (work/q238-frozen-posts-at-freeze.txt): mask-posimb posted 0cd8e9da = on disk: IN this freeze; mask-mesh on disk 487188c7f0ddce244f09abb05aeca4427e69d4be9133e87154863cdc4abec425, posted lines matching it: 0 (the line posted at 02:03:18 reads 3d4942fa): NOT in this freeze; mask-ceiling on disk 1649ba5ba69e1061af112e0ce6b98e4d42101080cd9e202f1bacea51edb8b45f, matching posted lines: 1: NOT in this freeze (the declaration's rule: a candidate qualifying after its 02:19:24 read joins only by a dated amendment hashed before E223's first datum)
# 695 cases (803 runs) x 13 models, all IN MM1's domain (none OUT OF DOMAIN); step 4 (switch counts) NOT NEEDED: E223 designs no tile; no E223 datum read by this lane; /usr/bin/python3 3.12.3
```

## What is declared (DECLARED-blind-e223.md; the JSON is the machine form)

- **The runs:** 803 runs in 695 cases, by id from the kit's schedules; every case in domain; classes ANCHOR, PLACE, EDGE, L3, WIDE, GATE, KIND, CELL111, SHAPE (the placements first); the 15 held-out sets; MASKE221 (blind-e221's MASK class by its own definition); GATESET (the masked energy cases); FULL and SUB; configuration twins apart.
- **The quantities:** wall cycles (T1), the counter mean (T2), seconds a pass (T3), W and J over idle given t (E1) and J over idle with t forecast (E2), J at rest given t (E3) and with t forecast (E4), per card, format, kind, class and held-out set.
- **The models:** MM1-v3.2, MM1-v3.3, MM1-v3.1, MM1-v3, MM1-v2, MM1-v3.2 + posimb, MM1-v3.2 + L3S, MM1-v3.2 + posimb + AF4, MM1-v3.2 + posimb + L3S, MM1-v3.2 + AF4 + L3S, MM1-v3.2 + all three, MM1-v3.2 + posimb-mask, MM1-v3.2 + AF4 + posimb-mask (all but the first five REPORTED). MM1-v3.3 = 'MM1-v3.2 + AF4' (E222's selection) equals MM1-v3.2 on every E223 case: AF4 acts only at gemmLnc tokens and E223 runs none.
- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the data's start-of-run records only (the callers: scripts/s02b_nominal.py's forecast_cases); a second footing, the nominal forecasts here, scored beside.
- **The comparisons:** exact sign tests per case: MM1-v3.3 vs MM1-v3.2 (NO DATA by construction), MM1-v3.2 vs MM1-v3.1 and vs MM1-v3 (H1-H5); on the placement class, each REPORTED mask candidate ('MM1-v3.2 + posimb', 'MM1-v3.2 + posimb-mask') vs MM1-v3.2 (H1, H2, H3, H5), REPORTED; L3S on its full-mask cases REPORTED; the switch route NOT APPLICABLE (no operand-pattern arm).
- **The pass rule:** part A (MM1-v3.2 within E215's bands on 90% of each card's no-twin cases, every rule), decided by the scoring lane's script, hashed before its first read; the others by the same rules REPORTED; part S NOT APPLICABLE.
- **E223 designs no tile:** every tile file it names is one of the lab's kinds byte for byte, so no switch count is made (no step 4).

## The nominal forecasts (forecasts-nominal-e223.csv / .json)

- Conditions: {"aifoundry1 card 0": {"V": null, "f": 800.0, "t0_c": 55.0}, "aifoundry1 card 1": {"V": 0.517, "f": 600.0, "t0_c": 60.0}, "aifoundry2 card 0": {"V": null, "f": 800.0, "t0_c": 55.0}}.
- 695 cases x 13 models: MM1-v3.2, MM1-v3.3, MM1-v3.1, MM1-v3, MM1-v2, MM1-v3.2 + posimb, MM1-v3.2 + L3S, MM1-v3.2 + posimb + AF4, MM1-v3.2 + posimb + L3S, MM1-v3.2 + AF4 + L3S, MM1-v3.2 + all three, MM1-v3.2 + posimb-mask, MM1-v3.2 + AF4 + posimb-mask.
- Energy: every model FORECAST on every case ({"FORECAST": 695} for MM1-v3.2).
- The terms' scopes: {"AF4 (gemmLnc)": 0, "L3S (full mask, gemmL)": 182, "posimb (subset masks of rgm136 gemmL)": 513, "posimb-mask (subset masks of rgm136 gemmL)": 513}.
- Checks before any output: E224's frozen forecast rows re-made by E224's own callers (2431 rows, worst relative difference 0.0); posimb-mask's frozen E222/E224 rows re-made (294 rows, worst 0.0).
- Recheck after the freeze (inputs/recheck/recheck.json): 193210 fields re-made in a process of their own, 0 differing.

## Not in this freeze (REPORTED candidates only)

- Q238's mask-mesh ('MM1-v3.2 + mesh'): its freeze line posted at 02:03:18 PST names a FROZEN.txt sha256 (3d4942fa...) that is not the file the lane holds (487188c7..., written 02:03:37 PST), at the declaration's read (02:19:24) and at the freeze (02:22:09).
- Q238's mask-ceiling ('MM1-v3.2 + mask-ceiling', a nonparametric reference, never a model candidate): frozen 02:21:13 and posted 02:21:44 PST, after the declaration was read and hashed (02:19:24 / 02:19:31).
- Either joins the blind test only by a dated amendment hashed and posted before E223's first datum (the declaration's rule), else is scored as UNREAD.

## Files

- `DECLARED-blind-e223.md`, `.json`: the declaration (section 0 the domain, a the runs, b the quantities, the models, the forecast procedure, c the metric, d the comparisons, e reported beside, f the pass rule, g the label rule, h the nominal footing, i the earlier reads, the inputs by sha256).
- `FROZEN.txt`: the freeze line as written for the Discussion.
- `forecasts-nominal-e223.*`: the frozen nominal forecasts.
- `DOMAIN-e223.md`, `domain-e223.csv`: the domain table (made from the declaration and the run list after the freeze; not in the freeze line).
- `inputs/`: the step files (the run list, the domain probe, the models' records, the twin keys, the bands, the nominal forecasts' full record), the recheck, the Q238 posts as read, the posimb-mask FROZEN.txt, the kit copy's SRC-SHA256SUMS.txt and the lab commit.
- `logs/`: the progress log and the step hash lists. `scripts/`: every script as run (box paths replaced).

Python: /usr/bin/python3 3.12.3 (-I -B), numpy, every numerical job single-threaded inside slot.sh. No card, no simulator, no ssh, no commit by this lane. SPDX-License-Identifier: Apache-2.0

# DECLARED-unread.md, dated note 1 (POST HOC): corrections after the verify (fix-unread-e212sw, Q218, Wed 18 Nov 2026)

**Label: POST HOC.** Written from 07:35 PST Wed 18 Nov 2026, after the unread lane's read (06:59:15 PST) and after its verifier,
verify-unread-e212sw (07:04-07:35 PST, verdict HOLDS WITH FIXES). **The declaration it corrects stays as hashed before the read**, byte for
byte: `DECLARED-unread.md` sha256 `f1daf832cc0078ef8fe90d108ce646cd3d656ca96634928deb2cfe6787aae44f` and `declared-unread.json` sha256
`5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc`. The forecasts (`forecasts-unread.csv` 2c26f013..., `forecasts-unread.json`
8938bbeb...) and the scores (`scores-unread.json` a535d78c...) are unchanged too. **No declared number and no verdict changes:** the pass rule,
decided by `scripts/s03_score.py` on the declared list, reads PASS. That scorer, re-run unchanged at 07:44:06 PST from a fresh copy of its inputs,
gives byte-equal CSVs and an equal JSON, apart from its two clock stamps.

Each item names the verifier's finding it answers.

## 1. Section a, the runs: E209's three real points were missed by the declaration's own rule (finding 1, medium)

- **What section a's rule takes in:** committed runs whose kind MM1-v3 left NOT FORECAST in energy for want of a count, and which now have one
  (group A). Group B is the same with the count committed and only phi missing.
- **What it missed:** three E209 points on aifoundry2 card 0 under its governor (data commit ea3fa3ce), each run with E206's four real2 tiles of
  its format (byte-equal to the files the phi rule and the frozen counts read):
  - e35: int8, `gemmL1x3x2`, 1 run;
  - e36: fp16, `gemmL3x5x5`, 1 run;
  - e34: fp32, `gemmL2x6x10`, 2 runs.
- **Why they belong in the test:** MM1-v3 as landed gives e35 and e36 no count and e34 no phi, and the frozen counts hold rows for e35's and
  e36's tiles. So e35 and e36 belong in group A and e34 in group B.
- **Why they were missed:** the lane's brief named E212, E206 and E207, and its list was built from those. The counts lane's NOT FORECAST list
  scanned energy points and E212 runs only. MM1-v3 read E209 for time only (data_v3's energy gate takes random, zeros and ones).
- **The fix: scored post hoc as ADDENDUM 1** (README section 9.1; files in `addendum-1-e209/`). The addendum keeps the declared rules and
  follows the same order, each step hashed before the next:
  1. its declaration at 07:47:44 PST (`addendum-declared-e209.json` 5f9e7f21...);
  2. its forecasts at 07:53:34 PST (`forecasts-e209-posthoc.json` 18438c3f...), made by the unread lane's step-2 machinery unchanged, which
     re-made four frozen entries bit for bit;
  3. its read and score at 07:55:15 PST (`scores-e209-posthoc.json` 8ab39919...).
- **Results, Q1 (W over idle given the measured seconds):**

  | point | MM1-v3 | null N |
  |---|---:|---:|
  | e35 | -0.01% | -23.13% |
  | e36 | +4.75% | -31.74% |
  | e34 | +2.18% | -33.12% |

- **The share of D cannot be scored:** none of the three has a zeros point at its configuration in E209.
- **Group A with e35 and e36 added** (REPORTED, post hoc): MM1-v3 6.71% rms against N's 25.10%. MM1-v3 is closer on 37 of 42 non-tied cases
  (2 ties), p = 4.4e-07, so P1 and P2 hold. P3 and P4 are unchanged.
- **Group B with e34 added:** MM1-v3 3.99% rms against N's 41.96% (n 4).
- **Label: post hoc and UNREAD, not blind.** MM1-v3 and the counts were frozen before any lane read these runs for this test. But E209's data,
  verify and scoring lanes had read them, MM1-v3's design lane v3-design-a had tabulated MM1-v2's error at all 45 E209 points (item 2e), and the
  verifier scored them first. These numbers equal the verifier's to 2.2e-16.

## 2. Section g, earlier reads: corrections

a. **mm-residuals also read E206 arms A and B** (finding 2, low).
   - Its committed table `tools/matmul/mm1/residuals/residuals-2026-11-17.csv` (a514caf0) holds the measured W over idle of E206 arm A's p110-p115
     and arm B's p111 and p113-p115. It also holds E207's six points, which section g already listed under E207.
   - v3-design-a's `diag_terms.py` and `diag2_groups.py` read that table before MM1-v3's freeze.

b. **mm-data is withdrawn from the E206 arm A line** (finding 5, nit).
   - Its 43 files date from 09:54-10:31 PST Mon 16 Nov 2026, about eight hours before E206 arm A's data commit d7e4f35e (18:26:14 PST).
   - Its search hits were the token `e37`, the older experiment E37's kind name.

c. **Only E212 a2c0-S2's 8 runs are clean** (finding 3, low). Of the 15 cases no MM1-v3 design or spec lane tabulated, seven are not clean
   (E206 p112 and E207's six). Two lanes wrote their measured W before MM1-v3's freeze:
   - MM1-v3's own build lane, mm1-v3, into its committed `out/points_energy_v3.csv` (unpriced there);
   - mm-residuals, into its table.

   Only a2c0-S2's 8 runs were tabulated in energy by no MM1-v3 lane:
   - MM1-v3's `out/unread_v2_e212_runs.csv` holds them for time only, with every energy column empty;
   - no residual lane could have them, because mm-residuals predates the session.

   The declaration's own sentence, "The a2c0-S2 split is the cleanest part", is right. It was the README's section 0 that called the wider
   15-case split "the cleanest part", and it is corrected there.

d. **Two numbers seen before this declaration** (finding 6, nit). The verifier found both in the harness transcript:
   - E210.md's quote of E206's S1 random-minus-zeros D, 29.78 W, which is the reference D of group B's p110;
   - a1c1-S2's session rest values in its `queue.json`, 29.91 W and 51 C.

   Neither is a group A value, and neither enters a forecast.

e. **E209's earlier readers** (for the addendum):
   - card-e209 (the session and its checks) and collect-e209 (the collection and E209's step-13 scorer, with joules per point against the frozen
     MM1 forecasts);
   - verify-e209d, fix-e209d (its dated note 15) and scores-e209;
   - v3-design-a, whose `work/diag/diag_terms.json` (14:03 PST Tue 17 Nov) holds MM1-v2's J-over-idle error at all 45 E209 points, e34-e36
     included, and prints e36 among the worst (+7.51%);
   - the public report's lanes, which copied E209's committed scores into their work trees;
   - verify-unread-e212sw, which scored MM1-v3 on these three first, post hoc.

## 3. The counts, by their committed folder (finding 4, low)

- **What the declaration cites:** the counts by the scratch lane's name, fix-v31counts, and their `SHA256SUMS`, sha256 c74c2d49...
- **Where they are now:** the same files are on GitHub main, unchanged, as `tools/matmul/mm1/v3.1/counts/`. Commit 3e8991d0 (07:23:56 PST
  Wed 18 Nov 2026) added the folder, and its `SHA256SUMS` has the same sha256, c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f.
- **Checks:** `diff -r` against the land dir the test used found no difference, and `sha256sum -c` gave 71 of 71 OK at 07:42:01 PST.
- The declaration keeps its scratch name, because it is hashed.

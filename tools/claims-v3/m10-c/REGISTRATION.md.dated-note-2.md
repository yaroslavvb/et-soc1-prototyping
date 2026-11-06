# REGISTRATION.md, dated note 2: E178 is the term's blind test for 23 of its 27 float kinds, its 4 bridge kinds re-measure fit kinds; the entry rule's statistics on the 23, registered as a REPORTED split; the tie against its own bytes as a kind row, the kinds whose accumulator cannot move, and the verifier's other faults (Q148(c), before any E178 datum)

*Written Fri 6 Nov 2026 (week 45), about 06:13-06:50 PST, on the Intel, desk only (no card, no lab box, no device command, no bench,
no post, no Modal), by the lane fix-termc of Q148, after the verifier verify-termc read `c71fbc7f`, `413d252b` and `6b5ad913` (holds
with fixes: 1 major, 3 minor, 2 nits). [`REGISTRATION.md`](REGISTRATION.md) (`c71fbc7f`), [dated note 1](REGISTRATION.md.dated-note-1.md)
(`413d252b`) and every file of `6b5ad913` stay as committed, `termc.py` among them. **Committed before any E178 datum:** `git log --all`
shows no commit under `docs/reports/data/` naming E178 (checked at 06:31 PST and again before the commit). Nothing under
`tools/claims-v3/e178/` is written. The figures below are printed by [`termc_note2.py`](termc_note2.py) (new, beside `termc.py`, which it
imports unchanged), run at 06:30 PST through the round's local slot on one core; [`termc-note2.txt`](termc-note2.txt) and
[`termc-note2.json`](termc-note2.json) hold them. **The choice to leave the entry rule as registered (section 1) was made before any of
them was computed.***

**Labels.** Section 1's split is a **REPORTED arm**, registered now, before E178's first datum: never a verdict, never the entry rule. Its
power is **design arithmetic**. The readings of sections 2, 3 and 6 are **post hoc**, on fit rows already read. Nothing registered moves:
the form, the rows, λ, L, the intervals, σ_C, the arms, the forecasts, the entry rule, its seeds and its power stand as committed.

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 06:22 PST: public rows L04,
   H07, H15, H21, H27 and H29; the registration's block (`c71fbc7f`) for the rest.
2. **Used.**
   - **E178's registration** (H27; `48171930` `tools/claims-v3/e178/`): `E178.md` lines 51-53 (C's arithmetic: fp32 rounded per step to
     nearest even with DAZ/FTZ, fp16's 2-term update in its fixed-point window), line 77 (R3, "the bridge to committed one-number kinds")
     and lines 78-80 (R4, `fp32.e178_uf`, whose accumulator "never leaves +0"); `kinds-e178.json`, `forecast-e178.json` and `tiles/`, read
     through `termc.e178_float_kinds`, which checks each tile's sha256.
   - **The term's own fit** (`6b5ad913`): `termc-fit.json` (its sha256 checked against `SHA256SUMS`), `kinds` and `rows.fit_rows`; each fit
     kind's tiles re-hashed (14 kinds, 18 paths).
   - **M10's rows** (H21; `6829c9ba` `docs/reports/data/2026-11-04-q142m-m10/rows-m10.json`, with `fit_m10.assemble`), by `termc.m10_classed`.
   - **Q139(u)'s footing** (H15; `f47669d1`): `reduced/e78-footing.json` and `reduced/e82-footing.json`, items `anchor_pi` and `fp32.pi`
     and their `per_pass` rows.
   - **The host's built-in kinds** (`workloads/sparsity/host/main.cpp`, `fillValues`, `27dce7f0`): every element the same word for
     `zeros`, `ones`, `twos`, `pi` and `onebit` (fp32), `zeros` and `ones` (fp16 and int8); the source lines are checked by string.
   - **E7 and E8** (L04, the September Horace experiment; `df89c94f` and `04746a3c`,
     `docs/reports/data/2026-09-20-power-aifoundry2/horace-runs.jsonl` and `horace2-runs.jsonl`): the launches of `twos`.
   - *Check against an earlier measurement of the same quantity at the same operating point:* section 2 is that check for the tie (the same
     bytes, measured in the same passes as a kind row). Before the split's power is computed, `termc.power` at 14 + 13 kinds reproduces
     `termc-fit.json`'s power table exactly; the footing reductions' per-pass D reproduce their items' means and counts.
3. **Not used.** E7's and E8's `twos` rows as fit rows (another card under its own clock, a superseded protocol, not on M10's footing); the
   GPU runs that name `twos` (H29: E135, E149, E150, E162; another chip); the committed text about Horace He's post that names it.
4. **Tiers.** Public tier only: the lab's committed data and code. No NDA-tier check is used, so there is no sha256 line, and no NDA-tier
   piece, name, verdict, ratio, direction or figure is cited.
5. **Readiness:** this block is the note's own.

## 1. E178's 27 float kinds: 23 new to the term, 4 the bridge (verify-termc's fault 1, major)

- **By sha256** (`termc_note2.py` checks [2] and [3]), 4 of E178's float tiles are the term's fit kinds: `fp32.ones` (9 rows in 9 runs),
  `fp32.neg_ones` (2 in 2), `fp16.ones` (10 in 10) and `fp16.neg_ones` (2 in 2). They are E178's R3, "the bridge to committed one-number
  kinds" (`E178.md` line 77). **They are blind by session only:** E178 is a new session, but the level was fitted on their bytes.
- **The other 23 (12 fp32, 11 fp16) match no fit kind, no float row of M10's (737), and no `.bin` file committed at `6b5ad913` outside
  E178's own tiles (15,231 files).** 22 of them also match no host built-in kind, so no committed measurement on this chip ran them. The
  23rd, `fp32.e178_v2` (2.0 in every element of A and B), holds the bytes the host's built-in `--values twos` writes, which E7 and E8 ran
  on aifoundry2 on 20 Sep 2026 (28 launches each, fp32, 0.58-0.60 GHz; both superseded by E9). Neither M10 nor this term reads those rows,
  so `fp32.e178_v2` is blind by kind for the term and for M10, but it is not new to the chip. Every other committed mention of `twos` is a
  GPU run (E135, E149, E150, E162) or text about Horace He's post (check [4]).
- **Corrected wording** (the files stay as committed):
  - the registration's opening paragraph, "none of them has been measured, so E178 is the term's first blind test";
  - registration section 8, "**Blind:** nothing here; E178's float kinds are the first blind test";
  - registration section 10, "the first blind test is E178's float kinds";
  - the README's labels, "Nothing here is blind; the first blind test is E178's float kinds";
  - the README's "What this changes", "E178's float kinds (constant-lane tiles every one, none measured before) are its first blind test".

  **Read instead:** E178 is the term's first blind test for 23 of its 27 float kinds; its 4 bridge kinds (R3) re-measure fit kinds and
  are blind by session only. The records quote it as **"blind for 23 of its 27 float kinds"**.
- **The entry rule is unchanged.** Registration section 6's C1 and C2 read every float kind E178's scorer keeps, the 4 bridge kinds among
  them, and section 7's power stands as committed. Reading only the 23 would be a rule change; this note does not make it.
- **Registered now, a REPORTED split (never a verdict, never the entry rule).** After E178's data, on the kinds the registered rule
  scores (E178's `c_kept`, a `D_w` in 2 or more kept passes):
  - **the split:** registration section 6's C1, unchanged in every part (d = rms(x′) − rms(x); its 95% interval by a bootstrap over
    kinds, 2,000 draws, `random.Random(1782)`; BETTER at d ≤ −0.010 W with the upper end below 0, WORSE with the lower end above 0, else
    NOT RESOLVED), C2 (d < 0 in fp32 and in fp16 separately) and m_φ (the mean of x per format with its t-interval over kinds), computed
    on **the new kinds alone**;
  - **beside it:** m_φ, x and x′ on the 4 bridge kinds;
  - **which kinds are the bridge:** a tile whose sha256 equals a fit kind's in its format, frozen in `termc-note2.json` and checked
    again by bytes at scoring (the scorer stops if they differ). Fewer than 2 kept passes: NOT SCORED, as the rule.
  - **The code:** `termc_note2.py score --scored <E178 scored.json>`. It calls `termc.score_session` exactly as committed for the
    registered rule and prints its result unchanged (check [7] compares them byte for byte), with the split beside it. `termc.py score`
    stays the registered scorer.
  - **How the records read the two:** the rule's verdict decides entry. If the rule reads BETTER with C2 and the split does not, the
    entry rests partly on kinds the level was fitted on, and the records say so beside the verdict. The next blind pool's P-C, on new
    tiles, is the term's next test either way.
- **The split's power** (design arithmetic: registration section 7's model, aifoundry3's L and σ_C, `numpy.random.default_rng(1783)`,
  C1's bootstrap at 1,000 draws; 12 fp32 + 11 fp16 kinds; `termc-note2.json` › `power_split`), beside the rule's at 14 + 13, which
  `termc.power` reproduces first:

  | truth | σ_com 0 | 0.02 W | 0.04 W |
  |---|---|---|---|
  | the level is right: the rule enters / the split reads BETTER with C2 | 0.556 / 0.485 | 0.488 / 0.466 | 0.532 / 0.488 |
  | half the level: the same | 0.037 / 0.033 | 0.159 / 0.134 | 0.262 / 0.258 |
  | no level: the same | 0.0005 / 0.000 | 0.009 / 0.006 | 0.102 / 0.098 |

  On 23 kinds the split reads a right level BETTER a little less often (0.47-0.49 against 0.49-0.56), and a wrong one about as rarely.

## 2. The tie against its own bytes measured as a kind row (fault 2, minor; post hoc)

The tie is 32 of the pi kind's 34 rows. Only E78 and E82 hold both the tie (`anchor_pi`, run first and last in each pass) and `fp32.pi`
(the same bytes, `pi.bin`, run once in each pass as a kind row). On Q139(u)'s footing (`tie_vs_kind`):

| session | tie D, W (se) | `fp32.pi` D, W (se) | kind − tie, W | paired by pass, W |
|---|---|---|---|---|
| E78, aifoundry3, 6 passes | 8.3557 (0.0280) | 8.4637 (0.0442) | **+0.108**, z 2.06 | +0.108 ± 0.0545 |
| E82, card 1, 7 passes | 8.0634 (0.0373) | 8.0998 (0.0447) | **+0.036**, z 0.63 | +0.036 ± 0.0504 |
| pooled (inverse variance) | | | **+0.076 ± 0.039** | +0.069 ± 0.0370 |

- **The bound on L.** Had the tie read like a kind row (each tie row's miss raised by the pooled +0.076 W), fp32's L on aifoundry3 would
  read **+0.0475 W**, 0.012 W above the registered +0.0354 and inside its [−0.053, +0.124]. Paired: +0.0464 (+0.011). With pi read from
  its two kind rows alone: +0.0450 (+0.010). fp16 has no tie.
- **Why it matters for E178:** E178's kinds run as kind rows, and pi is 1 of fp32's 6 kinds, so a tie that reads low pulls fp32's level
  down by about that much.
- **What it cannot say:** two sessions. Whether the gap comes from the tie's place in the pass (first and last) or from the same bytes read
  twice in another way is not separated. The registration's "the tie ... counts once, as a new E178 kind will" stands as a weighting, but
  the tie's rows are not shown to be exchangeable with a kind row's.

## 3. The kinds whose accumulator cannot move (fault 3, minor; by bytes, then post hoc)

- **By bytes** (`accumulator`, check [5]), under E178's arithmetic model (`E178.md` lines 51-53), **four** of the term's 11 one-word fit
  kinds add exactly 0 to C at every step, so their accumulator never moves:
  - `fp32.nz_both`: −0 × −0;
  - `fp32.dn1_both`: the smallest denormal squared, zero by DAZ;
  - `fp16.nz_both`: −0 in both halves;
  - `fp16.c_cancel`: A 1.0 in both halves and B's lane word `0xbc003c00` (+1.0 and −1.0), so each 2-term step adds 1 − 1 = 0, in
    either pairing of the halves.

  The verifier counted three by name; `nz_both` runs in both formats.
- **Of E178's 27 float kinds, 26 move the accumulator and one does not:** `fp32.e178_uf`, R4's kind, whose products flush to zero, so its
  accumulator "never leaves +0" (`E178.md` lines 78-80; its C must read +0 throughout). So the verifier's "unlike every E178 kind" reads
  "unlike 26 of E178's 27". All 13 of E178's fp16 tiles hold one number in both halves.
- **Post hoc, the four read a higher level than the seven that move** (each set by the registered estimator, L on aifoundry3;
  `still_kinds_levels`):

  | format | registered (all kinds) | without the kinds that cannot move | those kinds alone |
  |---|---|---|---|
  | fp32 | +0.0354 [−0.0533, +0.1241], 6 kinds | +0.0266 [−0.0738, +0.1270], 4 kinds, 32 runs | +0.0530 (2 kinds) |
  | fp16 | +0.0703 [+0.0241, +0.1164], 5 kinds | +0.0550 [−0.0025, +0.1125], 3 kinds, 11 runs | +0.0931 (2 kinds) |

  - So without them, **fp16's interval reaches 0**.
  - Leaving out one kind at a time: fp32 `dn1_both` +0.0301, `nz_both` +0.0337; fp16 `c_cancel` +0.0578 (the verifier's reading),
    `nz_both` +0.0713.
- **What it changes:** nothing registered. If the level depends on whether the accumulator moves, E178's 26 moving kinds read nearer the
  lower figures, and P + L runs high by about 0.01 W (fp32) to 0.015 W (fp16), well inside σ_C (0.094 and 0.055 W). Not modelled, and
  not separable on these few kinds. Registration section 3.1 lists these rows, so this is a disclosure, not a departure.

## 4. E178's checks (fault 4, minor)

The lane's result said "all six E178 hash lists and all of its --check scripts read unchanged". It ran 6 of the 10 E178 scripts that take
`--check`: `make_e178_kinds`, `forecast_e178`, `plan_e178`, `rail_e178 freeze`, `flips_e178_a1` and `power_e178_a1`.
- verify-termc ran the other applicable ones at 06:00:07-06:09:30 PST. All passed:
  - `make_harness_e178 --check` (84 files);
  - `make_kit_e178 --check`;
  - `power_r_e178_note1 --check` (byte for byte);
  - `check_e178.py --desk` (80 files).
- `scrub_tree_e178 --check` reads a run's output directory, so it applies only after data.
- **The records' wording:** "E178's six hash lists and nine `--check` scripts (every one that applies before data), with
  `check_e178.py --desk`, pass after the term's commits".
- This note's commit is re-checked the same way after it lands. That run is recorded with the lane's result, not here.

## 5. The power's "at most 0.10" (fault 5, nit)

- README section 4 says E178 "rarely admits a wrong term (at most 0.10)", and its table rounds to 0.10 at no level and σ_com 0.04 W. The
  committed figure is **0.102** (`termc-fit.json` › `power`). Read "about 0.10 (0.102)".
- The table's 0.001 at no level and no common miss is 0.0005: one draw in 2,000.

## 6. The jackknife's degrees of freedom (fault 6, nit; a reported caveat)

The registered interval takes its t at n − 1 (df 31 for fp32, 12 for fp16), but its variance comes from a few runs (`jackknife_df`):

| format | runs whose leaving-out moves L by over 0.005 W | Kish's effective runs | 95% at df 4, W | 95% at df 5, W |
|---|---|---|---|---|
| fp32 | 5 (E78 −0.019, E82 +0.020, E93 +0.021, E102 +0.018, E121 −0.021); the other 27 under 0.0018 | 5.0 | [−0.085, +0.156] | |
| fp16 | 6 (E78, E82, E88, E93, E102, E121: 0.005-0.014); the other 7 under 0.0021 | 4.1 | [+0.011, +0.129] | [+0.016, +0.125] |

- "fp32's interval holds 0, fp16's does not" stands at each df.
- The registered interval stands, and so do the forecasts' level intervals. The predictive half-widths use σ_C and do not move.

## 7. What this note does not change

- **The term:** its form, rows, estimator, λ and L; its intervals and σ_C; the arms; the frozen forecasts; the entry rule with its
  thresholds, seeds and power; the scorer `termc.py score`.
- **The committed files:** every file of `c71fbc7f`, `413d252b` and `6b5ad913`.
- **E178:** its registration, dated notes A1-A3, kit, scorer, rules, forecasts, plan, stops and card-minutes.

## 8. Files and re-run

| file | what |
|---|---|
| [`termc_note2.py`](termc_note2.py) | `selftest`, `posthoc` (this note's figures) and `score` (after E178's data: the registered rule and the split beside it) |
| [`selftest-termc-note2.txt`](selftest-termc-note2.txt) | its self-test, 8 checks, all pass |
| [`termc-note2.json`](termc-note2.json), [`termc-note2.txt`](termc-note2.txt) | the split (bridge and new kinds, the scans), the split's power, the accumulator table, the tie, the levels without the kinds that cannot move, the jackknife's df |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | these files and the inputs they read |

From the top of the tree, under the Intel's `/usr/bin/python3` (3.9, numpy 1.26), one core:
- `python3 -B tools/claims-v3/m10-c/termc_note2.py selftest` (about 5 s);
- `python3 -B tools/claims-v3/m10-c/termc_note2.py posthoc --out <dir>` (about 35 s; writes the two outputs, byte for byte these);
- after E178's data: `python3 -B tools/claims-v3/m10-c/termc_note2.py score --scored <E178 scored.json> --out <file>`;
- `shasum -a 256 -c tools/claims-v3/m10-c/SHA256SUMS-note2`.

The scans read the tree at `6b5ad913` through read-only git calls.

SPDX-License-Identifier: Apache-2.0

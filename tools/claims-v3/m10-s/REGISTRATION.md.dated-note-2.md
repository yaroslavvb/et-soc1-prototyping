# Term S's registration, dated note 2: an independent verifier's faults, corrected, and the training set as § 3.1 defines it (99 steps) (Fri 6 Nov 2026, week 45; written from 03:48 PST)

*A dated note beside [`REGISTRATION.md`](REGISTRATION.md) (`dfc005bf`) and its [dated note 1](REGISTRATION.md.dated-note-1.md)
(`6f9ae408`). It changes no committed file, and no rule, form, threshold, seed or entry condition. It was written after term S's
outputs (`6f9ae408`) and after an independent verifier read them (Fri 6 Nov, about 03:03-03:30 PST: holds with fixes, 1 major and 7
minor faults). It is committed with its code, [`term_s_note2.py`](term_s_note2.py), before that code's first fit or check output.
Every figure that code writes is **post hoc**, and the data README's
[dated note 1](../../../docs/reports/data/2026-11-06-q145b-m10-s/README.md.dated-note-1.md) quotes them. The items below follow the
verifier's faults in order.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 03:30-03:47 PST: public rows
   L23, H20, P15, P12, H07, H09, H15, H16, H19, H21, H22 and H24 (opaque pointers), and the map's rows 3 and 18 and its section 4 step 2.
2. **Used.**
   - **The lane's committed code and outputs** (`dfc005bf`, `23e23210`, `6f9ae408`): `term_s_v2.py`'s `t_s`, its 95 steps, its
     `k_law` and its `run_fit`, the registered fit, imported and run unchanged.
   - **E67's registered reduction** (`69d4e251`, `docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json`): the grid's B margins
     `cards.aifoundry3.items.ix_b<k>` (`d_p80`, `d_p80_se`, `zero`, `rate`; the same numbers as `ix.margins`), its leak 0.17545 W/°C
     (`gates`), its kept passes; its README says "the registered one is the result". Their counts rows are in `e57e65a3`
     `docs/reports/data/2026-11-01-q132-rtl-bench/counts-hl.json` (`fp32.ix_b<k>`, `fp32.ix_z`).
     *Check against the same quantity at the same operating point:* E65 measured the same four positions (0, 8, 16, 22) on the same
     card at 600 MHz, with A = 1.0 and with A = π. They are set side by side post hoc (a reading, not a test).
   - **The footing law's FL3** for E67 (`c14e5f35`, `tools/claims-v3/footing-law/footing_law.py` `k_session`, `footing-law.json`),
     with E67's committed `runs.csv`, exactly as `term_s_v2.k_law` reads the other lists.
   - **E151's correction C2** (`5e61334d`, `docs/reports/data/2026-11-03-e151-int8-b-aifoundry3/README.md`, corrections after
     verification), and **E68's stage map** (`eb7b7373`, `docs/reports/data/2026-10-27-e68-stage-map/README.md` and
     `operands-manifest.json`), for item 6.
   - **M10's band** (`6829c9ba`, `docs/reports/data/2026-11-04-q142m-m10/m10.json` › `families.float.band_k`) and pool 8's scored
     rows (`91f8ae40` E171, `b3255af1` E172, `scored.json` › `primary.rows` › `M10_primary_95`), for item 5.
   - **Ditzel's "Esperanto Retrospective"** (P15; slide 12), for item 6 (d).
3. **Not used.**
   - **E67's clean-pass sensitivity** (`hl-clean.json`, its amendment A15): post hoc there, and not E67's registered reduction.
   - **E67's A side, its grid cells and its anchors:** A flips, or the tile is a constant. They fail T_S, so they are not applicable.
   - **E68's five single-B-bit items:** they ran at 800 MHz, so § 3.1 does not admit them (item 6 (b)).
4. **Tiers.** Public tier only: the lab's committed data and code, and a public talk. No NDA-tier check is used, so there is no sha256
   line.

## 1. E67's four single-B-bit steps belong to § 3.1's set, which is 99 steps, not 95 (the major fault)

- **§ 3.1 defines the set by a rule.** A training step is every price-list item that passes T_S, has a registered zero that passes T_S
  as a zero, has a measured step, is fp32 or fp16, and ran at 600 MHz. E67's interaction-grid B margins `ix_b0`, `ix_b8`, `ix_b16` and
  `ix_b22` meet every part of it:
  - A holds one word, 0x3fb10bd0;
  - each margin flips one B bit, at 0, 8, 16 and 22, over the grid's base `ix_z`, which passes as a zero;
  - each has a registered step and a counts row for item and zero (Builds on, Used);
  - all four ran at 600 MHz on aifoundry3, in E67's grid passes 770, 774 and 775.
- **They were missed because of a scan defect.** The lane's structure scan read one of E67's pass directories, `p750`, and the grid's
  tiles are in `p770`-`p775`. Two statements are therefore wrong:
  - the Builds on block's Not used line, "no E67 item passes § 2's test (its `lq_h0` and `lb_h0` are E65's ties)";
  - § 2's "95 steps in six runs".

  **Both are struck.** No record quotes "no E67 item passes" or "E67 has no B single bit". The set is **99 steps in seven runs**: 79
  fp32 and 20 fp16, 85 on aifoundry3 and 14 on card 1.
- **A census.** `term_s_note2.py census` reads T_S on every committed tile of the seven lists. It is structure only and reads no model
  value. It finds 99 single B bits: the 95 and these four, and no other.
- **What runs: the registered fit on the 99 steps, both footings** (`term_s_note2.py fit99`).
  - The code is `term_s_v2.run_fit`, unchanged. It is handed term_s_v2's 95 steps plus these four, and FL3's slope for E67 from E67's
    `runs.csv`.
  - It stops unless the 95 committed steps reproduce (measured step, M10's step and residual, each to 1e-12 W).
  - It is **post hoc**: the 95-step outputs and the verifier's what-if on the same 99 steps were read before it.
- **Which reading is which.** The 95-step reading stays as committed: it is what ran, a departure from § 3.1 that this note discloses.
  The 99-step reading is § 3.1's set, run after the fact. The records quote both, and read the entry rule (E1-E3) on both.
- **Where the term is carried as a reported arm** (§ 8), its frozen table is the 99-step S3 table
  (`note2-term-s-reg-99.json` › `frozen_values`), with the 95-step table beside it. This governs only the next blind pool's
  predictor, and none exists.
- **A post hoc reading, labelled post hoc (n = 4).** M10's step error on E67's four steps (dense A word) is set beside E65's steps at
  the same positions (A = 1.0 and A = π). This takes up the verifier's hint that M10's over-pricing of the lists goes with A = 1.0. The
  data README's note 1 gives the figures. It is a reading, never a test.

## 2. E1's interval resamples steps, but the steps of one list share a session, its base words and its reduction

E1 holds as registered: by the step bootstrap of § 4 (2,000 draws, seed 145). Beside it, `term_s_note2.py checks` resamples E1 by run
(10,000 draws, seeds 146-148, with a jackknife over runs). This is post hoc, on both footings and on the 95 and 99 steps.

The records quote E1 as "holds by its registered step bootstrap", with the run-level interval beside it. They never call the lists'
held-out gain resolved at the run level unless that interval also clears 0. A later term's registration should resample runs, or read
its interval at the run level.

## 3. The run order, in full

From the round's slot log, the files' times and git, all PST. Dated note 1 items 1 and 2 left part of this out.

**term_s.py and term_s_v2.py.**
- The self-test ran three times before `term_s.py`'s commit: 02:33:11, 02:33:28 and 02:34:21, each rc 0. § 9 asks for self-tests
  before the first full run.
- `term_s.py` as committed (`23e23210`, 02:34:39) ran one fit, 02:34:47-02:34:54. It stopped (rc 1) on E173's `tiles_scored`, as
  dated note 1 item 1 says.
- **Then five fit runs of an edited, uncommitted working copy of `term_s.py`**, each writing straight into the data directory:
  02:35:18 (reg), 02:47:59 (law), 02:48:07 (reg), 02:52:44 (reg) and 02:52:51 (law).
- At 02:53:41 (both files' times) that copy was saved as `term_s_v2.py` and the committed `term_s.py` was restored.
- **The committed `term-s-reg.json`, `term-s-law.json` and their outputs come from `term_s_v2.py`'s runs** at 02:54:08 (reg) and
  02:54:16 (law), after its self-test at 02:54:00.
- So dated note 1's "the fit therefore runs as `term_s_v2.py`, a new file" is true of the committed outputs only. The fit first ran
  five times as the edited `term_s.py`.

**law_m10.py.** It ran four times before its commit (`6f9ae408`, 02:55:32):
- 02:39:26-02:40:42, stopped (rc 1);
- 02:41:13-02:42:48, stopped (rc 1). These two are dated note 1 item 2's runs;
- **a third, complete run, 02:43:20-02:45:04 (rc 0)**, which wrote to the lane's scratch. Its outputs were later removed;
- **an edit of `law_m10.py`** (the file's time, 02:45:51). What changed is not recorded;
- the run at 02:46:07-02:47:50, which wrote the committed outputs.

`posthoc_structure.py` ran once, at 02:49:07.

**What the committed code gives.** This lane re-ran it unchanged into a scratch directory, 03:40:21-03:42:42 PST, as one slot job.
Every committed output came out **byte for byte**:
- both self-tests;
- `law-m10-output.txt`, `m10-law.json`, `rows-m10-law.json` and `p8-law.json`;
- `term-s-reg.json`, `term-s-reg-output.txt`, `term-s-law.json` and `term-s-law-output.txt`;
- `posthoc-structure.json` and `posthoc-structure.txt`.

The one exception is `law-k.json`, which differs only in six path-dependent hashes (item 7 (b)). So the order changes no figure. What
the removed outputs and the 02:45:51 edit held cannot now be shown.

`term_s_note2.py`'s own census and comparison first ran at 03:44 PST, before this commit. They read structure and file hashes only. Both
run again from the committed code, and those outputs are the ones committed.

## 4. The post hoc structure reading

The data README's § 5 shows four of `posthoc-structure.txt`'s five classes. It leaves out "zero, eight lane words": 3 rows, E102's `hq`
zeros on card 1. Its "eight base words" row (26) also mixes two kinds of row:
- E147's 15 steps, each over its own zero;
- 11 whole tiles over the format's zeros.

The classes cover M10's 737 float rows of its 959. The data README's note 1 gives all five classes, steps and whole tiles apart, and
the like-for-like reading (`term_s_note2.py checks`). The records quote that, not § 5's table.

## 5. The band (§ 4) was registered and never computed

No code or output holds it, and dated note 1 does not list the omission. `23e23210`'s message says the code covers "the band"; it does
not. This decides nothing while the term stays out.

Where the next blind pool's predictor carries the term as a reported arm (§ 8), it computes the band for each T_S tile as half-width
**√(h_M10² + (k_M10 σ_S)²)**:
- h_M10 is the tile's M10 band half-width as that predictor computes it, k_M10 √(pool² + s² xᵀCx), from `m10.json`'s `band_k` and
  `interval_pool_by_format_card`;
- σ_S is by format: 0.167 W fp32 and 0.217 W fp16 on the 95 steps (`term-s-reg.json` › `sigma_S_w`), or the 99-step values
  (`note2-term-s-reg-99.json` › `sigma_S_w`) with the 99-step table.

For pool 8's class S it is computed post hoc by `term_s_note2.py checks`, from the scorer's own M10 band.

## 6. Builds on, corrected

- **(a) E151 is a narrower precedent than the block says.** Its correction C2 says three things:
  - its per-position B prices were measured at one B base word, with A held;
  - all four sessions ran the same tiles;
  - so its transfers test days and cards, not tiles or base words.

  So E151 shows that a per-position B price repeats across days and cards at one base word. It does not show that a price carries
  across base words or tiles. That is the dependence this lane then found: the lists' per-position steps do not carry to pool 8's
  one-base tiles. int8 stays out for the block's other reasons: pool 8 holds no int8 class-S tile, and M10's int8 family has no S
  class.
- **(b) E68 is in row L23, and the block named it nowhere.** It is aifoundry2's stage map at 800 MHz, run on 512 minions. Its
  operands manifest holds **five single-B-bit items**, each over a constant zero, on an eight-word base (the manifest's `base`):
  - `sm_sgn` (bit 31, A = 1.0) and `sm_pi_sgn` (bit 31, A = π);
  - `sm_e1`, `sm_e16` and `sm_e64` (bits 23, 27 and 29).

  They are **not applicable as training steps**, because § 3.1 admits only 600 MHz. Two more limits:
  - its pass directories keep only the operand files' hashes, so T_S cannot be read on their bytes;
  - its leakage correction is unresolved (its registered A1 slope of 1.508 against E66's 0.296 W/°C).

  So the Not used line "An 800 MHz price list: none is committed" and § 10's "800 MHz has no list" should read: **no 800 MHz price
  list exists on the kinds' footing.** E68's five steps (aifoundry2, half the minions) are the nearest, and a possible check of § 5's
  carry. That check is owed, not run.
- **(c) The check is on 15 rows, not 70.** The Used line's check names "E147's 70 rows" against M9's committed step features. The
  self-test compares E147's **15** T_S steps, the only E147 rows this lane uses (`selftest-term-s.txt` ›
  `e147_step_features.rows_compared` 15, largest difference 0.0).
- **(d) The bench's faithfulness note was owed and named nowhere.** The stock-take's map asks for it in its row 18: the bench models
  the open RTL's register files, not the silicon's. It is now written as
  [`rtl-sim/fma_toggle_v2/README.md.dated-note-1.md`](../../../rtl-sim/fma_toggle_v2/README.md.dated-note-1.md), committed with this
  note. § 1's public-source reason cites it.

## 7. Labels

- **(a) "Held out, M10 as frozen" (S0) is in-sample for M10 on 25 of the 95 steps.** M10 was fitted on E147's 15 steps and on the item
  and zero rows of 10 of E102's 14. S0 is the base, not a fitted form. The forms S1-S3 stay held out over runs: their values are
  fitted leave one run out. The records say so, and quote the size of the in-sample share from `term_s_note2.py checks` (the data
  README's note 1).
- **(b) Six of `law-k.json`'s `law_sha256` values are path-dependent:** E78, E82, E86, E90, E92 and E95.
  - These six sessions are re-reduced from dip-filtered pass copies. Their law reductions' `dirs` lists name the run's own scratch
    directory, so no re-run elsewhere can reproduce those six hashes.
  - Each committed hash is the hash of the reduction the lane's committed run wrote.
  - The content check is the reduction less its `dirs` list. In this lane's re-run all six are identical on it, and the other 24 law
    reductions are identical byte for byte (`term_s_note2.py compare`).

## 8. Times and rounding

**The true times are the commits' own, in PST. The records quote these:**

| file | its text says | committed |
|---|---|---|
| `REGISTRATION.md` | "written about 02:25-03:00"; dated note 1 and the data README: committed "about 02:31" | `dfc005bf`, **02:28:32** |
| `term_s.py`, `selftest-term-s.txt` | (none) | `23e23210`, **02:34:39** |
| `REGISTRATION.md.dated-note-1.md` | "about 02:50-03:05" | `6f9ae408`, **02:55:32** |
| the data README | "about 02:05-03:10" | `6f9ae408`, **02:55:32** |

**Two roundings:**
- **P8-M1 on the law for E171** reads −0.052 W **[−0.105, −0.003]**: `p8-law.json` › `E171.law.P8-M1.lo95` is −0.10549. The README, the
  lane's result and its headline say [−0.106, −0.003].
- **The exponent bits 28-30's measured steps run 0.74-1.10 W**, not 0.80-1.10. E65's bit 30 is 0.735 W (`term-s-reg.json` › `steps`).
  M10 reads 1.26-1.57 W there, as the README says.

SPDX-License-Identifier: Apache-2.0

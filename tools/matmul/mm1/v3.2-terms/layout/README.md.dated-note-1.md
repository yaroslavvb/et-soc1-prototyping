# Dated note 1 to the layout term: its two checks, the land's hash, how to read F1, and the controls beside it

*Thu 19 Nov 2026, Pacific time. Written by land-terms (round Q225) from 12:10 PST, before this lane read any E215 datum (it read
none at any time). Desk only. Every number below comes from the two checks named, which ran on committed data and on this folder;
each is **desk** and **post hoc**, and **held out** where it says so; nothing here is blind. This note changes no file of the folder:
the README, the declarations, the code, the outputs and the two frozen forecast files are committed byte for byte as lay-contention
left them. The one addition beside them is `controls-e215/` (see its README).*

## What is committed here, and its freeze line

- **The two frozen files**, final at **09:31:34 PST** before any E215 datum, were posted by their sha256 as post **#1.29.1** on the
  owner's coordination thread at **09:32:47 PST** (before check-lay ran). That post is their freeze line:

      50949ba38ff7f16db601408fc523e81462cc04df3dddb38dd3007106e3a30754  forecast-e215-v31-layout.csv
      f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259  forecast-e215-v31-layout.json

  This commit is a later record of them, not their freeze line. E215's two arms were held from 09:59:39 PST and released at about
  11:55 PST, after the freeze posts.
- **The land's own hash.** Post #1.29.1 also gave the land's `SHA256SUMS` as `d5ec254d80ad7b5c...` (19 files). After the freeze the
  lane added REPORTED files (`joint_layout.py` with `out/joint_layout.json`, `placement_layout.py` with `out/placement_by_config.csv`,
  `pairs_fitrecords_layout.py` with `out/pairs_fitrecords.json`) and edited its README (its freeze record logs both changes, at
  09:52:25 and 09:52:44 PST). The folder committed here is that later state: 25 files, with `SHA256SUMS` (25 of 25 OK) of sha256
  **`dc2ae92452f6c601de5ebfb0291c9a181a4d2334d516ccbb37cb283fcfc6fc48`**, which supersedes `d5ec254d` (check-lay's finding).
  The 19-file bytes were not kept, so `d5ec254d` cannot be re-verified. Every file the freeze names equals its hash in the lane's
  freeze record: the two forecast files, their makers
  `freeze_layout.py`, `eval_layout.py` and `features_layout.py`, `out/features_layout.json`, `out/eval_layout.json`,
  `DECLARED-layout.md` and `DECLARED-layout-addendum-1.md`. No forecast byte changed.

## The two checks

**check-lay: HOLDS** (09:54-10:09 PST; desk; `/usr/bin/python3` 3.12.3, numpy 1.26.4, `-I -B`, single-threaded).

- Its own caller re-made `forecast-e215-v31-layout.csv` byte for byte: 0 field differences; a_fresh -0.08316593007433395
  bit-equal; 0 walk-feature differences in 148 configurations. It called MM1-v3.1's Engine31 at its all-data constants and v3.1's
  masked walk itself, used the declared Phi_fresh, and fitted the constant in closed form; none of the lane's code was imported.
- All ten stated sha256 lines match; `SHA256SUMS` 25 of 25. No E215 datum was read by lay-contention.
- The term is exactly 0 at the full mask: 66 of 66 rows have factor 1.0; the 28 subset rows run 0.9942-1.0139.
- The keep rule holds on the lane's own numbers: LOLO (b) 6.2480 < 6.3195; LOLO (a) 89.3175 <= 89.7779; pooled LOEO 4.7101 <= 4.72.
  F1 beats 98 of 100 placebos of its own feature.

Its findings (four low, one note), which this note records:

1. The land's hash (above).
2. Keep condition 3, "at most 4.72% (MM1-v3.1's)", reads as a literal 4.72 or as v3.1's own 4.7228. Under the literal reading F2
   (4.7201%) fails by 0.0001; F2's LOLO (b), 6.3191%, is 0.129 points above the lowest kept form, so F1 wins under both readings.
3. Addendum 1's class-indicator test proves nothing under LOLO: an indicator is 0 on every training point of the fold that holds
   its class out, so its constant is 0 and its LOLO (a) and (b) equal v3.1's exactly. It repeats condition 1.
4. Addendum 1's last sentence, read literally ("the lowest LOLO (b) among forms that pass both"), would point at F5 (6.190%), which was
   never placebo-tested. The declared tie rule (within 0.10 points, fewer constants) gives F1, and the lane's reading is the
   consistent one.
5. (note) Thin margins: F1 gains 0.071 points of LOLO (b) and 0.013 of pooled LOEO (0.0099 under the 4.72 bound). On E215 the term moves
   only the 28 subset rows, by -0.58% (a017) to +1.39% (b005, b008), so E215 can tell F1 from MM1-v3.1 only weakly.

**verify-lay: HOLDS WITH FIXES** (10:09-10:30 PST; desk; the same interpreter; numerical jobs single-threaded under a 4 GB cap).

- **Holds.** Its own code re-derived the placement model: its request generator equals the walk's chip steps in 148 of 148
  configurations (0 minion-level mismatches in 3); with pools 4 KiB aligned (the platform allocator's minimum), lines per L3 home and
  fresh lines per memory shire have max/mean **1.000** at every step of every mask, so no slice or controller is hot. Every held-out
  number is re-made to the last digit (v3.1 / F1: LOEO with no twins 4.7228 / 4.7101; LOLO (b) 6.3195 / 6.2480; LOLO (a) 89.7779 /
  89.3175; LOCO 4.1497 / 4.1475), and the frozen E215 factors follow from the declared term (to 4.0e-10; 66 of 66 full-mask rows
  exactly 1).
- **Does not hold: reading F1 as a placement or contention term.** The fixes below are readings and records; no frozen byte changes.

## Read the README with these corrections

The README is not edited. Where it says otherwise, these readings stand (verify-lay's findings, most severe first).

1. **F1 is a correction for shire count and shape, not a placement or per-controller contention term** (medium). Its held-out gain
   does not come from placement: in 1,000 permutations of Phi_fresh within (shire count, shape) groups, the placebo's LOLO (b) is at
   or below F1's in 92.4% of draws (LOEO 88.8%); F1 averaged over the layouts of each (shire count, shape) does better (LOLO (b)
   6.150, LOEO 4.677) and passes the keep rule; F1 minus its mean within a shire count has no skill (6.428, 4.727); and F1 orders
   17 of the 36 untied equal-count layout pairs, chance. G1 (the hop mean) is the only feature with a placement hint, and it beats
   85.5% of its within-shape placebos: not significant. The README's "What F1 is, read honestly" already notes that F1's sign is the
   opposite of a per-controller load.
2. **No shire-count control was declared** (medium). N1+N2 = -0.0935 (1 - n/32) + 0.1177 (1 - n/32)^2, which uses no placement
   information, passes all three keep conditions (LOLO (b) 6.066, LOEO 4.699, LOLO (a) 89.44) and would have won had it been
   declared; 32/n - 1 alone scores 6.127 and 4.702 and fails only the degenerate LOLO (a) (90.25); G1 + N1 scores 5.888 and 4.700 and
   is kept. Their E215 forecasts are in `controls-e215/` (REPORTED).
3. **The gain is within noise** (medium). A paired bootstrap (10,000 resamples) gives the change in LOLO (b) as -0.071, 95% interval
   [-0.171, +0.032] (8.2% of resamples at or above 0), and in LOEO with no twins -0.013, [-0.048, +0.024]; F1 does better at 83
   points, worse at 54, the same at 75. A placebo of the whole declared selection (the 4 features permuted jointly, all 7 declared
   forms and the keep rule re-run, 1,000 times) gives p = 0.050, and keeps no form in 857 of the 1,000. The lane's 98 of 100 tests
   the winner alone.
4. **F1 holds only under the walk's L3 conventions** (medium). It is kept only with a 24 or 32 MB L3: at 16 MB a = +0.010 (the sign
   flips); at 48 and 64 MB it fails (LOLO (b) 6.522 and 6.374, LOEO 4.895 and 4.763); with C stores not allocating in the L3,
   a = -0.037 and it fails all three conditions, although that Phi correlates with the declared one at r = 0.95. State as a
   condition of F1: the walk's strict-LRU 32 MB L3, with stores allocating.
5. **The constant depends on the card** (low). In sample: aifoundry2 card 0 -0.167 (63% of the LOLO (b) gain), aifoundry1 card 1
   -0.087 (35%), aifoundry3 card 0, E215 arm A's card, -0.017 (9%), aifoundry1 card 0 +0.008 (-7%). E213 alone, the last blind day on
   E215's two cards, gives +0.109, and F1 worsens its LOLO (b) from 5.08 to 5.19. Neither the die nor the clock share explains the
   gain at E212's subset points (|r| <= 0.2).
6. **E215 cannot test F1's placement sensitivity** (low). F1 gives one factor to every layout of a shape at an equal shire count
   (a001-a008 and b001-b004 0.999505; a009-a010 1.0); only 14 small-count rows of distinct shapes move, by -0.6% to +1.4%. G1 does
   separate those layouts.
7. **The layout's sign flips with the shire count too** (low). At gemmL1x16x4, sharing B is faster at 4 shires (on 3 cards) and
   sharing A at 8 and 16. The layout effects repeat in sign across cards and reach 16.2%; G1 orders 22 of the 37 pairs and F1 17.

## NOT RUN

- By verify-lay: the joint all-constant refits (the README's REPORTED joint G1 LOLO (b) of 5.976 was not re-derived); T7's pair
  ordering (20 and 22 of 37); the die and the clock beyond E212's subset points; a variant in which the L3 slices of shires outside
  the mask do not serve; F2's link and F4's fan-out features (taken from the lane, used only in the selection placebo).
- By check-lay: `features_layout.py` as is (187 configurations: its walk calls covered the 148 that every fit and forecast uses; the
  other 39 are full-mask walks of E215 shapes with no subset row, where the term is 0 by construction); `placebo_layout.py`,
  `joint_layout.py` and the pair-ordering and placement scripts (REPORTED, not part of the freeze). The lane's own runs (09:09-09:31)
  cannot be audited after the fact; the evidence is the scripts, the audited re-run of the landed freeze, and the lab at 8bde0182.

## The controls beside it (`controls-e215/`)

verify-lay's REPORTED desk controls for all 94 E215 rows (`v02_e215_controls.csv`, sha256 `c5bc2394...`), written at **10:22:51 PST**
before any E215 datum (no E215 card command had run; both arms were held) and posted by their sha256 as post **#1.29.1.1** at
**10:31:36 PST**. They are REPORTED: never a registered rule of E215, and E215's registration scores none of them. Their maker and
the folder's contents are in `controls-e215/README.md`.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `controls-e215/` | verify-lay's REPORTED E215 controls, their maker and its input (see its README) |
| `SHA256SUMS-note1` | the sha256 of this note and of every file under `controls-e215/` (`SHA256SUMS` is lay-contention's and lists its 25 files) |

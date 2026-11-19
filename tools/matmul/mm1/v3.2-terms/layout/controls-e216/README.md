# REPORTED layout controls for E216's points, made before any E216 datum

*Thu 19 Nov 2026, Pacific time. Made by the lane controls-e216 (round Q229), 14:08-14:16 PST, on aifoundry2, at the desk. No card was
used and no simulator was run. The constants are verify-lay's: they were fitted on committed data that existed before E215 and E216, and
nothing was refitted here. The files are **REPORTED** desk forecasts. They were made before any E216 datum: E216's card lane had not
booked the card and had made no folder. They are never a registered rule of E216. E216's registration is not changed for them (the
orchestrator's answer to the registration's question 2). The orchestrator posts their sha256 on the owner's coordination thread before
E216's first card command; that post is their freeze line, and this folder is a record of it.*

## What this is

These are the same five controls that verify-lay made for E215's points (`../controls-e215/`, post #1.29.1.1). Here they are made for
**every one of E216's 46 registered points**:

| family | points | mask |
|---|---|---|
| G (gemmLnc) | 10 | full chip |
| Gt (their cooperative twins) | 10 | full chip |
| Y (subset masks) | 16, in 8 equal-count pairs y01-y08 | 2, 4 or 8 shires |
| F | 10 | full chip |

Each point is given at the registration's three frozen clocks: 799.0 MHz, route c's registered column, and 700 and 600 MHz, the route m
columns. That makes 138 rows.

Every control has the form T = T_v31 × (1 + Σ a_i x_i) on the wall cycles an op. Every x_i is 0 at the full mask, so at the 30 full-chip
points every column equals MM1-v3.1 exactly. The factors do not depend on the clock. The controls are not clipped, as in E215's file. No
factor at E216's points lies outside [0.3, 3.0], so a clip like the frozen term's would change nothing.

| column | what | constants (verify-lay, all data, two-stage) |
|---|---|---|
| `v31_cycles_per_op_wall` | MM1-v3.1's frozen E216 forecast (`forecast-e216.json`, `MM1-v3.1` > `cycles_per_op_wall`) | - |
| `F1_frozen_cycles_per_op_wall` | E216's frozen 'v3.1 + contention' forecast (the layout term F1: x = Phi_fresh at 32 MB) | a = -0.08316593007433395 (frozen) |
| `REPORTED_N3_cycles_per_op_wall` | x = 32/n - 1 (shire count only) | a = 0.0010073748612498246 |
| `REPORTED_N1+N2_cycles_per_op_wall` | x1 = 1 - n/32, x2 = (1 - n/32)^2 (shire count only) | a1 = -0.09348958586302018, a2 = 0.11765730189141044 |
| `REPORTED_G1_cycles_per_op_wall` | x = the active shires' mean L3 latency over the 32 homes (110 + 12 × hops) over the full chip's, minus 1 | a = 0.30314251932286107 |
| `REPORTED_G1+N1_cycles_per_op_wall` | G1 and 1 - n/32 | a1 = 0.6022127706566506, a2 = -0.021675728290377668 |
| `REPORTED_fresh24_cycles_per_op_wall` | Phi_fresh with a 24 MB L3 | a = -0.0899131685491204 |

The CSV also carries each point's id, family, pair, pair role, mask, arm, format and clock. It prints cycles with `%.4f`, as E215's file
does. `controls-e216.json` holds the same numbers unrounded, together with:

- each point's features and factors;
- the constants;
- each Y pair's within-pair ln difference for every control;
- the checks below;
- the inputs' sha256.

## How it was made: the same function as E215's file

`controls_e216.py` is the caller. It is the same function as the one that made E215's file, assembled from three parts:

- **Features.** It uses `v01_map.py`'s own functions, taken from the committed copy in `../controls-e215/` and imported, not rewritten:
  - the request generator, written from rgm136's `run_gemm_large`;
  - the strict-LRU L3 over 1 KiB tiles: two passes, the second counted, at 16, 24, 32, 48 and 64 MB;
  - the shire groups;
  - the hop mean, from the mesh map.

  It assembles them for each configuration exactly as `v01_map.main` does. Only `v01_map.main`'s `loads` diagnostics are left out, and no
  control reads them. E216 needs 24 configurations: the 8 Y shapes, each at its 2 masks and at the full chip.
- **Formula.** `feat_row` and the control formula are `v02_fits.py`'s own lines from its E215 block, copied verbatim.
- **Constants.** `constants-verify-lay.json` holds verify-lay's constants as its `v02_fits.json` stores them:
  - file: sha256 `1bfec7fc123787f5590356de65125df80d6bb4366f14e0376806913fbb27d312`;
  - written: 10:22:51 PST, before any E215 or E216 datum;
  - the values are kept as exact float reprs and equal that file's fit table.

**The reproduction of E215's file**, run first and repeated with the land copy of the caller:

1. **From the committed feature input.** The caller ran on `../controls-e215/work/v01_map.json` with the committed E215 forecasts and point
   list. It re-made `v02_e215_controls.csv` **byte for byte** (sha256 `c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d`,
   the posted file). All 470 unrounded control values (94 rows × 5 controls) are **bit-equal** to verify-lay's own rows in its
   `v02_fits.json`.
2. **From features re-made here.** The caller re-made E215's 43 configurations with the same functions.
   - Every field the records carry equals the committed `v01_map.json` in **43 of 43** configurations, with 0 fields differing: n, R, C,
     steps, requested lines, distinct lines, the generator-equals-walk check, fresh lines at all five capacities, and hop mean and max.
   - The CSV made from these records is again **byte for byte** the posted file.

**Checks at E216's points** (desk):

- **The request generator.** It equals the masked walk's `chip_steps` in 24 of 24 configurations.
- **n and requested lines.** Both equal the walk's in 24 of 24.
- **Fresh lines at 32 MB.** They equal the walk's `summary` and the registration's own frozen walk features exactly (largest difference
  0.0).
- **Fresh lines at 24 MB.** They equal the walk's `summary(l3_cap_mb=24)` to within the walk's 6-decimal rounding (largest difference
  3.3e-7 lines a step).
- **Hop mean and hop max.** Both equal the frozen walk features in 24 of 24.
- **F1's own column.** The caller's F1 is the frozen constant applied to the Phi_fresh made here. At all 138 rows it equals E216's frozen
  'v3.1 + contention' cycles **bit for bit**: the largest relative difference is 0, so they agree in every digit. Their `%.4f` and `%.9g`
  prints match at 138 of 138. The Phi from the registration's frozen walk features equals `forecast-e216.json`'s `phi_fresh` at 48 of 48
  subset rows.
- **Determinism.** The land copy re-made the CSV byte for byte from a second feature run. That run's features file equals the first on
  every key; the first run also stored its own run time, which this one does not.

## What the controls say about E216's Y pairs (REPORTED, desk; no datum)

The ln of the forecast for a over b, clock-free:

| pair | role | shape | masks a, b | N3 | N1+N2 | G1 | G1+N1 | fresh24 | F1 (frozen) |
|---|---|---|---|---|---|---|---|---|---|
| y01 | largest delta | gemmL1x8x8 | 0x3, 0x10001 | 0 | 0 | -0.0051 | -0.0102 | -0.0301 | -0.0280 |
| y02 | largest delta | gemmL1x8x12 | 0x3, 0x10001 | 0 | 0 | -0.0051 | -0.0102 | -0.0151 | -0.0278 |
| y03 | largest delta | gemmL1x4x16 | 0x3, 0x10001 | 0 | 0 | -0.0051 | -0.0102 | -0.0151 | -0.0277 |
| y04 | largest delta | gemmL4x2x16 | 0xf, 0x33 | 0 | 0 | +0.0044 | +0.0088 | -0.0141 | -0.0253 |
| y05 | largest delta | gemmL2x8x16 | 0x5555, 0x11111111 | 0 | 0 | -0.0055 | -0.0110 | +0.0114 | +0.0219 |
| y06 | largest delta | gemmL4x8x16 | 0x5555, 0x11111111 | 0 | 0 | -0.0055 | -0.0110 | +0.0114 | +0.0219 |
| y07 | control | gemmL1x4x24 | 0x101, 0x10001 | 0 | 0 | +0.0094 | +0.0187 | 0 | 0 |
| y08 | control | gemmL1x8x24 | 0x101, 0x10001 | 0 | 0 | +0.0094 | +0.0187 | 0 | 0 |

- **The count-only controls.** N3 and N1+N2 give both masks of a pair one factor, so they forecast no within-pair difference. They move
  both masks together: N3 by +0.30% to +1.51%, N1+N2 by -0.39% to +1.58%.
- **fresh24.** It has F1's sign at all six largest-delta pairs, and it is 0 at the two control pairs, as F1 is.
- **G1 and G1+N1.** They have F1's sign at y01-y03 and the opposite sign at y04-y06. At the two control pairs, where F1 forecasts no
  difference, G1+N1 forecasts +0.0187 in ln (G1 +0.0094). That is above E216's pair-rule threshold of 0.0077 in ln.

These are statements about frozen forecasts, not results.

Factor ranges at the 16 subset points:

| control | lowest | highest |
|---|---|---|
| N3 | 1.0030 | 1.0151 |
| N1+N2 | 0.9961 | 1.0158 |
| G1 | 1.0010 | 1.0221 |
| G1+N1 | 0.9857 | 1.0236 |
| fresh24 | 0.9784 | 1.0112 |

## How to use it

After E216's data, score these columns beside F1 and MM1-v3.1 as REPORTED numbers:

- **Which rows.** Every point. The Y family's pairs are where the controls differ.
- **Which clock.** A route c run is scored against the 799.0 MHz rows; a route m run against the rows at the frozen clock nearest its
  view clock, as E216's registration reads its own columns.

None of these columns enters any registered rule of E216.

## Not made

- **The layout-blind F1.** This is F1 with Phi_fresh averaged over the layouts of each (n, shape) in the fit set. verify-lay scored it,
  and the orchestrator's answer names it beside the four count and hop controls. It is not a column of E215's file. Its averaging group
  is undefined at E216's shapes, which never ran on the card, so making it would need a choice verify-lay did not make. Not made.
- **The constants themselves.** They are not re-derived here from the committed `v02_fits.py`. When land-terms re-ran that script on a
  lab clone of main 21ba4b45 (`../controls-e215/README.md`), it re-made E215's file byte for byte. That is the record of their origin.

## Re-running it

E216's registration files must first be at `tools/claims-v3/e216/` (that is, after E216's registration lands). The files read here were
the registration lane's own, with these sha256:

| file | sha256 |
|---|---|
| `points-e216.csv` | `a83b5e1cc4915b0084cb9d22788c0d33e965f8bece292ef1bfff5174f0586c57` |
| `forecast-e216.json` | `92c9444a7a0d72a0198fd3581a72c2a05b00969d08b024d09c90eab4f3dda5dc` |
| `desk/candidates-e216.json` | `846a373bf6a5fcdf265a94e703a7d9b9e4ae245ef96393531338fe8f145c0e18` |
| `terms/layout/out/features_layout.json` | `1de94e5611c0912eb4bfb4294df9fabeb07078f4c31344e29e15c5200f1b0183` |

Run from this folder, with OMP_NUM_THREADS=1 and the like:

    /usr/bin/python3 -I -B controls_e216.py e215 committed   # work/e215-committed.csv = ../controls-e215/v02_e215_controls.csv
    /usr/bin/python3 -I -B controls_e216.py features e215    # E215's 43 configurations, about 20 s
    /usr/bin/python3 -I -B controls_e216.py e215 remade      # work/e215-remade.csv, the same bytes
    /usr/bin/python3 -I -B controls_e216.py features e216    # work/features-e216.json, the same bytes, about 2.5 minutes
    /usr/bin/python3 -I -B controls_e216.py e216             # work/controls-e216.csv and .json = this folder's

- **Environment.** `$ET_LAB` names the lab's top if the folder is elsewhere, and `$E216_REG` names E216's registration folder.
- **Inputs.** The caller reads:
  - `../controls-e215/` (`v01_map.py`, `work/v01_map.json`, `v02_e215_controls.csv`);
  - `../forecast-e215-v31-layout.csv`;
  - `tools/claims-v3/e215/points-e215.csv`;
  - the masked walk (`tools/matmul/mm1/v3.1/walk/walk/walk_v31.py`);
  - the mesh map in `workloads/nocbench/analyze.py`;
  - E216's registration files above.
- **Interpreter.** `/usr/bin/python3` 3.12.3 with numpy 1.26.4, single-threaded.

## Files

| file | what |
|---|---|
| `controls-e216.csv` | the controls, 138 rows |
| `controls-e216.json` | the same unrounded, with features, factors, pairs, checks and inputs |
| `controls_e216.py` | the caller |
| `constants-verify-lay.json` | verify-lay's constants |
| `work/features-e216.json` | the 24 configurations' feature records, with the walk cross-checks |
| `SHA256SUMS` | the sha256 of every file above |

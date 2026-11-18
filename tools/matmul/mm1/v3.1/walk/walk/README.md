# MM1-v3.1's masked walk (Q217, lane v31-trace)

`walk_v31.py` is the subset walk of the lab's two matmul kernels at any shire mask, written from the kernels' sources with no fitted
constant. Desk code: standard library only, `/usr/bin/python3` 3.12.3. The traces under `../traces/` check it against sys_emu. The
registered trace check (MM1-v3.1's declaration, section 4) reads **PASS** at both masks: see `../README.md`.

*This file is v31-trace's README with the changes of round Q221 (lane t7-0xf): the log paths point at `../logs/`, the post hoc
tallies are given per pair, and the section "What the walk does not model" names the walk-trace differences the verifier found. The
old and new sha256 are in `../SCRUB.json`. Lane land-walk-v31 then applied the land verifier's (verify-t7-0xf) two wording fixes here:
the provenance of `walk_predictions_final.json` and the level model named in difference 2.*

## What it computes

| question | function | from |
|---|---|---|
| which minions a mask enables | `enabled(mask)` | `entry_point` in both kernels; the host's `participants()` and `Session::launch` (the runtime gets the same mask) |
| each minion's tile order | `minion_events(kernel, MB, NB, KB, shire, minion)` | `run_gemm_large` (rgm136) and `run_gemm_large_nm` (rgm211) |
| what each op fetches and stores | the same events: A and B TensorLoads (16 lines, stride 64, scratchpad line, coop group), TensorStores, TensorFMAs | the same functions and their helpers (`t_load`, `t_load_coop`, `t_store`, `fma_word`) |
| the shire's reads after cooperation | `shire_step_requests` | the coop groups (8 minions share A, 4 share B) |
| which active shires read each tile | `chip_steps`, `summary(...)["chip_step"]` | the partition (row group `s >> 2`, column group `s & 3`) |
| from which level, in which order | `minion_levels`, `l3_distances`, `l2_shire_tiles`, `summary(...)["l3_strict"]` | exact LRU stack distances: the lab's desk L2 model per shire (2,048 sets x 4 ways), the chip's L3 as one LRU over 1 KiB tiles of the active shires in lock step, strict at a capacity (32 MB default) |

Kernels: `rgm136.gemmL` (cooperative, mb outer), `rgm136.gemmLnc` (its non-cooperative branch), `rgm211.gemmLn` (cooperative,
nb outer), `rgm211.gemmL` (rgm211's own copy of the mb-outer loop).

A minion's work does not depend on the mask: every minion keeps the full chip's partition. A subset therefore computes the masked
shires' share of every C block, and each minion still does 64 MB NB KB TensorFMAs. What the mask changes is which tiles the chip reads
and how many shires share each one. At mask 0xf an A tile is read by 4 shires and a B tile by 1. At mask 0x1111 an A tile is read by 1
shire and a B tile by 4.

The shire stream (`shire_step_requests`) counts one read per cooperative group: 4 A and 8 B tile reads, 192 lines a shire-op. The
traces confirm the **distinct tiles per shire-step**, which follow from the per-minion sequences. They cannot confirm the one read per
group: sys_emu makes every member read all 16 lines itself, 64 tile reads and 1,024 lines a shire-op for gemmL and gemmLn (5.33x the
walk's count; equal for gemmLnc). The one read per group is the hardware's rule, taken from the code's `tensor_coop` values, which the
traces do show.

The levels are a model. No simulator has caches with capacity, so the traces cannot check them; see `../traces/README.md`.

## What the walk does not model (walk-trace differences, named by the trace verifier)

Simulated (sys_emu), not the card; none of them touches a check criterion.

1. **The firmware tensor operations before the kernel.** On every working hart 0, before the kernel's first instruction, the S-mode
   worker firmware issues one TensorIMA8A32, three TensorLoads and a second TensorIMA8A32. Each of the three loads reads one 64-B line
   16 times with stride 0: 48 line reads of one line a hart a launch, 0.146% of a working hart's lines at 1x1x16 and 0.018% at
   2x4x16. Hart 1s and harts outside the mask issue none. The walk lists the kernel's U-mode operations only.
2. **The C-store placement.** The walk's level model (`chip_steps`, which `footprint_tiles` and `l3_distances` read, and through them
   the summaries' footprint and L3 numbers) stores a row half's C tile after that half's last op. Each traced minion issues that store
   after the A and B loads of the next half's first op, which is where `minion_events` (the per-minion sequence the check compares)
   already puts it: a one-step shift in the level model, once per row half. The final tile follows the last op, as in the walk. At
   32 MB the shift changes none of the walk's LRU numbers at the traced shapes.
3. **The "Instruction killed and will be restarted" lines.** sys_emu prints this agent line (not a tensor operation, not an
   instruction): one on every logged hart 1 and on all but four logged hart 0s of the enabled shires at 1x1x16 (minion 29 of the first
   three enabled shires and minion 0 of the fourth have none), none on any logged hart outside the mask; and on unselected harts, 5 in
   the master shire (17 lines a run) and, at 2x4x16, 93 untraced hart 0s of the enabled shires (one each). The walk has no such event.

Also not modelled: time, bandwidth and contention (sys_emu has none, and its lock step is not the card's), and which level serves a
line (above).

## Use

```
python3 -I -B walk_v31.py summary rgm136.gemmL 2x4x16 0xf [--l2] [--l3-cap-mb 32]
python3 -I -B walk_v31.py minion  rgm211.gemmLn 2x4x16 0x1111 4 9
python3 -I -B walk_v31.py levels  rgm136.gemmL 2x4x16 0xf 0 9
```

## Tests (`test_walk_v31.py`, desk)

T1 enabled minions; T2 per-minion counts; T3 the two walks (identical at MB = 1 or NB = 1, different in order at MB, NB >= 2);
T4 gemmLnc = gemmL without cooperation; T5 mm-timing's counted simulator run (64/64/64/2 per hart, 32 harts; its record is
`testdata/counts-log-c-gemmL1x1x1-fp32.json`, a byte copy); T6 kit-e211's committed simulator records (ops a minion, walk tags);
T7 the shire stream = E136's `reuse_e136.shire_ops`; T8 the masked L3 = E206's `l3_model_masked` (126 shape, mask and capacity cases)
and, at the full mask, E211's `map_e211.stack_distances` for both walks; T9 footprint = MM1-v1's masked closed form; T10 the sharing;
T11 per-minion levels = the summary's shares. The tests read the lab's files from the checkout this folder sits in (or from the
environment variable `ET_LAB`). Results: `../logs/s01_walk_tests.log` (quick), `../logs/s03_walk_tests_full.log`,
`../logs/s05_walk_tests_full.log`, and Q221's run of the landed copy, `../t7-0xf/work/walk_tests_land.log`: **WALK TESTS 11 of 11
PASS**.

## Frozen before any trace

`walk_predictions.json` holds the walk's event counts and sha256 for every hart each planned run logs, and the walk's summaries
for those runs (sha256 `10f2f3da0dd543a088830edb67584713e5b66b986faae1d1c0327d041bc2bf57`, made 05:11:43 PST Wed 18 Nov 2026,
before any trace; landed byte for byte). `walk_predictions_final.json` is the same file made again (05:20:51 PST) with the final
`walk_v31.py` (sha256 `87736da2...`, last edited at 05:18:44 PST), which by v31-trace's account added `minion_levels`, `l2_shire_tiles`
and the `levels` command. The walk that made the frozen file (sha256 `b72f2ac4...`, named inside it) is not kept, so whether that edit
left every earlier function unchanged cannot be checked. What can be checked holds: the landed walk re-makes the frozen file exactly
(every run, all 1,488 hart entries with the 448 working hart 0s' event counts and sha256 among them, and the walk's summaries; only
`walk_sha256` and `made_pst` differ). `../logs/s05_run.out` records that the two files match; Q221 made them again with the landed
code and every run and hart was equal again (`../t7-0xf/work/predict-compare.json`); the land verifier's own model, written from the
kernels' C sources, gives the same 448 sequences.

## Post hoc table (`layout_table_v31.py` -> `layout_table_v31.json`)

This table reads the walk's numbers at every equal-shire-count layout pair E212 ran (14 pairs), beside E212's measured ratios. It is
**post hoc**: E212's data existed before the table, and nothing in it was fitted. Per pair (the sessions of a pair agree in all 14;
ties within 1% left out), the rule "the layout with fewer fresh lines runs faster" is right in **3 of 8** pairs (strict LRU, lines a
shire-op), **3 of 10** (strict, chip lines a step), **3 of 11** and **3 of 11** (MM1-v3's frozen retention, shire and chip), and "more
shared requests is slower" in **3 of 8**. The JSON's `sign_agreement` counts (pair, session) calls over 26 measurements (7 of 14,
7 of 18, 7 of 21, 7 of 21, 5 of 16). Either way the walk's fresh-line count does not order E212's layouts: the layout's time effect
needs a placement-aware term the walk does not have (see `../README.md`).

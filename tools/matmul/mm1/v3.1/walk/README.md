# MM1-v3.1's masked walk (T7) and its registered trace check: PASS at both masks

*Wed 18 Nov 2026, Pacific time. Round Q217 (lanes v31-trace and verify-v31trace) and round Q221 (lane t7-0xf; the land verifier
verify-t7-0xf's wording fixes applied by lane land-walk-v31, listed at the end). No card was used: every
trace here is **simulated** (sys_emu on aifoundry3, not the card). The walk is **desk** code with no fitted constant; its predictions
were frozen at 05:11:43 PST, before any trace. The rule is **registered** in MM1-v3.1's declaration (`../DECLARED-v31.md` section 4,
landed 7375bc9c). The layout table is **post hoc**. Interpreter: `/usr/bin/python3` 3.12.3, `-I -B`; numpy 1.26.4 only where the walk
tests import the lab's desk maps.*

## The verdict

**The registered T7 trace check reads PASS.** Criteria (a), (b) and (c) hold at both masks of E212's layout pair, 0xf (compact) and
0x1111 (spread), over every traced run. The trace verifier (verify-v31trace) held with fixes; its fixes are applied here and the check
was run again on the files in this folder. T7's desk precondition (`../t7_v31.py --check`) passes.

| mask | runs | (a)'s minimum log set | (a) | (b) | (c) |
|---|---|---|---|---|---|
| 0xf | t1, t3, t5, t7, u2 | met by u2: all 64 harts of shires 0-3 and of all 28 shires outside the mask | holds | 352 of 352 traced working minions, 0 mismatches; 900 traced off-mask minions, empty as the walk's | 352 of 352 working; 900 off-mask, 0 requests as the walk's |
| 0x1111 | t2, t4, t6, t8, u1 | met by u1: all 64 harts of shires 0, 4, 8, 12 and of all 28 shires outside the mask | holds | 352 of 352 working, 0 mismatches; 900 off-mask, empty as the walk's | 352 of 352 working; 900 off-mask, 0 requests as the walk's |

What (a) means at each mask, counted over the logged harts of all five runs: every logged hart 0 of an enabled shire issued tensor
loads (352 of 352); no logged hart 1 issued one (640 logged); no logged hart of a shire outside the mask retired a user-mode
instruction (1,800 logged, 0 with one). For (b) and (c), every traced working minion's whole tensor-operation sequence has the frozen
file's sha256 (704 of 704 over both masks), so its ordered load requests and its counts by operand equal the walk's. Section 4 calls a
minion traced when its hart 0 is logged, so each mask also has **900 traced off-mask minions** (896 in u1 or u2, and shire 31's minion 0
in each of the other four runs): all 900 are empty (no tensor operation, no user-mode instruction), as the walk's, which launches no
shire outside the mask. (b) and (c) therefore hold over 1,252 traced minions a mask: 352 working and 900 off-mask. (b)'s traced window
is read as the kernel's user-mode tensor operations, the ones each summary lists: the three S-mode TensorLoads the firmware issues on
every working hart 0 before the kernel (counted apart in each summary; see "What the walk does not model") read one line at
0x8000c08880 with stride 0 on u2's raw lines (harts 0 and 254), outside every operand pool, so they are not operand requests.

Before u2 (09:44:20-09:50:07 PST), 0xf had no fully logged shire outside the mask, so (a) was undecided there and the check read
NOT RUN (verify-v31trace's finding). u2 is the one run that closed it.

## What the walk computes

`walk/walk_v31.py`: for rgm136's gemmL, its non-cooperative branch gemmLnc, and rgm211's gemmLn at any shire mask, which minions work,
each minion's tile order, every fetch and store with its cooperation group, which active shires share each tile, and a level model from
exact LRU stack distances. `walk/README.md` has the table, the tests and the limits. T7 (`../t7_v31.py`) is the declaration's frozen code
form of the same stream; it matched this walk at 8 of 8 cases when it was frozen.

## What was traced (simulated; aifoundry3; nothing kept of the raw logs but per-hart summaries and a few excerpts)

| run | lane | kernel, shape | mask | harts logged | aifoundry3 (PST) | streamed | traced working harts = frozen | check |
|---|---|---|---|---|---|---|---|---|
| t1 | v31-trace | rgm136 gemmL 2x4x16 | 0xf | 162 | 07:27:50-07:41:55 | 37.9 GB | 32 of 32 | EXACT |
| t2 | v31-trace | rgm136 gemmL 2x4x16 | 0x1111 | 162 | 07:42:44-07:56:49 | 38.0 GB | 32 of 32 | EXACT |
| t3 | v31-trace | rgm211 gemmLn 2x4x16 | 0xf | 162 | 07:57:02-08:09:52 | 36.8 GB | 32 of 32 | EXACT |
| t4 | v31-trace | rgm211 gemmLn 2x4x16 | 0x1111 | 162 | 08:09:52-08:22:49 | 36.9 GB | 32 of 32 | EXACT |
| t5 | v31-trace | rgm136 gemmLnc 2x4x16 | 0xf | 162 | 08:22:49-08:36:11 | 37.3 GB | 32 of 32 | EXACT |
| t6 | v31-trace | rgm136 gemmLnc 2x4x16 | 0x1111 | 162 | 08:36:11-08:49:37 | 37.4 GB | 32 of 32 | EXACT |
| t7 | v31-trace | rgm136 gemmL 1x1x16 | 0xf | 258 | 08:49:37-08:54:14 | 9.9 GB | 128 of 128 | EXACT |
| t8 | v31-trace | rgm136 gemmL 1x1x16 | 0x1111 | 258 | 08:54:15-08:58:52 | 9.9 GB | 128 of 128 | EXACT |
| u1 | verify-v31trace | rgm136 gemmL 1x1x16 | 0x1111 | 2,048 | 09:24:19-09:30:05 | 10.04 GB | 128 of 128 | EXACT |
| u2 | t7-0xf | rgm136 gemmL 1x1x16 | 0xf | 2,048 | 09:44:20-09:50:07 | 10.00 GB | 128 of 128 | EXACT |

In all: 704 traced working minions, 6,295,552 tensor operations, 67,108,864 lines read and 262,144 written, each line at its
address plus i times the stride. The hosts' own records agree (ops a minion, minions, the C check exact 16,384 of 16,384 words; the
tiles are fp32 zeros, so that C check cannot show where C was stored: the store addresses in each traced minion's sequence do).
u1 and u2 log every hart (all 64) of all 32 compute shires; t1-t6 log hart 0 of eight minions in each enabled shire (every
neighbourhood and position, so every tile the shire reads) and every hart 1; t7 and t8 log all 64 harts of each enabled shire.
Every run: the host inside bubblewrap with no `/dev/et*` node, `prlimit --as` 4 GB, nice 19, a plain `timeout` (never `-k`), one run at
a time, only while no lane booked aifoundry3.

**What was logged, said exactly.** The statement "every off-mask hart ran no user-mode instruction" rests on the harts that were logged:
v31-trace's eight runs logged **16 logged off-mask harts** in all (harts 1984 and 1985 of shire 31 in each run); u1 and u2 log all 1,792
harts outside their masks. All 3,600 logged off-mask harts ran firmware only (146-246 M-mode and 164-1,095 S-mode instructions each),
no user-mode instruction (the runner's own counters agree for u1 and u2, and a raw-line parse of shires 4 and 31 in u2 and 1 and 31 in
u1 agrees). The 1,280 logged hart 1s entered and returned: 57 user-mode instructions each (55 with rgm211's ELF), no tensor operation.

**What "the shires' streams equal the walk's" means.** The traces confirm the **distinct tiles per shire-step** at every step (8,192
steps at 2x4x16, 1,024 at 1x1x16) and the chip's sharing of each tile among the active shires. That follows from the per-minion
sequences. It is not the walk's request count after cooperation: the walk counts one read per cooperative group (4 A and 8 B tiles,
192 lines a shire-op), while sys_emu makes every member read all 16 lines itself (64 tile reads, 1,024 lines a shire-op for gemmL and
gemmLn: 5.33x; equal for gemmLnc). The single read per group is the hardware's rule, read from the code's `tensor_coop` values, which the
traces show (`traces/README.md`, "What sys_emu can show, and what it cannot").

## What the walk does not model

The trace verifier named three walk-trace differences (each listed with its size in `walk/README.md`): the **firmware tensor
operations** before the kernel (two TensorIMA8A32 and three TensorLoads on each working hart 0: 48 reads of one line a launch, 0.146%
of a hart's lines at 1x1x16); the **C-store placement** (each C store comes one op later than the walk's level model, `chip_steps`,
puts it, once per row half; the per-minion sequence `minion_events`, which the check compares, already puts it where the traces do; no
effect at 32 MB on these shapes); and the **"Instruction killed and will be restarted"** lines (one on almost every logged hart of an
enabled shire, none outside the mask; not an instruction). The walk's levels (L2, L3, DRAM) are a model that no simulator here can test,
and the walk has no time, bandwidth or contention.

## Post hoc: the walk beside E212's measured layouts

Labelled post hoc: E212's layout pairs were measured before this table, and nothing was fitted. At 14 equal-shire-count pairs (1x16x4
and 1x1x16 at n 4, 8, 16, 24; 2x4x16 and 4x8x4 at n 4, 8, 16), does the layout the walk gives fewer fresh lines run faster? Counted per
pair (the sessions of a pair agree in all 14; ties within 1% left out):

| rule | pairs right |
|---|---|
| fewer fresh lines a shire-op, strict LRU at 32 MB | 3 of 8 |
| fewer chip fresh lines a step, strict | 3 of 10 |
| fewer fresh lines a shire-op, MM1-v3's frozen retention | 3 of 11 |
| fewer chip fresh lines a step, MM1-v3's retention | 3 of 11 |
| more shared requests a shire-op is slower | 3 of 8 |

Counted as (pair, session) calls over 26 measurements, as `walk/layout_table_v31.json` does: 7 of 14, 7 of 18, 7 of 21, 7 of 21 and
5 of 16. The walk is exact in what it predicts, but its fresh-line count does not order E212's layouts: the layout's time effect needs a
placement-aware contention term (L3 slices and memory controllers by address, which operand is shared), declared before any fit and tested
on a registered layout ladder.

## What the PASS decides

By the declaration's rule (section 4, step 1), MM1-v3.1's fit now fits T7, T7L and v3's n/32 form on all the data and on every LOEO and
LOLO fold; **T7 enters v3.1** only if its LOLO wall rms over all subset points is lower than both others' and its pooled LOEO wall rms is
within 0.05 points of the best of the three. That fit has not run: nothing here decides whether T7 enters.

## The scrub

Every home path and login was removed from the files in this folder: the round's work folder is written `<W>`, the lab clone `<LAB>`,
the home directory `~`, and the login in `ls -l` output `<login>`. The rewritten files are the 10 runs' `summary.json.gz` and
`out.json`, u1's and u2's `mine.json.gz`, `walk_predictions.json.sha256`, the run scripts and the logs; two Python files got a code change,
not a text replacement: `walk/test_walk_v31.py` (the lab from `ET_LAB` or this folder's place in the lab; mm-timing's counted run from
`walk/testdata/`) and `walk/layout_table_v31.py` (the lab the same way). `SCRUB.json` lists the old and new sha256 of every rewritten file
beside the frozen one: **`walk/walk_predictions.json` is landed byte for byte (sha256 `10f2f3da0dd543a088830edb67584713e5b66b986faae1d1c0327d041bc2bf57`)**. The checks were run again on the scrubbed summaries: equal to the checks of the
originals in every key, 10 of 10.

## Files

| path | what |
|---|---|
| `T7-TRACE-CHECK.json` | the verdict, criteria (a)-(c) per mask and per run, the precondition, the re-run, verify-v31trace's fixes, verify-t7-0xf's fixes |
| `SCRUB.json` | every rewritten file's old and new sha256; the frozen file's; the land's wording fixes (`land_walk_v31`) |
| `walk/` | the walk, its tests, the frozen predictions and their `.sha256`, the re-made predictions, the post hoc layout table, the levels table, `testdata/` |
| `traces/` | the summarizer and runner (`trace_run.py`), THE CHECK (`check_v31.py`), the desk test log maker, the run scripts, `plan.json`, `check_summary.*` (v31-trace's, with the original summaries' sha256) |
| `traces/runs/t1-...t8-.../` | v31-trace's runs: `summary.json.gz`, `check.json`, `traced_numbers.json`, `out.json`, `RUN.txt`, `sandbox-check.txt`, `err.excerpt.txt` |
| `traces/runs/u1/`, `traces/runs/u2/` | verify-v31trace's run and this lane's: summary, the runner's own counters (`mine.json.gz`), `check_v31.json`, the independent re-derivation (`v04_*.json`), the raw-line parse (`v06_*.json`), `out.json`, `RUN.txt`, `sandbox-check.txt`, `err.log` |
| `scripts/`, `logs/` | v31-trace's desk steps and logs |
| `verify-v31trace/` | its runner (`vt_run.py`), run scripts, independent checks (`v04_independent.py`, `v06_rawparse.py`, ...), outputs and logs |
| `t7-0xf/` | this lane's run scripts (u1's form at 0xf), `c02_criteria.py` (criteria (a)-(c) by the registered words), the land build and scrub, the re-check scripts, their outputs (`work/`) and logs |
| `SHA256SUMS` | every file here |

## Re-run (from this folder in a checkout of the lab)

```
python3 -I -B walk/test_walk_v31.py                          # WALK TESTS 11 of 11 PASS
python3 -I -B traces/check_v31.py --summary traces/runs/u2/summary.json.gz --kernel rgm136.gemmL --shape 1x1x16 --mask 0xf --out check-u2.json
python3 -I -B ../t7_v31.py --check                           # T7's desk precondition
sha256sum -c SHA256SUMS
```

## The land's wording fixes (verify-t7-0xf)

The land verifier (verify-t7-0xf) re-derived the PASS with its own code, written from the kernels' C sources, and held **with fixes**,
all of them wording: no number, verdict or data file changed. Lane land-walk-v31 applied them to this folder before the commit:

1. Both traced-minion counts are given (low): 352 traced working minions and 900 traced off-mask minions a mask, empty as the walk's
   (above, and in `T7-TRACE-CHECK.json`), counted again by land-walk-v31's own code from the summaries: 352 and 900 at each mask, all
   900 empty, none enabled by the walk.
2. `walk/README.md` no longer says that the final walk changed no earlier function (low): the walk that made the frozen file (sha256
   `b72f2ac4...`, named inside it) is not kept, so that cannot be checked. What is checked holds: the landed walk re-makes the frozen
   file exactly (all 1,488 hart entries, the 448 working hart 0s' sequences among them, and the walk's summaries; only `walk_sha256`
   and `made_pst` differ).
3. The one-op-late C store is the level model's (`chip_steps`), not the per-minion sequence's (nit): here and in `walk/README.md`.
4. (b)'s traced window is stated as the kernel's user-mode tensor operations (above, and in `T7-TRACE-CHECK.json`'s `why`).
5. The hosts' C check is not cited for addressing: the tiles are zeros (above).
6. `SCRUB.json` says what it lists (the 90 rewritten files and the frozen one; the 160 unchanged copies are counted, not listed) and
   records these edits with each file's sha256 before and after; `SHA256SUMS` was made again.

## NOT RUN

The card (none was used); any fit (whether T7 enters v3.1 is decided by v3.1's fit); a level check (no simulator here has caches with
capacity); traces at other layout pairs (n 8, 16, 24) or other shapes; int8 and fp16 traces (the walk's addresses do not depend on the
format); every hart of gemmLn's and gemmLnc's enabled shires (not required by the registered words, which judge the log set per mask).

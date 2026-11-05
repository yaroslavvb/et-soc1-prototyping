# Dated note A1 beside DESIGN.md (Thu 5 Nov 2026; Q142(x)) - pool 8 copied unchanged, its blind8.json written from MANIFEST by a committed rule with a pool-7 round trip, what the frozen predictor must read before any count, the bench driver's rule, and the designer's six recorded faults

*Written on Thu 5 Nov 2026 from about 01:35 PST on the Intel, desk only (no card, no device command, no lab box, no post in the
lab's channel, no Modal, no archive), and committed at the time git records. **Committed before `blind8.json`, any bench count of a
pool-8 tile or any pool-8 prediction exists.** `DESIGN.md` and `make_blind8.py` (`153b720f`) stay as committed. The pool's 90 files
are the designer's, copied unchanged into this directory: every file's sha256 equals the designer's scratch copy, the pool's own
`SHA256SUMS` passes (89 lines), and `make_blind8.py check --out tools/claims-v3/kinds/blind8` reads "checked 64 tiles: 0 problems"
(01:33:35 PST, through the round's local slot, `python3.10 -I`). **No tile, label, class, priority, re-run pick or MANIFEST line
changes.** This note answers the Q142(r)/(p)/(d) critic's fault 1 (the predictor cannot read the pool as delivered) and its fault 4
(the six minor faults of Q142(d)'s verifier, which no fix pass recorded), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6.*

## A1-1. blind8.json, and the converter's rule (the critic's fault 1)

**Why a converter.** Q142(p)'s frozen predictor (`predict_pool8.py`, `9d81d254`, run through `predict_pool8_a2.py`, `97765c0a`) reads
`blind8.json`, else the one `*.json` in the pool whose `tiles` list holds dicts with a `file` field. The pool as delivered has no
`blind8.json` (pool 7's JSON form, which the designer was barred from reading), so the predictor takes `provenance-blind8.json`
(fields `label`, `fmt`, `cls`, `role`, `prio`), and both `plan` and `predict` stop with `KeyError: 'name'` (exit 1).

**The rule, exactly as the critic gives it.** Each MANIFEST line, `<sha256> <file> <label> <format> case=<c> p<k> <role> <flag>`, gives
one tile of `blind8.json`, in MANIFEST's order:

| field | value |
|---|---|
| `name` | the label |
| `file` | the file |
| `type` | the format |
| `case` | c (the letter after `case=`) |
| `priority` | the integer k (never the string `p1`) |
| `anchor` | true if the role is `anchor` or `check` |
| `role` | the role |
| `real` | true if c is `R` |
| `sha256` | `whole`: the file's sha256, which must equal the line's; `a`: of bytes 0-1023; `b`: of bytes 1024-2047 |

Nothing else is written per tile: the flag stays in MANIFEST, and the predictor finds re-runs from the bytes. The code is
[`blind8_json.py`](blind8_json.py) `convert`, committed with this note. It refuses, writing nothing, on a line without eight fields, a
format other than fp32/fp16/int8, a priority other than p<integer>, a role other than anchor, check, kind or rerun, a repeated label, or a
tile that is not 2,048 bytes or whose bytes differ from its line. It writes no time stamp, so a re-run writes the same bytes, and it
never overwrites an existing file.

**Two careless forms that fail with no refusal** (the critic's probe): priority written as `p1` empties N1 (`make_sets` keeps priority
in (1, None)), so every 600 MHz rule would read NOT SCORED; and `anchor` set only for role `anchor` drops the three check anchors, so
KA is empty and P8-KA NOT SCORED. The rule above avoids both, and A1-3 tests for both.

## A1-2. Its round trip on pool 7

`blind8_json.py roundtrip` ([`roundtrip-blind7.json`](roundtrip-blind7.json), committed with this note) converts pool 7's MANIFEST by
the same function and compares it with the committed `blind7.json`:
- **61 of 61 tiles** give blind7.json's `file`, `type`, `priority`, `anchor`, `real` and `sha256` `whole`, `a` and `b`; 0 mismatches,
  the same order.
- The predictor's own `roles()` and `make_sets()` read the same roles and the same sets from both manifests. On pool 7 every tile is its
  own earlier twin, so both give RR 28 (its float kinds) and an empty N1.
- Not compared: `case` (blind7.json writes a description, MANIFEST a letter) and `role` (blind7.json has none). The predictor reads
  neither for pool 7's anchors.

## A1-3. What the frozen predictor must read from pool 8 before any count is used

After `blind8.json` is written, and before any count:
- `predict_pool8_a2.py plan tools/claims-v3/kinds/blind8`, given no counts, exits 0;
- `blind8_json.py sets tools/claims-v3/kinds/blind8` calls the predictor's own `manifest()`, `roles()`, `earlier_tiles()`, `tile_bytes()`
  and `make_sets()`, with the four fields `predict()` passes to `make_sets()` (type, priority, anchor role, re-run of). It must read:

| what | must read |
|---|---|
| the manifest picked | `blind8.json` |
| the anchors' roles | zeros 3 (from the bytes), scale 6 (no role field reads check), check 3 (the role field) |
| N1 | 31: fp32 11, fp16 8, int8 12 |
| F1, I1 | 19, 12 |
| RR | 12 |
| KA | 2 (the fp32 and fp16 check anchors; int8's enters nothing) |

Reported beside: RR's int8 part 0, pool 8's float scale anchors 4, the zeros anchors 3, and the 9 tiles of other priorities.
**If any reading differs, nothing is counted** and the lane stops with the reading.

**The forecast of LG's block, stated before the intervals are computed** (the critic's, from A2-4's function, noise, draws and seed
string): aifoundry3, E153's 8 re-runs (D_ref 1.36-21.88 W) and E163's 4 (9.85-24.81 W), df (2, 8), F point 4.459, GAIN 76.4% at a 0.6%
gain, LEVEL 90.0% at 0.11 W, the null NOT SEPARATED 93.6%; card 1, E157 and E164, 73.0% and 89.7%. If the committed block differs,
something in the inputs changed: the difference is explained, never tuned.

## A1-4. The bench driver's rule (written next; committed with the counts)

`docs/reports/data/2026-11-05-q142x-pool8-freeze/bench/bench_pool8.py`, from M10's `bench_m10.py`:
- **Kept:** the build check (the four unbuilt inputs as Q140(m)'s `bench-check/bench-sha256.txt`; the three binaries as that file, or as
  Q141(t2)'s build record for the mini's build, made with `-fno-dfg`); the points (RECOUNT-RULE.md section 1, the midpoints of N equal
  parts of a 0.5 s launch at 600 MHz, 546 cycles an op); `rtl-sim/fma_toggle_v2/run_kinds.py` unchanged, at nice +10, with at most 4
  jobs; the run record (wall time, jobs, points, the machine's architecture, never its name; the driver's sha256).
- **Changed:** (i) the tiles come from `blind8.json`, each tile's bytes checked against its sha256; (ii) **no case-S restriction**: term b
  covers every fp32 and fp16 tile by e(N) (registration section 2); (iii) **int8 is counted only at its own three points**,
  run_kinds.py's launch points at 318 cycles an op (`--points launch`, as pool 7's counts were), never at the float points (the
  registration's note A1-3); (iv) **C at every point:** a point whose `check_mismatch` is not 0 makes the run exit non-zero after its
  record is written, and that chunk is not used.
- **The steps:** the predictor's `plan` names each float tile's missing points; count exactly those (all of N = 9 for a new tile, the
  rest of N = 9 for a re-run or floor that holds committed points), and int8's three points for all 19 int8 tiles, the int8 floor
  included (the predictor reads an int8 row only from a given counts file); then `plan` again, and count again, until every float tile
  reaches its N (e(N) <= 0.10 W at M9's float prices, or N = 243). Committed points are reused by bytes, by the predictor's own rule.
- **Where:** the counts run on the mini, one chunk at a time with 4 jobs. First, one new pool-8 float point is counted on both the
  mini's build and the Intel's (through the round's local slot) and compared field by field with Q141(t2)'s `compare_points.py`, and
  one int8 point counted on the mini is compared with its committed count.
- **Then:** `predict_pool8_a2.py predict` for aifoundry3, aifoundry1c1, aifoundry2 and aifoundry1c0 (never `predict_pool8.py`; any
  non-zero exit means no predictions), and `predict_pool8_a2.py intervals` on the four files.

## A1-5. The designer's six recorded faults (Q142(d)'s verifier; no fix pass ran), recorded with the pool, no tile changed

Each fact below is read from committed files and git by [`a1_checks.py`](a1_checks.py) → [`a1-checks.txt`](a1-checks.txt), committed
with this note.

1. **The 23:19 exposure.** At about 23:19 PST Wed 4 Nov a `git log` the designer ran to copy the commit-message form printed the start
   of each paragraph of the two latest lab commits (Q142(r)'s `f3ebb62d` and Q142(p)'s `3e97f583`). Q142(r)'s subject quotes one
   aggregate held-out float error figure of M10; no figure per kind or class. **Before it, at 23:18:39 PST, the generator had written
   its own sha256, `fee9a4f01d32795e526c0b8ec06657b04024e8413351302080422643a76d14ea`, into the TEST pool's provenance** (blob
   `7a443e6d`, not yet committed), and the committed `make_blind8.py` (`153b720f`) is that exact file. The pool was made only after
   the commit, by the committed file (the pool's provenance: made 23:24:16 PST, `committed: true`, git head `153b720f`); the critic
   re-made it from the committed generator and the designer's downloads, and 88 of its 90 files are identical (item 3). The verifier and
   the critic judged that the blind claim stands; it is disclosed in DESIGN.md section 0.
2. **Two re-runs come from blind6 tiles flagged `hold`:** `fp32.a_onebit_b5_third` and `fp32.real_smol_softmax_v_causal`. In blind6,
   `hold` marks the hold candidates of the heat end-to-end holds (`blind6.json` › `hold_candidates`, E154 and E161). Both were measured
   as kinds in both pool-6 sessions, with every C check PASS: `fp32.a_onebit_b5_third` E153 4 passes, 9.443 W, and E157 3 passes,
   8.964 W; `fp32.real_smol_softmax_v_causal` E153 4 passes, 13.317 W, and E157 3 passes, 12.827 W (each session's primary D;
   40 launches each in E153's `ccheck-all.json` and E157's `ccheck-session.json.gz`, all PASS). The re-run rule ignores the source flag,
   and pool 8's MANIFEST and RERUNS write `rerun:blind6`. They stay re-runs, scored apart (LG); their references are clean.
3. **The README's "reproduces every byte."** The generated `README.md` says a rebuild reproduces every byte. A rebuild from the
   committed generator reproduces 88 of the pool's 90 files: `provenance-blind8.json` differs in `made_at` (and in `git_head` once HEAD
   has moved), and `SHA256SUMS`'s line for it with it. Every tile, MANIFEST, RERUNS, `real/` and README are identical.
4. **check's S-tile crash.** `make_blind8.py check` stops with a traceback (TypeError, exit 1) when an S tile's bytes lose their
   single-bit structure: `byte_sig` gets None from `single_bit_b` (line 265). A corrupted tile still fails the check (a non-zero exit);
   only S crashes (a flipped bit in a U tile is listed as a problem). Cosmetic; no tile is affected.
5. **DESIGN.md's dateline.** It opens "Written Wed 4 Nov 2026, 23:20-23:35 PST ... before any tile of the pool exists". It was last
   written at 23:21:08 and committed at 23:22:03 (`153b720f`); the pool's tiles were written 23:24:10-23:24:16. The stated end runs 13
   min past the commit and 11 min past the tiles. Precedence holds by git.
6. **The TEST pool's seed block.** The TEST pool's provenance (the designer's scratch, never committed) names commit `c996d135` and its
   rule but holds TEST_SEED's value, `0xc600b8998cea28aa`, because `write_pool` writes `SEED_COMMIT` and `SEED_RULE` unconditionally.
   It affects the TEST pool only: pool 8's provenance holds the real seed, `0x1da1fde559d92805`, which recomputes from `c996d135`
   (an ancestor of `153b720f`).

The verifier's list had one more item in the place the round's list gives the dateline: the lab scanner `sanitize_extracts.py` checks
only its fixed list on this Mac, so the designer's "privacy scan: clean" covers that list only, and `153b720f`'s message carries the
attribution lines twice. Recorded here too; neither changes a file of the pool.

## A1-6. The order

1. This note, `blind8_json.py`, `roundtrip-blind7.json`, `a1_checks.py` and `a1-checks.txt`, in one commit (new files only), before
   `blind8.json` exists.
2. `blind8_json.py convert` writes `blind8.json`; then A1-3's reading. If it differs, the lane stops.
3. The bench driver; the build checks; the counts on the mini, step by step.
4. `predict_pool8_a2.py predict` on the four cards, then `intervals`.
5. The public-text scan, then ONE commit, before any claim: the pool, `blind8.json`, the A1-3 reading, the driver, the counts and run
   records, the four predictions files, the intervals and a hash list of this lane's new files (this commit's included).

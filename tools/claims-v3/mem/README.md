# V3-MEM: memory anatomy, the cycle-counter window and the wake-up probe, on both cards

This experiment is PLAN3.md section 2, "V3-MEM" (it merges anat-X1, anat-X2, E-hub-2 and EXP-dvfs-1; new code N1).
It tests 80 claims through 15 pre-registered items: MEM-P1 to P10, MEM-X2, MEM-R1 to R3 and MEM-W. It uses
`workloads/memprobe` op programs and needs no new device code.

| file | what it is |
|---|---|
| `block.sh` | one pass on the local card: `bash tools/claims-v3/mem/block.sh <pass> [--smoke]` |
| `memv3.py` | file checks and drop rules (used by the block and the reducer); the counter-window and wake-up analyses |
| `reduce.py` | the decisions: `python3 tools/claims-v3/mem/reduce.py --data DIR --out verdicts.json` |
| `prereg/` | byte-identical copies of the pre-registered scratch reducers the plan names (hashes below) |

## What a pass does (`block.sh k`, exp name `mem`)

1. The block does not start, and exits 3, while another user is logged in, another user's device process runs, one
   of our own device processes still runs, or the `et_soc1` module's use count is not 0 (plan 2.13). It exits 2
   before touching the card if `workloads/memprobe/gen_ops.py` differs from the pre-registered copy
   `prereg/mp/gen_ops.py` (on aifoundry3 the tree is a synced copy; an older generator would write other programs
   under the same names).
2. `memprobe_host --info` reads the arena base. The block fails if the base is not 1 GB aligned (bits needs this, and
   so does P10).
3. The op lists are generated off-card with the plan's commands and seeds: `s = 100+k` for decomp, msmap, bits,
   refresh_jit and pagetimeout; seed 1 for ladder; `200+k` for the requester decomp; `20+k` for the wake-up probe.
   `t_rawodd` is the plan's `python3 -c` command, verbatim.
4. On aifoundry2 only, heat to 76 C (`heat76` in block.sh: lib.sh's `heat_to 76` loop, the same heater command,
   plus an `others_present` check before each heater launch). The block fails if the heater gives up, and exits 3
   (the queue retries) if another user arrives while it heats.
5. The 10 Hz sampler starts (`start_sampler`, with retry and drain). On aifoundry2 the block fails if it does not
   start, because a pass without telemetry is dropped there.
6. The 11 programs run in `shuf` order, each as its own process. The order is recorded in `order.txt`. The programs
   are t_raw, t_glitch, t_rawodd, ladder, decomp, l3map, msmap, bits, refresh, refresh_jit and pagetimeout.
7. ladder and then decomp run from requesters 7, 24 and 31 (`--hart 64*S`), into `req<S>/`.
8. The sampler stops (SIGTERM).
9. The wake-up probe runs in passes 1 to 3, and in any later pass while this card has fewer than 3 kept probes. On
   aifoundry2 the die is first topped up to 76 C (`heat76`). Then come a 1 s sample (5 Hz) to `wake/pre.jsonl`, the
   probe (`--reps 20`, delays 0 to 16M cycles), and a 1 s sample to `wake/post.jsonl`. If another user has arrived
   by then (checked before the heat, between heater launches and before the probe), only the probe is skipped
   (`wake/skipped`, noted in block.json): the X1 part already ran and is kept, and a later pass re-runs the probe.
10. `drop.json` is written, the `.ops` files are deleted (they can be regenerated from the seeds), and the gen_ops
    label `.json` files and the telemetry are gzipped.

Every memprobe process runs under `hold10` (timeout 10) with `--budget 8`. Nothing else opens the management node
while the sampler runs, because memprobe opens only the ops node. Before each program, the block checks
`others_present` again. If someone has arrived, it stops the sampler, marks the block failed and exits 3; the queue
then retries the pass.

Passes 6 and later are conditional re-runs. A pass k > 5 does nothing (exit 0, no block.json, the card is not
opened) when the card already has 5 kept X1 passes and 3 kept wake-up probes, or when it has 5 kept X1 passes and the
missing probes will come from passes 1-3 that were never tried. It runs only the wake-up probe when the card has 5
kept X1 passes but fewer than 3 kept probes. A pass 1-3 that failed, or that the queue gave up on (only
`p<k>.attempt-*` left), is not counted as a future probe, so pass 4 or 5 (or 6-8) takes over its probe. Put `mem 6`,
`mem 7` and `mem 8` at the end of each card's schedule.

**Status.** A block is `fail` only if the arena base, the heater (aifoundry2), the sampler start (aifoundry2) or one
of the 11 core programs fails. A requester or probe failure is recorded in the note, and in `drop.json` and
`runs.jsonl`. A drop is recorded in the note (`x1 DROP (...)`, `probe DROP (...)`) while the block stays `ok`. The
reducer re-derives every drop from the files.

**Schedule.** Run 5 passes per card with at least 10 minutes between passes on one card (plan 2.13), interleaved with
other experiments, then `mem 6` to `mem 8`.

**Card minutes per pass.** These are estimates (nothing has run on a card yet).

| card | card minutes per pass | where the time goes |
|---|---|---|
| aifoundry2 | about 3 to 4 | heat_to 76 from a warm-idle die, about 1.5 min; 17 processes at 2 to 4 s each; the sampler start; the wake-up part, about 0.5 min with its heat top-up |
| aifoundry3 | about 1.5 to 2 | no heater |

The plan allowed 18 and 10 card minutes per 5 passes. The worst case is bounded by 17 × 10 s plus the lib's heat
limit, well under 35 min.

**Smoke (`block.sh 1 --smoke`, exp `mem-smoke`, about 25 s of card time).** It checks each component in its smallest
form:
- `--info`;
- one 2 s heater launch on aifoundry2, with the die read before and after;
- the sampler;
- t_raw, t_rawodd and t_glitch;
- the plan's smoke test (a 16-line decomp from shire 7, `--hart 448`), plus a 4-line ladder for its L1 reference;
- a 1-rep wake-up probe between the 1 s pre and post samples;
- `memv3.py smoke`, which parses every output and prints the problems to `smoke.json`.

The block is ok only if there are no problems.

**Dry run.** `V3_DRY=1 bash tools/claims-v3/mem/block.sh <k> [--smoke]` prints every device call, including `--info`,
the heater, the samplers and each memprobe launch. `V3_FORCE=1` re-runs a finished pass and first moves the old
folder aside as `p<k>.attempt-<time>`.

## Per-pass layout (`build/claims-v3/<card>/mem/p<k>/`)

- Program data: `<prog>.u32` and `<prog>.json.gz` (labels) for the 11 programs; `req{7,24,31}/{ladder,decomp}`;
  `wake/wakeup.*`, `wake/pre.jsonl`, `wake/post.jsonl`.
- Telemetry and heating: `telemetry.jsonl.gz`, and `heat.jsonl` on aifoundry2.
- Process logs: `info.log`, `memprobe.log` (MEMPROBE lines), `memprobe.err` (host stderr, one header per process),
  `runs.jsonl` (rc and times per process), `order.txt`, `gen.log`.
- Records: `code.sha256` (including the prereg copies and gen_ops.py), `binary.sha256` (the host and
  `kernel/memprobe.elf`), `drop.json`, `block.json`.
- Size: about 1.5 MB per pass.

## What is dropped, and why

- **aifoundry2 X1 part.** An X1 part (the 11 programs plus the requesters, all under the sampler) is dropped if any
  sample has `mhz.minion != 600`, or if there is no telemetry (no sample with a clock reading). This is the plan's
  rule. A sample whose frequency request failed carries no `mhz` field (ettelem prints it only on success); it is a
  gap, not a sample off 600 MHz, and is counted as `n_no_clock` in the pass record. The refresh period and hop slope
  are never used to drop, because they are under test.
- **aifoundry3 X1 part.** It is never dropped on the clock, which is recorded. aifoundry3 is pinned at 600 MHz.
- **Wake-up probe.** It is judged on its own pre and post samples, not on the X1 sampler. On aifoundry2 a probe whose
  samples show `!= 600` (or are missing) is dropped and re-run. This follows the binding rule, although EXP-dvfs-1's
  P6 only says the clock is "recorded" there. On aifoundry3 the probe is kept and P6 reports whether the clock was
  600 MHz.
- **Incomplete or failed blocks.** A program whose u32 count differs from its labels makes the X1 part incomplete.
  Any block whose `block.json` is not `ok` is not used, and neither are the queue's `p<k>.attempt-*` folders.
- **Extra passes.** The reducer uses the first 5 kept X1 passes and the first 3 kept probes on each card, in pass
  order. Later kept passes are listed in `<out>.passes.json` as unused. This is a fixed rule, not a choice.

## Deviations from the plan's commands, and why

- **Arena base once per pass.** `--info` runs once per pass, not once per session, because every pass is its own
  session, at least 10 minutes apart. The base is read from the `arena_base` field of the MEMPROBE line. The host
  prints `MEMPROBE {"test":"info","arena_base":"0x…"}`, so this is the same value as the plan's
  `grep -o '0x[0-9a-f]*' | head -1`.
- **Stopping the sampler.** The plan's `kill $SAMPLER` is lib.sh's `stop_sampler`, which sends SIGTERM and waits. The
  plan's `| tee -a memprobe.log` is an append to `memprobe.log`.
- **Pre and post samples.** They use `start_sampler <file> 1 --every-ms 200` (retry and drain), a 1.2 s wait, and
  then `stop_sampler`. The plan uses a bare `timeout 10 ettelem sample --seconds 1 --every-ms 200`. The samples are
  the same: ettelem reads its flags in order, so a later `--every-ms` overrides lib.sh's 100, as `ettelem.cpp` line
  194 shows.
- **Heat before the probe (aifoundry2).** The die is topped up to 76 C before the wake-up probe as well, not only once
  before the sampler. The binding rule is that memory-bound work on aifoundry2 starts at 76 C or above, and the X1
  programs let the die cool.
- **Skipped probe (aifoundry2).** When the pre sample cannot start, the probe is skipped, because it would be dropped
  anyway.
- **Timer programs in separate processes.** The E-hub-2 component ran t_raw, t_glitch and t_rawodd in one process;
  the merged V3-MEM plan, followed here, runs each in its own process. As a result, MEM-R3 reads e from the t_glitch
  launch itself (see below).
- **Re-runs.** Passes 6 and later are the plan's "re-run dropped passes until >= 3 kept (target 5)", made
  automatic. The wake-up probe runs past pass 3 only as such a re-run.
- **Mid-pass arrivals.** If another user arrives mid-pass, the block stops with rc 3 before the next program or
  heater launch (the queue retries the pass). After the X1 part it only skips the wake-up probe. The block also
  checks the `et_soc1` use count before it starts.
- **Heating (aifoundry2).** `heat76` in block.sh repeats lib.sh's `heat_to 76` (same heater command, same 150-launch
  limit, same `heat.jsonl` record) and adds an `others_present` check before each heater launch, which lib.sh's loop
  lacks. In a dry run it calls lib's `heat_to` stub, so the dry output still shows the heat.
- **Smoke.** The smoke test is larger than the plan's one 16-line decomp from shire 7, so that it checks every
  component (listed above).

Checked against the sources, all of which agree with the plan:
- **gen_ops flags.** Every gen_ops flag exists in `workloads/memprobe/gen_ops.py`. bits keeps its default
  `--pre-delay 2000`, as in the committed 19 Sep run.
- **memprobe_host.** `memprobe_host --hart H` launches on shire H/64 and copies the op list into that shire's own
  scratchpad (`host/main.cpp`, `kernel/memprobe.c`). The host waits at most 6 s per kernel. The probe's 16M-cycle
  delays make about 4.9 s at 600 MHz (E18 held the card for 4.9 s), so it fits.
- **Build paths.** The paths come from lib.sh. On aifoundry2 the host is `build/memprobe-v3/host/memprobe_host`,
  whose `kernel/memprobe.elf` has the same sha256 (`55c6dbab…`) as the 19 Sep build. On aifoundry3 it is
  `build/memprobe/host/memprobe_host` under `~/nekko`.
- **The requester reducer.** The inventory's `recompute_latency.py --requester` cannot read a `req<S>/` folder. X2
  uses the verifier's `extra_values.py --x2-only`, as the plan says.

## Reduction

```bash
# after collecting build/claims-v3/<card>/ of both cards under one folder DIR (DIR/aifoundry2/mem/p1/..., DIR/aifoundry3/...)
python3 tools/claims-v3/mem/reduce.py --data DIR --out DIR/mem-verdicts.json   # also writes DIR/mem-verdicts.passes.json
```

The reducer runs off-card in under 1 s per pass. It works on partial data: with fewer than 3 kept passes on a card,
an item is `INSUFFICIENT`. Each record holds the item, its claims, the plan's prediction and decision rule, the test,
the per-card values and intervals, the outcome (`PASS`, `FAIL`, `CARD-DIFFERENT` or `INSUFFICIENT`) and a one-line
reading. MEM-R2 also carries the page wording.

**MEM-P1 to P10 and MEM-X2** use `prereg/`, unchanged. `reduce.py` stages each pass in a scratch copy (it un-gzips
the labels; `recompute_latency.py` never writes next to the data). It then calls `crosscard_v3.pass_values`, which
runs `recompute_latency.py --l1-ref --fixed-model`, `timer_window.py` and `extra_values.py`, including `--x2-only` for
each complete `req<S>/`. The bands, the one-sided rule for bounded fractions and the every-pass rules are those of
`crosscard_tests.py` as `crosscard_v3.py` modifies them. On top of that, `reduce.py` applies these rules from the V3
table:

- **MEM-P7.** The registered decision is "every pass, each card", so z must lie in [-3, 3] in every pass. The
  inventory's code put z under a 99% t-interval; that interval is still reported beside the rule.
- **MEM-P10.** "Arena base 1 GB aligned" is checked in every pass, from the MEMPROBE lines. A block stops on a
  misaligned base (the plan's assert), so such a pass is never kept; the reducer therefore also reads the base of
  every attempted pass folder, whatever its status, and a misaligned one fails the sub-test on that card.
- **MEM-P5.** A pass whose median locked-loop period is outside 512 to 651 cycles is reported and not tested for the
  slow fraction. If every pass on a card is outside, that sub-test does not apply.
- **Every-pass items, and the 3-repeat rule.** The plan's common rule is that fewer than 3 kept repeats on a card
  leave the claim as it is. It applies in both directions: an every-pass item (and MEM-R1, R2, R3) with fewer than
  3 kept passes on a card is undecided there even when a pass already shows an exception; the exception is listed in
  the reading ("seen: ..."). With 3 or more kept passes, any exception fails the item. The inventory's EXACT had no
  pass count.
- **anatomy-35.** It is restored only if P8b and P8c hold on both cards.

**MEM-R1 to R3** follow the registered test text (the plan's "validate3/hubv phase analysis" was inline code, not a
script) and are implemented in `memv3.py`:

- **Raw pairs (t_raw, t_rawodd).** A read at low bits `L <= e` returns 128 short with its low bits unchanged. So a
  pair `(L0, L1, d)` fits the windows e with `10 + 128([L0<=e] - [L1<=e]) == d`.
  - The registered readout uses only the pairs whose first read is at low bits 0 or 10 (t_raw), or at 0, 1, 10 or 11
    (t_rawodd), and whose difference is 10, 138 or -118. It is the set of e that fits them; the phases actually
    reached are reported. A pair with another difference is an R1 exception, not a reading of e, and a readout that
    no single e fits ("none fits") is not a reading either: neither can make R2's readouts "differ".
  - R1 uses every pair. The differences must be only 10, 138 or -118, and the set of e that fits all pairs must be
    non-empty and meet {9, 10, 11}.
- **t_glitch.** With no ±128 errors, e = 10. When the modal stamp phase of the -128 errors is 10 after that of the
  +128 errors, e = 9. When it is 10 before, e = 11. Anything else, including intervals other than 10, 138 or -118, is
  an R1 exception.
- **R2.** The readouts are sets, and "at least 2 distinct e" means that no single e fits every readout. The outcome
  is aifoundry2's, with at least 3 kept passes. aifoundry3 is reported (no prior). The page wording is chosen only
  from cards with at least 3 kept passes.
- **R3.** R3 is per t_glitch launch: e = 10 needs 0 off-by-128 intervals, and e = 9 or 11 needs 1% to 3%. Since each
  program is its own process, e comes from the same launch, so R3 tests the size and the single-phase shape of the
  miscorrection.

**MEM-W** (EXP-dvfs-1) uses the first 3 kept probes per card:

- **P1.** For L1 and for L1-in-place, at least 19 of 20 lines must be exactly 0 at every idle, and every nonzero
  value must be ±128.
- **P2.** The L3 median difference at 16M must be within ±2.
- **P3.** The L2 values are first re-referenced to the frame the 59-62 / 48-51 bands were written in: the 22 Sep run,
  whose L1 read 17 raw. Each value is shifted by (the pass's median L1 value - 17). This is the plan's "every latency
  re-referenced to the pass's own L1 hit"; without it, a build that reads L1 at 10 would fail the band. P3b is the
  median at 300 cycles against the median at 16M, within 1.
- **P4.** Each DRAM difference at 16M gets a class: slow is +8..+15, fast is -7..+7, outlier is beyond ±30, and
  anything else is "other". A pass holds if 40% to 85% of lines are slow, no line is "other", and at most 2 are
  outliers. Class agreement means the same label at 1,000 and at 16M, pooled per card, at least 0.80.
- **P5 (the decision).** No level may have at least 18 of 20 lines at +5 or more at 16M.
  - PASS on a card when P5 holds in 3 of 3 probes.
  - "Wake-up claimed" when P5 fails in at least 2 of 3; a single failure is "mixed". Both count as not holding.
  - A failing P3b only drops the settling explanation (dvfs-14), and the reading says so.
- **P6.** P6 reports the pre and post clocks.

**Pre-registered code (`prereg/`)** is copied byte-for-byte from the scratch folders the plan names. The sha256 of
each copy equals its source's:

```
bc16d52ab35132ee8f3335b9f0f4b2ccf78ff7e9aa32ca95c52b7b0f16c092c0  crosscard_tests.py   (validate3/inv/anatomy-work/)
c14f7fb0a347f3bab24b541e9abfe1ad5057c3afe38ac152fda220ee2911c156  recompute_latency.py (validate3/inv/anatomy-work/)
9951c3c1287b02d8788543ccfc632088fa929e68128e8b26c41363a45c3cb896  timer_window.py      (validate3/inv/anatomy-work/)
379e1522c16f5cc9884263c83e29d63084989fdbe996d6a80db35e3502ac89b3  mp/gen_ops.py        (validate3/inv/anatomy-work/mp/, = workloads/memprobe/gen_ops.py)
7088701dafb4455148fabeafab8ead0b8fdf5b609c74d50505ac651f64a27bbe  crosscard_v3.py      (validate3/anatomy-verify/tests/)
3fac585cf840b5be43d5e10ad47068771ba87f591e37acec5ed7a3534d3f7a39  extra_values.py      (validate3/anatomy-verify/tests/)
```

`crosscard_v3.py` still names the scratch path of `crosscard_tests.py`. `reduce.py` imports the prereg copy first, so
the copies are what runs even after the scratch folder is gone.

**Tested (no card).** The data are under `validate3/drv/mem/`, built by `make_synth.py`.

| test data | result |
|---|---|
| the committed 19 Sep folder as one aifoundry2 pass | P1 to P10 values equal the verifier's `dryrun_v3.json`; the readouts already differ (t_raw e >= 10, t_glitch e = 9, as hub-001 found), but with one pass every item, R2 included, is `INSUFFICIENT` |
| 5 perturbed passes per card, with planted drops | the drops are applied: a 700 MHz sample, and an 800 MHz pre-sample on a probe |
| the same, with a planted aifoundry3 L3 shift | `CARD-DIFFERENT` on MEM-P1 |
| planted failures | P3, P7, R1 (e = 12), R2 (e constant) and MEM-W (wake-up claimed) all fail as expected |
| partial data | every item is `INSUFFICIENT` |
| a sixth kept pass | it is not used |

Reviewer's cases (`validate3/drv/mem/review/`, built by `make_review.py`; outputs `*-verdicts.json`):

| test data | result |
|---|---|
| `bothfail`: the same failures planted on both cards (L3 +6, one msmap line, refresh period 2,340, t_rawodd e = 12, +15 cycles on DRAM at 16M in 2 of 3 probes) | `FAIL` on MEM-P1, P3, P5, R1 and MEM-W (wake-up claimed on both cards) |
| `few`: aifoundry2 has 2 kept passes, one with an msmap failure | every item `INSUFFICIENT`; MEM-P3's reading lists the failure ("seen: ...") |
| `baddiff`: e = 10 everywhere, one aifoundry2 t_raw pair at low bits 0 with difference 11 | R1 `CARD-DIFFERENT` (the exception), R2 `FAIL` (e constant; the bad pair is not read as a second e) |
| `clock`: aifoundry2 pass with one sample lacking `mhz`, one with a 700 MHz sample, and a failed block on base 0x8050000000 | the gap pass is kept, the 700 MHz pass dropped; MEM-P10 `CARD-DIFFERENT` from the misaligned attempt |

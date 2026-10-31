# E81 — the DRAM pattern question: is a two-value image cheap because it repeats? (Q130)

## Results

*Ten passes, `p8110`–`p8119`, Sat 31 Oct 2026 14:49:35–15:13:02 PDT on aifoundry3 card 0, 600 MHz, `--harts 1`
(1,024 harts), eleven DRAM items and the drift anchor per pass, after a smoke (`p8101`, 14:47:47). **22.8
card-minutes** of the registered 45. Every pass `block.json` `"status":"ok"`, 130 runs, **no run-gate failure**.
Pre-registered in `14f219ef` (14:45 PDT) before the claim (14:47:21) and the first launch. Reduced with `reduce.sh`
(the registered `tools/claims-v3/dp/reduce_dp.py`, unchanged). Pass 8110 is the registered warm-up and pass 8119 is
set aside by the registered drift rule (−0.647 W), so **the headline is eight passes, 8111–8118** (df = 7). Every
number below is from `dp.json` `headline` unless it says otherwise.*

**The hub's question has a two-part answer.** A two-value alternating image is cheaper than random data at the same
changed-bit and carried-one counts **partly because it repeats, but mostly because of where its ones sit inside each
line:**

> | at E75's k256 counts (256 bits change between lines, 256 ones per line) | W | pJ per 64 B line | share |
> |---|---:|---:|---:|
> | E75's own image (`dp_c2`: two values, ones in contiguous runs) over zeros | 1.866 [1.751, 1.980] | 1,591 | — |
> | **the arrangement:** the same bits scattered inside each line (`dp_s2 − dp_c2`) | **+0.996** [0.936, 1.055] | **+849** | **61 %** [57, 65] |
> | **the period:** 8,192 distinct lines instead of two (`dp_bern − dp_s2`) | **+0.640** [0.574, 0.706] | **+546** | **39 %** [35, 43] |
> | the whole step, E75's image → random bits at its counts (`dp_bern − dp_c2`) | **+1.636** [1.600, 1.671] | +1,395 | 100 % |
>
> *95 % t intervals over the eight headline passes. A line is one 64 B DRAM line; the line rate is measured,
> 1.1729 × 10⁹ lines/s (75.1 GB/s of lines).*

So **"compressible" fits only the smaller part.** Repetition does save power, and a short repeat is enough to get
all of the saving: a scattered **4-line** cycle costs exactly what a scattered 2-line cycle costs (`per_s_2to4`
+0.030 W [−0.061, +0.122]), and the whole period effect appears between four distinct lines and 8,192
(`per_s_4tolong` +0.610 W [0.496, 0.723]). The arrangement costs at every period: **+0.547 W** [0.388, 0.706] at period 1 (where no line ever
changes), **+0.996** at period 2 and **+1.124** [1.034, 1.213] at period 4.

**What this does to E75's "36.6 %".** At random's own counts the gap is measured directly here, with no model:

| step, at random's counts (192 changes, 290 ones per line) | W over zeros | share of the chord |
|---|---:|---:|
| a contiguous two-value image (`dp_c2r`) | 2.063 [2.028, 2.098] | **64 %** |
| + scattering its ones (`dp_s2r − dp_c2r`) | +0.808 [0.679, 0.938] | **+25 %** |
| + the rest, to random floats (`dp_random − dp_s2r`) | +0.351 [0.105, 0.597] | **+11 %** |
| = the zeros-to-random chord (`dp_random − dp_zeros`) | **3.222** [3.093, 3.350] (E75: 3.250) | 100 % |

The counts carried in E75's arrangement account for **64 %** of the chord when they are measured, not the 36.6 %
E75's two-arm model gave them: E75's model extrapolated to a (k = 0, w = 0) intercept that sits 0.8–1.4 W above the
zeros anchor (the first carried ones cost the most), and counted that step as unexplained. Of the 36 % that is left
(1.159 W [1.032, 1.286]), **scattering closes 70 %** (0.808 W) and the remaining 0.351 W is the period effect (+0.64 W
for random bits) net of what random *floats* save over random bits: **random floats cost 0.280 W [0.226, 0.334] less
than random bits** (`dp_random − dp_bern`) despite carrying 32 more ones per line, because the top byte of every
float in [0.5, 2) is the same (0x3F), which removes a quarter of the changes between consecutive words and lines (190 against
256 per line).

**None of it is on the compute rail.** The minion rail reads 8.32–8.48 W across all eleven items (8.421 W for `dp_c2`,
8.424 W for `dp_s2`: +0.003 W for the board's +0.996 W). The data-dependent energy of a DRAM load is on the memory
side: the DRAM, its interface and the paths between them (`runs.csv` `rail`).

### Every item

| item | period | arrangement | k | w | W over zeros (95 %) | pJ per line |
|---|---:|---|---:|---:|---:|---:|
| `dp_zeros` | 1 | — | 0 | 0 | 0 (32.252 W absolute) | 0 |
| `dp_c4` | 4 | contiguous (Hadamard) | 256 | 256 | 1.768 [1.645, 1.891] | 1,507 |
| `dp_c2` = E75's k256 bytes | 2 | contiguous | 256 | 256 | 1.866 [1.751, 1.980] | 1,591 |
| `dp_c1` = E75's k0 bytes | 1 | contiguous | 0 | 256 | 2.046 [1.880, 2.211] | 1,744 |
| `dp_c2r` | 2 | contiguous | 192 | 290 | 2.063 [2.028, 2.098] | 1,759 |
| `dp_s1` | 1 | scattered | 0 | 256 | 2.593 [2.384, 2.802] | 2,210 |
| `dp_s2` | 2 | scattered | 256 | 256 | 2.861 [2.720, 3.003] | 2,440 |
| `dp_s2r` | 2 | scattered | 192 | 290 | 2.871 [2.738, 3.004] | 2,448 |
| `dp_s4` | 4 | scattered (Hadamard) | 256 | 256 | 2.892 [2.722, 3.061] | 2,465 |
| `dp_random` | 8,192 | floats in [0.5, 2) | 190.2 | 288.3 | 3.222 [3.093, 3.350] | 2,747 |
| `dp_bern` | 8,192 | random bits | 256.1 | 256.0 | **3.501** [3.394, 3.609] | **2,985** |

Read down the table: every contiguous image costs less than every scattered one, whatever its period or counts; the
two long-period images cost the most; and among images of the same arrangement and period, the counts move little
(E75's own k-arm finding, reproduced: `dp_c1 − dp_c2` = +0.180 W [0.108, 0.252], E75 +0.20).

### Scoring

| # | prediction (registered) | reading | verdict |
|---|---|---|---|
| P1a | chord 2.65–3.85 W (E75 3.250) | **3.222** [3.093, 3.350] | **PASS** |
| P1b | `dp_c2 − dp_zeros` 1.30–2.50 W (E75 1.933) | **1.866** [1.751, 1.980] | **PASS** |
| P1c | `dp_c1 − dp_c2` −0.10 to +0.50 W (E75 +0.20) | **+0.180** [0.108, 0.252] | **PASS** |
| P2 | arrangement at period 2, 0.40–1.60 W | **+0.996** [0.936, 1.055] | **PASS** |
| P3a | arrangement at period 1, 0.40–1.60 W | **+0.547** [0.388, 0.706] | **PASS** |
| P3b | arrangement at period 4, 0.40–1.60 W | **+1.124** [1.034, 1.213] | **PASS** |
| **P4** | **no period effect** (`dp_bern − dp_s2` inside ±0.30 W) | **+0.640** [0.574, 0.706], present | **FAIL** — the hub's alternative holds in part: a long period costs |
| P5 | `dp_random − dp_s2r` within ±0.35 W | **+0.351** [0.105, 0.597] | **FAIL**, by 0.001 W on the mean; its interval is wide because two dip samples in one pass (8115) pull `dp_s2r` down (below) |
| P6 | `dp_random − dp_c2r` 0.70–1.80 W | **+1.159** [1.032, 1.286] | **PASS** |
| P7 | `dp_random − dp_bern` −0.30 to +0.45 W | **−0.280** [−0.334, −0.226] | **PASS**, at the low edge: random floats are *cheaper* than random bits, which the registration did not expect (it expected +0.1 W from the extra ones) |

**8 of 10 pass.** The registered hub rule reads **"both: the repetition and the arrangement each cost"**
(`dp.json` `hub.verdict`). Every verdict is the same at the two leakage sensitivities (`dp-leak0.2936.json`,
`dp-leak0.3803.json`; the registered auto slope is 0.0132 W/°C, from 47 runs): the arrangement at period 2 reads
0.996 / 0.929 / 0.909 W and the period 0.640 / 0.654 / 0.658 W across auto / 0.2936 / 0.3803 W/°C.

### The board meter's dips (a labelled post-hoc view; no registered verdict rests on it)

aifoundry3's board reading now and then lands on the 1–2 ms gap between two of a run's 0.4 s launches, and the
service processor holds the near-idle value for two 100 ms samples: E82's amendment A2 found the same on aifoundry1
card 1 the same afternoon. The registered estimator has no gate for it. **85 dip samples in ten passes, 12 of them
inside a run's [1 s, 3 s) window** (`dips.json`): two each in 8115's `dp_s2r` (−0.85 W on that run) and `dp_zeros`, in
8119's closing `anchor_pi` (the whole of 8119's −0.647 W drift) and in the warm-up's `dp_c1`, and one each in 8111's
`dp_s1`, an `anchor_pi` of 8113, 8114's `dp_s4` and 8115's `dp_c2r`. With those samples removed by E82's definition and every gate unchanged (`posthoc_dips.py`,
`dp-posthoc-dips.json`, nine headline passes because 8119 is no longer set aside): arrangement at period 2 **+1.012**,
period **+0.635**, the whole step **+1.647**, and P5 reads **+0.237** [0.196, 0.277] — inside its range. **The
registered result stands: P5 is a FAIL**; the view shows that its failure is the meter's, and that nothing else moves.

### What the arrangement and the period cost per event (derived, and partly post hoc)

The registered derived reading (`derived_not_scored`) divides each arrangement contrast by the toggles it adds between
consecutive 16-, 32- and 64-bit pieces of the stream, under an in-order mapping of a line onto a narrower path. **No
single width fits all four**: at 16 bits the arrangement costs 2.1, 4.2, 5.3 and 3.4 pJ per added toggle at periods 1,
2, 4 and at random's counts; at 64 bits the period-4 contrast even *removes* toggles (−35.5) while costing +1.124 W. So
the arrangement is not "toggles on one narrow bus".

**Post hoc, labelled (selected among 41 count models, so read it as a description, not a measurement):** four
per-line counts account for all ten items to **71 pJ per line rms** against 1,500–3,000 pJ per line (largest
residual −132 pJ, `dp_s1`):

    pJ per line over zeros ≈ 4.1 × (ones) + 3.9 × (toggles between consecutive 16-bit pieces)
                           + 2.4 × (toggles between the line's two 32 B halves)
                           + 2.2 × (bits changed between consecutive lines, only when the stream has > 4 distinct lines)

That shape fits a 64 B line moving as 16-bit beats over the DRAM interface (the ones and the beat-to-beat toggles)
and as two 32 B halves on a wide path, and **paths that each carry only every N-th line of a stream, with N a
multiple of 4**: if consecutive lines are spread over channels or banks that way, a period of 2 or 4 gives every such
path one constant value, so nothing on it ever changes — which would also explain why E75's DRAM k-arm (changes
between consecutive lines of one hart's stream) was flat. This is an inference from counts, not a measured mechanism: the card's address-to-channel map and its data-pin
mapping are not known here.

## What ran, and what was registered

| | registered (`tools/claims-v3/dp/`, `14f219ef`) | happened |
|---|---|---|
| command | E75's DRAM command unchanged: `flw_pat --harts 1 --seconds 4 --window 240000000 --stride 64 --slice-bytes 131072 --region 131072`, E75's binary | the same; the dry run printed exactly the eleven registered command lines (`logs/e81-dry.log`) |
| items | eleven DRAM items (E75's k0 and k256 bytes, their scattered twins, a Hadamard 4-cycle contiguous and scattered, `bern:0.5`, a contiguous and a scattered 2-cycle at random's counts, E75's zeros and random) + `anchor_pi` first and last | all of them, every pass |
| harness | E75's `mf/block.sh` and `mf/queue_mf.sh` unchanged, `MF_GEN=build/dp-gen MF_EXPN=dp`; `runitems.py` | the same; all twelve harness files hashed identical on the box and the Intel before the first launch (`logs/e81-box.sha`) |
| passes | smoke 8101, then 8110–8119; 8110 the warm-up, headline 8111–8119 | smoke 8101 (14:47:47–14:49:22, every launch ok); passes 8110–8119 (14:49:35–15:13:02, 1.99–2.22 min each). 8110 the warm-up; **8119 set aside** by the drift rule (−0.647 W: a meter dip in its closing anchor, above); headline 8111–8118, eight passes, df = 7 |
| budget | at most 45 card-minutes; `build/mf-STOP` at 38 | **22.8 card-minutes** (smoke 1.61 + passes 21.20); the 38-minute stop never acted; card session 14:47:45–15:13:33 PDT |
| claim | one post in `#community-lab` after the registration and before the first launch, edited at the release | posted 14:47:21 PDT, released 15:17 PDT by editing the same post (` — released` appended, every word kept) |
| card state | nothing set; `ettelem config` read only, under the lock, `timeout 10`, at both ends | `tdp_w` 0, `temp_threshold_c` 65, 600 MHz, 523 mV, `max_power` at 14:47:45 and at 15:13:33 (`ident/`); nothing written. Every launch at a 58.0 °C reading after a 59 °C preheat; window means 58.0–59.2 °C; worst window median `took_ms` 22 ms |

## Departures, dated

- **D1 (31 Oct 2026, after the registered reduction) — a labelled post-hoc view of the board meter's dips**
  (`tools/claims-v3/dp/posthoc_dips.py`, `dips.json`, `dp-posthoc-dips.json`, `reduce-posthoc-dips.txt`). The dips
  were found while reading the registered result, so this is not an amendment: it moves no registered verdict and
  is reported beside the result. It uses E82 amendment A2's definition unchanged (a sample more than 4 W below both
  samples two steps away), on a copy of the telemetry, every gate unchanged.
- **D2 (31 Oct 2026, after the data) — the per-event account is post hoc.** The registered derived reading (toggles
  at 16, 32 and 64 bits) is reported as registered; the four-count model beside it was chosen among 41 count models
  after the data were seen, and is labelled a description.
- **D3 (inherited, as E60–E79) — two device processes outside `timeout 10`.** `lib.sh`'s `die_c` in `block_begin` /
  `block_end` runs `ettelem sample --seconds 1` under `timeout 20`, and the telemetry sampler runs for the whole pass:
  `lib.sh`'s frozen design (`033d0776`), as in every block since E60. Every enercat and sparsity launch ran under
  `timeout 10`.
- **Not departures, for the record.** The registration's random counts were the law's (191.1 changes, 290.7 ones per
  line); the replica of the host's own source gives the realized 190.17 and 288.26, and `dp_c2r`/`dp_s2r` were built
  at 192/290 as registered (1.7 ones from random's, about 0.007 W at E75's e_one). The 38-minute stop rule never
  acted. P7 passed at its low edge in the direction the registration did not expect (it expected random floats about
  0.1 W *above* random bits).

## What it changes

1. **The Horace hub's Status item 6 closes** — answered, with an experiment number. At the same changed-bit and
   carried-one counts, a two-value alternating image is cheaper than random data by **1.636 W** [1.600, 1.671] per
   75 GB/s of DRAM lines (1,395 pJ per 64 B line). **61 % of that is the arrangement** of the ones inside each line,
   which costs at every period; **39 % is the period**, and only a long one: four distinct lines are as cheap as two.
   So the image is "compressible" in the narrow sense of the hub's hypothesis — repetition saves — but the larger
   part of what E75's images missed is where their ones sat.
2. **E75's DRAM reading is refined, not overturned.** Carried ones are the biggest single term: the contiguous
   two-value image at random's own counts is 64 % of the chord, measured directly (E75's 36.6 % left out the
   convex first step from zeros). But a bit-counting model of DRAM energy needs two more terms that E75's design
   held fixed by construction: **where the ones sit inside a line** (+0.81 W at random's counts, 25 % of the chord)
   and **whether consecutive lines on a path differ**, which only a long-period stream makes them do (+0.64 W at
   256/256). Counting ones and the changes between consecutive lines of one stream is not enough.
3. **For the blog material.** The same number of bytes, with the same number of ones and the same number of changes
   from line to line, can cost 1.6 W more to read from DRAM depending only on their pattern — half the 3.2 W
   zeros-to-random range. Random *floats* cost 0.28 W less than random *bits*, because a float's exponent byte
   barely changes. None of it is on the compute rail.
4. **The Levels tab's memory-path row** gains E81's three numbers (the arrangement, the period and the per-event
   account). It does not move the arithmetic waterfall: this is the memory path.
5. **What would settle the mechanism.** Two things, neither run here. A period ladder between 4 and 8,192 lines
   would find where the period effect starts, and so how many ways consecutive lines are spread; the host's `file:`
   operand takes exactly 256 B (four lines), so it needs a host change, registered first. And the card's
   address-to-channel map and data-pin mapping, read from the firmware and driver sources, would test the
   "each path carries every N-th line" inference directly.

## Files

| file | what it is |
|---|---|
| `passes/p8101` | the smoke (`anchor_pi`, `dp_bern`, `dp_s2`), not reduced |
| `passes/p8110`–`p8119` | the ten passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `code.sha256`, `gen.sha256`, `text.sha256`, `manifest.txt`, `run.log` |
| `gen/` | `make_dp.py`'s output regenerated on the Intel: `manifest.json` (the items, their commands and counts, π), `srcs/*.bin` (the eight 256 B images, byte-identical to the box's: every pass's `gen.sha256`), `counts.json` (every count, including the replica's realized counts of `random` and `bern:0.5`) |
| `dp.json` | the reduction at the registered `auto` leakage slope — the result |
| `dp-leak0.2936.json`, `dp-leak0.3803.json` | the two labelled sensitivities |
| `runs.csv` | one row per run: pass, item, launch reading, p_raw, p80, rail, rate, median `took_ms`, gate failures |
| `reduce.sh`, `reduce.txt` | the reduction commands and their printed output |
| `dips.json`, `dp-posthoc-dips.json`, `reduce-posthoc-dips.txt` | **post hoc, labelled** (D1): every board-meter dip and where it falls, and the registered reducer on dip-filtered copies of the passes |
| `ident/` | `ettelem config` at the start and the end of the card session, and `et-lab-manifest` |
| `logs/` | the queue log, the smoke log, the dry run, the box's harness hashes |

Code: `tools/claims-v3/dp/` (`make_dp.py`, `src_replica.cpp`, `run_e81.sh`, `predictions.json`, `reduce_dp.py`,
`README.md` — the registration), with E75's `tools/claims-v3/mf/block.sh`, `queue_mf.sh` and `make_mf.py` and the
runner `tools/claims-v3/runitems.py`, all unchanged.

## Reproducing it

    # on aifoundry3, in ~/aifoundry
    bash tools/claims-v3/dp/run_e81.sh setup
    bash tools/claims-v3/dp/run_e81.sh smoke 8101
    bash tools/claims-v3/dp/run_e81.sh go 8110 10
    # on any machine with the lab repo, numpy and GCC
    g++ -O2 -std=c++17 -o build/dp-replica tools/claims-v3/dp/src_replica.cpp
    build/dp-replica random 1 > build/random.bin; build/dp-replica bern:0.5 1 > build/bern50.bin
    python3 tools/claims-v3/mf/make_mf.py build/mf-gen
    python3 tools/claims-v3/dp/make_dp.py docs/reports/data/2026-10-31-e81-dram-pattern/gen --check --builtins build --e75-gen build/mf-gen
    bash docs/reports/data/2026-10-31-e81-dram-pattern/reduce.sh
    # the labelled post-hoc view (D1)
    D=docs/reports/data/2026-10-31-e81-dram-pattern
    python3 tools/claims-v3/dp/posthoc_dips.py $D/passes/p811? --work build/e81-dipwork --out $D/dips.json
    python3 tools/claims-v3/dp/reduce_dp.py build/e81-dipwork/p811? --gen $D/gen \
      --pred tools/claims-v3/dp/predictions.json --out $D/dp-posthoc-dips.json

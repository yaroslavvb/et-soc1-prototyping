# V3-DP: the DRAM pattern question (E81, Q130)

*Pre-registered Sat 31 Oct 2026 (week 44), 14:3x–15:1x PDT, on the Intel, by the Q130 workflow's aifoundry3 lane.
No card was opened for this file. Frozen at the commit that adds it, before the Discord claim and before the first
measured pass on aifoundry3. Changes after that go in Amendments, dated, before the data they touch.*

## The question

E75 (`docs/reports/data/2026-10-28-e75-memory-flip-ladder/`) priced a carried one and a changed bit on four memory
paths with images built from **two values alternating**, and at DRAM it found that those two designed counts explain
**only 36.6 %** of the zeros-to-random chord (95 % [30.0, 43.3]): random data costs about 1.1–1.2 W more than the
two-term model gives it. E75's registration had named the risk in advance — *"Two values alternating is a maximally
correlated pattern. If the DRAM interface does data-bus inversion or any history-dependent encoding, a 2-cycle is not
random data with the same counts"* — and the Horace hub carries it as Status item 6: **a third image at the same
changed-bit and carried-one counts but a longer period, to test whether a two-value alternating image is compressible
on the link or in DRAM in a way random data is not.**

E75's images differ from random data in **two** ways at once, and this experiment separates them:

| | E75's images | `--operands random` |
|---|---|---|
| **period** — how many distinct lines a hart's stream cycles through | 2 (a b a b …), or 1 at k = 0 | every line of a hart's 2,048-line region is distinct (8,192 in the 512 KB source) |
| **arrangement** — where the ones sit inside a 64 B line | contiguous runs (`two_values()` puts the toggling group at bits 0…k−1 and the static ones right after) | scattered |

Two mechanisms, two predictions:

* **The period (the hub's hypothesis).** A path that sees repeated values pays less: an encoding with memory, a
  compressor, or simply a channel that receives only the even lines of a 2-cycle (if lines interleave across
  channels by address, every line a channel sees is the same value, so no bit on that channel's wide paths ever
  changes). It predicts that a long-period image costs more than a 2-cycle at the same counts, whatever the
  arrangement.
* **The arrangement.** A path narrower than a line moves a line as pieces — LPDDR4x moves a 64 B line over 16-bit
  data pins as beats — and toggles between the pieces of *one* line. Contiguous runs barely toggle it; scattered
  ones toggle it about half the time. It predicts that scattering the ones of E75's own image costs more at every
  period, and that the period costs nothing.

E75's DRAM arms fit either: its k-arm (changes between consecutive lines) is flat and non-monotone, and its w-arm
(ones) is a clean price. E81 decides between them.

## The design

E75's DRAM command, unchanged (`make_mf.args_for("dram", …)`): `enercat_host --pattern flw_pat --harts 1 --seconds 4
--window 240000000 --operands <op> --stride 64 --slice-bytes 131072 --region 131072` — 32 B vector loads 64 B apart,
one 64 B line fetched per load, over 128 KB per hart (128 MB in all, 4× the L3). Same binary (aifoundry3's
`build/enercat-hl/host/enercat_host`, E75's), same block and queue (`tools/claims-v3/mf/block.sh`, `queue_mf.sh`,
run with `MF_GEN=build/dp-gen MF_EXPN=dp`), same runner (`tools/claims-v3/runitems.py`): the approach protocol, the
shuffled order and the drift anchor are E75's.

Every file image is 256 B = four 512-bit lines, repeated by the host through every slice, as in E75 (each hart's
region starts at the image's line 0: slice strides and bank offsets are multiples of 1 KB). The **scattered** images
are the contiguous ones with **one fixed permutation π** of the 512 bit positions applied to every line
(`make_dp.py`, splitmix64 Fisher–Yates, seed 0xE81, π written into the manifest), so a contiguous image and its
scattered twin carry exactly the same counts. The period-4 images use four rows of an order-8 Hadamard design on the
eight 64-bit blocks of a line (01010101, 00110011, 01100110, 00001111), so each line has 256 ones and **any two** of
the four differ in exactly 256 bits — as random lines do, in whatever order a path sees them.

Counts per line, re-derived from the bytes by `make_dp.py --check` over each hart's region in the order `flw_pat`
reads it. For `random` and `bern:0.5` they are the realized counts of the host's own source, rebuilt bit for bit by
`src_replica.cpp` (enercat's `sources()`, seed 1, compiled against GCC's libstdc++ as on the lab hosts):

| item | operand | period (distinct lines) | arrangement | k changed bits between consecutive lines | w ones per line | toggles between consecutive 16-bit pieces, per line |
|---|---|---:|---|---:|---:|---:|
| `dp_zeros` | `zeros` (E75's anchor) | 1 | — | 0 | 0 | 0 |
| `dp_c1` | file = **E75's `mf_dram_k0` bytes** | 1 | contiguous | 0 | 256 | 32 |
| `dp_s1` | file, π(c1) | 1 | scattered | 0 | 256 | 254 |
| `dp_c2` | file = **E75's `mf_dram_k256` bytes** | 2 | contiguous | 256 | 256 | 48 |
| `dp_s2` | file, π(c2) | 2 | scattered | 256 | 256 | 251 |
| `dp_c4` | file, Hadamard rows on 64-bit blocks | 4 | contiguous | 256 | 256 | 72 |
| `dp_s4` | file, π(c4) | 4 | scattered | 256 | 256 | 253.5 |
| `dp_bern` | `bern:0.5` (built in) | 2,048 per hart, 8,192 in all | random bits | 256.12 | 256.02 | 255.9 |
| `dp_c2r` | file, `two_values(512, 4, 192, 290)` | 2 | contiguous | 192 | 290 | 48 |
| `dp_s2r` | file, π(c2r) | 2 | scattered | 192 | 290 | 249 |
| `dp_random` | `random` (E75's anchor) | 2,048 per hart, 8,192 in all | floats in [0.5, 2) | 190.17 | 288.26 | 255.9 |

`dp_c2r` and `dp_s2r` carry random's own counts (rounded to an even k), so `dp_random − dp_c2r` is E75's miss
measured directly, without a model. `counts.json` (written by `--check`) also holds the toggles between consecutive
32-, 64- and 256-bit pieces and the alphabet's pairwise distances, for the derived reading below. Those piece
counts assume an in-order mapping of a line onto a narrow path; they are a covariate for a reading that is reported,
not scored.

Per pass: `anchor_pi` first and last (E75's drift anchor), the eleven DRAM items once each, shuffled; two burn-in
launches before the first. Passes **8110–8119** after a smoke (8101: `anchor_pi`, `dp_bern`, `dp_s2`). **8110 is the
registered warm-up pass**: reduced and reported, never in the headline (E75's lesson 5 — in E74 and E75 the pass set
aside was the first one off an idle card, on drift). Headline: 8111–8119, nine passes, df = 8.

## Frozen predictions (`predictions.json`)

An effect is **present** when its mean is ≥ 0.25 W and its 95 % interval excludes 0, **absent** when its 95 % interval
lies inside ±0.30 W (absent means smaller than 0.3 W, not zero), and **unresolved** otherwise.

| # | contrast | prediction |
|---|---|---|
| P1a | `chord` = random − zeros | **2.65–3.85 W** (E75: 3.250, SE 0.126): the frame replicates |
| P1b | `c2_minus_zeros` = c2 − zeros | **1.30–2.50 W** (E75's k256 rung, the same bytes: 1.933) |
| P1c | `c1_minus_c2` = c1 − c2 | **−0.10 to +0.50 W** (E75's k0 rung sits above its k256 rung: +0.20) |
| P2 | `arr2` = s2 − c2 | **+0.40 to +1.60 W**: scattering the ones of E75's own k256 image costs, at the same counts and period |
| P3a | `arr1` = s1 − c1 | **+0.40 to +1.60 W**: so does it at period 1, where no line ever changes |
| P3b | `arr4` = s4 − c4 | **+0.40 to +1.60 W** at period 4 |
| **P4** | **`period_s` = bern − s2** | **absent**: the hub's question, predicted **no** — random bits with the same mean counts and 8,192 distinct lines cost what a scattered two-value image costs |
| P5 | `resid_r` = random − s2r | **−0.35 to +0.35 W**: a scattered two-value image with random's own counts accounts for random |
| P6 | `gap_r` = random − c2r | **+0.70 to +1.80 W**: a contiguous one with random's counts misses most of the chord, as E75's model did |
| P7 | `random_minus_bern` | **−0.30 to +0.45 W**: random floats and random bits differ only by their counts (32 more ones: about +0.1 W at E75's 3.255 pJ per one) |

**The alternative, registered:** the hub's hypothesis — `period_s` present at about the whole gap (+1.0 to +1.2 W)
and `arr1`, `arr2`, `arr4` near zero. If it holds, P2–P5 fail and P4 fails, and that is the finding.

**The hub's answer is read by rule** (`reduce_dp.py`, `hub.verdict`): `period_s` present and `arr2` not → *the period:
a two-value image is cheaper because it repeats*; `arr2` present and `period_s` not → *the arrangement: the
repetition costs nothing*; both present → both, with their shares of `pattern_total` = bern − c2; both absent →
neither (the gap is then in what separates random floats from random bits, P7).

## Decision rules (registered)

1. **Estimator.** Per kept pass, each item's board power over [t0+1 s, t0+3 s), corrected to the launch reading with
   the leakage slope (p80, `reduce_hl.runs_of_pass`, E60–E75's machinery). Every contrast is a within-pass
   difference; the headline is the mean over the headline passes with a two-sided t interval on their scatter
   (df = n − 1). Watts convert to pJ per 64 B line with the measured line rate (the mean `ops_per_s` of the pass's
   DRAM runs), never an assumed one. The leakage slope is E75's registered `auto` estimator; 0.2936 and 0.3803 W/°C
   are reported as sensitivities.
2. **Run gates, E75's:** one clock; voltage within 3 mV of the pass median; an on-protocol launch within 0.5 °C of
   58 °C after a 59 °C preheat; the window's median telemetry `took_ms` ≤ 60 ms (the meter-starvation gate); an ok
   device record. A failed run is reported and left out.
3. **Pass gates:** `anchor_pi` drift first to last above 0.3 W sets a pass aside; so does a pass in which more than a
   third of its DRAM runs fail a gate. A set-aside pass is reported, never averaged.
4. **Temperature:** preheat 59 °C, launch at the first reading ≤ 58 °C, cap 78 °C, three unreachable runs in a row
   stop the pass (`runitems.py`).
5. **Budget:** at most **45 card-minutes** in all. About 1 min of smoke, then up to ten passes of about 2.5 min. The
   lane touches `build/mf-STOP` when the queue's card time reaches 38 min, so no pass starts after that (a pass that
   has started finishes). If fewer than four headline passes are kept, every verdict is reported as unresolved.
6. **What it changes.** It answers the hub's Status item 6 and says what a bit-counting memory-energy model needs
   beyond E75's two prices: a period term, an arrangement term, both, or neither. It does not move the arithmetic
   ledger (the multiply-add's waterfall).

**Reported, not scored:** every item over zeros (W and pJ per line); the period steps `per_c_2to4`, `per_s_2to4`,
`per_s_4tolong`, `s1_to_s2`; the shares (arrangement and period of `pattern_total`; arrangement and residual of
`gap_r`); the leakage sensitivities; the warm-up pass and the all-healthy-passes view; and a **derived reading**:
each arrangement contrast divided by the toggles it adds between consecutive 16-, 32- and 64-bit pieces of the stream
(`derived_not_scored`) — what a toggle would cost on such a path *if* that path is where the arrangement is paid.
The piece widths stand in for the data pins (16), a 32-bit beat pair and a 64-bit deserialized word; nothing here
says which width the card has, and the reading is labelled as an inference.

## How to run it (aifoundry3, in `~/aifoundry`)

    bash tools/claims-v3/dp/run_e81.sh setup        # images + --check (incl. byte identity with E75's two rungs),
                                                    # operand strings, .text and harness hashes, dry run. No card.
    bash tools/claims-v3/dp/run_e81.sh smoke 8101   # one short real block (about 1 min of card time)
    bash tools/claims-v3/dp/run_e81.sh go 8110 10   # the detached queue; log build/e81-dp.log
    bash tools/claims-v3/dp/run_e81.sh status       # passes, block.json, card minutes

Stop between passes: `touch ~/aifoundry/build/mf-STOP`. Data in `build/claims-v3/aifoundry3/dp/p<pass>/`; collected
into `docs/reports/data/2026-10-31-e81-dram-pattern/` and reduced there with `reduce.sh` (this directory's
`reduce_dp.py`, the three leakage settings).

## Risks, and what each one does to the result

- **The meter starves on DRAM bursts** (14-card-behaviour.md; E75's rule 3): E75's worst window median was 22 ms
  against the 60 ms gate. Kept.
- **`bern:0.5` matches the counts in expectation, not exactly**: 256.12 changes and 256.02 ones per line on average,
  with a binomial spread of about 11 bits per line. E75's DRAM response to ones is near-linear around 256 (its w-arm),
  so a ±11-bit spread moves nothing measurable; the means are 0.1 % from the file images'.
- **Period 4 may not be long enough** to break whatever a short period buys (if lines interleave over more than four
  channels, every channel can still see a single value). That is why `dp_bern` (8,192 distinct lines) decides the hub's
  question and `dp_s4` is a step on the way, reported, not scored.
- **The scattered images change more than the 16-bit toggles**: they also change the toggles between 64-bit and
  256-bit pieces (the contiguous Hadamard lines toggle *more* at 64 bits than their scattered twins: 288 against
  252.5). The derived reading reports all three widths so the arrangement effect can be read against each.
- **The first pass off an idle card is transient** (E74, E75): pass 8110 is the registered warm-up.
- **Another user, or the demo service on aifoundry3**: `mf/block.sh` stops on another user's device process or lock
  (departure D1 of `hl/README.md`: an idle login does not block), holds `/run/lock/etsoc-shire0.lock`, and caps every
  device process at `timeout 10`.
- **Nothing is set on the card**: no governor, TDP, threshold or clock write; `ettelem config` is read, read-only,
  under the lock with `timeout 10`, at the start and the end of the card session.

## Files

| file | what it is |
|---|---|
| `make_dp.py` | the eight file images, the eleven item commands, π, and every count; `--check` re-derives them from the bytes, `--e75-gen` checks `dp_c1`/`dp_c2` against E75's rungs, `--builtins` counts the replica's `random` and `bern:0.5` sources |
| `src_replica.cpp` | enercat's `sources()` for `random` and `bern:P`, bit for bit (build with GCC) |
| `run_e81.sh` | `setup` / `dry` / `smoke` / `go` / `status`, through E75's `mf/block.sh` and `mf/queue_mf.sh` unchanged |
| `predictions.json` | the predictions and decision rules above, frozen with this commit |
| `reduce_dp.py` | the registered reduction, written and tested before the first pass (on E75's passes relabelled: a pipeline test, not data) |

## Amendments

*(none yet)*

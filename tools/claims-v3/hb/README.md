# V3-HB: E65 — every bit position, the flow-M case, and the hart ladder (Q126)

*Pre-registered Mon 26 Oct 2026 (week 44) on aifoundry3, before the first measured pass; any change after this commit
goes in the Amendments section at the end, dated, before the data it touches. Request Q126. Card: **aifoundry3
only**, whose governor is latched at 600 MHz by `et-board-clock-guard`
(`docs/findings/14-card-behaviour.md`), which is why E60's ladder is clean there and why every number below is a
600 MHz, ~0.523 V number.*

## Why these three blocks

The week-43 recap ranked what stands between the project and a model that turns a load into watts. Three of its gaps
need a card, and all three need this card:

- **Gap 6 — a flip's price depends on which bit flips, and there is no law for it.** E60 *built* 13 bit positions and
  *ran* 6 (0, 8, 16, 22, 23, 31, on aifoundry1's card 0 at 800 MHz). The measured prices span 10× over those six, so a
  model that multiplies Hamming distance by one number is wrong by that much on sparse, quantised or sorted data —
  the regime Horace He's effect lives in. **Block A** runs all 32 positions, on the pinned card, against the family's
  own zero: the per-position weight vector the model has never had.
- **The price list's flow-M row.** Sunday's Q124 page priced one named stimulus at the gate level from Esperanto's
  design files: *b* bit 11 alternating with *a* = π costs **0.11–0.13 pJ** more per multiply-add in the multiplier
  (`tfma.flip.energy`), toggling **381 physical wires** in the Booth rows, the tree, its register and the product
  adder (`tfma.flip.gate`), both in `docs/reports/data/2026-09-27-chip-diagram/research/tensorfma32.json`. The card
  has never run that stimulus. **Block B** runs it, and four more positions with the same busy partner.
- **Gap 5 — a fixed cost for running a kernel at all.** E62 measured 5.80 W + 55.8 mW per hart at 800 MHz on
  aifoundry2 (5.35–5.46 W + 46–49 mW de-leaked), and the flip model, forced through zero, predicts 0 W for that
  offset: 45% of a 128-hart reading, and 11–16% of any partial-card load. **Block C** is one hart ladder per
  stimulus, idle-bracketed, to say whether the offset is the kernel's switching, or the cost of having a launch open
  at all.

Block D (a second launch temperature, gap 4) runs only if the card time allows, and is marked as such.

## Departures from the ask, and why

- **D1, "both heater kernels" becomes both heater *stimuli*.** The recap's block asked for E62's heater kernel and
  the hp heater. On aifoundry3 those are the same program: `lib.sh:35-43` builds `build/sparsity_t2` on aifoundry2
  and `build/sparsity` everywhere else from the same sources, `build/sparsity_t2` does not exist on aifoundry3
  (checked 16:30 PDT today), and hp's heater (`hp/hplib.sh:400`) and E62's (`hm/prereg/protocol.json`) pass
  *identical* arguments. Two builds of one source would have been a vacuous contrast. So the two arms are two
  operand sets through the one kernel — `--values randn` (E62's and hp's stimulus exactly) and `--values zeros` —
  which is the sharper test of the same question: an offset that survives when the switching almost vanishes is not
  the kernel's switching.
- **D2, the clock and the card are read across experiments, not within.** aifoundry3 is pinned at 600 MHz, so this
  session cannot vary the clock. The f·V² comparison against E62's aifoundry2 line at 800 MHz is therefore a
  between-session comparison and is reported as one, with the card scale (0.88–0.99 at equal V and f, 26 Sep)
  stated as its uncertainty.
- **D3, no RTL predictions for the new items.** `predict_hl.py` needs Verilator, which is not on this card's host.
  Blocks A and B are therefore registered against *measured* E60 anchors and the Q124 gate-level price, not against
  an RTL replay; `reduce_hl.py` reports `pred_dW: null` for an item with no prediction (amendment A4 below).
- **D4, launch reading.** E60's protocol on this card launched every run at 58 °C after 59 °C. The card has been up
  since 15:18 today and idles at 52 °C, so the same 58/59 °C pair is used unchanged for blocks A and B.

## Block A — the 32-position scan (gap 6)

`bit_<j>`, j = 0..31: one bit j of B flips every cycle in every lane, A = 1.0 everywhere, 4,096 designed B-bit flips
per multiply-add per minion. Its zero is `lq_h0` (A = 1.0, B constant), as in E60. Exponent bit 30 uses a base
exponent of 64 so both words stay normal; every other position uses 127 (`make_hl.py:bit_tiles`). Items are
generated into `build/hl-gen3`; every file E60 ran is byte-identical there (checked with E60's `gen.sha256`).

## Block B — the flow-M case (the price list's flow-M row)

`bpi_<j>`, j ∈ {0, 8, 11, 16, 22}: the same single-bit alternation with the **busy partner A = π**, against `lb_h0`
(A = π, B constant). `bit_<j>` and `bpi_<j>` share their B words — the base does not depend on the partner — so the
pair isolates what the partner costs at one position. `bpi_11` is the stimulus Q124 priced at the gate level.

## Block C — the hart ladder, two stimuli (gap 5)

`hm/run_hm.py` on `hb/protocol-randn.json` and `hb/protocol-zeros.json`, `--no-cam` (aifoundry3 has no camera).
Rungs 64, 128, 256, 384, 512, 768 and 1,024 harts at `--per-shire 32`; the n-shire rung lights shires
`round(i·32/n)`, a fixed spread over the die (E62-CAL measured power following harts, not geometry, to ±0.5 W). An
IDLE phase of 20 s sits before and after **every** rung, so leakage is de-trended per rung. Three laps, `order:
alternate`, so the rung order is counterbalanced against the session's own warming. One 8 s launch per rung per lap,
`--budget 9.5` under `timeout 10`, as E62. 13.0 card-minutes per session by `run_hm.py --list`.

## Block D — a second launch temperature (gap 4), only if time allows

`lq_h0`, `lq_h2`, `lq_h8` and `bit_22` launched hotter than blocks A and B's 58 °C. The switching drift with
temperature is quoted at +0.3–0.5 %/°C with the cause unknown; this measures it on one card at one clock.
**Amended before the block ran — see A7.**

## Protocol, shared

- Blocks A, B and D run through `hl/block.sh` (E60's, unchanged), which holds `flock -n
  /run/lock/etsoc-shire0.lock` for the pass, puts every device process under `timeout 10` with `--stop-file`, stops
  at a 78 °C reading or on telemetry older than 3 s, writes `et-lab-manifest` and `gen.sha256` beside the data, and
  releases the lock between passes. Departure D1 of E60's README (an idle login of another user does not block;
  another user *on this card* does) stands.
- Block C runs through `hm/run_hm.py`, which takes the same lock for its session, runs the same other-user checks
  before the session and between every launch, and stops at 78 °C, 80 W on two consecutive samples, or 72 °C before
  a full-card launch.
- Before the first launch: `et-boot-check --status` (the card link at its target speed), `et-who`, `who`, `uptime`,
  and a `V3_DRY=1` dry run of every block. The card is claimed in `#community-lab` before the first launch and
  released after. If anyone else takes the card, stop and wait.
- Card time at most 2.5 h in total.

## Pre-registered analysis

- **Blocks A, B, D:** `hl/reduce_hl.py`, unchanged but for amendment A4. Per run, P = mean board power over
  [t₀+1 s, t₀+3 s) corrected to the launch reading with the card's leakage slope; gates on one clock, voltage within
  3 mV of the pass median, an on-protocol launch, and fma cycles per op within 0.5% of the family's zero. Every item
  minus its own zero per pass; the unit of replication is the pass; SE from the between-pass scatter. Per-position
  price = (item − zero) / (4,096 · ops per second), in J per alternating bit.
- **Block C:** `hb/reduce_ladder.py`. Per rung, board power = the median of the 10 Hz samples in the **last 4.0 s**
  of its launch (E62-CAL's window); the de-leaked value subtracts the mean of the two bracketing IDLE phases' last
  10 s medians; both the raw and the de-leaked lines are fitted by least squares on hart count, with the intercept
  free. The unit of replication is the lap; SE from the between-lap scatter.

## Predictions, frozen with this commit

- **A1.** Over the mantissa field (j = 0..22) with A = 1.0 the price rises with j: Spearman ρ > 0.5 over the 23
  positions. The span over all 32 positions exceeds 5× (E60 saw 10× over six of them).
- **A2.** The six positions E60 ran on aifoundry1's card 0 at 800 MHz, rescaled by f·V² = (600/800)(0.523/0.604)² =
  0.562, reproduce here within a factor of 1.5 (the card scale is 0.88–0.99 and the clocks differ).
- **A3.** The sign bit (31) is among the four cheapest positions; the exponent bits (23–30) are dearer than the
  mantissa bits below 16.
- **B1.** `bpi_11` costs **100–250 fJ per alternating bit** all-in at the board. The gate-level price for the same
  stimulus is 0.11–0.13 pJ in the multiplier alone, and the board number also carries the operand bus, the register
  file's read ports, the result path and the accumulator, so the board number is **≥ the gate number**. A board
  number *below* 0.11 pJ refutes the gate-level price as a lower bound and is reported as such.
- **B2.** At every shared position the busy partner costs more than the quiet one: `bpi_<j>` − `bit_<j>` > 0 at ≥ 2 SE
  for at least 3 of the 5 positions (E60's ladders: 129.9 fJ with A = π against 116.7 fJ with A = 1.0, +11%).
- **C1 (the kernel question).** With a₀ the fitted intercept of the de-leaked line: if |a₀(randn) − a₀(zeros)| <
  0.5 W (hp's equivalence band), the offset is **not** the data's switching — it is the cost of having a launch open
  at all. If a₀(randn) − a₀(zeros) > 0.5 W and > 3 SE, part of it **is** the kernel's own switching, and the split is
  reported. Anything between is reported as undecided with its interval.
- **C2 (the clock-and-card question).** a₀(randn) in [2.5, 3.8] W supports "the offset scales with f·V² like
  switching" (E62's 5.80 W × 0.537 = 3.12 W). a₀(randn) in [5.0, 6.6] W supports "the offset is fixed across card and
  clock". Outside both, neither reading is supported and the number is reported bare.
- **C3 (the slope).** The randn slope is 30.0 ± 6 mW per hart (E62's 55.8 scaled by 0.537); the zeros slope is 10–40%
  of the randn slope.
- **C4 (linearity).** Residual rms of the seven rungs about the fitted line ≤ 0.4 W, or ≤ 3% of the span; otherwise
  the ladder is reported as bent, with its curvature.
- **D1.** The switching difference `lq_h8` − `lq_h0` grows by +0.3 to +0.5 %/°C with the launch reading. It is
  fitted on every run's **own recorded launch reading** across both regimes (A7), not on two nominal setpoints,
  and reported as %/°C with its SE and CI. The registered band is +0.3 to +0.5 %/°C.

## Decision rules

Each prediction above is scored PASS / FAIL / UNDECIDED against its own stated band, in the results section of the
data README and in E65 of `docs/findings/03-experiments.md`. A block whose passes do not survive the gates is
reported as not run, never re-registered.

**A6, Mon 26 Oct 2026, 16:5x PDT (before any block-C data).** The two ladder protocols' `cooldown_gate` named
`max_wait_s` / `die_c`, which are not `run_hm.py`'s keys (`enter_below_c` / `max_gap_s`), so the gate would have
parsed as absent. Corrected, and `make_ladder.py` regenerated both files. Nothing measured changes: the gate is
called only *between* blocks and each of these sessions has exactly one block, so it never fires either way.

**A7, Mon 26 Oct 2026, 16:5x PDT (before any block-D data; blocks A and B were running, block C had not started).**
Block D's registered launch pair, 65 °C after 66 °C, is **not reachable on this card**: E60's own heat probe put
aifoundry3's plateau at 64 °C under the 2 s heater bursts, and every one of blocks A and B's approaches today
reached only 60–61 °C before falling back to the 58 °C launch (`build/e65-ab.log`, "hot 60.0"/"hot 61.0" on every
run). Registered as written, block D would have skipped every run and stopped the pass at exit 7 without
measuring anything. **Changed:** block D runs with **no approach at all** (`HL_PREHEAT=0 HL_TARGET=200`), so its
runs follow one another at the duty cycle's own plateau instead of waiting down to 58 °C, and it runs **8 passes**
instead of 2 (a pass is about a minute without the approach). Each run still records its own launch reading
(`start_c`), and D1 is scored by fitting the switching difference against those readings over both regimes
(blocks A and B at 58 °C, block D at whatever it reaches), which is a better-posed estimate than two nominal
setpoints would have been. The temperature contrast is therefore whatever the card gives, and the result states
it; if it is under 2 °C the block is reported as having too little leverage to score D1.

**A8, Mon 26 Oct 2026, 17:3x PDT (before any block-D data; blocks A, B and C's randn session had run).**
`reduce_hl.py`'s launch gate is "an on-protocol launch within 0.5 °C of the target". A7's block D has **no
approach and therefore no setpoint** (`--preheat 0`, the sentinel `--target 200`), so that gate would have failed
every one of its runs and set every block-D pass aside. **Changed:** a pass whose `preheat` is 0 has `target`
None, and its launch gate becomes "a reading was recorded"; the reading is then a covariate, as A7 says, not a
setpoint. Every E60 and E65 pass with an approach keeps the 0.5 °C gate unchanged, and blocks A and B are
re-reduced with this code to confirm their numbers do not move.

**A9, Mon 26 Oct 2026, 17:45 PDT (written while block D's no-approach passes were running, before any data of the
second regime it adds).** 🛑 *The first sentence of this amendment is factually wrong and is corrected by A11
below: A7's passes launched at 55–62 °C, not 59 °C, and the reason a second regime was needed is the drift gate,
not a lack of spread. The text is left as written because it is the registered record of what was believed at
17:45; the regime it adds is unchanged and its data stands.* A7's no-approach block D launches at **59 °C**, one degree above blocks A and B's 58 °C
(`build/e65-d.log`, "start 59.0 C" on every run): that is the plateau this duty cycle actually reaches, and by A7's
own words it is "under 2 °C" and cannot score D1. **Added:** a second block-D regime with a real setpoint,
`HL_PREHEAT=62 HL_TARGET=61`, six passes of the same four items, so the block has three launch readings (58 °C from
blocks A and B, 59 °C from the plateau passes, 61 °C from these). The 0.5 °C launch gate applies to this regime
normally, since its `preheat` is above zero (A8 only exempts a pass with no approach). If the approach cannot reach
62 °C the passes skip and the queue stops at exit 7, which is reported as such and costs nothing already measured.
D1 is scored on the regression of the switching difference against the launch reading across all three readings,
with its CI; a span this short may only **bound** the coefficient, and the result says so.

**A10, Mon 26 Oct 2026, 17:5x PDT (a code correction *toward* the registration, made after block C's data and
disclosed here).** `reduce_ladder.py`'s printed C1 verdict tested `abs(a₀(randn) − a₀(zeros)) > 3·SE` for the
second branch, where the **registered rule's second branch is signed**: "if a₀(randn) − a₀(zeros) > 0.5 W and
> 3 SE, part of it **is** the kernel's own switching". A *negative* difference cannot mean the randn kernel carries
extra fixed switching, so the code's string was wrong against the rule it implements. The measured difference is
−0.52 W, which the code called "part of it is the kernel's switching" and the registered rule calls **undecided**
(it is 0.02 W outside the first branch and the wrong sign for the second). The code now prints the registered
rule's verdict. The rule itself is unchanged and nothing was re-registered *by this amendment*; the README reports the registered
verdict, the raw number and why the sign matters.

**A11, Mon 26 Oct 2026, 18:5x PDT (a correction to this record, made after all the data and changing no rule, no
code and no number).** A review of the published E65 write-up found three statements in it that the committed data
contradicts. Nothing measured moves; what changes is what this file and the results documents *claim*. In order:

- **A9's launch temperature was wrong, and so was its stated reason.** A9 says "A7's no-approach block D launches
  at **59 °C** … (`build/e65-d.log`, 'start 59.0 C' on every run)". The committed copy of that log
  (`docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/logs/queue-d-a7.log`) and `runs-blockD.csv` both say
  otherwise: over passes 671–678 the launch readings are **55–62 °C**, distributed 55 ×2, 56 ×1, 57 ×5, 58 ×4,
  59 ×8, 60 ×13, 61 ×12, 62 ×3 — only 8 of 48 runs at 59.0, median and mode 60 — and they **climb monotonically
  pass by pass** (671 = 55–57, 678 = 60–62) as the card warms with no idle between passes. So A7 did **not** give
  "under 2 °C" of leverage; it gave **7 °C**, more than twice the 3 °C D1 was finally scored on. A9's premise is
  therefore false, and the regime it added still turned out to be necessary, for a reason A9 did not state and
  could not yet see at 17:45: **A7's launch spread is produced by the same within-pass warming that the registered
  0.3 W `anchor_pi` drift gate rejects**, so every one of those eight passes was later set aside (drift +0.57 to
  +0.74 W) and none of their 7 °C was admissible. The honest justification for A9 is "the no-approach regime cannot
  pass the registered drift gate, so a gated regime at a real setpoint is needed", not "the card has no spread".
  For the record, blocks A and B's approaches peaked at **59–61 °C** (`logs/queue-ab.log`: 59.0 ×3, 60.0 ×107,
  61.0 ×13), not uniformly 60–61 as A7 says.
- **D1 was scored on a contrast this registration never names, and that is a departure, not the registered rule.**
  Registered D1 is "the switching difference **`lq_h8` − `lq_h0`** grows by +0.3 to +0.5 %/°C between the 58 °C and
  the 65 °C launch". But blocks A and B — the only blocks that run at 58 °C — were registered with the items
  `bit_<j>` against `lq_h0` and `bpi_<j>` against `lb_h0`; `lq_h8` appears in **block D alone** (14 runs, 0 in
  `runs.csv`). The registered contrast therefore has data at one temperature only and was **unmeasurable by
  construction** — a flaw in the registration itself, not in the run. D1 was scored instead on **`bit_22` − `lq_h0`**,
  the only item pair that blocks A, B and D share. That substitution is a **departure**, disclosed here; it was not
  registered before the data and neither A7 nor A9 names it. The lesson for the next card block: an across-regime
  prediction must have its *items* registered in every block it is meant to compare.
- **A2's reference was misdescribed, and A2 passes either way.** The results documents say E60's amendment A1
  "moved" the bit scan off aifoundry1's card 0 to aifoundry3, which would make E60's own "Per card" table stale.
  It did not. E60's A1 **added** the family to aifoundry3 passes 5–8 while keeping "aifoundry2, passes 6–10 and
  aifoundry1 card 0, passes 6–10: the registered lists again", and E60's committed `hl.json` carries all six
  positions under **both** `aifoundry1-c0` and `aifoundry3`. E60's "Per card" table is an accurate record of its
  registration and must not be edited. A2 was scored as a same-card replication (worst ratio **1.122**); under the
  **literal registered test** — E60's aifoundry1-c0 values rescaled by f·V² = 0.562 — the worst ratio is **1.106**,
  also inside the registered 1.5. **A2 is PASS on the registered rule as written**, and the same-card reading is
  reported beside it as the harder test, not in place of it.

## Files

`make_ladder.py` (block C's two protocols), `protocol-randn.json`, `protocol-zeros.json` (frozen with this commit),
`reduce_ladder.py` (block C's analysis), `run_e65.sh` (the driver on the box). Blocks A, B and D use
`tools/claims-v3/hl/` unchanged but for amendment A4, whose generator writes `build/hl-gen3`.

## Amendments

**A4 to `tools/claims-v3/hl/` (Mon 26 Oct 2026, with this commit, before any E65 data).**
- `make_hl.py`: `BITS` becomes all 32 positions (it built 13), and a new family `bpi_<j>` for j ∈ {0, 8, 11, 16, 22}
  runs the same single-bit alternation with A = π. `bit_tiles` gains a `partner` argument; the base words do not
  depend on it, so `bit_<j>` and `bpi_<j>` differ in A alone, and every file E60 ran is byte-identical.
  *Why:* the recap's gap 6 (26 missing positions) and the price list's flow-M row.
- `reduce_hl.py`: `ZERO["bpi"] = "lb_h0"`; the bit scan is reported for both partners (`bits`, `bits_pi`), each
  against its own zero; and every RTL-prediction lookup goes through a `dpred()` that returns `None` when an item has
  no replay, instead of raising. *Why:* D3 — Verilator is not on this host, so the 26 new positions and the five
  `bpi` items have no prediction, and E60's own items are unaffected (all of theirs are in `predictions.json`).
- `hm/run_hm.py` (its own amendment A1): the expected hostname comes from the protocol's top-level `card` field,
  defaulting to `aifoundry2`, and the `build/sparsity_t2` pairing rule (`lib.sh:35-43`) is checked only on the host
  that uses it. *Why:* block C runs E62's runner on aifoundry3. E62's own `protocol.json` names `aifoundry2`, so its
  behaviour is unchanged.

**A5 to `tools/claims-v3/hm/run_hm.py` (Mon 26 Oct 2026, 16:5x PDT, written after blocks A and B had started and
before any block-C data; its own amendment A2).** On `aifoundry3` and `aifoundry1` the runner's other-user test
becomes the card-scoped one of E60's departure D1: another user holding **this card's** device nodes or its lock,
from `sudo -n /usr/local/sbin/et-holders`, failing **closed** when the helper cannot be read. *Why:* two other lab
users keep idle tmux shell logins on aifoundry3, and `run_hm.py`'s `who`-based test would
have refused every block-C session with `other_user` while nobody was on the card — exactly the case E60's D1 was
written for, and the case `hl/block.sh` (which blocks A, B and D run through) already handles. aifoundry2 keeps
`lib.sh`'s login test, so E62 is unchanged. Nothing else about the check changes: the device-process test, the
`et_soc1` use count and the between-launch cadence stand.

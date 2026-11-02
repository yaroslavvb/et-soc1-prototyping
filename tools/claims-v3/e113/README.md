# E113: the A side's form — two layouts at fixed Hamming weight (Q133, aifoundry3 card 0, 600 MHz)

*Pre-registered Sun 1 Nov 2026 (week 44, times PST) on the Intel, before the Discord claim and before any card has run a new tile,
in Q133's run. Any change after this commit goes in Amendments at the end, dated, before the data it touches. Card: **aifoundry3
card 0 only**, whose governor is latched at 600 MHz by its boot-time TDP 0 — the card, clock, voltage and launch protocol of E65's B
price list, E67's A price list and E70's saturation ladder, so every number here adds to theirs without a conversion. E113 writes
no knob: no governor move, no TDP, threshold or clock set, no reset, no `--reset-ms`, no PMIC command; `ettelem config` is read,
read-only, under the card lock with `timeout 10`, at the session's start and end.*

**What it answers.** A carried item: **the A side's saturating form**. E70 rejected it, and the final critic's item 13 listed it as
not touched (the Horace hub's Status keeps that list). Section 11 of the kinds page as it read at `1fe8377a18af`
([horace-kinds-of-numbers § 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)) has no line of
its own for it: it falls under **item 15, "Smaller, and carried"**, and it bears on **item 6**'s clause "the A side … ladders
0.86–0.90 post hoc" (the power model misses the A-side ladders). Beside it: E78's C2, *the broadcast A word's weight is
unvalidated*, which E113 tests for an ungated fp32 lane only (below).

## The question

E70 ran the A side's multi-bit ladder in **one layout** (`alq_h<k>`: A's low k mantissa bits flip together, B = 1.0, the quiet
partner) and found that one saturating curve in A's own additive sum does not describe it: fit rms 1.063 W (4.6× the B side's
0.232 W), residuals systematic to 84 SE, increments that accelerate (+0.38, +1.53, +2.23 W at k = 8, 12, 16) where saturation
needs them to decay, and a fitted asymptote (6.37 W) 1.19 W, **28 SE below the ladder's own top rung** (`alq_h23`, 7.560 ± 0.042
W). On the B side the same law was decided by the one knob E70 turned there and not on A: **the layout of the flipping bits at
fixed Hamming weight** (`lq` low against `ls` spread, +3.860 ± 0.052 W at h = 8, 74 SE). E113 turns that knob on the A side.

A is the operand the multiplier **Booth-recodes** (E67's README; `txfma_f1.v` wires the recoder's `mplr` to `fa`), broadcast to all
eight lanes, where B feeds the partial-product muxes per lane. So it is not given that A's sub-additivity follows B's. Four questions:

1. **Does the layout matter on A?** At the same k, do spread bits cost more than low bits, as on B ("which bits"), or the same
   ("how many")?
2. **Is there an A-side saturating form?** Does one saturating curve in A's additive sum S_A collapse **both** A layouts — E70's
   question, now with the second layout that decided it on B?
3. **Or does an A mask cost a fixed fraction of the same mask flipped on B?** With the partner held at 1.0 the **product is the
   flipping operand**, so everything after the multiplier sees the same bit pattern whichever side flips (A at half the rate), and
   Q132(b)'s bench puts most of a bit's position dependence after the multiplier (a high mantissa bit 20× a low one's toggles there,
   2.1× inside it; `docs/reports/data/2026-11-01-q132-rtl-bench/README.md` § 3, bit 22 against bit 4, and `counts-hl.json`). Post hoc on E70's published
   numbers, `alq_h<k>` ≈ 0.643 × `lq_h<k>` fits E70's seven A rungs to **0.300 W rms**, against the A-side curve's 1.063 W. That
   was seen before this registration, on E70's low layout only; E113's spread layout is out of sample for it.
4. **The A word's weight against B (E78's C2, for an ungated lane).** ρ(8), the price per designed A bit (counted per lane slot,
   2,048 per multiply-add per k) over the price per designed B bit (4,096 per k), at the same mask, in both layouts, with the B rungs
   run in the same passes. Counted once per broadcast word instead, an A bit would have to cost about 8× a per-slot B bit.

## Design

One item list, one pass, so both A layouts, both zeros, the B ties and the random anchors share each pass's offset (24 runs after
two unrecorded burn-in runs of `anchor_pi`; `items_e113.sh`):

```
anchor_pi, aq_h0, alq_h1, alq_h2, alq_h3, alq_h4, alq_h6, alq_h8, alq_h12, alq_h16, alq_h23,
als_h2, als_h3, als_h4, als_h6, als_h8, als_h12, als_h16, lq_h0, lq_h8, ls_h8, nrd_a, nrd_b
```

- `alq_h<k>` — E70's low layout; `alq_h3` and `alq_h6` are new, so both layouts have every k in 2…16.
- `als_h<k>` — **new**: A's k flipping bits **spread evenly** over the 23 mantissa positions by `make_hl.spread_mask(k)`, the mask
  E70's B-side `ls_h<k>` used. At k = 23 the spread mask is the low mask, so `alq_h23` is both layouts' top rung, out of every fit.
- Every A item shares E67's one A base word (`make_hl.a_base_words`), alternates it with base ⊕ mask down the A rows (A flips every
  second micro-op, 2,048 designed bits per multiply-add per k), B = 1.0, and is read against `aq_h0` (A constant, B = 1.0).
- `lq_h0`, `lq_h8`, `ls_h8` — the B side at h = 8 in both layouts, for ρ(8) and a tie to E70's D1 (3.860 W).
- `nrd_a`, `nrd_b` — one side random fp32, the other 1.0 (E67's), for a random-word check of the A/B ratio.
- `make_e113.py` writes make_hl.py's whole set unchanged and adds the nine new tiles (`build/hl-gen6-e113`); `setup_e113.sh` checks
  on the box that every file of `build/hl-gen5` (E70's set) is byte-identical in it. On the Intel, 12 of 12 files this list shares
  with E70 match the sha256 E70's pass 790 recorded (`gen.sha256`), and on aifoundry3 (setup, 16:00 PST) 167 of 167 files of
  `build/hl-gen5` are byte-identical in `build/hl-gen6-e113`. The nine new tiles' sha256 are frozen in `new-tiles.sha256`; the box
  generated the same nine.

## The laws, and what each predicts (frozen in `predictions-e113.json` by `predict_e113.py`)

`S_A(m)` is the sum of E67's A single-bit prices over the mask m (`docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json`
`cards.aifoundry3.a_bits`). Every constant is from E70's registered reduction (`…/2026-10-27-e70-saturation-ladder/scored.json`).

| | law | form | constant (frozen) |
|---|---|---|---|
| **A** | additive | ΔW = S_A(m) | none |
| **H** | "how many" | ΔW(`als_h<k>`) = ΔW(`alq_h<k>`): D1_A(k) = 0 | none |
| **WA** | E70's A-side curve | ΔW = W (1 − e^(−S_A/W)) | W = 6.373 W, E70's pooled A fit (the form it rejected) |
| **M** | the mirror | ΔW = c × ΔW of the same mask flipped on B (E70's `lq_h<k>` for `alq_h<k>`, `ls_h<k>` for `als_h<k>`) | c = 0.6433, through the origin on E70's seven `alq` rungs against its `lq` rungs |

| item | layout | k | flipping A bits | S_A (W) | law A | law WA (6.37 W) | law M (c · B rung) | B rung, E70 | E70 measured |
|---|---|---|---|---|---|---|---|---|---|
| `alq_h1` | low | 1 | 0 | 0.459 | 0.459 | 0.443 | 0.390 | `lq_h1` 0.606 | 0.282 ± 0.070 |
| `alq_h2` | low | 2 | 0–1 | 1.599 | 1.599 | 1.414 | 0.597 | `lq_h2` 0.928 | 0.829 ± 0.097 |
| `alq_h3` | low | 3 | 0–2 | 2.072 | 2.072 | 1.769 | 0.832 | `lq_h3` 1.294 | — (new rung) |
| `alq_h4` | low | 4 | 0–3 | 3.150 | 3.150 | 2.485 | 0.968 | `lq_h4` 1.505 | 1.578 ± 0.017 |
| `alq_h6` | low | 6 | 0–5 | 4.209 | 4.209 | 3.081 | 1.516 | `lq_h6` 2.357 | — (new rung) |
| `alq_h8` | low | 8 | 0–7 | 5.784 | 5.784 | 3.801 | 2.089 | `lq_h8` 3.248 | 1.957 ± 0.070 |
| `alq_h12` | low | 12 | 0–11 | 9.025 | 9.025 | 4.826 | 3.539 | `lq_h12` 5.502 | 3.482 ± 0.016 |
| `alq_h16` | low | 16 | 0–15 | 15.913 | 15.913 | 5.848 | 5.381 | `lq_h16` 8.364 | 5.709 ± 0.136 |
| `alq_h23` | low | 23 | 0–22 | 32.852 | 32.852 | 6.336 | 7.813 | `lq_h23` 12.145 | 7.560 ± 0.042 |
| `als_h2` | spread | 2 | 0,12 | 1.429 | 1.429 | 1.280 | 1.342 | `ls_h2` 2.085 | — (new rung) |
| `als_h3` | spread | 3 | 0,8,15 | 3.279 | 3.279 | 2.563 | 2.225 | `ls_h3` 3.459 | — (new rung) |
| `als_h4` | spread | 4 | 0,6,12,17 | 3.923 | 3.923 | 2.930 | 2.848 | `ls_h4` 4.427 | — (new rung) |
| `als_h6` | spread | 6 | 0,4,8,12,15,19 | 7.264 | 7.264 | 4.334 | 3.786 | `ls_h6` 5.885 | — (new rung) |
| `als_h8` | spread | 8 | 0,3,6,9,12,14,17,20 | 9.743 | 9.743 | 4.991 | 4.573 | `ls_h8` 7.108 | — (new rung) |
| `als_h12` | spread | 12 | 0,2,4,6,8,10,12,13,15,17,19,21 | 15.715 | 15.715 | 5.832 | 5.719 | `ls_h12` 8.890 | — (new rung) |
| `als_h16` | spread | 16 | 0,1,3,4,6,7,9,10,12,13,14,16,17,19,20,22 | 22.477 | 22.477 | 6.185 | 6.271 | `ls_h16` 9.749 | — (new rung) |

**D1_A, the matched-k layout contrast** (spread − low, paired per pass; the zero cancels):

| k | S_A spread − low (W) | law A | law H | law WA | law M | the B side's own contrast, E70 |
|---|---|---|---|---|---|---|
| 2 | −0.170 | −0.170 | 0 | −0.134 | +0.745 | +1.158 |
| 3 | +1.207 | +1.207 | 0 | +0.794 | +1.393 | +2.165 |
| 4 | +0.773 | +0.773 | 0 | +0.444 | +1.880 | +2.922 |
| 6 | +3.055 | +3.055 | 0 | +1.254 | +2.270 | +3.528 |
| 8 | +3.959 | +3.959 | 0 | +1.190 | +2.483 | +3.860 |
| 12 | +6.691 | +6.691 | 0 | +1.005 | +2.180 | +3.388 |
| 16 | +6.564 | +6.564 | 0 | +0.337 | +0.891 | +1.385 |

ρ(8), A over B per designed bit at the same mask: law M 1.29 in both layouts; law WA 1.40 (spread); law A 2.74 (spread); law H 0.55
(spread); E70 measured 1.205 (low).

**What the design can and cannot separate.** On the spread rungs alone the frozen M and WA predictions differ by at most 0.55 W
(`als_h6`), so P3 below does not tell M from a curve in S_A; it tests M out of sample. **The low layout separates them** (WA
over-predicts E70's `alq_h8` by 1.84 W, M by 0.13 W), which is why the verdict on the form (P4) reads both layouts together, with each
one-parameter law refitted on E113's own rungs. The self-test (`selftest.txt`) scores three synthetic truths through the registered
code: a mirror truth reads P1 PASS, P2 REJECTED, P3 PASS, P4 "which bits" with c refitted to 0.6499 against 0.65; a "how many" truth
reads P1 FAIL and P4 "how many"; a curve-in-S_A truth reads P2 ACCEPTED with W refitted to 6.01 against 6.0.

## Predictions and decision rules (scored by `score_e113.py`, every contrast paired per pass)

| rule | asked | PASS / verdict | otherwise |
|---|---|---|---|
| **P1** layout on A | D1_A(8) = ΔW(`als_h8`) − ΔW(`alq_h8`) | **PASS** if > 1.0 W at ≥ 3 SE ("which bits") | **FAIL (how many)** if < 0.5 W with the 95% upper bound < 1.0 W; else INCONCLUSIVE |
| **P2** the A side's saturating form | rms of one curve W (1 − e^(−S_A/W)), W refitted on the 15 A rungs (`alq` k = 1–16, `als` k = 2–16) | **ACCEPTED** if ≤ 0.40 W | **REJECTED** if > 0.60 W; INCONCLUSIVE between. E70: 1.063 W on the low layout alone |
| **P3** the mirror, out of sample | rms of law M with c frozen at 0.6433 over the 7 spread rungs | **PASS** if ≤ 0.50 W | **FAIL** if > 0.80 W; INCONCLUSIVE between. WA frozen and law A reported beside it |
| **P4** the A side's form | read off P1 and D2_A: R_k (a free value per k, the best any "how many" law can do), R_SA (P2's curve), R_M (law M with c refitted) | "**which bits**" if P1 PASS and min(R_SA, R_M) < R_k / 2; "**how many**" if P1 FAIL and R_k < min(R_SA, R_M) / 2 | "both or neither" otherwise. Beside it, the better one-parameter law is named if its rms is ≤ 1/1.5 of the other's, else "not separated" |
| **P5** the A word's weight (ungated) | ρ(8) low and spread, each a mean of per-pass ratios with the B rung from the same pass | **PASS** if both in [0.7, 2.5] and \|spread − low\| ≤ 0.30 | **FAIL** if the difference exceeds 0.30 at ≥ 3 SE (the weight depends on the layout) or either ρ is outside the band; else INCONCLUSIVE |
| **P6** replicate | E70's seven `alq` rungs within 0.6 W (`alq_h23` 1.0 W), and `ls_h8` − `lq_h8` within 0.6 W of E70's 3.860 W | **PASS** if all hold | **FAIL**; a failure is a card-stability result and qualifies every other number |
| **P7** random words | ΔW(`nrd_a`) / ΔW(`nrd_b`), paired per pass | **PASS** if in [0.55, 0.75] (law M: c = 0.643) | **FAIL**. E70's own pair read 0.668, seen before this registration, so P7 is a replicate more than a prediction |

Reported with the rules, never verdicts: every rung with its fJ per designed bit (E70's within-experiment currency, which must not be
carried into the gate-level ledger); R_SA with W frozen at 6.373 W; R_A (additive); law WB (B's refitted W = 10.52 W on S_A, in the
JSON); the per-pass refits of W and c with their SEs; `alq_h23` out of sample under each refitted law and how far it sits above the
refitted W (E70: 28 SE); the refitted curve's prediction for `nrd_a` from its additive sum (17.30 W).

## Gates, reduction and arms

- **Per run:** `hl/reduce_hl.py` unchanged — board power over seconds 1–3 after the first launch, corrected to the launch reading
  with the card's own within-run leakage slope (`--leak auto`); gates on the clock (600 MHz in every sample), the voltage (±3 mV of
  the pass median), the launch (on protocol, within 0.5 °C of 58 °C), the records, and cycles per op (within 0.5% of the item's zero).
- **Per pass:** a pass is set aside if more than one run fails, if `anchor_pi` drifts more than 0.3 W first to last (E67's gates), or
  if the four constant-operand runs (`lq_h0`, `aq_h0`, `anchor_pi` twice: one physical state) span more than 0.45 W (E70's D-a).
- **The registered reduction** is `score_e113.py` over the kept passes, with every rung read against its zero and every contrast
  paired within a pass, SE from the between-pass scatter. **At least 3 kept passes**, or every rule reads NOT SCORED and the all-passes
  arm is reported, labelled as the fallback reading.
- **Arms (reported, never verdicts):** the leakage slope fixed at 0.2, 0.3 and 0.4 W/°C (E70's D-d); all passes with E67's gates
  only (no D-a).

## Protocol and budget

E67's and E70's protocol, unchanged, through `hl/block.sh` (`HL_GEN=build/hl-gen6-e113`, `HL_EXPN=e113`): the card lock
`/run/lock/etsoc-shire0.lock` held for each pass, every device process under `timeout 10` with `--stop-file`; launch at a 58 °C
minion-shire reading after a 59 °C preheat; 4 s runs on all 1,024 minions; two unrecorded `anchor_pi` burn-in runs, `anchor_pi`
first and last, everything else shuffled with the pass number as seed; a pass stops at 78 °C, on telemetry older than 3 s, or when
another user appears on this card. E60's departure D1, as `hl/block.sh` implements it, applies: another user's idle shell login
does not block on aifoundry3; a device process, a held lock or another user on this card does.

- **Session** (`session_e113.sh`, detached on the box after the claim): et-who; the opening `ettelem config`; a host-load sampler
  (E70's D-b, read only); the smoke, pass 1130 (`anchor_pi`, `als_h8`, `alq_h8`, no preheat) and `smoke_gate_e113.py` (block ok,
  every run ok on 1,024 minions at 546 ± 0.5% cycles per op); then `queue_e113.sh`, passes 1131–1137; the closing `ettelem config`.
- **Budget: at most 35 card-minutes.** The queue starts no pass that would end after the session's start + 32 min (the longest pass
  so far is the estimate, 300 s at first); a pass in flight is never cut. Expected: six passes of about 4.3 min. Minimum for a
  verdict: three kept passes. `build/e113-STOP` stops the queue before its next pass.
- **Time window:** the session starts by 18:00 PST and ends by 19:00 PST, or it is not started.
- **Claim:** one post in `#community-lab` before the session (`using aifoundry3 for 1 h, until ~HH:MM PST`), edited to append
  ` — released` after the data are pushed.

## What E113 does not answer

- **int8's A-side α (Q130(c) A1, 0.491).** `hl/run_hl.py` runs fp32 only; no int8 tile runs here.
- **The broadcast weight in a gated lane** (E78's C2 case: B = 0, A moving). E113's lanes are all ungated (B = 1.0); ρ(8) speaks
  for an ungated fp32 lane only.
- **The busy partner** (item 6's R8 clause): every A rung here has the quiet partner B = 1.0.
- **The power model's own prediction for the new tiles.** M5 and M4 price a tile from the fixed RTL bench's counts
  (`rtl-sim/fma_toggle_v2`), which is not built on this machine; the nine new tiles have no bench count, so no M5 prediction is
  frozen. E70's rungs have counts (`counts-hl.json`), and a later desk pass can price the new ones.
- Other base words, other cards, other clocks.

## Files

| file | what |
|---|---|
| `make_e113.py` | the operand set: make_hl.py's set unchanged plus `alq_h3`, `alq_h6` and `als_h2`…`als_h16`, every designed count re-derived from the files by `--check` |
| `predict_e113.py`, `predictions-e113.json` | the laws and every frozen prediction, from E65's, E67's and E70's committed files |
| `items_e113.sh` | the item list, the smoke list and the pass numbers |
| `setup_e113.sh` | on the box, files only: the operand set, the byte-identity check against `build/hl-gen5`, a `V3_DRY=1` dry run |
| `session_e113.sh`, `queue_e113.sh`, `smoke_gate_e113.py` | the card session, the passes with their deadline, the smoke gate |
| `collect_e113.sh` | on the box: `reduce_hl.py` over the ok passes and the three leakage arms, then `score_e113.py`, into one data directory |
| `score_e113.py` | the registered gates, contrasts, fits and rules P1–P7 |
| `selftest_e113.py`, `selftest.txt` | the scorer on three synthetic truths |
| `new-tiles.sha256` | the sha256 of the nine new operand files |

Data: `docs/reports/data/2026-11-01-e113-a-side-saturation/`.

## Amendments

*(none)*

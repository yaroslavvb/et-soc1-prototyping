# Q140(q) registration, amendment A2 (dated Wed 4 Nov 2026, about 09:15-09:30 PST): E169's step rule and its design

*Written by Q141(s), the card half's desk preparation, on the Intel. Desk only: no card, no device command, no access to a lab box,
nothing from the private archive. It amends Q140(q)'s registration for **E169 only**:
[`REGISTRATION.md`](../../../docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION.md) and
[`registration.json`](../../../docs/reports/data/2026-11-04-q140q-gemm-g4-stride/registration.json), committed in **`49575094`** at
02:26:25 PST; the freeze **`e39d06da`** (02:49:40 PST) with `predictions-e169.json` (sha256 `38ee500f…`), `stride_sm.py` (`4b8b028d…`)
and `peaks_e169.py` (`bf466124…`); and amendment A1 with the corrections, **`1bfaa4e4`** (04:03:20 PST,
[`REGISTRATION-A1.md`](../../../docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION-A1.md)). It sits in E169's kit,
the only path this lane writes, and none of those files changes. Every number below is printed by [`steps_e169.py`](steps_e169.py) →
[`steps-e169.txt`](steps-e169.txt) and stored in [`step-rule-e169.json`](step-rule-e169.json), which the scorer reads.*

*It is written after Q140's final critic (Q140(f), Wed 4 Nov about 08:10-09:10 PST) and **before any E169 claim or data**: at 09:15
PST the lab repository held no data directory for E169 and no `tools/claims-v3/e169/`, and its log names E169 only in Q140(q)'s
registration, freeze and corrections (`49575094`, `e39d06da`, `1bfaa4e4`) and in Q140(r)'s records (`b4e48993`), checked at `8eb3be71`,
equal to origin. It answers the critic's `card_half[6]` ("E169 needs a scorer,
a design and a step rule"), its `desk_next` 4 and 7, and its new fault 3 ("'E169 tests' the L3's 8 MB index needs a step rule that
is not registered"). On Q139's final critic that is **rank 6**, and on the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 1** ("Where a large GEMM
falls"). The owner's goal, 2 November 2026: to predict the power requirement and heat generation of numeric computations as
accurately as possible.*

## Why a step rule

B7, as registered, scores SM's level: SM's frozen T800 within 3% on every shape, and "resolved" when the measured T800 is closer to SM
than to ISO. SM's frozen T800 sits 6-45% above ISO on all six shapes, the non-power-of-two ones included, and on the committed ladder
SM's level ran 13-23% slow past 32 MB at every stride (Q140(q)'s README, C3 and C6). So B7 will most likely fail on the level, whatever
the 8 MB index does.

What the index predicts is a **step**. Take each non-power-of-two shape and its power-of-two partner:

| pair (P over N) | SM | ISO | STRICT | decides |
|---|---|---|---|---|
| P1/N1, `gemmL1x8x5` over `gemmL1x7x5` | **+37.06%** | 0.00% | 0.00% | yes |
| P2/N2, `gemmL2x8x3` over `gemmL2x6x3` | +7.94% | +5.76% | −1.03% | reported only |
| P3/N3, `gemmL1x4x8` over `gemmL1x5x8` | **+30.97%** | 0.00% | 0.00% | yes |

That is T800(P) / T800(N) − 1 from `predictions-e169.json` (fp32). It equals the critic's post hoc desk check to four decimals
(steps-e169.txt §1). ISO and STRICT have no set index, and on each decisive pair they class both shapes' lines alike: ISO's retention
is the same at both shapes' distances, and STRICT calls both shapes' far B lines fresh.

A step is a ratio of two shapes measured in one session, minutes apart. So the session's clock, its die temperature, and any level
error that P and N share cancel in it. The card's own record shows what a step looks like:

- **No power-of-two stride.** Adjacent rungs on E158's plateau (K2 NB 9-13, K4 NB 6-7, K6 NB 5-6, every far line at 39-59 MB) step
  by **−0.55% to +1.29%** (steps-e169.txt §3).
- **The committed collapses.** They ran **+14.9% to +33.3%** over the nearest rung of their own ladders (Q140(q) C3, reproduced
  exactly in steps-e169.txt §4). SM's frozen steps there were +9.1% to +45.5%, and ISO's 0.0% to +21.2%.

## S. The step rule (registered here; blind: no E169 data exists)

**S1. The quantity.** For a pair (P, N) in fp32 zeros:

- for each pass j, the step is T800_j(P) / T800_j(N). T800_j(X) is E158's per-pass reduction: the mean of `wall_s / iters` over the
  work launches of pass j's burst of X whose kernel clock (`cycles_max / wall_s`) reads **at or above 790 MHz**;
- a pass counts only if both bursts ran in it, each with at least 5 such launches (E119's `min_hi`);
- the measured step s is exp(mean of ln step_j) − 1, over the n passes that count.

**S2. The interval, from the passes, with E158's repeatability as its floor.** The 95% interval is exp(ℓ ± h) − 1, where ℓ is the
mean log step, h = t(0.975, n − 1) × max(sd, σ0) / √n, and sd is the passes' own sample sd of ln step_j. σ0 is **0.336%**:

- E158's sd of ln T800 over three passes, pooled over its 28 three-pass cells (56 df), is **0.237%** (worst cell 0.407%);
- σ0 = √2 × 0.237%, since a step is the log of a ratio of two such cells.

The floor keeps three to five passes' own sd, on 2-4 df, from making an interval narrower than the card has shown. At the floor the
half-width is **±0.42 / 0.53 / 0.83 points at 5 / 4 / 3 passes**. That is well inside the 3-point zones, so the zones decide, not the
noise. Between sessions E158 repeated E146's T800 within −0.31% to +0.29% (8 cells). A step is measured within one session, so that is
reported, not used. A pair needs **n ≥ 3** for a reading (the registered subset gives 3, the design 5).

**S3. The zones and a pair's reading.** Each hypothesis H in {SM, ISO, STRICT} has the zone Z_H = its frozen step ± **3.0 points**.
That is B7's own 3%, about twice the card's widest plateau-neighbour step (1.29%), and 3.6-7 times the half-width above. Its steps
are `step-rule-e169.json` › `hypotheses` (5 decimals). A pair reads:

- **SUPPORTS H** if its whole interval lies inside Z_H (it can name two: on P1/N1 and P3/N3 ISO and STRICT share 0.0, read "no
  step"; on P2/N2 SM's and ISO's zones overlap, [+4.94, +10.94] and [+2.76, +8.76]);
- **NONE OF THE THREE** if it lies wholly outside every zone (the README says between or beyond which);
- **UNRESOLVED** if it crosses a zone's edge;
- **NO READING** below 3 passes.

**S4. The verdict on the 8 MB index**, on the two decisive pairs **P1/N1 and P3/N3**. There SM's step is 31-37 points from ISO's and
STRICT's, ten or more times the zone. **P2/N2 is reported with the same reading but never counted**: SM and ISO stand 2.18 points apart,
under the zone, so it cannot separate them; it can separate both from STRICT. Each decisive pair has:

- a **presence**: PRESENT if the interval's low end is above +3.0 points (outside the no-step zone of ISO and STRICT), ABSENT if the
  interval lies inside [−3.0, +3.0], else UNRESOLVED;
- a **size**: SM if the interval lies inside SM's zone, NOT SM if it lies wholly outside it, else UNRESOLVED.

| verdict | when | what it says |
|---|---|---|
| **INDEX STEP AS SM** | both PRESENT and SM | the L3's public set map (8 MB index, 4 ways, true LRU, the runtime's offsets) sizes the step at power-of-two panel strides, though not the level |
| **NO STEP** | both ABSENT | no power-of-two step at these shapes: the 8 MB index does not set their time, and SM's index is refuted as the cause of such a step here |
| **A STRIDE STEP SM DOES NOT SIZE** | both PRESENT, at least one NOT SM | a step that no fully associative model makes: a block-stride term stays a candidate (the L3's index or the DRAM's mapping at the same strides), but SM's size is wrong |
| **A STRIDE STEP, ITS SIZE UNRESOLVED** | both PRESENT, none NOT SM, at least one size UNRESOLVED | as above, SM's size neither held nor refuted |
| **MIXED** | one PRESENT, the other ABSENT | the step depends on the panel's structure beyond SM's index (NB 8 against NB 4); each pair named |
| **UNRESOLVED** | any other combination | a presence crosses its edge |
| **NO VERDICT** | a decisive pair below 3 passes | — |

**S5. Reported beside, no verdict:**

- per pair, the **share of SM's step** the card shows, s / s_SM, over the same interval. The committed collapses showed 0.67-1.63
  (`step-rule-e169.json` › `committed_collapses_C3_post_hoc`);
- the ratio of the pass-pooled T800s, and each pass's step;
- the fp16 and int8 steps against their own frozen steps, if block F ran (SM +37.43 / +8.06 / +31.22% in fp16, +31.69 / +6.28 /
  +27.17% in int8);
- the registered sensitivity arms ALIGNED and A_STRICT (B3), whose fp32 steps are +35.99 / +10.74 / +30.56% and +32.54 / +6.69 /
  +24.37%.

**S6. The check of C labels, it does not drop.** If any check of C is neither exact nor approx (or a run has none), R0 FAILS. Every
reading and verdict is then printed labelled "R0 FAIL", as E158's R0 does.

**S7. What a step cannot say.** A step at a power-of-two stride does not by itself separate the L3's set index from a DRAM-side channel
or bank mapping at the same strides. E158's `K4n8` ran 6.5% slower than all-fresh (E158 C2), and no public source gives the
physical-address-to-memshire interleave (Q140(q) B4). SM's pattern is specific: a small P2/N2 step beside large P1/N1 and P3/N3 steps.
But the README reads even INDEX STEP AS SM as "consistent with the index", not as proof of it.

## B7, kept as registered

B7 is scored exactly as `49575094` wrote it and `predictions-e169.json` › `rules` freezes it (`step-rule-e169.json` ›
`b7_as_registered`):

- **point:** SM's frozen T800 within 3% of the measured T800 on every one of the six shapes (fp32; fp16 and int8 printed if run);
- **resolved**, on each of P1-P3: |T_SM − T_ISO| / T_ISO ≥ 3% (true by construction: +45 / +20 / +43%), and the measured T800 closer
  to SM than to ISO.

It is expected to FAIL on the point rule, by SM's level. ISO's and STRICT's level errors (measured / predicted − 1, per shape and as
an rms) are printed beside it, as Q140(q)'s committed-data scores were.

## D. The design (E169; nothing of it existed in the registration beyond "fp32 zeros bursts in E158's harness, T800 from launches at or above 790 MHz")

**D1. The card, the harness, the binary.** aifoundry2 card 0 under its own governor (65 W / 65 °C, read by `ettelem config` at the
queue's start and end and after every run). Nothing is set on the card. It runs E158's harness: E146's preflight with E136's three
registered sha256, E119's `run_e119.py` unchanged, and E158's queue with its names changed. The binary is E136's `rgm136`, unchanged:
every shape is an argument, `gemmL<MB>x<NB>x<KB>`. Every cell is zeros through the pool (the file's zero tile,
`tools/claims-v3/kinds/tiles/<format>/zeros.bin`).

**D2. A burst.** One 6 s process (budget 7.5 s), tail 4 s, from a die reading at or below 55 °C (the cool gate, waiting at most 300 s),
as E158. T800 comes from the launches at or above 790 MHz, by E158's per-pass reduction and E119's `clock_x` for the pooled T800.

**D3. The order on the card** ([`protocol.txt`](protocol.txt)):

1. **SMOKE.** The idle card for 30 s (the session's rest reading), then four 2 s launches of zeros, each with its check of C: P1 fp32,
   N2 fp16, P3 int8, N3 fp32. Each one's cycles per op must lie within 50-250% of STRICT's frozen T800 × 800 (the queue's check).
2. **The stop-path tests**, E158's, before the session; either failing halts the queue with no session:
   - stoptest-board: `board_cap_w` 30 W on three samples, one 6 s burst of `K4n8` fp32 zeros (E158's own test burst);
   - stoptest-die: `abs_stop_c` 30 °C.
3. **A** (pass 1): N1, P1, N2, P2, N3, P3, then the ties K4n7, K4n8, K6n5, K6n4, all fp32, in that order (each N before its P).
4. **B** (pass 2): the same ten, shuffled.
5. **C, D and E** (passes 3, 4 and 5): the six E169 shapes, each block shuffled.
6. **F** (the formats, printed if run): the six shapes in fp16, then in int8 (pass 1 of each).

The shuffles use `run_hpl.py`'s one generator over the blocks, `order_seed` 169. That is **50 bursts**. The **registered subset**, if
the cap or the slot cuts: A, B and C (three passes of the six, two of the ties), 26 bursts.

**D4. Formats.** fp32 zeros is primary. fp16 and int8 zeros run only in block F, last, and are printed if run: their steps against their
own frozen steps, and B7's point error, with no verdict.

**D5. The check of C (R0).** E136's GEMM host reference: `rgm136`'s `test: check` record compares C of each process's last launch with
the host's own sum over the whole K, on sampled C tiles spread over the C blocks (exact, approx or wrong). It runs in the smoke and in
every run. Any wrong, or a run with no check, fails R0 (S6). The smoke's cycles check is the queue's (D3).

**D6. The ties to E158** (added here; not in the critic's list). E158's rungs K4n7, K4n8, K6n5 and K6n4, in fp32, in passes 1 and 2.

- **TIE-T:** each tie shape's pooled T800 within **2%** of E158's measured T800 (E158 R0's replicate bar): 1.64871, 2.12508, 1.63532
  and 1.87826 µs.
- **TIE-S:** the two committed steps re-measured in this session, `K4n8`/`K4n7` and `K6n4`/`K6n5`, each within **2.0 points** of E158's
  +28.89% and +14.86%.

The ties are a positive control for the step measurement, in the same session as the new pairs. TIED if all hold, else NOT TIED with
the failures named. NOT TIED labels the step readings "session not tied to E158" and changes none of them.

**D7. The stops** (written into the protocol and tested in the queue's stop-path tests, on live samples):

- the board above **60 W on three samples in a row** (E158's, under this round's 85 W bound for aifoundry2);
- one die reading (the minion shires' mean or the hottest sensor) **at or above 76 °C** (this round's and E159's, under E158's 80 °C);
- the admission limit **82 W** at the estimate;
- the peak lock 60 W (E158's: after a run whose board reached 60 W, no cell with an estimate at or above that run's goes on).

The runner refuses a protocol whose board stop is above 85 W, whose die stop is above 76 °C, or whose admission limit is above 82 W,
under `--dry` too.

**D8. The admission estimates** (the predicted peak, not a scored prediction):

- fp32 at E169's shapes: `predictions-e169.json` › `peak.predicted_peak_w`, E146's P0(800) for fp32 zeros + 8.51 W, **at most 46.92 W**;
- fp16 and int8 at E169's shapes: the same rule through the same code (E146's desk split and `levels0`, as `peaks_e169.py`), in
  [`kit-e169.json`](kit-e169.json). Its fp32 values reproduce the frozen ones exactly;
- the ties: E158's frozen admission (`predictions-e158.json`), at most 39.8 W.

Everything is far under 82 W: nothing is duty-cycled or dropped. E158's 98 zeros bursts peaked at 36.1 W.

**D9. The pools' device addresses are not logged; the binary does not allow it.** E136's `rgm136` prints no buffer address: `put()`
returns each buffer's device address, and no record prints it (`host/main.cpp`). It also registers the runtime's verbose log levels as
disabled before the runtime starts (lines 43-52, against a log-level race that crashed a host). So the runtime's own "Malloc at
address" line (`esperanto-tools-libs/src/MemoryManager.cpp:291`, verbose level LOW) cannot print, and no option prints one. A rebuilt
binary would fail the preflight's sha256 and need its own command audit. E169 runs with B2's offsets (C, then A, then B, first fit over
4 KB blocks) as an assumption, as Q140(q)'s README already says.

**D10. Card time.** 50 bursts at about 12.1 s each (E158: 98 in 19.7 min) is about **10.1 card-minutes**. With the smoke and the two
stop tests (about 1.1 min in E158) that is about 11-12. Add up to 5 more if the first cool gate waits, since E169 follows E168 on
aifoundry2. The session's cap is **20 card-minutes**, and at most 25 in all. The subset takes about 6.5.

**D11. Device commands.** E158's chain exactly. Every command is a READ (`dmcmd_audit.py` GO, with E158's one reviewed exception, the
residency read `run_e119.py` rewrites and this `ettelem` refuses before it opens the device). No statistics reset (no `--reset-ms`),
no firmware-revisions query, no residency read, no set. The classified table is in the kit's [README](README.md#device-commands-sent).

**D12. A reported power reading, no verdict.** Each fp32 shape's first-second board at 800 MHz (E126's `collect`, `burst_p800_w_runs`)
is compared with three levels:

- E136's law P0(800) as frozen (`predictions-e169.json` › `peak.P0_800_fp32_zeros_w`, 38.36-38.41 W);
- P0 + β·δ_fp32, Q140(l)'s zeros level (the T_Z that G4 keeps; β 0.648275, δ −1.533980 W from `g4.json`);
- Q140(q) check (i)'s form, P0 + β·δ + 0.47 W/°C × (T_start − 54.3818 °C), the die law that G4 rejected for holds.

None of these six shapes has run, so this is a fresh out-of-sample reading of a zeros burst's power.

## Departures from the brief, dated Wed 4 Nov 2026

- **The stops.** The brief and the critic's `card_half[6]` call E158's stops "85 W on 3 live samples, 76 C". E158 registered and ran
  60 W on three samples and 80 °C (`tools/claims-v3/e158/E158.md` § The stops; its `protocol.json` › `safety`). The 85 W and 76 °C are
  E159's (Q140(q) A8: "Stops as E159") and this round's bound for aifoundry2. E169 takes the stricter of each (D7).
- **The addresses** are not logged, because the binary cannot log them (D9).
- **The ties** (D6) are added: about 1.7 card-minutes, so that the step measurement has a positive control in its own session.
- **The queue's session cap.** Its default `--cap` is 20 card-minutes, not E158's 40. The runner's `--max-card-min` takes the queue's
  value over the protocol's, so the default carries E169's cap.

## Order of the commits

1. This amendment with `step-rule-e169.json`, `steps_e169.py` and `steps-e169.txt`, before anything else of E169.
2. The scorer (`score_e169.py`, `reduce_e169.py`, `kit-e169.json`), its self-test on E158's committed data, and its output.
3. The run kit (protocols, runner, queue), the device-command audit, the dry pass on the Intel, the hash list, and the README.

# E109: int8 zeros' extra 0.61 W - not per-op work, not the lanes: int8's TensorFMA costs 1.7 W more with nothing issued (Q133, aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 11, "int8 zeros' extra 0.61 W"** (the complaint this answers), with an arm for **item 15**'s "why a live zero on A costs 1.72 W more than priced" ([E93](../2026-11-01-e93-zero-gate-silicon/README.md) R5).*

*Sun 1 Nov 2026 (week 44), Q133, lane a3-e109-int8-zeros. Pre-registered in [`tools/claims-v3/e109/E109.md`](../../../../tools/claims-v3/e109/E109.md) with [`predictions-e109.json`](../../../../tools/claims-v3/e109/predictions-e109.json), committed as **`5857b6bb`** at **12:53:35 PST**, 1 min 31 s before the claim in `#community-lab` (12:55:06 PST, message `1566556212500369609`) and 1 min 55 s before the first launch (the smoke's, 12:55:30 PST). No amendment was written. **aifoundry3 card 0** at its pinned **600 MHz, 521.8 mV**; `ettelem config` read under the card lock at 12:55:25 and 13:14:48 PST: TDP 0 W, threshold 65 °C, 600 MHz, 523 mV, both times. Nothing was set: no governor, TDP, threshold or clock set, no `--reset-ms`, no PMIC command. Card session 12:55:25-13:14:48 PST, **19.4 card-minutes** of the 25 allowed. Released 13:15 PST by editing the same post, read back as `<ai> Claude says: using aifoundry3 for 0.5 h, until ~13:30 PST doc — released (edited)`.*

## Results

**The registered test is NOT SCORED.** It needs at least 3 kept passes (E109.md, protocol step 4; `predictions-e109.json` › `min_kept_passes`). Three of the four registered passes ran: the queue's registered 23-minute deadline dropped pass 10913, because the passes took 387, 348 and 334 s, not the 330 s planned. Then E78's pass gate, applied unchanged by `reduce_e78.py`, set pass 10912 aside: its random fp32 anchor's three runs spanned 1.067 W against the gate's 1.0 W (one run read 51.75 W of board power, the others 52.82 and 52.75 W). That left 2 kept passes, so no registered verdict is claimed, and every number below is labelled. ([`e109.json`](e109.json) › `passes_set_aside`; [`logs/e109-queue.out`](logs/e109-queue.out))

**Two readings, both unregistered:** the registered reduction's two kept passes (10910, 10911; t at 1 degree of freedom, so its intervals are wide), and **post hoc**, all three passes with only that random-anchor span gate lifted ([`posthoc_e109.py`](../../../../tools/claims-v3/e109/posthoc_e109.py): `GATES["random_range_w"]` 1.0 → 99 W, every other gate E78's). The random fp32 anchor enters no E109 statistic except R10's tie: every E109 D is over the format's zeros anchors, which in pass 10912 span 0.053 W in fp32 and 0.054 W in int8. The two readings agree on every quantity. Where they differ is only the width; the three-pass numbers are quoted.

1. **It is not per-op work** (Q132(b)'s second reading). K = 8 nearly doubles the op rate (×1.94 fp32, ×1.92 int8) at the same reads, issued micro-ops and busy cycles a second. With no micro-op issued, that costs **+0.04 ± 0.20 W in fp32 and +0.09 ± 0.09 W in int8: 38 ± 187 pJ and 51 ± 53 pJ an op**, against the **770 pJ** the reading needs. Per-op work makes **+0.06 ± 0.18 W** of this session's **0.60 ± 0.12 W** gap. (R1 would FAIL; `scored-3pass.json` › `rules.R1_ops`, `quantities.<f>.e_op_pj`)
2. **The lanes point the other way.** Issuing the micro-ops on all-zero tiles, every slot gated, costs **fp32 1.51 ± 0.18 W** of its 1.86 W over idle, and **int8 0.42 ± 0.08 W** of its 2.46 W. So the lanes favour int8 by **1.09 ± 0.10 W** (R2 would read LANES-OPPOSE). That is the RTL count's direction (Q132(b) §14), at 3× and 17× the size its constant gives (0.52 and 0.03 W predicted). **Per register bit that sees a clock edge**, the edges the mask removes in the bench, the lanes cost **0.36 ± 0.04 fJ (fp32) and 0.49 ± 0.09 fJ (int8)**: nearly one price for both formats. Per bit clocked with the enable high it is 3.1 and 17.9 fJ, against M4's 1.07. On zeros a gated lane pays for its clock pins, not its enabled flops. ([`posthoc.txt`](posthoc.txt), post hoc)
3. **The gap sits where neither moves.** With no micro-op issued, the row mask 0x0000 (the same reads, cycles and op rate), int8's TensorFMA loop costs **2.11 ± 0.08 W over idle and fp32's 0.38 ± 0.09 W: int8 +1.74 ± 0.16 W**. Of the gap, **G_rest = +1.63 ± 0.15 W** (R3 would PASS, R0 would read PER-TIME). The read rate cannot carry that at one price: if all of fp32's no-issue loop were reads, a read would cost at most **1.16 ± 0.27 pJ**, and at that price int8's 1.34× read rate buys **0.12 ± 0.03 W**. int8's no-issue loop would need **4.9 pJ** a read. In the RTL bench the two formats' no-issue loops clock the same registers a second (2.53 and 2.51 × 10¹⁵ register-bit edges; 6.7 and 7.2 × 10¹⁴ enabled bits). So **the 1.7 W is outside what the bench counts**: the register arrays, the scratchpad, or the core. The RTL names int8-only paths that run every cycle the FSM works, none tested here: A's 64-bit reads into TenTMP (`vpu_tensorfma.v:338-366`); B written into the 16 integer units' TenB arrays (`vpu_lane.v`, `lane_tima`); TenC's read port, addressed every cycle (`:432`); the TIMA controls on `tima_clk_en = working && req_int8` (`vpu_tensorfma.v:841`). ([`posthoc.txt`](posthoc.txt), post hoc)
4. **B-line reads are not resolved.** Halving B-line reuse in fp32 (8 A rows against K = 8: twice B's half-line reads a second at the same op rate within 3%) costs **+0.21 ± 0.30 W**: **r_B = 6.5 ± 9.0 pJ** a 256-bit read. That interval includes 0 and the reads reading's 4.4 pJ (R4 would read NOT-RESOLVED; CONSISTENT). int8's contrast mixes A's and B's reads, as registered: −0.07 ± 0.19 W.
5. **The card runs the RTL's cycles.** Every arm's cycles per op equal the bench's plus 7.75, to 0.001 of a cycle: fp32 544.0 / 282.0 / 290.0 / 280.0, int8 318.0 / 166.0 / 190.0 / 166.0, and the two masked item-15 tiles 544.0 (R6 would PASS ×10). The row mask stops issue without stopping the FSM; K and the A rows set the op's length as the public FSM says.
6. **Item 15: E93's excess is inside the live lanes, not in moving B to them.** A and B as in E93's `a_nz_b_randn` (A = −0, every lane live) and E78's `a_zeros_b_randn` (A = +0, every lane gated), the B bytes identical:
   - With no micro-op issued, the two cost the same, +0.02 ± 0.04 W (R7 would PASS): A's sign is invisible until a micro-op reads it. B's random bytes moving to the register files with no micro-op cost **T = 0.21 ± 0.25 W** (A = +0) and **0.23 ± 0.28 W** (A = −0).
   - **The gated lanes do something with B.** Of the gated tile's 0.80 ± 0.07 W over zeros, **0.59 ± 0.31 W** goes with the micro-ops (R8 would FAIL its ±0.25 W). In the bench no counted register changes there, so that is wires or arrays, presumably the operand bus. It is E78's "moving B-bus bit", in the gated lane.
   - **A live −0 lane with random B costs 3.92 ± 0.38 W more than a constant live lane** (π × π, 8.44 W), with transport taken out. E93 priced that step at 2.47 W on another card (B's bus bits at E88's price plus half E88's sign cost) and read 1.72 W more. On this card the tile reads **12.59 ± 0.09 W** (E93: 12.11 W on aifoundry1 card 1). Its excess is not in transport.
7. **The session ties to E78 on this card in all six cells** (R10): random fp32 24.80, fp16 22.29, int8 `full` 7.14, π 8.44, `a_zeros_b_randn` 0.80 W, and the gap G 0.600 W against E78's 0.619 W.

**What it changes.** Item 11 moves from *open* to **narrowed** (labelled, not registered). The extra 0.61 W is not per-op work and not the lanes: they favour int8 by 1.1 W. It is a 1.7 W excess of int8's TensorFMA with nothing issued, which no single read price explains and which the RTL bench's registers do not show. Q132(b)'s two readings both fail as stated: "ops" fails by its per-op price (≤ 0.1 nJ against 0.77), "reads" by its price ceiling (fp32 allows 1.2 pJ, int8 needs 4.9). The open part names three paths outside the bench: the register arrays, the scratchpad's int8 reads, the core. Item 15 is narrowed: the live-zero excess sits in the live lanes, and B's moving bits cost 0.6 W even in gated lanes. A replicate with the registered three passes kept is still owed. It would take about 19 card-minutes in E109's frame, unchanged.

## The arms, both reductions

D over the format's zeros (interpolated between the pass's three zeros anchors), S over the idle bracket, ± 95% over passes. "Cycles" is the median over the kept runs; "predicted" is frozen (`predictions-e109.json` › `arms`). Source: `e109-3pass.json` and `e109.json` › `items`.

| item | cycles | predicted | ops/s (10⁹) | D, 3 passes | S, 3 passes | D, 2 kept | S, 2 kept |
|---|---|---|---|---|---|---|---|
| `fp32.zeros` | 546.001 | 546.0 | 1.1209 | 0 | +1.857 ± 0.148 | 0 | +1.830 ± 0.460 |
| `m0.fp32.zeros` | 544.001 | 544.0 | 1.1248 | −1.507 ± 0.175 | +0.376 ± 0.089 | −1.486 ± 0.767 | +0.386 ± 0.397 |
| `k8.fp32.zeros` | 282.001 | 282.0 | 2.1716 | −0.108 ± 0.273 | +1.728 ± 0.129 | −0.125 ± 1.346 | +1.710 ± 0.526 |
| `r8.fp32.zeros` | 290.001 | 290.0 | 2.1115 | +0.104 ± 0.044 | +2.047 ± 0.066 | +0.098 ± 0.176 | +2.038 ± 0.273 |
| `m0k8.fp32.zeros` | 280.001 | 280.0 | 2.1870 | −1.467 ± 0.266 | +0.445 ± 0.335 | −1.486 ± 1.299 | +0.388 ± 1.172 |
| `int8.zeros` | 318.001 | 318.0 | 1.9254 | 0 | +2.458 ± 0.034 | 0 | +2.452 ± 0.120 |
| `m0.int8.zeros` | 318.001 | 318.0 | 1.9252 | −0.419 ± 0.079 | +2.111 ± 0.083 | −0.409 ± 0.334 | +2.093 ± 0.190 |
| `k8.int8.zeros` | 166.000 | 166.0 | 3.6879 | +0.120 ± 0.166 | +2.500 ± 0.321 | +0.101 ± 0.737 | +2.471 ± 1.508 |
| `r8.int8.zeros` | 190.000 | 190.0 | 3.2225 | +0.054 ± 0.309 | +2.568 ± 0.185 | +0.057 ± 1.577 | +2.610 ± 0.144 |
| `m0k8.int8.zeros` | 166.000 | 166.0 | 3.6892 | −0.330 ± 0.041 | +2.161 ± 0.031 | −0.338 ± 0.099 | +2.168 ± 0.035 |
| `fp32.a_zeros_b_randn` | 546.001 | 546.0 | 1.1207 | +0.798 ± 0.074 | +2.630 ± 0.076 | +0.782 ± 0.095 | +2.625 ± 0.375 |
| `m0.fp32.a_zeros_b_randn` | 544.001 | 544.0 | 1.1249 | −1.303 ± 0.313 | +0.614 ± 0.272 | −1.231 ± 0.197 | +0.676 ± 0.200 |
| `fp32.a_nz_b_randn` | 546.001 | 546.0 | 1.1209 | +12.590 ± 0.088 | +14.451 ± 0.059 | +12.573 ± 0.232 | +14.438 ± 0.032 |
| `m0.fp32.a_nz_b_randn` | 544.001 | 544.0 | 1.1246 | −1.281 ± 0.342 | +0.591 ± 0.158 | −1.201 ± 0.094 | +0.628 ± 0.083 |
| `anchor_pi` | 546.001 | — | 1.1204 | +8.442 ± 0.135 | +10.405 ± 0.282 | +8.453 ± 0.643 | +10.345 ± 0.563 |
| `fp32.randn` | 546.001 | — | 1.1209 | +24.798 ± 0.561 | +26.681 ± 0.521 | +24.927 ± 0.384 | +26.802 ± 0.267 |
| `fp16.randn` | 546.001 | — | 1.1210 | +22.293 ± 0.491 | +24.047 ± 0.381 | +22.404 ± 0.590 | +24.135 ± 0.086 |
| `int8.full` | 318.001 | — | 1.9254 | +7.140 ± 0.107 | +9.621 ± 0.156 | +7.164 ± 0.146 | +9.652 ± 0.383 |

`m0` = the row mask 0x0000 (no micro-op issued), `k8` = K of 8, `r8` = 8 A rows, `m0k8` = both. Idle 26.00 W; leakage slope (E78's registered `auto`) 0.130 W/°C over 40 runs; idle consistency median 0.05 W; cycles per op 546.001 / 546.001 / 318.001 on the plain items.

## The registered rules against the data (not scored: two kept passes)

`scored.json` (the two kept passes) and `scored-3pass.json` (post hoc, three passes) are `score_e109.py`'s output on each reduction. It prints verdicts at any n ≥ 2. The registration does not score below 3 kept passes, so **none of these is a registered verdict**.

| rule | registered line | 2 kept passes | 3 passes, gate lifted (post hoc) |
|---|---|---|---|
| R0 the answer | a share with 95% lower bound ≥ G/2 | PER-TIME | **PER-TIME** |
| R1 per-op work | G_op ≥ G/2 | INCONCLUSIVE (+0.08 ± 0.82) | **FAIL** (+0.06 ± 0.18 W) |
| R2 the lanes | CARRY / OPPOSE (upper < 0) | LANES-OPPOSE (−1.08 ± 0.43) | **LANES-OPPOSE** (−1.09 ± 0.10 W) |
| R3 per-time | G_rest ≥ G/2 | PASS (+1.62 ± 0.72) | **PASS** (+1.63 ± 0.15 W) |
| R4 B reads | r_B > 0; reads' 4.44 pJ inside | NOT-RESOLVED; CONSISTENT | **NOT-RESOLVED; CONSISTENT** (6.5 ± 9.0 pJ) |
| R5 additive lanes | inside ±0.15 W | INCONCLUSIVE / INCONCLUSIVE | fp32 INCONCLUSIVE (−0.10 ± 0.18), int8 **PASS** (+0.05 ± 0.10) |
| R6 the RTL's cycles | \|measured − predicted\| ≤ 2 | PASS ×10 | **PASS ×10** (every difference ≤ 0.001) |
| R7 A's sign unseen | inside ±0.25 W | PASS (+0.03 ± 0.10) | **PASS** (+0.02 ± 0.04 W) |
| R8 gated = transport | inside ±0.25 W | INCONCLUSIVE (+0.53 ± 0.48) | **FAIL** (+0.59 ± 0.31 W) |
| R10 the tie | six cells | PASS ×6 | **PASS ×6** |

The frozen readings' rms over the eight item-11 arms at the measured rates (W): reads 0.67, ops 1.19, the RTL count 0.46. All three miss: the arms' pattern is the lanes' (`m0` drops 1.5 W in fp32 and 0.4 W in int8), plus a per-time difference that none of them holds.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | committed and pushed before the claim | `5857b6bb`, 12:53:35 PST; claim 12:55:06; first launch 12:55:30 (the smoke's) |
| desk | the RTL bench for every arm; sys_emu; `V3_DRY` of one pass and the smoke | done before the freeze: [`tools/claims-v3/e109/desk/`](../../../../tools/claims-v3/e109/desk/bench-arms.txt) (bench), [`sysemu-check.txt`](../../../../tools/claims-v3/e109/desk/sysemu-check.txt) (10 runs, all `tensor_errors` 0, mask 0 on checked operands `both`), [`logs/e109-desk-dry-10910.log`](logs/e109-desk-dry-10910.log) (34 device calls), [`logs/e109-desk-dry-smoke.log`](logs/e109-desk-dry-smoke.log) (8) |
| smoke | 8 items; gate on launch records, `ok`, `tensor_errors` 0 | 12:55:26-12:56:14; every item 6 launch records, all `ok`, `tensor_errors` 0: SMOKE-GATE PASS ([`logs/e109-session.log`](logs/e109-session.log)) |
| passes | 10910-10913, the queue's 23-minute deadline | 10910 (387 s), 10911 (348 s), 10912 (334 s); 10913 dropped by the deadline at 13:14:48 |
| kept | at least 3, E78's pass gates | **2**: 10912 set aside (random fp32 anchor span 1.067 W > 1.0 W). **Not scored** |
| runs | 32 a pass, none skipped | 96 of 96 ran, none skipped, none failed a run gate |
| budget | at most 25 card-minutes | 19.4 (12:55:25-13:14:48) |
| config | read at both ends, never set | TDP 0, 65 °C, 600 MHz, 523 mV at both ends of the session and of every pass |

## Departures (dated)

- **Sun 1 Nov 2026, 13:2x PST, after the data: the post-hoc three-pass reduction** ([`posthoc_e109.py`](../../../../tools/claims-v3/e109/posthoc_e109.py)): E78's reducer, byte-identical, with E78's random-anchor span gate lifted for all passes. Written after the registered reduction had set pass 10912 aside and before its numbers were read. Labelled post hoc everywhere.
- **Sun 1 Nov 2026, after the data: [`posthoc_check_e109.py`](../../../../tools/claims-v3/e109/posthoc_check_e109.py)** (`posthoc.txt`): the no-issue loop's power, the per-read ceilings, the lanes' price per clock edge and per enabled bit, the bench's register activity a second, and item 15's live lane over a constant lane. None of these was registered.
- **13:03 PST, during the session: a plumbing check.** `reduce_e109.py` and `score_e109.py` were run once on pass 10910 alone, in scratch, while 10911 ran, to catch a pipeline fault before the end. Nothing was changed; the queue had no decision left that depended on it.
- **The scorer prints verdicts at n = 2**, although the registration scores nothing below 3 kept passes. Those printed verdicts (`scored.json`) are not claimed.

## How it ran

12:53:35 registration pushed; 12:55:06 claim; 12:55:25 `session_e109.sh` started detached on the box (`setsid nohup`): the opening config read under the card lock; the smoke; the smoke gate; `queue_e109.sh`; the closing config read. `et-who` showed no holder before and after. Each pass: E78's two burn-in runs of π, then 32 registered runs (π first and last, E78's six anchors in each of three segments, E109's 12 items dealt round-robin with seed `E109|aifoundry3|<pass>`), launch at a 58 °C die reading after a 59 °C preheat, 2 s quiet, 4 s FMA runs on all 1,024 minions. Pass 10910 began from a 50 °C die and spent 54 s heating first. 13:15 release; 13:15-13:20 the data collected to the Intel, reduced with `reduce_e109.py` (`reduce_e78.py` unchanged; sha256 of it, `e78_common.py`, `kinds.json`, `e93.json`, the E93 tile and `lib.sh` checked against the freeze) and scored with `score_e109.py`.

## Files

`e109.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the registered reduction); `scored.json`, `results.md` (`score_e109.py` on it); `e109-3pass.json`, `runs-3pass.csv`, `reduce-3pass.txt`, `reduce-3pass.log`, `scored-3pass.json`, `results-3pass.md` (post hoc, the gate lifted); `posthoc.json`, `posthoc.txt` (post hoc); `aifoundry3/e109/p1091[0-2]/` (every pass's raw data: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_start.json`, `config_end.json`, `manifest.txt`, `binaries.sha256`, `code.sha256`, `gen.sha256`, `configs.json`, `plan.json`, `run.log`, `block.json`); `aifoundry3/e109-smoke/p10901/`; `logs/` (the session, the queue, the session's two config reads, the queue's binaries' sha256, the box build, the sys_emu log, the two dry runs). The registration, binary, desk bench and code: [`tools/claims-v3/e109/`](../../../../tools/claims-v3/e109/README.md).

Rerun, from the repo root: `uv run tools/claims-v3/e109/reduce_e109.py docs/reports/data/2026-11-01-e109-int8-zeros/aifoundry3/e109/p109* --out e109.json --csv runs.csv --txt reduce.txt`, then `python3 tools/claims-v3/e109/score_e109.py e109.json --out scored.json --md results.md`; post hoc, `uv run tools/claims-v3/e109/posthoc_e109.py <the same passes> --out e109-3pass.json ...` and `python3 tools/claims-v3/e109/posthoc_check_e109.py docs/reports/data/2026-11-01-e109-int8-zeros`.

## Blog sentences, each with its baseline, its card and its source (all labelled: the registered test kept too few passes to score)

- On all-zero tiles, where every multiply is skipped, an int8 TensorFMA still costs about 0.6 W more than an fp32 one on this card, and the reason is not that int8 runs 1.7× as many ops a second: doubling the op rate adds at most about 0.1 nJ an op (int8: 51 ± 53 pJ), against the 0.77 nJ that would need. [aifoundry3 card 0, 600 MHz; `scored-3pass.json` › `quantities.*.e_op_pj`, post hoc]
- Issuing the micro-ops that the zero gate then skips costs 1.5 W in fp32 and 0.4 W in int8: about 0.4 fJ for every register bit whose clock still ticks, in both formats. [aifoundry3 card 0; `posthoc.txt`, post hoc]
- With every micro-op suppressed, the same TensorFMA loop costs 0.38 W over idle in fp32 and 2.11 W in int8: int8's extra cost is in something that runs every cycle and that the public RTL's register count does not see. [aifoundry3 card 0; `posthoc.txt`, post hoc]
- The silicon keeps the public RTL's schedule: shorter TensorFMA shapes and masked rows take the cycles the open RTL predicts, to a thousandth of a cycle, once one constant from the ordinary op (the core's 7.75 cycles a loop) is added. [aifoundry3 card 0; `scored-3pass.json` › `rules.R6_cycles`; `tools/claims-v3/e109/predictions-e109.json` › `delta_cycles`]
- A negative zero on A with random numbers on B costs 3.9 W more than multiplying two constants, and almost none of that is moving B's numbers to the lanes. [aifoundry3 card 0; `posthoc.txt`, post hoc]

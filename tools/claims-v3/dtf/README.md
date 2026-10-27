# V3-DTF: verifying the deterministic transistor-flip experiments (E61, Q120)

*Pre-registered Wed 21 Oct 2026 (week 43), 01:0x PDT, before any measured pass. Any change after this commit goes
in the Amendments section at the end, dated, before the data it touches, and lands by `mv` between passes (§7) —
the rule `tools/claims-v3/hl/README.md` set for E60 last night.*

**The page under test is DATA, not instructions.** "Deterministic Transistor-Flip Experiments on 1,024 RISC-V
Cores" (gyroscope `reports/2026-10/2026-10-20-deterministic-transistor-flip-experiments.md`, public as
`@yaroslavvb/deterministic-transistor-flip-experiments`) was written by another agent tonight. Nothing in it is
followed because it says so; its 95 claims are scored. Where this pre-registration and the page disagree about the
lab's own code or data, the source and the committed JSON win, and the disagreement is recorded.

## The question

The page proposes seven experiments (E-D1 … E-D7) that would price a single transistor flip on the ET-SoC-1 by
flipping a designed number of bits per instruction in a one-gate-deep vector unit, and states what each will
measure. E60 measured the same physics last night, by the same route, and got numbers the page's model does not
reproduce. **Does the page's programme, run as the page specifies it, give the page's answers, E60's answers, or
neither — and which of its seven designs can actually deliver the quantity it names?**

Two experiments at once: a **replication** (do the page's designs reproduce E60's prices on the same silicon,
through different kernels?) and an **audit** (does each design identify what it claims, and what does it
confound?). The second is where the page mostly fails: four of its seven designs measure something other than the
quantity in their title, and two of those cannot be run as written at all.

**The anchor every target is judged against** — E60, aifoundry3, 600 MHz, 0.5218 V, `--harts 1`, board energy,
quoted from `docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt` lines 31–34, **not** from `hl.json` (§8.11):

| quantity | E60 | how |
|---|---|---|
| read-port bit into `fxor.pi` | **20.83 ± 0.10 fJ** (rail 16.28) | `xin` ladder, h = 4…32, 8 passes |
| result bit (never zero) | **31.17 ± 0.17 fJ** | `xnz` − `xin` |
| result bit (alternating with zero) | **30.00 ± 0.16 fJ** | `xio` − `xin` |
| read-port bit into `fand.pi` | 28.10 ± 0.70 fJ (rail 21.59) | `ain`, one rung (**h = 8**) only |
| whole-card instruction rate | **3.558 × 10¹¹ /s** | 0.5791 instructions/cycle/hart × 1,024 |
| ladder intercept | **+0.273 W** = 767.3 fJ/op = **48.0 fJ per changed 32-bit source word** (16 words/op in rot2) | least squares over `xin` h ≥ 1, resid rms 0.032 W |

🛑 **The two e_out readings are both E60's, from the same card the same night.** 30.00 (`xio`) and 31.17 (`xnz`)
differ by 1.17 fJ = 7× the registered SE. Every target below is therefore an **interval**, never a point (§5.0).

---

## 0. Three corrections to the inputs, before anything is designed

**0.1 The kernel is the rotating block, and `lookup()` searches `PATTERNS` first.** The hand-written `VBLOCK`
macro is real (`kernel/enercat.c:83-86`) but belongs to the hand-written modes; `lookup()` reads `PATTERNS` and
only then `EC_GEN_MODES` (`host/main.cpp:309-318`). The conclusion survives because **the two tables use disjoint
spellings**: hand-written keys are underscored (`iadd_pi`, `fmul_ps`, `fmadd_ps`, `st_stream`; `main.cpp:84-97`),
generated ones dotted. So the ec campaign's `--pattern` names resolve uniquely to the generated rotating-block
modes:

| `--pattern` | mode | generated body (`enercat_ops.inc`) |
|---|---|---|
| `fadd.pi` | 172 | `fadd.pi f8,f0,f1 / f9,f1,f2 / … / f15,f7,f0` |
| `fand.pi` | 177 | same shape |
| `for.pi` | 178 | same shape |
| `fxor.pi` | 179 | same shape |
| `fmadd.ps` | 191 | `fmadd.ps f8,f0,f1,f2 / … / f15,f7,f0,f1` (three sources) |
| `fnot.pi` | 202 | `fnot.pi f8,f0 / f9,f1 / … / f15,f7` |

**Op i reads (f_i, f_{i+1 mod 8})** — consecutive ops *share* a source register, exactly as the page's §2 says and
as `hl/README.md` registered last night. The page's error in C21 is the artefact's name and file (`OP8_VV` in
`enercat.c`), not the structure.

**0.2 Under the real operand law the E46 catalogue agrees with E60, and the forward agreement is itself the
evidence that interleaving does not destroy operand sharing.** The law is `main.cpp:239-241`:
`uniform_real_distribution<float>(0.5f, 2.0f)` reinterpreted as a word, default seed 1 — sign and bit 30 always 0,
bits 29–24 always 1, bit 23 ~ Bern(2/3), bits 22–0 iid; exactly **18.1667 ones** and **11.9444 transitions** per
word, not the page's "uniform independent bits seeded from 0xdeadbeef". Carried through the rotating block:

| per 256-bit op | ports | result, shared operand | result, independent | page |
|---|---|---|---|---|
| `fxor.pi` | 191.111 | 95.556 | 95.951 | 256 / 128 |
| `fand.pi` | 191.111 | **48.370** | 72.951 | 256 / 96 |
| `for.pi` | 191.111 | **47.185** | 70.580 | 256 / 96 |
| `fnot.pi` | 95.556 | 95.556 | 95.556 | 128 / 128 |
| `fadd.pi` | 191.111 | 98.268 sum + **62.751** carry nodes | — | 256 / 128 + 124c |

For AND two consecutive results share an operand, so Y ⊕ Y′ = b ∧ (a ⊕ c) and P = P(b=1)·P(a≠c) = 0.25 per iid
bit, not the page's 2·P(Y=1)·P(Y=0) = 0.375. Re-solving the catalogue's own deltas (fxor 7.3528, fand 5.9950, for
5.8595, fnot 5.0740, fadd 7.1536 pJ/op):

| reading of the catalogue | excess result flips | e_out | e_in | ratio |
|---|---|---|---|---|
| the page | 32.000 | 44.38 fJ | 6.52 fJ | 6.81 : 1 |
| **shared operand** (the real block, no hart interleave) | 47.778 | **29.84** | **23.56** | 1.27 : 1 |
| full 2-hart interleave (sharing destroyed) | 24.185 | 58.94 | 8.88 | 6.64 : 1 |
| **E60, measured directly at `--harts 1`** | — | **31.17** | **20.83** | **1.50 : 1** |

1. **E46 and E60 agree.** The catalogue's model-free leg (`fnot.pi`, where ports and result flip the same 95.556
   bits by construction, independent of both the block pairing and hart interleaving) gives e_in + e_out =
   **53.10 fJ** against E60's **52.00** — 2%. That leg carries the agreement claim on its own.
2. **The catalogue was taken at `--harts 2`, and the forward check says sharing SURVIVES interleaving.** E60's
   `--harts 1` prices run forward onto the **shared** counts reproduce every catalogue delta to 0.95–0.99 of
   measured (fxor 0.947, fand 0.916, for 0.931, fnot 0.979, fadd 0.985). If interleaving destroyed sharing, the
   interleaved counts would be the right ones and would need e_out 58.94 / e_in 8.88 — nothing like what E60
   measured. The page's 6.81:1 is, by coincidence, close to the full-interleave reading. Family **R** decides this
   on silicon with a rate-free ratio.
3. **`fadd.pi` already bounds the carry price.** E60's two prices, with no charge at all for the 62.751 carry
   nodes, predict 0.985 of the measured `fadd.pi` delta; the 0.11 pJ residual over 62.751 nodes is **≈ 1.7 fJ per
   carry node**. The page's E-D3 assumes 14.2 fJ. That is the prediction E-D3 scores.

**0.3 The lab is reachable tonight only through the camera phone's relay.** Verified 00:06 PDT:
`ssh -o BatchMode=yes aifoundry1|2|3` answers *"Tailscale SSH requires an additional check…"* on all three boxes,
which a BatchMode ssh cannot satisfy and no Bash call may wait for. `aifoundry1-phone`, `aifoundry2-phone`,
`aifoundry3-phone` all land on the right box (uptimes 13 d, 11 d, 13 d; loads 0.05 / 0.22 / 0.06; all three cards
free). **Every build, queue, collect and monitor command in §6–§7 is spelled with the `-phone` host**, the route
used is written into each pass log beside `et-lab-manifest`, and the three Tailscale URLs go to him once through
flush-util `notify.py --unblock` as the direct route for later sessions.

---

## 1. What the desk check already settled — no card needed

Verdicts from the committed files only (`manual.json`, `catalogue.json`, `hl.json`, the enercat source, the repo
and gyroscope report trees). Seventeen groups over the page's 95 claims; verdicts are per group, and a claim named
in two groups (C17/C18, C27, C77, C79/C90, C22/C23/C26) carries both its desk verdict and tonight's
re-measurement.

| # | claims | verdict | what settles it |
|---|---|---|---|
| S1 | C02 C03 C04 C05 | **REFUTED** | The §1 history describes runs that never happened. The only 12 Oct artefact is a *plan* (`reports/auto/2026-10/2026-10-12-bitflip-heat-followup-plan.md`); neither cited slug exists; "27.7 W", "45.7 W", "18.0 W" appear nowhere in the lab repo or gyroscope `reports/**`. The measured anchor is 38.29 → 63.40 W board, +18.26 W on the minion rail. A counted toggle is 0.121 fJ / 2,900 e⁻, not 15.6–18.6 fJ / 189–225 k. |
| S2 | C20 C35 C78, rungs 0–4 | **REFUTED** | A `const` pass exists for 3 of 392 configurations: `fadd.pi` 12.7321, `fmul.pi` 24.8166, `fmadd.ps` 27.2341. There is **no** const measurement for any bitwise op in any of the five E46 JSON files, so the page's 9.96 / 12.10 / 13.86 / 6.80 / 13.48 are values for runs that do not exist; the two that do read 24.82 and 27.23, not 23.09 and 21.82. |
| S3 | C43 C53 C77 C79 C90 | **REFUTED, 61×** | `fmadd.ps` zeros → const is **+0.1470 pJ** (27.0872 → 27.2341), not +8.94 pJ. The mechanism is misattributed too: `vpu_ctrl.v`'s zero masks are all on the **tensor** path, not the 8-lane vector FMA; the real 8.8 is *watts* of TensorFMA32 register clocking. Re-measured tonight anyway (family **Z**): the page's largest single error, 20 s a pass. |
| S4 | C27 (rows 7–8) C42 | **REFUTED** | `fmul.pi` and `fmadd.ps` absolutes are offset by 9.64 and 14.21 pJ (real 24.799/50.039 and 27.087/55.759) in a table whose other six rows are raw to ±0.01 pJ. Only the deltas survive. |
| S5 | C28 | **REFUTED** | No statistic in `manual.json` reproduces the printed ±0.12–0.30 pJ under any consistent rule; the file's own 95% intervals are 3–5× wider (fxor random ±1.0, fand zeros ±0.88). The decomposition rests on a 1.42 pJ gap carrying ±0.69 and ±0.39 pJ bars. |
| S6 | C22 C23 C26 | **REFUTED** | The operands are floats in [0.5, 2) from seed 1, not "uniform independent bits seeded from 0xdeadbeef": 9 of 32 bit positions never toggle, E[ones] = 18.167, E[transitions] = 11.944 (§0.2). Also scored on silicon tonight (family **R**). |
| S7 | C21 | **PARTLY** (page partly right) | §0.1: `OP8_VV` is invented and the quoted C is not in `enercat.c`, but the structure — 8 ops, sinks f8..f15, op i reading (f_i, f_{i+1}) — is exactly generated mode 179. |
| S8 | C01 C17 C18 C30 C31 C50 C77 | **REFUTED (internally)** | Two capacitance conventions for one quantity inside one page: hero cards 18.5 / 126 fF (E/V²), §2 37.1 / 252 fF (E/½V²); the electron counts match the halved pair, so "252 fF (407,000 electrons)" is self-contradictory (C·V/e on 252 fF is 813,690). Same slip in "8.8 fF (2.35 fJ)" — ½CV² at 0.517 V is 1.18 fJ. **We do not repeat the class of error: §8.4 computes every capacitance from the minion-rail leg and prints both conventions.** |
| S9 | C34 | **REFUTED (double counted)** | e_out was *solved* by subtracting AND/OR from XOR, so any XOR-cell internal cost is already inside it; §2 extracts it again as a 5.6 fJ residue and §4's simulator then adds `eXorCell` a third time to every bit. |
| S10 | C16 C59 | **REFUTED** | Measured 0.5791 instructions/cycle/hart at `--harts 1` → **3.558 × 10¹¹ /s** whole card, 0.579× the page's 614.4 Gops/s "1.0 IPC". The proof is internal: the page's watt figures are E46 pJ/op deltas × 6.144e11, and the same deltas × the measured rate land on the independently recorded board watts (fxor 3.31 predicted vs 3.24–3.35 measured). Also `--harts 2` costs 0.3665 per hart, so the shared front end, not the VPU, is the limit. |
| S11 | C19 C85 C86 C87 C88 C89 C91 | **REFUTED (internally)** | Six of the seven §6 rows disagree with the page's own simulator, mostly because an E46 delta wearing a "k = 0..256" label is the model's k = 128 value: E-D1 +4.52 vs 8.89 W, E-D2 +3.73 vs 8.01 W, E-D3 +4.40 vs 9.18 W, E-D4 0.6–1.4 vs 2.58 W span, E-D5 0.15–0.45 vs 0.295 W. Only E-D6 matches its simulator, and its premise is S3. Every row is still scored tonight as a prediction. |
| S12 | C48 C49 C51 C52 C81 | **REFUTED / unsourced** | 19.65 W card idle (measured ~31.8 W at 73 °C, ~36 W at 80 °C); "0.03 W power floor" is the *zeros* pattern's run-to-run repeat spread, not a sensor floor (the documented detection line is σ/precision = 3.33 W); 167 mA and 49.5 mK/W have no provenance; 3.2 mK is the camera's **20 s** figure, not its 5-minute one (1.3 mK at 60 s, 0.6 at 300 s), so E-D7 is ~5× easier than claimed and the printed number is still wrong. |
| S13 | C10 C82 | **REFUTED** | 1,088 minions in 34 shires, 1,024 running kernels. Worse for E-D7: the host's own `MESH` table (`main.cpp:321-327`) puts shires 0–15 in **every** mesh column (0–5, re-verified), so "West 0–15 / East 16–31" is not a spatial split and would modulate the whole die. No 16/16 vertical or horizontal cut exists; see §10. |
| S14 | C24 C25 C27(1–6) C32 C36 C37 C39 C40 C41 C66 C80 | **HOLDS** (the page's mining, where data exists) | 13.148 / 13.158 / 13.661 ✓; +7.353 / +5.995 / +5.859, gap 24% ✓; six rows to ±0.01 pJ ✓; `fsll.pi` +4.657, `fswizz.ps` +5.311, `fbcx.ps` +5.237 ✓; `fadd.pi` const − zeros +0.054 ✓ (the one real const value on the page); every E-D6 bit pattern decodes, 23/24 = 95.8% ✓. C39's 2.09× is arithmetic but not a width-only comparison (the flip counts also differ 4×). |
| S15 | C06 C09 | **PARTLY** (denominator superseded, 26 Oct 2026 — see the note under this table) | ~1,050 toggles per flipped input bit is arithmetically real and sourced — 21,331 counted toggles ÷ 20.3 bits on **`txfma_top`**, the tensor unit, not the vector `fmadd.ps` the page attaches it to. 🛑 But 21,331 is now known to be a count of **names under one Verilator, not of wires**, so both it and the ~1,050 it divides down to are superseded: see the note below. 8.8 fF per clocked bit is the one figure corroborated across documents; 8.0–11.8 fF per logic toggle is 9–13× the only per-toggle capacitance with a fit behind it (0.90 fF). |
| S16 | C17 C18 C44 | **SETTLED BY E60** | The split is 1.50 : 1, not 6.81 : 1; the sum (50.90 fJ) was the only thing the catalogue ever fixed, and the page got it to 98% while splitting it wrongly. 0.517 V is aifoundry2's 21 Sep point; the only clock-pinned card is aifoundry3 at 0.522 V, and the page puts every run on aifoundry2, which is governor-free at 800 MHz / 0.617 V (C59 again). |
| S17 | C92 C93 | **PARTLY** | Paths are right and "zero firmware changes" is right — tonight's build tests it. But "extend `enercat.c` with op_id 31..42" does not describe this harness: bodies are generated into an `.inc` and dispatched by name, the catalogue already holds 392 configurations, and four of the page's experiments need no new kernel at all because `--operands file:<256 B>` already exists. |

### The 21,331 denominator was recounted (Q126, 26 Oct 2026)

S15 and C29 above both divide by the bench's **21,331 toggles per random fp32 multiply-add**. That number
has since been taken apart, and nothing in this file was re-derived on the new one — read every per-toggle
figure here with the denominator below, not with 21,331.

| What was counted | Per random multiply-add | Where |
|---|---|---|
| the bench's own counter, as quoted here | 21,331 *names* under Verilator 5.042 (re-runs as 21,379) | `docs/reports/data/2026-09-21-horace-aifoundry2/toggles.json` |
| the same bench, same tiles, Verilator 5.052 | **7,014** | `TR/toggles-5052.json` |
| the counter defect, measured inside ONE traced run | coverage counter 21,297 against that run's own VCD 7,233 — **2.94×**, and all of it in `txfma_csa` and `txfma_4_2_compressor` (8.45×; every other module 0.98×) | `TR/verilator-5042-vcd.json` |
| each **physical** net counted once (job (b)) | **1,301** (1,325 at a 512-cycle window) — a floor | `TR/recount.json`, `randn.mean.nets_hier` |
| an independent count on real wires (the open netlist) | **3,299** unique nets for the whole unit, 3,623 with the hierarchy kept | `docs/reports/data/2026-10-26-open-netlist/` |

`TR/` is `docs/reports/data/2026-10-26-toggle-recount/`. Two physical counts still disagree 2.5× (1,301
against 3,299) and that is the live dispute; the 2.9× one this file was written under is settled. Each row
is in `docs/findings/05-claims.md` with its file and field (Q126(b), Q126(e)). So **~1,050 toggles per
flipped input bit** is 21,331 ÷ 20.3 and inherits the whole defect: on the per-net floor the same division
gives ~64, on the open netlist's whole-unit count ~163.

---

## 2. What tonight's runs test

| the page's claim | family | the quantity that decides it |
|---|---|---|
| C13 C15 — a one-gate-deep bitwise op flips exactly k designed bit-slices, no carry, no glitch | every family | the designed counts re-derived from the operand files on disk (`make_dtf.py --check`), the `objdump` walk of the built ELF, the ten `sys_emu` runs, the on-card smoke block, and the per-run ec rate / `ok` / `participants` gates (§8.2) |
| C33 C37 C60 — the `fnot.pi` leg, and "an inverter is cheap because 2 FETs vs 10–12" | **N**, **gate ladder** | fJ per (port + result) bit through a 1-FET-deep inverter vs an XOR at matched counts (one port vs two, stated as a confound), **and** the three-opcode gate ladder at *identical* port count and identical designed counts |
| C61 C62, I-22 — is the VRF **cell** flip separable from e_out? | **V** | 1B − 1A at matched everything-but-cells = fJ per flipped register-file **cell bit** (not "the VRF write": bitline and wordline drive is common-mode — §4 family V) |
| C14 C56 C57 C63 C64 C65 C86 — the input/output bridge; "zero writeback wires flip"; the NMOS/PMOS clamp | **B** | (B+D) − (A+C) at matched everything = 16h·e_out + c·w, with the changed-word term w fitted and its multiplier c registered per mechanism reading (§5.1) |
| C54 C66 C67 C68 C87 — "~14 fJ per carry stage" | **C** | slope/8 − e_out(add) = e_carry per bit position of carry propagation (ripple-equivalent), with curvature in L as the adder-topology test |
| C47 C55 C69–C73 C88 — the Miller wire law, k_adj at fixed k | **M** | the spread across four *occupancy-matched, zero-word-free* k_adj levels at identical designed counts, plus a complement-symmetry control |
| C46 C74 C75 C76 C89 — the 5-bit address bus, predecoder and wordline drivers | **A** | the slope against register-index Hamming distance, in both the gated (all-zero data) and the live (all-nonzero-equal data) regimes |
| C79 C80 C90 — the zero-gate step and its four constants | **Z** | `d6_one − d6_zero` in fJ/op |
| C58 C83 C84 C91 (part) — the half-die dipole amplitude and ΔP_card ≡ 0 | **B** (tier 1), **7** (tier 2) | the result-path load per half-die on the board meter; W-vs-E board equality; the camera's permutation-calibrated double difference at ~53 s dwell |
| C22 C23 C26 — the operand law, and whether 2-hart interleaving destroys operand sharing | **R** | `fnot.pi` random − const ÷ 95.556 against 52.00–53.10 fJ; the **rate-free ratio** of `fand.pi` per-op deltas at `--harts` 2 vs 1 against 1.000 / 1.12–1.14 |
| *(no page claim)* — does a zero operand word gate a lane? | **N** (primary), B, C, M (replications) | every page-exact item is paired with a nonzero-word control at identical designed counts; the functional form is fitted before it is applied anywhere |

---

## 3. What is not testable tonight, and why

| claims | why not |
|---|---|
| C07 — "a node glitches 0→1→0 two or three times inside one 1.67 ns period" | Needs a timing-annotated gate-level simulation. The lab has none, and no card measurement or cycle-accurate sim can settle a sub-cycle count. Untestable in principle here — the page's own reason for raising it. |
| C06 (as applied to vector `fmadd.ps`) C94 | The committed toggle bench (`rtl-sim/fma_toggle/`) covers `txfma_top` only. A VPU bitwise/adder bench is new tooling, not a card run. |
| C08 C09 — the 8.8 / 11.8 / 8.0 fF fits | A fit on the FMA path against RTL net counts. Vector-unit board power cannot separate clocked bits from logic toggles without those counts. |
| C11 C12 — the architecture prose | Documentation, not a measurement; both substantially right. |
| C49 C81, C84's 110 mK, C58's mK figures | Need a camera calibrated **on this card**: no contact thermometer, no black-vinyl patch, no flat field, fixed pattern 0.6 °C across the frame (≈17× the frame noise), whole field drifting +0.7 °C in 4 min tonight with every card idle. Phase and differences are usable; absolute mK and mK/W are not. |
| C82's West/East **map** | Needs per-sensor die temperature — the 35 Moortec sensors at 0.061 °C, which need a signed firmware image (improvement-ladder rung 12). Excluded by the stock-firmware rule. Tonight the camera can show the pattern *moves*, not that it maps to shires 0–15. |
| C95 — a 15-period 0.05 Hz lock-in at constant total power | Needs the in-kernel dipole: a new hand-written kernel case **plus** three raised timeouts (launch-stream 6 s, `Session::overBudget` 9.5 s, runner hold 10 s). Deferred to E62; §10 says what replaces it tonight. |
| C29 — "about 5,600 toggles per op" | On an unstated basis and absent from the corpus (the figure committed when this was written was 21,331 per random multiply-add; the physical counts are now 1,301–3,299 — see the recount note in §1). No run can score an unstated basis. |
| C02–C05 (S1) | Settled by the record, not by a run. |
| **the written register values, on silicon** | The on-silicon register dump is **not implemented** tonight (§7). Each shape's values are verified in the generator, in the ELF and in `sys_emu`; on the card the evidence is the rate, `ok` and `participants` gates. A value corruption that leaves the op count and the participant count intact would not be caught — stated in §11. |

---

## 4. The families and the items

Every item is a 256-byte operand image (`--operands file:`, which the host already accepts and hands to **every**
hart: `main.cpp:243-251`, exactly 256 B or it throws), except family R's `const` and `random` arms.
`make_dtf.py` writes each image, re-derives its counts from the bytes on disk, and writes `manifest.json` +
`gen.sha256` before the first measured pass.

Layout, verified from `kernel/enercat.c:40-46`: register f*N* = bytes 32N…32N+31, lane *l* of f*N* = the
little-endian `uint32` at byte 32N + 4*l*. `load_vsrc` issues `mov.m.x m0, zero, 0xff` then
`flw.ps f0,0(%0) … f7,224(%0)`. `RUN` repeats the block **eight times** per iteration, so `ops_per_iter` =
8 × (ops in the block): 64 for an 8-op shape, **128 for a 16-op shape**.

*h* is the mask weight per 32-bit lane, so a flipping port carries 8*h* bits per 256-bit op (the page's *k* = 8*h*).
**The mask is spelled once, here: `m(h)` = the low *h* bits** (`0x0000FFFF` at h = 16, `0xFFFFFFFF` at h = 32),
exactly as E60's `make_hl.py` `low_mask` does, so every copied and every new item shares one Miller phase at a
given h. **Every run on a new `df.*` mode is `--harts 1`**; the only `--harts 2` runs in the programme are family
R's two `fand.pi` arms on existing mode 177.

### Family X — cross-campaign ties (existing mode 179, no new anything)

`xin_h0`, **`xin_h8`**, `xin_h16`, `xin_h32`, and on aifoundry1 c0 also **`ain_h8`** and `ain_h32`. **The files
are copied byte-identical from E60's `build/hl-gen2`** and checked by sha256 against `gen-a1.sha256`. They put E61
on E60's measured scale without re-deriving it, and three nonzero rungs make the **ladder intercept a fitted
quantity with a degree of freedom left over for curvature**. `xin_h16` doubles as family M's reference: every
Miller item has `xin_h16`'s exact designed counts.

**`ain_h8`, not `ain_h32`, is the `fand.pi` price tie.** At h = 32 `ain`'s x is the all-zero word (`make_hl.py`:
x = random & ~m with m = `FFFFFFFF`), which is why E60's amendment A1 excluded `ain_h32` from every e_in fit; the
28.10 ± 0.70 fJ `fand` price came from h = 8. `ain_h32` is kept **only** as a drift tie and as the deliberate
zero-word corner.

### Family N — the `fnot.pi` dial, its zero-word control, and the intercept discriminator (mode 202, operand files only)

`d1n_h{0,8,16,32}` is the page's E-D1b **verbatim**: f0=f2=f4=f6 = `00000000`, f1=f3=f5=f7 = m(h).
`d1nz_h{0,8,16,32}` is the same ladder with no zero word anywhere: f_even = `5A5A5A5A`,
f_odd = `5A5A5A5A ^ m(h)` (at h = 32 that is `A5A5A5A5`; `~5A5A5A5A` = `A5A5A5A5` and `~A5A5A5A5` = `5A5A5A5A`,
so **neither operand nor result is ever zero at any h**). Designed counts identical, so `d1n − d1nz` at equal h
**is** the zero-operand price, the corner E60's amendment A1 could only label. (Registered: at h = 32 the `d1n`
arm's result is `~FFFFFFFF` = 0 every other op, so that rung carries a zero *result* word as well as a zero
operand — it is the page's design, and h = 8 and h = 16 are the clean rungs.)

**N also carries the mechanism discriminator for E60's +0.273 W intercept**, which is why it has four rungs. N is
a one-port unary shape: 8 changed source words/op against X's 16. The three live readings of the intercept
predict, for `d1nz` (whose results are never zero at any h):

| reading of E60's +0.273 W | what the term is per | N's predicted intercept | does it bias the B bridge? |
|---|---|---|---|
| **R1** | changed 32-bit **source** word (48.0 fJ each) | **+0.137 W** | no — all four B arms change 8 source words/op |
| **R2** | changed 32-bit word on **any** bus (48.0 fJ each) | **+0.273 W** | **yes, +0.273 W**: B and D change 8 source + 8 result words, A and C only 8 |
| **R3** | the **result word leaving zero** (a one-time step) | **≈ 0** | no — no B arm's result changes zero-ness between h = 0 and h > 0 |

A three-way discriminator with the readings 0.137 / 0.273 / 0.000 W apart, against a per-item SE of ~0.026 W on
the pinned card — measured in the same passes as the bridge it corrects.

### Family V — the register-file **cell** bit (new 16-op shapes; the page's 1A/1B, rebuilt so it can work)

The page's own 1A/1B cannot measure anything: with a static operand image and a fixed (dest, source) pairing every
sink is rewritten with the identical value forever, so **no register cell flips in 1A or 1B**, and its alternative
("one destination, f8, f8, f8…") is an eight-deep write-after-write chain whose issue rate differs, so the
subtraction would return the pipeline, not the SRAM. Rebuilt as a 16-op pair:

- **1A** (`df.un1a.fnot`, mode 304): two identical halves, `fnot.pi f8,f0 / f9,f1 / … / f15,f7` twice. Each sink
  always receives the same value → **0 cell flips**.
- **1B** (`df.un1b.fnot`, mode 305): first half as 1A; the second half's destinations **rotated by three**
  (f11,f12,…,f15,f8,f9,f10 against sources f0…f7). Register f(8+j) is then written by f_j and by f_{(j−3) mod 8} —
  opposite parity, so it alternates and **8h cell bits flip every op**.

Rotate by three, not one: rotate-by-one puts two writes of f8 back to back across the block boundary, and any
*even* rotation pairs two sources of the same parity, which holds the cell static and returns a null for the wrong
reason. With rotate-by-three the minimum distance between two writes of one register is 3 ops; the source stream,
the result-value stream, the opcode and the op count are **identical** between 1A and 1B, and the only designed
difference is 8h cell bits plus 0.125 write-address bits per op (0.05% of the signal; carried in the manifest so
the reduction can subtract it). Items `d1a_h{0,16,32}` / `d1b_h{0,16,32}` — the h = 16 rung exists because the
registered rule asks the difference to *scale with h*. `h0` is the pair's own null: at h = 0 nothing flips in
either, so a non-zero difference there means the two shapes differ for a reason other than cells.

**What this measures.** Both arms write one register per op, assert the same wordline and drive the same bitlines
with the same data stream. The only designed difference is whether the addressed cell's **stored state** changes.
The bitline and wordline write energy is **common-mode** and sits in the per-op intercept, where this contrast
cannot see it at all. So the quantity is **energy per flipped register-file cell bit**, prior **0.3–3 fJ** (½CV²
on a few fF at 0.52 V) — and a null here says the cell flip is cheap, which is what ½CV² predicts. It does **not**
say the write is "inside e_out"; that inference is withdrawn.

### Family B — the input/output bridge as a 2 × 2 (new `c2` shape)

The rotating block cannot hold a port still — op i reads (f_i, f_{i+1}), so port 2 is port 1 delayed by one op and
the two are collinear. E-D2 and E-D3 both need a held operand, so one new shape serves both:

```
op f8,f0,f7   op f9,f1,f7   op f10,f2,f7   op f11,f3,f7
op f12,f0,f7  op f13,f1,f7  op f14,f2,f7   op f15,f3,f7
```

**The images, spelled:** f0 = f2 = **x = `5A5A5A5A`**, f1 = f3 = **y = `5A5A5A5A ^ m(h)`**, f7 = the held word.
(x = 0 would have put a zero word on the flipping port and recreated exactly the `ain_h32` corner E60 excluded.)
Four rotating sources, **f7 held**, eight distinct sinks each written once per block. vs1 flips 8h bits every op
including the block wrap; vs2's value and address never change; no sink ever changes value, so no cell flips;
address traffic is a constant 3.25 bits/op. The 2 × 2 is {`fand.pi`, `for.pi`} × {held `00000000`, held
`FFFFFFFF`}:

| item | mode | opcode | held f7 | result | zero word? |
|---|---|---|---|---|---|
| `d2A_h*` | 300 | `fand.pi` | `00000000` | static 0 — **the page's Run A** | yes (held, and result) |
| `d2B_h*` | 300 | `fand.pi` | `FFFFFFFF` | = vs1, flips 8h — **the page's Run B** | no |
| `d2C_h*` | 301 | `for.pi` | `FFFFFFFF` | static all-ones — **the page's Run C** | no |
| `d2D_h*` | 301 | `for.pi` | `00000000` | = vs1, flips 8h | yes (held only) |

Why the fourth cell is not optional: the page's three runs confound e_out with the opcode (A is AND, C is OR —
their own zeros baselines differ by 0.50 pJ) and with the zero held operand. The 2 × 2 separates both. Writing
P = α(opcode) + 8h·e_in + n_res·e_out + c_w·w + g_op·[held = 0] + g_res·[result = 0]:

- **(B+D) − (A+C) = 16h·e_out + (c_w,B + c_w,D − c_w,A − c_w,C)·w − g_res**, where the w multiplier is **+16
  changed words/op under reading R2 and 0 under R1 and R3**, and g_res is carried by `d2A` alone (the only arm
  with a zero result).
- **(B−A) − (D−C) = 2·g_op + g_res** — *not* "2 × the zero-operand effect".
- The h = 0 rungs give the four intercepts with nothing flipping at all, and remove α(opcode) per cell; they do
  **not** remove w (at h = 0 no word changes in any arm) and they remove g_op/g_res only if those are static per
  op, which E60's `xio`/`xnz` pair (−3.8% **per result bit**) says they are not — hence §8.6.

This is the highest-value item in the programme: a within-family e_out with α cancelled, which E60 could only
reach by subtracting one family from another.

### Family gate — the three-opcode gate ladder at matched counts (`c2`)

A `fnot.pi`-vs-`fxor.pi` comparison would compare a one-port op with a two-port op, so gate depth would not be
separable from port count. Within `c2` with **held f7 = `00000000`**, three opcodes all give result = vs1 with 8h
result flips, two read ports, identical sinks, identical address traffic and **zero carries**:

| item | mode | opcode | result | what it adds |
|---|---|---|---|---|
| `d2D_h{0,32}` | 301 | `for.pi` | vs1 \| 0 = vs1 | already in family B |
| `d2X_h{0,32}` | **303** | `fxor.pi` | vs1 ^ 0 = vs1 | the XOR rung of the gate ladder |
| `d3z_h{0,32}` | 302 | `fadd.pi` | vs1 + 0 = vs1, **no carry nodes** | the ADD rung; **also** tests whether e_out is opcode-independent (the assumption family C imports) and gives e_in(add) + e_out(add) directly |

The gate contrast is OR vs XOR vs ADD at *identical* designed counts and *identical* port count, and the `fnot`
leg is reported against it **explicitly as a one-port/one-gate versus two-port/one-gate comparison**. The
registered conclusion from either is a **bound on the total gate contribution** (expected a few percent of
26.00 fJ per bit), never an attribution to FET count.

### Family C — the carry ladder (`c2` shape, mode 302 `fadd.pi`)

`d3_L`: f7 held = A_L = (2^L − 1) | `80000000`, vs1 alternating `40000000` ↔ `40000001`. Adding 1 to a run of L
ones flips carries c1…cL and sum bits 0…L; bits 30 and 31 are static ones that keep **no operand and no result
ever zero**, and L ≤ 29 so nothing interacts with them. L ∈ {0, 2, 8, 16, 29}. `d3p_L29` is the page's exact
design (A_L = 2^L − 1, vs1 `00000000` ↔ `00000001`), which puts a zero operand on the toggling port every other
op.

Registered limitations: (i) result bits = 8(L+1) and carry nodes = 8L are collinear, so this family alone cannot
split a sum bit from a carry node. e_carry exists only as **slope/8 − e_out(add)**, with e_out(add) from `d3z` —
the same opcode, the same shape, the same pass — never imported from `fand`/`for`. (ii) **"Carry nodes = 8L" is
the ripple count.** On a parallel-prefix adder the number of toggling internal nodes for a carry propagating L
positions is not L, so the quantity is named **energy per bit position of carry propagation
(ripple-equivalent)** and **curvature in L is the topology test**: fit L and L·log₂L over the five rungs and
report both, since a prefix tree gives a sublinear slope.

### Family M — the Miller set (existing mode 179, operand files only)

All six patterns are built at **8 active lanes × 16 flipping bits per lane** — exactly `xin_h16`'s designed
counts — and every one is **zero-free in both operands and the result**, re-derived from the bytes (f_even = x,
f_odd = y, result = x ^ y constant):

| item | x → y, all 8 lanes | k_adj | flips/word | zero word |
|---|---|---|---|---|
| `m_phase0` | `FFFF0000` → `FFFFFFFF` | **0.031** | 16 | no (result `0000FFFF`) |
| `m_nib` | `33333333` → `66666666` | **0.969** | 16 | no (result `55555555`) |
| `m_nib_c` | `CCCCCCCC` → `99999999` | **0.969** | 16 | no (result `55555555`) |
| `m_pair` | `22222222` → `11111111` | **1.469** | 16 | no (result `33333333`) |
| `m_byte` | `05050505` → `0A0A0A0A` | **1.719** | 16 | no (result `0F0F0F0F`) |
| `m_solid_z` | `00000000` → `FFFFFFFF` (lanes 0–3), lanes 4–7 held `00000000` | 0.000 | 32 | **yes — page-exact, kept as a separately labelled confounded extra** |

**The k_adj convention, stated:** per flipping wire, (2 × anti-phase neighbours + 1 × static neighbours) / 2,
summed over flipping bits and divided by their count, with no wrap at the word boundary.

Four distinct k_adj **levels** (0.031, 0.969, 1.469, 1.719) at matched occupancy and matched counts, with
`m_nib`/`m_nib_c` an exact bitwise-complement pair at the same level — the **complement-symmetry control** a
capacitive effect must pass. What still rests on an unverified assumption is that **bit index equals physical wire
adjacency**; that is said in the result, not discovered later.

### Family A — the address ladder (new `addr` shapes, modes 306–309), in two data regimes

`d5_a{0,1,3,5}`: `fxor.pi f{8+i}, fR, fR` with R alternating f0 ↔ {f0, f1, f7, f31} — register-index Hamming
distance Δ ∈ {0, 1, 3, 5} on both read ports, 2Δ + 1.75 address bits per op (the 1.75 is the f8…f15 destination
cycle, common to every rung, so it cancels). The image is 256 zero bytes and f30/f31 are zeroed in the prologue,
so **every data count is exactly zero**.

That is also the one regime where the data path, and possibly the decoder, is maximally gated — every operand word
is the zero word, exactly the condition the lab believes gates a lane. So two items run the same ladder with
**live operands**: `d5n_a{0,3}`, image = all eight registers hold `5A5A5A5A` (every word nonzero and every word
equal, so every data count is still exactly zero while the operands are live), Δ from f0 ↔ {f0, f7}. The
gated-vs-live pair at matched Δ is the test of whether gating reaches the address path. Registered: `f ^ f` = 0,
so **both** regimes have an all-zero *result* word by construction — the family bounds the address path with the
result path gated in both arms, and the pair answers only the operand-side question.

Three deliberate departures from the page: eight distinct sinks (the page's `fxor.pi f0,f0,f0 ×8` is a serial RAW
chain on f0 whose issue rate collapses and whose fetch power moves far more than the 0.05 W signal); vd kept out
of the ladder; and f31, not f15, for Δ = 5 so no sink is ever read.

**Prologue, against the repo's own rule.** Errata 1.29 is *"a VPU register read in the cycle after a write can
return stale data"*, with ≥ 8 independent instructions, a taken branch or a forcing sequence for Type B/C
consumers — **not** "a register written by a broadcast must not be read for ≥ 8 instructions". The documented fence
is `fmv.x.w x0, fN` (`docs/et-soc1-notes.md:337`; `nocbench.c:138` does exactly this after its own f30/f31
writes). Order, **outside `RUN`** (`RUN` replays its body eight times per iteration, so a prologue inside it would
make `ops_per_iter` 88 instead of 64 and every price 27% wrong with nothing else complaining):

```
mov.m.x m0, zero, 0xff
fxor.pi f30, f0, f0        # f ^ f = 0 whatever f held: no broadcast needed
fxor.pi f31, f0, f0
fmv.x.w x0, f30            # errata 1.29 type F fence, et-soc1-notes.md:337
fmv.x.w x0, f31
load_vsrc                  # 9 instructions
RUN
```

### Family Z — the zero-gate step (existing mode 191, operand files only)

`d6_zero` (`00000000`), `d6_one` (`3F800000` = the catalogue's `const`). All eight registers hold one constant, so
all three read ports see it, the result c·c + c never changes and no sink changes value: **every designed count is
zero** and only the address rotation moves, identically in both. `d6_one − d6_zero` is exactly the catalogue's
zeros → const step, re-measured at `--harts 1` on tonight's protocol. The page's `00800000` is **excluded**:
c·c = 2⁻²⁵² is subnormal and may take a slow path. `d6_e96m0` (`30000000`) and `d6_mantones` (`3FFFFFFF`) are the
first *extension* if a card finishes early, not part of the registered list.

### Family R — reconciliation, with `const` baselines and a rate-free statistic

The baseline arm is **`--operands const`** (every word `0x3F800000`, `main.cpp:277`), not `zeros`, so neither arm
of any delta carries a zero operand word and the zero-word effect cannot masquerade as the count-model difference.
The decision statistic is a **ratio of per-op deltas**, not a watt difference: at `--harts 2` each hart retires
0.3665 instructions/cycle against 0.5791 at `--harts 1`, so the card executes ~1.27× more ops/s and the two arms
are not comparable as watts. A ratio divides out the rate, the card scale **and** most of the intercept.

- `r_not_c1` / `r_not_r1` (`fnot.pi`, const / random, `--harts 1`): the model-free leg, whose counts are 95.556 in
  and out independent of both the block pairing and hart interleaving, so the delta ÷ 95.556 is e_in + e_out with
  no modelling choice — **after subtracting family N's measured intercept**, the `fnot` intercept in fJ/op on the
  same card and the same night (§5.3).
- `r_and_c1` / `r_and_r1` / `r_and_c2` / `r_and_r2` (`fand.pi`, both harts settings): the statistic is
  **ρ = (harts-2 per-op delta) / (harts-1 per-op delta)**.

### Family 7 — the spatial halves (mode 300 with `--shires`; its own contiguous block, §10)

`d7w_hi`, `d7e_hi`, `d7w_lo`, `d7e_lo`: `d2B_h32` (loud: 256 result bits/op) and `d2A_h32` (quiet) restricted to
`--shires 0x3131733b` (West) and `0xcece8cc4` (East). Re-verified from `MESH`: 16 shires and **512 participating
harts** a side, West = the x ≤ 2 set {0,1,3,4,5,8,9,12,13,16,20,21,24,28,29} plus shire 14 at (3,2), East its
exact complement. Same work, same total power, different place. No new kernel code beyond the DF set. These run as
a **separate contiguous-block experiment** (`dtf-cam`), not inside the shuffled electrical pass, and each side has
its **own** zero rung at its **own** shire mask.

### Designed counts, per 256-bit op (what `make_dtf.py --check` re-derives from the bytes)

| item | mode / shape | ops/iter | vs1 | vs2 | result | dest cell | carry | addr | zero word |
|---|---|---|---|---|---|---|---|---|---|
| `xin_h0`/`h8`/`h16`/`h32` | 179 rot2 | 64 | 0/64/128/256 | 0/64/128/256 | 0 | 0 | 0 | 5.25 | no |
| `ain_h8` / `ain_h32` | 177 rot2 | 64 | 64/256 | 64/256 | 0 | 0 | 0 | 5.25 | h32 only (x = 0) |
| `d1n_h0`/`h8`/`h16`/`h32` | 202 un | 64 | 0/64/128/256 | — | 0/64/128/256 | 0 | 0 | 3.50 | **yes** |
| `d1nz_h0`/`h8`/`h16`/`h32` | 202 un | 64 | 0/64/128/256 | — | 0/64/128/256 | 0 | 0 | 3.50 | no |
| `d1a_h0`/`h16`/`h32` | **304** un1a | **128** | 0/128/256 | — | 0/128/256 | **0** | 0 | 3.50 | no |
| `d1b_h0`/`h16`/`h32` | **305** un1b | **128** | 0/128/256 | — | 0/128/256 | **0/128/256** | 0 | 3.375 | no |
| `d2A_h0`/`h16`/`h32` | 300 c2 fand | 64 | 0/128/256 | 0 | 0 | 0 | 0 | 3.25 | **yes** |
| `d2B_h0`/`h16`/`h32` | 300 c2 fand | 64 | 0/128/256 | 0 | 0/128/256 | 0 | 0 | 3.25 | no |
| `d2C_h0`/`h16`/`h32` | 301 c2 for | 64 | 0/128/256 | 0 | 0 | 0 | 0 | 3.25 | no |
| `d2D_h0`/`h16`/`h32` | 301 c2 for | 64 | 0/128/256 | 0 | 0/128/256 | 0 | 0 | 3.25 | **yes** (held only) |
| `d2X_h0`/`h32` | **303** c2 fxor | 64 | 0/256 | 0 | 0/256 | 0 | 0 | 3.25 | **yes** (held only) |
| `d3z_h0`/`h32` | 302 c2 fadd | 64 | 0/256 | 0 | 0/256 | 0 | **0** | 3.25 | **yes** (held only) |
| `d3_L0`/`L2`/`L8`/`L16`/`L29` | 302 c2 fadd | 64 | 8 | 0 | 8/24/72/136/240 | 0 | 0/16/64/128/232 | 3.25 | no |
| `d3p_L29` | 302 c2 fadd | 64 | 8 | 0 | 240 | 0 | 232 | 3.25 | **yes** |
| `m_phase0`/`m_nib`/`m_nib_c`/`m_pair`/`m_byte` | 179 rot2 | 64 | 128 | 128 | 0 | 0 | 0 | 5.25 | **no (all five)** |
| `m_solid_z` | 179 rot2 | 64 | 128 | 128 | 0 | 0 | 0 | 5.25 | **yes (page-exact)** |
| `d5_a0`/`a1`/`a3`/`a5` | **306–309** addr | 64 | 0 | 0 | 0 | 0 | 0 | **1.75 / 3.75 / 7.75 / 11.75** | yes (all data 0) |
| `d5n_a0`/`a3` | **306 / 308** addr | 64 | 0 | 0 | 0 | 0 | 0 | **1.75 / 7.75** | no (operands live) |
| `d6_zero` / `d6_one` | 191 fused | 64 | 0 | 0 (×3 ports) | 0 | 0 | 0 | 7.00 | `d6_zero` only |
| `r_not_c1`/`r_not_r1` | 202 | 64 | 0 / 95.556 | — | 0 / 95.556 | 0 | 0 | — | no |
| `r_and_c{1,2}`/`r_and_r{1,2}` | 177 | 64 | 0 / 191.111 | 0 / 95.556 | 0 / 48.370 shared | 0 | 0 | — | no |
| `d7{w,e}_{hi,lo}` | 300 c2 fand, 16 shires | 64 | 256 | 0 | 256 / 0 | 0 | 0 | 3.25 | `lo` only |

**Changed 32-bit lane words per op** (the `src_words` / `res_words` fields, which carry §5.1's intercept
regressor; a word counts once per bus per op if any of its 32 bits changes between consecutive ops):

| shape | src_words | res_words |
|---|---|---|
| rot2 at h ≥ 1 (X, the five zero-free M items, `r_and_r*`) | 16 | 0 |
| `m_solid_z` (4 active lanes) | 8 | 0 |
| unary at h ≥ 1 (N, V's `d1a`/`d1b`, `r_not_r1`) | 8 | 8 |
| `c2`, result static (`d2A`, `d2C`, `d7*_lo`) | 8 | 0 |
| `c2`, result flips (`d2B`, `d2D`, `d2X`, `d3z` at h = 32, every `d3_L` and `d3p`, `d7*_hi`) | 8 | 8 |
| every h = 0 rung, every `const` arm, `d5*`, `d5n*`, `d6_zero`, `d6_one` | 0 | 0 |

So the intercept cancels along the C, A, Z and M contrasts (both rungs change the same words) and is present in
X's, N's and B's h-ladders — which is what §5.1 corrects.

`make_dtf.py --check` asserts the zero-word column **per 32-bit lane word**, not per 256-bit register, because the
lab's gating hypothesis is per lane (`make_hl.py` line 18: *"the chip gates a lane whose operand word is zero"*),
and it checks operands **and** results.

### manifest.json

One object: `{"seed", "modes": {name: id}, "items": [...]}`. Each item carries `name`, `family`
(X N V B gate C M A Z R 7 anchor), `kind` (`ec`, or `fma` for `anchor_pi`), `op` (the `--pattern`), `operands`
(`file` | `const` | `random`), `harts` (1, or 2 for R's two interleaved arms), `shires` (null or the `0x…` mask),
`ops_per_iter`, `zero` (the name of this item's family zero rung, or null), `h`, `L`, `delta` (null when not
applicable), `counts` (`vs1`, `vs2`, `result`, `cell`, `carry`, `addr`, `src_words`, `res_words`), `zero_word`,
`dup` (runs per pass, 1 or 2), `participants_expected` (1,024, or 512 for family 7 = 32 × popcount(mask)), and
`pair` (the matched partner's name, or null). The reduction reads `zero`, `dup`, `pair` and
`participants_expected` from this file rather than from a literal dict in the code — `reduce_hl.py:30`'s `ZERO`
dict is exactly how code and a pre-registration drift apart.

---

## 5. Registered predictions and targets

### 5.0 How every target is stated

1. **In fJ per designed flip, computed per run from that run's own completed-op count** — never in watts. The watt
   columns below exist only to size the runs, pick the power ceiling and feed the camera. Four of the new shapes
   have never executed (`c2`, `un1a`, `un1b`, `addr`), the ec rate gate is family-internal, and a 10% IPC
   difference in `c2` would move a watt-stated bridge value by 0.57 W ≈ 11 SE.
2. **As an interval, never a point.** The defensible E60 readings are themselves 7–11× the registered SE:
   **e_out ∈ [30.00, 31.17] fJ** (`xio`/`xnz`, same card, same night), **e_in ∈ [19.7, 20.9] fJ** (the joint fit
   gives 20.83 ± 0.10, the `xin`-ladder fit that produced the intercept gives 19.71), **e_in(fand) = 28.10 ±
   0.70 fJ** (one rung, h = 8). A target is that interval widened by the new statistic's own 3-SE-equivalent
   window (§9 rule 1).
3. **With the intercept's mechanism named.** Every target whose zero rung has no changing source word carries the
   intercept; §5.1 says which, and family N decides the multiplier.

### 5.1 The intercept, per target

E60's fitted **+0.273 W = 767.3 fJ/op = 48.0 fJ per changed 32-bit source word** (16 words/op in rot2). Where the
zero rung of a comparison has nothing changing and the nonzero rung does, the step is present:

| target | base (ours, 600 MHz) | R1 (+48 fJ/source word) | R2 (+48 fJ/any word) | R3 (result leaves zero) |
|---|---|---|---|---|
| `d1nz_h32 − d1nz_h0` | 4.736 W | **+0.137 → 4.873** | **+0.273 → 5.009** | +0 → 4.736 |
| `d1n_h32 − d1n_h0` | 4.736 W | +0.137 → 4.873 | +0.273 → 5.009 | +0.137 → 4.873 (`d1n`'s h32 result is 0 every other op) |
| `d2A_h32`, `d2C_h32` (result static) | 2.559 W each | +0.137 → 2.696 | +0.137 → 2.696 | +0 → 2.559 |
| `d2B_h32`, `d2D_h32` (result flips) | 5.398 W | +0.137 → 5.535 | +0.273 → 5.671 | +0 → 5.398 |
| **(B+D) − (A+C)** at h = 32 | **5.678 W** | **+0 → 5.678** | **+0.273 → 5.951** | +0 → 5.678 |
| (B−A) − (D−C) | 0.000 W | +0 | +0 | +0 |
| `r_not_r1 − r_not_c1` | 1.768 W | +0.137 → 1.905 | +0.273 → 2.041 | +0 → 1.768 |
| `d3`, `d5`, `d6`, the M contrasts | — | **cancels** | cancels | cancels |

So **the bridge is biased by exactly +0.273 W, and only under reading R2** — on a 5.678 W quantity that is +4.8%,
or 3–11 SE against the realised per-item SEs, enough to score E60's own e_out as REFUTED while confirming nothing.
The fix is structural: **e_out is quoted from the §8.5 joint fit, which carries "changed 32-bit words/s" as a
regressor**, and the raw combination is reported beside it with the 16w term subtracted explicitly under whichever
reading family N's intercept selects.

### 5.2 Per-flip energies — ours, the page's, and the new coefficients

- **e_in into `fxor.pi`** 20.83 ± 0.10 fJ (interval [19.7, 20.9]) · **e_out** [30.00, 31.17] ± 0.17 ·
  **e_in into `fand.pi`** 28.10 ± 0.70 fJ. **`for.pi` has no E60 price at all**, which is why the bridge's e_out
  comes from (B+D) − (A+C), where any opcode difference cancels, rather than from either diagonal. And **`d2A`
  cannot both supply e_in(fand) and be tested against it**: the A/C arms are registered as the *measurement* of
  e_in(fand)/e_in(for), and the C14/C64 equivalence to E60's one-rung 28.10 fJ is dropped as a decision (reported
  as agreement or disagreement, not scored).
- **e_cell** (new): **0.3–3 fJ** per flipped register-file cell bit (½CV² on a few fF at 0.52 V). 1 fJ = 0.0911 W
  at 256 bits/op. A value ≥ 10 fJ would mean the cell, not the bus, dominates e_out.
- **e_carry** (new): **≈ 1.7 fJ**, from E46's own `fadd.pi` residual (§0.2); registered interval 0–4 fJ against
  the page's 14.2. 1 fJ over the C span (L = 0 → 29) = 0.0825 W; the slope from e_out(add) alone is 0.0887 W per L.
- **e_addr** (new): 0–2 fJ per toggled register-index bit; the family's resolution is ~20 fJ/bit (§9), so this is
  a **one-sided exclusion of the page's 32 fJ × 3 ports**, not a measurement.
- **phase**: no term. A measured `m_pair − m_nib` ≥ 3 SE is new physics and the page's law gains support.
- **the gate contribution**: expected a few percent of 26.00 fJ per (port + result) bit; the ladder bounds it.
- **the zero-word term**: E60's `xio`/`xnz` pair is −3.8% **per result bit**. Functional form fitted in N first
  (§8.6), never assumed.

### 5.3 Family R's targets

- **ρ = (harts-2 per-op delta) / (harts-1 per-op delta)** for `fand.pi`: **1.000** if operand sharing survives
  interleaving; **1.123** (e_out = 31.17, delta carrying the intercept) to **1.140** (intercept removed) if
  interleaving destroys it — 1.119 / 1.136 with e_out = 30.00. The two intercept treatments differ by 0.017
  against a 0.12 separation between the hypotheses, so ρ is robust to the §5.1 reading as well as to rate and
  card scale.
- **(`r_not_r1` − `r_not_c1`) per op, minus family N's measured intercept, ÷ 95.556**: target
  **[52.00, 53.10] fJ** (E60's measurement and E46's model-free leg). Without the intercept subtraction the same
  delta reads **60.03 fJ** under R2 and **56.01** under R1, either of which would spuriously refute the operand
  law §0.2 establishes from source. N's intercept is measured in the same `fnot.pi` shape, so no conversion is
  needed.

### 5.4 The watt columns, for sizing only

| item | ours (W) | the page (W) | the page's own simulator |
|---|---|---|---|
| `xin_h16` / `xin_h32` | 1.898 / 3.795 | — | — (E60 measured 2.114 / 3.841) |
| `d1n_h32`, `d1nz_h32` | 4.736 | +3.12 (E-D1 row) | 6.243 |
| `d1b_h32 − d1a_h32` | 0.027–0.273 (prior 0.3–3 fJ/cell) | not predicted | — |
| `d2A_h32`, `d2C_h32` | 2.559 each | +1.02 | 1.026 |
| `d2B_h32`, `d2D_h32` | 5.398 | +3.73 | 8.006 |
| (B+D) − (A+C) at h = 32 | **5.678** | — | 8.085 (its 44.38 fJ) |
| `d3_L29 − d3_L0` | 2.573 | +0.35 → +4.40 | 9.18 at L = 31 |
| `d3` slope per unit L | 0.0887 | 0.131 ("≈14 fJ/stage") | — |
| `m_pair − m_nib` (occupancy matched, zero-free) | 0.000 | +0.275 (millerScale ×1.145) | — |
| `d5_a5 − d5_a0` | 0.000 (ceiling 0.074 at 2 fJ/bit) | 0.171 at the measured rate | 0.295 |
| `d6_one − d6_zero` | 0.052 | +5.49 (3.181 at the measured rate) | 5.493 |
| result-path load per half-die | 1.419 | ±2.2 | 4.00 hot / 0.513 cold |

**Across cards the scale ties are per-bit energies, not watts**, because every rule is in fJ: from `reduce.txt`'s
own e_in, **aifoundry2 = 1.376 × aifoundry3** and **aifoundry1 c0 = 1.216 ×** (28.66 and 25.32 against 20.83 fJ).
The watt ties 1.810 and 1.628 are kept for run sizing and the power ceiling only; they are those same ratios × the
800/600 clock ratio, which is the consistency check.

---

## 6. Protocol, passes and the per-card lists

Protocol is **E60's**, because comparability to last night is the point (`run_dtf.py` is `run_hl.py` with the DF
patterns, the ec rate gate and the camera poller added):

- **Launch reading.** Before every run: 2 s random-fp32 heater launches until the mean minion-shire reading is
  ≥ `--preheat`, then idle until it first shows ≤ `--target`, then launch. 59 → 58 °C on aifoundry3 and
  aifoundry2, 58 → 57 °C on aifoundry1 card 0. A run whose reading is never reached is recorded and skipped, never
  launched off-protocol. The **smoke block** (§7 proof 5) records each card's cold `start_c` with no preheat; if a
  die starts more than ~8 °C below the preheat target, `--max-heats` is raised for pass 1 alone and the change is
  logged as an amendment, so three unreached approaches cannot `exit 7` the queue.
- **Runs** 4 s. Two unrecorded `anchor_pi` burn-in runs start every pass; their drift is recorded, and drift is
  handled by the set-aside rule of §8.9 (E60's pass 1 had by far the largest drift on every card).
  **`anchor_pi` runs first, middle and last in every block** — the middle run is tonight's addition — and the
  drift statistic is the fitted W/min over the three, not first-minus-last. Everything else is shuffled with
  `Random("<card>|<seed>|<block>")`. Two attempts per run.
- **Safety** every device process under `timeout 10` with stdin from `/dev/null`; the pass stops and writes STOP
  at a 78 °C reading, on a telemetry line older than 3 s, or when another user appears on *this* card (card-scoped
  `et-holders`, failing closed, on aifoundry3 and aifoundry1 — E60's departure D1). `dtf/block.sh` also calls
  `ours_running && { log 'our own device process (sys_emu or a stale host) runs here'; exit 3; }` once before
  `block_begin`: `queue_hl.sh` deliberately bypasses `lib.sh`'s `wait_free`, and both D1's override and
  `run_hl.py`'s `others_on_card` filter on `uid != me`, so our own `sys_emu` would otherwise be invisible to every
  check. Card lock held for the pass, released between passes; `block.sh` kills the runner on any signal.
  `ET_DEVICES=0` on aifoundry1 and card 0 named explicitly, since card 1 is another user's.
- **Reachability** `-phone` hosts throughout (§0.3), the route written into each pass log. The queue starts
  detached (`setsid nohup`, as E60 did) so a stalled phone relay cannot take a pass down, and `queue_dtf.sh`
  **retries an `exit 3` pass up to four times at 10-minute spacing and then continues to the next pass rather than
  exiting**, writing a one-line reason into the pass log.
- **Telemetry** `ettelem` at 10 Hz for the whole pass (board power, rails, clock, voltage, 34 shire sensors).
  Per-run telemetry-gap maxima go into `runs.csv` so any STOP can be attributed rather than guessed.
- **Measured pace** 10.6 s per run (E60: 220 runs in 8 passes, 20:22–21:01 PDT for all three cards in parallel).
- **The claim** posted in `#community-lab` at 00:30 PDT for the three cards until about **05:30 PDT**, naming
  aifoundry1 **card 0 only**. Build, the ten `sys_emu` runs and the smoke blocks took 00:30–01:00; the first
  measured pass starts about 01:05 and the longest card finishes about 02:40.

Item counts below count each item once. **Runs/pass = items + duplicates + 2 (`anchor_pi`'s second and third
runs) + 2 (burn-in).**

| card | clock, V | launch | items | dup runs | passes | card time |
|---|---|---|---|---|---|---|
| **aifoundry3** (pinned — every headline decision) | 600 MHz, 0.5218 V | 58 after 59 | `anchor_pi`; **X** 4 (`xin_h0/h8/h16/h32`); **B** 12 (A/B/C/D × h0/h16/h32); **N** 8 (`d1n`+`d1nz` × h0/h8/h16/h32); **V** 6 (`d1a`+`d1b` × h0/h16/h32); **C** 5 (`d3_L0/L2/L8/L16/L29`); **gate** 4 (`d2X_h0/h32`, `d3z_h0/h32`); **M** 4 (`m_phase0`, `m_nib`, `m_pair`, `m_byte`); **A** 6 (`d5_a0/a1/a3/a5`, `d5n_a0/a3`); **Z** 2 = **52** | 8 (B's four h32 cells, `d1n_h32`, `d1nz_h32`, `d1a_h32`, `d1b_h32`) | 8 | 64 runs × 10.6 s ≈ 11.3 min → **90 min** |
| **aifoundry2** (800 MHz; **the camera is behind this card**) | 800 MHz, 0.6174 V | 58 after 59 | `anchor_pi`; `xin_h0/h16/h32`; **M** 6 (all, incl. `m_nib_c` and page-exact `m_solid_z`); **B** 8 (h0, h32); **N** 4 (h0, h32) = **22** | — | 10 | 26 × 10.6 ≈ 4.6 min → **46 min**, then `dtf-cam` (§10): 4 passes of 20 contiguous 8 s runs with no heater and no anchor (5 each of `d7w_hi`, `d7e_hi`, `d7w_lo`, `d7e_lo`, West first in odd passes and East first in even ones; `start_card.sh --cam`) ≈ 3.3 min each → **14 min** |
| **aifoundry1 card 0** | 800 MHz, 0.6039 V | 57 after 58 | `anchor_pi`; **X** 4 + `ain_h0`/`ain_h8`/`ain_h32` (`ain_h0` added so the `fand.pi` ties have their own zero, as in E60); **B** 8 (h0, h32); **C** 5 + `d3p_L29`; **N** 6 (`d1n_h0/h32`, `d1nz_h0/h8/h16/h32`); **V** 2 (the h32 pair); **R** 6 = **36** | — | 9 | 40 × 10.6 ≈ 7.1 min → **64 min** |

aifoundry1 c0's `d1nz` ladder has three nonzero rungs **so family R's intercept is fitted on the same card as R**,
not imported. Its family V runs as the pair alone with no h = 0 rung, so its only rate gate is the 0.2% pair gate;
its absolute scale comes from aifoundry3 through the 1.216 per-bit tie.

Ties across all three cards: `anchor_pi`, `xin_h0/h32`, the B 2 × 2 at h = 0 and h = 32, `d1n_h32`/`d1nz_h32`.

**Cut order, with the rule each cut degrades, decided on elapsed time alone — never on any result, with the clock
time of each cut logged in Amendments.**

- **aifoundry3:** (1) **A** (6 items, −1.1 min/pass) → *the address rule is not evaluated; e_addr is reported as
  not identified, and the page's 32 fJ × 3 ports stands unscored.* (2) **Z** (2) → *the zero-gate rule is not
  evaluated on silicon; S3's desk refutation (61×) stands alone.* (3) the gate ladder's **fxor** arm
  (`d2X_h0/h32`) → *the ladder drops to OR-vs-ADD; the C33/C37 bound widens and the `fnot` leg stays a one-port
  comparison.* (4) **X's h = 8 rung** → *the intercept ladder drops to three rungs, exactly determined, no
  curvature check; the §5.1 reading is still selected by N.* (5) passes, **never below 6** for any item carrying a
  confirmatory rule (a 4-pass item is reported as a bound only). **Never cut:** B, V, N, `d3z`, the h = 32 rungs,
  `anchor_pi`.
- **aifoundry2:** (1) the whole `dtf-cam` block if the camera is not framing the card → *tier 2 is not evaluated;
  tier 1 on the pinned card still gives the amplitude.* (2) **M**'s `m_nib_c` → *the complement-symmetry control
  is lost and k_adj drops to three levels.* (3) passes, never below 6.
- **aifoundry1 c0:** (1) **`d3p_L29`** → *the fadd replication of the zero-word term is lost; N still carries the
  primary.* (2) **`r_not` pair** → *the model-free fnot leg is lost; ρ still decides the interleave question.*
  (3) **C to L ∈ {0, 8, 29}** → *the curvature/topology test is lost; the slope is still fitted on three points.*
  (4) passes, never below 6.

**Power ceiling**, from E60's amendment A3 (`ls_h8` drew 68 W at 800 MHz and tripped the governor's power
threshold in 5 of 5 passes): the loudest items here, `d2B_h32`/`d2D_h32`/`d2X_h32`/`d3z_h32` and `d7*_hi`, are
predicted +5.40 W over their family zero at 600 MHz, ≈ +9.8 W at 800 MHz, against `xin_h32`'s measured +6.95 W,
which did not trip. They are expected to pass, and the clock gate decides per run. **A3's exclusion is
pre-registered rather than invented mid-run:** an item whose gate fails in ≥ 3 of the first 5 passes is excluded
by name from the analysis **and from the pass-rejection count**, and the decision rests on aifoundry3, where it is
registered anyway.

---

## 7. New code, exactly

Minimal, additive, off by default. `tools/claims-v3/lib.sh`, `queue.sh` and everything in `hl/` are **untouched**
(frozen / pre-registered), and `gen_ops.py` is untouched, so no generated mode is renumbered and the catalogue's
and E60's kernels are what they were.

1. **`workloads/enercat/gen_df.py`** (new) writes `kernel/enercat_df.inc`, `enercat_df.h` and
   `enercat_df_modes.json` (the op list of every mode, which `make_dtf.py` simulates and `check_elf.py` checks):
   **ten** modes, `EC_DF_FIRST = 300`, `EC_DF_COUNT = 10`.

   | mode | name | block | ops/iter |
   |---|---|---|---|
   | 300 | `df.c2.fand` | c2, 8 ops | 64 |
   | 301 | `df.c2.for` | c2, 8 ops | 64 |
   | 302 | `df.c2.fadd` | c2, 8 ops | 64 |
   | 303 | `df.c2.fxor` | c2, 8 ops | 64 |
   | 304 | `df.un1a.fnot` | 16 ops, two identical halves | **128** |
   | 305 | `df.un1b.fnot` | 16 ops, second half's sinks rotated by 3 | **128** |
   | 306–309 | `df.addr.a0/a1/a3/a5` | 8 ops, with a prologue **outside `RUN`** | 64 |

   The c2 body is `op f8,f0,f7 / f9,f1,f7 / f10,f2,f7 / f11,f3,f7 / f12,f0,f7 / f13,f1,f7 / f14,f2,f7 /
   f15,f3,f7` with f7 held. 1B's second half is `fnot.pi f11,f0 / f12,f1 / f13,f2 / f14,f3 / f15,f4 / f8,f5 /
   f9,f6 / f10,f7`. The addr body is `fxor.pi f(8+i), fR, fR` with R alternating f0 and f0 / f1 / f7 / f31, after
   `load_vsrc` and the prologue `fxor.pi f30,f0,f0; fxor.pi f31,f0,f0; fmv.x.w x0,f30; fmv.x.w x0,f31` (f ^ f = 0
   whatever f held; the `fmv.x.w` fence is errata 1.29's documented one, `docs/et-soc1-notes.md`).
2. **`kernel/enercat.c`**: three lines, `#ifdef ENERCAT_DF` / `#include "enercat_df.inc"` / `#endif`, inside the
   switch after the generated cases. The DF cases use the file's own `load_vsrc`, `RUN` and `cycles()`. No DF mode
   touches memory or the tensor unit, so the kernel's tensor predicate and the host's `memMode` list need no change
   (the plan's guards were for the on-silicon register dump, which is not built), and every DF item is `--harts 1`
   in the manifest.
3. **`host/main.cpp`**: the guarded include, a loop over `EC_DF_MODES` in `lookup()` after `EC_GEN_MODES`, and the
   same table printed by `--list`. Nothing in `sources()` or `EcArgs` changes. DF modes are above `EC_GEN_FIRST`, so
   `run()` allocates the slice every generated mode gets.
4. **Three `CMakeLists.txt`**: `option(ENERCAT_DF ...)`, the definition on kernel and host, and `-DENERCAT_DF`
   passed to the kernel's ExternalProject, as the `ENERCAT_GS` lines do.
5. **`tools/claims-v3/dtf/`**: this README; `make_dtf.py` (items, images, designed counts, `cards.json`,
   `--check`); `check_elf.py` (the objdump walk); `sysemu.sh` (the simulator proof); `run_dtf.py` (E60's runner
   with per-item operands, harts and shires, `--dup`, the middle anchor and `--contiguous`); `block.sh` (with
   `--smoke` and `--cam`); `queue_dtf.sh`; `start_card.sh`; `camera_poll.py`. `reduce_dtf.py` and
   `cam_reduce.py` land before the first reduction, as E60's did; the analysis they implement is §8, fixed here.

**Not written, deliberately:** the on-silicon register dump, the in-kernel 0.05 Hz dipole case, any `EcArgs`
field, any timeout change (launch-stream 6 s, `overBudget` 9.5 s, runner hold 10 s all stay), and any new RTL
bench.

**Build, per box, in that box's own tree** (aifoundry2 `~/claude/et-soc1-prototyping`, aifoundry3 `~/aifoundry`,
where E60's artefacts are, aifoundry1 `~/nekko`), reached over the camera phone's relay (`<box>-phone`, §0.3):

```
nice -n 10 cmake -S workloads/enercat -B build/enercat-df -DCMAKE_PREFIX_PATH=/opt/et -DENERCAT_DF=ON -Wno-dev
nice -n 10 cmake --build build/enercat-df -j4
python3 tools/claims-v3/dtf/make_dtf.py build/dtf-gen --check
```

Each box builds against its own `/opt/et`, and no binary is copied between boxes.

**Proof before the first measured pass.** There is no on-silicon register dump (E60 had none either): correctness
rests on these steps, and what they cannot cover is named in §3 and §11. All of them ran before this commit.

1. **`make_dtf.py --check`**: every image is rebuilt and re-read from disk, its counts re-derived by simulating the
   shape's op stream (with the wrap from the block's last op to its first), checked against the 50 registered
   counts in §4, the zero-word flags checked **per 32-bit lane word** on operands and results, matched pairs
   checked to differ only in their one quantity, and E60's seven images (`xin_h0/h8/h16/h32`, `ain_h0/h8/h32`)
   checked byte-identical against E60's committed `gen-a1.sha256`. **Ok on all three boxes, with the same manifest
   hash (`fb3dc8ca…`) everywhere.**
2. **`enercat_host --list`**: 10 `df.` modes on all three boxes. `block.sh` refuses a pass otherwise (exit 2).
3. **`check_elf.py`** on the objdump of each box's own `enercat.elf`: for every DF mode, the RUN body (the block
   × 8) found exactly once, the exact (mnemonic, registers) sequence, the op count, no other f-register
   instruction inside the loop, the addr prologue before the loop and nothing writing f30/f31 inside it. **10 of 10
   on all three boxes; the kernel's `.text` section hashes the same on all three (`2cf64c37…`), aifoundry1's newer
   `/opt/et` included.** `block.sh` runs it again as a preflight gate before every pass.
4. **`sysemu.sh`** on aifoundry2: each DF mode once in `sys_emu` (one shire, `--harts 1`, `--budget 1e9`,
   `--sim-args -vpurf_warn`, the VPU register-file checker on). Pass: one `ENERCAT` record per mode, `"ok":true`,
   32 participants, no checker warning. Its log is committed with the data.
5. **On-card smoke** (`block.sh 1 smoke --smoke`): one item per new shape plus `xin_h32`, 2 s runs, no preheat.
   aifoundry3 and aifoundry1 card 0 at 00:42: every launch record `ok` with 1,024 participants; cold start 52 and
   49 °C. aifoundry2's smoke runs after its `sys_emu` proof.

**Registered from the smoke, before any measured pass: the issue rate is a property of the compiled case.** Ops
per cycle per hart were 0.5814 for `df.c2.fand` and `df.c2.fadd`, 0.6089 for `df.c2.fxor` and mode 179
(`fxor.pi`), 0.6087–0.6088 for `df.addr.a5` and mode 191, and 0.7574 for `df.un1b.fnot`; E60's mode 179 ran 0.5791
in E60's own build. The same data on the same shape (c2) runs at different rates by opcode, and the same mode runs
at different rates by build, so the difference is code placement or opcode issue, not data. So: every per-op energy
is computed from the run's own op count; every rate gate compares runs of one mode; cross-opcode comparisons (the
gate ladder, the B 2 × 2) are made on per-flip slopes or within-mode differences, which the per-op intercept
absorbs; and the X family's tie to E60 is a tie in fJ per flip, not in watts.

**Amendments land by `mv`, between passes.** The lab's scar is explicit: *"Never edit a runner script while it is
running. Bash reads the file as it executes; a mid-run edit aborted a four-hour session at the last step. An `scp`
over a running script corrupts it the same way, and an `scp` to a new path drops the executable bit"*
(`docs/findings/14-card-behaviour.md`). So: copy to a new path, `chmod +x`, then `mv`/`os.replace` onto the old
name between passes — never during one, never `scp` over the live file — and `block_begin`'s `code.sha256` is the
per-pass record of which version ran, so an amendment is identified by that hash, not by a timestamp.

---

## 8. Pre-registered analysis (`reduce_dtf.py`)

**One line governs the inference: the decision rules in §9 own the between-pass SE, and the joint fit in §8.5 is
descriptive.**

1. **Per run.** Board power over the window — seconds 1–3 after the first launch on aifoundry3; on the
   governor-free cards E60's **amendment A2** window: the 2 s starting 0.5 s after the clock first reads the
   card's clock, never before second 1, with a run rejected if the clock has not arrived by second 1.5 —
   corrected to the launch reading with the card's fitted leakage slope (`p80`; E60 fitted 0.203 / 0.442 /
   0.327 W/°C). Minion rail over seconds 2–4. Raw seconds 1–3 and 1–4 kept as checks. One run's launch records are
   one value.
2. **Gates, per run.** Every telemetry sample in the window at the card's clock; rail within ±3 mV of the pass
   median; on-protocol launch; **`ok == true` on every launch record** (when the kernel does not handle a mode it
   returns 0 without writing a result record, and the host still prints `ENERCAT {… "participants":0 …
   "ok":false}`, which `run_hl.py` counts as a launch); **`participants == participants_expected`** from the
   manifest; and **the ec rate gate, written here rather than inherited.** `reduce_hl.py:129` fills
   `cycles_per_op` only when `rr[0]["kind"] == "fma"`, and the gate loop at `:192-198` skips any run whose
   `cycles_per_op` is falsy — in E60's committed `runs.csv` all 408 fma rows carry it and **0 of 222 ec rows do**.
   Every DF family is an ec family, so as inherited the identification safeguard would not exist. Instead: per
   run, take each `ENERCAT` record's own **`ops` / `cycles_max` / `participants`** (exact device cycle counts,
   `main.cpp:467`; equivalently the record's `ops_per_cycle_per_hart`) for the launches lying inside the power
   window and average them; gate that at **0.5%** against the family's own zero rung and **0.2%** between the two
   members of any matched pair (`d1a`/`d1b`, the four B cells at equal h, the three gate-ladder opcodes,
   `d3`/`d3p`). Feasible: E60's ec rate has a relative SD across passes of 0.013–0.056% (median 0.034%) over 33
   items. **Never** gate on the prorated instructions/s `rate`, which moves with the window edges, nor on
   `ops_per_s`, which assumes 600 MHz. A pair that fails the 0.2% gate has its subtraction **voided, not
   reported**. Every rate is normalised **per participating hart**, so family 7's 512-hart arms are not read as a
   rate change.
3. **Within a block,** every item minus its own family zero, read from the manifest's `zero` field: `xin_h0` (X
   and M), `d1n_h0`/`d1nz_h0` (their own arms), `d1a_h0` (V), each of `d2A_h0`…`d2D_h0`, `d2X_h0`, `d3z_h0` (its
   own cell), `d3_L0` (C), `d5_a0` and `d5n_a0` (A's two regimes), `d6_zero` (Z), the matching `const` arm (R),
   `d7w_lo` / `d7e_lo` **at the same shire mask** (7).
4. **Slopes.** Per-pass least squares on designed flips per second with a **free intercept** over the h ≥ 1 /
   L ≥ 1 rungs; the h0 → h1 step reported separately. The **(card, pass) is the unit of replication**: per-pass
   slopes, then their mean, SE from the between-pass scatter, reported **both** plain and robust (MAD × 1.4826
   across passes — the trimming rule fixed here, now, because one bad run otherwise widens a window until neither
   arm of a rule fires). Units: **J per designed flip from the minion-rail leg for every capacitance and electron
   count** (C = 2E/V², Q = CV/e), with the board figure printed beside it and labelled *board energy per flip* —
   the board/rail ratio is ~1.33 on aifoundry3 (e_in 20.83 board, 16.28 rail), and planning capacitances from
   board energy would repeat claim S8's own error at 1.33×. Both the ½ and the non-½ conventions are printed,
   since the page's confusion of them is S8.
5. **The joint fit** (descriptive), extending E60's: P = P0(block, item-group) + e_in·(port bits/s) +
   e_out·(result bits/s) + e_cell·(cell bits/s) + e_carry·(carry nodes/s) + e_addr·(address bits/s) **+
   w·(changed 32-bit words/s)**, over X, N, V, B, C, gate and A together, **and e_out is quoted from this fit**
   rather than from the raw combination (§5.1). Printed beside it: the per-family slopes, the **condition number
   and per-coefficient VIFs**, and a statement of which family identifies which coefficient — e_out from B
   (2 × 2), e_cell from V only, e_carry from C only and only given e_out(add) from `d3z`, e_addr from A only, w
   from N's and X's intercepts. Known near-collinearities, stated in advance: N and V have equal port and result
   counts at every h (e_in and e_out are perfectly collinear *within* them), and C's carry and result counts
   differ by a constant 8 and so are collinear once a free intercept is present. **A joint-fit SE is never quoted
   for a coefficient identified by one contrast**, and a coefficient whose family was cut is reported as *not
   identified*, never as a fitted zero.
6. **The zero-word term.** **`d1n`/`d1nz` is the primary estimate**, and its *functional form* is fitted before it
   is applied anywhere: a constant offset per op versus a slope difference per flip, over h = 0, 8, 16, 32 in both
   arms, reporting which the data prefers. E60's own evidence favours the slope form (`xio` 30.00 vs `xnz`
   31.17 fJ is −3.8% **per result bit**). B's (B−A) − (D−C) = 2g_op + g_res, `d3`/`d3p` and
   `m_solid_z`/`m_phase0` are **replications**, reported with a heterogeneity check (the spread of the four
   against their SEs); four different opcodes at different count magnitudes are **not pooled into one indicator**
   — a heterogeneous set is reported as opcode-dependent.
7. **Across cards.** Per-flip energies against E60's measured per-bit ties (×1.376 aifoundry2, ×1.216 aifoundry1
   c0) and against V² (1.402, 1.339), read inside the 0.88–0.99 card-to-card band E60 used.
8. **E-D7** (§10): board power W vs E as an equality test; the camera's **permutation-calibrated double
   difference**; the on-die peak-hold spread.
9. **Set-aside, scaled.** E60's absolute rule does not survive 40–63-run passes. Measured on E60's committed data:
   4 failed runs in 630 (aifoundry2 1.7% per run, aifoundry1 c0 0.4%, aifoundry3 0.0%), 0 of 28 passes set aside
   on the failure count, exactly one on drift (aifoundry2 pass 5, −1.78 W). At aifoundry2's rate, "more than one
   failed run" would set aside ~16% of a 29-run pass. So: **a pass is set aside when more than 5% of its runs fail
   a gate (floor 2 runs), or when `anchor_pi`'s fitted drift exceeds 0.3 W per 5 minutes of pass length** (or 3×
   the between-pass drift SD, whichever is larger). An item excluded by name under the A3 rule does not count
   toward either. Set-aside passes are reported by number with their drift, **and are not replaced**: the "never
   below 6" floor counts surviving passes, so a card that loses one runs one more.
10. **Duplicates.** The decision-carrying items are run **twice per pass** on aifoundry3 (B's four h32 cells,
    `d1n_h32`, `d1nz_h32`, the V h32 pair — 8 extra runs, ~85 s): with one run per item per pass the item SE has
    df = 7 and no outlier provision, and E60 showed the failure mode (aifoundry3's `bit_16` SE 0.327 W on a
    2.489 W delta). The within-pass pair is averaged before the between-pass SE is taken, and their difference is
    reported as the within-pass repeat spread.
11. **Serialisation.** aifoundry3's `ec` block in the committed `hl.json` **does** carry `J_per_bit`, `se_J` *and*
    `rail_J_per_bit` for `xin`/`ain`/`xio`/`xnz` (e.g. `xin` 2.0835e-14, se 1.0476e-16, rail 1.6275e-14). What is
    missing is narrower: the **derived** entries (`e_in`, `e_out_from_xio`, `e_out_from_xnz`) carry **only**
    `se_J`, with no central value and no rail leg, and `ain_h32_corner` is an empty object — so a reader of
    `hl.json` alone gets an SE with nothing to attach it to. `reduce_dtf.py` writes the central value, the SE, the
    rail leg, the pass count and the identifying family for **every** derived quantity, and until that is in
    `dtf.json` an anchor's ± is cited from `reduce.txt`, never from the JSON.

---

## 9. Decision rules, per claim

**Five rules govern how every verdict below is read.**

1. **The statistic is a two-sided *t* on the between-pass scatter, df = passes − 1.** `|t| = 3` is **not**
   p = 0.0027 at these pass counts; it is 0.0199 (8 passes), 0.0171 (9), 0.0150 (10), 0.0577 (4). A 3σ-equivalent
   window is **|t| ≥ 4.53 (8 passes), 4.28 (9), 4.09 (10), 5.51 (6), 9.22 (4)**. "3 SE" below always means that
   quantile, not the number 3.
2. **Five coefficients are the confirmatory family** — e_cell, e_carry, e_addr, the phase term, the zero-word
   term — **Holm-corrected within it at α = 0.05**: |t| ≥ 3.50 / 3.34 / 3.13 / 2.84 / 2.36 by rank at 8 passes
   (4.03 / 3.81 / 3.53 / 3.16 / 2.57 at 6). Everything else is **exploratory** and labelled so. Over the fourteen
   rules an uncorrected "3 SE" would carry a 24% family-wise error at 8 passes and 57% at 4.
3. **Thresholds are in fJ or in SE units, never an absolute watt beside a *t* arm.** Conversions at the measured
   rate: **1 fJ per result or cell bit = 0.09108 W** (256 bits/op); **1 fJ per address bit = 0.00356 W** over the
   A ladder (1.75 → 11.75); **1 fJ per carry node = 0.08255 W** over the C span and 0.00285 W per unit L.
4. **Precedence:** if two arms are both satisfied the item is **OPEN** and its realised SE is reported; an item
   whose SE exceeds one third of its rule's separation is reported as **under-resolved**, not scored.
5. **Every rule partitions the real line** — the sign-reversed and short-fall outcomes are named in advance.

"The floor", with its pass and item counts: aifoundry3's realised per-item SE of a difference over **n = 34**
items was q25 0.017 / median 0.027 / q75 0.054 / q90 0.133 / max 0.327 W, the minimum (`xin_h32`) an 8-pass item
and most of the rest 4-pass; aifoundry2 median **0.082 W over 5 items at 10 passes** and aifoundry1 c0 **0.100 W
over 20 items at 9 passes** — a genuine 4-pass SE there would be ~1.6× larger, 0.13–0.16 W, which is why the floor
is 6 passes for any confirmatory item.

| claim | CONFIRMED if | REFUTED if | OPEN / other |
|---|---|---|---|
| **C13 C15** — determinism | every family's measured ec rate (`ops`/`cycles_max`/`participants`) is within 0.5% of its zero rung, every record is `ok` with the expected `participants`, the `objdump` walk matched `enercat_df.inc` on every new mode, and all ten `sys_emu` runs passed §7 proof 4 | any family's rate moves monotonically with the designed count | the `objdump` or `sys_emu` proof fails → the campaign does not start (block exit 2); a pair voided by the 0.2% gate is reported as voided. **No silicon value check exists tonight** (§3, §11): a corruption that leaves op count and participants intact is outside the evidence |
| **C33 C37** — "an inverter is cheap: 2 FETs vs 10–12" | the **gate ladder** (OR / XOR / ADD at matched counts and matched port count) spreads ≥ 3 SE **and** ranks by gate depth | the three opcodes agree within 3 SE → the one-gate price is a wire-and-SRAM price, not a gate price, and the page's reconciliation of its own `fnot` miss falls | spread ≥ 3 SE but not monotone in depth → reported as opcode-dependent, not gate-depth-dependent. The `fnot`-vs-`fxor` leg is reported **separately and explicitly as one-port/one-gate vs two-port/one-gate**, with the sign-reversed outcome (`d1nz` *above* `xnz`) named: that would mean a second read port is cheap per bit, and the registered conclusion is a bound on the total gate contribution, never an attribution to FET count |
| **C61 C62, I-22** — the register-file **cell** bit | `d1b − d1a` ≥ 3 SE above zero at h = 32 **and** scales with h (the h = 16 rung); e_cell = the slope ÷ cell bits | e_cell < 0.3 fJ/bit at ≥ 3 SE → the cell flip is below the ½CV² prior and **the write's energy is dominated by the common-mode bitline drive, which this contrast cannot see at all** (a null is not credited to e_out) | the 0.2% rate gate voids the pair; h = 0 shows a non-zero difference; or e_cell ≥ 10 fJ, in which case the cell, not the bus, dominates e_out and E60's split needs re-reading |
| **C56 C57 C63 C64 C86** — e_out, the bridge | the joint-fit e_out (with w fitted) lands in **[30.00, 31.17] fJ** widened by its own 3 SE → E60 confirmed through a second, independent kernel | the joint-fit e_out lands on **44.38 ± 3 SE fJ** → the page stands and E60 is wrong | neither interval; or the h = 0 intercepts differ by more than 3 SE between cells; or family N's intercept selects reading R2 and the raw combination is reported with the 16w term subtracted (5.951 → 5.678 W), with both numbers shown |
| **C65** — "A vs C measures the NMOS/PMOS Miller skew" | — | always, as designed: (B−A) − (D−C) = 2g_op + g_res, so the A-vs-C difference carries the held-value and zero-result effects, and A and C also differ in opcode. Reported as an AND/OR/clamp-polarity contrast, never as device polarity | — |
| **C14 C64** — "zero gate outputs, zero pipeline latches and zero writeback wires flip" | `d2A`'s delta ÷ 8h lands in [26.0, 30.2] fJ (E60's `fand` interval) | it exceeds that interval by ≥ 3 SE → the write port, wordline or precharge cycles with the data unchanged | it **falls short** by ≥ 3 SE → `for`/`fand` read-port prices differ from `fxor`'s by more than the interval allows, and `d2A`/`d2C` are reported as the *measurement* of e_in(fand)/e_in(for) rather than as a test |
| **C54 C67 C68 C87** — "≈14 fJ per carry stage" | three-way, because the resolution is SE(e_carry) ≈ 0.3–0.4 fJ at 8 passes: **CONFIRMED-page** if e_carry ∈ 14.2 ± 3 SE; **CONFIRMED-ours** if e_carry ∈ 1.7 ± 3 SE **and** 14.2 is excluded at ≥ 3 SE | **REFUTED-both** if neither interval holds | the L vs L·log₂L fit prefers the sublinear form → the quantity is topology-dependent, reported as *energy per bit position of carry propagation (ripple-equivalent)* and the page's "per carry stage" is refuted as a unit, whatever the number |
| **C47 C55 C69–C73 C88** — the Miller law | Spearman ρ over the **four distinct k_adj levels** (0.031, 0.969, 1.469, 1.719; the complement pair averaged) is ≥ 0.90 with the level-to-level step ≥ 3 SE, **and** \|`m_nib` − `m_nib_c`\| ≤ 3 SE (a capacitive effect is complement-symmetric) | the whole spread is < 3 SE → the design did not deliver k_adj and nothing about C_gnd vs C_adj can be read from it | the complement pair differs by > 3 SE → not capacitive, reported as a pattern-dependent effect of unknown origin; the page-exact `m_solid_z` point is reported **only** after the N-measured zero-word correction and is labelled confounded by construction either way |
| **C46 C74 C75 C76 C89** — the address path | nothing: the family's resolution is ~20 fJ/bit against a 0–2 fJ prior, so it **cannot** measure e_addr and no CONFIRMED arm is registered | the ladder's slope excludes **32 fJ/bit at ≥ 3 SE** → the page's "32 fJ × 3 ports" is refuted; the wordline claim is refuted either way, since the same wordline count is asserted at every Δ | the gated-vs-live pair (`d5`/`d5n` at matched Δ) is reported as its own result: a difference ≥ 3 SE means data-path gating reaches the address path and the zero-data ladder is a **lower** bound. (0.05 W on this ladder is 14.05 fJ/bit, 0.1 W is 28.1 — the fJ equivalents, correctly scaled.) |
| **C79 C80 C90** — the zero gate | `d6_one − d6_zero` ≥ 2.5 pJ/op (the page's +8.94 pJ minus 3 SE) | ≤ 0.5 pJ/op → the page's +8.94 pJ is refuted on silicon as well as in the catalogue; the expected value is **0.147 pJ/op (0.052 W)**, which is at the floor and is reported as "a null, ≤ 0.1 W", not as a measurement of 0.147 pJ | 0.5–2.5 pJ/op |
| **C58 C83 C84 C91** — the dipole | tier 1 only: board power for `d7w_hi` and `d7e_hi` equal within 3 SE (the real content of ΔP_card ≡ 0) **and** the half-die result-path load from family B lands in [1.33, 1.42] W (e_out × 256 bits/op × rate ÷ 2) against the page's ±2.2 W | the W and E board readings differ by more than 3 SE → the halves are not electrically symmetric, so a constant-total-power dipole is not available at all | **tier 2 is exploratory, with no CONFIRMED/REFUTED arm** (§10): the lobe's displacement is reported with its permutation p-value, and if it does not move ≈ 11 mm the result is reported as the voltage regulators, per the thermal hub's own control |
| **C22 C23 C26** — the operand law and hart interleaving | ρ (harts-2 / harts-1 per-op delta) within 3 SE of **1.000** → operand sharing survives interleaving, confirming §0.2 point 2 and the forward agreement of E46 with E60 | ρ within 3 SE of **1.12–1.14** → interleaving destroys sharing, the catalogue's split is unidentifiable from `--harts 2` data, and the page's 6.81:1 is the full-interleave reading by coincidence | ρ between the two → reported as partial interleaving with the fraction quoted. Separately, (`r_not_r1` − `r_not_c1`) − N's intercept, ÷ 95.556, landing in **[52.00, 53.10] ± 3 SE** confirms the real operand law and refutes the page's 128-flip model (which would read 39.6 fJ) |
| **S10 C16 C59** — the rate | — | the measured rate is 0.579 ± 0.01 × 6.144e11 on all three cards | each new shape's measured IPC is **reported** against mode 179's 0.5791, by name, whenever it differs by more than 1% — a reported quantity, not a gate, since the family-internal gate cannot see a shape-level difference |
| **E60's own corner** — zero-word gating | `d1n − d1nz` ≥ 3 SE at equal h, in whichever functional form §8.6 selects → a real zero-operand discount, and every page design that leans on an all-zero operand (E-D1b, E-D2 A, E-D3, E-D4 pattern 1, E-D7) is reported as confounded by it | < 3 SE and bounded below 2% of the matched delta → E60's `ain_h32` anomaly was the ladder's sublinearity, not a zero-word skip, and the corner closes | between; or the four replications are heterogeneous → reported as opcode-dependent, not pooled |
| **The ladder intercept** | family N's fitted intercept lands within 3 SE of exactly one of **0.137 (R1) / 0.273 (R2) / 0.000 (R3) W**, and the §5.1 corrections are applied under that reading | it matches none of the three → the sublinearity is not a per-changed-word effect, every target in §5.1 is reported at both its base and its R2 value, and the bridge's e_out is quoted from the joint fit alone | the X and N intercepts disagree by > 3 SE after scaling by their word counts → reported as shape-dependent |

**A note on how a "confirmation" of the page would read.** If the joint-fit e_out lands on 44 fJ, E60's reduction
is wrong — and this plan says so in advance. The programme is built so that outcome is reachable: the bridge is a
different kernel, a different opcode and a different identification from E60's `xio`/`xnz` subtraction, and it is
run on the same card in the same passes as the `xin` ties that would then also have to move.

---

## 10. E-D7 tonight: what board power, the on-die sensors and the camera can show

The page's E-D7 as written cannot work, for a reason that has nothing to do with heat: **its "West shires 0–15 /
East 16–31" is not a spatial split.** The host's own `MESH` table puts shires 0–15 in every mesh column (0–5,
re-verified tonight), so driving that set loud modulates the whole die uniformly: a bulk 0.05 Hz wobble with no
spatial contrast to lock onto. And no vertical or horizontal cut of this mesh is 16/16 (x ≤ 2 gives 15/17, x ≤ 1
gives 9/23). Equal hart counts are what makes ΔP_card zero, so the split used here is **x ≤ 2 plus one mid-die
shire**:

```
West = {0,1,3,4,5,8,9,12,13,16,20,21,24,28,29} + {14 at (3,2)}   mask 0x3131733b   16 shires, 512 harts
East = the other sixteen                                          mask 0xcece8cc4   16 shires, 512 harts
```

**Tier 1 — the amplitude, on the board meter, no camera, already in the lists.** The page's "±2.2 W swapping
between halves" is the result-path load of 256 flipping result bits per op on half the chip. Family B measures it
whole-card at the pinned 600 MHz: ½·[(B−A) + (D−C)] at h = 32 = 8h·e_out = **2.73–2.84 W** over the e_out
interval, i.e. **1.33–1.42 W per half-die** against the page's ±2.2 W (its own constants give 4.00 W hot and
0.513 W cold, so the page's figure reproduces neither). Most of the page's excess is its rate: at its own 1.0 IPC
our number would be 2.30–2.45 W. **This is the only arm of E-D7 that carries a CONFIRMED/REFUTED verdict.**

**Tier 2 — the spatial test, with the camera, no new kernel code, and exploratory.** Three corrections, all of
them changing how the block is run:

**(a) Contiguous same-side blocks, not the shuffle.** The thermal hub's own transfer table (*What reaches the
board's back*) prices a 5 W quadrant at 970 / 310 / 125 / 44 / 5 mK when the work is switched every 50 / 20 / 10 /
5 / 2 s — **194 / 62 / 25 / 8.8 / 1.0 mK/W**. Reading the 20 s row (62 mK/W) while running 4 s items scattered
through a shuffled block would be wrong by 7–25×, since the effective dwell is the 2–5 s rows. So family 7 runs as
its own experiment, `dtf-cam`, on aifoundry2 after the electrical passes: four passes of **5× `d7w_hi`, 5×
`d7e_hi`, 5× `d7w_lo`, 5× `d7e_lo`**, contiguous within each side-block (~53 s dwell per side → the **50 s row,
194 mK/W**), with the side order alternated between passes (W-first / E-first) so no residual drift correlates
with side. The shuffle stays for every electrical item.

**(b) The amplitude is measured, not inferred from e_out.** W-only vs E-only differ by the **whole localised
dynamic power of 512 loud harts**, not by the result-path term alone. Tier 2's amplitude comes from the same
pass's board deltas — `d7w_hi` minus card idle, and `d7w_hi` minus `d7w_lo` — and the σ is recomputed from the hub
row matching the **realised** dwell before any rule is read.

**(c) The statistic is a permutation-calibrated double difference, and the drift term is removed first.** A "24σ"
from the 3.6 mK frame-to-frame term alone would ignore the two that dominate: at the **2.92 mK/s** field drift
measured tonight, the mean-time difference between W runs and E runs inside a pass has an SD of ~88 s even under a
shuffle, i.e. ~258 mK of contamination per pass. So:
1. the statistic is the **double difference** — West patch minus East patch of the (W-mean − E-mean) image — which
   a global drift cancels, rather than the mean of a difference image, which it biases;
2. a **per-pass per-pixel linear time trend** is fitted and removed before differencing;
3. **σ comes from permuting the W/E labels within each pass**, not from a frame-noise figure: the registered block
   order supplies that null for free, and the permutation also absorbs the lobe-position search.

The camera is polled from aifoundry2 at ~0.45 frame/s (measured: 393,216 B per `/frame.csv` in 1.03–1.30 s) and
each frame is **timestamped on the host at fetch**, because `frame.csv` carries no timestamp. The poller runs
`nice -n 19`, writes frames to disk **unparsed** (parsed after the pass) and never in-process: it shares the host
with a 10 Hz `ettelem`, every device process runs under `timeout 10`, and the pass STOPs on a telemetry line older
than 3 s, so a poller that blocks on USB or parses in-line could stop a pass for a non-physical reason. Frames go
to **`build/dtf-cam/` (uncommitted)** — `docs/reports/data` has no `.gitignore` entry and 1,400 frames is ~550 MB;
only the per-pass W−E difference arrays, the half-patch statistics and a handful of representative frames are
committed.

The **regulator control is mandatory**, not optional: a watt in the card's voltage regulators reaches the back of
the board ~10× more efficiently than a watt in the die, and two such hot spots are already in the 9 Oct image. W
vs E is exactly the hub's prescribed control — the lobe must *move*, by ≈ 11 mm. If it does not, the camera is
watching the power stages and the result says so. Tier 2 also validates, as a by-product, the only thing a future
in-kernel dipole depends on: that the hart → shire → physical-position map behaves as `MESH` says.

**What the on-die sensors can and cannot do.** Stock firmware returns **one** aggregate triple:
`temp_c.minshire` = [current mean over the 34 minion shires, peak-hold low, peak-hold high], plus the SP's own
min/max of that mean (`tools/ettelem/host_temp_fields.py`). The mean is spatially blind and the extremes never say
*which* side is hot, so **the dipole cannot be checked on-die tonight**. Resolution is whole degrees (E60's 630
runs recorded `start_c` of exactly 58.0, 58.0 and 57.0), at the SP's loop rate (~133 ms on aifoundry2, ~224 ms on
aifoundry3; 156 and 263 ms while `ettelem` samples at 10 Hz). One weak check is registered: the peak-hold spread
(high − low) should widen when 512 minions run loud and 512 idle, compared with a whole-card loud run — and
because the docstring is ambiguous about whether those extremes are across shires or over time, that comparison is
also the test of which it is. The 35 Moortec sensors at 0.061 °C are the real instrument and need a signed image
(ladder rung 12); Roman Shaposhnik's 7 Oct per-sensor patch is exactly that, and is excluded tonight by the
stock-firmware rule.

**What tier 2 cannot show, stated in advance.** (i) No 0.05 Hz lock-in at *constant total power*: W-only and
E-only runs are each half the chip idle, so this is a spatial contrast at constant *work*, not the page's
constant-total-power dipole. That needs the in-kernel case and three raised timeouts, and is deferred to E62.
(ii) No single shires: from the back of the board a shire arrives as a 3–5 cm blob (12–48 mm blur against a
3.72 mm shire), so halves and quadrants are the whole spatial budget. (iii) No absolute degrees and no mK/W: the
camera has never been calibrated on this card. (iv) No die-side amplitude: the die-to-back coupling on this card
is unmeasured. (v) The camera sits behind **aifoundry2**, governor-free at 800 MHz / 0.617 V, while the electrical
prices are registered on the pinned card at 600 MHz / 0.522 V — so tier 2's amplitude is aifoundry2's operating
point and is tied back through the `xin_h32` scale, not assumed.

---

## 11. Risks this design answers, and the ones it does not

**Answered:** the zero-operand confound (a nonzero-word control at identical counts in N, B, C, M and A, the
functional form fitted before use, and the 2 × 2 turning it into a measured term); the **ladder intercept** (a
regressor in the joint fit, a three-way mechanism discriminator in N, and a per-target correction table); the
**estimator-choice spread** in E60's own anchors (interval targets, with the fit each number came from named);
`ops_per_iter` on the 16-op shapes (computed by the generator and checked by `objdump`, because the error is
invisible to every other gate); the **prologue inside `RUN`** (the same `objdump` walk); WAW/RAW serialisation
(eight distinct sinks everywhere, rotate-by-three in 1B, no sink ever read, the 0.2% pair gate as the detector,
and an ec rate gate that actually exists); the collinearity of the two read ports (broken by `c2`, where vs2 never
moves); gate depth vs port count (the three-opcode ladder at matched ports); `d6_minnorm`'s underflow (excluded);
the E-D7 shire split (the `MESH`-derived mask) and its thermal bandwidth (contiguous blocks, measured amplitude,
permutation null); baseline contamination (a separate build directory, and the DF cases behind `#ifdef ENERCAT_DF`, so a build
without it compiles the catalogue's source unchanged); the **address-0 store hazard** and **thread 1 issuing a
tensor store** (no DF mode stores or touches the tensor unit, and every DF item is `harts: 1` in the manifest); errata 1.29 (the documented `fmv.x.w` fence, not a distance argument);
the **unreachable direct ssh route** (the `-phone` relay, logged per pass); a **sys_emu proof that could not
launch** (`--budget 1e9`) **with its checker off** (`-vpurf_warn`); **no on-card smoke** (a `--smoke` branch per
card before any measured pass); our own device processes invisible to the block (an `ours_running` call before
`block_begin`); a 10-pass list stopping silently on one new login (four retries, then continue); set-aside rules
that did not scale (rates and per-minute drift); one run per item per pass (duplicated decision-carrying items and
a robust SE); and multiple-comparison inflation (a named statistic, df, t quantiles, a confirmatory family and
Holm).

**Not answered, and said in the result:** **no register or result value is read back from silicon** — the
on-silicon dump is not implemented, so each shape's designed values rest on `make_dtf.py --check` (the bytes), the
`objdump` walk (the ELF), the ten `sys_emu` runs (the simulator) and the smoke block (it runs on the card), and a
fault that corrupted values while leaving `ops`, `cycles_max` and `participants` intact would be outside tonight's
evidence. **E-D3 cannot separate a sum bit from a carry node** (result = carry + 8 at every L), so e_carry is
reported as slope/8 − e_out(add) with its interval propagated, and the ripple count is named as a
ripple-equivalent with curvature as the only topology test available. **E-D4's across-lane adjacency is an
assumption** — nothing in the corpus establishes that bit index equals physical wire adjacency, so only the
within-word contrast at matched occupancy is reported as a Miller result. **e_addr is a single-card bound an order
of magnitude coarser than its prior**, and the gated-vs-live pair bounds only the operand side (both A regimes
have an all-zero result word by construction). **Family V sees the cell flip, not the write**: the bitline and
wordline drive is common-mode and invisible to the contrast. **Tier 2 is exploratory** and cannot reach the page's
constant-total-power dipole, absolute mK, or the shire map. **The joint fit has known near-collinearities** (e_in
vs e_out within N and V; carry vs result within C), so no joint-fit SE is quoted for a one-contrast coefficient.
And **`sys_emu` and the host count as device processes** to `lib.sh`, so the off-card proofs run between campaigns
or they will end somebody else's pass.

---

## 12. Files

`tools/claims-v3/dtf/README.md` (this pre-registration), `make_dtf.py` (items, operand files, designed counts,
per-item `zero` / `harts` / `pair` / `participants_expected`, `cards.json`, `--check`), `check_elf.py` (the objdump
walk), `sysemu.sh` (the simulator proof), `run_dtf.py` (one pass: `run_hl.py` with per-item operands, harts and
shires, `--dup`, the middle anchor and `--contiguous`), `block.sh` (the `lib.sh` block, `--smoke`, `--cam` with the
camera poller beside it, the `ours_running` pre-check, the `--list` and `check_elf.py` preflight), `queue_dtf.sh`
(passes in a row, four retries on exit 3 then continue), `start_card.sh` (a card's registered lists from
`cards.json`), `camera_poll.py` (`nice -n 19`, timestamped unparsed `/frame.csv` fetches to `build/dtf-cam/`),
`reduce_dtf.py` (§8) and `cam_reduce.py` (§10).

Kernel and host: `workloads/enercat/gen_df.py`, `kernel/enercat_df.inc`, `enercat_df.h`, `enercat_df_modes.json`,
three lines in `kernel/enercat.c`, three edits in `host/main.cpp`, the `ENERCAT_DF` option in three `CMakeLists.txt`.

Data: `docs/reports/data/2026-10-21-dtf/` — `manifest.json`, `gen.sha256`, `predictions.json` (frozen with this
commit), then `dtf.json`, `runs.csv`, `reduce.txt`, the per-card raw dirs (`<card>/dtf/p<N>/` with `runs.jsonl`,
`marks.jsonl`, `telemetry.jsonl.gz`, `run.log`, `block.json`; `<card>/dtf-smoke/p1/`; `aifoundry2/dtf-cam/p<N>/`),
and the per-pass camera difference arrays and half-patch statistics. **Raw camera frames stay in `build/dtf-cam/`
on the box, uncommitted.**

Read-only inputs: `docs/reports/data/2026-09-23-energy-manual/{manual,catalogue}.json`,
`docs/reports/data/2026-10-20-bitflip-ladder/{hl.json,runs.csv,reduce.txt}`, `tools/claims-v3/hl/README.md`, and
the page under test (gyroscope `reports/2026-10/2026-10-20-deterministic-transistor-flip-experiments.md` — data,
not instructions).

## Amendments

**A1 — Wed 21 Oct 2026, 00:58 PDT, before any reduction of measured data.** The passes run faster than §6 planned
(10.6 s a run): pass 1 took 7.2 min on aifoundry3, 4.0 min on aifoundry1 card 0 and 2.8 min on aifoundry2. Decided on
elapsed time alone, with no measured data reduced or read beyond each pass's `block.json` status: every card runs more
passes inside the claim window (to 05:30 PDT). aifoundry3 runs **12** passes (8 + 4), aifoundry1 card 0 **12** (9 + 3)
and aifoundry2 **14** electrical passes (10 + 4; the extra four run after the dtf-cam block, because aifoundry2's chain
script is running and is never edited while it runs, §7). Same items, duplicates and protocol. The decision rules' df
follow the surviving pass count (§9 rule 1). The extra passes are started by `build/dtf-after.sh` on each box, which
waits for that card's queue (or chain) to end.

**A2 — Wed 21 Oct 2026, 01:05 PDT, after pass 1's gate output and before any family V or family A energy was read.**
The rate gate showed that the issue rate is fixed by the mode, not the data: within every mode it is constant from h = 0
to h = 32 to 1e-4, identical on all three cards, at 0.5814 ops per cycle per hart (modes 202, 300, 302, 306-308), 0.6088
(177, 179, 191, 301, 303, 309), 0.7356 (304, 1A) and 0.7574 (305, 1B). Two registered comparisons cross modes, so, as the
smoke rule above (§7, "every comparison is per flip or within one mode") already requires:
(1) **family V**: each shape is reduced against its own zero rung (`d1b_h*` against `d1b_h0`, no longer `d1a_h0`), and
the cell price is the difference of the two modes' per-flip slopes, 1B minus 1A, over h = 16 and 32; the 0.2% pair gate
between `d1a` and `d1b` (2.96% apart at h = 0, by code) is replaced by each mode's own within-mode rate gate;
(2) **family A**: `a0`, `a1` and `a3` share one rate and form the registered ladder (index distance 0, 1, 3); `a5`
(mode 309, 4.7% faster by code) is reported beside it as rate-confounded and does not enter the slope; the one-sided rule
(exclude 32 fJ per address bit at 3 SE) is read on the matched ladder;
(3) a clerical fix: `participants_expected` is 1,024 × harts, so family R's two-hart arms expect 2,048.
The run-driving fields are unchanged; the analysis reads `manifest-a2.json` (the same items, these three fields
corrected) beside the committed `manifest.json`.

*Anything changed after the pre-registration commit goes here, dated, before the data it touches, and lands by
`mv` between passes (§7) — identified in the reduction by `block_begin`'s `code.sha256`, not by a timestamp. Each
cut taken under §6's cut order is logged here with its clock time. The first candidate is already visible: if the
0.2% pair gate voids `d1a`/`d1b`, the fallback is the in-place accumulator (`fxor.pi f8,f8,f0` in eight
independent chains, reuse distance 8), which measures the same cell energy through a different hazard profile and
needs one more emitted shape.*

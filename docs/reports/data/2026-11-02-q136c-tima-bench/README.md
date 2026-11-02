# Q136(c): the TIMA bench, int8's no-issue excess. What int8's loop runs that fp32's does not, counted on every stream of E109's and E124's design and priced at the bench's own constants: 0.47–0.96 W of the measured 1.57–1.74 W from reset, and 0.15–0.29 W in the card's order, where TenC's reads carry over into fp32 (desk; core-et, a later revision)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 11, "int8 zeros' extra 0.61 W"**, the complaint this answers. It is item 5 of Q134's final critic: "Where int8's no-issue excess goes: 1.57 ± 0.21 W on aifoundry1 card 1 (registered, E124's Y1), and 1.7 W on aifoundry3 (labelled, E109). The candidates are the TIMA units' TenB arrays, TenC's read port, the TIMA controls, the scratchpad's int8 reads, or the core." Its work list begins: "extend the fixed bench to count those arrays and reads". The data it prices are [E109](../2026-11-01-e109-int8-zeros/README.md)'s and [E124](../2026-11-01-e124-int8-zeros-replicate/README.md)'s.*

*Mon 2 Nov 2026 (week 45), Q136, lane desk-q136c-tima-bench, 06:53–08:10 PST. **Desk only**: no card was opened, no device command was sent, there was no ssh, and nothing was measured in watts here. Every watt below is E109's or E124's, named where it is used. The bench is [`rtl-sim/tima_bench/`](../../../../rtl-sim/tima_bench/README.md). It extends Q132(b)'s [`rtl-sim/fma_toggle_v2/`](../../../../rtl-sim/fma_toggle_v2/README.md) (core-et's whole `vpu_top`, Verilator 5.052 with `-fno-dfg`) with E109's `+rows`, `+cols` and `+mask`. It was built and run on a desk machine with `nice -n 10` and at most 6 jobs ([`versions.txt`](versions.txt)). **The RTL is core-et's, the Erbium branch**: a later revision of the ET-SoC-1's lineage, not the ET-SoC-1's own. Every count here is that revision's. Nothing here was registered, and E109's and E124's data were read first.*

## Results

**1. The bench now counts what the first one could not, and nothing it already counted moves.**

The new counts are the four register arrays (TenA; the 16 TenB arrays, two per lane, one in each TIMA unit; TenTMP; the 16 TenC macros), the lane register files, the scratchpad's reads by size, the read and write buses, and every macro register by source line. The checks:
- **E109's desk counts, exactly.** E109's 20 desk streams, compared on all 18 fields per stream, 360 values, give **0 differences** from its committed [`bench-arms.json`](../../../../tools/claims-v3/e109/desk/bench-arms.json) ([`counts.json`](counts.json) › `check_against_e109_bench_arms`).
- **The functional check passes.** Q132(b)'s `fcheck_vpu.py` on this binary leaves **fp32 22,016 of 22,016, fp16 22,016 of 22,016 and int8 18,944 of 18,944** accumulator words exact, and the gate's valid slots equal its rule in 63 of 63 cases ([`fcheck-vpu.json`](fcheck-vpu.json) › `summary`).
- **The latch counts agree with an independent count.** In every stream, storage changes counted at each latch write equal an independent negedge shadow of every entry. Writes agree with the RTL's own enables: TenB writes equal 8 × B half-line reads, TenA writes equal A reads, and TenTMP writes equal int8's 64-bit reads ([`counts.json`](counts.json) › `streams[].per_op.arrays`).
- **A rebuild gives the same counts.** A second build from the committed sources gave identical counts on 62 of 62 streams ([`rebuild-check.txt`](rebuild-check.txt)).

**2. What int8's no-issue loop runs that fp32's does not.** With the row mask 0x0000 nothing issues, and the bench's streams run at the card's own cycles per op (E109 R6: the bench's cycles plus 7.75, matched by both cards to 0.001). Per op on one minion ([`priced.md`](priced.md) §1), and a second chip-wide at E124's measured op rates ([`priced.json`](priced.json) › `experiments.<E124>.per_s.<item>.counts`):

| | `m0.int8.zeros`, an op | `m0.fp32.zeros`, an op | int8, a second | fp32, a second |
|---|---:|---:|---:|---:|
| ops a second (E124, measured) | | | 1.925 × 10⁹ | 1.125 × 10⁹ |
| **TenC reads** (16 macros) | **5,092** = 16 × every one of 318.25 cycles | 0 | **9.80 × 10¹²** | 0 |
| of which at a new address | 4,096 | 0 | 7.89 × 10¹² | 0 |
| **TIMA controls**: register bits clocked on `tima_clk_en` | **33,167** | 0 | **6.38 × 10¹³** | 0 |
| **TenB arrays**: writes (both formats keep B there) | 256 | 256 | 4.93 × 10¹¹ | 2.88 × 10¹¹ |
| TenB latch bits written, data-latch bits opened | 8,192, 16,384 | 8,192, 16,384 | 1.58, 3.15 × 10¹³ | 0.92, 1.84 × 10¹³ |
| **scratchpad reads**: 32-bit, 64-bit, 256-bit | 128, **64**, 32 | 256, 0, 32 | 2.46, 1.23, 0.62 × 10¹¹ | 2.88, 0, 0.36 × 10¹¹ |
| scratchpad bits requested | 16,384 | 16,384 | 3.15 × 10¹³ | 1.84 × 10¹³ |
| TenTMP writes (int8's A path) | 64 | 0 | 1.23 × 10¹¹ | 0 |
| register bits clocked, all (the first bench's count) | 383,331 | 605,295 | 7.38 × 10¹⁴ | 6.81 × 10¹⁴ |

Four readings of that table:
- **TenC is read every cycle**, while the FSM works and through the core's 8-cycle loop, by all 16 TIMA units, whether or not anything issues. That runs at the same rate in every int8 arm (9.80–9.81 × 10¹² a second in `int8.zeros`, `m0`, `k8`, `r8` and `m0k8`), so it is a per-time quantity, the shape E109's and E124's R3 and R0 read on the card.
- **The TIMA controls** are about 107 register bits clocked on every working cycle (33,167 an op over 310 working cycles), at 6.4 × 10¹³ a second, also per-time. They are not new to the count: they sat inside the first bench's "rest". They exceed the whole +5.7 × 10¹³ register bits a second by which int8's loop out-clocks fp32's; fp32-only registers, such as `vpu_tensorfma.v:628` and the lane register file's, net −0.7 × 10¹³ ([`counts.json`](counts.json) › `streams[].per_op.lines`).
- **TenB is where B goes in both formats.** It is the only TenB storage there is, and both TIMA units' write-data latches open on every B write. Per op the two formats write it identically; int8 writes it 1.71 times as often a second.
- **The two formats request the same 16,384 scratchpad bits an op.** int8 reads A in 64-bit halves into TenTMP (`vpu_tensorfma.v:338-366`), so it makes 224 reads an op against fp32's 288.

**3. TenC's read enable carries over: on a card, fp32 reads TenC too, at one frozen address.** TenC's read enable is `f2_tima_ren3`, a register on `tima_clk_en = working && req_int8` (`vpu_tensorfma.v:841`, `:917`). It loads `~first_pass` (`:865`), and only a reset clears it. TenC is clocked by the lane's ungated clock (`vpu_lane_tima.v`, `tenc_rf`). So once any int8 op has run, the enable stays high through every later fp32 op until the next int8 op or a reset. E109's and E124's passes interleave int8 and fp32 runs on cards that had run int8 since their last reset. Run as the card runs them, after two int8 ops (`+pre=2`), **`pre.m0.fp32.zeros` reads TenC 8,708 times an op (16 × 544.25), none at a new address**. That is 9.80 × 10¹² a second, as int8's ([`priced.md`](priced.md) §2). In the card's order, then, TenC's reads are not int8's alone. What stays int8's is the walk of its read address: 7.89 × 10¹² reads a second at a new address, 1.48 × 10¹³ address-bit toggles. Whether silicon does the same is not known here: this is the later revision's logic. Whether a card's minions are reset between launches is not known either.

**4. Priced at the bench's constants, the candidates carry 0.47–0.96 W of N from reset and 0.15–0.29 W in the card's order.** N = S(`m0.int8.zeros`) − S(`m0.fp32.zeros`) is **1.567 ± 0.209 W** on aifoundry1 card 1 (E124, registered Y1) and **1.735 ± 0.164 W** on aifoundry3 (E109, three passes, post hoc; 1.708 ± 0.588 W with the two kept). Here the counts' differences a second are priced at each of Q132(b)'s constant sets: M2 floats and int8, M4 floats, I3 int8. Card 1's prices carry its scale from E82 ([`priced.json`](priced.json) › `experiments.<exp>.contrasts.<contrast>.priced_w`):

| contrast | card | TenB arrays | **TenC read port** | TIMA controls | scratchpad, TenA, TenTMP | **sum** | measured N |
|---|---|---:|---:|---:|---:|---:|---:|
| N from reset (the bench's own order) | card 1 | 0.020–0.041 | **0.357–0.705** | 0.076–0.150 | 0.020–0.040 | **0.473–0.936** | 1.567 ± 0.209 |
| N from reset | aifoundry3 | 0.021–0.042 | 0.367–0.724 | 0.079–0.154 | 0.020–0.042 | **0.487–0.962** | 1.735 ± 0.164 |
| N in the card's order (fp32 after int8) | card 1 | 0.020–0.041 | **0.027–0.054** | 0.076–0.150 | 0.020–0.040 | **0.145–0.285** | 1.567 ± 0.209 |
| N in the card's order | aifoundry3 | 0.021–0.042 | 0.028–0.056 | 0.079–0.154 | 0.020–0.042 | **0.149–0.294** | 1.735 ± 0.164 |

Each range runs from the float constants (M4, M2) to int8's own (I3, M2 int8), whose prices per clocked bit are 1.7–2.0 times the floats'. On zeros almost nothing toggles, so the clocked-bit terms carry nearly everything, and the bus terms carry nothing. The constants were fitted as D over each format's zeros, so pricing what runs *on* zeros extrapolates them, as Q132(b) §14 did and said. These are ranges across models, not statistical intervals. On the clocked-bit price that dominates, the constants' own jackknife errors are 0.8% (M4) and 1.3% (M2) for the floats and 16% for I3 (Q132(b)'s `m4-bench-prediction.json` › `families.*.coef_jackknife_se_fJ`, `analysis.json` › `coef_spread`). **At the measured means, every reading leaves at least 0.63 W of N unpriced, and in the card's order at least 1.28 W of 1.57 W.** Zeros' whole gap G = S(`int8.zeros`) − S(`fp32.zeros`) prices at 0.50–0.98 W from reset and 0.17–0.33 W in the card's order on card 1, against the measured 0.548 ± 0.037 W. G is not a test of these candidates, though: it also carries the lanes, which favour int8 by 1.06 W (E124 R2) ([`priced.json`](priced.json) › `contrasts."zeros' gap G, …"`).

**5. What each candidate would have to cost to carry N alone, against what the bench and the cards allow** ([`priced.json`](priced.json) › `experiments.<exp>.break_even`, `scratchpad_at_one_price`):

| one event | Δ a second, int8 − fp32 | to carry N alone (card 1 / aifoundry3) | what bounds it |
|---|---:|---:|---|
| a TenC read (16 a cycle), from reset | 9.80 × 10¹² | **160 / 177 fJ** | the bench prices its 32 output-register bits at 34 fJ (M4) to 68 fJ (M2 int8); the macro's own access is not in the bench |
| a TenC read at a new address (the card's order) | 7.89 × 10¹² | **199 / 220 fJ** | the same; the bench prices the address walk at 0.03–0.06 W |
| a TIMA control bit clocked | 6.38 × 10¹³ | 24.5 / 27.2 fJ | 11–26 times the bench's 1.07–2.13 fJ a clocked bit: **no** |
| a TenB write (one 32-bit entry) | 2.05 × 10¹¹ | 7.7 / 8.5 pJ | its 32 latch bits and 64 data-latch bits price at about 0.1–0.2 pJ: **no** |
| a scratchpad read, any size | 1.07 × 10¹¹ | 14.6 / 16.2 pJ | if *all* of fp32's no-issue S were reads, one costs at most **0.61 ± 0.13 / 1.16 ± 0.27 pJ**, so int8's extra reads buy at most **0.07 ± 0.01 / 0.12 ± 0.03 W**: **no** |
| a scratchpad bit requested | 1.31 × 10¹³ | 120 / 132 fJ | the same bound per bit: at most **10.8 ± 2.3 / 20.4 ± 4.8 fJ**, so int8's extra bits buy at most **0.14 ± 0.03 / 0.27 ± 0.06 W**: **no** |
| a 64-bit A read into TenTMP (int8 only) | 1.23 × 10¹¹ | 12.7 / 14.1 pJ | a scratchpad read, as above: **no** |
| a working cycle of one minion's FSM in int8 | 5.97 × 10¹¹ | 2.6 / 2.9 pJ | what runs every int8 cycle must cost this, whatever it is |

The per-read ceilings reproduce E124's and E109's own exactly: E124's [`extras.json`](../2026-11-01-e124-int8-zeros-replicate/extras.json) › `reported.read_ceiling_fp32_pj` (0.613 ± 0.128 pJ) and `extra_reads_at_fp32_ceiling_w` (0.066 ± 0.014 W), and E109's [`posthoc.txt`](../2026-11-01-e109-int8-zeros/posthoc.txt) (1.16 ± 0.27 pJ; 0.124 ± 0.030 W). The per-bit ceiling is new: int8 requests 1.71 times fp32's bits a second, the same per op. **Of the four candidates the critic named, only TenC's read port is large enough at a price a register file's read could have**: about 160–220 fJ a 32-bit read, 2.3–6.5 times what the bench prices for the 32 bits it can see (34–68 fJ). In the card's order it would need to cost that per change of address, not per access. The TIMA controls, the TenB arrays and the scratchpad's reads are bounded far below N, the last by fp32's own no-issue level. The core is not in the bench.

**6. One arm separates TenC's address walk from the rest: a single A row.** Desk-only: no card has run it, and nothing here is frozen for one. With one A row (`m0r1`, K = 16, mask 0), **both formats take the same 54.25 bench cycles an op** (62 predicted on a card, with E109's 7.75), so the op-rate difference vanishes, and int8 reads TenC every cycle at one address. Priced at the bench's constants, N with one A row is 0.07–0.14 W in the card's order (TenC exactly 0; the TIMA controls 0.06–0.13 W) and 0.40–0.79 W from reset ([`priced.json`](priced.json) › `contrasts."desk-only arm: N with one A row, …"`). Measured on a card, with fp32 after int8 as it always is there:
- **N with one A row near 0.1 W:** the excess goes with TenC's address walk, or with another per-row activity.
- **Near N:** it is something int8 does every cycle that is neither the walk nor the op rate. Candidates: TenC's reads if they are int8's alone on silicon, the TIMA controls at a far higher price than the bench's, or the core.

Two other desk arms, for completeness ([`priced.md`](priced.md) §3):
- **First_pass on every op is not clean.** first_pass overrides the row mask (`vpu_tensorfma.v:650`), so 16 MUL micro-ops issue an op and the TIMA clocks run. With K = 1 (`f1.m0k1` against `m0k1`) TenC's reads fall from 548 to 228 an op, not to 0: the read enable is still high for 14.25 of the op's 34.25 cycles, the core's loop among them.
- **K = 1 and eight A rows** move the walk and the reads together.

The arm the critic asked for, "a registered arm that changes int8's A path or TenC's addressing", is E129's to register.

**7. The per-stream counts.** All 19 streams of E109's design are in [`priced.md`](priced.md) §1 and [`counts.json`](counts.json) (set `design`): its twelve items, and E78's six anchors (each format's zeros and random tile) and π, which it ran beside them. E124 ran the same design unchanged, and its R10 cell `fp32.a_nz_b_randn` is among them. They are counted per op, and a second at each card's measured rates (`priced.md` › "A second, chip-wide": E109 three passes, E109 two kept, E124). §2 holds the fp32 streams in the card's order, and §3 the desk-only arms. A few more readings:
- **The lanes.** Issuing the micro-ops on zeros (`int8.zeros` against `m0`) turns on 2,432 TIMA clock-gate enables an op and adds 7,296 TIMA control bits. TenC's reads do not change.
- **Item 15's random B.** B's random bytes reach the TenB arrays at **3,490 storage bits changed an op** in both `fp32.a_zeros_b_randn` and `fp32.a_nz_b_randn`, issued or not. The scratchpad's read bus carries 8,890 and 8,922 bit changes an op. This is E109's and E124's transport T, seen in the arrays.
- **Every TenB write opens both TIMA units' write-data latches.** One early enable serves both units of a lane (`vpu_lane.v`, `tenb_wr_en_early`), so 16,384 data-latch bits open an op for 8,192 written.

## What this changes

**Item 11 (critic 5) narrows; it does not close.** The bench now counts every candidate the critic named except the core, per stream, for E109's and E124's design. At the bench's own constants the four price at **0.47–0.96 W of the 1.57–1.74 W from reset, and 0.15–0.29 W in the card's order**. So the bench, as fitted, does not explain int8's no-issue excess. Its breakdown:
- **TenC's read port:** 9.8 × 10¹² reads a second, 16 every int8 cycle. It is the one candidate large enough, at about 0.16–0.22 pJ a read, 2.3–6.5 times its output register's bench price. In this RTL revision its read enable carries over into fp32, so on a card only its address walk would be int8's.
- **The TIMA controls:** 0.08–0.15 W at the bench's prices.
- **The TenB arrays:** 0.02–0.04 W. B goes there in both formats.
- **The scratchpad's int8 reads:** 0.02–0.04 W of VPU-side bits, and at most 0.07–0.27 W of SRAM at one price per read or per bit, bounded by fp32's own no-issue level.

**What is left open:** a macro's own access energy (TenC's), which the bench cannot price; the core; and whether TenC's read enable carries over on silicon. Section 6's one-A-row arm separates the address walk from the rest, as a candidate for E129. For section 11's wording: "the candidates are the TIMA units' TenB arrays, TenC's read port, the TIMA controls, the scratchpad's int8 reads, or the core" can now read "counted and priced: TenB, the TIMA controls and the scratchpad's reads are each bounded below a fifth of the excess; TenC's read port carries it only at about 0.2 pJ a read, and on a card only through its address walk; the core is not counted".

**E109's "the 1.7 W is outside what the bench counts" stands, sharpened:** it is outside what the bench can *price*. The new count shows where int8's loop differs, and none of the differences it can price is large enough.

## For the blog, each from a committed file

*Any line about the RTL is about its later revision (Erbium, core-et), not the ET-SoC-1's own.*

- In int8, each integer unit keeps its accumulators in a small memory beside it. In the open RTL's later revision that memory is read every clock cycle while an int8 matmul runs, even when the zero mask lets nothing through: 16 reads a cycle per core, about 10 trillion a second across the chip. [`priced.json` › `experiments.<E124>.per_s."m0.int8.zeros".counts.tenc.reads`]
- Priced at the simulation's own fitted constants, everything int8's idle loop does that fp32's does not comes to 0.5–1.0 W. The cards measure 1.6–1.7 W, so the simulation's prices do not cover it. [`priced.json` › `contrasts."N, from reset (the bench's own runs)"`; E124 `extras.json` › `added_rules.Y1`]
- The RTL leaves that memory's read switched on after any int8 work, through later float work too. If silicon does the same, the reads themselves cannot be what makes int8 cost more; only their changing address could, at about 0.2 pJ a read. [`counts.json` › stream `pre.m0.fp32.zeros`; `priced.json` › `break_even`]
- Reading the scratchpad cannot explain it at one price: even if fp32's whole idle loop were reads, int8's extra reads would cost at most 0.07–0.12 W, and its extra bits at most 0.14–0.27 W. [`priced.json` › `scratchpad_at_one_price`]
- A test the simulation suggests: give int8 a single row of A. It still reads the accumulator memory every cycle, but always at one address, at exactly fp32's op rate. If the extra cost disappears, it was the address changing. [`priced.json` › `contrasts."desk-only arm: N with one A row, fp32 after an int8 run"`]

## Registered against what happened

Nothing was registered. This is a desk count, made after E109's and E124's data were published and read. The arms of result 6 are desk-only counts, not predictions frozen for any card run: a card arm built on them would register its own.

| | brief (Q136(c), Mon 2 Nov ~06:50 PST) | happened |
|---|---|---|
| the bench | extend Q132(b)'s fixed bench (`-fno-dfg`) to count TenB, TenC's read port, the TIMA controls, the scratchpad's int8 reads | `rtl-sim/tima_bench/`: the arrays, the reads by size and the buses, and every macro register by line; E109's desk counts reproduced exactly, the functional check passes |
| per-stream counts | E109's and E124's designs | 19 design streams, 7 + 3 card-order streams, 8 desk-only arms, 20 check streams; per op and a second at three reductions' rates |
| priced | at the bench's constants | M2, M4, I3; card 1's scale from E82 |
| compute | the Intel, `nice -n 10`, ≤ 6 cores | the same; building took 29 min of wall time for 2 min of CPU (below) |

## Departures (dated)

- **Mon 2 Nov 2026, 07:01–07:28 and 07:41–07:50 PST: the desk machine's load guard paused this lane's build and one run.** Its die read 97 °C, the "hot" tier, and the guard stops agent processes for at most 30 minutes. Each resumed by itself; nothing was killed or changed, and the guard's own controls were not touched. The paused run had been rewriting `counts.json` when it stopped, and finished on resume.
- **07:55 PST: one fault in the first build's accounting, harmless to every count.** `acct_line.cpp` copied `acct.cpp`'s `acct_get`, which reads past its tally array for the fourth unit that `tb_vpu.sv`'s ACCTU line asks for and nothing reads. The committed source returns 0 there. Rebuilt from the committed files, it gave identical counts on 62 of 62 streams ([`rebuild-check.txt`](rebuild-check.txt)). `rtl-sim/fma_toggle_v2/acct.cpp` has the same read and is left as the record.
- **The brief's "the TIMA units' TenB arrays" are not int8's alone.** B goes there in every format, because it is the only TenB storage (`vpu_lane.v`, `LANE_TIMA[*].lane_tima.tenb_rf`). The table counts both formats.

## Device commands sent

**None.** This lane opened no card and no device node, ran no harness and no ssh, and sent no device-management command of any kind, read or write (CONTEXT §17's list is empty for it).

## What this cannot say

- **RTL, not silicon, and a later revision.** The carry-over of TenC's read enable is core-et's logic; the ET-SoC-1's own RTL is not public here.
- **A macro's own read energy is not in the bench**, nor is the dcache's SRAM, nor the core. The prices above are the bench's for the bits it sees: TenC's output register, address and data lines.
- **The constants are extrapolated.** They were fitted as D over each format's zeros on E78's kinds. Here they price what runs on zeros, which no fit has tested (Q132(b) §14).
- **The idle bracket is not modelled.** If a card's minions clock the VPU at idle with TenC's read enable high, those reads are in the idle level too. Either way, they cancel in N in the card's order.
- **The scratchpad is the bench's array.** The read requests (number, size, address) are the RTL's; the data bus's toggles are the bench model's.

## Files, and how to rerun

| file | what |
|---|---|
| [`counts.json`](counts.json) | 65 streams, per TensorFMA op on one minion: the bench's own fields, `x` (the scratchpad and buses), `arrays` (per class: writes, bits, changes, data latch, reads, new-address reads, address and data toggles, the shadow check), `lines` (every macro register: width, clocked, changed, edges); `check_against_e109_bench_arms`; `binary_sha256` |
| [`priced.json`](priced.json), [`priced.md`](priced.md) | the counts a second at E109's (both reductions) and E124's rates; the contrasts priced at M2, M4 and I3; the break-even prices; the scratchpad at one price. `priced.md` is generated from the same run |
| [`fcheck-vpu.json`](fcheck-vpu.json) | the functional check on this binary |
| [`versions.txt`](versions.txt), [`rebuild-check.txt`](rebuild-check.txt) | tools, core-et's commit, the binary's sha256; the two builds compared |

From the repo root (standard library only):

```
VERILATOR=<verilator> CXX=/usr/bin/clang++ JOBS=6 bash rtl-sim/tima_bench/build.sh <scratch>
python3 rtl-sim/tima_bench/run_streams.py --bin <scratch>/obj_q136c/Vtb --out counts.json --jobs 6
python3 rtl-sim/tima_bench/price.py --counts counts.json --out-json priced.json --out-md priced.md
```

`price.py` reads E109's `e109-3pass.json` and `e109.json`, E124's `e124.json`, and Q132(b)'s `analysis.json`, `m4-bench-prediction.json` and `e94-e95-bench-prediction.json`, all committed.

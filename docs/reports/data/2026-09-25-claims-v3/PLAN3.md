# PLAN3: version-3 check of the ET-SoC-1 report claims (both cards, proven effects only)

Planner output, 2026-09-25. No card was touched and no repository file was changed to write it. Inputs: the 11 verified
group inventories in `validate3/inv/*.verified.json` (1,372 claims, 18 pages, 45 inventory experiments), the rendered page
texts in `validate2/final/`, PLAN2 §2.3 for canonical homes, and the runners and workloads in the repository. The
machine-readable twin is `plan3.json` (every claim with its action, every experiment with its commands and predictions).

Standard applied (from the brief): the unit is an independent repeat (pass, session, separately started block, card);
PROVEN-BOTH needs >= 3 repeats on each card, a 99% interval (t on repeat-level values, or an exact test) that excludes the
null on each card and the same sign on both; a best-of-many pick needs Bonferroni. Every prediction below was written
before any run; decisions use the new runs only (committed runs are printed beside, never pooled into a test).

## 0. Summary

| | count |
|---|---|
| PROVEN-BOTH (inventory verdict) | 258 |
| CARD-DIFFERENT (inventory verdict) | 68 |
| ONE-CARD (inventory verdict) | 277 |
| UNDER-REPLICATED (inventory verdict) | 167 |
| WITHIN-NOISE (inventory verdict) | 45 |
| NOT-EMPIRICAL (inventory verdict) | 348 |
| QUOTED (inventory verdict) | 209 |
| all claims | 1372 |

QUOTED claims resolved to their home page's verdict: PROVEN-BOTH 305, CARD-DIFFERENT 110, ONE-CARD 335, UNDER-REPLICATED 202, WITHIN-NOISE 49, NOT-EMPIRICAL 371. 139 of the 209 quoted claims quote a home that is not proven on both cards.

Actions now: keep 562 (+24 wording fixes), keep but inherit an unproven input 88, state per card 110, say "one card" 144 (41 of them because the other card cannot do it), say the runs 58, label as one-off or superseded 38, **drop or weaken now 57**, test with a planned experiment 291.

Experiments: the 45 inventory experiments merge into 13: 7 MUST, 5 SHOULD, 1 that needs the owner's waiver (E6 is not
recommended: §3). Card time (minutes of the
card held by our blocks, including heating on aifoundry2; spacing and waits for other users are extra wall time):

| scope | aifoundry2 | aifoundry3 |
|---|---|---|
| MUST (7 experiments) | 427 min (7.1 h) | 254 min (4.2 h) |
| MUST + SHOULD (12 experiments) | 780 min (13.0 h) | 493 min (8.2 h) |
| + V3-LONG if the owner waives the 10 s rule (D1) | 885 min | 573 min |
| + IDLE-LONG overnight cooling (optional) | +225 min | +90 min |

Builds needed first: memprobe on aifoundry3 (deploy-lab.sh) and a fresh memprobe-v3 build on aifoundry2; the gp-sdk
mmbench on aifoundry3 (deploy-lab-gpsdk.sh + smoke tests); sgemm on aifoundry2; etcfg (host C file) on both; ettelem on
aifoundry3 only if it lacks --reset-ms. No new device code is needed for any MUST or SHOULD experiment.

## 1. Claim table

### 1.1 Counts per page

Verdicts as the verified inventories give them; "Q unproven" = quoted claims whose home is neither PROVEN-BOTH nor arithmetic
on proven inputs. Actions: Keep (incl. wording fixes and arithmetic), Qual. (per card, one card, runs, label), Test (a planned
experiment; MUST in brackets), Drop (drop or weaken now).

| page | claims | PB | CD | 1C | UR | WN | NE | Q | Q unproven | Keep | Qual. | Test (MUST) | Drop |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| limits-of-observability | 136 | 27 | 15 | 6 | 4 | 5 | 42 | 37 | 25 | 81 | 44 | 4 (4) | 7 |
| energy-manual | 178 | 71 | 16 | 15 | 9 | 11 | 31 | 25 | 18 | 109 | 41 | 17 (3) | 11 |
| heat-per-mm | 87 | 42 | 1 | 0 | 1 | 11 | 26 | 6 | 2 | 70 | 3 | 1 (0) | 13 |
| horace-experiment | 138 | 9 | 18 | 48 | 24 | 2 | 24 | 13 | 10 | 36 | 64 | 35 (27) | 3 |
| why-low-power | 70 | 5 | 6 | 7 | 16 | 1 | 24 | 11 | 9 | 31 | 22 | 15 (13) | 2 |
| dvfs-leakage | 82 | 4 | 9 | 26 | 17 | 0 | 15 | 11 | 9 | 21 | 46 | 14 (12) | 1 |
| power-temperature | 58 | 7 | 1 | 16 | 9 | 1 | 9 | 15 | 8 | 23 | 14 | 20 (20) | 1 |
| spatial-temperature-brief | 23 | 4 | 0 | 1 | 5 | 0 | 8 | 5 | 4 | 13 | 5 | 5 (5) | 0 |
| hot-line | 62 | 28 | 0 | 5 | 10 | 2 | 15 | 2 | 1 | 45 | 4 | 12 (12) | 1 |
| on-chip-relay | 49 | 23 | 0 | 3 | 6 | 2 | 9 | 6 | 2 | 35 | 7 | 4 (4) | 3 |
| l2-mainline-starvation | 8 | 0 | 0 | 0 | 0 | 0 | 2 | 6 | 3 | 5 | 3 | 0 (0) | 0 |
| memory-anatomy | 127 | 0 | 0 | 61 | 18 | 2 | 24 | 22 | 16 | 30 | 33 | 59 (59) | 5 |
| memory-hierarchy | 61 | 8 | 1 | 28 | 4 | 1 | 12 | 7 | 4 | 23 | 19 | 17 (15) | 2 |
| on-chip-communication | 61 | 5 | 0 | 25 | 4 | 2 | 17 | 8 | 5 | 25 | 12 | 21 (21) | 3 |
| matmul-efficiency | 48 | 2 | 0 | 7 | 12 | 0 | 16 | 11 | 9 | 20 | 12 | 16 (16) | 0 |
| sparse-compute | 66 | 6 | 0 | 13 | 20 | 1 | 13 | 13 | 9 | 23 | 12 | 30 (30) | 1 |
| testdrive | 14 | 0 | 0 | 0 | 4 | 0 | 7 | 3 | 2 | 8 | 2 | 4 (4) | 0 |
| ridge-points | 104 | 17 | 1 | 16 | 4 | 4 | 54 | 8 | 3 | 76 | 7 | 17 (17) | 4 |
| **all** | 1372 | 258 | 68 | 277 | 167 | 45 | 348 | 209 | 139 | 674 | 350 | 291 (262) | 57 |

Pages resting almost entirely on one card: memory anatomy (61 of 127 ONE-CARD, all aifoundry2), memory hierarchy and on-chip
communication (aifoundry2, one session on 18 Sep), sparse compute (aifoundry3, one run on 18 Sep), matmul efficiency
(aifoundry2, one run per workload). Each gets a MUST experiment on the other card.

### 1.2 Drop or weaken now (57 claims)

Within noise, contradicted, or a cause the data do not measure. Where an experiment could restore a claim it is named; until
it reports, the page carries the weaker statement. The action text is the verified inventory's wording unless marked.

| claim | page | verdict | restorable by | action now |
|---|---|---|---|---|
| hub-047 | limits-of-observability | WITHIN-NOISE | V3-MEM | "Two counters per neighbourhood, not synchronised; a read whose low 7 bits are 0–10 is 128 short; the standard…" → Write "reads whose low 7 bits are 0 to about 10 come back 128 short (aifoundry2; the window moved by one cycle between two launches)" until V3-MEM reports. |
| hub-062 | limits-of-observability | WITHIN-NOISE | V3-MEM | "hpmcounter3 reads 128 short whenever its low 7 bits are 0–10 (on the card)" → As hub-047: "0 to about 10 (aifoundry2, the window moved between launches)". |
| hub-083 | limits-of-observability | WITHIN-NOISE | - | "0.050 ± 0.017 (aifoundry2), 0.064 ± 0.014 (aifoundry3)" → qualify: 'not distinguishable from zero on aifoundry2 (pass fits 0.03-0.06)'; the page's '7–33%' already hedges |
| hub-089 | limits-of-observability | WITHIN-NOISE | - | "the DRAM one differs by 7%" → qualify: 'the DRAM terms agree within their errors (72.9 and 68.1, each +-5 pJ/B)' |
| hub-107 | limits-of-observability | WITHIN-NOISE | - | "plus 0.029 mV per watt of anything else" → qualify: give per card ('0.03 on aifoundry2, not distinguishable from zero across passes; 0.013 on aifoundry3') |
| hub-V01 | limits-of-observability | WITHIN-NOISE | - | "The SRAM and NoC coefficients are collinear with the minion one" → rewrite (contradicted as worded): 'collinear with each other, not with the minion one' |
| hub-V05 | limits-of-observability | WITHIN-NOISE | V3-MEM | "128 short ... 11 [cycles] on the card" → rewrite: '12 cycles in the simulation; 10 to 11 or more on the card, changing between launches (aifoundry2, 19 September)', or drop the card number until E-hub-2 |
| energy-manual-100 | energy-manual | WITHIN-NOISE | V3-CAT | "— 1.6 and 3.2 pJ per byte of line, about 75% of the 2.0 and 4.2 pJ/B a tensor load pays for the same bytes fr…" → qualify: 'roughly 70–90% of a tensor load's cost (not separable from equal on aifoundry2)' |
| energy-manual-102 | energy-manual | WITHIN-NOISE | V3-CAT | "64 B tensor loads from the scratchpad by stride: 64 B 248.3 / 382.1 per 64 B at 1,126 GB/s; 128 B 235.5 / 380…" → qualify: say the same-bank stride halves the bandwidth; its energy per byte is not separable from the others |
| energy-manual-105 | energy-manual | WITHIN-NOISE | V3-CAT | "…or an activation is small next to the transfer (one of 20 pJ/B would have shown)" → qualify: 'one of about 30 pJ/B on zeros, 50 on random data, would have shown' |
| energy-manual-129 | energy-manual | WITHIN-NOISE | V3-RL | "Small messages cost more per byte (the 128 B rows)" → qualify: 'resolved on aifoundry2's shire ring; not yet on aifoundry3' (EXP-EM3) |
| energy-manual-153 | energy-manual | WITHIN-NOISE | V3-RL | "…and the own scratchpad reads 8% below (3.99 against 4.3 … 7.1)" → qualify: 'at the low edge of its bracket (8% below, within noise)' |
| energy-manual-158 | energy-manual | WITHIN-NOISE | - | "Lowest ratios: divuw/zeros 0.75, divu/zeros 0.82, csrr_fccnb/random 0.84, rem/zeros 0.85, srl/zeros 0.85. Hig…" → Drop the lowest/highest-ratio lists: no single entry differs from the common 0.95 after correction. |
| energy-manual-33 | energy-manual | WITHIN-NOISE | - | "An integer add costs 5.7 pJ on zeros [5.2–6.4], barely more than a nop (5.3) or a fence (4.5): on zeros it is…" → qualify: 'an integer add on zeros, 5.7 pJ, is within noise of a nop (5.3) on both cards' |
| energy-manual-40 | energy-manual | WITHIN-NOISE | - | "Transcendentals are the dearest arithmetic: fexp.ps is 159 pJ and flog.ps 219 pJ for eight lanes, at a quarte…" → qualify: 'the transcendentals flog.ps (219 pJ) and fexp.ps (159) rank with the 64-bit divides (142-149) as the dearest arithmetic; frcp.ps (115) is cheaper; only L1-bypass loads/stores and atomics cost more' |
| energy-manual-44 | energy-manual | WITHIN-NOISE | V3-CAT | "The cheapest instruction is fence at 4.5 pJ and the dearest amoaddg.d at 1,393 pJ, a span of 311× (pooled ove…" → qualify: 'the cheapest are fence and nop (4.5–5.3 pJ); the dearest the global atomics amoaddg.w and .d (~1,390 pJ), a span of about 310×' |
| energy-manual-45 | energy-manual | WITHIN-NOISE | - | "Chart annotation: "dearest: amoaddg.d, 1,393 pJ"" → qualify: label the global atomics, not one of them |
| energy-manual-91 | energy-manual | WITHIN-NOISE | - | "The probe does not set the memory's contents, so these rows sit between the zeros and random columns of secti…" → qualify: 'the DRAM level is within noise of the random-data row' |
| heat-21b | heat-per-mm | WITHIN-NOISE | V3-WIRE | "the four-hop point sits 3-7% above the straight line ... for random data and zeros [board power part: 2.6% ze…" → qualify: give the 3-7% for the mesh rail only; on board power only all-ones (11-12%) is resolved |
| heat-22 | heat-per-mm | WITHIN-NOISE | V3-WIRE | "with link-disjoint flows (section 6) the mesh rail grows linearly to within 1%" → qualify: 'with link-disjoint flows the mesh rail grows linearly within the noise (the four-hop point sits 0-2% off the line for random data; 99% bounds +-4%, +-7% for zeros)', or drop '1%' until EXP-heat-1 P14 |
| heat-29 | heat-per-mm | WITHIN-NOISE | - | "the block patterns of section 9 were not fitted and come in below it: slightly for 16-128 B blocks (3-6% belo…" → drop: the 16-128 B blocks are on the model within about 1% when compared over the same hops (also the plane's 'slightly below the plane' for the blocks) |
| heat-32 | heat-per-mm | WITHIN-NOISE | V3-WIRE | "[board power, free links] random bit data part 122 [96-146] fJ/hop (32.7 fJ/mm, '33'), data-independent 52 [3…" → qualify: give the board free-link total (47 fJ/mm, resolved) and say its split into data and fixed parts is not resolved per card with the leakage correction (resolved without it: 118-120 + 53-61 fJ per hop); await EXP-heat-1 |
| heat-36 | heat-per-mm | WITHIN-NOISE | - | "the fit gives 26 fJ per mm per flit-to-flit difference and 35 per one carried, the same within a few percent…" → qualify: keep the per-card values (a2 35, a3 34) and say 'no difference between the cards within the noise (99% bound on the card difference: +-9% for b, +-19% for a)'; drop 'within a few percent' |
| heat-42 | heat-per-mm | WITHIN-NOISE | V3-WIRE | "At one hop, where neither set shares a link, the data-dependent parts agree within 2%, and the totals within…" → qualify: 'agree within the noise (99% bounds +-11% on aifoundry2, +-6% on aifoundry3)'; the 3%/6% total offsets are resolved on aifoundry3 only |
| heat-48 | heat-per-mm | WITHIN-NOISE | V3-WIRE | "On board power the contrast is larger (122 against 186, 52 against 103) but noisier (96-146 over passes for t…" → qualify: on board power only the total contrast (+64-69% over 1-4 hops) is resolved per card; the data/fixed split is not |
| heat-49 | heat-per-mm | NOT-EMPIRICAL | - | "and part of it is the regulator's loss, which grows with load" → Drop "part of it is the regulator's loss, which grows with load" or mark it as an expectation. |
| heat-54 | heat-per-mm | WITHIN-NOISE | - | "The free-link mesh-rail data cost, 25, is just above the top of that range [12-24 fJ]" → qualify: 'at the top of that range' |
| heat-69 | heat-per-mm | WITHIN-NOISE | - | "The x-only and y-only pairs differ by 10-12% over one and two hops - y below x on both cards" → qualify: drop the numbers, keep 'the x-only and y-only sets differ in link sharing, so they cannot separate router from wire' |
| heat-71 | heat-per-mm | NOT-EMPIRICAL | - | "[the regulator's loss is] more on the mesh" → Drop "[the regulator's loss is] more on the mesh" or mark it as an expectation. |
| heat-75 | heat-per-mm | WITHIN-NOISE | V3-WIRE | "On board power ... the same bound is 98% and 58%, so it cannot rule out that most of the board's fixed part i…" → keep the conclusion; replace '98%' by 'about 100% (97% and 115% on the two cards, poorly determined)' |
| heat-V04 | heat-per-mm | WITHIN-NOISE | V3-WIRE | "[implied contrast] the four-hop step appears on the loaded mesh, where link sharing jumps from 32% to 55%, an…" → qualify: present the sharing jump as a coincidence in distance, not as shown by the link-disjoint contrast, until EXP-heat-1 P15 |
| horace-lowpower-022 | horace-experiment | WITHIN-NOISE | - | "Heating per FLOP follows power over idle, not total power ... The ratio of the last two, 2.8, is close to the…" → rewrite: 'the rise ratio (2.85 on aifoundry2, 3.29 on aifoundry3) exceeds the watt ratio (2.63, 2.61): random data heat 8-26% more per board watt than ones' |
| horace-lowpower-025 | horace-experiment | WITHIN-NOISE | V3-ABL-A | "(ladder implied by the same sentence) random exponents alone (52.6 W) cost more than random signs alone (51.4…" → qualify: 'signs and exponents cost about the same (51-53 W)'; keep the mantissa step pending X1 T3 |
| horace-lowpower-126 | horace-experiment | UNDER-REPLICATED | V3-LONG | "The heat predictions also need that card's own thermal network ... aifoundry2's does not transfer, since it i…" → Drop "aifoundry3 sheds heat visibly faster" (its own network gives a larger 7 s response). |
| horace-lowpower-168 | why-low-power | UNDER-REPLICATED | - | "table rows TensorLoad from L2 (42.6 W, +6.2, 2.45 TB, 2.6 pJ/B) and from LPDDR4x (47.0 W, +10.7, 75.5 GB, 142…" → Drop the page's own 142 and 2.6 pJ/B (one aifoundry2 session); quote the energy manual's two-card level values (DRAM 122 [117-129], own L2 per card). |
| horace-lowpower-200 | why-low-power | WITHIN-NOISE | - | "These are the ablation session's values (random fp32 63.9 W at the launch temperature); the Horace experiment…" → rewrite: 'the two sessions agree to 0.2 W; the pages quote 63.9 and 63.4 W because they correct for leakage with different slopes (0.68 and 0.81 W/C)' and use one slope on both pages |
| dvfs-16 | dvfs-leakage | UNDER-REPLICATED | V3-COOL | "Every result checked in this work was correct: the matmul benchmark checks its outputs bit-exact against a ho…" → Drop "every result checked in this work was correct" (contradicted: two relay launches on aifoundry2 returned 1,118 and 1,000 wrong elements while the governor dropped the clock 800->600 MHz inside the launch, discarded 23 Sep attempt); say every other checke… |
| pt-spatial-22 | power-temperature | WITHIN-NOISE | V3-MMB | "The idle law accounts for 7.7 W of the extra 8.9 W as leakage; the rest is why busy power climbs a little fas…" → qualify: keep 'the idle law accounts for 7.7 of the 8.9 W'; drop 'the rest is why busy power climbs a little faster per degree than an idle card' (the remaining 0.6-1.3 W is not established as a slope difference) |
| hotline-relay-l2-37 | hot-line | WITHIN-NOISE | - | "This session is the top of each range except the reading-only row's" → Drop "This session is the top of each range except the reading-only row's". |
| hotline-relay-l2-68 | on-chip-relay | WITHIN-NOISE | - | "All three draw the same power, and one of them gets thirty times as much done with it (4.34 / 4.42 / 5.30 W o…" → drop 'all three draw the same power' / 'at the same power'; say 'within about a watt of each other; the own scratchpad draws 0.5-0.8 W more than DRAM, and next shire vs DRAM could not be told apart' |
| hotline-relay-l2-82 | on-chip-relay | WITHIN-NOISE | V3-LAT | "It does not follow the mean distance (1.6 to 4.5 hops): r = -0.32 and -0.30 against the mean" → qualify: 'over five offsets no relation to the mean hop count could be seen (r = -0.3)'; await E-RL1 (31 offsets) |
| hotline-relay-l2-95 | on-chip-relay | NOT-EMPIRICAL | - | "The relay is the same idea at shire granularity, through the scratchpads, a path that cannot hang" → Drop "a path that cannot hang"; say "a path with no ready-flag handshake; no relay run hung". |
| anatomy-14 | memory-anatomy | UNDER-REPLICATED | - | "⅔ unmetered: 67% off the metered rails (mostly DDR), 18% mesh, 10% SRAM, 5% cores." → Replace the one-card two-run "2/3 unmetered" KPI with the energy manual's two-card figure: 70% of a DRAM byte's energy is on no metered rail (energy-manual-114, PROVEN-BOTH); keep 67% only as "this page's two runs on aifoundry2". |
| anatomy-35 | memory-anatomy | WITHIN-NOISE | V3-MEM | "For memory shires 3, 5 and 7 they instead read 10–30 cycles slower than a closed row: even after the fence, t…" → rewrite: 'With a fence but no wait, 49 of 128 loads still found the row open and read 6-12 cycles fast; that was common for memory shires 0, 1, 2 and 4 and rare for 3, 5, 6 and 7. The loads that missed it read a median 16 cycles above the closed-row time, whi… |
| anatomy-81 | memory-anatomy | UNDER-REPLICATED | - | "The core's share rises from 41 to 64 pJ because it spends longer stalled." → Drop "because it spends longer stalled" (cause not measured); keep the two readings as one card, two runs. |
| anatomy-85 | memory-anatomy | WITHIN-NOISE | - | "The DRAM row itself could not be isolated: a pattern that conflicts on every access costs no more per load th…" → qualify: 'no difference was detectable (two runs each, one card)'; drop 'costs no more per load' |
| anatomy-96 | memory-anatomy | WITHIN-NOISE | V3-MEM | "A simulation of the open RTL (...) shows the mechanism, with a 12-cycle window where this card shows 11: twel…" → Keep the RTL mechanism (12-cycle window in simulation); replace "this card shows 11" by "on aifoundry2 the window was 0-10 in one launch and 0-9 in the other (19 Sep)" until V3-MEM R1/R2 report. |
| memhier-onchip-45 | memory-hierarchy | UNDER-REPLICATED | V3-COOL | "... and at 800 MHz for shire 0." → Drop "... and at 800 MHz for shire 0" (no such chase exists). |
| memhier-onchip-55 | memory-hierarchy | WITHIN-NOISE | - | "Some per-hart cycle counters in the two-hart tests also read high, probably erratum 1.23 (simultaneous PMU re…" → rewrite: 'per-hart cycle counts in one launch differ by 1-5% (two-hart L1) to 6-11% (one-hart DRAM streams) on both cards, because harts finish at different times, so bandwidth uses wall time'; drop 'read high, probably erratum 1.23' |
| memhier-onchip-112 | on-chip-communication | WITHIN-NOISE | V3-RL | "The deltas are small (1.6-2.5 W on a 34 W card, 18 September), and the per-hop slope's r2 is 0.95, so treat t…" → qualify: '+-20% for each configuration's energy; the per-hop slope is 1.3 (aifoundry3) to 2.3 (aifoundry2) pJ/B per hop, known to about +-50%' |
| memhier-onchip-83 | on-chip-communication | WITHIN-NOISE | V3-RL | "Messaging costs 0.7-2.1 pJ per byte inside a shire with 1 KB messages (3.3 with 128 B), busy cores included (…" → Keep 0.7-2.1 pJ/B inside a shire (1 KB, proven on both cards); give the 128 B figure (3.3) as aifoundry2's only ("not resolved on aifoundry3") until V3-RL (c). |
| memhier-onchip-88 | on-chip-communication | WITHIN-NOISE | V3-RL | "less than the 2.71 W of the same cores spinning (18 September); Every configuration drew less power over idle…" → drop 'less than the same cores spinning' for rings inside a shire; say 'about as much as the same cores spinning (within 0.3 W); 1 KB rings across the mesh draw 0.2-1.2 W less'; X3 settles it with 3 passes per card |
| matmul-sparse-testdrive-100 | sparse-compute | WITHIN-NOISE | V3-ABL-B | "The tensor unit itself adds about 0.6 W with all zeros (0.14 pJ per slot), against 15.6 W dense" → qualify: 'under 1 W, not separated from the spin baseline in these runs' and drop the 0.14 pJ, unless E3 (A-zero vs spin, the page's configuration) or E2 (A and B zero vs spin) confirms it |
| ridge-88 | ridge-points | WITHIN-NOISE | V3-RL | "At the spec rates only L3's 3.6 FLOP/B lies above its ridge of 3.0" → qualify: 'at the spec rates L3 (3.6, range 3.2-4.4) sits at or just above the assumed spec ridge of 3.0 and another shire's scratchpad (2.3) just below it: not established'; await ridge-X4 |
| ridge-89 | ridge-points | WITHIN-NOISE | - | "On all-ones operands the balance points stay below, though L3 (9.4 against 10) and DRAM (109 against 130) com…" → qualify: 'on all-ones L3 sits at its ridge (9.4, range 8.3-11.3, against 10): no verdict; DRAM stays below (89 with the byte energy on all-ones data)' (no experiment: margin too small to resolve; drop the verdict now) |
| ridge-91 | ridge-points | WITHIN-NOISE | V3-RL | "Zeros readout: '... and so does TensorSend inside a shire; TensorSend between shires overlaps its ridge' (and…" → qualify: show both rows as 'ranges overlap: no verdict'; the pairs row (3.2 vs 3.3) is not worth testing, the in-shire row (10.0 vs 8.8) can be decided by ridge-X4 with >= 6 passes per card |
| ridge-92 | ridge-points | WITHIN-NOISE | - | "Spec ridges with all-ones operands (readout): 'every level from the shire outward flips (DRAM 89 against 82,…" → qualify: DRAM and L2 overlap their spec ridges on all-ones; no verdict for those rows (no experiment: margin too small to resolve; drop the verdict now) |

### 1.3 Qualify now

#### (a) One card, and the other card cannot do it (41)

aifoundry3's firmware pins 600 MHz (TDP 0 W), so nothing about the governor, 700/800 MHz, V/f or clock changes can be
measured there; aifoundry3 never gets above ~61-66 C and aifoundry2 cannot hold 600 MHz below ~68 C. These stay one card
and the page must say "aifoundry2 only" (or "aifoundry3 only") explicitly. Those also listed under V3-COOL get more
aifoundry2 repeats; a claim resting on a single run is dropped if V3-COOL does not replicate it.

| claim | page | runs now | replicated by | say |
|---|---|---|---|---|
| hub-077 | limits-of-observability | {"a2": 3, "a3": 0} | - | say "aifoundry2 only" (the starved-rail readings happen on aifoundry2 only (aifoundry3's sampler stays at 22 ms)) |
| hub-112 | limits-of-observability | {"a2": 4, "a3": 0} | - | say "aifoundry2 only" (aifoundry3 cannot reach 71-77 C (heater plateau ~61-66 C)); keep, say one card: aifoundry3 idles at 50-59 °C, where it reads 767 mV, stepping to 766 at 58-59 °C in the wire runs |
| energy-manual-119 | energy-manual | {"a2": 0, "a3": 3} | - | say "aifoundry3 only" (aifoundry2's sampler starves on this ring (hub-072)) |
| energy-manual-168 | energy-manual | {"a2": 6, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| horace-lowpower-066 | horace-experiment | {"a2": "E7+E8, 50 runs", "a3": "n/a (pinned)"} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| horace-lowpower-070 | horace-experiment | {"a2": 3, "a3": "impossible"} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| horace-lowpower-183 | why-low-power | {"a2": 2, "a3": "impossible"} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| horace-lowpower-V06 | why-low-power | {"a2": "cool-start idle bins 64-67 C (cold1, cold2)", "a3":… | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-02 | dvfs-leakage | {"a2": 8, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-08 | dvfs-leakage | {"a2": 8, "a3": 22} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-09 | dvfs-leakage | {"a2": 8, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-12 | dvfs-leakage | {"a2": 2, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-22 | dvfs-leakage | {"a2": 26, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-25 | dvfs-leakage | {"a2": 8, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)); qualify: say up-steps were seen at readings up to 66 °C (10% with 66 on both neighbouring samples), never at 67 or above |
| dvfs-26 | dvfs-leakage | {"a2": 2, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-28 | dvfs-leakage | {"a2": 8, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-31 | dvfs-leakage | {"a2": 2, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-33 | dvfs-leakage | {"a2": 2, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-34 | dvfs-leakage | {"a2": 2, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-35 | dvfs-leakage | {"a2": 7, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)); qualify: 'on a cool die only random data at 700-800 MHz exceeds 65 W (at 600 MHz it does too, but only above about 82 °C, where the thermal test already holds the floor)' |
| dvfs-36 | dvfs-leakage | {"a2": 8, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); qualify: give 'median about 0.7 s (0.14-2.0 s over 31 starts on two days)' and say one card |
| dvfs-37 | dvfs-leakage | {"a2": 8, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent) |
| dvfs-72 | dvfs-leakage | {"a2": 2, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-74 | dvfs-leakage | {"a2": 2, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)) |
| dvfs-76 | dvfs-leakage | {"a2": 7, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)); qualify: 'about 0.3 s (0-0.5 s)' |
| dvfs-V02 | dvfs-leakage | {"a2": 2, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); qualify: say the reset comes about 1 s (0.5-1.4 s) after the host sees the kernel end, and that the loop may step up in between; one card (aifoundry3 cannot leave 600 MHz; its log shows one idle event per busy period) |
| dvfs-V03 | dvfs-leakage | {"a2": 2, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); qualify: 'once moving, it changed the clock every 0.1-1 s (median 0.4 s, about three passes)'; one card |
| hotline-relay-l2-11 | hot-line | {"a2": "1 session: 10 moved runs, 2 steady runs", "a3": "im… | V3-COOL | say "aifoundry2 only" (clock-dependent); keep, say one card: add a sentence that the stop was measured at a steady 600 MHz and that aifoundry2's governor, when it moved the clock, let 1-7% through (one session, discarded for the energy bars); one session: if V3-COOL does not replicate it, keep only as a labelled one-session obs… |
| hotline-relay-l2-V09 | on-chip-relay | {"a2": "1 session: DRAM 16 runs with the clock moving, 16 s… | V3-COOL | say "aifoundry2 only" (clock-dependent); add to Method: 'every run reported here passed; the check failed twice (DRAM route, 1,000-1,118 elements) in a discarded aifoundry2 attempt while the governor changed the minion clock mid-run'; one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation… |
| memhier-onchip-09 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-11 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-12 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-14 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); qualify: say the model was fitted on rows 0 and 31 and tested on rows 7 and 24 (61 of 62 within a cycle); one card; one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-35 | memory-hierarchy | {"a2": 1, "a3": 0} | - | say "aifoundry2 only" (needs a clock change or a temperature only aifoundry2 has (aifoundry3 is pinned at 600 MHz, rests at 50-57 C)); qualify: 'mostly came from' (a2 still shows L2 9% above the scratchpad at a pinned 600 MHz); one session: label it as such |
| memhier-onchip-37 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-42 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-43 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-47 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); qualify: say the fit leaves a ~10-cycle spread by requesting shire; one card; one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-V01 | memory-hierarchy | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| memhier-onchip-96 | on-chip-communication | {"a2": 1, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent); one session: if V3-COOL does not replicate it, keep only as a labelled one-session observation (no general statement) |
| ridge-49 | ridge-points | {"a2": 2, "a3": 0} | V3-COOL | say "aifoundry2 only" (clock-dependent) |

#### (b) One card, no test planned (45 own claims)

Descriptions of one session (its idle, its die temperature, its clock), aifoundry2's thermal network and long-run model
(one card in one chassis), and a few details no workload re-measures. Name the card and the session; no generalisation.

| claim | page | text | say |
|---|---|---|---|
| hub-049 | limits-of-observability | workloads/traceprof: 512 events from 32 harts in 2.6 ms of kernel time, 1.57 M cycles; ~20–40 cycle… | name the card and the session (it is one card, one session) |
| energy-manual-124 | energy-manual | The 18 September pair of runs … read 2–20% higher in every configuration (median 10%). | qualify: against aifoundry2's own reruns the old values are −1% to +22% (median +10%) |
| horace-lowpower-007 | horace-experiment | six of them had been predicted from the previous day's data before they first ran, to 1.3 W rms | name the card and the session (it is one card, one session) |
| horace-lowpower-011 | horace-experiment | A three-line model ... predicts those times from the flip counts. On runs it was not fitted to, the… | name the card and the session (it is one card, one session) |
| horace-lowpower-048 | horace-experiment | table: power predicted before the pattern had ever run, by model form (rms 4.2 / 1.3 / 2.7 / 1.3 W;… | name the card and the session (it is one card, one session) |
| horace-lowpower-051 | horace-experiment | the model of section 8, fitted to the long runs ... puts 1.31 C per W in stages of 60 s and longer… | name the card and the session (it is one card, one session) |
| horace-lowpower-054 | horace-experiment | For the three coolest patterns (2 to 5 W over idle) the reading moves by at most one whole degree d… | name the card and the session (it is one card, one session) |
| horace-lowpower-075 | horace-experiment | 29 runs took four hours, because after a hot run the die needs up to seven minutes to get back to 8… | name the card and the session (it is one card, one session) |
| horace-lowpower-076 | horace-experiment | long-run table (28 runs): switching power from flip counts, time to 90 C, fitted model's time and e… | name the card and the session (it is one card, one session) |
| horace-lowpower-082 | horace-experiment | Flip energies: register clocking 3.18 fJ, multiplier tree 0.025 fJ, rest of the unit 0.80 fJ, opera… | name the card and the session (it is one card, one session) |
| horace-lowpower-083 | horace-experiment | Thermal stages 1.5 s 0.106, 4 s 0.050, 60 s 0.234, 150 s 0.136, 400 s 0.860, 2,500 s 0.081 C/W; sum… | keep, say one card; do not quote the slow stages as physics (the page says so) |
| horace-lowpower-085 | horace-experiment | then the flip energies to the busy samples (0.49 W) ... Driven by the measured power it follows the… | name the card and the session (it is one card, one session) |
| horace-lowpower-089 | horace-experiment | each watt adds 1.2 C through the network after ten minutes, 1.47 C once settled | name the card and the session (it is one card, one session) |
| horace-lowpower-091 | horace-experiment | Closed on itself, that loop has a gain of 0.65 x 1.47 = 0.95 at 80 C: a watt of switching held for… | name the card and the session (it is one card, one session) |
| horace-lowpower-093 | horace-experiment | How well it fits: for the 19 runs that reached 90 C the time is off by 12% in the median ... worst… | keep (labelled as fit numbers) |
| horace-lowpower-094 | horace-experiment | held-out table and 'Up to a few minutes it predicts as well as it fits: median 9%, worst 23% (ones,… | name the card and the session (it is one card, one session) |
| horace-lowpower-097 | horace-experiment | The flip budget of this card ... +3.1 W of switching, with the die at 82 C ... The long runs agree:… | keep, say one card and chassis; give 2.6-3.1 W |
| horace-lowpower-109 | horace-experiment | long runs of the structured matrices (Hadamard 75/73 s, kaleidoscope 19/20, ReLU 47/63, -0.0 114/11… | name the card and the session (it is one card, one session) |
| horace-lowpower-110 | horace-experiment | The ReLU pair is a third slow for a 1.2 W miss. Near the card's flip budget the time to a cap is a… | name the card and the session (it is one card, one session) |
| horace-lowpower-112 | horace-experiment | On held-out runs: time to 90 C 9% median error, 23% worst; ten-minute end temperatures 3-5 C too ho… | name the card and the session (it is one card, one session) |
| horace-lowpower-127 | horace-experiment | 46 measured runs and 4 burn-in cycles in 58 minutes. Heating and cooling to the launch point took 1… | keep, say aifoundry2 |
| horace-lowpower-131 | horace-experiment | The two earlier versions of this experiment (20 September: an uncontrolled run, then runs each star… | qualify: 'E8 agrees within 0.4 W; E7 only after its temperature correction' |
| horace-lowpower-V03 | horace-experiment | zeros, checkerboard and random normal 75% zeroed: '< 8 m C per 10^12 FLOPs (rise below the sensor's… | rewrite: 'not resolved by the whole-degree sensor (0.1-0.8 C by the thermal network)' instead of '< 8' |
| horace-lowpower-V05 | horace-experiment | A run ends early when the die reads 90 C, which keeps it inside what this card had already seen (93… | qualify: '93 C on the hottest sensor, 90 C on the mean reading the cap uses' |
| horace-lowpower-189 | why-low-power | The minion, SRAM and NoC rails alone read 22 W with every multiply-add gated, at 80 C | keep, say one card (a3 13.9 W at 56 C) |
| dvfs-66 | dvfs-leakage | aifoundry3, held at 600 MHz, ran the same strict protocol at a 55.8 °C launch (55.77 ± 0.18 °C, 20… | name the card and the session (it is one card, one session) |
| pt-spatial-03 | power-temperature | the die idled at 72 °C here (62-73 °C on other days) | keep, say one card (add that aifoundry3 idles near 50-56 °C) |
| pt-spatial-07 | power-temperature | Idle 31.2 W at 72 °C die; 16 W on the three measured rails, 15 W elsewhere | keep, say one card; point to hub §4.2 for aifoundry3's 12-13 W |
| pt-spatial-19 | power-temperature | t 60 s · matmul · die 84.0 °C · board 62.7 W · minion 29.8 · SRAM 7.2 · mesh 4.9 · unmetered 20.9 W… | name the card and the session (it is one card, one session) |
| pt-spatial-28 | power-temperature | Board minus rails is 15.0 W at idle at 72 °C (15.9 W at 81 °C) | keep, say one card; do not imply a temperature trend from the two windows |
| pt-spatial-41 | power-temperature | The clock stayed at 600 MHz ... Every run here had the die above 70 °C, so it held the lowest opera… | name the card and the session (it is one card, one session) |
| pt-spatial-66 | spatial-temperature-brief | In aifoundry2's telemetry of 20 September the low read 62 °C in all 3,681 samples, 1 °C under the S… | name the card and the session (it is one card, one session) |
| hotline-relay-l2-35 | hot-line | First session, aifoundry2, 10 Hz, die 72-73 C, idle 31.27 W: over idle 1.41 / 2.63 / 1.46 / 1.45 /… | keep (it is labelled first session, a2; the pooled column carries the result) |
| hotline-relay-l2-72 | on-chip-relay | One session on aifoundry2: idle 30.61 W at 71 C, the minion clock at 600 MHz throughout; the kernel… | keep (it describes that session) |
| hotline-relay-l2-V05 | on-chip-relay | This session (aifoundry2, 22 Sep): 4.34 / 4.42 / 5.30 W over idle and 104.8 / 8.9 / 4.25 pJ per byt… | label the reduction, or recompute the session with analyze_reruns.reduce_dir so it pools consistently with the reruns |
| anatomy-104 | memory-anatomy | The standard cycle CSR traps. | keep, say one card (or cite the firmware's counter-enable setting) |
| anatomy-26 | memory-anatomy | In this map memory shires 0–3 sit above the grid and 4–7 below it; their positions come from the fi… | qualify: M2's position is not determined (see anatomy-49) |
| anatomy-V03 | memory-anatomy | Hart 0 of all 1,024 minions walked a working set sized to hit exactly one level, with no evicts. | keep, say 'sized to hit' (a design, checked only by the load rates) |
| memhier-onchip-41 | memory-hierarchy | the die read 63 C before the energy runs | name the card and the session (it is one card, one session) |
| memhier-onchip-111 | on-chip-communication | the card was cooling after another user's matmul (die at 80 C at the start, 77-78 C during the two… | name the card and the session (it is one card, one session) |
| memhier-onchip-59 | on-chip-communication | minion clock 600 MHz and mesh clock 400 MHz throughout | name the card and the session (it is one card, one session) |
| memhier-onchip-86 | on-chip-communication | the 18 September values read 2-20% higher | qualify: '2-20% above the two-card mean (-1% to +22% against aifoundry2's own re-runs)' |
| matmul-sparse-testdrive-42 | matmul-efficiency | aifoundry2 is x86-64 Ubuntu 24.04 with one card (PCIe Gen4, 32 GB, minion shires at 600 MHz, NoC at… | name the card and the session (it is one card, one session) |
| matmul-sparse-testdrive-95 | sparse-compute | The service processor reported 600 MHz in every sample, logged about 4 times a second during the sw… | name the card and the session (it is one card, one session) |
| matmul-sparse-testdrive-97 | sparse-compute | Each configuration then ran 4 s of launches ... The second run used the reverse order. The two agre… | name the card and the session (it is one card, one session) |

#### (c) The cards differ: give per-card values (68 own claims)

Both cards measured, and they disagree beyond noise. Most pages already state both values; the rows below say what to write.
An experiment in the third column re-tests the size or the cause (for example whether scratchpad contents explain the level
differences, or whether the 0.92-0.95 scale is temperature), not the fact of the difference.

| claim | page | re-tested by | say |
|---|---|---|---|
| hub-033 | limits-of-observability | - | keep, state per card |
| hub-034 | limits-of-observability | V3-TEL | qualify: 'one SP pass is 133 ms on aifoundry2 in the SP's own trace (one session, no sampler); under ettelem's 10 Hz sampling, which every power page used, aifoundry2's values change about every 150 ms (148-164 ms over… |
| hub-036 | limits-of-observability | V3-TEL | keep, state per card: τ ≈ 1.15 s and 84% at 2 s on aifoundry2, τ ≈ 1.22 s and 83% on aifoundry3 (the current range already spans both) |
| hub-070 | limits-of-observability | V3-TEL | replace 'whether its SP loop or its PMIC is the slower is not established' with 'its SP's own loop runs about every 260 ms (the timestamps of its governor log, 22 Sep, one window, under 10 Hz sampling); why the same fir… |
| hub-072 | limits-of-observability | - | keep (already per card) |
| hub-073 | limits-of-observability | - | keep |
| hub-074 | limits-of-observability | - | keep |
| hub-075 | limits-of-observability | - | keep |
| hub-078 | limits-of-observability | - | keep |
| hub-082 | limits-of-observability | - | keep (per card already) |
| hub-088 | limits-of-observability | - | keep; optionally 'pinned to about 1% (one standard error)' |
| hub-113 | limits-of-observability | - | keep, state per card: 'about 0.07 mV per watt on aifoundry2, 0.14 on aifoundry3' |
| hub-119 | limits-of-observability | - | keep |
| hub-124 | limits-of-observability | - | qualify: 'Today: 15 W of a 32 W idle on aifoundry2 (13 W of 24 W on aifoundry3) and 3.8-7.5 W of a full-rate DRAM workload are on no sensor' |
| hub-127 | limits-of-observability | V3-TEL | qualify: as hub-034 (the 133 ms) |
| energy-manual-05 | energy-manual | V3-X5, V3-ABL-A, V3-CAT | keep, state per card |
| energy-manual-09 | energy-manual | V3-CAT | keep, state per card |
| energy-manual-109 | energy-manual | - | keep, state per card |
| energy-manual-11 | energy-manual | V3-IDLE | keep, state per card |
| energy-manual-121 | energy-manual | V3-RL | keep, state per card |
| energy-manual-127 | energy-manual | V3-RL | keep, state per card |
| energy-manual-131 | energy-manual | V3-RL | keep, state per card |
| energy-manual-154 | energy-manual | V3-CAT | keep, state per card |
| energy-manual-163 | energy-manual | V3-IDLE | keep, state per card |
| energy-manual-22 | energy-manual | V3-IDLE | keep, state per card |
| energy-manual-46 | energy-manual | V3-CAT | keep, state per card |
| energy-manual-83 | energy-manual | V3-RL | keep, state per card |
| energy-manual-84 | energy-manual | V3-RL | keep, state per card |
| energy-manual-87 | energy-manual | V3-RL | keep, state per card |
| energy-manual-90 | energy-manual | V3-RL | keep, state per card |
| energy-manual-V01 | energy-manual | V3-ABL-A | qualify: 'launched at 80 °C on aifoundry2, 56 °C on aifoundry3' |
| heat-77 | heat-per-mm | - | keep, state per card |
| horace-lowpower-002 | horace-experiment | - | keep, state per card (these are aifoundry2 at 81 C); replace 'in proportion to' with 'roughly in proportion to (random data 8-26% more per watt)' |
| horace-lowpower-008 | horace-experiment | - | keep, state per card (say 'on aifoundry2'; a3's own network also fits to 0.29 C but with more stages) |
| horace-lowpower-013 | horace-experiment | V3-X5 | keep (the page states per-card values) |
| horace-lowpower-014 | horace-experiment | - | keep, state per card |
| horace-lowpower-018 | horace-experiment | - | keep, state per card (factor 15 on a2, 14 on a3; board pJ per card) |
| horace-lowpower-019 | horace-experiment | - | keep, state per card |
| horace-lowpower-020 | horace-experiment | - | keep for aifoundry2; for aifoundry3 give the rise spread (0.2 C); fix the reduction (drop single-sample dropouts in the 1-3 s window) before quoting a3's power spread |
| horace-lowpower-023 | horace-experiment | - | keep, state per card |
| horace-lowpower-027 | horace-experiment | - | keep, state per card |
| horace-lowpower-050 | horace-experiment | - | keep, state per card (say aifoundry2); the physical labels (die/spreader, package/heatsink) are interpretations |
| horace-lowpower-053 | horace-experiment | - | keep, state per card |
| horace-lowpower-059 | horace-experiment | - | keep, state per card |
| horace-lowpower-114 | horace-experiment | - | keep, state per card |
| horace-lowpower-116 | horace-experiment | - | keep (already per card) |
| horace-lowpower-117 | horace-experiment | - | keep; label the residuals as one session with 3 runs (1 for sign and mantissa) |
| horace-lowpower-119 | horace-experiment | V3-X5 | keep; say 'about 7% (3-10% per pattern, differences within noise)' and that the cards ran at different temperatures |
| horace-lowpower-120 | horace-experiment | V3-X5 | keep |
| horace-lowpower-122 | horace-experiment | - | keep |
| horace-lowpower-134 | why-low-power | - | keep, state per card (the byline says aifoundry2) |
| horace-lowpower-138 | why-low-power | V3-ABL-A | keep, state per card (fp16 is one card) |
| horace-lowpower-141 | why-low-power | - | keep, state per card |
| horace-lowpower-145 | why-low-power | V3-ABL-A | keep, state per card |
| horace-lowpower-146 | why-low-power | - | keep, state per card |
| horace-lowpower-153 | why-low-power | - | keep, state per card |
| dvfs-07 | dvfs-leakage | V3-TEL | keep, state per card |
| dvfs-19 | dvfs-leakage | V3-TEL | keep, state per card |
| dvfs-21 | dvfs-leakage | - | keep, state per card |
| dvfs-42 | dvfs-leakage | V3-TEL | keep, state per card |
| dvfs-44 | dvfs-leakage | V3-TEL | keep, state per card |
| dvfs-45 | dvfs-leakage | - | keep, state per card |
| dvfs-48 | dvfs-leakage | - | keep, state per card |
| dvfs-63 | dvfs-leakage | V3-IDLE | keep, state per card: replace +0.73 (one session's bin mean) by '+0.6 W (0.5-0.7 over 16 sessions, 22-24 Sep)'; the chart's shift button likewise |
| dvfs-68 | dvfs-leakage | - | keep, state per card |
| pt-spatial-01 | power-temperature | V3-TEL | state per card and per sampler: while ettelem samples at 10 Hz, board power and the rail records refresh about every 156 ms on aifoundry2 and 263 ms on aifoundry3 (a one-command poller saw 135 ms on aifoundry2); replace… |
| memhier-onchip-34 | memory-hierarchy | V3-RL | state per card: 'within 10%: on aifoundry2 the L2 costs 2.6 against the scratchpad's 2.4 pJ/B, on aifoundry3 2.4 against 2.6; the buffers' contents were not controlled' |
| ridge-16 | ridge-points | - | qualify: aifoundry3 is pinned at 600 MHz; aifoundry2's governor runs up to 800 MHz on a cool die; every measurement on this page is at 600 MHz |

#### (d) Fewer than three repeats and no test planned, one-offs, superseded values (61 own claims)

| claim | page | action | runs now | say |
|---|---|---|---|---|
| hub-061 | limits-of-observability | label | {"a2": 0, "a3": 0} | keep, say once: 'once (two test launches, ~0.5 s each, on <card>)'; name the card (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| hub-079 | limits-of-observability | label | {"a2": 1, "a3": 1} | keep, say once: 'seen once on each card (the first start of E32)' (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| hub-120 | limits-of-observability | label | {"a2": 1, "a3": 1} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| energy-manual-141 | energy-manual | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| energy-manual-169 | energy-manual | label | {"a2": 0, "a3": 0} | qualify: say where the traps were seen, or commit the log (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| energy-manual-41 | energy-manual | label | {"a2": 0, "a3": 0} | qualify: say where the traps were seen, or commit the log (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| energy-manual-92 | energy-manual | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| horace-lowpower-009 | horace-experiment | qualify-runs | {"a2": "zeros 2, randn 3, ones 2 runs (one mornin… | say the card and the number of runs (column "runs now"); no general statement beyond them; keep, say one card; qualify: 'two zero runs and three random runs, a demonstration' (the section says so; the lede and KPI do not) |
| horace-lowpower-052 | horace-experiment | qualify-runs | {"a2": "58 min, 46 runs", "a3": "13 min, 20 runs"} | qualify: 'in-sample, over this session; the five-hour fit of section 8 reaches 0.63 C' |
| horace-lowpower-055 | horace-experiment | qualify-runs | {"a2": "14 patterns", "a3": "8 patterns"} | keep, say 'on aifoundry2 (and in aifoundry3's own refit)'; label as fit numbers |
| horace-lowpower-057 | horace-experiment | label | {"a2": "one 2.8 s window (29 samples) after one n… | keep, say one card (one overnight reading) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| horace-lowpower-067 | horace-experiment | label | {"a2": "one night", "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| horace-lowpower-068 | horace-experiment | qualify-runs | {"a2": "2/2/3 runs", "a3": "impossible"} | say the card and the number of runs (column "runs now"); no general statement beyond them |
| horace-lowpower-069 | horace-experiment | qualify-runs | {"a2": 2, "a3": "impossible"} | say the card and the number of runs (column "runs now"); no general statement beyond them; keep, say one card, two runs |
| horace-lowpower-072 | horace-experiment | qualify-runs | {"a2": 2, "a3": "impossible"} | say the card and the number of runs (column "runs now"); no general statement beyond them |
| horace-lowpower-073 | horace-experiment | qualify-runs | {"a2": "2 zeros vs 3 random runs", "a3": "impossi… | say the card and the number of runs (column "runs now"); no general statement beyond them; keep, say one card; qualify 'in these seven runs' |
| horace-lowpower-081 | horace-experiment | label | {"a2": "one-off", "a3": 0} | keep (a one-off observation, used to exclude two runs) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| horace-lowpower-086 | horace-experiment | label | {"a2": "one reading", "a3": 0} | keep (the page says it is a single measurement) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| horace-lowpower-V04 | horace-experiment | label | {"a2": "one-off readings", "a3": 0} | keep, say one card; '80 C in section 1' is the protocol's held temperature, not an idle equilibrium, so drop it or say 'held at 80 C' (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| horace-lowpower-156 | why-low-power | qualify-runs | {"a2": 2, "a3": "impossible"} | say the card and the number of runs (column "runs now"); no general statement beyond them |
| horace-lowpower-182 | why-low-power | qualify-runs | {"a2": "2 peak readings per pattern (cold1 + cold… | say the card and the number of runs (column "runs now"); no general statement beyond them; keep, say one card (the Caveats do); canonical home for V^2f (PLAN2 row 5b) |
| horace-lowpower-185 | why-low-power | qualify-runs | {"a2": "two 0.5 s stretches at 800 MHz (after the… | say the card and the number of runs (column "runs now"); no general statement beyond them; keep, say one card and two short stretches |
| horace-lowpower-197 | why-low-power | label | {"a2": "2 one-off readings", "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| dvfs-24 | dvfs-leakage | qualify-runs | {"a2": 1, "a3": 0} | qualify: 'in one session (21 Sep), 1 of 44 boundaries with 1-2 ms gaps; with 0.2 s gaps (23 Sep) 4 of 20 dropped to the boot point'; say one card |
| dvfs-27 | dvfs-leakage | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| dvfs-29 | dvfs-leakage | qualify-runs | {"a2": 2, "a3": 0} | say the card and the number of runs (column "runs now"); no general statement beyond them |
| dvfs-30 | dvfs-leakage | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| dvfs-32 | dvfs-leakage | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| dvfs-39 | dvfs-leakage | label | {"a2": 0, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| dvfs-60 | dvfs-leakage | qualify-runs | {"a2": 1, "a3": 0} | qualify: present with dvfs-61's multi-session numbers rather than as a precise single check |
| dvfs-V04 | dvfs-leakage | qualify-runs | {"a2": 1, "a3": 0} | keep, but say 'since our last recorded workload'; store the probe's start time with its data |
| hotline-relay-l2-44 | hot-line | label | {"a2": "1 development run (card not recorded)", "… | qualify: 'hung in the one development run we made (card not recorded)' (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| hotline-relay-l2-92 | on-chip-relay | label | {"a2": "1 development run (card not recorded)", "… | qualify: 'hung in the one development run (card not recorded)' (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| hotline-relay-l2-98 | on-chip-relay | label | {"a2": "development observation", "a3": 0} | qualify: 'faulted during development (card not recorded)' (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-15 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded, say one card and two runs (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-70 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded; say one card, two runs in one session (the energy manual has every level on both cards) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-71 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded; say one card, two runs in one session (the energy manual has every level on both cards) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-72 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded; say one card, two runs in one session (the energy manual has every level on both cards) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-73 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded; say one card, two runs in one session (the energy manual has every level on both cards) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-74 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded; say one card, two runs in one session (the energy manual has every level on both cards) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-75 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded; say one card, two runs in one session (the energy manual has every level on both cards) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-80 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded, say one card (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-82 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded, say one card (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-83 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded (the page already points to Heat per millimetre for a mesh hop) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-84 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded, say one card (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-87 | memory-anatomy | qualify-runs | {"a2": 2, "a3": 0} | qualify: '14–25% higher in every run'; drop the grouping by pattern |
| anatomy-88 | memory-anatomy | qualify-runs | {"a2": 2, "a3": 0} | say the card and the number of runs (column "runs now"); no general statement beyond them |
| anatomy-92 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| anatomy-V02 | memory-anatomy | label | {"a2": 2, "a3": 0} | keep as superseded with anatomy-74, or replace with the energy manual §4.4 rail split (both cards) per PLAN2 §2.3 row 7 (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| memhier-onchip-54 | memory-hierarchy | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| memhier-onchip-56 | memory-hierarchy | qualify-runs | {"a2": 1, "a3": 0} | say the card and the number of runs (column "runs now"); no general statement beyond them |
| memhier-onchip-V03 | memory-hierarchy | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| memhier-onchip-102 | on-chip-communication | label | {"a2": 1, "a3": 0} | label as a one-off / superseded value: name the card, date and n; no general statement from it |
| memhier-onchip-103 | on-chip-communication | label | {"a2": 1, "a3": 0} | qualify: reconcile with the knowledge base (software reset vs power cycle) (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| memhier-onchip-V04 | on-chip-communication | label | {"a2": 1, "a3": 0} | keep as the superseded 18 Sep value; say aifoundry2, two runs (label as a one-off / superseded value: name the card, date and n; no general statement from it) |
| memhier-onchip-V05 | on-chip-communication | qualify-runs | {"a2": 1, "a3": 0} | keep (version history) |
| matmul-sparse-testdrive-26 | matmul-efficiency | qualify-runs | {"a2": 1, "a3": 0} | keep (a description of this run) |
| matmul-sparse-testdrive-33 | matmul-efficiency | qualify-runs | {"a2": 1, "a3": 0} | keep (a description of this run) |
| matmul-sparse-testdrive-65 | sparse-compute | qualify-runs | {"a2": 0, "a3": 1} | keep as a hypothesis (already labelled 'probably') |
| ridge-50 | ridge-points | qualify-runs | {"a2": 2, "a3": 0} | qualify: 'aifoundry2 only, two sessions, launches up to 740 MHz'; await ridge-X2 |
| ridge-51 | ridge-points | qualify-runs | {"a2": 2, "a3": 0} | keep, say 'aifoundry2 only, two sessions' and that PCIe is a prediction; await ridge-X2 |

### 1.4 Quoted claims that quote an unproven home (139 of 209)

Resolved by hand against the home page's claims (`plan3work/quoted_map.py`). A quote inherits its home's verdict: it is
fixed on the quoting page with the same qualifier as the home (per card, one card, runs), and it changes again when the
home's experiment reports. 70 quoted claims point at proven homes and need nothing.

| quoting claim | page | home (verdict) | home tested by | note |
|---|---|---|---|---|
| hub-009 | limits-of-observability | energy-manual-01, dvfs-07, dvfs-04 (UNDER-REPLICATED) | V3-IDLE, V3-MEM, V3-TEL | idle law one card; no power gating one launch |
| hub-010 | limits-of-observability | horace-lowpower-001, horace-lowpower-006, horace-lowpower-009, horace-lowpower-012 (UNDER-REPLICATED) | V3-ABL-A, V3-COOL | 25% faster from a cool die: seven runs one morning |
| hub-011 | limits-of-observability | horace-lowpower-135, horace-lowpower-136, horace-lowpower-158, horace-lowpower-138 (UNDER-REPLICATED) | V3-ABL-A, V3-IDLE | 1.5 W loop one card two runs; 23 W leakage model-dependent |
| hub-012 | limits-of-observability | pt-spatial-01, pt-spatial-46 (UNDER-REPLICATED) | V3-TEL | voltage map one capture |
| hub-013 | limits-of-observability | hotline-relay-l2-62, hotline-relay-l2-85 (UNDER-REPLICATED) | V3-LAT | 'up to a quarter' from one launch per offset |
| hub-015 | limits-of-observability | anatomy-05, anatomy-17, anatomy-18, anatomy-95 (ONE-CARD) | V3-MEM |  |
| hub-016 | limits-of-observability | memhier-onchip-01, memhier-onchip-02, memhier-onchip-05, memhier-onchip-08, energy-manual-84 (ONE-CARD) | V3-LAT, V3-RL | latencies aifoundry2 only; L2 energy card-different |
| hub-017 | limits-of-observability | memhier-onchip-62, memhier-onchip-96, memhier-onchip-73 (ONE-CARD) | V3-COOL, V3-LAT |  |
| hub-018 | limits-of-observability | matmul-sparse-testdrive-01 (ONE-CARD) | V3-MMB |  |
| hub-019 | limits-of-observability | matmul-sparse-testdrive-50, matmul-sparse-testdrive-69 (UNDER-REPLICATED) | V3-ABL-B, V3-LAT |  |
| hub-021 | limits-of-observability | matmul-sparse-testdrive-106 (UNDER-REPLICATED) | V3-LAT |  |
| hub-022 | limits-of-observability | pt-spatial-59 (UNDER-REPLICATED) | V3-TEL |  |
| hub-024 | limits-of-observability | anatomy-70, anatomy-74 (UNDER-REPLICATED) | - | superseded |
| hub-025 | limits-of-observability | pt-spatial-46 (UNDER-REPLICATED) | V3-TEL |  |
| hub-026 | limits-of-observability | horace-lowpower-001, horace-lowpower-010 (ONE-CARD) | V3-LONG | time-to-90 C one card |
| hub-027 | limits-of-observability | dvfs-08 (ONE-CARD) | - |  |
| hub-028 | limits-of-observability | dvfs-04, dvfs-61 (UNDER-REPLICATED) | V3-IDLE, V3-MEM |  |
| hub-029 | limits-of-observability | horace-lowpower-013, dvfs-07 (CARD-DIFFERENT) | V3-TEL, V3-X5 |  |
| hub-047 | limits-of-observability | anatomy-95, hub-V05 (WITHIN-NOISE) | V3-MEM | the 0-10 window changes between launches (hub-V05) |
| hub-048 | limits-of-observability | anatomy-05 (ONE-CARD) | V3-MEM |  |
| hub-062 | limits-of-observability | anatomy-95, hub-V05 (WITHIN-NOISE) | V3-MEM | window 0-10 not constant |
| hub-080 | limits-of-observability | energy-manual-18 (UNDER-REPLICATED) | V3-IDLE |  |
| hub-116 | limits-of-observability | energy-manual-168, energy-manual-164 (ONE-CARD) | - | cool reruns aifoundry2 |
| hub-118 | limits-of-observability | horace-lowpower-020 (CARD-DIFFERENT) | - | a2 +-0.03 C; a3 0.2 C |
| hub-122 | limits-of-observability | energy-manual-05, horace-lowpower-120 (CARD-DIFFERENT) | V3-ABL-A, V3-CAT, V3-X5 |  |
| energy-manual-106 | energy-manual | anatomy-07 (ONE-CARD) | V3-MEM |  |
| energy-manual-116 | energy-manual | hub-036 (CARD-DIFFERENT) | V3-TEL | stated as a range covering both cards: acceptable |
| energy-manual-117 | energy-manual | memhier-onchip-64 (ONE-CARD) | V3-LAT | shire map confirmed by latency on aifoundry2 only |
| energy-manual-125 | energy-manual | hub-072, hub-073 (CARD-DIFFERENT) | - | aifoundry2 only phenomenon; say so |
| energy-manual-130 | energy-manual | memhier-onchip-71 (ONE-CARD) | V3-LAT |  |
| energy-manual-140 | energy-manual | memhier-onchip-107 (ONE-CARD) | V3-LAT |  |
| energy-manual-146 | energy-manual | horace-lowpower-111 (ONE-CARD) | - | pricer output from one-card energies |
| energy-manual-156 | energy-manual | horace-lowpower-120 (CARD-DIFFERENT) | V3-X5 |  |
| energy-manual-159 | energy-manual | hub-034 (CARD-DIFFERENT) | V3-TEL | 133 ms needs sampler/card qualifier |
| energy-manual-16 | energy-manual | dvfs-63 (CARD-DIFFERENT) | V3-IDLE | +0.6 W over 16 sessions, not +0.7 |
| energy-manual-161 | energy-manual | hub-075 (CARD-DIFFERENT) | - |  |
| energy-manual-171 | energy-manual | hotline-relay-l2-62, energy-manual-131 (CARD-DIFFERENT) | V3-RL | energy ratio 11.3x a2, 13.5x a3 |
| energy-manual-174 | energy-manual | dvfs-08 (ONE-CARD) | - | pointer; operating points a2 only by necessity |
| energy-manual-25 | energy-manual | horace-lowpower-176 (UNDER-REPLICATED) | V3-ABL-A |  |
| energy-manual-29 | energy-manual | horace-lowpower-175 (UNDER-REPLICATED) | V3-ABL-A |  |
| energy-manual-58 | energy-manual | horace-lowpower-082 (ONE-CARD) | - |  |
| energy-manual-59 | energy-manual | horace-lowpower-111, horace-lowpower-082 (ONE-CARD) | - | pricer output from one-card energies |
| energy-manual-60 | energy-manual | horace-lowpower-012 (ONE-CARD) | V3-ABL-A |  |
| heat-14 | heat-per-mm | memhier-onchip-64 (ONE-CARD) | V3-LAT |  |
| heat-15 | heat-per-mm | hub-034 (CARD-DIFFERENT) | V3-TEL | per card already; add sampler qualifier |
| horace-lowpower-004 | horace-experiment | matmul-sparse-testdrive-50 (UNDER-REPLICATED) | V3-ABL-B | power saving is aifoundry3, two runs; cycle equality proven both |
| horace-lowpower-031 | horace-experiment | dvfs-08, dvfs-43 (ONE-CARD) | V3-TEL | governor behaviour one card by necessity |
| horace-lowpower-064 | horace-experiment | hub-097, horace-lowpower-027 (CARD-DIFFERENT) | - | 7 W is a2 (a3 4.9 W) |
| horace-lowpower-065 | horace-experiment | dvfs-31, dvfs-35, dvfs-43 (ONE-CARD) | V3-TEL |  |
| horace-lowpower-074 | horace-experiment | dvfs-07 (CARD-DIFFERENT) | V3-TEL |  |
| horace-lowpower-113 | horace-experiment | dvfs-39 (UNDER-REPLICATED) | - | lab-machine state, not a card measurement |
| horace-lowpower-115 | horace-experiment | dvfs-07 (CARD-DIFFERENT) | V3-TEL |  |
| horace-lowpower-124 | horace-experiment | dvfs-63 (CARD-DIFFERENT) | V3-IDLE | +0.6 W over 16 sessions, not +0.73 |
| horace-lowpower-129 | horace-experiment | hub-034 (CARD-DIFFERENT) | V3-TEL |  |
| horace-lowpower-132 | horace-experiment | matmul-sparse-testdrive-50 (UNDER-REPLICATED) | V3-ABL-B |  |
| horace-lowpower-140 | why-low-power | dvfs-04 (UNDER-REPLICATED) | V3-MEM | no power gating: one wake-up launch on aifoundry2 |
| horace-lowpower-142 | why-low-power | energy-manual-01, horace-lowpower-087 (ONE-CARD) | V3-IDLE | 23 W split model-dependent (20-29 W) |
| horace-lowpower-172 | why-low-power | dvfs-08 (ONE-CARD) | - |  |
| horace-lowpower-187 | why-low-power | energy-manual-06 (ONE-CARD) | V3-IDLE |  |
| horace-lowpower-188 | why-low-power | dvfs-61 (ONE-CARD) | V3-IDLE |  |
| horace-lowpower-191 | why-low-power | horace-lowpower-091, horace-lowpower-089 (ONE-CARD) | - |  |
| horace-lowpower-195 | why-low-power | horace-lowpower-027, hub-097 (CARD-DIFFERENT) | - |  |
| horace-lowpower-196 | why-low-power | hub-034, horace-lowpower-182 (UNDER-REPLICATED) | V3-COOL, V3-TEL |  |
| horace-lowpower-198 | why-low-power | horace-lowpower-013 (CARD-DIFFERENT) | V3-X5 |  |
| dvfs-56 | dvfs-leakage | anatomy-60, anatomy-07 (ONE-CARD) | V3-MEM |  |
| dvfs-58 | dvfs-leakage | horace-lowpower-136 (UNDER-REPLICATED) | V3-ABL-A | clock gating mechanism is RTL; the 1.5 W loop is one card, two runs |
| dvfs-59 | dvfs-leakage | horace-lowpower-084, horace-lowpower-087 (ONE-CARD) | V3-IDLE |  |
| dvfs-62 | dvfs-leakage | energy-manual-18, energy-manual-11 (UNDER-REPLICATED) | V3-IDLE | 15.1 W at 73 C is one session (a2) |
| dvfs-67 | dvfs-leakage | horace-lowpower-013, horace-lowpower-120 (CARD-DIFFERENT) | V3-X5 |  |
| dvfs-69 | dvfs-leakage | horace-lowpower-175 (UNDER-REPLICATED) | V3-ABL-A |  |
| dvfs-70 | dvfs-leakage | horace-lowpower-006 (ONE-CARD) | V3-ABL-A |  |
| dvfs-71 | dvfs-leakage | horace-lowpower-182 (UNDER-REPLICATED) | V3-COOL |  |
| dvfs-73 | dvfs-leakage | hub-034, hub-036 (CARD-DIFFERENT) | V3-TEL |  |
| pt-spatial-05 | power-temperature | energy-manual-06, energy-manual-01 (ONE-CARD) | V3-IDLE |  |
| pt-spatial-06 | power-temperature | hub-095, hub-124 (CARD-DIFFERENT) | - |  |
| pt-spatial-09 | power-temperature | hub-036 (CARD-DIFFERENT) | V3-TEL | range covers both cards: acceptable |
| pt-spatial-34 | power-temperature | anatomy-87 (UNDER-REPLICATED) | - |  |
| pt-spatial-37 | power-temperature | hub-113 (CARD-DIFFERENT) | - | 0.07 a2, 0.14 a3 |
| pt-spatial-42 | power-temperature | dvfs-43, dvfs-25 (ONE-CARD) | V3-TEL |  |
| pt-spatial-43 | power-temperature | horace-lowpower-069, horace-lowpower-070 (UNDER-REPLICATED) | V3-COOL |  |
| pt-spatial-44 | power-temperature | memhier-onchip-64 (ONE-CARD) | V3-LAT |  |
| pt-spatial-60 | spatial-temperature-brief | memhier-onchip-64 (ONE-CARD) | V3-LAT |  |
| pt-spatial-61 | spatial-temperature-brief | pt-spatial-46 (UNDER-REPLICATED) | V3-TEL |  |
| pt-spatial-73 | spatial-temperature-brief | horace-lowpower-083 (ONE-CARD) | - |  |
| pt-spatial-75 | spatial-temperature-brief | horace-lowpower-006 (ONE-CARD) | V3-ABL-A |  |
| hotline-relay-l2-58 | hot-line | memhier-onchip-75 (ONE-CARD) | V3-LAT |  |
| hotline-relay-l2-73 | on-chip-relay | energy-manual-86, energy-manual-87, energy-manual-88 (CARD-DIFFERENT) | V3-RL | own scratchpad 2.52 is pooled over a card difference (2.40 / 2.63) |
| hotline-relay-l2-94 | on-chip-relay | memhier-onchip-104, memhier-onchip-102 (UNDER-REPLICATED) | - | mechanism from design; the hang was seen once |
| hotline-relay-l2-105 | l2-mainline-starvation | hotline-relay-l2-14, hotline-relay-l2-07 (UNDER-REPLICATED) | V3-LAT | 0.01-0.05% range includes the one-launch DRAM-homed counts (07) |
| hotline-relay-l2-107 | l2-mainline-starvation | hotline-relay-l2-46, hotline-relay-l2-48, hotline-relay-l2-49 (UNDER-REPLICATED) | V3-LAT | pacing numbers one launch per card (E-HL1) |
| hotline-relay-l2-108 | l2-mainline-starvation | memhier-onchip-104, memhier-onchip-102 (UNDER-REPLICATED) | - | hang seen once |
| anatomy-08 | memory-anatomy | hub-034 (CARD-DIFFERENT) | V3-TEL | 133 ms is aifoundry2 SP pass without a sampler; ~150 ms under ettelem, ~255 ms on aifoundry3 |
| anatomy-09 | memory-anatomy | energy-manual-86, anatomy-74 (UNDER-REPLICATED) | - | 122 pJ/B proven both; the page's own 79 is one card, two runs |
| anatomy-10 | memory-anatomy | heat-55, anatomy-83 (UNDER-REPLICATED) | - | heat per-hop proven both; the page's 0.9 pJ/B is one card, two runs |
| anatomy-110 | memory-anatomy | hub-034 (CARD-DIFFERENT) | V3-TEL | 133 ms needs sampler/card qualifier |
| anatomy-111 | memory-anatomy | hub-034, hub-036 (CARD-DIFFERENT) | V3-TEL |  |
| anatomy-113 | memory-anatomy | memhier-onchip-96 (ONE-CARD) | V3-COOL | one card by necessity (clock) |
| anatomy-114 | memory-anatomy | memhier-onchip-43 (ONE-CARD) | V3-COOL | one card by necessity (clock) |
| anatomy-115 | memory-anatomy | dvfs-05, energy-manual-01 (ONE-CARD) | V3-IDLE | split weakly identified (20-29 W) |
| anatomy-117 | memory-anatomy | memhier-onchip-62 (ONE-CARD) | V3-LAT |  |
| anatomy-22 | memory-anatomy | memhier-onchip-62 (ONE-CARD) | V3-LAT | other requesters 12 cycles/hop: on-chip comm measured on aifoundry2 only (anat-X2 tests) |
| anatomy-39 | memory-anatomy | memhier-onchip-47 (ONE-CARD) | V3-COOL | clock split is one card by necessity |
| anatomy-44 | memory-anatomy | memhier-onchip-43, memhier-onchip-44 (ONE-CARD) | V3-COOL, V3-LAT | clock split is one card by necessity |
| anatomy-76 | memory-anatomy | energy-manual-83, energy-manual-84, energy-manual-86 (CARD-DIFFERENT) | V3-RL | L1/L2 per byte differ by card at home |
| anatomy-89 | memory-anatomy | hub-036 (CARD-DIFFERENT) | V3-TEL | tau 1.15 s a2, 1.22 s a3 |
| anatomy-96 | memory-anatomy | hub-063, hub-V05 (WITHIN-NOISE) | V3-MEM | the card window (11) is hub-V05: varies between launches |
| anatomy-V01 | memory-anatomy | memhier-onchip-01 (ONE-CARD) | V3-LAT |  |
| memhier-onchip-16 | memory-hierarchy | energy-manual-83, energy-manual-84, energy-manual-87, energy-manual-88, energy-manual-86 (CARD-DIFFERENT) | V3-RL | L1, L2, own scratchpad pooled over card differences |
| memhier-onchip-40 | memory-hierarchy | dvfs-08 (ONE-CARD) | - |  |
| memhier-onchip-48 | memory-hierarchy | anatomy-11 (ONE-CARD) | V3-MEM |  |
| memhier-onchip-58 | memory-hierarchy | memhier-onchip-96, anatomy-41, anatomy-11 (ONE-CARD) | V3-COOL, V3-MEM |  |
| memhier-onchip-110 | on-chip-communication | hub-034 (CARD-DIFFERENT) | V3-TEL |  |
| memhier-onchip-67 | on-chip-communication | anatomy-26, anatomy-49 (ONE-CARD) | V3-MEM | M2 position not determined |
| memhier-onchip-83 | on-chip-communication | energy-manual-126, energy-manual-129 (WITHIN-NOISE) | V3-RL | the 128 B figure (3.3) is resolved only on aifoundry2 |
| memhier-onchip-84 | on-chip-communication | energy-manual-127 (CARD-DIFFERENT) | V3-RL | slope 2.3 a2 vs 1.3 a3 |
| memhier-onchip-97 | on-chip-communication | memhier-onchip-14, memhier-onchip-36 (ONE-CARD) | V3-COOL, V3-LAT |  |
| matmul-sparse-testdrive-06 | matmul-efficiency | horace-lowpower-138, horace-lowpower-165 (CARD-DIFFERENT) | V3-ABL-A |  |
| matmul-sparse-testdrive-09 | matmul-efficiency | horace-lowpower-024 (UNDER-REPLICATED) | V3-ABL-A |  |
| matmul-sparse-testdrive-10 | matmul-efficiency | horace-lowpower-001, horace-lowpower-024 (UNDER-REPLICATED) | V3-ABL-A | 51-53 W signs/exponents two runs a2 |
| matmul-sparse-testdrive-11 | matmul-efficiency | energy-manual-56, energy-manual-55 (ONE-CARD) | V3-ABL-A |  |
| matmul-sparse-testdrive-12 | matmul-efficiency | horace-lowpower-138 (CARD-DIFFERENT) | V3-ABL-A |  |
| matmul-sparse-testdrive-32 | matmul-efficiency | hub-034 (CARD-DIFFERENT) | V3-TEL |  |
| matmul-sparse-testdrive-35 | matmul-efficiency | energy-manual-10 (ONE-CARD) | V3-IDLE |  |
| matmul-sparse-testdrive-37 | matmul-efficiency | dvfs-25, dvfs-43 (ONE-CARD) | V3-TEL |  |
| matmul-sparse-testdrive-V02 | matmul-efficiency | dvfs-08 (ONE-CARD) | - |  |
| matmul-sparse-testdrive-103 | sparse-compute | horace-lowpower-013, horace-lowpower-122 (CARD-DIFFERENT) | V3-X5 |  |
| matmul-sparse-testdrive-104 | sparse-compute | dvfs-45 (CARD-DIFFERENT) | - |  |
| matmul-sparse-testdrive-52 | sparse-compute | horace-lowpower-023 (CARD-DIFFERENT) | - | these are aifoundry3 values; name the card |
| matmul-sparse-testdrive-53 | sparse-compute | horace-lowpower-006 (ONE-CARD) | V3-ABL-A |  |
| matmul-sparse-testdrive-79 | sparse-compute | memhier-onchip-73, memhier-onchip-75 (ONE-CARD) | V3-LAT |  |
| matmul-sparse-testdrive-90 | sparse-compute | memhier-onchip-73, memhier-onchip-75 (ONE-CARD) | V3-LAT |  |
| matmul-sparse-testdrive-94 | sparse-compute | memhier-onchip-V08, memhier-onchip-105 (ONE-CARD) | V3-LAT |  |
| matmul-sparse-testdrive-96 | sparse-compute | hub-034 (CARD-DIFFERENT) | V3-TEL |  |
| matmul-sparse-testdrive-V09 | sparse-compute | matmul-sparse-testdrive-29 (ONE-CARD) | V3-ABL-B, V3-MMB |  |
| matmul-sparse-testdrive-112 | testdrive | matmul-sparse-testdrive-01 (ONE-CARD) | V3-MMB |  |
| matmul-sparse-testdrive-119 | testdrive | dvfs-45 (CARD-DIFFERENT) | - |  |
| ridge-83 | ridge-points | energy-manual-51, energy-manual-54 (UNDER-REPLICATED) | V3-ABL-A | int8 0.158 pJ/OP is aifoundry2, two runs |
| ridge-94 | ridge-points | energy-manual-83, energy-manual-84, energy-manual-87, energy-manual-118 (CARD-DIFFERENT) | V3-RL |  |
| ridge-96 | ridge-points | energy-manual-83 (CARD-DIFFERENT) | V3-RL |  |

### 1.5 Arithmetic on unproven inputs (88 NOT-EMPIRICAL claims)

Arithmetic, spec sheets or source reading whose inputs include a one-card, under-replicated or within-noise number. They
keep the weakest input's qualifier (for example the A100 comparisons that use one run of matmul watts). Per page:

- limits-of-observability: hub-003, hub-004, hub-058, hub-068, hub-069, hub-097, hub-117, hub-128
- energy-manual: energy-manual-14, energy-manual-143, energy-manual-144, energy-manual-149, energy-manual-150, energy-manual-157, energy-manual-17, energy-manual-21, energy-manual-V02
- heat-per-mm: heat-51
- horace-experiment: horace-lowpower-028, horace-lowpower-034, horace-lowpower-062, horace-lowpower-092, horace-lowpower-098, horace-lowpower-100, horace-lowpower-123
- why-low-power: horace-lowpower-150, horace-lowpower-151, horace-lowpower-154, horace-lowpower-159, horace-lowpower-160, horace-lowpower-162, horace-lowpower-173, horace-lowpower-184
- dvfs-leakage: dvfs-06, dvfs-65, dvfs-V05
- power-temperature: pt-spatial-15, pt-spatial-49
- hot-line: hotline-relay-l2-27, hotline-relay-l2-53
- memory-anatomy: anatomy-06, anatomy-120, anatomy-21, anatomy-25, anatomy-42, anatomy-53, anatomy-56, anatomy-77, anatomy-V04, anatomy-V05
- memory-hierarchy: memhier-onchip-03, memhier-onchip-17, memhier-onchip-46
- on-chip-communication: memhier-onchip-104, memhier-onchip-106, memhier-onchip-108, memhier-onchip-61, memhier-onchip-89, memhier-onchip-91, memhier-onchip-99, memhier-onchip-V07
- matmul-efficiency: matmul-sparse-testdrive-02, matmul-sparse-testdrive-05, matmul-sparse-testdrive-07, matmul-sparse-testdrive-08, matmul-sparse-testdrive-14, matmul-sparse-testdrive-16, matmul-sparse-testdrive-19, matmul-sparse-testdrive-36, matmul-sparse-testdrive-V01
- sparse-compute: matmul-sparse-testdrive-64, matmul-sparse-testdrive-68, matmul-sparse-testdrive-77, matmul-sparse-testdrive-84, matmul-sparse-testdrive-89, matmul-sparse-testdrive-91
- testdrive: matmul-sparse-testdrive-107, matmul-sparse-testdrive-110, matmul-sparse-testdrive-113
- ridge-points: ridge-52, ridge-71, ridge-76, ridge-87, ridge-90, ridge-93, ridge-95, ridge-V01, ridge-V03

The full input list per claim is in `plan3.json` (`claims[].action_note`).

### 1.6 Claims under test (291)

Until their experiment reports, each carries its current qualifier ("aifoundry2 only", "two runs", ...); the inventory's
`page_action` gives the interim wording. `plan3.json` maps each to its experiment(s) and prediction item(s).

## 2. Experiments

Common rules for every prediction (stated once): the unit is the named independent repeat; PROVEN-BOTH needs the item to hold
on each card; holds on one card and fails on the other gives CARD-DIFFERENT with per-card values; fewer than 3 kept repeats
on a card leaves the claim as it is; a failed prediction is reported as failed and the page takes the measured value (no
refit, no band widened after seeing data); aifoundry2 repeats with any sample off 600 MHz are dropped and re-run; decisions
use the new runs only. 99% t on repeat-level values: df 2 9.925, df 3 5.841, df 4 4.604, df 5 4.032.

| id | priority | merges (inventory experiments) | cards | repeats | claims | a2 min | a3 min |
|---|---|---|---|---|---|---|---|
| V3-MEM | MUST | anat-X1, anat-X2, E-hub-2, EXP-dvfs-1 | both | 5 per card (wake-up probe in passes 1-3 only, as registered) | 80 | 18 | 10 |
| V3-LAT | MUST | memhier-onchip-X1, memhier-onchip-X2, E4, E5, ridge-X3, E-HL1, E-RL1 | both | 3 per card (+2 extra short divergence blocks per card for E4 (f), 5 i… | 104 | 95 | 46 |
| V3-MMB | MUST | E1, ridge-X1, X1 | both | 4 per card (pt X1 needs 4; E1 and ridge-X1 get a fourth pass at no ex… | 50 | 42 | 25 |
| V3-ABL-A | MUST | horace-lowpower-X1, EXP-EM4 | both | 4 shuffled blocks per card (unit = one run: separate process, own app… | 60 | 115 | 65 |
| V3-ABL-B | MUST | E2, E3 | both | 3 shuffled blocks per card; TenB - L1 is a within-block paired differ… | 16 | 59 | 30 |
| V3-X5 | MUST | horace-lowpower-X5, EXP-EM4 | both | 3 hot + 3 cool one-block invocations per card, alternating hot, cool… | 9 | 38 | 30 |
| V3-TEL | MUST | E-hub-1, X4, X2, X3, EXP-dvfs-2 | both | 3 per card, >= 30 min apart, arm order shuffled per pass (python3 -c… | 53 | 60 | 48 |
| V3-WIRE | SHOULD | EXP-heat-1, EXP-heat-2 | both | 6 per card (28 configurations each, shuffled per pass, seed 31+p on a… | 16 | 45 | 38 |
| V3-RL | SHOULD | EXP-EM3, memhier-onchip-X3, ridge-X4 | both | 6 per card; rl then relay in each pass; ring order reversed and ABBA… | 30 | 72 | 43 |
| V3-IDLE | SHOULD | EXP-EM1, EXP-dvfs-4, horace-lowpower-X4 | both | 3 heat/cool cycles per card (short: 15 min of cooling each); IDLE-LON… | 34 | 66 | 80 |
| V3-CAT | SHOULD | EXP-EM2 | both | arm A: a2 8 passes (W H W H W H W H: warm 74-82 C / hold 88 C), a3 6… | 14 | 81 | 78 |
| V3-COOL | SHOULD | EXP-dvfs-3, horace-lowpower-X2, E-HL2, E-RL2, memhier-onchip-X4, ridge-X2 | a2 only | >= 3 cool mornings for the light block (unit = cool period) + >= 3 se… | 40 | 89 | 0 |
| V3-LONG | OWNER | horace-lowpower-X3 | both | 3 runs per pattern per card (unit = run) | 7 | 105 | 80 |
| **MUST total** | | | | | | 427 | 254 |
| **MUST + SHOULD total** | | | | | | 780 | 493 |

### V3-MEM (MUST): Memory anatomy, cycle-counter window and wake-up probe on both cards (memprobe op programs)

Why: The whole memory-anatomy page (61 ONE-CARD claims, 6 KPIs), the hub tile "1 cycle" and the no-power-gating result rest on aifoundry2 only, mostly one launch.

Merges: anatomy:anat-X1, anatomy:anat-X2, hub:E-hub-2, dvfs:EXP-dvfs-1. Cards: both. Suggested experiment number when run: E35.

Build / sync first:
- aifoundry3: scripts/deploy-lab.sh aifoundry3 workloads/memprobe (copies sources + gen_ops.py to ~/nekko, nice -j4 build against aifoundry3's /opt/et; if the tar step fails, rsync workloads/memprobe to ~/nekko/workloads/ and run the same two cmake commands by hand).
- aifoundry2: fresh build so the 19 Sep build stays: cmake -S workloads/memprobe -B build/memprobe-v3 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/memprobe-v3 -j4.
- Record sha256 of each card's kernel/memprobe.elf (the two builds are not one binary; every latency is re-referenced to the pass's own L1 hit).
- New driver run_memprobe_v3.sh (scratch, both hosts): heat() and start_sampler copied from tools/ettelem/run_reruns_warm.sh and run_onchip_power.sh; see new_code N1.

Repeats: 5 per card (wake-up probe in passes 1-3 only, as registered). Order: a2-p1, a3-p1, a2-p2, ... (cards run in parallel; >= 10 min between passes on one card); inside a pass the 11 programs run in shuf order, each its own process.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `Once per card session: BASE=$(timeout 10 $H --info | grep -o '0x[0-9a-f]*' | head -1); assert BASE % 2^30 == 0 (H = build/memprobe-v3/host/memprobe_host on a2, ~/nekko/build/memprobe/host/memprobe_host on a3).`
- Per pass k (off-card first): G="python3 workloads/memprobe/gen_ops.py"; s=$((100+k)); $G timer --out $P; $G ladder --out $P --lines 64 --seed 1; $G decomp --out $P --lines 1500 --reps 3 --pre-delay 1000 --seed $s; $G l3map --out $P --lines 8192; $G msmap --out $P --lines 64 --seed $s; $G bits --out $P --base $BASE --trials 150 --seed $s; $G refresh --out $P --name refresh_jit --n 19000 --jitter 3000 --start 0x1000 --seed $s; $G refresh --out $P --n 24000 --start 0x1000; $G pagetimeout --out $P --row-bit 13 --trials 60 --delays 0,100,200,400,700,1000,1500,2000,3000,5000,8000,12000,20000 --seed $s; t_rawodd: python3 -c "import sys; sys.path.insert(0,'workloads/memprobe'); import gen_ops as g; p=g.Prog(); [(p.stamp(('s',i)), p.raw(('raw',i))) for i in range(4000)]; p.write('$P','t_rawodd',{})"; for S in 7 24 31: $G ladder --out $P/req$S --lines 64 --seed 1; $G decomp --out $P/req$S --lines 1500 --reps 3 --pre-delay 1000 --seed $((200+k)); passes 1-3: $G wakeup --out $P/wake --reps 20 --seed $((20+k)) --delays 0,100,300,1000,10000,100000,1000000,4000000,8000000,16000000.
- Card part: who; pgrep -af '_host|ettelem|dev_mngt' (stop if anyone else); [a2] heat to >= 76 C; start_sampler $P/telemetry.jsonl (ettelem sample --every-ms 100, retry + drain); for p in $(shuf -e t_raw t_glitch t_rawodd ladder decomp l3map msmap bits refresh refresh_jit pagetimeout); do timeout 10 $H --program $P/$p.ops --out-dir $P --budget 8; done; for S in 7 24 31; do for p in ladder decomp; do timeout 10 $H --hart $((64*S)) --program $P/req$S/$p.ops --out-dir $P/req$S --budget 8; done; done; kill $SAMPLER (plain SIGTERM); passes 1-3: timeout 10 build/ettelem/ettelem sample --seconds 1 --every-ms 200 > $P/wake/pre.jsonl; timeout 10 $H --program $P/wake/wakeup.ops --out-dir $P/wake --budget 8; same 1 s sample > post.jsonl.
- `Smoke test first (a2 and a3): one 16-line decomp from shire 7 (--hart 448) to confirm a program runs from another shire.`

Sampler: ettelem sample 10 Hz through the X1/X2 programs; drop an aifoundry2 pass only on telemetry (any sample mhz.minion != 600), never on the refresh period or hop slope (those are under test); re-run dropped passes until >= 3 kept (target 5).

Card minutes: aifoundry2 18, aifoundry3 10.

Reduction: validate3/anatomy-verify/tests/crosscard_v3.py --a2 <kept a2 passes> --a3 <a3 passes> (calls recompute_latency.py --l1-ref --fixed-model and extra_values.py; X2 via extra_values.py --x2-only); cycle-counter window: validate3/hubv phase analysis on t_raw/t_glitch/t_rawodd; wake-up: validate3/dvfs-verify/wake.py per pass dir. Run all on scratch copies (recompute_latency.py writes next to its input).

Pre-registered predictions and decision rules (80 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| MEM-P1 | anatomy-12, anatomy-17, anatomy-30, anatomy-41, anatomy-43 | L3 hits within +-4 cycles of 110 + 12*hops(0, PA[10:6]) for >= 97% of lines; fitted slope in [11.5, 12.5], intercept in [107, 113] (every latency re-referenced to the pass's own L1 hit = 5). | 99% t over 5 pass values inside the band on each card; the >= 97% fraction tested one-sided (lower end of the interval >= 0.97). |
| MEM-P2 | anatomy-05, anatomy-11, anatomy-13, anatomy-16, anatomy-19, anatomy-20, anatomy-24, anatomy-49, anatomy-50, anatomy-51, anatomy-52, anatomy-101 | DRAM (fastest of 3 loads) within +-3 cycles of the 19 Sep model (constant 91, 19 Sep memory-shire positions, NOT refitted) for >= 85% of lines; median residual in [-3, 3]. | one-sided on the fraction (lower 99% bound >= 0.85), 99% t on the median residual inside [-3, 3], each card. |
| MEM-P3 | anatomy-18, anatomy-47, anatomy-48 | msmap: for 64/64 lines the read counter that rises is the PA[8:6] memory shire, every pass. | deterministic: every pass on each card. |
| MEM-P4 | anatomy-54, anatomy-55, anatomy-57 | bits: back-to-back row conflict +40 in [32, 48]; sequential same row -12 in [-15, -9]; other row, issued after, +9 in [6, 12]; other bank in [-2, 2] cycles. | 99% t over passes inside each band, each card. |
| MEM-P5 | anatomy-01, anatomy-40, anatomy-58, anatomy-59, anatomy-60, anatomy-61, anatomy-62, anatomy-63, anatomy-65 | refresh period 2,325 in [2,322, 2,328] cycles (i.e. 600 MHz); closed - open cluster means in [10, 13]; max extra wait in [170, 250]; locked-loop slow fraction in [0.22, 0.28] with no load >= 250 (a pass whose median loop period is outside 512-651 cycles is reported, not failed). | 99% t inside the bands, each card; max < 250 in every pass. |
| MEM-P6 | anatomy-07, anatomy-46, anatomy-64, anatomy-69 | refresh series, pairs with both stamps > 150 cycles from the estimated refresh start: row hits with no refresh between >= 0.98, across a refresh <= 0.02. | one-sided 99% bounds, each card. |
| MEM-P7 | anatomy-66, anatomy-67, anatomy-68 | pagetimeout: pooled z against refresh alone in [-3, 3]; <= 3 of 300 late (3,000-20,000 cycles) pairs find the row open. | every pass, each card. |
| MEM-P8 | anatomy-04, anatomy-29, anatomy-31, anatomy-32, anatomy-33, anatomy-34, anatomy-35, anatomy-36, anatomy-37, anatomy-105, anatomy-106 | ladder medians L2 48 [46, 50], L3 171 [167, 175], DRAM 309 [303, 315]; no-fence residual [+30, +90]; P8b fence-no-wait row-open fraction ms{0,1,2,4} - ms{3,5,6,7} in [0.20, 0.80] and > 0; P8c median excess of the non-open loads over the closed-row model in [+6, +30] and > 0. | 99% t inside each band and excluding 0 where stated, each card. anatomy-35 (memory shires 3, 5, 7 slower) is restored only by P8b/P8c holding on both cards. |
| MEM-P9 | anatomy-45 | L2 reads 44-52 (48) on rep 0 and <= 40 (37) on reps 1-2 for >= 90% of lines. | one-sided on the fraction, each card. |
| MEM-P10 | anatomy-03, anatomy-28, anatomy-94, anatomy-95, anatomy-99, anatomy-100, anatomy-102, anatomy-103, anatomy-V01, anatomy-121 | raw back-to-back pairs all 10 after the <11 fix; +-128 pairs 15.6% in [14.0, 17.2]%; stamps at low bits 11 never short; arena base 1 GB aligned. | deterministic items every pass; fraction by 99% t, each card. |
| MEM-X2 | anatomy-05, anatomy-22, anatomy-50 | from requesters 7, 24, 31: L3 within +-4 of 110 + 12*hops(S, home) for >= 97%, DRAM within +-3 of 110 + 12*hops(S, home) + 91 + 12*hops(home, memory shire) for >= 85% of lines (tests the route and the per-hop cost from other requesters; cannot identify the 91). | one-sided 99% bounds over 5 passes, each card. |
| MEM-R1 | hub-001, hub-063, hub-047, hub-062, anatomy-96 | every launch on both cards: raw pair differences take only 10, 138 and -118; the short values form one block 0..e with e in {9, 10, 11}. | deterministic, any exception fails. |
| MEM-R2 | hub-V05 | aifoundry2: e is not the same in all programs (>= 2 distinct e among its 15 readouts); aifoundry3: reported per readout, two-sided (no prior). | count; page: e constant on both cards -> "low 7 bits 0-e read 128 short (both cards)"; e varies -> "the window is 10-12 cycles and changes between launches; check corrected intervals for +-128 outliers". |
| MEM-R3 | anatomy-100, anatomy-103 | with fixcyc's threshold 11, t_glitch has 0 intervals off by 128 when e = 10 and 1-3% (one counter phase) when e = 9 or 11. | exact per launch. |
| MEM-W | dvfs-04, dvfs-13, dvfs-14, dvfs-15, dvfs-54, dvfs-55, dvfs-57, dvfs-77, dvfs-V05 | wake-up probe (passes 1-3): (P1) L1 paired difference idle - no idle exactly 0 at every idle in >= 19 of 20 lines (exceptions exactly +-128); (P2) L3 median paired difference at 16M cycles within +-2; (P3) L2 no-idle 59-62, every idle >= 1,000 cycles 48-51 in >= 18 of 20 lines, 300-cycle delay within 1 cycle of the 16M median; (P4) DRAM at 16M: 40-85% of lines at +8..+15, rest within +-7, >= 80% same class at 1,000 and 16M; (P5) no level shows a shift >= +5 cycles common to >= 18 of 20 lines at 16M cycles; (P6) clock 600 MHz on aifoundry3, recorded on aifoundry2. | "no wake-up >= 5 cycles up to 16M cycles" PROVEN-BOTH if P5 holds in 3 of 3 passes on each card; a wake-up is claimed if P5 fails in >= 2 of 3 on a card; otherwise mixed. P3's 300-cycle part failing drops only the settling explanation (dvfs-14). |

Also informed by this experiment (no own prediction item; the item of the claim they depend on decides): anatomy-V05, hub-015, hub-048.

### V3-LAT (MUST): Latency, cycle-count and bandwidth sweeps (memhier, nocbench, sparsity, sgemm, hot line, relay, enercat lone-minion streams)

Why: Memory-hierarchy and on-chip-communication KPIs are aifoundry2-only, one session; the sparse-compute cycle counts, masked loads, layer times and work-queue results are aifoundry3-only, one run; the hot-line pacing numbers and relay offsets are one launch per card.

Merges: memhier-onchip:memhier-onchip-X1, memhier-onchip:memhier-onchip-X2, matmul-sparse-testdrive:E4, matmul-sparse-testdrive:E5, ridge:ridge-X3, hotline-relay-l2:E-HL1, hotline-relay-l2:E-RL1. Cards: both. Suggested experiment number when run: E36.

Build / sync first:
- aifoundry2: sgemm is not built on this host: cmake -S workloads/sgemm -B build/sgemm -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/sgemm -j4 (no card needed).
- aifoundry3: rsync the current workloads/{memhier,nocbench,sparsity,onchip}/run_lab.sh, analyze.py and workloads/nocbench/analyze.py to ~/nekko (check `enercat_host --help` lists --minions; sparsity_host flags --where/--masks/--gemv-tree/--variant exist in its usage).
- Hot line and relay: DATA must be an absolute path; do not run a patched runner copy from a scratch dir (runners cd to $(dirname $0)/../..). E-HL1 and E-RL1 use their own nb()/on() loops with timeout 10, so no runner copy is needed.

Repeats: 3 per card (+2 extra short divergence blocks per card for E4 (f), 5 in all). Order: per pass, groups in a per-pass shuffled order (seed = pass): memhier chase, memhier scp, nocbench (3 invocations on a2), sparsity fma/tload/gemv/diverge, E4 extras, ridge-X3 streams, sgemm, hot-line sweep, relay sweep; pass 2 reverses group order inside nocbench; >= 30 min between passes on one card; a2 heated to >= 76 C before any group whose die reads < 70 C.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `memhier: bash workloads/memhier/run_lab.sh <memhier_host> build/v3lat/memhier-<card>-p$K chase ; ... scp  (14 processes, each timeout 10 --budget 8, wait_free between).`
- `nocbench: bash workloads/nocbench/run_lab.sh <nocbench_host> build/v3lat/nocbench-<card>-p$K [classes counts stream functs | matrix sync | allreduce barrier xallreduce loaded] (a2: three invocations, heat before each).`
- sparsity: for g in fma tload gemv diverge; do bash workloads/sparsity/run_lab.sh build/sparsity/host/sparsity_host build/sparsity-v3/<card>-p$K $g; done; extras (each timeout 10 ... --budget 8): tload --where l2 --masks 0xFFFF --shires 0xFFFFFFFF --per-shire 32 --iters N for N = 2000, 20000, 200000; --where dram N = 2000, 20000; gemv --gemv skip --gemv-tree --sweep 0.9,0.95,0.99 --iters 2000 --seed 2 (and 3); diverge --variant {static,refill} --alpha {3,2} --mean-k 64 --kmax 16384 --items 256 --harts 2 --shires 0xFFFFFFFF --per-shire 32 (seed 1) as 5 separate short blocks per card.
- `ridge-X3: timeout 10 build/enercat/host/enercat_host --budget 8 --pattern tload_pat --operands random --shires 0xffffffff --minions 0x1 --slice-bytes 64M --region 64M --stride 1K --access-bytes 1K --seconds 3 --window 240000000, and the same with --shires 0x1 --minions 0x1.`
- `sgemm: for a in "-n 64 --shires 0x1" "-n 512 --shires 0x1" "-n 512" "-n 1024"; do /usr/bin/time -v timeout 10 build/sgemm/host/sgemm_host $a --reps 3; done (keep the printout).`
- hot line (E-HL1): nb() { g=$1; shift; timeout 10 build/nocbench/host/nocbench_host --test hotline --warmup 5 --window 6000000 --pace 0 "$@" | grep NOCBENCH | sed ... >> $DATA/hl1-<card>-p$K/sweep.jsonl; } over the 42 run_hotline.sh configurations + edge N = 19, 21, 22, 23 + N-minion alone baselines N = 1, 2, 4, 8, 12, 16, 19-24 + knee P = 9000, 9500, 9800, 10500 + windows W = 3e6, 24e6, 60e6 for 4 homes + pollers + warm-up 0/10, shuffled with shuf --random-source=<(yes $K); optional last: the scpself bus-error probe then one plain health launch.
- `relay (E-RL1): on() { timeout 10 build/onchip/host/onchip_host --test relay "$@" | grep ONCHIP | sed ... >> $DATA/rl1-<card>-p$K/sweep.jsonl; } over the 86 run_onchip.sh relay configurations + 2 probes + offsets d = 1..31 (--medium hop --stage-bytes 1M --stages 8 --work 1 --hop-distance d), shuffled.`
- `aifoundry2 steady-600 controls for V3-COOL: in each LAT pass on a warm die, one copy of tools/ettelem/run_hotline_power10.sh (next to the original, timeout 10) and 20 relay DRAM --stages 640 + 10 hop --stages 7800 launches (the E-HL2 / E-RL2 warm blocks).`

Sampler: run_lab.sh clock.csv loggers (dev_mngt_service ~4 Hz) for memhier/nocbench/sparsity; ettelem 10 Hz on aifoundry2 for sgemm, hot line, relay and enercat (clock check); drop any aifoundry2 launch whose clock samples in its window read != 600 MHz or whose cycles_max / wall_s > 0.6 GHz, and re-run.

Card minutes: aifoundry2 95, aifoundry3 46.

Reduction: workloads/memhier/analyze.py and workloads/nocbench/analyze.py --memhier <X1 dir> --search (no --embed, on copies), validate3 chases.py and noc_audit.py; workloads/sparsity/analyze.py per pass (no --embed); analyze_hotline.py + a new per-card pass-mean script for P1-P7; analyze_onchip.py + offsets fit (longest_handoff/ring_hops) with the permutation test; pooling script for sgemm and enercat streams.

Pre-registered predictions and decision rules (104 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| LAT-M1 | memhier-onchip-01, memhier-onchip-02, memhier-onchip-04, memhier-onchip-18, memhier-onchip-20, memhier-onchip-23, memhier-onchip-53, hub-016 | every pass, both cards, 600 MHz: L1 5.25+-0.01, read buffer 36.00+-0.05, L2 and local scratchpad 47.00+-0.05 cycles; knees between 512/768 B and 2/4 KB; hart 1 39.0/50.0+-0.05; all pointer checks ok. | deterministic: every pass on each card inside the tolerance; a systematic miss on one card -> CARD-DIFFERENT. |
| LAT-M2 | memhier-onchip-05, memhier-onchip-08, memhier-onchip-39, memhier-onchip-44, memhier-onchip-V02 | L3 (4 MB) from shire 0: 169.0+-1.0, 7: 160.7+-1.0, 24: 159.3+-1.0, 31: 168.9+-1.0 cycles; requester effect L3(0) - L3(24) = 9.7+-1.5; DRAM (256 MB) from 0/31 296+-5, from 7/24 288+-5 cycles. | tolerances every pass; requester effect: 99% t (df 2) excludes 0 and overlaps 9.7+-1.5, each card. Drop any a2 chase with point_ghz >= 0.65. |
| LAT-M3 | memhier-onchip-13, memhier-onchip-26, memhier-onchip-36 | remote scratchpad from shires 0, 7, 24, 31: 99.84 + 12.00*MARTY hops +-1.0 cycle for >= 95% of points; a->b equals b->a within 0.5 cycle; per-pass slope of row 0 = 12.00+-0.05. | every pass, each card. |
| LAT-N1 | memhier-onchip-60, memhier-onchip-98, memhier-onchip-82, memhier-onchip-107 | intra-shire (shires 0, 24): the same 28 fast pairs (7 tree edges per neighbourhood) at 68+-1 cycles, all 468 others 113.5-115; shire barrier 237+-1; 32-minion allreduce 432+-2. | deterministic tolerance per pass per card. |
| LAT-N2 | memhier-onchip-62, memhier-onchip-63, memhier-onchip-64, memhier-onchip-66, memhier-onchip-94, memhier-onchip-95, memhier-onchip-79, memhier-onchip-68, memhier-onchip-74, hub-017 | matrix ping-pong on the MARTY map 150.0+-1.0 + 12.02+-0.05*hops, worst residual <= 2 cycles; --search recovers MARTY's distances in 12/12 restarts; m31 = m0 within 1.5 cycles per pair; 1 KB matrix 12.0+-0.1/hop to 5 hops and 36+-1 beyond; credits 148+-3 + 12.2+-0.2*hops; blocking credit in shire 120+-1. | deterministic tolerance per pass per card; the --search result per card per pass (a different map on aifoundry3 would miss the tolerances by >= 12 cycles). |
| LAT-N3 | memhier-onchip-70 | flag round trip median 535+-60 cycles with no distance dependence: per card, OLS of cycles_per_iter on MARTY hops over the 3 passes' 1,488 pairs with a shire-block bootstrap (10,000 draws). | "no distance dependence" kept as "less than half of TensorSend's 12 cycles/hop" if the 99% bootstrap upper bound < +6 and every pass slope < +6; dropped if the bound >= +12.02 on either card. |
| LAT-N4 | memhier-onchip-71, memhier-onchip-72, memhier-onchip-73, memhier-onchip-75, memhier-onchip-76, memhier-onchip-78, memhier-onchip-105 | stream fits 40/86/135/224 +-3 cycles + 2.33/4.00/3.00/4.64 +-0.1 per register; combine - move within +-0.5 cycle; allreduce 1,024 minions 1,368+-10, all 32 shires = alone within 1; chip barrier 4,995+-25 (1/shire), 5,018+-25 (all); all ok = true. | deterministic tolerance per pass per card. |
| LAT-S1 | matmul-sparse-testdrive-47, matmul-sparse-testdrive-48, matmul-sparse-testdrive-55, matmul-sparse-testdrive-56, matmul-sparse-testdrive-V04, matmul-sparse-testdrive-V06 | cycles/op fp32/fp16 546.0+-0.1 at every sparsity and pattern, int8 318.0+-0.1, TenB 529.1+-0.1, rowmask 544.0+-0.1 (546 with 16 rows), all-1024 546.1+-0.1; fp16 pair result "math" at 50% and 100%; every line ok. | deterministic: any deviation on either card falsifies. |
| LAT-S2 | matmul-sparse-testdrive-58, matmul-sparse-testdrive-59, matmul-sparse-testdrive-V07, ridge-72, ridge-73, ridge-74 | one minion: L2/scp 160/81/45-47 +-2 cycles at 16/8/4 lines; DRAM 730/320/144 +-5%. | pass means (n = 3) inside the bands on each card. |
| LAT-S3 | matmul-sparse-testdrive-60, matmul-sparse-testdrive-61, matmul-sparse-testdrive-62, matmul-sparse-testdrive-63, ridge-31, ridge-40 | all-minion DRAM 8,300+-5% at 16 lines (2,000 loads), 1-8 lines within 20% of it; L2 all-minion 16 lines, cold-L2-fill model: 289+-12 cycles at 2,000 loads, 259.3+-1.5 at 20,000, 256.0-256.6 at 200,000; DRAM 16 lines 8,300+-3% at both lengths. | pass means inside the bands on each card; the 2,000 - 20,000 difference excludes 0 at 99% on both cards -> the page attributes the 2.03 TB/s to the probe's cold start (and quotes 76 GB/s / 2.46 TB/s as the streaming rates). |
| LAT-S4 | matmul-sparse-testdrive-69, matmul-sparse-testdrive-70, matmul-sparse-testdrive-71, ridge-62, ridge-63 | layer (tree, seed 1): 7.54+-0.1 us masked at 0%, 7.31+-0.1 plain, 2.14+-0.1 at 99%; seeds 2-3 at 99%: 1.9-2.5 us. | pass means inside the bands on each card. |
| LAT-S5 | matmul-sparse-testdrive-78, matmul-sparse-testdrive-81, matmul-sparse-testdrive-82, matmul-sparse-testdrive-83, matmul-sparse-testdrive-87, matmul-sparse-testdrive-88 | divergence: lane efficiencies identical to 18 Sep (same seed); throughput within +-3%; static - refill at alpha 3 > +0.1 T/s every pass; refill - static at alpha 2 = +0.017+-0.02 T/s. | alpha-2 crossover: 5 independent short blocks per card, 99% t (df 4) of refill - static must exclude 0 with positive sign on both cards to keep "from alpha = 2", else "between alpha = 3 and 2". |
| LAT-G | matmul-sparse-testdrive-106, matmul-sparse-testdrive-107, matmul-sparse-testdrive-108, matmul-sparse-testdrive-109, matmul-sparse-testdrive-111, hub-021 | sgemm per launch within +-3% of 0.31 / 68.0 / 2.37 / 16.8 ms (1.7 / 3.9 / 113 / 127 GFLOP/s); 0 mismatches in all 1,576,960 outputs every pass; process wall 0.2-0.4 s, peak RSS 1.5-2.5 GB. | pass means (n = 3) 99% t within +-5% of each page value on each card; any mismatch on either card falsifies "silicon results were correct". |
| LAT-R3 | ridge-68, ridge-69, ridge-71 | (a) lone-minion DRAM 16-line 1.40+-0.07 B/minion-cycle, 4-line 1.78+-0.10, 1-line 73+-4 cycles per load; k_hat = 32*c(1)/c(16) in [2.5, 4.5]; lone-minion L2/scp 6.4 and DRAM 1.4 within 10%. (b) enercat one minion 1.40+-0.10, 32 minions 0.88+-0.03 per minion. | 99% t (df 2) per card: k_hat inside [2.5, 4.5] on both -> ridge-68 consistent; above 4.5 on either -> drop "4 lines per round trip"; (one - 32 minions) excludes 0 positive on both -> page adds the concurrency sentence; one-minion enercat ~0.88 -> the 1.40 is the sparsity kernel's. |
| LAT-H | hotline-relay-l2-07, hotline-relay-l2-08, hotline-relay-l2-10, hotline-relay-l2-14, hotline-relay-l2-15, hotline-relay-l2-16, hotline-relay-l2-21, hotline-relay-l2-23, hotline-relay-l2-24, hotline-relay-l2-29, hotline-relay-l2-30, hotline-relay-l2-43, hotline-relay-l2-48, hotline-relay-l2-52, hotline-relay-l2-V01, hotline-relay-l2-V02, hotline-relay-l2-V03, hotline-relay-l2-105, hotline-relay-l2-107 | P1 stopped scratchpad-homed host counts 384+-16 (390+-16 for 0x3 32-minion rows, 295+-16 at N = 24); DRAM-homed <= 0.05% of the same-pass alone count; unstopped fractions within +-2 pp of the committed per-card value; 10 ms shares in [0.997, 1.005]; 10.00+-0.02 and 0.31+-0.01 cycles per atomic. P2 edge: host >= 95% of its N-minion alone rate for N = 19, 20, 21 and <= 1% for N = 22, 23, 24. P3 992 paced: <= 1% at P = 9,000 and 9,500; > 1% at 9,800 and 10,500; mean [50, 60]% at 10,000, [82, 90]% at 12,000, [93, 97]% at 16,000; hammering shires [94, 98]% of unpaced at 10,000. P4 host_ops(60e6 window) <= 2 x host_ops(3e6) for all four home/line combinations. P5 31 one-per-shire requesters: host <= 1%. P6 host at N = 2-20 >= 97% of its N-minion alone rate ("within about a percent" only if every pass mean >= 98.5%). P7 warm-up: in-window count 32*(17 - w)+-32 for w = 0 and 10. | binary outcomes (P2, P4, P5, P7, stop/no-stop parts of P1, P3) in 3/3 passes on each card; magnitudes on pass means with the 99% t (df 2) reported; a band counts as failed if the mean is outside. |
| LAT-R | hotline-relay-l2-65, hotline-relay-l2-76, hotline-relay-l2-79, hotline-relay-l2-82, hotline-relay-l2-83, hotline-relay-l2-84, hotline-relay-l2-85, hotline-relay-l2-V10 | from each card's 5-offset line (941.0 - 35.19 L a2; 930.3 - 33.98 L a3): (i) Spearman rho(L, GB/s) <= -0.5 over the 11 new geometries; (ii) >= 9 of 11 within +-5% of the line; (iii) mean-hops coefficient in GB/s ~ L + mean hops over 16 geometries: 99% CI inside +-10 GB/s per hop; (iv) offset 32-d within +-2% of d; (v) hop/DRAM [11.5, 13.2], own/DRAM [29.0, 33.0]; size, intensity, stage ratios within +-5% of the committed per-card values; two-stage >= 1.05 x the 4-32 mean; DRAM at 256 MB >= 1.05 x at 64 MB. | (i) one-sided permutation test over the 11 new geometries on the 3-pass means, p < 0.01 per card (fails on either card -> drop "falls with the longest hand-off", keep "offset moves bandwidth by up to a quarter"); (iii) equivalence; (iv), (v) on pass means. |

Also informed by this experiment (no own prediction item; the item of the claim they depend on decides): matmul-sparse-testdrive-77.

### V3-MMB (MUST): Tensor matmul benchmark (mmbench): throughput, exactness, power per card; private-tile L2 test; the E5 load step

Why: The matmul page's lede and KPIs (9.5/19.0/71.8 T, exact, 57-62 W) are one run on aifoundry2; the ridge page's int8 7.3 B/cycle cause; the power-temperature page's busy slope and load step are one aifoundry2 session.

Merges: matmul-sparse-testdrive:E1, ridge:ridge-X1, pt-spatial:X1. Cards: both. Suggested experiment number when run: E37.

Build / sync first:
- aifoundry3: scripts/deploy-lab-gpsdk.sh aifoundry3 (run from this checkout; needs external/et-platform with gp-sdk 06605ab; builds kernels and launchers with nice -j4). Smoke tests with logs kept: cd ~/nekko && make mmbench-check DEVICE=silicon; timeout 10 /opt/et/bin/it_test_code_loading --mode=pcie.
- aifoundry3: memprobe dram_seq table for run_thermal.sh: python3 workloads/memprobe/gen_ops.py table --pattern dram_seq --out-file ~/nekko/build/memprobe-data/dram_seq.tbl (memprobe built by V3-MEM); confirm ~/nekko/build/ettelem/ettelem exists.
- rsync scripts/mmbench-power.py, scripts/mmbench-report-data.py, scripts/et-power-log.sh, tools/ettelem/run_thermal.sh to ~/nekko on aifoundry3.
- aifoundry2: already built (~/nekko/build/launchers/mmbench_launcher, ~/nekko/build/kernels/nekko/mmbench.elf); quit et-powertop first.

Repeats: 4 per card (pt X1 needs 4; E1 and ridge-X1 get a fourth pass at no extra setup). Order: per pass: E1 workloads one invocation each in the registered orders (p1 fp32,fp16,int8,DRAM; p2 DRAM,int8,fp16,fp32; p3 int8,fp32,DRAM,fp16; p4 fp16,DRAM,fp32,int8), then ridge-X1 (private/shared alternating per mode; mode orders p1 fp32,fp16,int8; p2 int8,fp16,fp32; p3 fp16,int8,fp32; p4 fp32,int8,fp16), then the run_thermal.sh load step; >= 10 min between passes.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- E1: cd ~/nekko && for w in $ORDER; do python3 scripts/mmbench-power.py --launcher build/launchers/mmbench_launcher --kernel build/kernels/nekko/mmbench.elf --only $w --seconds 6 --out build/mmbench-v3/<card>-p$k/$w; python3 scripts/mmbench-report-data.py build/mmbench-v3/<card>-p$k/$w; done (w in fp32-tensor-L2 fp16-tensor-L2 int8-tensor-L2 fp32-tensor-DRAM; a2: heat to 76 C before a workload whose die reads < 70 C, start at <= 74 C).
- `ridge-X1: timeout 10 build/launchers/mmbench_launcher -k build/kernels/nekko/mmbench.elf -d silicon -m $m -n 4 -p -i $ITERS -r 3 -t 4 >> private.jsonl; sleep 3; timeout 10 ... -m $m -n 16 -i $((ITERS/4)) -r 3 -t 4 >> shared.jsonl (ITERS fp32/fp16 280000, int8 250000).`
- `pt X1: a2: heat() to >= 76 C then tools/ettelem/run_thermal.sh build/x1/a2-p$P; a3: sleep 60; BUILD=$HOME/nekko/build tools/ettelem/run_thermal.sh build/x1/a3-p$P.`

Sampler: mmbench-power.py's et-power-log.sh (board ~8 Hz) for E1; none for ridge-X1 (cycle counters); run_thermal.sh's ettelem 185 s at 10 Hz for pt X1. Drop launches with implied_ghz outside 0.595-0.605; drop and re-run an a2 pt X1 pass with any mhz.minion != 600.

Card minutes: aifoundry2 42, aifoundry3 25.

Reduction: mmbench-report-data.py per pass + pooling script (pass-level mean, sd, 99% t, Welch between cards); cycles/op = cycles_max / ops_per_minion for ridge-X1; validate3/inv/pt-spatial-work/x1_reduce.py per pass then --pool.

Pre-registered predictions and decision rules (50 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| MMB-a | matmul-sparse-testdrive-29, matmul-sparse-testdrive-30, matmul-sparse-testdrive-31, matmul-sparse-testdrive-24, ridge-11, ridge-12, ridge-13, ridge-28, ridge-64, ridge-75, matmul-sparse-testdrive-V09 | cycles/op every launch, both cards: fp32 529.0+-0.5, fp16 529.0+-0.5, int8 280.4+-1.0; DRAM 15,000-16,200 on a2 and within +-6% of a2 on a3. | deterministic: every launch of every pass inside the band on both cards. |
| MMB-b | matmul-sparse-testdrive-01, matmul-sparse-testdrive-03, matmul-sparse-testdrive-V03, matmul-sparse-testdrive-43, hub-018 | 9.511+-0.01 / 19.02+-0.02 / 71.78+-0.08 T(FL)OP/s at 600 MHz, every launch exact with 0 bad minions; smoke tests (mmbench-check, it_test_code_loading) pass on aifoundry3. | deterministic. |
| MMB-c | matmul-sparse-testdrive-04, matmul-sparse-testdrive-21, matmul-sparse-testdrive-23, matmul-sparse-testdrive-25 | above idle (mean_w - idle_before_w): a2 fp32 26+-3 W, fp16 27+-3, int8 28+-3, DRAM 8+-2; a3 = 0.92 x a2 +-3 W. | per card 99% t over 4 pass values excludes 0; a3/a2 ratio of pass means in 0.85-1.0. Board watts are stated per card with die temperature. |
| MMB-d | matmul-sparse-testdrive-22, matmul-sparse-testdrive-05, matmul-sparse-testdrive-07 | board G(FL)OP/s per W higher on a3 than a2 by >= 8% in each L2 mode. | Welch per mode, alpha 0.01/3 (Bonferroni over three modes); a significant difference is labelled "card at its operating temperature", never a card property. |
| MMB-e | matmul-sparse-testdrive-07 | A100 int8 lead (1560 / ET GOP/s per W): a2 1.25-1.45x, a3 1.00-1.25x. | one-sided 99% t vs 1560 per card; if aifoundry3's interval includes 1560 the page drops "the A100 wins int8 efficiency" as a general statement. |
| MMB-f | matmul-sparse-testdrive-34 | rise from the first to the last 1 s of a 6 s L2 workload: +0.5 to +2 W on a2, ~0 on the DRAM workload. | pass values, 99% t, each card. |
| MMB-X1 | ridge-07, ridge-18, ridge-33, ridge-55, ridge-65, ridge-70 | (a) shared controls 529.0+-0.5 (fp32, fp16), 280.4+-1 (int8); (b) private tiles fp32/fp16 529-545 cycles/op; (c) private int8 480-560 cycles/op (3.7-4.3 B/minion-cycle: the shared pool explains 7.3). | deterministic per launch; (b) any card above 560 -> drop "can just keep fp32 and fp16 busy"; (c) <= 330 on both cards refutes the shared-pool cause; 330-480 -> report, cause open. |
| MMB-T | pt-spatial-02, pt-spatial-04, pt-spatial-08, pt-spatial-20, pt-spatial-21, pt-spatial-22, pt-spatial-23, pt-spatial-24, pt-spatial-25, pt-spatial-26, pt-spatial-27, pt-spatial-29, pt-spatial-31, pt-spatial-32, pt-spatial-38, pt-spatial-39, pt-spatial-V02, horace-lowpower-030, horace-lowpower-090 | load step (4 passes): P1 busy slope from 5 s after launch a2 0.80+-0.10 W/C at ~75-88 C, a3 0.45+-0.15; P2 minion-rail share a2 0.45-0.55, a3 0.40-0.60; P3 idle after - idle before a2 +3 to +7 W, a3 +1 to +4 W, a2 within +-0.7 W of the idle law; P4 DRAM phase remainder +3 to +7 W, minion rail < +1.0 W; P5 die_mv.ddr in the DRAM phase 2-5 mV below the idle trend, within 1 mV under the matmul; P6 droop per W of minion-rail rise: 99% interval excludes 0 (band a2 0.03-0.08, a3 0.03-0.15 reported); P7 at tau = 0 the remainder overshoots >= 10 W at the start and dips >= 2 W at the stop, filtered with the card's tau (1.15 / 1.22 s) within +-1 W; P8 /PMIC board average - board/ <= 0.5 W steady; P9 600 MHz throughout; P10 a2 cools 4-8 C in the 40 s after the matmul. | 99% t over passes (df 3): P1, P3, P4 remainder, P5, P6 exclude 0 on each card with the mean in band; P4 minion rail and P8 upper bounds; P7, P9 every pass; sign disagreement -> CARD-DIFFERENT; magnitude only -> per card. The busy-minus-idle clause (pt-spatial-22) is not decided by 4 passes (needs ~8 per card): it stays dropped. |

Also informed by this experiment (no own prediction item; the item of the claim they depend on decides): matmul-sparse-testdrive-41.

### V3-ABL-A (MUST): Tensor-unit energy by operands, precision, structure and active minions, strict start (run_ablation.sh, 7 s runs)

Why: why-low-power KPIs (0.32 / 2.7 / 6.0 pJ per MAC, the 1.5 W integer loop, linear in minions), Horace's structured matrices, negative zero and bit-field ladder, and the energy manual's fp16/int8 rows are aifoundry2-only, two runs in one session.

Merges: horace-lowpower:horace-lowpower-X1, energy-manual:EXP-EM4. Cards: both. Suggested experiment number when run: E38.

Build / sync first:
- Patched runner copy build/v3abl/run_ablation_v3.sh (untracked, both hosts): cd "${REPO:?}" instead of the dirname line; timeout 10 instead of $((secs+5)); args=${args//@TSEED@/$(( block % 2 + 1 ))}; SEED_OFFSET added to both seed expressions; wait while lsmod et_soc1 use count > 1 before each run.
- Config abl_a.cfg = validate3/inv/horace-lowpower-work/x1.cfg (19 lines) + fp16_zeros, fp16_ones, int8_zeros, int8_ones from tools/ettelem/ablation.cfg (23 lines). Record sha256 of the cfg, x1_predictions.json and this plan before the first run.
- aifoundry3: rsync docs/reports/data/2026-09-21-horace-aifoundry2/structured_tiles/ to the same path under ~/nekko and compare sha256 with the committed files.

Repeats: 4 shuffled blocks per card (unit = one run: separate process, own approach to the launch temperature). Order: one invocation per card, blocks shuffled by the runner; cards in parallel.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `a2: REPO=$PWD bash build/v3abl/run_ablation_v3.sh build/v3abl-a build/v3abl/abl_a.cfg 4 7 80 84 build/sparsity/host/sparsity_host`
- `a3: ssh aifoundry3 'cd ~/nekko && REPO=$PWD bash build/v3abl/run_ablation_v3.sh build/v3abl-a build/v3abl/abl_a.cfg 4 7 55 60 build/sparsity/host/sparsity_host'`

Sampler: ettelem 10 Hz for the whole session (started by the runner). Runs with any sample mhz.minion != 600 dropped before analysis.

Card minutes: aifoundry2 115, aifoundry3 65.

Reduction: python3 tools/ettelem/analyze_ablation.py build/v3abl-a --out abl_a_<card>.json --leak 0.81 --launch-temp 80.9 (a3: --leak 0.55 --launch-temp 55.8; never the default 0.68), then x1_reduce.py (pre-registered dropout rule: drop samples > 2 W below the window median in seconds 1-3, report the count) applying x1_predictions.json; a3 refit of the four flip energies (leave-one-out) from the same runs.

Pre-registered predictions and decision rules (60 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| ABL-T1 | horace-lowpower-107 | -0.0 costs like ones (/negzero - ones/ < 1.0 W) and > +6 W over +0.0, both cards. | Bonferroni family of 19 sub-tests per card, alpha 0.01/19 (t 6.7 at df 6); equivalence: corrected interval inside +-1.0 W; difference: excludes 0 with the predicted sign and point estimate inside the tolerance. |
| ABL-T2 | horace-lowpower-026, horace-lowpower-045, horace-lowpower-049 | A ones/B random - A random/B ones = +3.5+-1.0 W (a2), +3.2+-1.0 W (a3). | as T1. |
| ABL-T3 | horace-lowpower-017, horace-lowpower-024, horace-lowpower-025, horace-lowpower-046, horace-lowpower-V02 | signs - ones +4.7/+4.3, mant - signs +9.0/+8.3 (+-1.5), randn - mant +3.0/+2.4 (+-1.0) W (a2/a3). | as T1. horace-025 ("exponents cost more than signs") is not tested and stays dropped: pow2 - signs is not in the family. |
| ABL-T4 | horace-lowpower-012, horace-lowpower-102, horace-lowpower-103, horace-lowpower-104, horace-lowpower-105, horace-lowpower-106, horace-lowpower-108 | aifoundry3 structured switching = 0.924 x model within 1.0 W for Hadamard, butterfly, kaleidoscope; DFT pair +2.7+-1.0 W and ReLU +1.3+-1.0 W above 0.924 x model; aifoundry2 repeats its E15 values. | as T1 (equivalence for the non-DFT three). |
| ABL-T5 | horace-lowpower-143, horace-lowpower-163, horace-lowpower-166, horace-lowpower-180, horace-lowpower-138, horace-lowpower-145, energy-manual-53, energy-manual-54, energy-manual-56, energy-manual-57, ridge-83 | pJ/MAC over idle int8 0.32/0.29 (+-0.04), fp16 2.70/2.49 (+-0.2), fp32/int8 in [15, 23] on each card; EM4: aifoundry3/aifoundry2 = 0.92+-0.04 for fp16 and int8 zeros, ones, randn. | as T1; the EM4 ratio by 99% t on per-run values. |
| ABL-T6 | horace-lowpower-136, horace-lowpower-161, horace-lowpower-167, horace-lowpower-176, horace-lowpower-170, energy-manual-25, dvfs-58 | integer spin 1.46/1.35 W over idle (+-0.4/0.5), interval excluding 0. | as T1. |
| ABL-T7 | horace-lowpower-175, horace-lowpower-155, horace-lowpower-171, dvfs-69, energy-manual-29 | per-minion switching 1,024 vs 256 ratio in [0.98, 1.10]; line intercept <= +0.5 W. | as T1. |
| ABL-T8 | horace-lowpower-006, horace-lowpower-061, horace-lowpower-121, horace-lowpower-125, energy-manual-51, energy-manual-52, hub-010, hub-011 | ones - zeros +8.5/+7.8 (+-0.8), randn - zeros +25.2/+23.0 (+-1.0/1.5) W. | as T1. |
| ABL-R | horace-lowpower-040, horace-lowpower-041, horace-lowpower-043, horace-lowpower-056, horace-lowpower-199, horace-lowpower-030, horace-lowpower-090, energy-manual-V01 | v3 (reduction only, no new prediction of values): the four flip energies refitted on aifoundry3 from these runs (14+ patterns, leave-one-out rms reported per card); run-to-run half-differences per configuration; within-run drift slope per card; launch temperatures per card. | descriptive: the page states each card's own fit; a leave-one-out rms <= 0.6 W on aifoundry3 lets "predicts to 0.5 W rms" read "on both cards (0.50 / x W)". |
| ABL-EM4c | energy-manual-55 | cycles per op 546.00 (fp32, fp16) and 318.00 (int8) in every launch on both cards. | exact. |
| ABL-EM4d | horace-lowpower-128 | aifoundry2 80 C blocks within 2% of 21 Sep for every pattern. | Welch 99% of new - 21 Sep includes 0 (descriptive; consistency check only). |

Also informed by this experiment (no own prediction item; the item of the claim they depend on decides): energy-manual-05, energy-manual-157, ridge-84.

### V3-ABL-B (MUST): Sparse-compute energy configurations and TenB streaming, strict start (run_ablation.sh, 5 s runs)

Why: The sparse-compute KPIs "power saved 86%" and "board energy per layer" are aifoundry3, two runs of one session, without temperature correction; the matmul page's "the difference is the kernel" was never a controlled comparison.

Merges: matmul-sparse-testdrive:E2, matmul-sparse-testdrive:E3. Cards: both. Suggested experiment number when run: E39.

Build / sync first:
- sys_emu check first, no card: build/sparsity/host/sparsity_host --sysemu --test fma --type int8 --pattern none --values randn --b-stream --shires 0x1 --per-shire 1 --iters 10 (and --type fp16): results must be exact (--b-stream has only run on silicon with fp32).
- Config v3-energy.cfg (18 lines): the 12 run_energy.py CONFIGS (spin, fma-dense, fma-50, fma-875, fma-zero, fma-col50, fma-rowmask, gemv-dense-90, gemv-skip-0, gemv-skip-90, gemv-skip-99) + gemv-dense-0 + int8_ones_l1, int8_ones_tenb, int8_randn_l1, int8_randn_tenb, fp16_randn_l1, fp16_randn_tenb. Same patched runner as V3-ABL-A.

Repeats: 3 shuffled blocks per card; TenB - L1 is a within-block paired difference. Order: one invocation per card; a2 80/84 C, a3 55/57 C.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `a2: REPO=$PWD bash build/v3abl/run_ablation_v3.sh build/v3abl-b build/v3abl/v3-energy.cfg 3 5 80 84 build/sparsity/host/sparsity_host`
- `a3: the same under ~/nekko with targets 55 57`

Sampler: ettelem 10 Hz (runner). Drop a2 runs with mhz.minion != 600.

Card minutes: aifoundry2 59, aifoundry3 30.

Reduction: analyze_ablation.py (a2 --leak 0.81 --launch-temp 80.9; a3 --leak 0.55 --launch-temp 55.8) + scratch pooling: per-block paired differences, per-block least-squares line, per-layer energy from gemv iters/duration in runs.jsonl (analyze_ablation.py leaves gemv work empty).

Pre-registered predictions and decision rules (16 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| ABLB-2a | matmul-sparse-testdrive-29, matmul-sparse-testdrive-V09 | cycles/op at 1,024 minions: L1 fp16 546.0+-0.1, int8 318.0+-0.1; TenB fp16 529+-2; TenB int8 (A resident, never measured) 265-300, identical on the two cards within 0.5 cycle. | deterministic. |
| ABLB-2b | matmul-sparse-testdrive-13, matmul-sparse-testdrive-15 | above-idle power TenB - L1: int8 randn +4 to +10 W, int8 ones +3 to +8 W, each card. | per-block paired differences (n = 3), 99% t (df 2) excludes 0 with positive sign on both cards -> "streaming B through TenB costs X W" PROVEN-BOTH per card; "the difference is the kernel" kept only if in addition V3-MMB's mmbench int8 above-idle exceeds this session's int8_randn_l1 above-idle by > 10 W on each card (Welch, alpha 0.01); otherwise "probably the kernel". |
| ABLB-2c | matmul-sparse-testdrive-13 | int8_randn_l1 above idle: a2 9.5-10.5 W, a3 0.92 x a2 +-1 W. | 99% t per card. |
| ABLB-3ab | matmul-sparse-testdrive-50, horace-lowpower-004, horace-lowpower-132, hub-019 | fma-dense above idle a3 17.3+-2.0, a2 18.8+-2.5 W; fma-zero a3 2.4+-0.7, a2 2.6+-0.8; saving 1 - zero/dense 0.86+-0.04 on each card. | per-block values (n = 3), 99% t: saving interval inside 0.80-0.92 on both cards -> PROVEN-BOTH, watts per card. |
| ABLB-3c | matmul-sparse-testdrive-98, matmul-sparse-testdrive-101 | six-point line slope a3 14.8+-2, a2 16.1+-2.5 W; rms residual <= 0.6 W. | 99% t per card. |
| ABLB-3d | matmul-sparse-testdrive-57 | (dense - rowmask)/(dense - fma-50) in 0.9-1.4 on each card. | per-block ratio 99% interval inside 0.7-1.5 on both cards -> keep "cuts power like zeros do"; otherwise both cuts per card. |
| ABLB-3e | matmul-sparse-testdrive-73, matmul-sparse-testdrive-74 | layer energy above idle per layer a3 skip-0 70+-10, skip-90 19+-5, skip-99 7+-3 uJ; a2 = a3 x 1.08+-0.15. | stated per card; board energy including idle stated per card with its die temperature; no CARD-DIFFERENT drawn from it. |
| ABLB-3f | matmul-sparse-testdrive-75 | gemv-skip-0 - gemv-dense-90 +1.1+-0.6 W; gemv-dense-0 - gemv-dense-90 (same kernel, gating alone) +0.3 to +1.5 W. | a "gating alone" percentage kept only if gemv-dense-0 - gemv-dense-90 excludes 0 on both cards. |
| ABLB-3g | matmul-sparse-testdrive-99, matmul-sparse-testdrive-100 | spin a3 1.4-2.1 W, a2 1.3-1.7 W; fma-zero - spin +0.3 to +0.9 W on each card. | fma-zero - spin excludes 0 on both cards -> keep "about 0.5 W"; else "under 1 W, not separated from the spin baseline". |

### V3-X5 (MUST): Is the 0.92-0.95 card scale the card or its temperature? Two launch temperatures on each card

Why: Three pages attribute aifoundry3's lower switching power to the card; every comparison changed card and launch temperature together (81 vs 56 C).

Merges: horace-lowpower:horace-lowpower-X5, energy-manual:EXP-EM4 (temperature arm (ii), folded in). Cards: both. Suggested experiment number when run: E40.

Build / sync first:
- Same patched runner as V3-ABL-A; x5.cfg = fp32_zeros, fp32_ones, fp32_uniform (--values uniform), fp32_randn, fp16_randn (the EM4 temperature-arm pattern). EM4's own 74/88 C arm is dropped: it asks the same question with a weaker design.

Repeats: 3 hot + 3 cool one-block invocations per card, alternating hot, cool (unit = run; SEED_OFFSET = block index so tiles differ). Order: per card: hi0, lo0, hi1, lo1, hi2, lo2; aifoundry2 hot 83/86 C, cool 76/79 C; aifoundry3 hot 65/68 C, cool 55/60 C.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `for b in 0 1 2; do SEED_OFFSET=$b REPO=$PWD bash build/v3abl/run_ablation_v3.sh build/v3x5/hi$b build/v3abl/x5.cfg 1 7 83 86 build/sparsity/host/sparsity_host; SEED_OFFSET=$b ... build/v3x5/lo$b ... 1 7 76 79 ...; done (a3: 65 68 / 55 60).`

Sampler: ettelem 10 Hz per invocation; drop runs with any mhz.minion != 600 (a2 cool target stays >= 76 C, above the governor's window).

Card minutes: aifoundry2 38, aifoundry3 30.

Reduction: analyze_ablation.py per directory (--leak 0.81 / 0.55, --launch-temp target + 0.9), then the V3-ABL-A dropout rule.

Pre-registered predictions and decision rules (9 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| X5 | horace-lowpower-013, horace-lowpower-099, horace-lowpower-119, horace-lowpower-120, horace-lowpower-123, horace-lowpower-125, horace-lowpower-198, energy-manual-157, energy-manual-05 | card hypothesis: switching power at the two launch temperatures on each card differs by < 0.5 W for uniform and randn; temperature alternative (0.3 %/C): aifoundry3 65 C reads ~+0.7 W over 55 C, aifoundry2 83 C ~+0.5 W over 76 C. v3: fp16_randn added (the EM4 temperature arm), reported with the same test. | per card and pattern (uniform, randn): Welch 99.75% interval of hot - cool (Bonferroni over 4 tests). "Card property" if all four intervals lie inside +-0.5 W; "temperature effect" if the aifoundry3 intervals exclude 0 with positive sign and point estimates >= +0.4 W; otherwise "not separated" and the pages say "the card or its temperature". |

### V3-TEL (MUST): The meter chain: SP pass interval by sampler, --reset-ms windows, peak-hold, per-shire voltage maps, governor readouts

Why: "133 ms" is quoted on 15 pages but is one aifoundry2 session without a sampler; ettelem sees ~150 ms (a2) and ~255 ms (a3). The spatial brief's KPIs (voltage map, "high 3 C above the mean") are one capture / one window per card; --reset-ms has never been used in a run.

Merges: hub:E-hub-1, pt-spatial:X4, pt-spatial:X2, pt-spatial:X3, dvfs:EXP-dvfs-2. Cards: both. Suggested experiment number when run: E41.

Build / sync first:
- etcfg is a source file: gcc -O2 -I/opt/et/include -o <scratch>/etcfg tools/etcfg/etcfg.c on each host (no card).
- Confirm on both hosts that build/ettelem/ettelem is the 24 Sep build that lists --reset-ms and sptrace/loglevel in its usage; if not, rsync tools/ettelem and rebuild with nice -j4. Confirm dev_mngt_service accepts DM_CMD_GET_MODULE_VOLTAGE (strings/usage only); drop the VOLT arm if not.
- New pass driver run_tel_v3.sh (~100 lines, scratch, both hosts), see new_code N2.

Repeats: 3 per card, >= 30 min apart, arm order shuffled per pass (python3 -c 'import random; r=random.Random(K); ...', logged). Order: per pass: (1) governor readouts (no sampler, INFO log level): sptrace sp0.bin; etcfg > driver.json; 5 x timeout 10 sparsity_host --test fma --type fp32 --pattern none --values zeros --shires 0xffffffff --per-shire 32 --seconds 2 --budget 5 --seed 1, 3 s apart; sptrace sp1.bin; ettelem config > config.json; dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS; (2) [a2: heat to >= 76 C] SPST extract, 60 s quiet, then the arms Q, PWR (scripts/et-power-log.sh, one command per ~16 ms), L10 (one DM_CMD_GET_MODULE_POWER per 0.1 s, bounded 450-iteration loop), E10 (ettelem 100 ms, 60 s), E20 (ettelem 50 ms, 60 s), E40 (ettelem 25 ms, 30 s), VOLT (DM_CMD_GET_MODULE_VOLTAGE loop) in a shuffled order with 30 s quiet after each, SPST extract; (3) [a2 reheat] reset segment: ettelem sample --seconds 45 --every-ms 100 --reset-ms 1000 while three 3 s enercat fmadd_ps random bursts run 10 s apart; SPST extract; (4) DEBUG block: ettelem loglevel debug (EXIT trap restores info); idle sptrace; 3 load windows: ettelem sample --seconds 14 --every-ms 100 --reset-ms 600000 with a 7 s sparsity randn burst 3 s in, sptrace at the end of each window; 1 idle window; loglevel info.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `See components for the exact command lines (E-hub-1, X4, X2, X3, dvfs-2); the driver runs them in the order above. Every device launch is a 2 s zeros, 3 s enercat or 7 s randn process under timeout 10; samplers hold only the management node; stop them with SIGTERM, never kill -9; on a failed start drain once with dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000.`

Sampler: as the arms; aifoundry2 bursts with mhz.minion != 600 dropped from the reset tests

Etiquette: The SPST reset and --reset-ms change shared min/max that anyone watching et-powertop sees: check for other users first. The management node is single-opener: no other ettelem or dev_mngt_service during a pass.

Card minutes: aifoundry2 60, aifoundry3 48.

Reduction: workloads/memprobe/analyze_power.py read_trace() for the SPST .bin.done files; validate3/pt-spatial-verify/v13_refresh.py (ettelem arms) and v13b_powercsv.py (PWR, L10) per arm; the sptrace regex of validate3/dvfs-verify; validate3/inv/pt-spatial-work/x2_reduce.py and x3_reduce.py.

Pre-registered predictions and decision rules (53 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| TEL-P1 | hub-034, hub-127, hub-003, hub-069, hub-117 | aifoundry2: SP stats trace pass interval, median over each quiet segment, 131.6-135.6 ms in every pass. | 3/3 passes in band. |
| TEL-P2 | hub-034 | aifoundry2: during PWR (et-power-log single-command poll) the median pass is within +-1.5 ms of the same pass's quiet median. | /PWR - Q/ <= 1.5 ms in 3/3. |
| TEL-P3 | hub-034, hub-127, pt-spatial-01 | aifoundry2: during E10 the median pass is >= 145 ms in every pass and E10 - quiet > 8 ms; E40 >= E10. | 3/3 passes E10 >= 145 ms and the 99% one-sided t bound (df 2) on paired E10 - Q > 0. |
| TEL-P4 | hub-034 | aifoundry2 mechanism (two-sided): VOLT - quiet >= 5 ms if DM_CMD_GET_MODULE_VOLTAGE lengthens the pass; within +-1.5 ms if not. | 99% t (df 2) on VOLT - Q: > 5 ms confirmed; inside +-1.5 rejected; else not resolved. |
| TEL-P5 | hub-070, dvfs-19 | aifoundry3: median pass 255-272 ms during E10 and >= 230 ms when quiet ("the SP loop is slow"); quiet < 160 ms would make it sampler-induced. | 3/3 passes in the bands -> "the SP loop is slow"; quiet < 160 in 3/3 -> sampler-induced; else reported as is. |
| TEL-P6 | hub-037 | first use of --reset-ms: since_reset_ms cycles 0-1000; every 1 s window >= 8 s after the last burst has sp.minion_w max - min <= 1.0 W; the window holding each burst's first second has max >= idle + 50% of the burst's minion-rail step; with no reset (E10) the max never falls. | exact, 0 failures allowed; else rung 6 reads "untested / not working". |
| TEL-P7 | hub-036 | resets leave the running average alone: median f(1 s) over the 9 bursts per card 0.45-0.68 (a restart would give >= 0.9). | median of 9 bursts per card inside the band. |
| TEL-S | pt-spatial-01, pt-spatial-13, pt-spatial-15, pt-spatial-16, dvfs-73, anatomy-08, anatomy-110, energy-manual-159, heat-15, horace-lowpower-129, matmul-sparse-testdrive-32, matmul-sparse-testdrive-96, memhier-onchip-110 | board refresh period seen by each poller: S1 a2 P_L (0.1 s single-command poll) 131-140 ms, P_H (ettelem 10 Hz) 152-160 ms, P_H2 (20 Hz) >= P_H + 10 ms; S2 a3 P_L 200-245 ms, P_H 258-268 ms, P_H2 >= P_H + 10; S3 P_H - P_L > 0 on both cards. | paired over 3 passes: P_H - P_L 99% t (df 2) excludes 0 with the same sign on both cards -> "the sampler lengthens the pass" PROVEN-BOTH and every page gives the period per card and per sampler; if it includes 0 on a card with /mean/ < 5 ms, pages give only the ettelem figures (~156 / ~263 ms). |
| TEL-Q | pt-spatial-10, pt-spatial-12, pt-spatial-46, pt-spatial-47, pt-spatial-48, pt-spatial-49, pt-spatial-50, pt-spatial-71, hub-V04, hub-012, hub-025, pt-spatial-61 | Q1 on aifoundry3 the DEBUG ring holds 34 "MS nn Voltage" lines and parses; 0 "Temp [C]" lines on both; "MEM n Voltage" lines only right after a sample. Q2 the idle pattern of the 34 minion readings repeats across passes: Pearson r >= 0.6 for every pass pair on each card. Q3 the two cards' idle patterns uncorrelated /r/ < 0.45 if they are per-monitor offsets. Q4 under load the common level falls 1-3 mV and each shire's deviation changes by <= 1 mV (sd <= 0.5 mV). Q5 minion "now" shows no plane (permutation p >= 0.0042) in every idle capture; the SRAM "now" gradient reappears on aifoundry2 (p < 0.0042) in >= 2 of 3 passes. | Q2 all 3 pass pairs per card; Q3 r >= 0.45 (one-sided p < 0.01) rejects per-chip offsets; Q4 99% upper bound of the pass-level sd <= 0.5 mV; failure of Q2 or Q4 drops the offset sentence (pt-spatial-49). |
| TEL-R | pt-spatial-51, pt-spatial-59, pt-spatial-65, pt-spatial-67, pt-spatial-68, pt-spatial-69, pt-spatial-70, hub-022 | R1 the reset resets the peak-hold within 1 s (low >= mean - 2, high <= mean + 3) on both cards; R2 at the end of every load window high - SP max in {2, 3, 4}, median 3; R3 at each rise high - mean is 3 or 4 in >= 80% of rises; R4 idle windows high - SP max <= 2; R5 low - SP min is -1 or -2 in every window; R6 after a 7 s burst >= 17 of 34 per-shire lows sit >= 2 mV below idle while the 10 Hz die_mv.minion mean fell <= 2.5 mV. | unit = pass (3 load windows are sub-samples). R1 gates everything (fails -> claims stay UNDER-REPLICATED); R2 holds if every load window in {2,3,4} and each pass median is 3 (equal but not 3 -> own figure; disagreeing pass medians -> WITHIN-NOISE); R6 decides "the lows catch droops the polling misses": >= 2 of 3 passes per card, else the clause is dropped. |
| TEL-G | dvfs-07, dvfs-40, dvfs-41, dvfs-42, dvfs-43, dvfs-44, dvfs-46, dvfs-51, dvfs-75 | aifoundry3 every pass: config tdp_w 0, temp_threshold_c 65, max_power; sp1.bin (read after 5 launches, before any config query) holds >= 5 "Power throttle down event, current pwr N  tdp level: 0" and >= 5 "Power idle state event, current pwr N  tdp level 0", at most one repeated idle event, 0 throttle-up; every launch 0.59-0.61 GHz. aifoundry2 (die >= 68 C): 65 / 65 / managed_power; any idle-state line in the pre-60b40c10f format (a 353f20e-format line refutes "both cards run the older governor"). Both: driver tdp_w 65, boot 600 MHz, cm_shire_mask 0xffffffff, l3_kb 32768; same firmware and PMIC revisions (1.3.1 / 1.5.0). | deterministic, 3 of 3 passes per card; no governor line on aifoundry2 in any pass -> dvfs-75 stays one card. |

Also informed by this experiment (no own prediction item; the item of the claim they depend on decides): hub-041, pt-spatial-V03.

### V3-WIRE (SHOULD): Heat per millimetre, third run: board-power split, four-hop step, link-disjoint linearity; plus the byte-for-byte fill check

Why: The page's mesh-rail results are PROVEN-BOTH already; the board-power split into data and fixed parts, the d=4 step on board power and the link-disjoint contrast are within noise at 3 passes.

Merges: heat:EXP-heat-1, heat:EXP-heat-2. Cards: both. Suggested experiment number when run: E42.

Build / sync first:
- None on aifoundry3 (enercat v2 built); pre-flight: ls ~/nekko/workloads/enercat/run_wire.py ~/nekko/build/enercat_v2/host/enercat_host ~/nekko/build/ettelem/ettelem; re-sync with scripts/deploy-lab.sh if run_wire.py lacks --set v2 or the sampler retry.

Repeats: 6 per card (28 configurations each, shuffled per pass, seed 31+p on a2 and 41+p on a3). Order: one runner invocation per card, both cards at the same time; the 12 dump-slice launches (heat-2) before the first pass.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `a2: setsid nohup python3 workloads/enercat/run_wire.py docs/reports/data/2026-09-2X-wire3-aifoundry2 --set v2 --host-bin build/enercat_v2/host/enercat_host --passes 6 --seed 31 --warm-c 69 --only wu/p0/,wu/p0.5/,wu/p1/,wsep/p0/,wsep/p0.5/ < /dev/null > wire3-a2-driver.log 2>&1 &   (the runner unmodified: its host --budget 9.5 s caps every hold; timeout 12 is only a kill switch)`
- `a3: the same under ~/nekko with --seed 41 into wire3-aifoundry3, then scp back.`
- `heat-2: for OP in 'tstore_raw bern:0.25' 'tstore_raw alt:64' 'tstore_raw frz' 'tstore_uniq uq:0.25'; do for r in 1 2 3; do timeout 10 build/enercat_v2/host/enercat_host --pattern $1 --operands $2 --slice-bytes 32K --seconds 0.3 --window 60000000 --dump-slice 1024 > dump_${2//:/_}_$r.txt; done; done`

Sampler: runner-managed ettelem 10 Hz; bursts with sampler median > 60 ms or any sample off 600 MHz dropped by analyze_wire.bursts()

Card minutes: aifoundry2 45, aifoundry3 38.

Reduction: python3 validate3/heat-verify/exp_test_v3.py <a2 dir> <a3 dir> (P1-P16); the no-leakage-correction reduction is printed as descriptive only and decides nothing.

Pre-registered predictions and decision rules (16 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| WIRE-P1-16 | heat-01, heat-02, heat-05b, heat-06, heat-19, heat-21a, heat-21b, heat-22, heat-23, heat-32, heat-42, heat-43, heat-48, heat-75, heat-V04 | per card, 6 passes, 99% t (df 5): P1 mesh contention data part 16..40 fJ/bit/hop; P2 fixed 23..43; P3 board free-link data 75..165; P4 board free-link fixed 22..82; P5a/b board contention split 24..104 and 16..86; P6 all-ones over random per hop mesh 4.5..12.5%, board 2..12%; P7a-d d=4 above the 1,2,3,6 line mesh random 3..9%, zeros 3.5..9.5%, ones 11..19%, board ones 7..17%; P7e/f board random 1.5..7.5%, zeros -0.5..5.5%; P8/P9 exit step mesh 0.35..0.75 hop, board 0.7..1.5; P10 d=0 data part within +-4% of d=1; P11 free-link totals 33..39.5 (mesh), 35..58 (board) fJ/mm; P12 one-hop all-ones saving 31..41%; P13 board per-second bound descriptive; P14a/b link-disjoint d=4 off the 1,2,3,5 line inside +-3% (random), +-4% (zeros); P15a/b [wu d4-off] - [wsep d4-off] mesh random +1.5..+9%, zeros +2..+10%; P16 one-hop data part wu/wsep - 1 inside +-5%. | PASS when the per-card interval excludes the null on both cards and both means are inside the range; SIGN-ONLY when the null is excluded but a mean is outside (page states new per-card values); FAIL otherwise (dropped or qualified); equivalence items (P10, P14, P16) pass only if the whole interval lies inside the range on each card. The no-leakage reduction is descriptive only. |
| WIRE-FILL | heat-V01 | every DUMP word equals its EXPECT word in all 12 launches on each card. | deterministic; any mismatch drops "checked byte for byte"; even on PASS the page says the check is of the store kernel on a DRAM slice. |

### V3-RL (SHOULD): Rings, levels and relay energy with spin brackets and controlled scratchpad contents (6 passes per card)

Why: Level energies (L1, L2, own scratchpad) and the per-hop slope differ between cards; whether scratchpad contents cause the difference is untested; "rings draw less than spinning" and small-message costs are within noise.

Merges: energy-manual:EXP-EM3, memhier-onchip:memhier-onchip-X3, ridge:ridge-X4 (reduction only). Cards: both. Suggested experiment number when run: E43.

Build / sync first:
- New runner tools/ettelem/run_rl_spin_v3.sh placed next to the original on both hosts (it cds relative to its own path; chmod +x after copying to aifoundry3): a copy of run_rings_levels_power.sh with timeout 10 and --budget 8 on every launch, spin brackets (nocbench spin first/last in half A, memhier spin first/last in half B), ABBA order for l2/scp-local, and a contents prefill before scp-local and scp-remote (odd passes: timeout 10 build/enercat/host/enercat_host --pattern tstore --operands zeros --slice-bytes 64K --scp --seconds 0.3 --window 60000000; even passes --operands random). First confirm in memhier's kernel that the scp-local buffer starts at the enercat slice base.
- tools/ettelem/run_onchip_power10.sh next to the original: timeout 40 -> timeout 10.

Repeats: 6 per card; rl then relay in each pass; ring order reversed and ABBA -> BAAB on even passes. Order: a2 and a3 in parallel; >= 30 min between passes; a2 heated to >= 76 C before each half and before the relay.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `a2 (local): heat; tools/ettelem/run_rl_spin_v3.sh build/v3rl/a2-p$K A; heat; ... B; heat; tools/ettelem/run_onchip_power10.sh build/v3rl/a2-p$K/relay 8`
- `a3: ssh aifoundry3 'cd ~/nekko && tools/ettelem/run_rl_spin_v3.sh build/v3rl/a3-p$K A && ... B && tools/ettelem/run_onchip_power10.sh build/v3rl/a3-p$K/relay 8'`

Sampler: the runners' ettelem 10 Hz with start retry; bursts with sampler median > 60 ms (xshire16 on a2) or clock off 600 MHz (> 2% of samples) dropped

Card minutes: aifoundry2 72, aifoundry3 43.

Reduction: analyze_reruns.py <new dirs> --no-first --out <scratch>/reruns3.json (new passes only), validate3/inv/energy-manual-work/reruns_perpass.py and rings_relay_extra.py, a copy of analyze_reruns.reduce_dir per pass for the spin/ring differences; then validate3/inv/ridge-work/e_energy.py on a scratch manual.json rebuilt with these passes and V3-ABL-A's FLOP side.

Pre-registered predictions and decision rules (30 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| RL-a | energy-manual-127, memhier-onchip-112, memhier-onchip-84 | mesh slope over the five 1 KB cross-shire rings a2 2.3+-0.5, a3 1.3+-0.5 pJ/B per hop. | Welch 99% of the per-pass slope difference excludes 0 (6 new passes per card) -> CARD-DIFFERENT stands with per-card slopes; else pooled with +-50%. |
| RL-b | energy-manual-128 | aifoundry2 "leaving the shire" step (intercept - shire ring - one hop) +3.3+-2 pJ/B. | 99% t excludes 0 on that card. |
| RL-c | energy-manual-129, memhier-onchip-83 | aifoundry3: shire-c4 - shire = +1.0 and xshire1-c4 - xshire1 = +3.6 pJ/B. | 99% t excludes 0 (6 passes) on aifoundry3 -> "small messages cost more" on both cards. |
| RL-d | energy-manual-121, energy-manual-122, energy-manual-131, energy-manual-152, energy-manual-171 | relay DRAM/next-shire ratio a2 11.2+-0.6, a3 13.5+-0.8; relay DRAM a3/a2 1.07+-0.03. | Welch 99% on log ratios. |
| RL-f | energy-manual-153 | relay own scratchpad 3.95-4.05 against a bracket low edge of 4.30-4.40. | Welch 99% of measured - low edge excludes 0 on each card -> "8% below its bracket"; else "at the low edge". |
| RL-g | energy-manual-83, energy-manual-84, energy-manual-87, energy-manual-90, memhier-onchip-34, ridge-94, ridge-96, memhier-onchip-16, hotline-relay-l2-73 | L1 level a2 - a3 = +0.18+-0.06 pJ/B; own-scratchpad level a3 - a2 = +0.23+-0.06; L2 - scratchpad a2 +0.18+-0.15, a3 -0.28+-0.15. | as RL-a; both L2 - scratchpad intervals containing 0 -> "the same within +-10%". |
| RL-h | energy-manual-87, memhier-onchip-34 | contents arm: each card's scp-local level follows the prefill (zeros 2.0+-0.3, random 4.2+-0.5 pJ/B) and at equal contents a3 - a2 is within +-0.1 pJ/B. | as RL-a on the prefilled passes; a3 - a2 inside +-0.1 -> the card difference is contents, and the page says so. |
| RL-X3 | memhier-onchip-88, memhier-onchip-50, memhier-onchip-51, memhier-onchip-52, memhier-onchip-89, memhier-onchip-90, memhier-onchip-93 | (a) nocbench spin - ring over idle per pass: pair +0.0..+0.5 W; neigh and shire within +-0.4 W; xshire2/4/6 >= +0.4 W on both cards; (d) memhier two-hart spin 2.3-2.8 W, nocbench one-hart spin 2.2-2.6 W; (e) inside-shire ring power above mesh-ring power and scp-remote cheaper than s->s+8 and s->s+16 in every pass. | (a) "less than spinning" kept for a ring only if its interval is > 0 on both cards, else "about as much as spinning (+-x W)"; (d), (e) every pass on both cards -> PROVEN-BOTH. |
| RL-X4 | ridge-88, ridge-91 | L3 random vs spec 3.0 -> 3.6+-0.5 (above); other shire random -> 2.3+-0.6 (below); zeros in-shire TensorSend vs 8.8 -> 10.0+-1.5 (above). | byte side 99% t over all passes per card (23 Sep + V3-RL), FLOP side over V3-ABL-A blocks; balance interval [byte lo / FLOP hi, byte hi / FLOP lo]; a verdict only when both cards' intervals lie on the same side of the ridge, else "ranges overlap: no verdict". ridge-89, ridge-92 and the pairs half of ridge-91 are not tested (margins need 11 to > 100 passes). |

### V3-IDLE (SHOULD): Idle heat/cool cycles: the idle law's shape on aifoundry3, the unsensed slope, the leakage split

Why: The idle law (12.6 W + 23.3 W e^((T-80)/36)) is fitted on aifoundry2 only; its leakage split is not identified (T_L flat over 30-45 C); aifoundry3's shape and SRAM rail are single-bin readings.

Merges: energy-manual:EXP-EM1, dvfs:EXP-dvfs-4, horace-lowpower:horace-lowpower-X4 (long variant). Cards: both. Suggested experiment number when run: E44.

Build / sync first:
- Scratch runner idle_cycles.sh (~30 lines, both hosts): ettelem sample --seconds 5400 --every-ms 100 with start_sampler retry; per cycle skip if lsmod et_soc1 use count != 1 (only our sampler), heat() with timeout 10 sparsity_t2 (a2) / sparsity (a3) 2 s randn bursts until minshire >= target (a2 88 C; a3 plateau, log it), mark, then 900 s with no launch.

Repeats: 3 heat/cool cycles per card (short: 15 min of cooling each); IDLE-LONG variant: extend each cycle's cooling to 90 min (a2) / 45 min (a3), overnight only, when the room is cool. Order: both cards in parallel; cycles on at least two different days; IDLE-LONG only on nights when aifoundry2 is expected to reach < 64 C.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `setsid nohup ./idle_cycles.sh DATA/2026-09-2x-idlecycles-<host> <target> 3 900 < /dev/null > log 2>&1 & (IDLE-LONG: ... 3 5400 on a2, 3 2700 on a3)`

Sampler: ettelem 10 Hz (board, rails, minshire, die_mv, mhz); samples from 1 s before to 6 s after any launch excluded; a2 samples with mhz.minion != 600 dropped

Card minutes: aifoundry2 66, aifoundry3 80; IDLE-LONG adds 225 / 90 overnight.

Reduction: whole-degree bins (n >= 20); fit P = c + A e^((T-80)/T_L) on the flip_thermal_model grid per cycle (scratch copy of flip_thermal_model.py step 2a / ftm_copy.py); residual to the published law; unsensed = board - rails; 99% t over cycles.

Pre-registered predictions and decision rules (34 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| IDLE-0 | energy-manual-22 | feasibility: aifoundry3's plateau under the continuous heater Tmax = 60-66 C. | logged; sets the aifoundry3 range for (a), (e). |
| IDLE-a | energy-manual-145, energy-manual-01, dvfs-63, energy-manual-16, horace-lowpower-124 | aifoundry3 idle - aifoundry2 law = +0.61 W (tolerance +0.3 to +0.9) in every whole-degree bin 51 C..Tmax, residual slope within +-0.03 W/C. | 99% t over 3 cycles: offset interval inside [0.3, 0.9] and slope interval inside [-0.05, +0.05] -> "the law with +0.6 W describes aifoundry3 at 51-Tmax C"; the shape above Tmax stays one card. |
| IDLE-b | energy-manual-06, energy-manual-15, dvfs-61 | aifoundry2 idle - law = -0.23+-0.3 W in every bin it visits (~70-88 C). | 99% t over 3 cycles. |
| IDLE-c | energy-manual-11, energy-manual-12, energy-manual-13, energy-manual-163 | aifoundry2 unsensed idle slope over 74-88 C = 0.055 W/C, 99% upper bound < 0.15; metered-rail slope 0.51+-0.07 W/C at 75-80 C. | (c) holds if the unsensed slope's upper bound < 0.15 W/C. |
| IDLE-d | energy-manual-18, dvfs-62, hub-080 | aifoundry2's 73 C split within 0.2 W of 22 Sep (11.05 / 2.00 / 3.64 / 15.10 W). | 99% t over cycles with a 73 C bin. |
| IDLE-e | energy-manual-19, energy-manual-20, energy-manual-22 | aifoundry3 SRAM rail slope over 51-Tmax = 0.047+-0.03 W/C and >= 0.8 W above the aifoundry2 SRAM law in every bin. | 99% t over 3 cycles. |
| IDLE-f | energy-manual-163 | only if Tmax >= 70 C: aifoundry3 unsensed at 70 C 12.9-13.9 W against aifoundry2's 14.7; else values stay per card at each card's temperature. | conditional. |
| IDLE-k | dvfs-05, dvfs-06, energy-manual-147, energy-manual-149 | aifoundry2 cooling from >= 86 C (samples >= 20 s after the last burst): profile-best T_L 30-48 C, busy share A80/63.9 W of 0.31-0.47 over the T_L range within 0.005 W rms of the best; law residual over 70-85 C -0.2+-0.2 W. | "busy leakage above Kanter's 30%" established only if in 3 of 3 passes the lower end of the profile range gives a busy share > 0.30; otherwise the page states the range. |
| IDLE-L | energy-manual-10, horace-lowpower-084, horace-lowpower-087, horace-lowpower-088, horace-lowpower-139, horace-lowpower-158, horace-lowpower-142, anatomy-115, hub-009, dvfs-59, pt-spatial-05, horace-lowpower-187 | IDLE-LONG (90 min cooling on a2, 45 on a3): best T_L in [30, 45] C, A80 in [19, 29] W, slope at 80 C 0.65+-0.03 W/C (a2); a3 slope at 56 C 0.30+-0.08 W/C, offset +0.7+-0.4 W. | one-sample t over 3 passes, 99%; the leakage split is "identified" only if the CI of A80 is narrower than +-3 W. Expected outcome: not identified -> pages give 20-29 W and quote the slope. |

### V3-CAT (SHOULD): Energy catalogue: a within-card temperature panel and the DRAM-row rows on aifoundry3

Why: Whether the catalogue's 5% card gap is temperature; the DRAM row-pattern rows (dramrow2) exist on aifoundry2 only; the fence/nop and stride-256 rankings are within noise.

Merges: energy-manual:EXP-EM2. Cards: both. Suggested experiment number when run: E45.

Build / sync first:
- run_catalogue_t10.py (scratch copy of workloads/enercat/run_catalogue.py): timeout 12 -> 10 in both subprocess calls; --host-bin (default build/enercat_v2/host/enercat_host; confirm --jump-every/--jump-bytes in its argument parser on aifoundry3); --hold-hot C (up to 5 heater launches before a configuration's gap until minshire >= C). Pin ROOT to the checkout if the copy is not placed next to the original.

Repeats: arm A: a2 8 passes (W H W H W H W H: warm 74-82 C / hold 88 C), a3 6 passes (C H C H C H: cool / hold Tmax-1 from V3-IDLE); arm B: 6 passes on a3, 3 on a2 (preheated to 76 C), interleaved with arm A. Order: per card alternate A and B; other-user check before every pass.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `arm A: python3 run_catalogue_t10.py <out> --only <the 30-configuration panel of EXP-EM2> --passes 1 --burst 3 --gap 4.5 --seed 20<k> [--hold-hot 88 | Tmax-1]; arm B: --only dramrow2,tload/dram,tstore/dram,l1fill/stride32,l1fill/stride64,tload/scp,fence,nop --passes 1`

Sampler: run_catalogue.py's own ettelem 10 Hz; a2 bursts with mhz_busy_all_600 false dropped

Card minutes: aifoundry2 81, aifoundry3 78.

Reduction: workloads/enercat/analyze_catalogue.py on scratch copies (--out only), then per-pass tests on the NEW passes only (the 23 Sep passes are printed beside, never pooled into the test).

Pre-registered predictions and decision rules (14 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| CAT-a | energy-manual-05, energy-manual-09, energy-manual-46, energy-manual-154, energy-manual-157, hub-122 | card hypothesis: per-pass median over the 30-configuration panel of log(value / config mean), hot - warm = 0+-0.5%; temperature alternative +0.21 %/C x dT. | beta = (hot - warm)/dT per card, Welch 99% on pass values (a2 4 v 4, a3 3 v 3): excludes 0.21 %/C -> "the scale is the card"; excludes 0 and includes 0.21 -> temperature explains it; else not established. |
| CAT-b | energy-manual-05 | cool aifoundry3 / warm aifoundry2 = 0.951+-0.015 (pass level). | Welch 99% on pass-level medians. |
| CAT-c | energy-manual-103, energy-manual-104, energy-manual-105, energy-manual-108 | dramrow2 on aifoundry3: seq, rowhit, rowmiss within +-15 pJ/B of each other and 13-26% above aifoundry3's own tload/dram on each operand set. | one-way ANOVA p > 0.01 over the three patterns (6 passes) AND Welch 99% of rows - tload excludes 0 -> PROVEN-BOTH with the aifoundry2 block. |
| CAT-e | energy-manual-75 | tstore/dram - tload/dram, random, aifoundry3: +3.2+-3 pJ/B. | Welch 99% per card. |
| CAT-f | energy-manual-100, energy-manual-102 | L1 fill per byte / tensor load per byte, random: 0.75+-0.10 on each card. Stated in advance as underpowered: fence vs nop (energy-manual-44) and stride-256 energy (energy-manual-102) are expected to stay within noise. | Welch 99% per card. |

Also informed by this experiment (no own prediction item; the item of the claim they depend on decides): energy-manual-44.

### V3-COOL (SHOULD): aifoundry2 only, from a cool die: governor timing, clock-change correctness, V/f, the Horace speed effect, clock-split latency and bandwidth elasticities

Priority note: calendar-limited (cool mornings); the Horace speed-effect part is owner decision D2.

Why: All clock-dependent claims (governor behaviour, 800 MHz latencies and bandwidths, V^2 f, the 25% speed effect, the relay's wrong elements under a clock drop) come from one or two cool mornings.

Merges: dvfs:EXP-dvfs-3, horace-lowpower:horace-lowpower-X2, hotline-relay-l2:E-HL2, hotline-relay-l2:E-RL2, memhier-onchip:memhier-onchip-X4, ridge:ridge-X2. Cards: a2 only (aifoundry3's firmware pins 600 MHz: every claim here stays one card whatever the outcome). Suggested experiment number when run: E46.

Build / sync first:
- Patched copies next to the originals (they cd relative to their own path): run_vf_cold10.sh (timeout 12 -> 10), run_horace_cold_v3.sh (others() wait of run_vf_cold.sh before each run), run_hotline_power10.sh (timeout 20 -> 10), run_onchip_power10.sh (timeout 40 -> 10).
- New wrappers (no device code): run_cool_v3.sh (waits with the card closed, polling ettelem sample --seconds 1 every 5 min until minshire <= 63 C and no other user; then runs the light block), run_clock_chase_v3.sh (memhier-onchip X4), run_rl_clock_v3.sh (ridge X2).

Repeats: >= 3 cool mornings for the light block (unit = cool period) + >= 3 separate cool mornings for the full-chip speed-effect sequence; horace X2 V/f one cycle per morning. Order: light block on a cool morning: ridge-X2 cool phase (8 configs, 2 s launches) -> memhier X4 chases with heater nudges walking 800 -> 700 -> 600 MHz -> E-HL2 cool hot-line block + E-RL2 20 DRAM --stages 640 + 10 hop relay launches -> dvfs-3 relay (run_onchip_power10.sh 8) and governor (run_governor.sh ... 64 600 4 zeros ones randn) -> run_vf_cold10.sh one cycle -> heater to 76 C -> ridge-X2 hot phase. Speed-effect mornings: run_horace_cold_v3.sh build/v3cold_n<N> 63 300 zeros randn ones only; the steady-600 warm controls of E-HL2 and E-RL2 run inside V3-LAT passes (their minutes are counted here).

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `wait: bash run_cool_v3.sh (polls timeout 10 build/ettelem/ettelem sample --seconds 1 --every-ms 500 every 5 min with the card otherwise closed until minshire <= 63 C and the et_soc1 use count is 0, then runs the light block below)`
- ridge-X2 cool phase (and hot phase after the heater): build/ettelem/ettelem sample --seconds 300 --every-ms 100 running; per config in a per-cycle shuffled order: timeout 10 build/memhier/host/memhier_host --budget 8 --test stream --where dram --bytes-per-minion 8K|24K|256K --seconds 2 (l2, l3, dram), ... --where scp-local --bytes-per-minion 64K, ... --where scp-remote --bytes-per-minion 64K --scp-shift 16, and timeout 10 build/nocbench/host/nocbench_host --budget 8 --test shift --rings pair|shire|xshire:2 --count 32 --seconds 2; 4 s gaps
- memhier X4: tools/ettelem/run_clock_chase_v3.sh <out>: ettelem sample --every-ms 100 in the background; alternate timeout 10 build/memhier/host/memhier_host --budget 8 --test chase --where scp --scp-shire all --sizes 64K --chaser-shire {0,31} and ... --test chase --chaser-shire {0,24} --sizes 4M,256M for ~4 min, with a 2 s heater launch (timeout 10 build/sparsity_t2/host/sparsity_host --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1) whenever one clock has held > 40 s
- `E-HL2 cool block: tools/ettelem/run_hotline_power10.sh $DATA/hl2-s$S-cool (copy of run_hotline_power.sh with timeout 20 -> 10, placed next to it; DATA absolute); E-RL2 inside it: 20 x timeout 10 build/onchip/host/onchip_host --test relay --medium dram --stage-bytes 1M --stages 640 --work 1, then 10 x --medium hop --stages 7800 (labelled and appended as in E-RL1)`
- `dvfs-3: tools/ettelem/run_onchip_power10.sh OUT/relay-passN 8; tools/ettelem/run_governor.sh OUT/gov-passN 64 600 4 zeros ones randn (4 s runs: the runner passes --budget 10 to the host)`
- `horace X2 V/f: tools/ettelem/run_vf_cold10.sh build/v3vf_n<N> 63 14 1 build/sparsity/host/sparsity_host (one cycle per morning); speed-effect mornings: tools/ettelem/run_horace_cold_v3.sh build/v3cold_n<N> 63 300 zeros randn ones`

Sampler: ettelem 10 Hz (25 ms in run_governor.sh); a launch counts at a clock only if every sample inside it shows the same mhz.minion

Feasibility: aifoundry2 rested at 73-74 C on 22-24 Sep and reached <= 64 C only on the 21 Sep morning and at 19:51 UTC on 23 Sep. If no cool period comes within a week, stop and label every claim here "one card, one morning, n runs" (or drop it where its only support is one run).

Card minutes: aifoundry2 89, aifoundry3 0.

Reduction: validate3/dvfs-verify relay.py, trans.py, postblock.py, bootreset.py; build_vf.py --cold; analyze_horace_cold.py; chases.py with the telemetry clock; c_elasticity.py adapted; Fisher exact tests for E-HL2 / E-RL2 pooled over sessions.

Pre-registered predictions and decision rules (40 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| COOL-rel | dvfs-16, hotline-relay-l2-V09 | relay (dvfs-3 a, E-RL2): launches with no clock change and with only single-step changes return 0 wrong elements; among DRAM launches with a direct 800->600 drop inside the launch >= half return wrong elements > 0; no steady-600 run (warm blocks, 90 runs) and no hop run reports a wrong element; >= 1 moved DRAM run fails in >= 2 of 3 sessions. | one-sided Fisher exact (moved vs steady) x (failed vs passed), pooled, p < 0.01, >= 4 moved launches (report power honestly; ~60 moved DRAM runs needed at a 12% rate). No failure in >= 40 moved DRAM runs -> V09 recorded as not reproduced. The steady-600 "0 wrong" part is tested on both cards by V3-LAT and V3-RL relay launches. |
| COOL-gov | dvfs-29, dvfs-36, dvfs-37, dvfs-V02, dvfs-V03, dvfs-24 | governor at 25 ms: on the first sample after each down-step sp.minion_c[0] >= 66 in >= 80% of down-steps and more often than minshire[0] >= 66; voltage moves with frequency in 100% of changes; first change 0.14-2.0 s after start, median 0.5-0.9 s; consecutive changes a median 0.3-0.5 s apart; >= 30% of up-steps 600->800 within one 100 ms window; idle reset to 600 within 1.5 s (median 0.8-1.2 s); zeros runs: <= 10% of boundaries above 600 MHz drop straight to 600. | binomial 99% CI per session; McNemar one-sided pooled alpha 0.01; latencies in range in >= 2 of 3 sessions. |
| COOL-hl | hotline-relay-l2-11 | every "starved" run whose clock is not 600 MHz throughout lets >= 1,000,000 host loads through per 2 s window; every steady-600 "starved" run gets 384+-16. | Fisher exact on (clock moved vs steady) x (through vs stopped), pooled over 3 sessions, one-sided p < 0.01 with >= 6 runs per clock class and the same direction in each session. |
| COOL-vf | horace-lowpower-009, horace-lowpower-068, horace-lowpower-069, horace-lowpower-072, horace-lowpower-073, horace-lowpower-156, horace-lowpower-182, horace-lowpower-185, dvfs-71, pt-spatial-43 | (a) full-chip zeros TFLOPS / randn TFLOPS >= 1.15 in each of 3 cool periods (E10: 1.22-1.27); (b) switching-power ratio 800/600 MHz randn light 1.91+-0.20, ones 1.91+-0.30; (c) idle at 800 MHz exceeds idle at 600 by 5-9 W at the same reading. | (a) one-sample t on the 3 log ratios, 99% interval above 0; (b) 99% interval inside [1.6, 2.2]; (c) excludes 0. One card by necessity. |
| COOL-ch | memhier-onchip-09, memhier-onchip-11, memhier-onchip-12, memhier-onchip-14, memhier-onchip-37, memhier-onchip-42, memhier-onchip-43, memhier-onchip-47, memhier-onchip-96, memhier-onchip-V01, anatomy-39, anatomy-44, anatomy-113, anatomy-114 | per chase at telemetry clock f: remote scratchpad = 65.95 + (56.48 + 20.00*hops)*f +-1 cycle; L3 from 0 = 72.2 + 161.4 f +-1.5; from 24 = 72.2 + 145.1 f +-1; DRAM from 0 = 86.3 + 344.8 f +-6; on-chip plateaus 47.0 at every f. | per session: >= 95% of counted chases within tolerance; per-hop scratchpad slope at 800 MHz 16.00+-0.1; >= 5 counted chases at each of 600, 700, 800 MHz or the session is repeated. |
| COOL-el | ridge-49, ridge-50, ridge-51, ridge-52, ridge-53, ridge-V01 | elasticity ln(GB/s cool / hot) / ln(f cool / f hot): L2 and own scratchpad 1.00+-0.02; DRAM 0.00+-0.05; L3 0.65+-0.20; other-shire scratchpad 0.33+-0.10; TensorSend pairs and in-shire rings 1.00+-0.05; between shires (xshire:2) < 0.3. | per config mean over >= 3 cycles, 99% t: L2, scratchpad, pairs, in-shire inside [0.95, 1.05]; DRAM inside [-0.1, 0.1]; L3 and other shire exclude 0 and 1; xshire:2 lower bound > 0.3 -> the explorer must scale it with the clock. |

Also informed by this experiment (no own prediction item; the item of the claim they depend on decides): memhier-onchip-45.

### V3-LONG (OWNER): Minutes-long runs to a temperature cap on both cards

Priority note: runs only with the owner's waiver of the 10 s rule (decision D1).

Why: The Horace KPI "19-26 s / 107-167 s / never" and the equal-flip-power claim come from one aifoundry2 session.

Merges: horace-lowpower:horace-lowpower-X3. Cards: both. Suggested experiment number when run: E47.

Build / sync first:
- None; v3long.sched (12 lines: ones 32 600 <s>, randn 12 600 <s>, randn 32 600 <s>, zeros 32 600 <s>, s = 1..3, shuffled).

Repeats: 3 runs per pattern per card (unit = run). Order: shuffled schedule; cooling between runs.

Commands (exact component commands, verified against the scripts, are in `plan3.json` `experiments[].components_detail`):
- `a2: tools/ettelem/run_horace_long.sh build/v3long v3long.sched 80 84 90 900 14400 600; a3: ... 55 60 65 900 10800 600`

Sampler: ettelem 10 Hz

Etiquette: Each run holds the card up to 10 minutes: this breaks the 10 s rule and needs the owner's explicit OK (the script's waiver covered E12 only). A chain of 9 s launches is not a way around it.

Card minutes: aifoundry2 105, aifoundry3 80.

Reduction: analyze_horace_long.py; validate_flip_model.py with the frozen model.json (a2)

Pre-registered predictions and decision rules (7 claims):

| item | claims | prediction | decision |
|---|---|---|---|
| LONG | horace-lowpower-010, horace-lowpower-077, horace-lowpower-078, horace-lowpower-079, horace-lowpower-080, horace-lowpower-126, hub-026 | time-to-cap ratio ones@1024 / randn@384 in [0.7, 1.4] on each card; zeros@1024 never reaches the cap and ends within +-2 C of launch; randn@1024 reaches the cap >= 4x sooner than ones@1024. | per card: zeros all 3 below cap; randn all 3 reach it and log-time difference >= log 4 (Welch 99%); equal flip power: Welch 99% of the log time ratio inside [log 0.7, log 1.4] (fallback on a3: de-quantised rise at 120 s, ratio inside [0.8, 1.25]). |

### 2.13 Schedule

- The two cards run in parallel (separate hosts); the operator starts a block on one card while the other runs. Long unattended blocks (ABL-A, ABL-B, WIRE, IDLE) are launched with setsid nohup ... < /dev/null & and polled with pgrep.
- Before every block: who; uptime; pgrep -af "_host|ettelem|dev_mngt|et-powertop"; lsmod | awk '$1=="et_soc1"{print $3}' (0, or 1 when only our own sampler holds it). Another user present: wait, do not start.
- Every device process is under timeout 10 or a host --budget <= 10 s (patched copies listed in new_code); samplers hold only the management node and are stopped with SIGTERM, never kill -9; a failed sampler start is followed by one drain (dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000).
- aifoundry2 power and memory-bound blocks start on a die >= 76 C (heat() of run_reruns_warm.sh: 2 s sparsity_t2 randn launches under timeout 10) and drop anything with mhz.minion != 600; aifoundry3 needs no heater (pinned 600 MHz).
- Passes of one experiment on one card are separate blocks >= 30 min apart (10 min for MEM and MMB), with other experiments' blocks in between, so repeats do not share a session state.
- Pre-registration: before the first card block, plan3.json (predictions) and every new reduction script are hashed (sha256 in the run log) and, if the owner agrees (decision D5), committed.

Day 0 (no card, or < 1 min checks):
- a2: build memprobe-v3 and sgemm; compile etcfg; write the scratch drivers (N1-N7); dry-run every reducer on committed data (crosscard_v3.py, exp_test_v3.py, x1_reduce.py for pt, x2/x3_reduce.py).
- a3: deploy memprobe (deploy-lab.sh) and gp-sdk (deploy-lab-gpsdk.sh); rsync runners, cfgs, structured tiles, scripts/mmbench-*.py, et-power-log.sh, run_thermal.sh; check ettelem knows --reset-ms / sptrace / loglevel; gen the dram_seq table.
- Short card checks (both, < 1 min each, user check first): mmbench-check and it_test_code_loading on a3; the shire-7 memprobe smoke test on both; the int8/fp16 --b-stream sys_emu check (no card).

aifoundry2 (this host):

| day | block | items (card minutes) | minutes |
|---|---|---|---|
| 1 | AM rounds | TEL-p1 (20); MEM-p1 (4); MMB-p1 (11); LAT-p1 (32); X5 hi0 + lo0 (13); MEM-p2 (4); TEL-p2 (20); MMB-p2 (11) | 115 |
| 1 | PM long session | ABL-A, 4 blocks, unattended (115) | 115 |
| 2 | AM rounds | [if a cool morning: COOL light block first, see below]; LAT-p2 (32); X5 hi1 + lo1 (13); MEM-p3 (4); TEL-p3 (20); MMB-p3 (11); LAT-p3 (32); X5 hi2 + lo2 (13); MEM-p4, MEM-p5 (8); MMB-p4 (11); LAT divergence blocks 4-5 (3) | 147 |
| 2 | PM long session | ABL-B, 3 blocks, unattended (59) | 59 |
| 3 | SHOULD | WIRE, 6 passes, unattended (45); RL-p1..p3 interleaved with CAT arm A W/H and arm B passes (36 + 40) | 121 |
| 4 | SHOULD | RL-p4..p6 (36); CAT remaining passes (41); IDLE cycles 1-3 in the evening (66); IDLE-LONG overnight if the owner wants it and the room is cool (+225) | 143 |
| any cool morning (die <= 63 C at start, polled with the card closed) | COOL | light block (~30 min): ridge-X2 cool phase, memhier-X4 chases, E-HL2 cool block + E-RL2 relay, dvfs-3 relay + governor, run_vf_cold10 one cycle, heater, ridge-X2 hot phase; on a separate cool morning: run_horace_cold_v3 zeros/randn/ones (~5 min) | 89 |

aifoundry3 (ssh, from ~/nekko):

| day | block | items (card minutes) | minutes |
|---|---|---|---|
| 1 | AM rounds | TEL-p1 (16); MEM-p1 (2); MMB-p1 (6); LAT-p1 (15); X5 hi0 + lo0 (10); MEM-p2 (2); TEL-p2 (16); MMB-p2 (6); LAT-p2 (15); X5 hi1 + lo1 (10) | 98 |
| 1 | PM long session | ABL-A, 4 blocks, unattended (65) | 65 |
| 2 | AM rounds | MEM-p3 (2); TEL-p3 (16); MMB-p3 (6); LAT-p3 (15); X5 hi2 + lo2 (10); MEM-p4, p5 (4); MMB-p4 (6); LAT divergence blocks 4-5 (1) | 60 |
| 2 | PM long session | ABL-B, 3 blocks, unattended (30) | 30 |
| 3 | SHOULD | IDLE cycle 1 first (its Tmax sets CAT arm A's hold temperature) (27); WIRE, 6 passes, unattended (38); RL-p1..p3 (22); CAT arm A C/H and arm B passes (39) | 126 |
| 4 | SHOULD | RL-p4..p6 (21); CAT remaining passes (39); IDLE cycles 2-3 (53); IDLE-LONG overnight optional (+90) | 113 |

MUST fits in two lab days on each card, run in parallel (aifoundry2 is the bottleneck: ~7.1 h of card time against ~4.2 h).
SHOULD adds two more days plus cool mornings on aifoundry2. In each round the order of experiments rotates, so no experiment's
passes share a session with each other.

## 3. New code and runners

- **N1**: run_memprobe_v3.sh (scratch, both hosts): per-pass driver for V3-MEM: off-card op generation (incl. t_rawodd via gen_ops.Prog and the requester folders), user check, a2 heat(), start_sampler with retry and drain, shuffled programs each under timeout 10 --budget 8, requester programs, SIGTERM the sampler, wake-up probe with 1 s pre/post samples (passes 1-3).
- **N2**: run_tel_v3.sh (scratch, both hosts, ~100 lines): per-pass driver for V3-TEL: governor readouts at INFO (no sampler), SPST extracts x3, the shuffled arms Q/PWR/L10/E10/E20/E40/VOLT with marks.jsonl, the --reset-ms burst segment, the DEBUG block (loglevel debug with an EXIT trap back to info, sptrace per window). Bounded poll loops only (never kill a poller mid-request).
- **N3**: build/v3abl/run_ablation_v3.sh: patched copy of tools/ettelem/run_ablation.sh: cd "${REPO:?}"; timeout 10; @TSEED@ substitution; SEED_OFFSET in both seed expressions; wait while the et_soc1 use count > 1 before each run. Configs abl_a.cfg (23 lines), v3-energy.cfg (18), x5.cfg (5).
- **N4**: tools/ettelem/run_rl_spin_v3.sh (next to the original; copied to aifoundry3 with chmod +x): rings/levels with spin brackets, ABBA, contents prefill (enercat tstore zeros / random) before scp-local and scp-remote, timeout 10 + --budget 8; tools/ettelem/run_onchip_power10.sh (timeout 40 -> 10).
- **N5**: idle_cycles.sh (scratch, both hosts, ~30 lines): 90-min sampler, 3 x (heat to target, mark, 900 s or 5400 s idle), skip a cycle when another user holds the card.
- **N6**: run_catalogue_t10.py: copy of workloads/enercat/run_catalogue.py with timeout 10, --host-bin, --hold-hot C (ROOT pinned if not placed next to the original).
- **N7**: aifoundry2 cool-morning wrappers: run_cool_v3.sh (wait with the card closed until <= 63 C, then the light block), run_clock_chase_v3.sh (memhier X4 chases with heater nudges), run_rl_clock_v3.sh (ridge X2 cool/hot phases), and patched copies next to the originals: run_vf_cold10.sh (timeout 10), run_horace_cold_v3.sh (others() wait), run_hotline_power10.sh (timeout 10).
- **N8**: Reduction scripts still to write (off-card, before the first run, hashed with the predictions): abl_reduce.py (x1_reduce: the ABL-A dropout rule, T1-T8 with the 19-test Bonferroni family, the EM4 ratios, the aifoundry3 flip-energy refit), ablb_reduce.py (per-block paired differences, lines, layer energies from runs.jsonl), x5_reduce.py, mmb_pool.py (E1 pass-level values, Welch, per-W), ridge_x1.py, lat_pool.py (E4/E5/ridge-X3 pass means and the divergence df-4 test), hl1_reduce.py (P1-P7 per card), rl1_offsets.py (geometry fit and permutation test over the 11 new geometries), tel_reduce.py (SP-trace alignment and P1-P7, reusing validate3/hubv/sp_period.py), idle_reduce.py (per-cycle bins and fits, from ftm_copy.py and leak_share_profile.py). Existing and dry-run: anatomy-verify/tests/crosscard_v3.py, heat-verify/exp_test_v3.py, inv/pt-spatial-work/x1_reduce.py, x2_reduce.py, x3_reduce.py, dvfs-verify/wake.py, inv/memhier-onchip-work/chases.py, noc_audit.py, ver-energy-manual/verify_cat.py, verify_reruns.py, inv/energy-manual-work/reruns_perpass.py, rings_relay_extra.py, inv/ridge-work/c_elasticity.py, e_energy.py.
- **N9** (device code): New device code: none is needed for any MUST or SHOULD experiment. The only claim that would need a kernel change is matmul-sparse-testdrive-65 (flat DRAM time under a fixed mask "probably" caused by home-shire concentration): E6's --rotate-mask mode (host + kernel + sys_emu check + nice -j4 rebuild on both cards). A simpler test with an existing workload does not decide it cleanly: enercat tload_pat with --access-bytes 512 at --stride 1K (lines on 16 of the 32 home shires: PA[9] = 0 always) against --stride 512 (all 32 homes, same bytes) changes DRAM bank/row locality at the same time (PA[12:10] is the bank; stride 512 puts two consecutive accesses in one row), so a difference would not isolate the home shires. Recommendation: keep the sentence labelled as a hypothesis ("probably ... untested") and do not build E6 now.
- **N10**: Not code but a waiver: V3-LONG needs minutes-long holds (owner decision D1). A chain of 9 s launches holds the card just as long and is not a way around the rule.

## 4. Decisions for the owner

**D1. Minutes-long holds for the long runs (V3-LONG, horace-lowpower-X3).** Allow 12 runs of up to 10 minutes per card (~105 min aifoundry2, ~80 min aifoundry3), breaking the 10 s rule under a written waiver; OR keep the rule and qualify the long-run results now.
Claims: horace-lowpower-010 (KPI "19-26 s / 107-167 s / never"), horace-lowpower-077, horace-lowpower-078, horace-lowpower-079, horace-lowpower-080, horace-lowpower-126, hub-026.
If not: The Horace KPI and section 7 say "aifoundry2, one session (3-4 runs per pattern)"; "equal flip power, equal curve" becomes "consistent with (one run of random normal on 384 minions)". Recommendation: No waiver unless the section matters to readers; the KPI survives as a labelled one-card, one-session result.

**D2. The Horace speed-effect headline (zeros 25% faster from a cool die) and V^2 f.** Spend >= 3 cool mornings on aifoundry2 (V3-COOL speed-effect sequence; aifoundry3 can never test it) to replicate it on one card; OR demote it now from the lede/KPI to a labelled "one card, one morning, seven runs" demonstration.
Claims: horace-lowpower-009, horace-lowpower-068, horace-lowpower-069, horace-lowpower-072, horace-lowpower-073, horace-lowpower-156, horace-lowpower-182, horace-lowpower-185, hub-010, pt-spatial-43, dvfs-71.
If not: The lede and KPI stop presenting 11.6 vs 9.3 TFLOPS as a finding; it moves to section 6 as a demonstration with its n. Recommendation: Demote now (it can never be PROVEN-BOTH); run the cool-morning sequence opportunistically and restore the KPI as "one card, n cool mornings" if it replicates.

**D3. The idle law's leakage split (12.6 W fixed + 23.3 W leakage at 80 C, "doubles every 25 C").** Present the split as a range now (20-29 W at 80 C; T_L 30-45 C fits equally) and lead with the measured slope 0.65 W/C; optionally run IDLE-LONG overnight (likely inconclusive: the verifier expects "not identified").
Claims: energy-manual-01 (the manual's first headline), energy-manual-06, energy-manual-10, horace-lowpower-087, horace-lowpower-139 (why-low-power lede "23 W at 80 C"), horace-lowpower-158, dvfs-05 (DVFS lede), anatomy-115, hub-009.
If not: Pages keep "23 W" and "doubles every 25 C" as exact, which the data do not identify. Recommendation: Change the headlines to the range and the slope now; IDLE-LONG only on a cool night.

**D4. Scope and card time.** MUST only (aifoundry2 ~7.1 h, aifoundry3 ~4.2 h of card time, ~2 lab days in parallel) or MUST + SHOULD (~13.0 h / ~8.2 h, ~4 lab days, plus cool mornings and optional overnight idle curves).
If not: Without SHOULD, the heat-per-mm board split, level-energy card differences, the catalogue temperature question and the clock-dependent claims stay qualified as they are now. Recommendation: MUST first; decide SHOULD after MUST reports, since MUST results may make V3-CAT (card vs temperature) unnecessary.

**D5. Pre-registration commit.** Commit plan3.json (predictions and decision rules) and the reduction scripts to the repository (e.g. docs/reports/data/2026-09-25-v3-plan/) before the first card run, so the predictions demonstrably predate the data; OR keep them in scratch with sha256 in the run log.
If not: The forking-paths standard rests on the run log's hashes only. Recommendation: Commit.

## 5. Top risks

- aifoundry2 heat overhead: its die falls below 68 C within a few minutes of light probes, so every LAT/MEM group needs the heater; card time on aifoundry2 is ~1.7x aifoundry3's and dropped (off-600 MHz) groups must be re-run.
- Cool mornings may not come: aifoundry2 rested at 73-74 C on 22-24 Sep. V3-COOL (all clock-dependent claims, the Horace speed effect) may stall; after a week the claims are qualified as they stand.
- Builds on aifoundry3: memprobe and the gp-sdk (mmbench) are not built there; deploy-lab-gpsdk.sh needs external/et-platform at gp-sdk 06605ab. The two cards run different /opt/et toolchains, so absolute cycle offsets can differ (the 22 Sep memprobe build read an L1 hit 7 cycles slower): V3-MEM re-references to each pass's L1 hit, and a build difference must not be reported as a card difference.
- Management node: single opener, samplers that die mid-request poison the queue, some traffic (s <-> s+16 rings, a2 y-only 3-hop pairs, DRAM reads on a2) starves the sampler. Drop rules are fixed in advance; the TEL driver uses bounded poll loops only.
- First use of --reset-ms and SPST resets (V3-TEL): they reset shared min/max that other users see and may disturb the PMIC running average; if the reset does not reset the peak-hold (R1), the X3 claims stay under-replicated.
- aifoundry3 cannot be heated much above ~61-66 C and aifoundry2 cannot hold 600 MHz below ~68 C, so the cards never share a temperature at 600 MHz: card vs temperature can only be separated within each card (V3-X5, V3-CAT), and absolute idle/board values stay per card.
- Many pre-registered bands are tight (deterministic cycle counts, +-0.05 cycle tolerances): expect some FAILs from tolerance, not physics. The rule is fixed: the page takes the measured per-card value; no band is widened after seeing data.
- Other users on the shared cards delay blocks; the plan has no hard dates, only order and spacing.

## Files

- `validate3/PLAN3.md` (this file), `validate3/plan3.json` (twin: claims, experiments, schedule, decisions).
- `validate3/plan3work/`: `quoted_map.py` (QUOTED resolution), `classify.py` + `build_plan.py` (actions), `v3exps.py`,
  `preds.py` (merged experiments and predictions), `extras.py` (schedule, new code, decisions, risks), `gen_outputs.py`.

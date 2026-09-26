# Visualization pass: survey and plan (ET-SoC-1 reports, 25 Sep 2026)

Scope: the 19 pages of "The measurement set" in `docs/reports/MIRROR.md` (the aifoundry1 lab pages and the private
pages are left out). This is a survey only. No repository file was changed. Every data path and field named below was
opened and checked, either during this survey or by one of its six parallel read-only passes. "Not committed" means
the v3 outputs do not exist in the repo yet.

## 0. Ground rules for the implementer

- **Pages run inside spacesheep.dev, which blocks external scripts.** Everything is inline: source-built pages get
  `chartkit.js` from `scripts/build-report.py`, and standalone pages get it from `scripts/paste-chartkit.py`.
- **What chartkit already offers** (`docs/reports/sources/chartkit.js`, global `CK`):
  - Drawing: `frame` (a responsive SVG), `lin`/`log` scales, `axes`, `inside`, `fmt`, `path`, `el`/`txt`.
  - Interaction: `tip` (pointer, keyboard and touch tooltips), `keynav`, `legend` (optionally toggling series), `showSeries`.
  - Controls and state: `seg` (a radio group), `range` (a slider, optionally with stops), `readout` (aria-live), `bus` (named pub/sub).
  - Tables and colour: `stackTable` (phone layout), `ramp`/`rampInk` (one-hue sequential scale), `color(i)` (series tokens c1–c5, c7), `reduced` (prefers-reduced-motion).
  - Nothing more is needed for anything in this plan, except the two helpers proposed in §3 (a card registry and a sortable table).
- **No page has a sortable table.** A grep for `aria-sort` or `sortable` finds none.
- **Card colours are inconsistent between pages:**
  - Horace (`horace-experiment.script.js:471`) uses aifoundry2 = `--c1` and aifoundry3 = `--c2`.
  - The energy manual's idle chart (`energy-manual.script.js:113-114`) uses aifoundry2 = `--c2` and aifoundry3 = `--c3`, because `--c1` is the law.
  - sparsity.html uses aifoundry3 = `--c2`.
  - Fix these before adding a third card (§3.1).
- **Many pages already have what the obvious ideas would suggest.** Do not rebuild any of these:
  - the energy manual's workload calculator (§7.1);
  - Why-low-power's C·V²·f + leakage calculator (§4);
  - Influence's explorer with N/k/Q sliders;
  - the hot line's N/P saturation sliders (§3);
  - DVFS's governor replay with Play, scrub and a rule panel (§2), and its idle-law slider (§5);
  - heat-per-mm's P–t plane and voltage slider;
  - power-temperature's per-shire voltage heatmap `vmap` and the W-against-°C `pvt` scatter;
  - Ridge's interactive roofline `c-roof`;
  - on-chip communication's ping-pong mesh map;
  - memory hierarchy's scratchpad die map `scp-map` and its latency-against-working-set chart;
  - Horace's "Price a workload" and its 2-card scale slider.

## 1. What version 3 changes, page by page

The experiments come from `plan3.json.gz` (`experiments[].claims_tested` joined to `claims[].page`), plus the two that
are not in PLAN3. The v3 campaign runs on aifoundry2, aifoundry3 and aifoundry1-c1; aifoundry1-c0 is excluded (amendment A4).

- **catfull:** the energy manual's full 392-configuration catalogue, three passes on each card. Its `reduce.py` gives
  per-card and pooled values and card-to-card ratios.
- **gs:** gathers, scatters and packed atomics (E48), on three cards. `reduce.py --gs-out gs.json`.

"cool" (V3-COOL, aifoundry2 only, from a cool die) and "long" (V3-LONG) in the table are PLAN3 experiments with no
`tools/claims-v3/` directory. COOL's steady-600 MHz warm controls run inside lat's passes on aifoundry2.

None of the v3 outputs are committed yet. A card toggle that "gains a third card" therefore needs the page's data JSON
regenerated, and several scripts hard-code two cards (listed per page below).

| page | v3 experiments (claims tested) | TEST | QUALIFY-PER-CARD |
|---|---|---|---|
| hub (limits-of-observability) | mem 7, lat 3, mmb 1, abla 2, ablb 1, tel 13, idle 2, cat 1, long 1 | 4 | 18 |
| energy manual | abla 12, x5 2, tel 1, rl 13, idle 16, cat 13, + catfull, gs | 17 | 23 |
| heat per mm | wire 16, tel 1 | 1 | 2 |
| DVFS and leakage | mem 9, abla 2, tel 11, idle 6, cool 8 | 14 | 11 |
| power and temperature | mmb 17, tel 12, idle 1, cool 1 | 20 | 4 |
| Horace | mmb 2, abla 27, ablb 2, x5 6, tel 1, idle 4, cool 5, long 6 | 35 | 23 |
| why low power | abla 15, x5 1, idle 4, cool 3 | 15 | 8 |
| hot line | lat 17, cool 1 | 12 | 0 |
| on-chip relay | lat 8, rl 1, cool 1 | 4 | 1 |
| memory anatomy | mem 64, tel 2, idle 1, cool 4 | 59 | 5 |
| memory hierarchy | lat 15, rl 5, cool 10 | 17 | 2 |
| on-chip communication | lat 21, tel 1, rl 7, cool 1 | 21 | 2 |
| matmul efficiency | mmb 17, ablb 3, tel 1 | 16 | 3 |
| sparse compute | lat 23, mmb 1, ablb 10, tel 1 | 30 | 4 |
| ridge points | lat 10, mmb 12, abla 2, rl 4, cool 6 | 17 | 3 |
| test drive | lat 5 | 4 | 1 |
| spatial temperature brief | tel 9 | 5 | 0 |
| L2 starvation brief | lat 2 | 0 | 0 |
| influence functions | not in PLAN3 (written 25 Sep); gs, idle and catfull feed its model | — | — |

## 2. Top 12: best impact per effort

The ranking weighs three things:
- how much clearer a key result gets;
- the effort;
- whether the data is committed now, or whether v3 turns the item into the page's card view.

| # | page · section | what to build | effort | data (verified) | v3 |
|---|---|---|---|---|---|
| 1 | DVFS · 5 What that costs (#what-that-costs) | Strip plot of every session's idle offset, one row per card. It leads the `#sesstab` table hidden in a details block. | S | `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json` `idle_sessions.sessions[]` (41: 25 a2, 16 a3; `session, card, day, T, n, offset_W`) and `idle_sessions.summary.{aifoundry2,aifoundry3}.{mean_W,sd_W,min_W,max_W}` | idle adds an aifoundry1-c1 row and more days |
| 2 | Energy manual · §7.1 Build a workload's energy (#build-a-workload-s-energy), plus #bytemap and #allinstr | One card selector for the page, "pooled / aifoundry2 / aifoundry3 / aifoundry1-c1", on `CK.bus('card')`. It drives the existing calculator (per-card pJ and per-card rates) and adds a "compare cards" mode: one stacked bar per card. `#allinstr`'s own Card seg moves onto the bus, and `#bytemap` gains one. | M | `docs/reports/data/2026-09-23-energy-manual/manual.json` `catalogue.combined[k].per_card.{aifoundry2,aifoundry3}.{mean,se,n,unit}` (392 keys); `catalogue.cards.<card>.summary[k].{ops_per_s,bytes_per_s,pj_per_op,pj_per_byte}` | catfull (all costs on three cards), idle (per-card law), abla, rl. **The most important card toggle.** |
| 3 | Hub · §1 The measurement reports (#reports) | Claim-status scoreboard: one stacked bar per page by verdict. A seg switches to a cards view (both / a2 / a3 / none). A click opens the page. After v3 it becomes the before/after view. | M | `docs/reports/data/2026-09-25-claims-v3/plan3.json.gz` `counts.per_page[slug].{claims, effective_verdict_quoted_resolved, action}` (18 pages) and `claims[].{page,cards}`. It must be copied into `limits-of-observability.data.json` as a new key. | every reducer moves claims between verdicts. Add a column for aifoundry1-c1. |
| 4 | Heat per mm · §4 (#distance) and §6 (#contention) | Card seg (pooled / per card) beside the existing meter seg, or per-card lines with legend toggles. | M | `docs/reports/data/2026-09-24-wire-energy/report.json` `wire.configs[cfg].{pj_per_byte,noc_pj_per_byte}.per_card.{aifoundry2,aifoundry3}.{mean,se,n}` (126 configs) | wire: 6 passes × 3 cards |
| 5 | On-chip comm · Where the shires are (#where-the-shires-are-a-6-6-mesh) | A "shade by" seg on the existing `#mesh`: TensorSend 32 B / 1 KB / credit / memory flag. Later, a card seg. | S | embedded `#nocbench-data` `matrices.{matrix-pingpong, matrix-pingpong-c32, matrix-fcc, matrix-flag}.pairs` (496 `[a,b,cycles]`), with `a, b, r2, worst` (matrix-flag r2 = 0.003, distance-free) | lat re-runs all four matrices per card |
| 6 | On-chip relay · §3 (#where-the-advantage-comes-from-and-where-there-isn-t-one) | Two small panels: GB/s against stages (1–32) and GB/s against shires (2–32), with DRAM / next shire / own shire as lines. This data is in the page but never drawn. | S | `docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json` `stages[]` (6 rows) and `shires[]` (5 rows), each `{dram,hop,scp}.gb_s` and `hop_over_dram`. At 32 shires DRAM falls to 46.8 GB/s and hop/DRAM is 12.7×. No script reads these today. | lat (E-RL1) re-runs them on three cards. aifoundry3's rows are in `2026-09-22-onchip-aifoundry3/sweep.jsonl`. |
| 7 | Why low power · 1 The comparison (#the-comparison) | Ratio chart: one diverging log bar per metric (A100/ET) for transistors, die area, load and idle power, TFLOPS, pJ/FLOP, W/mm², V²f and memory bandwidth. Bars point left where ET wins. Keep `#cmp` in a details block. | S | `docs/reports/data/2026-09-21-horace-aifoundry2/lowpower-report.json` `facts.a100.{transistors_b,die_mm2,tflops,watts,idle,volts,mhz,mem_gbs}`, `facts.et.{…,idle62,idle80}` | abla and mmb change the ET values per card |
| 8 | Ridge points · #c-roof (and #the-same-numbers-for-an-a100) | A toggle that overlays the A100's ceilings and its three bandwidth diagonals, dashed in `--ref`, on the existing roofline. | S | embedded `#ridge-data` `a100.peaks.{fp32,fp16,int8,tf32}` and `a100.levels[].{name,tbs,tbs_peak,ridge.*}`. Today these appear in tables only. | none for the A100 |
| 9 | Hot line · 2 The thing that actually starves (#the-thing-that-actually-starves) | Step-through SVG of one shire: host minions, the bank and its queue, and remote atomics arriving. A seg steps through alone → below the knee (queue drains) → saturated (remote requests outrank local ones and the host stops at about 384 ops). It shares N and P with the §3 sliders over a bus. | M | `docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json` `context.{bank_service_cycles (10), remote_atomic_latency_cycles (216.2), window_independence, errata}`; `local[]`; `shires[]` (12 rows; `host_ops` 384–391 whether 2 or 32 shires hammer; not used by the script today) | lat (E-HL1) adds raw data for the windows. The diagram itself is unchanged. |
| 10 | Heat per mm · 8 What it means in practice (#meaning) | Route and payload calculator: click two shires on a copy of the §2 die drawing. A payload slider (64 B–1 MB), a data seg and a meter seg drive a readout: nJ over the mesh against the same bytes from DRAM and from the own scratchpad. Beyond 6 hops is flagged as extrapolated. | M | report.json `inputs.mesh_xy.value`, `inputs.hop_mm.value` (3.72), `headline['v2/board'|'v2/noc_rail'].{random_bit_total,per_one,per_transition,fixed_per_bit}.mean`, `context.{tload_dram_random_pj_per_byte (129.1), own_scratchpad_pj_per_byte (4.21)}` | wire changes the per-hop values. Take the card from item 4's seg. |
| 11 | Memory anatomy · Which address bits share a row (#which-address-bits-share-a-row) | Physical-address decoder: a hex input with presets. It shows a colour-coded bit strip (line offset, home shire PA[10:6], memory shire PA[8:6], bank PA[12:10], column PA[17:13], row) and a readout of the fields. Hover shows each bit's measured cost. A bus sets the `#trace-one-load` explorer's L3 home. | M | embedded `const D`: `D.bits["6".."29"].{ab_med,ab_p10,ab_p90,b_minus_b0_med,…}`, `D.msmap.rows[].{pa,ms_bits,deltas[8]}`, `D.memByHome[h]` | mem MEM-P3 and P4 re-measure the per-bit costs per card. The mapping is deterministic. |
| 12 | Memory hierarchy · spec sheet (#et-soc-1-measured) | Per-level energy dot plot: one row per level, each card's mean ± se, with the pooled lo–hi range. It replaces the "0.86 / 0.68 pJ" slash notation. | S | `docs/reports/data/2026-09-23-energy-manual/reruns.json` `levels_pj_per_byte.{l1,l2,l3,dram,scp-local,scp-remote}.{mean,lo,hi,n,per_card.{aifoundry2,aifoundry3}.{mean,se,n}}` | rl (RL-g, RL-h) adds the third card |

Next in line (also S, data committed):
- **Power and temperature:** a dot-and-whisker chart of busy drift per card (§2 below).
- **Hot line:** an energy chart replacing `pwrtab` (§8).
- **Horace:** a card picker in "Price a workload" (§6).
- **On-chip communication:** a chain-order path comparison, and a systolic grain calculator (§12).
- **Matmul:** an operand band on the efficiency explorer (§13).

## 3. Cross-page ideas

### 3.1 A card registry in chartkit (do this before any card toggle)
Add `CK.cards` to `chartkit.js`:
- An ordered list: aifoundry2, aifoundry3, aifoundry1-c1. aifoundry1-c0 is excluded, but keep a slot drawn in `--ref`.
- Fixed tokens: aifoundry2 = `--c1`, aifoundry3 = `--c2`, aifoundry1-c1 = `--c3`. Pooled draws in `--ink`.
- Fixed marks: filled, ring, and diamond.

Then add `CK.cardSeg(host, {cards, pooled:true})`, which emits on `CK.bus('card')`, and a picker `CK.pick(v, card)`:
- It returns `v.mean` for pooled, or `v.per_card[card].mean` with its `se`.
- `per_card:{<card>:{mean,se,n}}` is already the shape used in manual.json `catalogue.combined`, report.json `wire.configs`, reruns.json and ridge `energy.e_flop` and `e_byte`.
- The pickers should hide a card that has no value, rather than draw zero.

Then:
- recolour the energy manual's idle chart (`energy-manual.script.js:113-114`) and Horace (`:471`) to the registry;
- give every page with a card toggle the same labels.

Effort S for the helper; the per-page wiring is counted in each item.

### 3.2 A sortable, filterable table helper
Add `CK.sortTable(table, {filter})` to chartkit: click a header to sort, with `aria-sort`, numeric parsing that
understands the true minus, and an optional text filter box. It is S. First users:
- the hub: `#reportstab`, `#imptab`, `#sessionstab`;
- the energy manual: `#tensor`, `#memtab`, `#linetab`, `#rowtab`, `#neightab`, `#comm`, `#sync`;
- Horace: `#tbl`, `#coef`, `#struct-tbl`, `#val-tbl`;
- heat-per-mm: `#modeltab`.

These tables are long, and readers look for the extreme rows.

### 3.3 The hub as the v3 dashboard
Build these on `docs/reports/2026-09-20-et-soc1-limits-of-observability.html`, from `sources/limits-of-observability.*`:
- **(a)** The claim scoreboard (top-12 item 3).
- **(b)** The session map (`#map-frame`) lanes, generalised from a2/a3 to a card list.
  - `cardOf()` (around line 605 of the script) only knows a2, a3, both and none.
  - `D.sessions[].card` already holds free text such as "aifoundry3, all three".
  - v3 sessions span three cards, so this is required, not optional (S).
- **(c)** The §4.2 `#v1` Card seg, with its options taken from the keys of `D.power.per_config` (today `{aifoundry2,aifoundry3}`, 392 entries each), so that catfull's third card appears without code changes (S).
- **(d)** Optionally, a "cards covered" matrix of pages × cards from `claims[].cards`, as a second seg state of (a).

`limits-of-observability.data.json` keys: `ladder` (26), `contrast` (10), `reports` (19), `power`, `improvements` (20),
`sessions` (17), `energy_events` (37 events), `superseded` (9).

### 3.4 Where the gather/scatter (gs) results should go
There are two homes, and both need `gs.json` from `tools/claims-v3/gs/reduce.py`, which is not committed yet.

- **Energy manual §3.1 (#every-instruction-the-core-executes):**
  - A new class in `CLASSES`, "Indexed loads and stores: gathers, scatters, packed atomics". No gather or scatter appears on the page today.
  - A "per element" option on the `all-unit` seg.
  - Points on `#bytemap` beside the contiguous paths.
- **Influence functions S3:** where the measured rate lands inside the 10–300 G/s estimate band. See §19.

## 4. Per page

Each entry lists what exists, then the opportunities in order of preference. "Card seg" means the §3.1 registry seg.

### 1. Limits of observability (hub): `docs/reports/2026-09-20-et-soc1-limits-of-observability.html`

The page is built from `sources/limits-of-observability.{body.html,script.js,data.json}`.

Existing:
- **§1 `#map-frame`:** a session → report timeline in card lanes, with superseded arrows. It has a Card seg (both / a2 / a3), a "show superseded" checkbox, a click panel `#map-panel`, and hover and keynav.
- **§1 `#reportstab`:** a static table.
- **§2 `#gran`:** instrument time resolution, with the filter buttons `#filters` shared with `#laddertab`.
- **§2 `#ev`:** "how many identical events before the meter sees one", with an Operands seg, σ and precision ranges, and the readout `#ev-read`.
- **§4.2 `#v1`:** measured against fitted unmetered watts, with a Card seg, a class legend toggle and the readout `#v1-read`.
- **§4.3 `#dr`:** DDR-rail droop (aifoundry2 only), with a View seg and a class toggle.
- **§5 `#imptab`:** with filters.
- **§6 `#contrast`:** a static table.
- **§7 `#sessionstab`:** inside a details block.

Opportunities:
- The claim scoreboard (top 12, item 3), M.
- Session-map lanes for N cards (§3.3b), S.
- The data-driven `#v1` Card seg (§3.3c), S.

### 2. The energy manual: `docs/reports/2026-09-23-energy-manual.html`

It is built from `sources/energy-manual.*` and `docs/reports/data/2026-09-23-energy-manual/manual.json` (per
`docs/energy-manual/README.md:37`).

manual.json keys: `operating_point, rest, tensor, awake, memory_reads, comm, relay, sync, enercat, catalogue, reruns, unmetered, cards`.

Existing:
- **KPI tiles:** `#k1` to `#k4`.
- **§1 `#idle`:** the idle law with both cards' bins (legend only).
- **§1.1 `#sram`:** SRAM-rail leakage against temperature, both cards.
- **§3 `#instr`:** 13 instructions by operand.
- **§3.1 `#allinstr`:** a beeswarm of every instruction. It has a unit seg, a Card seg (both / a2 / a3), a zeros toggle, a find box and a readout.
- **§4 `#bytemap`:** pJ/B against bandwidth with iso-power diagonals. It has a data seg, a "watts to spend" range and family toggles, but **no card seg**.
- **§4.3 `#wire`:** pJ/B against hops.
- **§4.4 `#railsplit`:** each class of operation split across the metered rails.
- **§7.1 calculator:**
  - Controls: 7 presets, a die-temperature range from 45 to 95 °C, a data seg, a duration input, and three event rows, each with a select and a rate slider.
  - `#calc` is a stacked board-power bar set against the measured value.
- **§8 `#cards`:** the a3/a2 ratio of every entry against aifoundry2's pJ, with the median and a 10–90% band.

Where the calculator's numbers come from today:
- Per-op costs are pooled: `catalogue.combined[k].mean`.
- Rates are aifoundry2's: `catalogue.cards[CARDS[0]].summary[k]`.
- Tensor costs come from `tensor.bars` and `tensor.rows[].per_s`, which are aifoundry2's.
- Idle is aifoundry2's law: `rest.{P_fix_w, A_leak_80_w, T_L_c}`. `rest.cards` holds only TDP, threshold, power state, MHz and mV, so a per-card idle law must wait for the idle results.

Opportunities:
- **(a) A page-wide card bus driving the calculator** (top 12, item 2), M.
- **(b) §8 two cards → N cards**, M.
  - Build: a "compare … against …" pair of segs, or one ratio track per non-reference card with its own median band.
  - Data: `catalogue.cross_card.{pair, ratios, median 0.950, p10, p90, n 386}`, `combined[k].per_card` and `reruns.*.per_card`.
  - v3: catfull and x5. x5 asks whether aifoundry3's 0.92–0.95 is the card or its temperature, so a "same die temperature" view from cat is a natural later state.
- **(c) gs home** (§3.4), M, after gs.

The big per-card tables give a2 and a3 as text: `#awake`, `#tensor`, `#memtab`, `#memold`, `#linetab`, `#rowtab`, `#neightab`, `#comm`, `#sync` and `#relaycheck`. The first two below are the ones to make sortable (§3.2); consider turning the others into dot-per-card plots only after catfull lands.
- `#tensor` (3 precisions × 3 operands);
- `#memtab`;
- `#awake`;
- `#memold`;
- `#linetab`;
- `#rowtab`;
- `#neightab`;
- `#comm`;
- `#sync`;
- `#relaycheck`.

### 3. Heat per millimetre: `docs/reports/2026-09-24-heat-per-mm.html`

It is built from `sources/heat-per-mm.*` and `docs/reports/data/2026-09-24-wire-energy/report.json`, whose keys are
`inputs, literature, wire, first_principles, context, headline, scaled`.

Existing (all charts pool the two cards):
- **§2 `mesh`:** the die drawn to scale, with hover.
- **§4 `dist`:** pJ/B against hops 0–6 per ones-density P, with a meter seg.
- **§5 `model`:** cost per hop against P, with a meter seg, and the `#modeltab` table.
- **§5 `plane`:** a P–t plane with sliders, presets, a "send complemented" button and a readout.
- **§6 `cont`:** with a meter seg.
- **§6 `linkmap`:** with distance, flow-set and route segs.
- **§7 `volt`:** fJ/bit·mm against supply voltage, with a slider and snap buttons.
- **§9 `alt`:** alternating 0/1 blocks, with a meter seg.

The text-only key result is §8 `#practice` / `#practice2`: ten hops against DRAM, and "an add is worth X mm".

Opportunities:
- **(a) Card seg on `dist` and `cont`** (top 12, item 4), M.
  - The prose already quotes per-card splits that no chart can show ("5% on aifoundry2 and 9% on aifoundry3"; the four-hop step "resolved on aifoundry3 only").
- **(b) Route and payload calculator** (top 12, item 10), M.

### 4. The DVFS loop and its leakage: `docs/reports/2026-09-22-dvfs-leakage.html`

It is built from `sources/dvfs-leakage.*` and `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`. Its `cards`
block is required and is added by `tools/ettelem/build_cards_data.py --merge`.

Existing:
- **§2 `cycle`:** "Watch the governor decide": a run seg, Play, a scrub slider and the rule panel `#gov-rule`. aifoundry2 only.
- **§2 `attrib`:** down-steps against the 65 °C and 65 W thresholds. Clicking a point replays it in `cycle`.
- **§4 `wake`:** the wake-up probe, with a level seg and an idle-repeat slider. aifoundry2 only.
- **§5 `leaklaw`:** the idle law, with a temperature slider, a "under a random matmul" toggle, a "shift by aifoundry3's offset" toggle, a readout and a share strip.
- **Tables:** `#verdict`, `#trans`, `#cardcfg`, `#leaktab`, and `#sesstab` in a details block.
- §6 links to Horace's `cardsw`; do not duplicate it.

Opportunities:
- **(a) Idle offset per session, by card** (top 12, item 1), S.
  - The finding is that 25 aifoundry2 sessions sit at −0.37 to +0.02 W and 16 aifoundry3 sessions at +0.53 to +0.74 W: the law transfers with a fixed per-card offset.
  - After idle, replace the "shift by aifoundry3" toggle with a card seg on `leaklaw` (M).
- **(b) Governor branch plane per card**, S–M.
  - Section: §3 (#the-same-firmware-on-three-cards), beside `#cardcfg`.
  - Build: a board-W × die-°C plane shaded by the branch that fires (thermal down / power down / step up / hold). A card seg moves the TDP line from 65 W (aifoundry2) to 0 W (aifoundry3), where the step-up region vanishes.
  - Overlay aifoundry3's throttle-down powers and aifoundry2's transitions.
  - Data: `thresholds.{tdp_w,temp_c}`, `cards.config.{aifoundry2,aifoundry3}.{tdp_w,temp_threshold_c,power_state_name,minion_mhz,minion_mv}`, `cards.sptrace_aifoundry3.{pwr_mw, down_events 26, up_events 0}` and `transitions[].{T,P,dir}`.
  - v3: tel TEL-G gives aifoundry1-c1's governor config.
- **(c) Card seg on `wake`**, S, once mem MEM-W has run on every card. Data today: only `wakeup` (aifoundry2).

### 5. Power and temperature telemetry: `docs/reports/2026-09-20-et-soc1-power-temperature.html`

It is built from `sources/power-temperature.*` and `docs/reports/data/2026-09-20-power-aifoundry2/summary.json`, whose
keys are `thermal, horace, shires, horace2, context, voltage_repeat, mesh`.

Existing:
- **§2:** `power` and `temp` series, with a legend and a time scrub on `CK.bus('pt-time')`.
- **§2 `pvt`:** W against °C, with a view seg, a "fit starts" slider, gap toggles and a readout.
- **§2 `edge-a` / `edge-b`:** with a τ slider.
- **§3 `vmap`:** a die heatmap with a rail seg (minion / SRAM / mesh), a value seg (now / low / high / swing) and a readout. One aifoundry2 idle capture.
- **§1 `#methods`:** a table. The hub's `#gran` already charts it; do not duplicate.

Opportunities:
- **(a) Busy drift per card, with its uncertainty**, S.
  - Section: §2, beside `pvt` and the "power slope under load" KPI.
  - Build: a dot and a ±2·se whisker per card, with reference ticks at the pvt fit (0.80) and the idle-law slope (0.65).
  - Why: it shows at once that aifoundry3's 0.55 W/°C is not pinned down, which today is prose (`#busy-drift`, `#busy-drift-a3`).
  - Data: `context.busy_drift_cards.aifoundry2 = {w_per_c 0.8071, se 0.0129, runs 14, temp_c [82,86]}`, `.aifoundry3 = {0.5472, se 0.1447, runs 7, [57,61]}`.
  - v3: mmb adds a card and repeats; idle adds the per-card law slope.
- **(b) Voltage map across captures and cards, with a repeatability scatter**, M.
  - Build: a card seg and a capture seg (idle / load / load − idle) on `vmap`. Beside it, a scatter of each shire's deviation in capture A against capture B, with an r readout, linked by hover over a bus.
  - Why: the page's hypothesis, that each monitor carries its own offset, is exactly what that scatter tests.
  - Data today: `shires[s].{mnn,sram,noc} = [now,low,high]`, `mesh.layout` and `voltage_repeat[]`. `raw/sp2.bin` and `raw/sp3.bin` hold two more idle maps, which `tools/ettelem/parse_sptrace_voltage.py` can extract.
  - v3: tel TEL-Q (Q2 pass-pair r ≥ 0.6, Q3 card-to-card |r| < 0.45, Q4 load against idle).

### 6. The Horace experiment: `docs/reports/2026-09-20-horace-experiment.html`

It is a folder deploy with GIFs, built from `sources/horace-experiment.*` and
`docs/reports/data/2026-09-21-horace-aifoundry2/report.json`, whose keys are
`grid, patterns, session, leak_w_per_c, runs (46), thermal, power_model, chain, chain_rms, toggles, cold, long, model, structured, validation, before, cards`.

Existing (about 19 frames, mostly aifoundry2):
- **Lede:** `horace-heating.gif`.
- **§1:** `#cl-temp` and `#cl-pow`, every run with a toggle legend; `#perflop`.
- **§3:** `#strip`; `#stack`, with a seg and a readout.
- **§4:** `#thermal`, `#chain`, `#chain-sc`.
- **§5:** `#three`.
- **§6:** `#cold`.
- **§7:** `#long-curves`.
- **§8:** `#cap-sc`, `#leak`, `#step`, `#session`, `#budget`.
- **§9:** `#struct`, and "Price a workload" (a workload select, ranges for minions, launch T and ambient, presets, `#pr-bar`, `#pr-temp`).
- **§10 `#cardsw`:** aifoundry2 against aifoundry3, with a scale slider (0.85–1.05) and calibrate-on-a-pattern.

Opportunities:
- **(a) §10 for N cards, plus "card or temperature?"**, M.
  - Build: a card seg on `#cardsw` with a per-card fitted scale, and a small scatter of fitted scale against launch temperature, one line per card through its two x5 arms.
  - Data today: `cards.patterns[].{values, model, a2, a3, a2_sd, a3_sd}` (the a2/a3 fields are hard-wired to two cards and must become a per-card map), `cards.scale` (0.9236), `cards.launch.{aifoundry2.T 80.96, aifoundry3.T 55.77}` and `cards.idle`.
  - v3: abla and x5. This is the page's main open question.
- **(b) Card picker in "Price a workload"** (#price-a-workload), S.
  - Build: scale the switching power by the chosen card's scale and swap its idle into the board-W readout. Grey out the thermal curve for cards other than aifoundry2.
  - Data: `cards.scale` and `cards.idle.{aifoundry2 36.33, aifoundry3 25.13}`.
- **(c) Replay button on `#cl-temp`/`#cl-pow`**, S, low priority. It sweeps a time cursor and honours `CK.reduced`. Data: `runs[].curve_T` and `curve_P` on `grid`. v3: none.

### 7. Why is it low power?: `docs/reports/2026-09-21-why-low-power.html`

It is built from `sources/why-low-power.*` and `docs/reports/data/2026-09-21-horace-aifoundry2/lowpower-report.json`,
whose keys are `ablation, model, flips, facts, vf, second_card`.

Existing:
- **§2 `#fx`:** a waterfall from the A100 to ET, with ranges for V and clock, presets, an fp32/fp16 seg and a readout.
- **§4 `#stack` and `#leak`:** the C·V²·f + leakage calculator: a workload seg; V, f, T and minion ranges; presets. aifoundry2 only.
- **`#cores`, `#prec` and `#volt`.**

Opportunities:
- **(a) Comparison as a ratio chart** (top 12, item 7), S.
- **(b) Capacitance ladder**, S–M.
  - Section: §3 (#esperanto-s-equation-measured), next to `#cdyn`, which shows 8 of the 30 configurations.
  - Build: a log-x dot strip of C_dyn per minion, dyn/1024/(V²f), for all 30 configurations. Reference lines at Esperanto's 0.040 nF target and the x86 core's 2.2 nF.
  - Data: `ablation.configs` (a dict of 30: `{dyn, minions, unit, per_s, pj_per_unit_dyn, p80, idle}`). aifoundry3 has only `second_card.patterns.{zeros,ones,randn}`.
  - v3: abla (23 configurations on each card) fills a per-card ladder.
- **(c) One card bus for `#cores`, `#prec` and the §4 calculator**, S after the data is restructured (`ablation.configs` holds one card today). v3: abla and idle.

### 8. One hot line stops a shire: `docs/reports/2026-09-22-hot-line.html`

It is built from `sources/hot-line.*` and `docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json`. The pooled
energies are `const POOLED` in the script, copied from `data/2026-09-23-energy-manual/reruns.json`
`hotline_nj_per_op` (`contended, spread, contended_scp, starved, local_only`, each with `per_card`) and `hotline_over_idle_w`.

Existing:
- **§1 `#fair`:** a mesh map with a share-against-hops scatter and a fit, and a seg for 1 or 32 minions per shire. Both cards.
- **§3 `#req`:** `reqN` and `reqP` ranges, a verdict readout and a legend. Both cards.
- **§5 `#pace`.**
- **Tables:** `fairtab`, `localtab`, `wintab`, `placetab`, `pwrtab`.

Opportunities:
- **(a) §2 step-through of the starving shire** (top 12, item 9), M.
- **(b) Per-card knee on `#req`**, S. Add a card seg or per-card marks, and add stops for the new N = 19, 21–23 and P = 9,000–10,500 points. Data: `requesters` and `pace`, fields `card, remote_minions, pace, frac_of_alone, total_ops, host_ops`. v3: lat E-HL1 locates the knee on three cards.
- **(c) An energy dot and interval chart replacing `pwrtab`**, S. Log-x nJ per atomic for the five labels, with per-card dots; it makes the 17× gap between contended and spread visible. Data: `POOLED.nj.*.{mean,lo,hi,n,per_card}`. v3: only COOL c6, aifoundry2.

### 9. Hand it to the next shire: `docs/reports/2026-09-22-on-chip-relay.html`

It is built from `sources/on-chip-relay.*` and `docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json`, whose keys
are `cards, headline{a2,a3}, intensity, size, stages, shires, distance, layout, empty, ring, repeats, bigsize, probe, power`.

Existing:
- **§1 `#samew`:** three bar panels, with per-card pJ in the tooltips.
- **§3 `#size`:** aifoundry2.
- **§4 `#intensity`:** aifoundry2.
- **§5 `#ring`:** a mesh map and a scatter, with an offset seg (1, 2, 4, 8, 16), a longest / mean-hops seg and a readout. Both cards.
- **Tables:** `media`, `power`, `dist`.

Opportunities:
- **(a) Stages and shires panels** (top 12, item 6), S. Then a card seg on `#size` and `#intensity`, M, once the page emits aifoundry3's `sweep.jsonl` rows (`gb_s, stages, shires, stage_bytes, medium`).
- **(b) Relay planner**, M.
  - Build: slider stops at the measured points only (MB per buffer from `size` and `bigsize`, adds per element from `intensity[].work`, stages). A readout gives time and energy per stage for DRAM, next shire and own shire, using the measured GB/s and `POOLED` pJ/B.
  - The readout must say which sweep each number comes from, because the sweeps vary one axis at a time.
  - v3: lat and rl.
- **(c) The ring offset as a slider over d = 1…31**, S, when lat E-RL1's 31 offsets land. Data: `distance[].{hop_distance, mesh_hops, longest.hops, by_card.*.gb_s}`.

### 10. Anatomy of a memory access: `docs/reports/2026-09-19-et-soc1-memory-anatomy.html`

It is standalone, with its data in `const D` in the last script. Raw data: `docs/reports/data/2026-09-19-memprobe-aifoundry2/`.

Existing (aifoundry2):
- **`#trace-one-load` explorer:** the mesh with `mapcolour` and `clickmode` segs, the `#req` and `#home` selects, the `lvl` and `dstate` segs, a readout, `#flame`, `#mstrip` and `#cells`.
- **`#ladder`.**
- **`#l3`:** latency against hops.
- **`#modelerr`.**
- **`#bits`:** with a mode seg.
- **`#refresh`:** with a mode seg.
- **`#pto`.**
- **`#energy`:** with a mode seg. The energy-manual view already holds per-card values in `D.manual`.
- **`#timer`.**

Opportunities:
- **(a) Physical-address decoder** (top 12, item 11), M.
- **(b) Per-card latency models**, M, after mem.
  - Build: a card seg on `#l3`, `#modelerr` and `#ladder`. In the explorer, replace the assumed 12 cycles per hop with measured requesters.
  - Data today: `D.l3[h].{med,hops,n}`, `D.ladder[...]` and `D.modelErr`.
  - v3: mem MEM-P1, P2, P8 and X2 test 110 + 12/hop and 91 + 12/hop on every card. Memory anatomy has 59 TEST claims, the most of any page.
- **(c) Refresh lock-in simulator**, M.
  - Build: a slider for the loop period (300–3000 cycles, default 576) and about 30 loads laid over the 2,325-cycle refresh period, showing why every fourth load is slow.
  - Data: `D.refresh.period_cycles` (2325.4), `D.refresh.curve[].{phase,med,max,p90}` (50 bins), `D.opCycles` and `D.inRefresh`.

### 11. Memory hierarchy: `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html`

It is standalone, with its data in `<script type="application/json" id="memhier-data">`. Raw data:
`docs/reports/data/2026-09-18-memhier-aifoundry2/`.

Existing:
- **`#lat`:** latency against working set, with a clock seg (600 / 700 / 800), a legend and a readout.
- **`#split`.**
- **`#scp-scatter` and `#scp-map`:** with a from-shire seg (0 / 7 / 24 / 31) and a mode seg.
- **`#cmp-lat`, `#cmp-bw`, `#cmp-en`:** log dumbbells against the A100 (`const CMP`).
- **Tables:** `#et-table`, and `#a100-table` in a details block.

Opportunities:
- **(a) Per-level energy dot plot per card** (top 12, item 12), S.
- **(b) Card seg on `#lat` and `#scp-map`**, M, after lat (LAT-M1–M3). Data today: `curves["shire 0"|"shire 24"|"local scratchpad, shire 0"]` as `[bytes,cycles,ns,ghz]`, and `scp_matrix[0|7|24|31]` (32 values each).
- **(c) Mixed-level latency and energy calculator**: sliders for the share of loads hitting L1, L2, L3 and DRAM, giving ns per load and pJ/B for ET against the A100. M. Coordinate it with the energy manual calculator so the two do not overlap.

### 12. On-chip communication: `docs/reports/2026-09-18-et-soc1-on-chip-communication.html`

It is standalone, with its data in `#nocbench-data`, whose keys are
`layout, empty_cells, scp_rows, classes, matrices, sizes, allreduce, primitives, energy, reruns, scp_remote_gbps_600`.

Existing:
- **`#mesh`:** shaded by the 32 B TensorSend round trip from the selected shire, with the `#ring-btn` toggle.
- **`#dist`:** with a size seg and a "hide flag" toggle.
- **`#neigh`.**
- **`#size`:** with a mode seg.
- **`#tree`:** allreduce, with the A100 `grid.sync()` as a dashed line.
- **`#energy`:** with a mode seg and per-card fits.
- **`#layout`:** a pattern seg and a phase range.

Opportunities:
- **(a) "Shade by" seg on `#mesh`** (top 12, item 5), S.
- **(b) Chain-order comparison**, S.
  - Build: turn `#ring-btn` into a seg (none / shire-ID order / one-hop ring) that draws the path on `#mesh`, with a readout of the total and worst-step round trip from the measured pairs.
  - Why: it makes "ID order averages 3.3 hops per boundary, up to 8" concrete.
  - Data: `matrices["matrix-pingpong"].pairs`, `layout` and the script's `RING`.
- **(c) Systolic grain calculator**, S.
  - Section: #what-it-means-for-systolic-and-wavefront-designs.
  - Build: work-per-cell and message-size sliders and a link seg (tree edge / other / mesh hops), with a readout of the communication fraction and the grain k ≈ 10·t_msg/t_cell.
  - Data: `primitives.{tree_hop 68.077, other_hop 114.077, shire_barrier 237.01, allreduce32 432.42}`, the `matrix-pingpong` fit `a` and `b`, and `sizes.stream`.
  - v3: lat changes the constants only.

### 13. Matmul efficiency: `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html`

It is standalone, with its data in `#trace-data` (`trace` [t,W] ×645, `windows`, `idle_w`, `eff.{run,randn,a100}`).
Raw data: `docs/reports/data/2026-09-18-aifoundry2/`.

Existing:
- **Efficiency against the A100:** three log rows, with an `eff-data` seg, an `eff-board` seg, clickable A100 markers and a ratio readout.
- **`#trace`:** with a `trace-pick` seg and a readout.
- aifoundry2 only.

Opportunities:
- **(a) An operand band on the efficiency rows**, S.
  - Build: zeros → randn as a band, and a card seg for fp32.
  - Why: the page's own caveat says the ±1/±2 operands flatter ET.
  - Data: `data/2026-09-23-energy-manual/manual.json` `tensor.rows[].{config, per_s, over_idle_w, idle_w, pj_marginal}` and `tensor.bars.<config>.per_card` (aifoundry3 only for fp32).
  - v3: abla.
- **(b) Results by card**, M, after mmb.
  - Build: small multiples per workload (fp32 / fp16 / int8 / DRAM) of TFLOP/s and board W, with one dot per pass coloured by card, replacing the Results table.
  - Data shape: mmb's `e1/<workload>/results.json`, the same family as `data/2026-09-18-aifoundry2/results.json` `results[].{workload,tflops,mean_w,min_w,idle_before_w}`.

### 14. Sparse compute: `docs/reports/2026-09-18-et-soc1-sparsity.html`

It is standalone, with its data in `#sparsity-data` (`fma, tload, gemv, diverge, energy`). Raw data:
`docs/reports/data/2026-09-18-sparsity-aifoundry3/`.

Existing (aifoundry3 only):
- **`#c-fma`.**
- **`#c-pow`:** with a "later" toggle.
- **`#c-tl`.**
- **Layer explorer:** a zeros range, kernel and reduction segs, `#lx-grid`, `#c-gemv` and `#lx-read`.
- **`#c-lane`, `#c-thr`.**
- **`#c-queue`:** with a range.

Opportunities:
- **(a) Home-shire map for masked DRAM loads**, M.
  - Section: #masked-loads.
  - Build: a step seg over 16 / 8 / 4 / 1 lines that lights the L3 home shires hit (32, 16, 8 and 2), next to bars of chip GB/s and GB/s per lit home.
  - Why: per-home bandwidth stays flat while the total falls: 72.12/32 = 2.25, 37.88/16 = 2.37, 19.31/8 = 2.41, 5.11/2 = 2.56.
  - Data: `tload["dram-all"]` as `[lines, cycles, GB/s]`.
  - v3: lat.
- **(b) One card seg for #zeros, #masked-loads and #layer**, M, after lat and ablb. Sparse compute has 30 TEST claims and is the page that most needs a card view.
- **(c) L2 TB/s against probe length**, S, after lat's e4x (2,000 / 20,000 / 200,000 loads). Reference: `tload["l2-all"][0]` = `[16, 296.8, 2032.81]`.

### 15. Ridge points: `docs/reports/2026-09-18-et-soc1-ridge-points.html`

It is standalone, with its data in `#ridge-data`, whose keys are
`clock_mhz, design_mhz, noc_mhz, minions, scp_bytes_chip, peaks, op_cycles, levels, limits, kernels, energy, a100`.

Existing:
- **`#c-roof` roofline:** precision, clock and level segs, a spec toggle, an intensity range and five kernel rings.
- **`#c-ebal`:** operand and ridge segs, with per-card ranges in the tooltips.
- **`#c-reuse`:** with a mode seg, a precision seg and a range.
- **Tables:** `t-peaks`, `t-ridge`, `t-spec`, `t-a100`, `t-clock`, `t-batch`, `t-energy`.

Opportunities:
- **(a) A100 roofs on `#c-roof`** (top 12, item 8), S.
- **(b) Energy roofline**, M.
  - Section: #energy-balance-points.
  - Build: pJ per FLOP against intensity, E(I) = e_flop + e_byte/I on log-log axes. It shares the `roof-int` slider and level, with operand and card segs and a readout of the data-movement share.
  - Data: `energy.e_flop.{fp32,fp32_ones,fp32_zeros,int8,vec32}.{pj,lo,hi,per_card}` and `energy.e_byte[]` (8 levels, `{name,pj,lo,hi,per_card}`; the L1 row has `probe_pj_by_card` instead).
  - v3: abla, rl and catfull.
- **(c) Kernels and levels by card, plus shared against private tiles**, M, after mmb (ridge-X1) and lat. Committed today: `levels[].measured.rerun.{gbps,passes}`.

### 16. Test drive: `docs/report/index.html`

It is standalone, with its data in `#ladder-data` (`fosdem.rungs[9]`, `tensor`, `peak`).

Existing: `#ladder-chart`, with an order seg, a legend and a readout, and the static `#sgemm-table` (4 rows, aifoundry3).

Opportunity: after lat's `sg` unit, a dot chart of GFLOP/s for each SGEMM size by card, with three reps as dots and a
card seg. S. The caption itself says a later session will re-run these values. Otherwise the page needs nothing.

### 17. Spatial temperature: a brief: `docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html`

It is standalone. Its data:
- `const HOST_TEMP`: `t_s, mean, low, high, sp_max, sp_min`, plus `sessions[]` and `cards{aifoundry2,aifoundry3}`.
- `const SHIRE_MV`: 34 shires × `mnn/sram/noc` as `[value,lo,hi]` mV.

Existing:
- **`#meshgrid`:** with a `grid-view` seg (sensor channel / minion voltage).
- **`#hosttemp`:** a session seg, a time range, a readout and a legend.

Opportunities:
- **(a) Rail and card selector on the mesh**, S.
  - Build: add SRAM and NoC rails to `grid-view` from `SHIRE_MV`, and show [lo, hi] in the tip.
  - v3: add a card seg when tel TEL-Q maps land.
- **(b) Sensor-to-host pipeline diagram**, M.
  - Section: #bottleneck.
  - Build: 35 sensors → truncation to 1 °C → mean and peak-hold → a 5-field host packet. Include a raw-code → °C converter using the page's formula `T = (57400 + 249400*s/4096 − 124700)/1000`, linked to the `ht-time` slider.
  - Why: the page's thesis rests on a C listing today.

No per-shire temperature data exists, which is the brief's point, so a die temperature heatmap is **not** possible.

### 18. L2 mainline starvation: a brief: `docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html`

This is a pointer page with no chartkit and no data. Recommend nothing beyond a link to the hot line §2 diagram
(`…/et-soc1-hot-line#the-thing-that-actually-starves`) once top-12 item 9 exists. Effort S (a link).

### 19. Influence functions on the ET-SoC-1: `docs/reports/2026-09-25-influence-on-et.html`

It is built from `sources/influence-on-et.*` and `docs/reports/data/2026-09-25-influence-on-et/analysis.json`, whose
keys are `generated, producer, kinds, model, owner, s1, duty, kills, s2, dense, pipeline, presets, topk_inserts`.

Existing:
- **`#pipe`:** step costs, with a legend, hover and keynav.
- **§2 Explorer:** N, k, Q and rate ranges; precision, index-location and rule segs; presets; the KPI tiles `#x-size`, `#x-et`, `#x-h`, `#x-be`; `#cap` and `#rate`; a readout.
- **`#s2`:** with a seconds/joules seg.

Opportunities:
- **(a) Measured gather/scatter in S3**, M, after gs.
  - Build: a log-x rate chart per instruction form and level, with the 10–300 G/s estimate band shaded and the 1.92 G/s spread-atomic reference line; a rate / pJ-per-element seg and a card seg.
  - Data today: `model.et.atomics_spread.{ops_per_s 1.92e9, nj 1.16}`.
- **(b) Card picker in the Explorer**, S. It swaps in the chosen card's idle W, because S1's verdict holds "only while the card is kept busy". Data: `model.et.idle_W.{lo 25.13 (aifoundry3), hi 36.33 (aifoundry2)}`, `model.et.sram_pj_B` and `dram_pj_B`. v3: idle and catfull.

## 5. Suggested order of work

1. **Helpers (§3.1, §3.2):** the card registry and the sortable table. Also fix the card colours on the energy manual and Horace.
2. **Items 1, 5, 6, 7, 8 and 12:** all S, all on committed data, independent of v3.
3. **Items 2, 3 and 4:** the card views. Build them now on the two committed cards so the v3 data drops in.
   - Also generalise the hard-coded a2/a3 code: the hub's `cardOf()`, Horace's `cards.patterns[].a2/a3`, and heat-per-mm's and the energy manual's rate lookups.
4. **Items 9, 10 and 11:** the M mechanism diagrams and calculators.
5. **After the v3 reducers land:**
   - the per-card items marked "after";
   - the gs homes (§3.4);
   - Horace §10 for N cards;
   - energy manual §8 for N cards.

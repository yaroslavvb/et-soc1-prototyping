# TODO: changes waiting for the next pass

Written 2026-09-26 from a review of every published page and of the repository by eight AI review agents, each
finding checked against the page text or the data before it was listed (the request is in
[`../findings/02-requests.md`](../findings/02-requests.md)). The live pages equalled their files on that day
([`MIRROR.md`](MIRROR.md), "Last check").

- **Part 0** is for the owner. **Part A** changes published pages, so it waits for the next pass: edit the source
  named in MIRROR.md's "How each page is built", rebuild, run `check_page.sh`, deploy (MIRROR.md, "Deploying one
  page"), run `check-mirror.py`, and commit the page, its sources and this file together. **Part B** is
  repository-only work this pass did not reach.
- The version-3 campaign's own page changes (PLAN3 §1) wait for its data. Do both lists in the same pass so each
  page is rebuilt and deployed once. "PLAN3" marks an item already planned there.
- IDs are the review's: HUB hub · EN energy manual, heat per mm · HOR Horace, why low power · PWR power, DVFS, the
  briefs, the aifoundry1 pages · NOC hot line, relay, on-chip communication, L2 brief · MEM memory anatomy, memory
  hierarchy, ridge points · CMP matmul, sparse compute, test drive, influence · DOC repository docs. Severity:
  **high** (a wrong number a reader would repeat, or a broken rule), medium, low. Kinds: fix, cut, chart.
- Tick an item in the commit that lands it; delete this file when it is empty.

## 0. For the owner

- [ ] **PWR-01 (high, a rule).** CLAUDE.md and AGENT.md §10 forbid other people's accounts or files in this public
  repository, but:
  - "aifoundry1 is fixed" §4 (`2026-09-25-aifoundry1-fix.html:172–186`) tabulates named lab users' home directories,
    with sizes and contents, and says who should delete what.
  - "What is broken on aifoundry1" names one user's home directory four times in its HTML.
  - `data/2026-09-25-aifoundry1/disk-transcript.txt` lists every account's home directory, although that
    directory's README says outputs listing other users were not committed.

  Proposed:
  - Replace §4 with "About 400 GB of the 452 GB pool is user data in home directories; the per-user breakdown went
    to the lab admin."
  - Write "a user's et-platform checkout" for the named paths.
  - Remove the transcript from the tree.

  Rewriting git history, and whether the two pages stay public, are the owner's decisions. Nothing was changed.
- [ ] `scripts/add-lab-user.sh:4` names a root SSH route ("Needs `ssh root@aifoundryN`"), which AGENT.md §10
  excludes. Reword it ("administrative SSH to each machine, the lab admin's"), unless the owner decides otherwise.
- [ ] CLAUDE.md, the owner's file, was not edited:
  - :16 "Every published page is a committed file" → "Every public page is a committed file listed in MIRROR.md
    (private pages are listed there by name only)".
  - :64 runs `make mmbench-check DEVICE=silicon` without `et-who`, the card lock or `timeout 10`.
  - :35–36 lists three of the five upstream clones.

## A. Page changes (rebuild and deploy)

### Across pages

- [ ] **Cards picked by position (NOC-2; medium, and high before the three-card data).**
  - The hot line and the relay take cards by position (`hot-line.script.js:7,56,141,283,500,535`;
    `on-chip-relay.script.js:12,129`). Their analyzers sort the names (`analyze_hotline.py:64,102,117`;
    `analyze_onchip.py:171,179,189,204,212`), so `aifoundry1-c1` would come first.
  - Fix: name the reference card (`'aifoundry2'`) and draw cards in `CK.cardsIn` order.
  - Also two-card-only views:
    - memory anatomy's §6 chart (`workloads/memprobe/report_template.html:1847–1851,1893`, `build_report.py`
      `CARDS`, the pairwise `cards_differ` test);
    - the DVFS `#cardcfg` table (`dvfs-leakage.script.js:373–381`);
    - the spatial brief's "On both cards" (`:1022,1029`);
    - the hub's `#dr` chart (`sync_hub_data.py` copies droop rows for aifoundry2 only).
  - Land this before V3-LAT's three-card data is reduced.
- [ ] **aifoundry1 and aifoundry3 statements (medium).** Since 25 September aifoundry1's two cards work (card 0
  overheats; no sustained work on it). aifoundry3's 0 W TDP is set by a boot service at every boot; it is neither
  flashed nor a firmware property.
  - **DVFS (PWR-03, high; AGENT.md §3).**
    - Byline "(aifoundry1 unavailable)" (`dvfs-leakage.body.html:32`).
    - §3's heading and paragraphs (`:185–196`: "three machines", the `srcversion` story). Keep the id: the power
      page links it.
    - `:231–234` "65 W TDP on all three machines", "its flashed TDP"; §8 `:462–464`. Add a 26 September Versions
      line.
    - For the aifoundry1 paragraph: "**aifoundry1 was not measured for this page.** Until 25 September every
      device-layer tool refused its two cards (`Error unable to evaluate compatibility!`): the module DKMS had built
      there had an empty version string, from a Makefile typo in a stale driver snapshot; nothing reads the
      `srcversion` this page first blamed. A module rebuild fixed it that day. Card 0 (firmware 1.4.1) idles at
      300 MHz and overheats, so it takes no sustained work; card 1 (1.2.0) idles at 600 MHz. Both report aifoundry2's
      65 W TDP and 65 °C threshold."
  - **Horace §10** (`horace-experiment.body.html:521`; PWR-04, HOR-13): "…could not be opened until 25 September
    (an empty driver version string); none of its data is on this page".
  - **The Horace lede** (`:28–29`) and **Why low power §3** (`why-low-power.body.html:106–107`) say aifoundry3's
    firmware holds its clock (HOR-3). Fix: "…whose TDP setting lets the clock rise (a boot service sets
    aifoundry3's to 0 W)".
  - **Matmul, sparse compute and the test drive (CMP-4).**
    - Matmul caveat "One clock point" (`2026-09-18-et-soc1-matmul-efficiency.html:758`).
    - Sparse-compute caveats (`2026-09-18-et-soc1-sparsity.html:906`): "a boot service sets aifoundry3's TDP to
      0 W at every boot".
    - The test drive's footer (`docs/report/index.html:966`): name aifoundry3's patched `libetrt.so` (an -O3 build
      of 836a4ab).
  - **"Both lab cards" and "the second card" (PWR-08).** Name the cards in these bylines and texts: the spatial
    brief (`:681`), the power page (`power-temperature.body.html:18,160`, `script.js:69`), memory hierarchy and
    on-chip communication.
  - **"aifoundry1 is fixed" never says card 0 overheats (PWR-02, high).**
    - Add to the box, §1 and §3: about ten minutes of short test launches took card 0 to 98–102 °C; right after, it
      read 115–117 °C idle and drew 66–71 W at 600 MHz until its firmware dropped it to 300 MHz; card 1 peaked near
      71 °C. Source: `../findings/14-card-behaviour.md`.
    - At `:124,163`: "still counts about one corrected error a second; its kernel log is rate-limited since
      25 September".
- [ ] **Meter refresh period (HUB-01; medium; PLAN3 §1.3(c), V3-TEL).**
  - The pages disagree:
    - Power and temperature: a new value every 156 ms (aifoundry2) and 263 ms (aifoundry3).
    - The hub, the energy manual, heat per mm, Horace, why low power, matmul, sparsity, on-chip communication and
      influence: about 150 and 255 ms (148–164 and 251–260).
    - DVFS, memory anatomy, `05-claims.md:42` and `14-card-behaviour.md:30,83–96`: 133 and 250 ms.
  - Phase-folding the committed logs gives 155.6–156.0 ms and 263.1–264.0 ms, so the power page is right. 133 ms
    is the SP's own pass with no sampler running (one session).
  - Fix:
    - Key `pass_s` by card (0.156, 0.264) in `tools/ettelem/sync_hub_data.py:57–61`.
    - Rewrite hub §4.1, KPI 3 ("156–264 µJ"; board step "1.6–2.6 mJ"), the ladder rows and §6; "twice as slowly"
      becomes "about 1.7 times as slowly".
    - Then the other pages. Alternatively, wait for V3-TEL and apply its value everywhere at once.
- [ ] **Versions notes (cut, about 1,500 words).** Keep one dated line per version and only the corrections that
  changed a claim; the history lives in `../findings/04-artifacts.md`. Pages: the hub (219 words), heat per mm (310),
  the power page (254), DVFS (243), the hot line (186), the spatial brief (169), the relay (153), on-chip
  communication (91), the L2 brief, Horace and why low power.

### Hub · `sources/limits-of-observability.*`

- [ ] HUB-02 (medium). §7 and the session map omit E33 and E34, which were registered on 25 September and measured
  board power.
  - Split the "—" row (`data.json:2310`) into E33 (18 Sep 17:44–17:52, `2026-09-18-memhier-aifoundry2/`), E34
    (18 Sep 19:14–19:28, `2026-09-18-nocbench-aifoundry2/`) and "—" for matmul and sparsity.
  - `body.html:258`: "…E33 and E34 were registered on 25 September". The count becomes 19.
- [ ] HUB-06, CMP-10 (medium). The Influence row (`data.json:516`) says "one narrow case survives"; the page has two
  research items and a measurement. Fix: "none of a big lab's bill does; two narrow research items survive, the
  stronger (S1) scoring a small fixed index held in on-chip SRAM a few queries at a time, and one card experiment
  would settle it."
- [ ] NOC-4 (medium). The hot-line row (`data.json:437`): add "at a steady 600 MHz" to "the host shire's own loads
  fall to 0.02% of normal".
- [ ] HUB-07 (low). §4.1 "as it did for every power page" → "as in every session from 20 September on" (the
  18 September pages polled at 8–12 Hz).
- [ ] HUB-08 (low). The board-power ladder note (`data.json:12`), "freeze the reading" → "slow the reading to about
  two new values a second".
- [ ] HUB-09 (low). The Temperature and voltage row's status: "tooling" → "firmware", with the note "per-shire
  voltages work now (DEBUG trace)".
- [ ] HUB-10 (low), several small fixes:
  - Order the research group newest first (Influence before Sparse compute).
  - §5: "Rungs marked done say where".
  - Add a 26 September Versions line.
  - Glossary: "A hop is one step between neighbouring stops, about 3.72 mm".
  - The E20–E21 row: "unopenable on 22 September; working since 25 September".
  - The DVFS row's date: "21–24 Sep".
- [ ] HOR-12 (low). `data.json:2157` "below half a degree it only bounds the rise" → "below about one degree".
- [ ] EN-6 (low). `data.json:2199` "bars that are mostly the card" → "bars that are about half the card".
- [ ] NOC-10 (low). The hub links the relay's `#the-same-watts-a-thirtieth-of-the-work`
  (`data.json:3482,3502,3522`). Follow the relay's renamed ids (see the relay).
- [ ] Cut (about 740 words):
  - one sentence per index cell;
  - the refresh period stated once (§4.1) instead of ten times;
  - §4.1's starved-meter paragraph;
  - the events note's list of rate sources (`script.js:280–283`);
  - the last sentence of "Three things follow";
  - §4.3's "That is a current meter…";
  - the MDI and ECC details once (§3);
  - the §1 intro and §9;
  - the `#v1` caption's provenance;
  - KPI 3's sub-line.
- [ ] Charts:
  1. **The meter chain as a diagram in §4.1**, the page's central subject, which has no picture. The 12 V input
     feeds three PMBus regulators, then the PMIC (84 values, with running averages at their τ), then the SP loop,
     then ettelem. The seven unmetered rails sit greyed beneath, with the 15.1 W remainder. Data: `power.pmbus_*`,
     `rail_filter.<card>`, `sampler.<card>`, `energy_events.meter`.
  2. **The fit's coefficients per card**, as dot-and-whisker panels beside `#fittab`. Data:
     `power.fit.<card>.coef.*` and `power.checks.fit.<card>.se_hc3.*`.
  3. **The meter starved by the workload**: one strip per card of each burst's median sample latency. Data:
     `catalogue.json` `bursts.<card>[].sampler_median_ms` and `reruns.json` `dropped[]`.

### Energy manual · `sources/energy-manual.*` (markdown through `tools/ettelem/render_*.py`)

- [ ] EN-1 (medium). "Leaving the shire costs more than any hop" (`energy-manual.script.js:555,678`;
  `render_energy_manual.py:363`, `render_catalogue.py:307`). Over 1–6 hops the step is about one hop (0.99 and
  1.06); it is 2 only in the 1–8-hop fit, which the half-traffic 8-hop point pulls down.
  - §4.3: "Leaving the shire costs about one more hop: over 1–6 hops the intercept is 6.5 pJ/B on random data against
    4.3 for the shire's own scratchpad (1.0–1.1 hops' worth on the two cards; the 1–8-hop fit, which the 8-hop point
    pulls down, puts it at 2)."
  - §5: "For messages, leaving the shire is the biggest step, mostly because the same busy cores move 7–34× fewer
    bytes (On-chip communication); for tensor loads it costs about one hop (section 4.3)."
- [ ] EN-3 (low-medium). The idle law was fitted on bins at 64–67 and 81–88 °C, with none between
  (`energy-manual.script.js:180`, `render_energy_manual.py:120`). Say so, and mark the 70 and 80 °C rows as
  interpolated. The same wording appears in Horace §8 and §10 and in why low power (HOR-10).
- [ ] EN-4 (low). The unmetered DRAM term's error bars: 04a and 19-observability give ±1.6/1.4 (OLS), the hub
  ±5.4/4.9 (HC3). Have `fit_unmetered.py` write `se_hc3` and the renderers print it (HUB-03).
- [ ] EN-5 (low). "n = 6" in §9 (`energy-manual.body.html:216`) also covers 4.3's DRAM rows and 4.4's rail split,
  which are aifoundry2 only, n = 3.
  - `09-method.md:72` "(3 for the constant set)" → "(3 for the six DRAM-row configurations, aifoundry2 only)".
  - Drop `render_energy_manual.py:197`'s "(3 where the constant set was not run)".
- [ ] NOC-4 (medium). Related reports (`energy-manual.body.html:243`): add "at a steady 600 MHz" to "fatal to the
  host shire's own loads".
- [ ] NOC-9 (low). `energy-manual.script.js:466` "both draw about 5 W" → "about 5 W while the kernel runs (4.3–4.4 W
  averaged over the burst, Hand it to the next shire §2)".
- [ ] Cut (about 350 words): the §4.2 L1 note (288 words, down to about 170), §7.1's compcap, §10's repeated numbers,
  the §1 idle caption and §9's hot-line bars.
- [ ] Charts:
  1. **§1.1 `#sram` for every card.** `inRange` (`script.js:190–193`) drops aifoundry3's bins, which hides the
     caption's key result: the fit misses aifoundry3 by about 2×.
  2. **§7.2 `#relaycheck` as a bracket chart:** the priced zeros-to-random bar, the measured mean and the per-card
     marks, on a log x axis from 3 to 150 pJ/B.
  3. **§5: rings against mesh distance**, with each card's fit and §4.3's tensor-load wire line.

### Heat per millimetre · `sources/heat-per-mm.*`

- [ ] EN-2 (medium). The lede's "contention adds 40–45% per millimetre on the mesh rail, and 55–65% on board power"
  (`heat-per-mm.script.js:671–673`) mixes two bases. Like for like over one to four hops: "43–47% … on the mesh rail
  and 64–69% on board power". Part B holds the repository copies.
- [ ] Cut (about 470 words): Versions (310 words); §7 "At the voltage it runs at…"; §10 "Not resolved"; §8's
  line example, which the route calculator already shows; the repeats in the §2 and §6 captions.
- [ ] Chart: a card selector on §5's `model`, to show the per-card all-ones excess (5% against 9% on board power).
  Optional: §4's per-step increments beside the link-sharing share.

### The DVFS loop and its leakage · `sources/dvfs-leakage.*`

- [ ] PWR-03 (high). See "aifoundry1 and aifoundry3 statements" above.
- [ ] PWR-05 (medium). §1 says the governor reads the PMIC's averaged wattage. Per `claims-v3/firmware.md:17,32–39`,
  the cards' build (about mid-May 2024) compares the PMIC's instantaneous SoC power with the TDP, and the average
  only decides when a step-down ends.
  - §8: add "…its power tests use the PMIC's instantaneous SoC power; the average decides only when a step-down
    ends".
  - §1: add "(in this source; §8)". Also fix `:461` and Related (`:518`).
  - This rests on firmware.md alone: the extracted source is not committed.
- [ ] PWR-09 (low). Resting temperatures on this page and the power page's lede: "62–74 °C" and "aifoundry3 50–58 °C
  on 22–24 Sep (55–57 °C since 25 Sep)".
- [ ] Cut (about 245 words): verdict row 6 (`script.js:363`); §8's "The 36 transitions…" (`body:424–428`); §5's
  Kanter paragraph; §2's split sentence.
- [ ] Chart: turn `#attrib` into a governor plane per card (plan.md §4(b), not built).
  - Die °C against board W, shaded by the rule's action.
  - `CK.cardSeg` moves the TDP line from 65 W to 0 W.
  - Data: `transitions[]`, `cards.config.<card>.tdp_w`, and `cards.sptrace_aifoundry3.pwr_mw` as a rug.

### Power and temperature telemetry · `sources/power-temperature.*`

- [ ] PWR-10 (low). `script.js:125` says `DM_CMD_SET_FREQUENCY` with power management off "works now, with care",
  but AGENT.md §5 forbids changing a card's clocks. Change it to "lab admin only".
- [ ] Cut (about 105 words): the "Later measurements" box (`body:30–41`) down to the law, its range and pointers;
  the refresh period stated five times and τ three times.
- [ ] Charts:
  1. Tick the fresh readings under `#edge-a` and `#edge-b`: each 10 Hz sample whose `board` value changed, with a
     readout like "124 new values in 20 s, one per ~160 ms".
  2. After V3-TEL: the SP pass per card and sampler.

### The Horace experiment · `sources/horace-experiment.*`

- [ ] HOR-1 (medium). The lede's "the thermal network does not transfer" (`body.html:37`) was never tested. Fix:
  "…in that card's one session; that card's cooling over minutes was not measured, so the thermal network is
  aifoundry2's alone."
- [ ] HOR-5 (low-medium). §1 (`:86–88`) sets aifoundry2's at-launch watts beside aifoundry3's run averages. Give both
  at launch; aifoundry3's are 1.9, 9.7 and 24.9 W.
- [ ] HOR-6 (low). §8 (`:408`) "by 3 to 5 °C on the low-power runs" → "by 3.6 to 5.2 °C on the four runs near the
  flip budget (zeros +0.7 °C)".
- [ ] HOR-7 (low). §2 (`:108`) "(80–86 °C)" → "(82–86 °C)".
- [ ] HOR-8 (low). The "board W at 80 °C" headers (`script.js:96`, the coefficient table, and
  `why-low-power.script.js:60`) → "at launch (81 °C)".
- [ ] HOR-9 (low). §7 (`:320–321`) "(one run each)" → "(one run each in the fit)".
- [ ] HOR-14 (low). Add a 26 September Versions line. Versions also says the checks moved from §2 to Method, but §2
  still carries them.
- [ ] Planned in PLAN3 §1.2 and §1.6: 63.9 against 63.4 W; "5 to 6 W over ones"; the DFT pair's cause; "moves between
  cards unchanged"; "Hadamard like random signs".
- [ ] Cut (about 850 of the page's 12,600 words):
  - §9's CLI transcript → one Method line;
  - §5 items that repeat §1 and §3;
  - §8's fit details → `11-thermal-model.md`;
  - the lede's repeats of the KPIs;
  - one home each for the repeated explanations (aifoundry3's clock, 62 °C, 0.81 against 0.65 W/°C, 8–26%, "not
    resolved");
  - move the §3 and §7 tables into `<details>`.
- [ ] Chart: seconds to 90 °C against switching power.
  - x: flip watts; y: seconds, log scale. One dot per long run (`long[]`); the time-limit runs as arrows; the
    afternoon's matrices as rings.
  - The model curve, and the flip budget as a line.
  - It ties §7 and §8 together and lets the 29-row table fold away.

### Why is it low power? · `sources/why-low-power.*`

- [ ] HOR-4 (low-medium). Voltage and clock, bullet 3 (`:182–184`): 47 W falls within the curve's 44–49 W and 64 W
  lies above it, so "brackets" is wrong.
- [ ] HOR-11 (low). Activity, bullet 2 (`:141–143`): "Idle cores cost nothing measurable" holds only for the fp32
  matmul; the integer loop implies a floor of about 0.24 W.
- [ ] Cut (about 500 words):
  - Voltage bullet 1's 800 MHz note → Caveats;
  - Leakage bullets 1 and 3, whose canonical homes are DVFS §5 and energy manual §1;
  - the §1 prose after the ratio chart;
  - Method's vf.json parenthetical;
  - the 62 and 73 °C readings, once;
  - Caveats bullet 2 → hub §4.2;
  - Versions.
- [ ] Chart: the capacitance ladder (plan.md 7(b), not built). Plot the effective switched capacitance per minion
  for all 30 `ablation.configs` in `lowpower-report.json`, against Esperanto's 0.040 nF target, with aifoundry3's
  three points.

### One hot line stops a shire · `sources/hot-line.*`

- [ ] NOC-1 (medium). The lede (`body.html:9–10`) says "about 24 requesters", against the KPI's 21–24. Fix:
  "between 21 and 24 requesters in one other shire flip it (the bank's arithmetic says 22), fewer than the 32
  minions a shire has."
- [ ] NOC-8 (low). The edge at 22 holds for requesters in shire 1, three hops away. Say so in `#k3sub` and
  `#ineqtext`.
- [ ] Planned in PLAN3: the energy table is aifoundry2 only (V04); "180 M"; "about 1.2 W … read 1.4 W"; the window
  table; "12,000 gives it 85%".
- [ ] Cut (about 330 words): Versions; the §1 caption and the paragraph after it; `#nrgcap`; the L2 bullet in
  Related; §4's impact sentence; §2's clock paragraph.
- [ ] Chart: "Stops, not slows", replacing `#wintab` in §2.
  - Log–log: operations against window. Remote atomics rise 400× while the host stays flat at 384; a dashed line
    shows "if it only slowed".
  - Data: `context.window_independence[]` and the 21 two-second runs,
    `data/2026-09-23-reruns-aifoundry{2,3}-warm/hotline-pass*/runs.jsonl`.

### Hand it to the next shire · `sources/on-chip-relay.*`

- [ ] NOC-6 (low). §5's "about half of what a tensor load … from its own scratchpad costs" sits against §2's
  2.40/2.63 pJ/B.
  - Name the 4.2 pJ tensor load of a random byte (energy manual §4.1).
  - Label §2's figures "(32 B loads, contents not set; §4.2)".
- [ ] NOC-7 (low). §6 (`body.html:118–119`) gives aifoundry2's 15.3× and 13.4× without naming the card. Use §3's
  ranges, or cut the sentence.
- [ ] NOC-10 (low). Rename `#how-far-the-slab-moves-does-not-change-the-bandwidth` and
  `#the-same-watts-a-thirtieth-of-the-work`. Keep empty spans with the old ids, and update the hub's links.
- [ ] Cut (about 230 words):
  - Versions;
  - the §2 table, which duplicates `#samew`: move the chart into §2, the table into `<details>`, and say "within
    about a watt" once;
  - two sentences in §6;
  - §5's caption.
- [ ] Chart: both cards on `#size` (§3) and `#intensity` (§4), from `onchip.json` `size[].by_card` and
  `intensity[].by_card`. Add `by_card` to `bigsize` in `analyze_onchip.py`.

### On-chip communication · `2026-09-18-et-soc1-on-chip-communication.html`

- [ ] Cut (about 80 words): the per-card fit sentence appears twice verbatim (the intro and script line 1500); keep
  the 800 MHz clause once.
- [ ] Charts:
  1. A chain-order comparison (plan.md §12(b), not built). `#ring-btn` becomes a selector (ID order, every k IDs, a
     one-hop ring) that draws the path on `#mesh` and marks its longest step. It shows why the relay's 10-hop 31→0
     step sets its pace.
  2. Lower priority: the systolic grain calculator (plan.md §12(c)).

### L2 mainline starvation (pointer page) · `2026-09-22-et-soc1-l2-mainline-starvation.html`

- [ ] NOC-11 (low). `:78` "1D rings, 2D in barrier-separated phases, and the hardware trees" → "1D rings and the
  hardware trees, and, by the RTL rule (not run), 2D in barrier-separated phases."

### Anatomy of a memory access · `workloads/memprobe/report_template.html`

- [ ] MEM-3 (low). §4 and the explorer (`:858–863,1250`) assume one 4.3 ns burst per 64 B line. The page's own
  source (`docs/research/counters-and-dram.md:335,366`) says two BL16 bursts. With two, the chip's share is about
  28 cycles and the memory shire at most about 63.
- [ ] MEM-4 (low; PLAN3 §1.2). §7 (`:1001–1005`): "lands 11 cycles late" beside "0–10 … 0–9". Apply PLAN3's wording
  to both.
- [ ] Cut (about 205 words): §6's host-log bullet and its "Later measurements" bullet; §9 "Clock domains"; §2's
  closing paragraph.
- [ ] Chart: the memory-shire leg against distance in §4. One dot per home shire on the 104/116/…/176 staircase, with
  a toggle for memory shires one or two hops out.

### Memory hierarchy · `2026-09-18-et-soc1-memory-hierarchy.html`

- [ ] MEM-2 (medium). The page mixes A100 parts, and disagrees with Ridge points.
  - The bandwidth dumbbell (`:1345`) uses the 80 GB HBM2e part (1.77 TB/s), while its latency and energy come from
    the 40 GB part.
  - Ridge points uses 1.40 TB/s.
  - Shared memory is 19.5 TB/s here (`:1343`) and 14.8 on Ridge points.
  - Fix: use 1.40 ("HBM2 40 GB; 1.77 for the 80 GB HBM2e"), and 14.8 or label 19.5 as the peak (source:
    `sources/2026-09-18-a100-memory-hierarchy.md` §6).
- [ ] MEM-6 (low). The readout at `:1188` says "nearest line: 31 at 600 MHz", where 31 counts loads, not a shire.
  Fix: "nearest line: 600 MHz for all 31".
- [ ] Cut (about 240 words):
  - item 5's governor description, and the chase numbers repeated four times;
  - the spec-table note's L1 loop (energy manual §4.2 is canonical);
  - item 6;
  - the "clock was not pinned" caveat.

### Ridge points · `2026-09-18-et-soc1-ridge-points.html`

- [ ] MEM-1 (medium; PLAN3 ridge-68 leaves it optional). "Other limits" (`:765`): four lines in flight at a
  ~290-cycle DRAM round trip give about 0.9 B/cycle, not the measured 1.4. Replace with: "The Erbium DCache
  description allows 4 line requests in flight per minion. At the ~290-cycle DRAM latency single loads see
  (Anatomy), that would give about 0.9 B/cycle, but one minion measured 1.4. Either TensorLoads see a shorter round
  trip or more lines are in flight; the TensorLoad round trip was not measured."
- [ ] MEM-5 (low). `:744` "a 4,500 × 4,500 fp32 block" against the chart's "about 4,580" → "about 4,600 × 4,600",
  or fill it from `reuse-scpmax`.
- [ ] Cut (about 170 words): the shared-32 KB-tile explanation once ("Own shire"); the energy chart's caption and
  table note.
- [ ] Charts:
  1. Bandwidth against the minion clock, in "Which ridge points move with the clock". Plot each launch's GB/s over
     its level's 600 MHz median. Data: `data/2026-09-18-memhier-aifoundry2/energy{,2}/runs.jsonl`, embedded through
     `ridge-points.py --embed`.
  2. The energy roofline (plan.md, not built): pJ per FLOP against intensity, on the `roof-int` slider.

### Matmul efficiency · `2026-09-18-et-soc1-matmul-efficiency.html`

- [ ] CMP-9 (low). The explorer's legend draws the A100 as a ring and a dot, but the chart uses diamonds. Use
  `CK.legend`'s `'diamond'`.
- [ ] Cut (about 330 words):
  - `#eff-sum` (`:1003`), which repeats the Later box;
  - the gp-sdk lab notes (`:796–802`) → one sentence pointing to `patches/README.md`;
  - the Later box's last A100 sentence;
  - the leakage clause in Caveats;
  - the meter parenthetical;
  - the orphan clock sentence.
- [ ] Chart: an operand-and-card band on the efficiency explorer (plan.md §13(a), not built). Show GFLOP/s per W over
  zeros, ones and random, per card, from `manual.json` `tensor.rows`; extend `eff_object` in
  `scripts/mmbench-report-data.py:76–95`. The band makes plain that the int8 verdict flips with the data.

### Sparse compute · `2026-09-18-et-soc1-sparsity.html`

- [ ] CMP-8 (low). Scenario 2 (`:836`) pairs times from the on-chip-reduction kernel with energies from the
  host-reduced one. Label each.
- [ ] Cut (about 220 words): the "Answers to the questions…" section (keep the fp16 rule and the messaging answer);
  two caveats bullets; the Later box's last sentence; the sync costs once (§5).
- [ ] Chart: masked DRAM loads with the home shires lit (plan.md §14(a), not built; data `tload["dram-all"]`),
  labelled as the page's hypothesis.

### Test drive · `docs/report/index.html`

- [ ] CMP-3 (medium). "The tensor-unit rung was reached the same day: 9.5 TFLOP/s … FOSDEM's 10.25 scaled to
  600 MHz" (`:793,950,952`). But 9.5 TFLOP/s is the inner loop on cached tiles, while FOSDEM's rung is a whole
  512×512 matmul.
  - Fix: "The tensor unit's inner loop, on cached tiles, ran the same day at 9.5 TFLOP/s (Matmul efficiency),
    FOSDEM's 10.25 scaled to 600 MHz; a full tensor-unit GEMM has not been run."
  - Change the label (`:987`) to "Tensor-unit loop, cached tiles".

### Spatial temperature brief · `2026-09-22-et-soc1-spatial-temperature-brief.html`

- [ ] Cut (about 100 words): turn the "On both cards." paragraph into a table built from `HOST_TEMP.cards`; trim
  Versions.
- [ ] Chart: the sensor-to-host pipeline in §2 (plan.md §17(b), not built). Draw the 35 sensors, the conversion and
  the host fields; hovering a field lights its inputs.

### Influence functions · `sources/influence-on-et.*`, `data/2026-09-25-influence-on-et/make_analysis.py`

- [ ] CMP-1 (medium). "1.8–2.9× the energy" and S2's "26–42% of fp32 peak" use the matmul run's board power, on
  operands with all-zero mantissas. Gradients are random-like.
  - With `manual.json` `tensor.rows` `*_randn` (fp16 61.1 W, fp32 63.9 W): "1.9–3.1×" and "30–48%" (fp16 14–23%).
    Say "on random data (aifoundry2, 80 °C)".
  - Locations: `make_analysis.py:318–337,343`; `body.html:40,63,262,299,369`.
- [ ] CMP-2 (medium). "7.5 µs … 2.2 TB/s, 9% under" divides cycles by the host's wall-time `ghz` (0.583), a field
  meant for launches of 0.1 s or more. At 600 MHz the time is 7.31 µs, and the energies come from the host-reduced
  kernel at 7.36 µs.
  - Fix: `t_s = 1/sp["per_s"]`; "7.4 µs for 250 µJ"; "2.3 TB/s, 7% under".
  - Locations: `make_analysis.py:97`; `body.html:47,310,354`.
- [ ] CMP-5 (low-medium). "the chip's 72 MB of on-chip SRAM" → "the chip's scratchpads (72 MB usable of 80 MB)"
  (`body.html:42,232`; `script.js:244,280`; `make_analysis.py:353`).
- [ ] CMP-6 (low). The per-op energies subtract the superseded 30.61 W idle. Use `idle_before_w`: int8 0.39 pJ, fp16
  1.41 pJ.
- [ ] CMP-7 (low). The lede and KPI show `s1.l2_case.lead` with `data-dp="0"` ("3–4×") where S1 prints 2.6–3.9×. Use
  `data-dp="1"`.
- [ ] Cut (about 300 words):
  - §6 "Corrections folded in…" → the data README;
  - the H100 energy caveat twice, not four times;
  - "What 'sparse-friendly' buys here";
  - S1's "Value to a big lab".
- [ ] Chart: S1's lead against queries per pass. A log-log plot of mJ per query against Q, for the ET card and the
  H100, from `s1.parity_*.table[]`, with the crossings marked.

### The aifoundry1 pages (standalone HTML)

- [ ] PWR-01 and PWR-02: see part 0 and "aifoundry1 and aifoundry3 statements" above.
- [ ] Cut (about 650 words): the fix page's §4 (with PWR-01); the troubleshooting page's lede (284 words), which
  repeats its four boxes; §1's procedure into `<details>`.

## B. Repository-only work not done in this pass

### After the campaign (every block hashes `tools/claims-v3/`)

- [ ] `tools/claims-v3/lib.sh`:
  - `:17–18`: aifoundry3 has system numpy, and all three hosts have a venv, since 25 September.
  - `:3–4`: add aifoundry1.
  - `:7`: note amendment A3.
  - `:52`: the data path `collect.sh` writes.
  - `:70–71`: a sudo detail (AGENT.md §10) → a variable.
- [ ] With the results:
  - Register E35–E48 and widen "Cite as".
  - Number the 25–26 September requests.
  - Add a results series to `CLAIM_SERIES` in `tools/ettelem/sync_hub_data.py`.
  - Update AGENT.md §3 and getting-started.
  - Rebuild aifoundry1's `build/<workload>` directories with the g3log fix.

### The knowledge base against the version-3 pages (the page holds)

`docs/findings/` predates the version-3 first pass (`0399048`). This pass fixed the summaries in its commit and
flagged the rest at the top of `../findings/README.md`.

- [ ] `05-claims.md`:
  - `:207` idle law on aifoundry3: +0.61 W, sd 0.05, over 16 sessions; −0.18 W over 25 on aifoundry2.
  - Add rows for the two-day governor figures (275 changes; a median first change of 0.73 s over 31 starts; a reset
    about 1.0 s after a block ends; a meter lag of 0.3 s) and for the power page's 156/263/135 ms; fix `:42`.
  - `:341–342`: heat per mm's all-ones excess and its 256 B pattern (heat-05b, heat-64).
  - PLAN3 §1.2's heat-32, heat-69, heat-75, energy-manual-100, -105 and -44.
  - `:398`: Ridge energy balance, per card.
  - `:315` and `:362`: per-card L1 and L2; "within 0.8%".
  - `:320–321`: the droop per card (0.865 and 0.835 mV/W; 0.029 and 0.013; 0.070 and 0.137).
  - `:57`, `:135`, `:433` (HOR-2, HOR-R3).
  - Add rows for memory anatomy (E1, E2): 110 + 12/hop, 91 + 12/hop, ±3 cycles for 97% of lines, tRCD, +40, the
    refresh, the counter carry.
  - Register the 18 September matmul, sparsity and SGEMM sessions (9.5 TFLOP/s, 168 GFLOP/s per W, 127 GFLOP/s) as
    E50–E52; E35–E48 are reserved.
- [ ] The topic files:
  - `17-hot-line.md:10–12,53–54,93–95,134–135,138`: "at a steady 600 MHz", seventeen loads per minion, 192–240, the
    barrier's single development run.
  - `18-on-chip-relay.md:96,119–120`: r = −0.3; "a path with no ready-flag handshake".
  - `16-dvfs-and-leakage.md:24–25,33,38,89,151,171–172`.
  - `11-thermal-model.md:33–34,86,96–97,134–135`.
  - `13-why-low-power.md:17–18,25,105–106,165`.
  - `12-heat-management.md:49–51,71`.
  - `10-data-dependent-power.md:21–28,52,60`.
  - `14-card-behaviour.md:30,83–96` (the refresh) and `:270` (a power cycle).
  - `19-observability-and-the-unmetered.md:17,32–35,64–70,84`.
  - `20-heat-per-mm.md`: contention, all-ones, the 256 B pattern.
  - `15-earlier-findings.md:25,35,44,85–91,95`.
  - `03-experiments.md:69–70,82,302,430,822–838,974`.
  - `01-resources.md:45,84–86,150–152,160,198–200`.
  - `docs/et-soc1-notes.md:66–67,71–74,88,93,166,169,175,258`.
  - `docs/research/counters-and-dram.md:335`.
- [ ] `README.md`:
  - "0.75 pJ/B on zeros and 1.81 on random … (2.3 over 1–6 hops" → the manual's 0.6–0.75, 1.7–1.8 and 2.1–2.3.
  - "a flat 8%" → "about 8% (3–10% per pattern)".
  - "repeats the whole experiment" → "repeats the 7 s runs".
  - "on a different afternoon" → "in a separate session that afternoon". The same slip is in `03-experiments.md:302`,
    `../findings/README.md:84` and `05-claims.md:120`.
  - "5% on SRAM" (also in getting-started:81).

### Records and commands

- [ ] `04-artifacts.md`:
  - rows in the Commits table after `bde52e0`;
  - a tools row for `tools/g3log-race/race.cpp` (E49);
  - A16's `sync_hub_data.py` blocks `power.checks` and `claims_status`;
  - A4's "six versions" (version 6 is only the 7 s runs);
  - A2's row, which stops at 24 September;
  - the card registry and `sortTable` in the chartkit note.
- [ ] The claims-v3 README's file table omits AMENDMENTS.md.
- [ ] `getting-started.md`:
  - `:221` "(51–54 °C before)" → "(53–54 °C before; amendment A5)";
  - `:360–361`: the `06605ab` pin, not the patch, avoids the Erbium problem;
  - `:423` needs `python3`, and `:424`'s input list lacks `plan3.json.gz`;
  - `:173`: FOSDEM's 10.25 came from software-pipelining the tensor unit;
  - `:78`: up-steps at readings up to 66 °C.
- [ ] Card commands without `et-who`, the card lock or `timeout 10`:
  - getting-started `:268,276,292–293`;
  - `README.md` "make run-hello DEVICE=silicon" (it also needs `deploy-lab-gpsdk.sh`);
  - the memhier, nocbench and sparsity READMEs ("Check `uptime`, `who` and `ps` first").
- [ ] Clone lists (`README.md:208`, getting-started:188) omit et-testdrive and etTopoScan. `scripts/vm:4` gives
  `make -C hello run` for `make run-hello`.
- [ ] `01-resources.md`: R5's etiquette → AGENT.md §5; R10's resolver note (lab-access.md); R12, the L2 brief, is a
  pointer page since 25 September.

### Concision in the repository (about 4,000 words)

- [ ] `README.md:21–182`, the per-report prose (about 2,380 words): one sentence and a 21-row table (page, code, raw
  data) built from MIRROR.md and getting-started §8. Keep the only copy of the hub's survey-source location.
- [ ] `getting-started.md`, replacing duplicates with links to their canonical homes:
  - "Earlier work"'s "Done" (about 650 words) and the dated result bullets of "Where things stand" (about 650);
  - the etiquette (AGENT.md §5);
  - the publishing rules (MIRROR.md);
  - the card table (14-card-behaviour);
  - Tailscale (lab-access);
  - the energy-manual chain (04-artifacts A16).
- [ ] AGENT.md §1 and §9: point to getting-started and MIRROR.md instead of keeping dated snapshots.

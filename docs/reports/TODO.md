# TODO: changes waiting for the next pass

Written 2026-09-26 from a review of every published page and of the repository by eight AI review agents, each
finding checked against the page text or the data before it was listed (the request is in
[`../findings/02-requests.md`](../findings/02-requests.md)). The live pages equalled their files on that day
([`MIRROR.md`](MIRROR.md), "Last check").

**Status, 30 September 2026 (13:05 PDT):** 134 items: 108 done, 6 superseded by the version-3 results, 20 open (four
of them the owner's, in part 0). The review of 26 September listed 110; the lab re-check of 27 September added 7, the
major pass of 28–29 September (Q65) 9 more, the sparse parity work (Q66, E59) its 6 next steps and the owner's call on
its page, and the third card's runs of 29 September one open result.

- **Part 0** is for the owner. **Part A** changes published pages, so it waits for the next pass: edit the source
  named in MIRROR.md's "How each page is built", rebuild, run `check_page.sh`, deploy (MIRROR.md, "Deploying one
  page"), run `check-mirror.py`, and commit the page, its sources and this file together. **Part B** is
  repository-only work this pass did not reach. **Part C** is the card work and records that the major pass of
  28–29 September (Q65) left: DV2's reduction and the third card's pcie2, nocr and memp2 (both done on 29 September),
  tau on the third card, and the open results. **Part D** is the sparse
  parity solver's next steps (Q66, E59).
- **Reconciled on 27 September** with the merge `0cfc742` (the three-card pages of 26 September, this review's chart
  and collapsible-depth passes, and E48 on the pages) and the review pass after it, then checked item by item against
  the tree the same day: a ticked item says "done 27 Sep" or "superseded 27 Sep" and where; a partly landed item stays
  open and says what is left. The version-3 campaign's data (E35–E48) is in, so no item waits for it any more. "PLAN3"
  marks an item planned in PLAN3 §1.
- IDs are the review's: HUB hub · EN energy manual, heat per mm · HOR Horace, why low power · PWR power, DVFS, the
  briefs, the aifoundry1 pages · NOC hot line, relay, on-chip communication, L2 brief · MEM memory anatomy, memory
  hierarchy, ridge points · CMP matmul, sparse compute, test drive, influence · DOC repository docs. Severity:
  **high** (a wrong number a reader would repeat, or a broken rule), medium, low. Kinds: fix, cut, chart.
- Tick an item in the commit that lands it; delete this file when it is empty.

## 0. For the owner

- [x] **PWR-01 (high, a rule).** CLAUDE.md and AGENT.md §10 forbid other people's accounts or files in this public
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

  Done 27 Sep, by the owner's decision: the two aifoundry1 pages and the disk transcript stay public for now; the
  proposed changes were not made.

- [ ] `scripts/add-lab-user.sh:4` names an administrative SSH route word for word, which AGENT.md §10
  excludes. Reword it ("administrative SSH to each machine, the lab admin's"), unless the owner decides otherwise.
  Open on 27 September: the owner's.

- [ ] CLAUDE.md, the owner's file, was not edited (open on 27 September: the owner's):
  - :16 "Every published page is a committed file" → "Every public page is a committed file listed in MIRROR.md
    (private pages are listed there by name only)".
  - :64 runs `make mmbench-check DEVICE=silicon` without `et-who`, the card lock or `timeout 10`.
  - :35–36 lists three of the five upstream clones.

- [ ] **The lab report's remaining fixes (its section 2.8), waiting for the owner (Q65).** On 28 September the
  session's permission check refused them, so the owner runs each or allows it. aifoundry1 already has U20, U22, U24
  and U27 (20:51 PDT, owner-approved; [`../lab-access.md`](../lab-access.md), "aifoundry1's lab fixes of
  28 September").
  - U16: install `et-reset` on the three hosts (`tools/lab/README.md`, "et-reset").
  - U17: the ZFS pool scrub.
  - U18: `et-lab-health` rev 3 and its daily timer (`tools/lab/README.md`, "The daily timer").
  - U19 and U26: the reboots.
  - U20 on aifoundry2 and aifoundry3: bluetooth, cups-browsed and the firmware-updater snap disabled, apport's
    core-dump hook masked.
  - U22 on aifoundry2 and aifoundry3: the login-service setting aifoundry1 got.
  - U23 on aifoundry3: its login-service item.
  - U24 on aifoundry2 and aifoundry3: the other two machines pinned to their tailnet names in `/etc/hosts`.
  - U25: the PCIe Gen3 link test of aifoundry1's card 0.
  - U27 on aifoundry2 and aifoundry3: boot to the text console (the headless default target).

- [ ] **NV's first voltage write (E54), waiting for the owner.** The probe block on aifoundry3
  (`tools/claims-v3/nv/README.md`: `block.sh 1 --probe`, detached; 540 mV, then 600, then the restore to 485, about
  a minute) is NV's first command that changes the card's state. The session's permission check refused it on
  28 September (predictions frozen in `4312253`; the read-only probe at 22:54 PDT found BL2 0.20.0 and the NoC at
  485 mV), so the owner runs it or allows it. The smoke and the development passes follow on aifoundry3, then the
  validation on aifoundry2 (DV2's validation there ended on 29 September; part C).

- [x] **The sparse parity page is public** (`et-soc1-sparse-parity`, space `a6212e3c…`): the owner made it public on
  29 September (Q67), and the hub's link went out with it.

## A. Page changes (rebuild and deploy)

**Charts: done on 26–27 September** (commits `6f207ce` to `974d120`, then the merge `0cfc742`). Every "Chart"/"Charts"
item below is built, except two: heat per mm's optional per-step increments and a chart of the power page's SP pass
per card (V3-TEL's values are on that page as text). On-chip communication's grain calculator was added in the merge.
Many fix and cut items landed in the merge too; those are ticked below.

### Across pages

- [x] **Cards picked by position (NOC-2; medium, and high before the three-card data).**
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
  - Done 27 Sep: the hot line and the relay order cards through `CK.cardsIn` with aifoundry2 named; memory anatomy's §6
    chart, the DVFS `#cardcfg` table, the spatial brief's per-card table and the hub's droop chart take every card in
    the data.
- [x] **aifoundry1 and aifoundry3 statements (medium).** Since 25 September aifoundry1's two cards work (card 0
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
  - Done 27 Sep: DVFS (byline, §3 "on three cards", the aifoundry1 paragraph, the 26 September Versions line), Horace
    §10 (aifoundry1-c1 measured there), the boot-service wording on Horace, why low power, matmul, sparse compute and
    the test drive, the cards named (PWR-08; the power page's last "Both cards" on 27 September), and PWR-02 on
    27 September (a dated update box on both aifoundry1 pages; the PCIe line's rate-limited log).
  - **"aifoundry1 is fixed" never says card 0 overheats (PWR-02, high).**
    - Add to the box, §1 and §3: about ten minutes of short test launches took card 0 to 98–102 °C; right after, it
      read 115–117 °C idle and drew 66–71 W at 600 MHz until its firmware dropped it to 300 MHz; card 1 peaked near
      71 °C. Source: `../findings/14-card-behaviour.md`.
    - At `:124,163`: "still counts about one corrected error a second; its kernel log is rate-limited since
      25 September".
- [x] **Meter refresh period (HUB-01; medium; PLAN3 §1.3(c), V3-TEL).** Done 27 Sep: every page gives the period per
  card with its basis — while ettelem samples at 10 Hz about 156 ms on aifoundry2, 158 on aifoundry1-c1 and 263 on
  aifoundry3 (phase-folded logs; E41), with nothing polling 133, 135 and 224 ms (E41). The merge brought the other
  pages and the knowledge base to it; the hub (KPI 3 "156–263 µJ", §4.1) followed in the review pass of 27 September,
  which tells the SP trace's own pass (160–266 ms) apart. The review's first reading, kept for the record:
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
    - Then the other pages.
- [x] **Versions notes (cut, about 1,500 words).** Keep one dated line per version and only the corrections that
  changed a claim; the history lives in `../findings/04-artifacts.md`. Pages: the hub (219 words), heat per mm (310),
  the power page (254), DVFS (243), the hot line (186), the spatial brief (169), the relay (153), on-chip
  communication (91), the L2 brief, Horace and why low power.
  Done 28 Sep (`031c723`) on every page listed: one line per date with the corrections that changed a claim, and a
  link to the source's history on GitHub. The full history is each source's git history, which `04-artifacts.md`
  now points to; it is not in `04-artifacts.md` itself, as this item first said.

### Hub · `sources/limits-of-observability.*`

- [x] HUB-02 (medium). §7 and the session map omit E33 and E34, which were registered on 25 September and measured
  board power. Done 27 Sep: hub §7 and the session map (rows E33 and E34).
  - Split the "—" row (`data.json:2310`) into E33 (18 Sep 17:44–17:52, `2026-09-18-memhier-aifoundry2/`), E34
    (18 Sep 19:14–19:28, `2026-09-18-nocbench-aifoundry2/`) and "—" for matmul and sparsity.
  - `body.html:258`: "…E33 and E34 were registered on 25 September". The count becomes 19.
- [x] HUB-06, CMP-10 (medium). The Influence row (`data.json:516`) says "one narrow case survives"; the page has two
  research items and a measurement. Fix: "none of a big lab's bill does; two narrow research items survive, the
  stronger (S1) scoring a small fixed index held in on-chip SRAM a few queries at a time, and one card experiment
  would settle it." Done 27 Sep: the index's Influence row.
- [x] NOC-4 (medium). The hot-line row (`data.json:437`): add "at a steady 600 MHz" to "the host shire's own loads
  fall to 0.02% of normal". Done 27 Sep: the index's hot-line row.
- [x] HUB-07 (low). §4.1 "as it did for every power page" → "as in every session from 20 September on" (the
  18 September pages polled at 8–12 Hz). Done 27 Sep: §4.1.
- [x] HUB-08 (low). The board-power ladder note (`data.json:12`), "freeze the reading" → "slow the reading to about
  two new values a second". Done 27 Sep: the ladder note.
- [x] HUB-09 (low). The Temperature and voltage row's status: "tooling" → "firmware", with the note "per-shire
  voltages work now (DEBUG trace)". Done 27 Sep: the row's status is firmware (`needs_fw_change`), with that note.
- [x] HUB-10 (low), several small fixes (done 27 Sep: all six, on the hub):
  - Order the research group newest first (Influence before Sparse compute).
  - §5: "Rungs marked done say where".
  - Add a 26 September Versions line.
  - Glossary: "A hop is one step between neighbouring stops, about 3.72 mm".
  - The E20–E21 row: "unopenable on 22 September; working since 25 September".
  - The DVFS row's date: "21–24 Sep".
- [x] HOR-12 (low). `data.json:2157` "below half a degree it only bounds the rise" → "below about one degree".
  Done 27 Sep: the hub's data.
- [x] EN-6 (low). `data.json:2199` "bars that are mostly the card" → "bars that are about half the card".
  Superseded 27 Sep: rung 10 was rewritten on three cards, and the phrase is gone.
- [x] NOC-10 (low). The hub links the relay's `#the-same-watts-a-thirtieth-of-the-work`
  (`data.json:3482,3502,3522`). Follow the relay's renamed ids (see the relay). Done 27 Sep: all three link
  `#power-within-a-watt-a-thirtieth-of-the-work`.
- [x] Cut (about 740 words):
  Done 28 Sep (`031c723`).
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
- [x] Charts (done 27 Sep: `#chain` in §4.1, `#coef` beside `#fittab`, `#starve`):
  1. **The meter chain as a diagram in §4.1**, the page's central subject, which has no picture. The 12 V input
     feeds three PMBus regulators, then the PMIC (84 values, with running averages at their τ), then the SP loop,
     then ettelem. The seven unmetered rails sit greyed beneath, with the 15.1 W remainder. Data: `power.pmbus_*`,
     `rail_filter.<card>`, `sampler.<card>`, `energy_events.meter`.
  2. **The fit's coefficients per card**, as dot-and-whisker panels beside `#fittab`. Data:
     `power.fit.<card>.coef.*` and `power.checks.fit.<card>.se_hc3.*`.
  3. **The meter starved by the workload**: one strip per card of each burst's median sample latency. Data:
     `catalogue.json` `bursts.<card>[].sampler_median_ms` and `reruns.json` `dropped[]`.

### Energy manual · `sources/energy-manual.*` (markdown through `tools/ettelem/render_*.py`)

- [x] EN-1 (medium). "Leaving the shire costs more than any hop" (`energy-manual.script.js:555,678`;
  `render_energy_manual.py:363`, `render_catalogue.py:307`). Over 1–6 hops the step is about one hop (0.99 and
  1.06); it is 2 only in the 1–8-hop fit, which the half-traffic 8-hop point pulls down.
  - §4.3: "Leaving the shire costs about one more hop: over 1–6 hops the intercept is 6.5 pJ/B on random data against
    4.3 for the shire's own scratchpad (1.0–1.1 hops' worth on the two cards; the 1–8-hop fit, which the 8-hop point
    pulls down, puts it at 2)."
  - §5: "For messages, leaving the shire is the biggest step, mostly because the same busy cores move 7–34× fewer
    bytes (On-chip communication); for tensor loads it costs about one hop (section 4.3)."
  - Done 27 Sep: §4.3 and §5 ("about one more hop"), and the two renderers.
- [x] EN-3 (low-medium). The idle law was fitted on bins at 64–67 and 81–88 °C, with none between
  (`energy-manual.script.js:180`, `render_energy_manual.py:120`). Say so, and mark the 70 and 80 °C rows as
  interpolated. The same wording appears in Horace §8 and §10 and in why low power (HOR-10). Done 27 Sep: §1's
  caption and `01-at-rest.md` (the gap's rows marked interpolated); Horace §8 and §10 and why low power say "none
  between".
- [ ] EN-4 (low). The unmetered DRAM term's error bars: 04a and 19-observability give ±1.6/1.4 (OLS), the hub
  ±5.4/4.9 (HC3). Have `fit_unmetered.py` write `se_hc3` and the renderers print it (HUB-03). Still open on
  27 September: `fit_unmetered.py` writes no `se_hc3`, and 19-observability still gives ±1.6/1.4.
- [x] EN-5 (low). Superseded 27 Sep by the three-card catalogue (§9's bars and 09-method.md were rewritten).
  "n = 6" in §9 (`energy-manual.body.html:216`) also covers 4.3's DRAM rows and 4.4's rail split, which are
  aifoundry2 only, n = 3.
  - `09-method.md:72` "(3 for the constant set)" → "(3 for the six DRAM-row configurations, aifoundry2 only)".
  - Drop `render_energy_manual.py:197`'s "(3 where the constant set was not run)".
- [x] NOC-4 (medium). Related reports (`energy-manual.body.html:243`): add "at a steady 600 MHz" to "fatal to the
  host shire's own loads". Done 27 Sep: Related reports.
- [x] NOC-9 (low). `energy-manual.script.js:466` "both draw about 5 W" → "about 5 W while the kernel runs (4.3–4.4 W
  averaged over the burst, Hand it to the next shire §2)". Done 27 Sep: §7.2 ("while the kernel runs", with the
  burst averages).
- [x] Cut (about 350 words): the §4.2 L1 note (288 words, down to about 170), §7.1's compcap, §10's repeated numbers,
  the §1 idle caption and §9's hot-line bars. Partly landed: §7.1's compcap (27 September).
  Done 28 Sep (`031c723`).
- [x] Charts (done 27 Sep: `#sram`, `#relaycheck`, `#rings`):
  1. **§1.1 `#sram` for every card.** `inRange` (`script.js:190–193`) drops aifoundry3's bins, which hides the
     caption's key result: the fit misses aifoundry3 by about 2×.
  2. **§7.2 `#relaycheck` as a bracket chart:** the priced zeros-to-random bar, the measured mean and the per-card
     marks, on a log x axis from 3 to 150 pJ/B.
  3. **§5: rings against mesh distance**, with each card's fit and §4.3's tensor-load wire line.

### Heat per millimetre · `sources/heat-per-mm.*`

- [x] EN-2 (medium). The lede's "contention adds 40–45% per millimetre on the mesh rail, and 55–65% on board power"
  (`heat-per-mm.script.js:671–673`) mixes two bases. Like for like over one to four hops: "43–47% … on the mesh rail
  and 64–69% on board power". Part B holds the repository copies. Done 27 Sep: the lede says "like for like over
  one to four hops", per card from the three-card run.
- [x] Cut (about 470 words): Versions (310 words); §7 "At the voltage it runs at…"; §10 "Not resolved"; §8's
  line example, which the route calculator already shows; the repeats in the §2 and §6 captions.
  Done 28 Sep (`031c723`).
- [x] Chart: a card selector on §5's `model`, to show the per-card all-ones excess (5% against 9% on board power).
  Done 27 Sep: `#modelcard`.
- [x] Optional chart: §4's per-step increments beside the link-sharing share.
  Done 28 Sep (`031c723`): `#incr`.
- [x] **The routing order (E56):** the route map drew every leg x first, "as the analysis assumes", and said the
  order was not measured; read data travel y first on both cards tested. Default the map to y first, relabel the
  toggle, and quote the shares under y first (`wire.json` `checks.link_sharing.<cfg>.shared_link_hop_fraction_yx`:
  0 / 22 / 30 / 55 / 78% at 1 / 2 / 3 / 4 / 6 hops, against 0 / 22 / 32 / 55 / 72% under x first).
  Done 29 Sep (the major pass): `heat-per-mm.script.js`; `../findings/20-heat-per-mm.md` notes it.

### The DVFS loop and its leakage · `sources/dvfs-leakage.*`

- [x] PWR-03 (high). See "aifoundry1 and aifoundry3 statements" above. Done 27 Sep: the byline, §3 and its
  aifoundry1 box.
- [x] PWR-05 (medium). §1 says the governor reads the PMIC's averaged wattage. Per `claims-v3/firmware.md:17,32–39`,
  the cards' build (about mid-May 2024) compares the PMIC's instantaneous SoC power with the TDP, and the average
  only decides when a step-down ends.
  - §8: add "…its power tests use the PMIC's instantaneous SoC power; the average decides only when a step-down
    ends".
  - §1: add "(in this source; §8)". Also fix `:461` and Related (`:518`).
  - This rests on firmware.md alone: the extracted source is not committed.
  - Done 27 Sep: §1 and §8 (the May 2024 build tests the PMIC's instantaneous reading).
- [x] PWR-09 (low). Resting temperatures on this page and the power page's lede: "62–74 °C" and "aifoundry3 50–58 °C
  on 22–24 Sep (55–57 °C since 25 Sep)". Done 27 Sep: both pages.
- [x] Cut (about 245 words): verdict row 6 (`script.js:363`); §8's "The 36 transitions…" (`body:424–428`); §5's
  Kanter paragraph; §2's split sentence. Partly landed: verdict row 6 (27 September; the page checks five claims).
  Done 28 Sep (`031c723`).
- [x] Chart: turn `#attrib` into a governor plane per card (plan.md §4(b)). Done 27 Sep: `#attrib` with
  `#attrib-card`.
  - Die °C against board W, shaded by the rule's action.
  - `CK.cardSeg` moves the TDP line from 65 W to 0 W.
  - Data: `transitions[]`, `cards.config.<card>.tdp_w`, and `cards.sptrace_aifoundry3.pwr_mw` as a rug.

### Power and temperature telemetry · `sources/power-temperature.*`

- [x] PWR-10 (low). `script.js:125` says `DM_CMD_SET_FREQUENCY` with power management off "works now, with care",
  but AGENT.md §5 forbids changing a card's clocks. Change it to "lab admin only". Done 27 Sep: the
  "Static against dynamic power" row.
- [x] Cut (about 105 words): the "Later measurements" box (`body:30–41`) down to the law, its range and pointers;
  the refresh period stated five times and τ three times.
  Done 28 Sep (`031c723`).
- [x] Chart: tick the fresh readings under `#edge-a` and `#edge-b`: each 10 Hz sample whose `board` value changed,
  with a readout like "124 new values in 20 s, one per ~160 ms". Done 27 Sep.
- [x] Chart: the SP pass per card and sampler (V3-TEL's values are in; the page gives them as text).
  Done: built on 27 Sep as `#askcost`, closed in the sweep of 28 Sep (`031c723`).

### The Horace experiment · `sources/horace-experiment.*`

- [x] HOR-1 (medium). The lede's "the thermal network does not transfer" (`body.html:37`) was never tested. Fix:
  "…in that card's one session; that card's cooling over minutes was not measured, so the thermal network is
  aifoundry2's alone." Done 27 Sep: the lede.
- [x] HOR-5 (low-medium). §1 (`:86–88`) sets aifoundry2's at-launch watts beside aifoundry3's run averages. Give both
  at launch; aifoundry3's are 1.9, 9.7 and 24.9 W. Done 27 Sep: §1.
- [x] HOR-6 (low). §8 (`:408`) "by 3 to 5 °C on the low-power runs" → "by 3.6 to 5.2 °C on the four runs near the
  flip budget (zeros +0.7 °C)". Done 27 Sep: §8.
- [x] HOR-7 (low). §2 (`:108`) "(80–86 °C)" → "(82–86 °C)". Done 27 Sep: §2.
- [x] HOR-8 (low). The "board W at 80 °C" headers (`script.js:96`, the coefficient table, and
  `why-low-power.script.js:60`) → "at launch (81 °C)". Done 27 Sep: `#tbl` and why low power's `#cdyn`.
- [x] HOR-9 (low). §7 (`:320–321`) "(one run each)" → "(one run each in the fit)". Done 27 Sep: §7.
- [x] HOR-14 (low). Add a 26 September Versions line. Versions also says the checks moved from §2 to Method, but §2
  still carries them. Done 27 Sep: Versions (the 27 September line).
- [x] Planned in PLAN3 §1.2 and §1.6: 63.9 against 63.4 W; "5 to 6 W over ones"; the DFT pair's cause; "moves between
  cards unchanged"; "Hadamard like random signs". Superseded 27 Sep by the version-3 results (E38): why low power's
  Method says why the pages quote 63.9 and 63.4 W (two leakage slopes); "5 to 6 W over ones" gives random signs' 4.8
  to 5.1 W on three cards; the DFT pair was re-measured on three cards and its cause is "not known"; Hadamard sits 1.8
  to 2.1 W below random signs on each card; "moves between cards unchanged" is gone.
- [x] Cut (about 850 of the page's 12,600 words):
  Done 28 Sep (`031c723`).
  - §9's CLI transcript → one Method line;
  - §5 items that repeat §1 and §3;
  - §8's fit details → `11-thermal-model.md`;
  - the lede's repeats of the KPIs;
  - one home each for the repeated explanations (aifoundry3's clock, 62 °C, 0.81 against 0.65 W/°C, 8–26%, "not
    resolved");
  - move the §3 and §7 tables into `<details>`.
  - Partly landed on 27 September: the §3 and §7 tables are in `<details>`.
- [x] Chart: seconds to 90 °C against switching power.
  - x: flip watts; y: seconds, log scale. One dot per long run (`long[]`); the time-limit runs as arrows; the
    afternoon's matrices as rings.
  - The model curve, and the flip budget as a line.
  - It ties §7 and §8 together and lets the 29-row table fold away.
  - Done 27 Sep: §7, with the long-run table in `<details>`.

### Why is it low power? · `sources/why-low-power.*`

- [x] HOR-4 (low-medium). Voltage and clock, bullet 3 (`:182–184`): 47 W falls within the curve's 44–49 W and 64 W
  lies above it, so "brackets" is wrong. Done 27 Sep: bullet 3.
- [x] HOR-11 (low). Activity, bullet 2 (`:141–143`): "Idle cores cost nothing measurable" holds only for the fp32
  matmul; the integer loop implies a floor of about 0.24 W. Done 27 Sep: bullet 2.
- [x] Cut (about 500 words):
  Done 28 Sep (`031c723`).
  - Voltage bullet 1's 800 MHz note → Caveats;
  - Leakage bullets 1 and 3, whose canonical homes are DVFS §5 and energy manual §1;
  - the §1 prose after the ratio chart;
  - Method's vf.json parenthetical;
  - the 62 and 73 °C readings, once;
  - Caveats bullet 2 → hub §4.2;
  - Versions.
- [x] Chart: the capacitance ladder (plan.md 7(b); built 27 September). Plot the effective switched capacitance per
  minion for all 30 `ablation.configs` in `lowpower-report.json`, against Esperanto's 0.040 nF target, with
  aifoundry3's three points. Done 27 Sep: `#cap-ladder` (§3).

### One hot line stops a shire · `sources/hot-line.*`

- [x] NOC-1 (medium). The lede (`body.html:9–10`) says "about 24 requesters", against the KPI's 21–24. Fix:
  "between 21 and 24 requesters in one other shire flip it (the bank's arithmetic says 22), fewer than the 32
  minions a shire has." Done 27 Sep: the lede, with the three-card edge (21 leave it at 96%, 22 stop it).
- [x] NOC-8 (low). The edge at 22 holds for requesters in shire 1, three hops away. Say so in `#k3sub` and
  `#ineqtext`. Done 27 Sep: `#k3sub` names the requesters' shire and its hops.
- [x] Planned in PLAN3: the energy table is aifoundry2 only (V04); "180 M"; "about 1.2 W … read 1.4 W"; the window
  table; "12,000 gives it 85%". Superseded 27 Sep by the version-3 passes (E36): Method says the energy table is
  aifoundry2's first session; the window table, the paced runs and "about … W … this session read …" are computed
  from the three passes on each of three cards.
- [x] Cut (about 330 words): Versions; the §1 caption and the paragraph after it; `#nrgcap`; the L2 bullet in
  Related; §4's impact sentence; §2's clock paragraph.
  Done 28 Sep (`031c723`).
- [x] Chart: "Stops, not slows", replacing `#wintab` in §2.
  - Log–log: operations against window. Remote atomics rise 400× while the host stays flat at 384; a dashed line
    shows "if it only slowed".
  - Data: `context.window_independence[]` and the 21 two-second runs,
    `data/2026-09-23-reruns-aifoundry{2,3}-warm/hotline-pass*/runs.jsonl`.
  - Done 27 Sep: §2, with `#wintab` in `<details>` under it.

### Hand it to the next shire · `sources/on-chip-relay.*`

- [x] NOC-6 (low). Superseded 27 Sep: §5 was rewritten on three cards and the comparison is gone. §5's "about half of
  what a tensor load … from its own scratchpad costs" sits against §2's 2.40/2.63 pJ/B.
  - Name the 4.2 pJ tensor load of a random byte (energy manual §4.1).
  - Label §2's figures "(32 B loads, contents not set; §4.2)".
- [x] NOC-7 (low). Superseded 27 Sep: the one-stage advantage is 14.3–14.8× on three cards, and the unnamed figures
  are gone. §6 (`body.html:118–119`) gives aifoundry2's 15.3× and 13.4× without naming the card. Use §3's ranges, or
  cut the sentence.
- [x] NOC-10 (low). Rename `#how-far-the-slab-moves-does-not-change-the-bandwidth` and
  `#the-same-watts-a-thirtieth-of-the-work`. Keep empty spans with the old ids, and update the hub's links. Done
  27 Sep: both renamed, the old ids kept, the hub's links updated.
- [x] Cut (about 230 words):
  Done 28 Sep (`031c723`).
  - Versions;
  - the §2 table, which duplicates `#samew`: move the chart into §2, the table into `<details>`, and say "within
    about a watt" once;
  - two sentences in §6;
  - §5's caption.
  - Partly landed on 27 September: the §2 table is in `<details>` under `#samew`.
- [x] Chart: both cards on `#size` (§3) and `#intensity` (§4), from `onchip.json` `size[].by_card` and
  `intensity[].by_card`. Add `by_card` to `bigsize` in `analyze_onchip.py`. Done 27 Sep: every card on both.

### On-chip communication · `2026-09-18-et-soc1-on-chip-communication.html`

- [x] Cut (about 80 words): the per-card fit sentence appears twice verbatim (the intro and script line 1500); keep
  the 800 MHz clause once.
  Done 28 Sep (`031c723`).
- [x] Charts (done 27 Sep: both added):
  1. A chain-order comparison (plan.md §12(b)). `#ring-btn` becomes a selector (ID order, every k IDs, a
     one-hop ring) that draws the path on `#mesh` and marks its longest step. It shows why the relay's 10-hop 31→0
     step sets its pace.
  2. Lower priority: the systolic grain calculator (plan.md §12(c)).

### L2 mainline starvation (pointer page) · `2026-09-22-et-soc1-l2-mainline-starvation.html`

- [x] NOC-11 (low). `:78` "1D rings, 2D in barrier-separated phases, and the hardware trees" → "1D rings and the
  hardware trees, and, by the RTL rule (not run), 2D in barrier-separated phases."
  Done 28 Sep (`031c723`).

### Anatomy of a memory access · `workloads/memprobe/report_template.html`

- [x] MEM-3 (low). §4 and the explorer (`:858–863,1250`) assume one 4.3 ns burst per 64 B line. The page's own
  source (`docs/research/counters-and-dram.md:335,366`) says two BL16 bursts. With two, the chip's share is about
  28 cycles and the memory shire at most about 63. Done 27 Sep: §4 and the explorer.
- [x] MEM-4 (low; PLAN3 §1.2). §7 (`:1001–1005`): "lands 11 cycles late" beside "0–10 … 0–9". Apply PLAN3's wording
  to both. Done 27 Sep: §7 gives PLAN3's per-launch windows (0–10 and 0–9, 19 September) beside "about 11 cycles
  late", and V3-MEM's result (no single window fits 11 of the 15 launches).
- [x] Cut (about 205 words): §6's host-log bullet and its "Later measurements" bullet; §9 "Clock domains"; §2's
  closing paragraph. Partly landed on 27 September: the "Later measurements" bullet is gone and the host-log bullet
  is in `<details>`.
  Done 28 Sep (`031c723`).
- [x] Chart: the memory-shire leg against distance in §4. One dot per home shire on the 104/116/…/176 staircase, with
  a toggle for memory shires one or two hops out. Done 27 Sep: §4.

### Memory hierarchy · `2026-09-18-et-soc1-memory-hierarchy.html`

- [x] MEM-2 (medium). The page mixes A100 parts, and disagrees with Ridge points.
  - The bandwidth dumbbell (`:1345`) uses the 80 GB HBM2e part (1.77 TB/s), while its latency and energy come from
    the 40 GB part.
  - Ridge points uses 1.40 TB/s.
  - Shared memory is 19.5 TB/s here (`:1343`) and 14.8 on Ridge points.
  - Fix: use 1.40 ("HBM2 40 GB; 1.77 for the 80 GB HBM2e"), and 14.8 or label 19.5 as the peak (source:
    `sources/2026-09-18-a100-memory-hierarchy.md` §6).
  - Done 27 Sep: 1.40 TB/s (1.77 labelled as the 80 GB part) and 14.8 TB/s (19.5 labelled as the peak).
- [x] MEM-6 (low). The readout at `:1188` says "nearest line: 31 at 600 MHz", where 31 counts loads, not a shire.
  Fix: "nearest line: 600 MHz for all 31". Done 27 Sep.
- [x] Cut (about 240 words):
  Done 28 Sep (`031c723`).
  - item 5's governor description, and the chase numbers repeated four times;
  - the spec-table note's L1 loop (energy manual §4.2 is canonical);
  - item 6;
  - the "clock was not pinned" caveat.
  - Partly landed on 27 September: the busy-core floor item and the unpinned-clock caveat.

### Ridge points · `2026-09-18-et-soc1-ridge-points.html`

- [x] MEM-1 (medium; PLAN3 ridge-68 leaves it optional). "Other limits" (`:765`): four lines in flight at a
  ~290-cycle DRAM round trip give about 0.9 B/cycle, not the measured 1.4. Replace with: "The Erbium DCache
  description allows 4 line requests in flight per minion. At the ~290-cycle DRAM latency single loads see
  (Anatomy), that would give about 0.9 B/cycle, but one minion measured 1.4. Either TensorLoads see a shorter round
  trip or more lines are in flight; the TensorLoad round trip was not measured."
  Done 27 Sep: "Other limits", "A lone minion" (rewritten on the three-card data).
- [x] MEM-5 (low). `:744` "a 4,500 × 4,500 fp32 block" against the chart's "about 4,580" → "about 4,600 × 4,600",
  or fill it from `reuse-scpmax`. Done 27 Sep: "about 4,580 on a side".
- [x] Cut (about 170 words): the shared-32 KB-tile explanation once ("Own shire"); the energy chart's caption and
  table note.
  Done 28 Sep (`031c723`).
- [x] Charts:
  1. Bandwidth against the minion clock, in "Which ridge points move with the clock". Plot each launch's GB/s over
     its level's 600 MHz median. Data: `data/2026-09-18-memhier-aifoundry2/energy{,2}/runs.jsonl`, embedded through
     `ridge-points.py --embed`.
  2. The energy roofline (plan.md): pJ per FLOP against intensity, on the `roof-int` slider.
  - Done 27 Sep: both (the roofline per card).

### Matmul efficiency · `2026-09-18-et-soc1-matmul-efficiency.html`

- [x] CMP-9 (low). The explorer's legend draws the A100 as a ring and a dot, but the chart uses diamonds. Use
  `CK.legend`'s `'diamond'`. Done 27 Sep.
- [x] Cut (about 330 words):
  Done 28 Sep (`031c723`): every sub-item. The page is 16 words longer than before only because it now gives the hub
  scoreboard's five counts.
  - `#eff-sum` (`:1003`), which repeats the Later box;
  - the gp-sdk lab notes (`:796–802`) → one sentence pointing to `patches/README.md`;
  - the Later box's last A100 sentence;
  - the leakage clause in Caveats;
  - the meter parenthetical;
  - the orphan clock sentence.
  - Partly landed on 27 September: `#eff-sum` and repeated text.
- [x] Chart: an operand-and-card band on the efficiency explorer (plan.md §13(a)). Show GFLOP/s per W over
  zeros, ones and random, per card, from `manual.json` `tensor.rows`; extend `eff_object` in
  `scripts/mmbench-report-data.py:76–95`. The band makes plain that the int8 verdict flips with the data. Done
  27 Sep.

### Sparse compute · `2026-09-18-et-soc1-sparsity.html`

- [x] CMP-8 (low). Scenario 2 (`:836`) pairs times from the on-chip-reduction kernel with energies from the
  host-reduced one. Label each. Done 27 Sep: Scenario 2.
- [x] Cut (about 220 words): the "Answers to the questions…" section (keep the fp16 rule and the messaging answer);
  two caveats bullets; the Later box's last sentence; the sync costs once (§5).
  Done 28 Sep (`031c723`).
- [x] Chart: masked DRAM loads with the home shires lit (plan.md §14(a); data `tload["dram-all"]`),
  labelled as the page's hypothesis. Done 27 Sep.

### Test drive · `docs/report/index.html`

- [x] CMP-3 (medium). "The tensor-unit rung was reached the same day: 9.5 TFLOP/s … FOSDEM's 10.25 scaled to
  600 MHz" (`:793,950,952`). But 9.5 TFLOP/s is the inner loop on cached tiles, while FOSDEM's rung is a whole
  512×512 matmul.
  - Fix: "The tensor unit's inner loop, on cached tiles, ran the same day at 9.5 TFLOP/s (Matmul efficiency),
    FOSDEM's 10.25 scaled to 600 MHz; a full tensor-unit GEMM has not been run."
  - Change the label (`:987`) to "Tensor-unit loop, cached tiles".
  - Done 27 Sep: the text and the label.

### Spatial temperature brief · `2026-09-22-et-soc1-spatial-temperature-brief.html`

- [x] Cut (about 100 words): turn the "On both cards." paragraph into a table built from `HOST_TEMP.cards`; trim
  Versions. Partly landed: the per-card table.
  Done 28 Sep (`031c723`).
- [x] Chart: the sensor-to-host pipeline in §2 (plan.md §17(b)). Draw the 35 sensors, the conversion and
  the host fields; hovering a field lights its inputs. Done 27 Sep: §2.

### Influence functions · `sources/influence-on-et.*`, `data/2026-09-25-influence-on-et/make_analysis.py`

- [x] CMP-1 (medium). "1.8–2.9× the energy" and S2's "26–42% of fp32 peak" use the matmul run's board power, on
  operands with all-zero mantissas. Gradients are random-like.
  - With `manual.json` `tensor.rows` `*_randn` (fp16 61.1 W, fp32 63.9 W): "1.9–3.1×" and "30–48%" (fp16 14–23%).
    Say "on random data (aifoundry2, 80 °C)".
  - Locations: `make_analysis.py:318–337,343`; `body.html:40,63,262,299,369`.
  - Done 27 Sep: `make_analysis.py` and the page, on random data.
- [x] CMP-2 (medium). "7.5 µs … 2.2 TB/s, 9% under" divides cycles by the host's wall-time `ghz` (0.583), a field
  meant for launches of 0.1 s or more. At 600 MHz the time is 7.31 µs, and the energies come from the host-reduced
  kernel at 7.36 µs.
  - Fix: `t_s = 1/sp["per_s"]`; "7.4 µs for 250 µJ"; "2.3 TB/s, 7% under".
  - Locations: `make_analysis.py:97`; `body.html:47,310,354`.
  - Done 27 Sep: "7.4 µs".
- [x] CMP-5 (low-medium). "the chip's 72 MB of on-chip SRAM" → "the chip's scratchpads (72 MB usable of 80 MB)"
  (`body.html:42,232`; `script.js:244,280`; `make_analysis.py:353`). Done 27 Sep: body and script.
- [x] CMP-6 (low). The per-op energies subtract the superseded 30.61 W idle. Use `idle_before_w`: int8 0.39 pJ, fp16
  1.41 pJ. Done 27 Sep: `make_analysis.py` (`idle_before_w`).
- [x] CMP-7 (low). The lede and KPI show `s1.l2_case.lead` with `data-dp="0"` ("3–4×") where S1 prints 2.6–3.9×. Use
  `data-dp="1"`. Done 27 Sep.
- [x] Cut (about 300 words):
  Done 28 Sep (`031c723`).
  - §6 "Corrections folded in…" → the data README;
  - the H100 energy caveat twice, not four times;
  - "What 'sparse-friendly' buys here";
  - S1's "Value to a big lab".
  - Partly landed on 27 September: §6's corrections moved to the data README, "What 'sparse-friendly' buys here" and
    "Value to a big lab" cut.
- [x] Chart: S1's lead against queries per pass. A log-log plot of mJ per query against Q, for the ET card and the
  H100, from `s1.parity_*.table[]`, with the crossings marked. Done 27 Sep.

### Over the PCIe link · `sources/pcie-link.*`, and the hub's rung 30

- [x] `pcie-link.body.html:131–132` says why aifoundry3's host copies memory at half the others' rate "was not
  established; reading it needs root". It was read as a user on 27 September 22:18: aifoundry3 runs one DDR4-2666
  DIMM on a single memory channel, aifoundry2 two channels, aifoundry1 two channels of DDR4-3200
  (`data/2026-09-27-pcie/hosts.txt`, addendum). Say so, and in the hub (`limits-of-observability.data.json`,
  rung 30 "ask-lab-root") mark the memory part done by us; MaxPayload and MaxReadReq still need root.
  Done 28 Sep (`031c723`): the page and rung 30 say the memory channels were read without root; rung 30 stays
  `ask_team`, since MaxPayload and MaxReadReq still need root.

### The aifoundry1 pages (standalone HTML)

- [x] PWR-01 and PWR-02: see part 0 and "aifoundry1 and aifoundry3 statements" above. Done 27 Sep: PWR-02 on both
  pages (the dated update box, the PCIe line); PWR-01 by the owner's decision (part 0: both pages stay public for now).
- [x] Cut (about 650 words): the fix page's §4 (with PWR-01); the troubleshooting page's lede (284 words), which
  repeats its four boxes; §1's procedure into `<details>`. The fix page's §4 stays, with PWR-01 (part 0); the rest
  is open.
  Done 28 Sep (`031c723`), except the fix page's §4, which stays by the owner's decision.

### The ET-SoC-1, interactively (the chip diagram) · `sources/chip-diagram.*`

- [x] **The chip diagram's routes (E56):** read replies go y first and write requests x first on both cards, so fact
  L104 and every route the diagram draws x first are wrong for replies (`data/2026-09-29-nocr/`; the frozen
  `PREREG.md`, `2472ab3e…`). Draw replies y first and correct L104 in
  `data/2026-09-27-chip-diagram/build_facts.py`; rebuild, check and deploy the diagram (and the memory levels, if
  its views use L104).
  Done 29 Sep (the major pass): L104 is kind "measured", and `build_facts.py` asserts both cards' verdicts from
  `data/2026-09-29-nocr/raw/<card>/summary.json`; every reply is drawn y first, on the diagram and the memory levels.
- [x] **E55 and E57 on the chip diagram** (the hub's rungs 33, 34 and 36 said the diagram's parts were measured while
  it still drew them as before): flow 6's "Into DRAM" through the lines' L3 homes (T34-A, fact `pcie.write-l3`), with
  only the L3's write-back to DRAM dashed; L50 measured (R33a on both cards, R33b on aifoundry3); fact
  `minion.tensor-cache-path` settled for the L2 (R36); `pcie.conc` says E50's two streams had four commands in flight
  and adds E55's one command per stream (1.012); the asks "the Host -> DRAM path", "the DRAM address map", "the
  tensor unit's cache path" and "the host link's open questions" rewritten.
  Done 29 Sep (the major pass): `build_facts.py` (AMEND2 and the E55/E57 section), `research/make_asks.py`,
  `chip-diagram.script.js`.

## B. Repository-only work not done in this pass

### After the campaign (every block hashes `tools/claims-v3/`)

- [ ] `tools/claims-v3/lib.sh`, **once the owner releases the heat-placement lock** (DV2's validation, whose lock
  also held it, ended at 16:57 PDT on 29 September; `lib.sh` and `queue.sh` stay in the heat-placement lock,
  `tools/claims-v3/hp/prereg/PREREG.md`, whose `reduce.py --val` refuses to reproduce `val.json` on any changed byte;
  whether to release it, or to keep the frozen bytes elsewhere for that check, is the owner's decision):
  - `:17–18`: aifoundry3 has system numpy, and all three hosts have a venv, since 25 September. Landed on
    27 September (`a745199`, the comment only) and reverted on 28 September by DV2's commit `8eb0e38`, which keeps
    `lib.sh` at the locked bytes (`d884e53`'s): re-apply `a745199`'s comment.
  - `:3–4`: add aifoundry1.
  - `:7`: note amendment A3.
  - `:52`: the data path `collect.sh` writes.
  - `:70–71`: a sudo detail (AGENT.md §10) → a variable.

  Left: all five.
- [x] With the results:
  - Landed: E35–E49 registered and "Cite as" widened (03-experiments.md); the requests of 25–27 September numbered
    (Q44–Q57); a results series in `CLAIM_SERIES`; AGENT.md and getting-started updated.
  - Left: rebuild aifoundry1's `build/<workload>` directories with the g3log fix.
  - Done 28 Sep: the rebuild (the next section's first item).

### Our tools, after the heat-placement work (from the lab re-check of 27 September)

The heat code is frozen until its validation on aifoundry1's card 1 ends (about 08:00 PDT, 28 September). Then:

- [x] Rebuild aifoundry1's `build/<workload>` host programs with `registerRuntimeLogLevels()` (the item above), then
  update getting-started's "Where things stand".
  Partly done 28 Sep (07:52 PDT, after card 1's validation queue ended): enercat, memhier, memprobe, nocbench, onchip
  and sgemm rebuilt with the fix (each host now imports g3log's `addLogLevel`; the kernels are byte-identical). Left:
  `build/sparsity`, the heat-placement lock's frozen heater (rebuild it when the owner releases that lock), and
  `build/enercat_v2`, the campaign's catalogue host, whose hash its cat blocks record (`tools/claims-v3/gs/README.md`:
  never rebuild it; aifoundry3's is unfixed too). No build of pmcsel or traceprof there; enercat_gs and pciebench
  already had the fix.
  Done 28 Sep (20:56 PDT, Q65): `build/sparsity` rebuilt with the fix (host `e0fbecce…`, the kernel unchanged), the
  frozen heater kept as `build/sparsity.frozen-hp-20260922`; `build/enercat_v2` stays unfixed on purpose.
  getting-started's "Where things stand" updated on 29 September.
- [ ] The heat code's card-0 temperature guard (`tools/claims-v3/hp/`) takes card 0's lock for its lifetime, and the
  drain on a two-card host checks the other card's node with `et-who`, not only its lock (the stock
  `dev_mngt_service` opens both cards).
- [x] `workloads/pciebench/run_pcie.sh` releases the card lock between sub-tests (runs held it 12.8–14.9 s; AGENT.md
  §5's 10 s rule is per device-opening process).
  Done 28 Sep (`031c723`), dry-tested only: its next real run will be its first on a card, and with 20 s lock waits a
  run can take longer than `schedule.sh`'s `timeout 150`. Its first card run: aifoundry1's card 1, 28 Sep 23:56 PDT,
  every sub-test exit 0 (`data/2026-09-29-pcie2/run_pcie-r101/`).
- [ ] The queues poll `et-who` less often, and scripts use `et-who --check`'s exit status instead of parsing its text
  (`tools/lab/README.md`; `et-who --check` is installed on all three hosts since 28 September). DV2's validation has
  ended, but `queue.sh` and `lib.sh` are in the heat-placement lock too: with the `lib.sh` item above.
- [ ] `V3_DRY` fails closed for agents: a marker file, or real runs only with an explicit `V3_REAL=1`. With the
  `lib.sh` item above, for the same reason.
- [x] Commit the heat branch, with the firmware findings behind it (per-release governor behaviour, aifoundry3's
  latch at a 0 W TDP, card 1's fixed clock, the release-to-commit mapping) in `14-card-behaviour.md` and a
  `data/2026-09-27-heat-placement/` directory: source lines and commits only.
  Done 28 Sep: merged at `6ba8f47` (`heatpage`, the page at `a8b3984`; `heat-placement` is merged too); the firmware
  findings are in `14-card-behaviour.md`, "The clock governor, by firmware build", and the source read in
  `data/2026-09-28-heat-placement/plan/notes/firmware.md` (the heat data's directory is dated 28 September).

### The knowledge base against the version-3 pages (the page holds)

`docs/findings/` predates the version-3 first pass (`0399048`). This pass fixed the summaries in its commit and
flagged the rest at the top of `../findings/README.md`.

- [ ] `05-claims.md`:
  - `:207` idle law on aifoundry3: +0.61 W, sd 0.05, over 16 sessions; −0.18 W over 25 on aifoundry2 (landed).
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
    E50–E52 (E35–E49 are taken).
  - Partly landed on 27 September: the idle law (`:207`); the two-day governor row and the refresh per card and
    poller (`:42` and a Version 3 row); the droop and IR drop per card; heat per mm's all-ones excess per card and the
    Ridge balance points per card (Version 3 rows, E42 and RL-X4); memory anatomy's latency model, bank timing and
    refresh (Version 3 rows, E35). Left: the 256 B pattern; PLAN3 §1.2's heat and energy-manual rows (the "Cheapest
    and dearest instruction" row still gives 4.6 and 1,486 pJ); the per-card L1 and L2 and "within 0.8%" (the "Levels
    at 600 MHz" row still says "both cards, n = 6", the "Bandwidth at 600 MHz" row "within 0.3%"); `:57`, `:135` and
    `:433` (HOR-2, HOR-R3); memory anatomy's counter carry; E50–E52; and `:120`'s "A different afternoon session".
- [x] The topic files:
  Done 28 Sep (`031c723`).
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
  - `docs/et-soc1-notes.md:206`: "on a different afternoon" → "in a separate session that afternoon".
  - Partly landed on 27 September: the refresh in `14-card-behaviour.md` (`:30,83–96`) and
    `19-observability-and-the-unmetered.md` (`:17`); `13-why-low-power.md`'s one-card caveat (`:165`);
    `20-heat-per-mm.md`'s contention and all-ones (the three-card run); `01-resources.md`'s card lines. The rest is
    open (`17-hot-line.md` has none of its four fixes).
- [x] `README.md` (done 27 Sep: none of these phrases is left in `README.md`; the "different afternoon" slip is
  still in `05-claims.md:120` and `docs/et-soc1-notes.md:206`, now listed under those files):
  - "0.75 pJ/B on zeros and 1.81 on random … (2.3 over 1–6 hops" → the manual's 0.6–0.75, 1.7–1.8 and 2.1–2.3.
  - "a flat 8%" → "about 8% (3–10% per pattern)".
  - "repeats the whole experiment" → "repeats the 7 s runs".
  - "on a different afternoon" → "in a separate session that afternoon". The same slip is in `03-experiments.md:302`,
    `../findings/README.md:84` and `05-claims.md:120`.
  - "5% on SRAM" (also in getting-started:81).

### Records and commands

- [x] `04-artifacts.md` (partly landed on 27 September: all but A4's "six versions"):
  Done 28 Sep (`031c723`).
  - rows in the Commits table after `bde52e0`;
  - a tools row for `tools/g3log-race/race.cpp` (E49);
  - A16's `sync_hub_data.py` blocks `power.checks` and `claims_status`;
  - A4's "six versions" (version 6 is only the 7 s runs);
  - A2's row, which stops at 24 September;
  - the card registry and `sortTable` in the chartkit note.
- [x] The claims-v3 README's file table omits AMENDMENTS.md. Done 27 Sep.
- [x] `getting-started.md` (done 27 Sep: all five, in "Where things stand", "Earlier work", §2's card table, §7's
  gotchas and §8's hub row):
  - `:221` "(51–54 °C before)" → "(53–54 °C before; amendment A5)";
  - `:360–361`: the `06605ab` pin, not the patch, avoids the Erbium problem;
  - `:423` needs `python3`, and `:424`'s input list lacks `plan3.json.gz`;
  - `:173`: FOSDEM's 10.25 came from software-pipelining the tensor unit;
  - `:78`: up-steps at readings up to 66 °C.
- [x] Card commands without `et-who`, the card lock or `timeout 10` (done 27 Sep: getting-started §3 and §4, the
  README's Run, and the three READMEs):
  - getting-started `:268,276,292–293`;
  - `README.md` "make run-hello DEVICE=silicon" (it also needs `deploy-lab-gpsdk.sh`);
  - the memhier, nocbench and sparsity READMEs ("Check `uptime`, `who` and `ps` first").
- [x] Clone lists (`README.md:208`, getting-started:188) omit et-testdrive and etTopoScan. `scripts/vm:4` gives
  `make -C hello run` for `make run-hello`. Partly landed on 27 September: both clone lists name all five; left:
  `scripts/vm:4`.
  Done 28 Sep (`031c723`): `scripts/vm:4` too.
- [x] `01-resources.md`: R5's etiquette → AGENT.md §5; R10's resolver note (lab-access.md); R12, the L2 brief, is a
  pointer page since 25 September. Done 27 Sep: all three.

### Concision in the repository (about 4,000 words)

- [x] `README.md:21–182`, the per-report prose (about 2,380 words): one sentence and a 21-row table (page, code, raw
  data) built from MIRROR.md and getting-started §8. Keep the only copy of the hub's survey-source location.
  Done 28 Sep (`031c723`): the table is kept by hand in `README.md` ("Add a row here with each new page"); its
  generator stays out of the repository.
- [x] `getting-started.md`, replacing duplicates with links to their canonical homes:
  Done 28 Sep (`031c723`).
  - "Earlier work"'s "Done" (about 650 words) and the dated result bullets of "Where things stand" (about 650);
  - the etiquette (AGENT.md §5);
  - the publishing rules (MIRROR.md);
  - the card table (14-card-behaviour);
  - Tailscale (lab-access);
  - the energy-manual chain (04-artifacts A16).
- [x] AGENT.md §1 and §9: point to getting-started and MIRROR.md instead of keeping dated snapshots.
  Done 28 Sep (`031c723`).

## C. Card work and its records, after the major pass of 28–29 September (Q65)

- [x] **Reduce DV2's validation** (E51) after its idle cycles end on aifoundry2, about 16:45 PDT on 29 September:
  collect the passes and run `tools/claims-v3/dv2v/reduce_val.py` against the frozen `PREREG-VAL.md` (`e150ce16…`);
  then the DVFS page's §8, `14-card-behaviour.md` and E51. Until then nothing in its lock changes (AGENT.md §7).
  After it: part B's `lib.sh` item, and its two items on `et-who --check` and `V3_DRY`.
  Done 29 Sep (`e4d894d`): the queue ended at 16:56:46 PDT, the lock checked OK before the reduction, and the frozen
  reducer's verdicts are in `data/2026-09-28-dvfs2-aifoundry2/validation/` (`verdicts-dv2val.json`, README): TH3, TH4
  and TH8 survived, TH7 fell (1 of 52 exits), TH1-busy, TH1-idle, TH2 and Q2 are untested (G1-T 7 of 9 on the mean
  where 80% is needed, I1 4 of 5 cycles, G4-S 4 of 6 blocks). The records and pages on 30 September: E51 in
  `03-experiments.md`, `05-claims.md`, `14-card-behaviour.md`, `16-dvfs-and-leakage.md`, the findings README,
  `02-requests.md` (Q59, Q65), getting-started, the DVFS page's §8 (the verdicts table and the owner's two questions)
  and the hub (§7's E51 row, the firmware note). Part B's three items stay open: `lib.sh` and `queue.sh` are also in
  the heat-placement lock.
- [ ] **The third card:** after DV2, run pcie2 (E55), nocr (E56), memp2 (E57) and tau (E58) on aifoundry2 under their
  frozen pre-registrations (tau only after the amendment its `PREREG.md` requires for aifoundry2: a heat step, its
  own start temperature, a D burst that does not starve its sampler and its own calibration, written before any
  aifoundry2 data), as a third card beside aifoundry1's card 1 and aifoundry3. Then NV's validation there
  (`tools/claims-v3/nv/schedule-val-aifoundry2.txt`), once its first write and development on aifoundry3 are done
  (part 0).
  Partly done 29 Sep, 16:59–17:38 PDT (`b1198cb`, the frozen locks verified): pcie2 gave aifoundry3's verdicts (T35-S
  and T34-A survived); nocr found read replies y first and write requests x first, as on the other two cards, and
  T-DIRECT refuted by its rms rule (4.47 cycles); memp2 R33a FAIL (14 of 15), R33b and R36 PASS, R43 FAIL, E102's
  bandwidth PASS and its energy not resolved, T102 FAIL (`data/2026-09-29-{pcie2,nocr,memp2}/README.md`). On the pages
  30 September: the hub's rungs 31–36 and 43 and §7, the PCIe page's §5, the chip diagram (facts L104, L50,
  `pcie.write-l3`, `pcie.conc`, `minion.tensor-cache-path` and its asks) and the memory levels (`l3.route`). Left: tau,
  after its amendment, then NV's validation (part 0). Unblocked: aifoundry2's card is back in service since
  6 October 2026 (lab report SH5 done).
- [ ] **memp2's R43 is open:** no registered theory of the 128 B per cycle cap survives on any of the three cards
  (T43-B misses 7 conditions, Cc 5, on each; `data/2026-09-29-memp2/README.md`). New theories need a new
  pre-registration.
- [ ] **nocr's R31 rule on aifoundry3:** the ESR fit is 1,557 + 35.9 cycles per hop (r² 0.995) but its rms is 4.7
  cycles against the frozen rule's 4, so T-DIRECT is refuted there and the places that rest on it (P5–P7) are not
  decided on that card; in development on card 1 it survived. The frozen rule stands for this run: decide the places
  with aifoundry2's run or a new pre-registration.
  aifoundry2's run (29 Sep) refuted T-DIRECT too (1,556.8 + 35.9 cycles per hop, r² 0.996, rms 4.47), so only a new
  pre-registration can decide the places by timing.
- [ ] **memp2 on the third card left two results open** (`data/2026-09-29-memp2/val-aifoundry2/`): two lines that
  differ only in PA[17], a column bit in the L50 map, read as a row conflict on aifoundry2 (R33a's condition `col`,
  0 cycles from the other-row reference, 48 trials), where aifoundry3 and card 1 read one row (−21), and so did the
  anatomy's one-bit flip of PA[17] on the same card on 19 September (−12 cycles); and the stride-256 energy excess was
  not resolved there (+35.7 and +31.1 pJ per 64 B, 99% intervals that include 0, the die at 76–78 °C). A
  service-processor readback of that card's ADDRMAP registers (the hub's rung 26) would settle the first; a new
  pre-registered run the second.

## D. Sparse parity (Q66, E59): next steps

E59 solved noisy sparse parity on aifoundry3's card on 29 September: L1 (512, 4, 0.3, 448) in 0.131 s, L2 (512, 4,
0.4, 1,850) in 0.323 s and (256, 5, 0.4, 1,925) in 1.52 s on 1,024 minions, 1.1–1.6× six tuned AVX-512 threads
(`../findings/03-experiments.md`, E59). What limits it
(`workloads/sparseparity/data/2026-09-29-aifoundry3-card-m4/README.md` and `-m5-energy/README.md`): hart 1's row
generation, the shire's bandwidth for streamed A (about 512 cycles per op at 32 minions per shire), and the epilogue
(1,606 cycles per output tile with the tensor unit idle). The code, the builds and the card rules are in
`workloads/sparseparity/README.md`; every card step is one locked `timeout 10` process.

- [ ] **Cooperative B loads** (`tensor_coop`, PRM 9.2.4 and 9.3.1.1; `docs/research/sparse-parity/DESIGN.md` §2.2 and
  §6). With A streamed, each op brings 2 KB through the shire's L2, and 32 private streams per shire run at about 512
  cycles per op (E37's 511.94), which bounds L2's one-stage scan at 0.28 s from the ops alone, 0.30 s with the staged
  rows counted (DESIGN.md, Amendments). If the 32 minions of a shire walk the same (column tile, sample slice)
  sequence and load each B line once for all of them, an op needs about 1 KB plus the generated rows; DESIGN.md §2.2
  predicts about 295 cycles per op. The planner must group 32 row tiles that share a first column tile into one shire
  step. Never run in this repository: `sys_emu` first, then one neighbourhood, then one shire.
- [ ] **Resident A.** Held in the L1 scratchpad (48 lines, 3 KB), a row tile's A is loaded once for all its column
  tiles and only B streams (270 cycles per op with A held in E39's microbenchmark). It fits only at S ≤ 3 (m ≤ 192):
  there the epilogue outweighs the 3 ops of an output tile, and at η = 0.4 a stage 1 at m1 ≤ 192 keeps 83% of the
  candidates at P(loss) < 10⁻⁴ (and 57% at m1 = 320). M5's `m5-l1-res192` (L1, m1 192, τ1 40) launched in 0.127 s
  against 0.125 s streamed at m1 320, at 1,996 cycles per op on its busiest minion, and kept 6.7 × 10⁶ survivors at
  P(loss) 1.8 × 10⁻³: 0.266 s per solve. It could pay with a cheaper epilogue, or with a loop order that keeps A
  resident at larger m.
- [ ] **A faster row generator** (hart 1). On the (256, 5) instance generation is the limit: in M4 the busiest minion
  of its second half ran 1,629 cycles per op against 270–280 for the op, with hart 0 waiting for rows
  (`workloads/sparseparity/data/2026-09-29-aifoundry3-card-m4/f5-b/h1.log`, `cycles_per_op_busiest`,
  `wait_cycles_max`). M4's incremental generation gained 1.1–1.2×; both harts generating would gain at most 1.06× (one
  issue slot per minion). First run `card_run.sh m4gen` (timing only, not yet on a card): it separates the staged
  stores' cost from the expansion's (`workloads/sparseparity/README.md`, "M4 on a card").
- [ ] **Host-side early exit for sliced one-stage solves** (`docs/research/sparse-parity/DESIGN.md` §2.8 and its
  Amendments). A solve that runs as several launches (`--slices N` in one process, or host-side slices, one process
  each) could stop at the first launch whose records report c ≥ τ_acc: each hart's 64 B record already carries its
  best c, so no survivor log is needed. Not implemented; the full-scan time stays the primary metric (§2.8).
- [ ] **More cards.** E59 ran on aifoundry3's card only (pinned at 600 MHz). Run `card_run.sh m5` and `energy.sh`
  with the same kernel (`.text` `3e14be32…`) on aifoundry1's card 1 (600 MHz; `card_run.sh` sets `ET_DEVICES=1` and
  the shire1 lock) or card 0 (in service again since its fan was replaced on 2 October 2026; idles at 300 MHz;
  `card_run.sh` and `energy.sh` would need a card-0 option), and on aifoundry2 once its card is back in service (out
  since 2 October 2026: its cooling failed), where DV2's validation ended at 16:57 PDT on 29 September (E29 saw its
  governor lift the clock to 700–800 MHz mid-burst below about 68 °C, `../findings/14-card-behaviour.md`, "The clock
  governor is thermal first", so record the clock with every run). `energy.sh` refuses aifoundry2 unless
  `SPP_ALLOW_AIFOUNDRY2=1`, a guard written for DV2's validation, which has ended; keep it while that card is out of
  service.
- [ ] **`lib.sh`'s device-process pattern** (review R4, finding 8). `ps` truncates
  `sparseparity_host` to `sparseparity_ho` (15 characters), which `DEV_COMM`'s `_host$` in
  `tools/claims-v3/lib.sh:57`, `tools/claims-v3/dv2/z2.sh:37` and `dv2lib.sh` never matches, so a campaign block
  would not count a running sparse parity host as a device process (the card lock and `et-who`'s node holders still
  protect the card). Add `^sparseparity_ho` to those patterns, as `workloads/sparseparity/energy.sh` already does.
  `lib.sh` waits with part B's `lib.sh` item (the heat-placement lock); `dv2/z2.sh` and `dv2lib.sh` were held only by
  DV2's lock, which ended with its validation on 29 September.

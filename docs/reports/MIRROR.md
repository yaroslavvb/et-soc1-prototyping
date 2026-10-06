# The spacesheep mirror: every published page and its file here

The repository is the ground truth. spacesheep.dev is where people read the pages. Every public page below is a
committed file in this repository, and the live page must equal that file. The only allowed difference is what the
host adds when it serves the page: `data-ss-id` attributes on elements and, on the raw address, its viewer scripts just
before `</body>`. Private pages are listed but not mirrored.

- **Check:** `python3 scripts/check-mirror.py` compares every public page with its file and exits non-zero on any
  difference (see [Checking that live equals repo](#checking-that-live-equals-repo)).
- **Keep this file current.** Add a row when a page is created, and edit it when a page moves, is deleted or changes
  visibility. `scripts/check-mirror.py` reads the tables between the `mirror:begin` and `mirror:end` markers: one row
  per space, the uuid in backticks, the repo file in backticks (or "not mirrored").
- **Addresses.** `https://spacesheep.dev/@yaroslavvb/<slug>` is the viewer (the page framed, with comments).
  `https://<space-uuid>.spacesheep.app/` is the raw page, and a folder deploy serves each of its files at
  `https://<space-uuid>.spacesheep.app/<file>`. A private space answers both anonymously with a sign-in step only.
- **Waiting changes.** Page changes found by the review of 26 September wait in [`TODO.md`](TODO.md) for the next
  pass, which deploys them with this file's procedure.
- The per-page history (what each version changed, the A-numbers, the reviews) is in
  [`docs/findings/04-artifacts.md`](../findings/04-artifacts.md). The review's `manifest.tsv` in
  `data/2026-09-24-report-review/` is a dated record of 24 September; this file supersedes it.

## The pages (as of 2026-09-29)

<!-- mirror:begin -->

### The measurement set: the pages the hub indexes

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [The ET-SoC-1, interactively](https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram) (27 Sep, the interactive chip schematic; linked at the top of the hub) | `6cfdea5c-a598-438e-bd1a-613093ede523` | public | `docs/reports/2026-09-27-et-soc1-chip-diagram.html` | folder (since the deep zoom of 30 Sep; the folder renamed `ladder-img/` on 1 Oct, the shared ladder): `index.html` + `ladder-img/andromeda.webp` `ladder-img/card.webp` `ladder-img/cmb.webp` `ladder-img/earth.webp` `ladder-img/milkyway.webp` `ladder-img/rack.webp` (the page fetches each only when the camera comes near its level) + `ladder-img/ladder-data.json` (the deep zoom's facts, fetched at idle after the first paint) |
| [Anatomy of a memory access, interactively](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-levels) (28 Sep, each level of the memory system drawn and animated down to the transistors; the memory anatomy page's companion, linked from its top, and from the hub's §1 index and §5 rungs 37–44) | `3ec78e9e-1f89-4258-8e30-eee4ca4a27cc` | public | `docs/reports/2026-09-28-et-soc1-memory-levels.html` | folder (since 1 Oct, the shared ladder's part 2; a file before): `index.html` + `ladder-img/andromeda.webp` `ladder-img/card.webp` `ladder-img/cmb.webp` `ladder-img/earth.webp` `ladder-img/milkyway.webp` `ladder-img/rack.webp` (fetched only when the camera comes near their levels) + `ladder-img/ladder-data.json` (the ladder's facts, fetched at idle after the first paint): the same folder as the chip diagram's |
| [Where the work sits: placement and the thermal trip](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-placement) (28 Sep, E52: does the same work run longer before the thermal trip in some parts of the chip; development on aifoundry3, a frozen validation on aifoundry1's card 1; in the hub's §1 index and §7) | `daa1d70b-45f0-4989-b26e-099ca555f028` | public | `docs/reports/2026-09-28-et-soc1-heat-placement.html` | file |
| [The effect of overheating](https://spacesheep.dev/@yaroslavvb/et-soc1-effect-of-overheating) (28 Sep, Q61 and E53: outside research on processor temperature limits, average against hottest, heat and switching speed, and why a hot chip stops and recovers, checked on the ET-SoC-1; in the hub's §1 index and §7) | `76d6540b-af38-453f-95f6-880fd3723831` | public | `docs/reports/2026-09-28-effect-of-overheating.html` | file |
| [Feasibility of running the ET-SoC-1 without its heatsink](https://spacesheep.dev/@yaroslavvb/et-soc1-without-heatsink) (30 Sep, Q70: can a card run with its heatsink off so that a sensor can look straight at the chip; with Q81's low-clock envelope since that evening; arithmetic on the record and 43 outside sources, no card touched; in the hub's §1 index; linked from the overheating, heat placement and power pages and from the thermal camera page) | `f4722866-cd5b-430d-b6a5-b45795486735` | public | `docs/reports/2026-09-30-esperanto-without-heatsink.html` | file |
| [The PCIe link and the launch path](https://spacesheep.dev/@yaroslavvb/et-soc1-pcie-link) (27 Sep; the chip diagram's PCIe and launch figures) | `2016e21b-711c-4879-8204-cb03791584a4` | public | `docs/reports/2026-09-27-et-soc1-pcie-link.html` | file |
| [Limits of observability · ET-SoC-1 reports hub](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2) | `2ea37420-67b9-484e-9d4c-581e8a9f0323` | public | `docs/reports/2026-09-20-et-soc1-limits-of-observability.html` | file |
| [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15) | `cc3cb1d6-51cf-420b-a165-7d8629904d97` | public | `docs/reports/2026-09-23-energy-manual.html` | file |
| [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17) | `5602ff62-878f-4db6-b703-02061000d9ce` | public | `docs/reports/2026-09-24-heat-per-mm.html` | file |
| [The DVFS loop and its leakage](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11) | `171dcd4a-5b6d-49d3-aca0-db4980fabfa5` | public | `docs/reports/2026-09-22-dvfs-leakage.html` | file |
| [Power and temperature telemetry](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3) | `acee5c6d-56c0-45e7-aa97-ce11af37bdd8` | public | `docs/reports/2026-09-20-et-soc1-power-temperature.html` | file |
| [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4) | `da445a93-7be3-42c2-b9be-4992fa4a3b62` | public | `docs/reports/2026-09-20-horace-experiment.html` | folder: `index.html` + `horace-heating.gif` `horace-heating-6.gif` `horace-long.gif` |
| [Why is it low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5) | `baede20c-57d9-4e01-8157-2014670dd8cf` | public | `docs/reports/2026-09-21-why-low-power.html` | file |
| [One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) (A13) | `ac439287-4503-42c7-88e7-b5d3e3b64b06` | public | `docs/reports/2026-09-22-hot-line.html` | file |
| [Hand it to the next shire: on-chip relay vs DRAM](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) (A14) | `8678d49d-3f0c-49be-b08a-5528de8ece3c` | public | `docs/reports/2026-09-22-on-chip-relay.html` | file |
| [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1) | `2bf74fd1-fd7f-4e19-8e35-6168ae42657c` | public | `docs/reports/2026-09-19-et-soc1-memory-anatomy.html` | file |
| [Memory hierarchy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy) | `4b6e0a37-808d-4fc9-8001-555125733c46` | public | `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html` | file |
| [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication) | `ab8e1b2b-de17-44f4-8645-006fa960e349` | public | `docs/reports/2026-09-18-et-soc1-on-chip-communication.html` | file |
| [Matmul efficiency](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency) | `590752c1-17a8-4f5d-97ef-bcf33fd6a3e7` | public | `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html` | file |
| [Sparse compute](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute) | `5abf6014-8de0-4e82-8744-5676bac6453e` | public | `docs/reports/2026-09-18-et-soc1-sparsity.html` | file |
| [Ridge points](https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points) (A19) | `dd341b0b-a52e-4e23-b8b3-101a83119133` | public | `docs/reports/2026-09-18-et-soc1-ridge-points.html` | file |
| [Test drive](https://spacesheep.dev/@yaroslavvb/et-soc1-testdrive) | `16732875-c03e-434d-a643-7a432586c7f7` | public | `docs/report/index.html` | file (`docs/report/` holds only this file) |
| [Spatial temperature: a brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief) | `bc391cfe-64e2-4f36-884c-9bbfcb267de8` | public | `docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html` | file |
| [L2 mainline starvation: a brief](https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation) (a pointer page) | `49ca367f-886f-4c0a-b472-12d8fc449300` | public | `docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html` | file |
| [Influence functions on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions) (exploratory, 25 Sep) | `55ae9267-3fc8-42a4-8621-4102fd7c97f7` | public | `docs/reports/2026-09-25-influence-on-et.html` | file |
| [Sparse parity on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-parity) (exploratory, 29 Sep: Q66 and E59, noisy sparse parity solved on the card's 1,024 minions against the host CPU's best method; in the hub's §1 index beside the influence-functions page, and E59 in §7) | `a6212e3c-63f8-4971-a833-06457e2824da` | public (deployed private at 12:45 PDT on 29 Sep, made public at the owner's word the same afternoon) | `docs/reports/2026-09-29-sparse-parity.html` | file |

### The lab machines

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [What is broken on aifoundry1](https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting) (25 Sep) | `a2d70512-f892-474e-aca6-0568176cb092` | public | `docs/reports/2026-09-25-aifoundry1-troubleshooting.html` | file |
| [aifoundry1 is fixed](https://spacesheep.dev/@yaroslavvb/aifoundry1-fix) (25 Sep, the fix log) | `31e35ba7-36f4-486e-b6f3-687f7c7ad3a0` | public | `docs/reports/2026-09-25-aifoundry1-fix.html` | file |
| [A PCIe link retrain hung aifoundry1](https://spacesheep.dev/@yaroslavvb/aifoundry1-link-retrain-hang) (30 Sep, the incident and its lesson) | `11e77f93-1896-475f-b962-3418a3712006` | public | `docs/reports/2026-09-30-aifoundry1-link-retrain-hang.html` | file |
| [ET-SoC-1 review: the TODO list](https://spacesheep.dev/@yaroslavvb/et-soc1-review-todo) (26 Sep) | `1db405d2-34c6-45f0-b939-03b74d3d68b4` | public | `docs/reports/2026-09-26-review-todo.html` | file (rendered from docs/reports/TODO.md by scripts/build-todo-page.py; redeploy after every change to TODO.md) |

### The lab, for newcomers

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [New user? Start here: the AI Foundry ET-SoC-1 lab](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-start) (30 Sep; since 2 Oct, three steps: create your account as root once, start Claude on the lab machine as yourself, give it one line; the brief it reads is `docs/lab-start/START.md`; linked from the lab dashboard) | `7f665ca1-873b-4d0f-86b1-8ab15cd9ab25` | public | `docs/reports/2026-09-30-aifoundry-lab-start.html` | file |

### The session

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [Two weeks with the ET-SoC-1: the session timeline](https://spacesheep.dev/@yaroslavvb/et-soc1-session-timeline) (27 Sep; refreshed 1 Oct, and on 5 Oct to 19 Sep–5 Oct: the main session and every other Claude session on the lab's machine, on both of the owner's Claude accounts, in lanes of their own; the owner's messages as summaries and, on hover and in a reader, their own words, with access details, addresses, other people's names and private links removed and marked; aifoundry2's card off the bus and the hosts down; every deploy and commit; built by `tools/timeline/`, whose README has the pipeline) | `b0669cbd-6132-4ac6-b35a-9b928a2ef926` | public | `docs/reports/2026-09-27-session-timeline.html` | file |

### Public, not mirrored

| Page | Space | Visibility | Repo file | Why |
|---|---|---|---|---|
| [Lab machine accounts](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-accounts) (18 Sep) | `5bcb11cb-7e1f-4cf2-bde3-c375c904b3a9` | public | not mirrored | A standalone copy of an older [`docs/lab-access.md`](../lab-access.md) with `scripts/add-lab-user.sh` built in, written by hand on 18 September. The machines' login banners link it. It is older than `lab-access.md`, which is the current text. |
| [What trips people up on the AI Foundry lab](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-problems-for-roman) (25 Sep, the lab problems report for the lab lead; re-checked and republished 27 Sep with statuses, 17 new problems and "Requests for Roman", which the hub's §5 links) | `6c75b258-53fe-45fe-b2cf-11f8572ac2c3` | public | not mirrored | Written for the lab lead; public since the owner confirmed it on 26 September. Its source stays out of this repository (`38f6b02`; `docs/reports/2026-09-25-lab-problems.html` is gitignored). |
| [Pointing a thermal camera at the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-thermal-camera-experiments) (the owner's page with its plan and `lockin.py`; on 30 September its "not shared" box and two related-report lists gained links to the heatsink feasibility page and its siblings) | `9f8173a6-6b78-4ae0-90b5-ae9fbb40fe18` | public | not mirrored | The owner's own page, written outside this repository and deployed as a folder (`index.html`, `plan.md`, `lockin.py`, `img/rack.jpg`); listed so that `check-mirror.py` checks it stays public. The 30 September edit changed only the links and one sentence, from a byte-exact copy of the live folder. |
| [AI Foundry lab](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard) (30 Sep: the lab dashboard: the three machines, four cards and their users, republished by `tools/lab/dashboard/update.sh` from a 10-minute cron job on aifoundry2) | `4406691d-54ff-4e6c-ba53-15aca104b74b` | public | not mirrored | Rendered from live data every 10 minutes, so there is no file to compare. Private when created; public since 30 September at the owner's word ("AI Foundry pages should be public"): every run checks the space and shares it public again if it is not (`"visibility": "private"` in `~/.config/lab-dashboard/config.json`, or `LAB_DASH_VISIBILITY=private`, restores the private guard). It names lab users (login names, activity, card use); the collector still drops addresses, command lines and paths. The code and the page template are in `tools/lab/dashboard/` (README.md); the data never enters the repository. |
| [AI Foundry lab: history](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-history) (2 Oct: hour, day and week graphs of the three machines and their cards, republished by `tools/lab/history/update.sh` from a 5-minute cron job on aifoundry2; linked from the dashboard) | `fca10a2b-075d-43ba-a9b5-1f145ca0cbe1` | public | not mirrored | Rendered every 5 minutes from the records the live collectors keep on each machine (`~/live/history/`), so there is no file to compare. Machine readings and card telemetry only: no user names. |
| [AI Foundry lab, 2 October 2026: what changed](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-2-october) (2 Oct: the maintenance session's report of the day: the live dashboard and history, aifoundry2's idle runaway, aifoundry1 card 0 back in service, the three-step new-user flow, open items, commits) | `5e340312-edf4-4661-944a-10b3fe00a3c7` | public | `docs/reports/2026-10-02-aifoundry-lab-day.html` | file |
| [AI Foundry Discord map](https://spacesheep.dev/@yaroslavvb/aifoundry-discord-map) | `c6433479-e2a7-4c9d-bcef-b45bbd1709fd` | public | not mirrored | Not part of this line of work; listed because its slug starts like this set's. Public (the owner, 26 September). |
| [Influence functions: Hessians, cost, sketching, and weak factoring](https://spacesheep.dev/@yaroslavvb/influence-functions-hessians-sketching-weak-factoring) (18 Sep, the influence-functions technical report) | `44996c6f-fab6-4d48-950d-8ee09c3f4ee7` | public | not mirrored | The report that [Influence functions on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions) starts from: that page links it three times (`sources/influence-on-et.body.html`), and `data/2026-09-25-influence-on-et/README.md` once. Its source belongs to the influence-functions work, not this repository; listed so that `check-mirror.py` checks it stays public (public on 27 September, `spacesheep list`). |

### Private: listed, not mirrored

| Page | Space | Visibility | Repo file | Why |
|---|---|---|---|---|
| aifoundry2 power cycle: instructions for the owner's Intel agent (1 Oct, made by another session) | `d8070e18-98fb-467c-aa57-a1b243723442` | private | not mirrored | Operational instructions for the owner's own agent, with access details: never public (AGENT.md §10). It went out public on 1 Oct at 14:13 PDT though its own description says private; the next check-mirror run warned, and it was set private at about 17:55 the same day |
| Notes of a conversation with David Kanter (R9, 20 Sep) | `f3533740-5ad9-45e1-927c-098dbbe5c210` | private | not mirrored | A personal memo quoting a private conversation; private and unlinked since 24 September (the owner's decision). The DVFS page and R9 describe it in words. |

<!-- mirror:end -->

The account also holds spaces that are not part of this work (plans, notes, other projects). They are not listed.

## How each page is built

Edit the source named here, never the generated HTML. The source-built pages share
`docs/reports/sources/report.template.html` and the chart toolkit `docs/reports/sources/chartkit.js`; the
standalone pages carry a pasted copy of the toolkit (`python3 scripts/paste-chartkit.py PAGE`, and `--check`). The
build prerequisites are in [`docs/getting-started.md`](../getting-started.md) §8 (Python 3 with numpy, and `npm ci`
once for mathjax-full).

| Page | Source | Final build step (from the repository root) | Earlier steps |
|---|---|---|---|
| Chip diagram (27 Sep) | `sources/chip-diagram.*` | `python3 docs/reports/data/2026-09-27-chip-diagram/build_facts.py` (writes `facts.json` from the sourced research files beside it; it reads the hub's data, `2026-09-27-pcie/pcie.json` and, since 29 September, `2026-09-29-nocr/raw/<card>/summary.json`, `2026-09-29-pcie2/pcie2.json` with its `dev-aifoundry1-c1.md`, and `2026-09-29-memp2/val-aifoundry3/memp2.json`, `val-aifoundry2/memp2.json` (the third card, since 30 September) and `dev-aifoundry1-c1/memp2.json`), then `python3 scripts/build-report.py chip-diagram docs/reports/data/2026-09-27-chip-diagram/facts.json docs/reports/2026-09-27-et-soc1-chip-diagram.html`. Since 30 September (the deep zoom) build_facts.py also reads `research/inside.json`, `research/outside.json` and `research/outside-geo.json` through `research/deepzoom.py`, the memory levels' `facts.json` (the facts and numbers that `sources/circuitkit.js` cites) and the images in `docs/reports/ladder-img/` (named `chip-diagram-img/` until 1 October; their sha256 into the manifest); the page script pulls in `sources/chip-diagram.outside.js` and `sources/circuitkit.js` with `/*@include …*/` lines, which build-report.py expands. Build order (1 October): `research/build_inside.py` and `research/build_outside.py` (each rewrites its json; build_inside.py reads this page's `facts.json`, and `make_geo.py` needs the Census and Natural Earth files its header names), then `build_facts.py`, then the page; the memory levels' `build_facts.py` reads this `facts.json` (chip:mesh.grid, L40, L42, L104, L105, mesh.logical-map, with their topic, value and unit) and this one reads theirs: all are fixed points, so after a change rerun build_inside.py and build_facts.py once more and check that rebuilding the memory levels' `facts.json` leaves it unchanged. Deploy as a folder: the built page as `index.html` beside a copy of `ladder-img/`. Since 1 October (the shared ladder, DESIGN in the work directory, `docs/reports/data/2026-10-01-ladder/README.md`): first `python3 docs/reports/data/2026-10-01-ladder/build_ladder.py` (the ladder's scales and facts, from its `research/`, among them `research/circuits.json`, the textbook constructions that `research/build_circuits.py` writes; `--check`), which `research/deepzoom.py` reads; `build_facts.py` then also writes `docs/reports/ladder-img/ladder-data.json` (the deep zoom's facts, fetched by the page; its sha256 into `facts.json` `lazy`); the page script pulls in the shared `ladder-core.js`, `ladder-panel.js`, `ladder-outer.js`, `circuitkit.js`, `ladder-mem.js`, `ladder-inner.js`, `ladder-circuits.js` (since the owner's second update of 1 October: the textbook constructions, and every part's way further in) and the chip's own `chip-diagram.blocks.js`, and the body `ladder.css`. Since the fixes of 1 October (evening) the page ships its script without the comments that take whole lines (`"strip_comments": true` in its meta.json; build-report.py, the sources keep them), and `research/make_circuitkit.py --check` exits 1 if `sources/circuitkit.js` no longer matches the memory levels' kit it copies (the provenance lines aside) | `python3 docs/reports/data/2026-09-27-chip-diagram/research/make_asks.py` (writes `research/asks.json`; it reads the same nocr, pcie2 and memp2 files); rerun both after nocr's, pcie2's or memp2's `reduce.py` |
| Memory levels (28 Sep) | `sources/memory-levels.*` | `python3 docs/reports/data/2026-09-28-memory-levels/build_facts.py` (writes `facts.json` from the sourced research files in `research/` beside it; it reads the hub's data for the rungs its asks link to, the chip diagram's `facts.json` for the chip-scale layout and, since 28 September, the energy manual's `manual.json` for the rail splits of three cards), then `python3 scripts/build-report.py memory-levels docs/reports/data/2026-09-28-memory-levels/facts.json docs/reports/2026-09-28-et-soc1-memory-levels.html`. Since 1 October (the shared ladder, part 2: the page hosts the chip diagram's path camera beside its own) build it after the chip diagram's `facts.json`: `build_facts.py` copies that file's `scales`, `geo`, `img`, `onum`, `outside`, `ring` and `lazy` blocks, and the chip's facts the scales cite, into its `ladder` block; the page script includes `sources/memory-levels.ladder.js`, which includes the shared `ladder-core.js`, `ladder-outer.js`, `ladder-mem.js`, `chip-diagram.blocks.js`, `ladder-inner.js`, `ladder-circuits.js`, `ladder-panel.js` and the page's own `memory-levels.nodes.js`, `memory-levels.links.js` and `memory-levels.hand.js`, and the body `ladder.css`; deploy as a folder, the built page as `index.html` beside a copy of `ladder-img/`. Since the fixes of 1 October (evening) the page ships its script without the comments that take whole lines (`"strip_comments": true` in its meta.json) | none; rerun both after a change to the hub's `.improvements` (the rung numbers, titles and anchors its asks link to) or to `manual.json` |
| Heat placement (28 Sep) | `sources/heat-placement.*` | `python3 docs/reports/data/2026-09-28-heat-placement/build_heat_data.py` (writes `heat.json` from the raw blocks, `val.json`, `tools/claims-v3/hp/` and the DVFS page's `dv2.json`; `--check` exits 1 if it is stale), then `python3 scripts/build-report.py heat-placement docs/reports/data/2026-09-28-heat-placement/heat.json docs/reports/2026-09-28-et-soc1-heat-placement.html` | the reductions and `val.json` (`tools/claims-v3/hp/reduce.py`; the data README, "How to reproduce"); never edit the heat-placement lock's files (`tools/claims-v3/hp/prereg/PREREG.md`) |
| The effect of overheating (28 Sep) | `sources/effect-of-overheating.*` | `python3 docs/reports/data/2026-09-28-overheating/build_overheat_data.py` (writes `overheat.json` from E53's `reductions/`, the analyses in `analysis/`, `sources.json`, and the DVFS page's `dvfs.json` `v3.sp_readouts`; refuses a cited source key missing from `sources.json`), then `python3 scripts/build-report.py effect-of-overheating docs/reports/data/2026-09-28-overheating/overheat.json docs/reports/2026-09-28-effect-of-overheating.html` | `python3 tools/claims-v3/oh/reduce.py --all --data docs/reports/data/2026-09-28-overheating/raw --out docs/reports/data/2026-09-28-overheating/reductions` and `python3 docs/reports/data/2026-09-28-overheating/extras.py` (E53); `for s in max_temps correct_vs_temp timing_vs_temp hot_minus_mean idle_vs_temp runaway events_vs_temp derived; do python3 docs/reports/data/2026-09-28-overheating/scripts/$s.py > docs/reports/data/2026-09-28-overheating/analysis/$s.txt; done` (they read all of docs/reports/data, about 1 min; rerun after new telemetry lands) |
| Without a heatsink (30 Sep) | `sources/esperanto-without-heatsink.*` | `python3 docs/reports/data/2026-09-30-without-heatsink/make_page_data.py` (writes `page.json`; it imports `nohs_calc.py` and stops if the model's printout no longer matches `nohs_calc.out`; `--check` exits 1 if `page.json` is stale), then `python3 scripts/build-report.py esperanto-without-heatsink docs/reports/data/2026-09-30-without-heatsink/page.json docs/reports/2026-09-30-esperanto-without-heatsink.html` | after a change to the model, `nohs_calc.py > nohs_calc.out` and `card0_guard.py > card0_guard.out`, and since the low-clock section (30 Sep evening) `imaging_calc.py`, `lowclock_calc.py` and `lc_plan_calc.py` in that order (the data README; a few minutes, `nice -n 19`) |
| Over the PCIe link (27 Sep) | `sources/pcie-link.*` | `python3 scripts/build-report.py pcie-link docs/reports/data/2026-09-27-pcie/pcie.json docs/reports/2026-09-27-et-soc1-pcie-link.html` | `python3 workloads/pciebench/reduce_pcie.py docs/reports/data/2026-09-27-pcie/raw --prereg docs/reports/data/2026-09-27-pcie/PREREG.md --out docs/reports/data/2026-09-27-pcie/pcie.json --md docs/reports/data/2026-09-27-pcie/results.md`; then the chip diagram's `research/build_facts_v2.py` and `build_facts.py`, which read `pcie.json` |
| Hub (A2) | `sources/limits-of-observability.*` (text and data) | in this order: `python3 tools/ettelem/sync_hub_data.py`, then `python3 tools/ettelem/v3_counts.py` (the "Checked on three cards" counts in 18 page sources, from the hub's data), then the page builds: `python3 scripts/build-report.py limits-of-observability docs/reports/sources/limits-of-observability.data.json docs/reports/2026-09-20-et-soc1-limits-of-observability.html`, and every page whose source `v3_counts.py` changed | rerun `sync_hub_data.py` after regenerating any file it reads (`--check` exits 1 if stale, and also runs `v3_counts.py --check`); after a change to `.improvements`, the chip diagram's and the memory levels' `build_facts.py` read its rungs again |
| Energy manual (A15) | `sources/energy-manual.*` | `python3 scripts/build-report.py energy-manual docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-23-energy-manual.html` | 04-artifacts.md A16, "Rebuilding the energy data, in order" |
| Heat per mm (A17) | `sources/heat-per-mm.*` | `python3 scripts/build-report.py heat-per-mm docs/reports/data/2026-09-24-wire-energy/report.json docs/reports/2026-09-24-heat-per-mm.html` | 04-artifacts.md A18: `analyze_wire.py` (24 September runs), `analyze_wire_v3.py` (the version-3 check's passes, `wire3.json`), then `build_wire_report.py --wire ... --wire3 ...` |
| DVFS (A11) | `sources/dvfs-leakage.*` | `python3 scripts/build-report.py dvfs-leakage docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json docs/reports/2026-09-22-dvfs-leakage.html` | E19 in 03-experiments.md: `analyze_dvfs.py ... --v3 docs/reports/data/2026-09-25-claims-v3` (04-artifacts.md, "Rebuilding the version-3 data"), then `build_cards_data.py --merge` |
| Power and temperature (A3) | `sources/power-temperature.*` | `python3 scripts/build-report.py power-temperature docs/reports/data/2026-09-20-power-aifoundry2/summary.json docs/reports/2026-09-20-et-soc1-power-temperature.html` | `tools/ettelem/summarize_power_session.py DATA --out DATA/summary.json` |
| Horace (A4), Why low power (A5) | `sources/horace-experiment.*`, `sources/why-low-power.*` | `tools/ettelem/finish_horace.sh` (its last two lines build both pages from `docs/reports/data/2026-09-21-horace-aifoundry2/report.json` and `lowpower-report.json`) | the whole Horace line, inside the script; the GIFs too. The version-3 check's three cards come in through the script's `build_cards_data.py --v3` (section 10, merged into `report.json` only) and `build_lowpower_report_data.py --v3` lines |
| Hot line (A13) | `sources/hot-line.*` | `python3 scripts/build-report.py hot-line docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json docs/reports/2026-09-22-hot-line.html` | 04-artifacts.md A16: `analyze_hotline_power.py`, then `analyze_hotline.py --v3 docs/reports/data/2026-09-25-claims-v3/raw --power ... --context ... --barrier ... --stop-runs ...` (since 26 September the three cards' V3-LAT passes; the 22 September sweeps stay as history) |
| On-chip relay (A14) | `sources/on-chip-relay.*` | `python3 scripts/build-report.py on-chip-relay docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json docs/reports/2026-09-22-on-chip-relay.html` | `workloads/onchip/analyze_onchip.py` over the three cards' V3-LAT relay sweeps with `--cards aifoundry2,aifoundry3,aifoundry1-c1` (04-artifacts.md, "Rebuilding the version-3 data"; E25 gives the 22 September form) |
| Influence functions | `sources/influence-on-et.*` | `python3 scripts/build-report.py influence-on-et docs/reports/data/2026-09-25-influence-on-et/analysis.json docs/reports/2026-09-25-influence-on-et.html` | `python3 docs/reports/data/2026-09-25-influence-on-et/make_analysis.py` |
| Sparse parity (29 Sep) | `sources/sparse-parity.*` | `python3 docs/reports/data/2026-09-29-sparse-parity/make_page_data.py` (writes `page.json` beside it from E59's committed results, with numpy, and stops if a number the prose quotes no longer matches the data), then `python3 scripts/build-report.py sparse-parity docs/reports/data/2026-09-29-sparse-parity/page.json docs/reports/2026-09-29-sparse-parity.html` | none: `make_page_data.py` reads the results as committed (`workloads/sparseparity/data/2026-09-29-aifoundry3-{card,card-m4,m5-energy}/`, the CPU runs in `workloads/sparseparity/cpu/data/2026-09-29-aifoundry3-r/` and `workloads/sparseparity/data/2026-09-29-aifoundry3-sysemu-m5/cpu2s.jsonl`, SP3's sweep in `workloads/sparseparity/proto/data/2026-09-28-aifoundry1/`, `tools/cycle_model.py` and `docs/research/sparse-parity/design_model.py`); its docstring lists each block's source |
| Memory anatomy (A1) | `workloads/memprobe/report_template.html` | `python3 workloads/memprobe/build_report.py docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-19-et-soc1-memory-anatomy.html` (its `--v3` defaults to `docs/reports/data/2026-09-26-memprobe-3cards/cards.json`) | E1 in 03-experiments.md; the three cards: `workloads/memprobe/analyze.py --v3 docs/reports/data/2026-09-25-claims-v3/raw --v3-passes docs/reports/data/2026-09-25-claims-v3/results/mem.passes.json --out docs/reports/data/2026-09-26-memprobe-3cards/cards.json` |
| Memory hierarchy, On-chip communication, Matmul efficiency and the Test drive's ladder, Sparse compute, Ridge points | the prose in the HTML; an `--embed` script rewrites only the embedded JSON | the commands in 04-artifacts.md, "Rebuilding the standalone pages" (memory hierarchy with `--v3 .../raw`, on-chip communication with `--v3 docs/reports/data/2026-09-25-claims-v3`; sparse compute reads the check by default), then `python3 scripts/paste-chartkit.py PAGE` | the energy data (04-artifacts.md A16) for the pages that read `manual.json` or `reruns.json` |
| Spatial temperature brief, L2 mainline-starvation brief | the HTML, by hand | none (`python3 tools/ettelem/host_temp_fields.py --check docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html` tests the brief's two constants) | none |
| The two aifoundry1 pages | the HTML, by hand (standalone) | none | the evidence is in `docs/reports/data/2026-09-25-aifoundry1/` |
| New user? Start now (30 Sep) | `docs/lab-start/START.md` (the brief) and `sources/lab-start.*` | `python3 docs/lab-start/make_page_data.py` (writes `docs/reports/data/2026-09-30-lab-start/brief.json` from START.md), then `python3 scripts/build-report.py lab-start docs/reports/data/2026-09-30-lab-start/brief.json docs/reports/2026-09-30-aifoundry-lab-start.html` | none: the brief is edited by hand; push it before deploying, since the page links its raw file on GitHub |
| Session timeline (27 Sep) | `sources/session-timeline.*` | `python3 tools/timeline/sanitize_extracts.py` (scans the eight committed extracts in `docs/reports/data/2026-09-27-session-timeline/` and exits 1 if anything private is left; with the local privacy table it first rewrites them with the page's redactions), `python3 tools/timeline/build_timeline_data.py` (writes `timeline.json` beside them), then `python3 scripts/build-report.py session-timeline docs/reports/data/2026-09-27-session-timeline/timeline.json docs/reports/2026-09-27-session-timeline.html` | the extracts themselves come from the session's transcripts and the lab machines' queue logs, which are not in the repository: `tools/timeline/README.md` gives the order of the extraction scripts and their environment variables |

On 2026-09-25 each of the ten `build-report.py` steps above rebuilt its committed page byte for byte from the
committed data (hub, energy manual, heat per mm, DVFS, power and temperature, Horace, why low power, hot line,
on-chip relay, influence functions). 04-artifacts.md, "The 25 September validation", records the same for the rest.
Since 26 September most pages' data also carry the version-3 check's three cards, through options on the same
generators; the commands, in order, are in 04-artifacts.md, "Rebuilding the version-3 data", and on that day each
reproduced its file in the tree byte for byte.

## The GitHub Pages mirror

Since 1 October 2026 (the owner's request: the chip diagram mirrored to GitHub Pages, where links with `#anchors` and
`?flow=` work directly), the two interactive pages are also served from branch `gh-pages`:
https://yaroslavvb.github.io/et-soc1-prototyping/ (an index), `chip-diagram/` and `memory-levels/`. The branch is
generated: `tools/publish-gh-pages.sh` builds it from the committed pages of HEAD (with `docs/reports/ladder-img/`
beside each page: since the shared ladder's part 2 the memory levels fetch it too) and force-pushes one fresh commit,
so run it after each deploy of either page and never edit the branch by hand (`--dry-run` builds into
`~/claude/work/gh-pages-site` only). The spacesheep pages stay canonical; the mirror carries the commit it was built
from in its index.

## Deploying one page

The rules behind each line are in 04-artifacts.md, "Publishing notes, learned the hard way".

```bash
P=docs/reports/2026-09-22-hot-line.html; UUID=ac439287-4503-42c7-88e7-b5d3e3b64b06; SLUG=et-soc1-hot-line
D=$(mktemp -d); cp "$P" "$D/index.html"     # the Horace page: also copy its three GIFs into $D
spacesheep deploy "$D" --space "$UUID" -m "<what changed>"   # pass --slug "$SLUG" whenever you pass --title
rm -rf "$D"                                  # takes the .spacesheep.json pin file with it
spacesheep list | grep "$SLUG"               # visibility and address unchanged?
python3 scripts/check-mirror.py --only "$SLUG"
```

- Deploy from a directory of its own, never from `docs/reports/` itself: the CLI writes a `.spacesheep.json` pin file
  into the deployed directory, and a stale pin once published one report over another (22 September).
- Always pass `--space` on an update. Passing `--title` without `--slug` re-slugs the space and breaks its address.
- A new page: pass `--title`, `--slug`, `--emoji`, `--description` and **`--visibility public`** on the first deploy.
  The owner's rule since 29 September: the experiments are for sharing, so every new report page is public by
  default (the CLI's own default is private; 1.9.1 has no "unlisted" level, and `public` means anyone with the link).
  Keep a page private only when it holds something that must not be public (AGENT.md §10: access paths, privileges,
  other people's accounts, a private conversation). Then add its row here with the uuid from `spacesheep list --json`.
  An existing private page: `spacesheep share <uuid> --visibility public`.
- A deploy can change a space's visibility. Compare `spacesheep list` with this file after every deploy; changing an
  existing page's visibility (other than publishing a new report page as above) is the owner's call.
- Commit the page file and this file together with the deploy, so the repository and the live page never disagree
  for long.
- Push before you deploy. The pages link files on GitHub by `tree/main` and `blob/main` addresses (the version-3
  check's `raw/` and `results/`, `results/gs.json`, `results/tel.json`, `workloads/enercat/analyze_wire_v3.py`, …), and
  a link to a path that exists only on a branch answers 404. Merge or push the branch to `main` first; for any path a
  page links, `git ls-tree origin/main <path>` must list it.

## Checking that live equals repo

```bash
python3 scripts/check-mirror.py                  # every page; exit 0 only if every public page is equal
python3 scripts/check-mirror.py --only et-soc1-hot-line --via https
```

For each public page it fetches the live `index.html` and compares it with the repo file after removing the host's
`data-ss-id` attributes. With a spacesheep key configured (`spacesheep login`, or `SPACESHEEP_KEY`) it reads the
stored file with `spacesheep read <uuid> index.html -o <dir>`. It also reads the account's `spacesheep list --json` and
compares every row's visibility and slug with this file, and warns about any public space whose slug starts like
this set's (`et-soc1`, `etsoc1`, `aifoundry`, `2026-09-22-et-soc1`) that is not listed here as public. Since the
account passed 50 spaces that list is cut: the CLI shows only the 50 most recently updated, so a row missing from it is
unchecked rather than deleted ([`../findings/04-artifacts.md`](../findings/04-artifacts.md), "Publishing notes", 5 October
2026; reported to the spacesheep team). Without a key it fetches the raw page
anonymously over HTTPS (`https://<uuid>.spacesheep.app/`) and also removes what the host inserts just before
`</body>` (its print style, print mark and viewer scripts), after checking that the insertion holds only `<style>` and
`<script>` blocks and the host's own `ss-` elements, and that it is the same on every page. Folder files (the
Horace GIFs) are always fetched over HTTPS and compared byte for byte, because `spacesheep read` returns binary files
mangled. For every private row with a uuid it checks that neither address serves the page anonymously. Exit status: 0 when
everything matches, 1 on any difference (content, visibility or a private page served anonymously), 2 when a page
could not be reached and nothing else was wrong.

**Last check: 2026-09-30, 16:15 PDT**, after the memory levels' and the chip diagram's smooth camera, the memory levels'
player bar and the chip diagram's beginner panel (Q74-Q76): both equal to their files; 31 of 32 mirrored public pages
equal, exit 1 for work outside that pass: the hub (`et-soc1-limits-of-observability`) differs from its file, and the lab
dashboard, listed here as private, is served publicly (its visibility is the owner's call).

**Earlier check: 2026-09-29, 02:30 PDT**, after the major pass (E55-E58 on the hub, the chip diagram's y-first reads and
host writes through the L3 homes, memory levels, PCIe, power and temperature's filter, DVFS's DV2 validation, heat per
mm's NV and routes, the TODO page, the session timeline refreshed to 29 September, and the lab report's statuses):
28 of 28 mirrored public pages equal to their files, no warnings, exit 0 (the session timeline listed since `6bbf0f3`).

**Earlier check: 2026-09-28, 17:37 PDT**, after the superseded energies were folded into the pages (memory anatomy,
memory hierarchy, on-chip communication, matmul efficiency, sparse compute, and their leftovers on memory levels, the
energy manual, power and temperature, why low power and the hub), the chip diagram's flow B (Broadcast) and heat per
mm's Q63 section: 27 of 27 mirrored public pages equal to their files, exit 0; one warning: the session timeline is
public on spacesheep but not listed here (its page and tools are not in the repository; the owner's call).

**Earlier check: 2026-09-28, 13:57 PDT**, after the effect-of-overheating page (new, public), the hub (the page in §1's
index, E53 in §7, its asks as rungs 45-46 with rungs 13, 24 and 42 extended), the chip diagram and the memory levels
(both re-read the hub's rungs), through `spacesheep read` with a key: 27 of 27 mirrored public pages equal to their files,
no warnings, exit 0 (no deploy needed a retry).

**Earlier check: 2026-09-28, 09:20 PDT**, after the heat-placement page (new, public), the TODO sweep's 21 pages, the
DVFS page and the hub (aifoundry2 restored, E52, the heat page in the index): 26 of 26 mirrored public pages equal to
their files, no warnings, exit 0 (three deploys needed a retry after "fetch failed").

**Earlier check: 2026-09-28, 05:08 PDT**, after the memory-levels page (new, public), the hub (rungs 37-44, E51, the
firmware caveat), the memory anatomy page, the DV2 pages (DVFS, Horace, why low power, power and temperature, the
energy manual) and the chip diagram's smooth zoom: 25 of 25 mirrored public pages equal to their files, no warnings,
exit 0.

**Earlier check: 2026-09-27, 22:05 PDT**, after deploying the page pass (`b083d80`: correctness fixes and new charts on 18
pages): 24 of 24 mirrored public pages equal to their files, no warnings, exit 0 (the testdrive page needed a second
deploy: the first one returned no confirmation and the check found the old page).

**Earlier check: 2026-09-27, 18:20 PDT**, after the chip diagram v2, the new PCIe page and the hub: 24 of 24 mirrored public pages
equal to their files, no warnings, exit 0.

**Earlier check: 2026-09-27, 14:40 PDT**, after deploying the merge (the version-3 three-card results, the review's chart
and collapsible-depth passes, E48, the in-depth audit's fixes) and the new chip diagram, through the CLI: 23 of 23
mirrored public pages equal to their files, no warnings, exit 0.

**Earlier check: 2026-09-26, 23:26 PDT**, after the collapsible-depth pass, through `spacesheep read` with a key: 22 of 22
mirrored public pages equal to their files, no warnings, exit 0.

**Earlier check: 2026-09-26, 17:25 PDT**, after the chart pass, through `spacesheep read` with a key: 21 of 21 mirrored
public pages equal to their files; exit 1 because the review's TODO space (`et-soc1-review-todo`), deployed private,
was public although deployed private, and two other spaces were public but not listed here as public. The
owner confirmed all three as public the same day, and this file now lists them so.

**Previous check: 2026-09-26, about 15:30 PDT**, against the files at `299fac8` (the 26 September visualization pass is
live), anonymously over HTTPS only: that session had no spacesheep key, so `spacesheep list` was not read. 21 of 21
mirrored public pages equal to their files (the host's insertion, 16,757 B, identical on every page), the Horace GIFs
3 of 3 equal, the viewer addresses of all 22 public rows answering 200, the private memo not served anonymously; exit 0.

**Last check both ways: 2026-09-25, 21:46 PDT**, against the files at `bde52e0` (read-only):

| | Through `spacesheep read` (key configured) | Anonymously over HTTPS |
|---|---|---|
| Mirrored public pages equal to their files | 21 of 21 | 21 of 21 (the host's insertion, 16,757 B, identical on every page) |
| The Horace GIFs | 3 of 3 equal | 3 of 3 equal |
| Viewer addresses answering 200 anonymously | 22 of 22 public rows | 22 of 22 |
| Visibility and slug as listed here (`spacesheep list --json`) | every row with a uuid | (read in the same run) |
| The private memo | not served anonymously | not served anonymously |
| Exit status | 0 | 0 |

Rerun at 21:57 PDT through `spacesheep read` with CLI 1.9.1 (the CLI on aifoundry2 was updated from 1.5.1 at 21:52),
and anonymously from a fresh clone with no key: the same result, 21 of 21 equal, exit 0.

The first run warned about two public spaces in the account whose slugs start like this set's but that this file does
not list as public; they are for the owner to decide on. Negative controls, run the same day on altered copies of
three pages, were all caught: a one-character change (`differs`, with the line), an extra element before `</body>`, an
extra `<script>` at the end of the body (over HTTPS, by the insertion's hash), a changed GIF byte, a public page listed
as private (`SERVED ANONYMOUSLY` and a visibility mismatch) and a wrong slug (a 302 and a slug mismatch).

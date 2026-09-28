# Anatomy of a memory access, interactively: design

Written 27 September 2026 for the builders of this page. It covers the page's structure, one engine that runs five
data-driven scenes, a plan for each level (what is drawn at each scale, from which facts, and how each access
animates), the labelling rules, accessibility, sizes, and the asks for the team.

**How to read the citations.** A fact id (`l1.lram`, `l2.macro.data`, `l3.lat-fit`, `scp.vmin-table`,
`dram.ctl.tRCD`, …) points to a row of one of the five facts files below. Each row carries its own source (a repo file
and line or field, a manual PDF page, or an RTL file and line) and its kind. Statements not backed by a fact id cite
their file and page directly.

**Inputs** (the session's scratchpad, `memlevels/`; kept here in `research/`):

| File | Shape | Facts (spec / measured / derived / generic / unknown) | Steps |
|---|---|---|---|
| `facts-l1.json` | list; steps have topic `sequence/<name>` | 65 (30 / 12 / 8 / 8 / 7) | 26: load-hit 6, store-hit 6, miss-refill 7, scratchpad-read 3, tensorload 3, refresh 1 |
| `facts-l2.json` | list; steps have topic `access-sequence` | 85 (52 / 16 / 10 / 1 / 6)¹ | 30: load-hit 13, load-rbuf-hit 4, store-writeback 6, miss-refill 5, no-refresh 2 |
| `facts-l3.json` | object: facts, access_sequence, asks, meta | 84 (34 / 21 / 9 / 12 / 8) | 18: load_hit 9, store 3, miss_and_refill 4, atomic 1, refresh 1 |
| `facts-scp.json` | object: meta, facts, access_sequence, unknowns | 91 (33 / 25 / 17 / 9 / 7) | 32: load_own 11, store_own 5, load_remote 6, store_remote 3, fill 2, atomic 2, miss_refill_refresh 3 |
| `facts-dram.json` | list; steps have field `seq` | 83 (36 / 19 / 12 / 11 / 5)¹ | 22: load 11, row-hit 1, row-conflict 1, store 5, refresh 4 |

¹ Counted without the steps. The files' own kind totals include them: 115 rows in L2, 105 in DRAM. One DRAM step,
`dram.seq.refresh.04`, is itself of kind unknown.

The builder scripts `build_facts_{l1,l2,l3,scp,dram}.py` sit next to these files or in `l1/`, `l2/` and `scp/`.

**Reference for the look and the interaction:** the chip tour, `docs/reports/sources/chip-diagram.{body.html,script.js,meta.json}`
and its data `docs/reports/data/2026-09-27-chip-diagram/` (then in the et-soc1-merge worktree). The tour is being
polished while this page is built. **Re-read its latest files when you copy the engine**, and record the script's
mtime and line count in a comment at the top of `memory-levels.script.js`.

---

## 0. Deliverables and constraints

All files are new, in the worktree et-soc1-pages5 (branch pages-v5):

| File | What |
|---|---|
| `docs/reports/sources/memory-levels.meta.json` | `{"title": "Anatomy of a memory access, interactively", "description": "…"}` (one sentence, like the chip tour's) |
| `docs/reports/sources/memory-levels.body.html` | the stage markup, its CSS and the prose (§1.4) |
| `docs/reports/sources/memory-levels.script.js` | one engine and five scenes (§2), in one IIFE like the chip tour |
| `docs/reports/data/2026-09-27-memory-levels/research/` | copies of the five facts files and their builders, kept as a record (as the chip tour keeps `research/`) |
| `docs/reports/data/2026-09-27-memory-levels/build_facts.py` | merges them into `facts.json` (§2.1), with the checks in §2.2 |
| `docs/reports/data/2026-09-27-memory-levels/facts.json` | the page's data (`D`) |
| `docs/reports/2026-09-27-et-soc1-memory-levels.html` | built by `scripts/build-report.py memory-levels docs/reports/data/2026-09-27-memory-levels/facts.json docs/reports/2026-09-27-et-soc1-memory-levels.html` |

Do not edit any existing file. That includes every other page and source, `chartkit.js`, `report.template.html`, the
hub's `limits-of-observability.*`, the anatomy page (`workloads/memprobe/report_template.html` and its data) and the
chip tour. The coordinator adds the links to this page and the hub's asks (§13). Do not commit, deploy or ssh, and do
not touch the cards. The publish slug is the coordinator's call; `et-soc1-memory-levels` is the proposal.

The page is the owner's request: "For Anatomy of a memory access, do detailed interactive diagrams similar to the
interactive ET-SoC-1 tour … down to individual transistors … all levels of the memory system separately (L3 gets its
own diagram, so does DRAM)." It is a companion to the anatomy page (`workloads/memprobe/report_template.html`,
`#trace-one-load` … `#what-would-split-it-further`), not a replacement for it.

---

## 1. Page structure

### 1.1 The stage (one screen, like the chip tour's `#stage`)

It uses the same grid as the chip tour: rows `head / body (drawing + panel) / bar / caption`, `height: 100dvh`, and
nothing scrolls inside it except the panel's list.

- **Header.** The `h1` has a long form ("Anatomy of a memory access, interactively") and a short one ("Memory
  access"), with the same `.t-long`/`.t-short` swap. Beside it are the **level tabs** (§1.2) and the **access buttons**
  of the current level: its sequences, as `aria-pressed` buttons like the chip tour's flow buttons.
- **Body.** The drawing is `<svg id="mem">`, with one viewBox per scale frame (§2.3). The details panel (`aside.pn`)
  has a scrolling body and a fixed legend at the foot. The legend shows the three badges, the part colours and the
  rail bands.
- **Stage bar.** It has the chip tour's controls, in its order: Play, ←, the steps of the running access, →, Follow
  (C), **Dive** (V, new: §2.5), a separator, Tour (T), Present (F) and Panel (P).
- **Caption row.** On the left is the scale control: a path of scale names for the current branch, with − and +
  (§2.3), then the kick line and the tour dots. On the right are the caption (up to 32 px) and a two-line sub-caption,
  both `aria-live`.
- **Overlays.** These are reused from the chip tour: skip links, the frame's keyboard hint, the toast, and the source
  tooltip `#srctip`. The chip tour's small picture of the die becomes a **context mini-map** (`.pip`). It shows the
  parent scale with the lit part ringed, and it appears when the camera is two or more scales deep (§2.3).

### 1.2 Level tabs and deep links

| Tab | Key | Hash | Long label | Short label (≤ 1450 px) | Accesses (buttons) |
|---|---|---|---|---|---|
| L1 | 1 | `#l1` | L1 data cache | L1 | Load hit · Store hit · Miss → L2 · VPU scratchpad read · TensorLoad · Refresh? |
| L2 | 2 | `#l2` | L2 (shire cache) | L2 | Load hit · Read-buffer hit · Write-back · Miss → L3 · Refresh? |
| L3 | 3 | `#l3` | L3 (across the mesh) | L3 | Load hit · Write-around · Miss → DRAM · Atomic · Refresh? |
| Scratchpad | 4 | `#scp` | Scratchpad | Scratch | Own load · Own store · Remote load · Remote store · Fill · Atomic · Miss? Refresh? |
| DRAM | 5 | `#dram` | DRAM (LPDDR4X) | DRAM | Load (closed row) · Row hit · Row conflict · Store · Refresh |

- **Tab semantics.** The tabs are a `role="tablist"` with `role="tab"`, `aria-selected`, `aria-controls="stage-view"`
  and roving tabindex. While focus is in the tab list, Left, Right, Home and End move between tabs; everywhere else
  Left and Right step the access (§1.3). Number keys 1-5 pick a level from anywhere.
- **Hash grammar.** `#<level>[/<access>[/<step>[/<scale>]]]`, for example `#l2`, `#l3/load-hit`, `#dram/refresh/2`,
  `#l1/load-hit/4/cell`. The levels are `l1 l2 l3 scp dram`. The aliases `#scratchpad`, `#L1`, … are accepted
  case-insensitively. A hash the page does not know is left to the template, whose section anchors (`#asks`,
  `#facts`, …) keep working.
- **Changing tabs.** A tab change calls `history.replaceState` with the new hash, never `location.hash =`, so the page
  does not jump. It then posts `{type: 'ss-hash', hash}` to `window.parent`: that is the template's contract for
  mirroring the fragment into the spacesheep URL (`report.template.html:190-208`, which also forwards an outer
  fragment in on load). On load and on `hashchange`, the script parses the hash, selects the level, and scrolls the
  stage into view.
- **Id collisions (a trap).** No element may have the id `l1`, `l2`, `l3`, `scp` or `dram`. The template auto-ids
  every `h2`/`h3` from its text (`report.template.html:199-201`), so no prose heading may slug to a level id. A
  heading reading just "DRAM" would. Use headings such as "The DRAM level, step by step".
- **Query flags,** as in the chip tour: `?theme=light|dark`, `?panel=off`, `?dive=on|off`, `?tour=1` (start this
  level's tour) and `?tour=all`.

### 1.3 Keyboard map (chip tour keys kept wherever they fit)

| Key | Action |
|---|---|
| 1-5 | level L1, L2, L3, scratchpad, DRAM |
| `[` `]` | previous or next access of this level (the buttons show these keys in their `title`) |
| Left/Right, PageUp/PageDown | previous or next step; during the tour, crossing into the next or previous slide at an access's ends |
| Shift+Left/Right | previous or next tour slide |
| Space | pause or resume everything that moves, the camera included; stepping while paused draws the step's end state |
| + / − (and Backspace) | zoom in along the current branch, or out |
| Enter on a part | zoom into it if it has a child scale, else show its details (Space always shows details) |
| C | Follow: the camera follows the access |
| V | Dive: the camera goes down to the transistors on steps that have a circuit animation |
| T | this level's tour; Shift+T tours all five levels in order |
| Q or Esc | end the tour |
| F | present (full screen, or the stage fills the frame, as in the chip tour) |
| P | hide or show the panel |
| D | light or dark theme |

### 1.4 Prose below the stage

The prose follows the chip tour's order. Headings must not slug to a level id (§1.2).

1. **How to use it.** The keys and the controls, as in the chip tour's `#use`.
2. **What the ET-SoC-1 uses instead of SRAM, level by level.** This section answers the owner's example question
   directly. It is a table (level, storage, what the sources say, kind, source) plus a paragraph on the one
   contradiction. Its rows:
   - **L1 data array:** latch RAM, "4 LRAM (Latch-RAM) blocks of 128 rows x 64 bits" (`l1.lram`: Minion DCache
     Description pdf p.29; datasheet §2.1.1.5 pdf p.9).
   - **L1 tags and TLB:** latch register files (`l1.metadata`, `l1.tlb`).
   - **L1 valid and LRU bits:** flip-flops (`l1.metadata`, `l1.lru`).
   - **Neighbourhood I-cache data:** SRAM, placed in the HV region (`l1.icache-sram`).
   - **Shire cache (L2, L3 and scratchpad):** "SRAM memory panels" named as compiled 1PUHD and 2PUHDRF macros
     (`l2.macro.*`, `l3.macros`, `scp.panel`: Shire Cache Specification v1.1 pdf pp.48, 51). The datasheet counts
     140 MB of on-die SRAM (`l2.sc.chip-total`). The bitcell is **unknown**.
   - **DRAM:** LPDDR4X from Micron (`dram.org.capacity`). The cell is the JEDEC 1T1C, **generic** (`gen.cell`).

   Then the derived reason the L1 cannot be those SRAM panels. The data panel's lowest listed Vmin is 585 mV at trim
   RM0 (`scp.vmin-table`, spec Table 14 pdf p.51). The minion rail the L1 runs on measures 0.517 V at 600 MHz
   (`l1.voltage`). The Neighborhood MAS says SRAM cells "need to be placed in an HV region" (`l1.lv-region`, pdf
   p.14). This reasoning is `et-derived` and asked (ask-not-sram, §13).

   The contradiction: the lab lead said the chip is "not using SRAM". The remark is not recorded in the repo, so the
   page quotes the owner's report of it, attributed to the lab lead. Use the name only if the coordinator decides to.
3. **One load, level by level.** The text version of the five diagrams, written by the script from `D`, like the chip
   tour's `#summary-text`. It gives each level's accesses as ordered lists, with their numbers.
4. **What is documented, what is generic, what is unknown.** Counts by level and kind, from `D`.
5. **What would settle the rest: the asks.** A table with columns part, what is unknown, what would settle it, the ask
   id and the hub row. It lists the new rows and the existing rows that get new effects (§13).
6. **Every fact on this page.** The chip tour's sortable and filterable table, with a Level column and a Kind column
   that shows the badge.
7. **Related reports.** The anatomy page, the memory hierarchy, the chip tour, the energy manual, on-chip
   communication, the relay and the hub.
8. **Sources.** The manuals and the RTL and firmware trees, with the caveats in §12.

---

## 2. The shared framework: one engine, five data-driven scenes

### 2.1 Data: `facts.json` (`D`), built by `build_facts.py`

```
D.meta     {built_from[], counts{level:{kind:n}}, chip_tour{script_mtime, lines}, caveats[]}
D.facts    {"<level>:<id>": {id, level, topic, statement, value, unit, source, kind, badge, cards[], cards_txt,
                              page_link, note, caveat}}
D.steps    {"<level>": {"<access>": {title, measured, steps: [{n, stage, block, action, latency, energy, kind,
                              facts[], circuit: [{el, does, kind, kind_note}]}]}}}
D.num      {"<key>": {v, t, u, f}}          // every number the page prints outside a fact's own statement
D.parts    {"<level>": {"<part>": [fact keys]}}   // the facts each details panel lists
D.asks     [{id, title, question, settles, levels[], facts[], hub: {new|extends: anchor}, state}]
D.rungs    {"<hub anchor>": {rung, what, status}}   // read from limits-of-observability.data.json .improvements
D.layout   the chip tour's .layout (read-only copy: the measured map, the die view, the memory shires), for the
           chip-scale views of L3, the scratchpad and DRAM, with the chip facts it needs copied under "chip:<id>"
D.addr     the default example addresses (a DRAM-region line and a scratchpad line) and their decoded fields per level
D.conflicts [{what, sources[], resolution}]       // §12, shown in the prose and in the relevant panels
```

**Normalisation.** The five files use five step schemas, which the build maps onto the one above:

| Level | Where the steps are | Circuit element fields |
|---|---|---|
| L1 | `circuit` is a string plus `circuit_kind` | becomes one element |
| L2 | list items with `element` / `switches` / `kind` | mapped onto `el`, `does`, `kind` |
| L3 | `access_sequence` | `element` / `action` / `kind` |
| Scratchpad | `access_sequence` | `device` / `switches` / `kind` |
| DRAM | list items with `seq` and `step` | `what` / `kind` |

- **Kinds.** Composite kinds such as `"generic (et-spec that the crossing exists)"` or
  `"generic (cell); et-spec (macros)"` keep their first word as the badge and the rest as `kind_note`, which the panel
  shows. The kinds map onto three **badges**:
  - `spec`, `measured` and `derived` (from `et-spec`, `et-measured`, `et-derived`) become **documented**;
  - `generic` becomes **generic**;
  - `unknown` becomes **unknown (asked)**.
- **Fact keys** are `<level>:<id>`. The id `g.no-refresh` exists in both L1 and L3; it is the only collision among
  485 ids, and the namespacing resolves it. The panel shows the bare id with a level tag.
- **Card coverage.** The free-text `card` strings ("aifoundry2, aifoundry3, aifoundry1-c1 (…)", "not recorded", …)
  become `cards: [a2, a3, a1c1]` plus `cards_txt`, as the chip tour's `CARDS` does.
- **Caveat markers.**
  - A fact whose only source is `external/core-et-main/…` (Ainekko's co-simulated translation) gets
    `caveat: "reimpl"`. The panel shows "re-implementation RTL" beside its badge.
  - A fact from the Shire Cache Specification v1.1 gets `caveat: "spec-v1.1"`, shown once per panel as "spec v1.1,
    Erbium branch; it also documents later chips" (`l2.spec-version`).

### 2.2 Build checks (the build refuses to write `facts.json` if one fails)

1. **Printed numbers.** Every `D.num` entry's text occurs in its fact's statement, or rounds from it. This is the chip
   tour's `build_facts.py` rule (`NUMS`, `rounds_to`). The page prints numbers only through `n(key)` or a computed
   `cn(value, facts)`.
2. **References.** Every step's `facts[]`, every `D.parts` entry and every ask's `facts[]` resolves to a key.
3. **Unknowns and asks.** Every `unknown` fact belongs to exactly one ask in `D.asks`, and every ask names at least one
   fact.
4. **Generic facts.** Every generic fact's statement starts with "GENERIC" or its source says "textbook" or "(GENERIC)".
   The panel always prints the badge, whatever the text says.
5. **One canonical value per quantity.** One number is printed for each quantity that appears in several files. The
   duplicates are listed in §12, and the build asserts that the canonical keys are the ones used.
6. **Hub rows.** `D.rungs` holds the hub rows the asks link to. Proposed new rows (§13) are marked `proposed: true`
   until the coordinator adds them, and the page then links to the hub's list rather than to a missing anchor.

### 2.3 The engine: the chip tour's, copied and generalised

Copy these from `chip-diagram.script.js`, keeping their behaviour and comments. Their names are as in the tour; the
line numbers drift while it is polished.

| Copied | What it gives |
|---|---|
| `CLK` loop, `wait`, `anim`, `every`, `tween`, `CANCEL` and `alive` tokens, `fadeIn`/`fadeOut`/`popIn` | the pausable clock and animation primitives |
| `packet`, `travel`, `pulse`, `ring`, `callout`, `pipe`, `bandChart` | moving packets, trails, rings, callouts and bar charts |
| `goTo`, `zoomWorker`, `zoomSeg`, `planFrom`, `chainSegs`, `strokeKeeper`, `ctxMark`, `dimLevel` | the camera: one ease over a chain of zooms, redirectable, with semantic label fades (`--lab`, `--ctx`) and a packet carried across a zoom |
| `startFlow`, `runFrom`, `showStage`, `playStage`, `markStage`, `goStage`, `restartStage`, `setFollow` | these become `startAccess`, … over `D.steps` |
| `panel`, `pnReveal`, `factLi`, `factsBlock`, `asksBlock`, `askHtml`, `topPage`, `kpi`, `n()`, `cn()`, `src()`, the `#srctip` handlers | the details panel and sourced numbers |
| `STEPS`, `startTour`, `endTour`, `dots`, `highlight`, `setCap`/`fitCap`, `resetCap`, `renderBar`, `playBtn`, `playPause` | the tour and the caption |
| `present`, `setPres`, `presenterWindow`, `SRC_HTML`, `FRAMED`, `kbdHint`, `togglePanel`, `setTheme`/`toggleTheme`, the `keydown` handler | presenting and the global keys |

**Generalise the camera from three fixed layers to a tree of scales per level.** The chip tour hard-codes chip, shire
and minion (`LAYERS[0..2]`, `SF` and `MF` frames, `LOGT` and `LOGM` step lengths).

- **Scale nodes.** Each level defines a tree of scale nodes. Each node is
  `{id, name, parent, frame: {x,y,w,h}, build(inst), targetIn(parentLayer, inst) → rect, inst(addr)}`.
  - `frame` is where the node is drawn: every node uses the chip tour's 1300 × 792 viewBox, VB `{x: -190, y: -84}`,
    so the text classes `.t-lab` (20 units), `.t-sm` (17), `.t-mid` (24) and so on carry over.
  - `targetIn` is the part of the parent's drawing that the zoom grows into this frame.
  - `inst` names the instance, such as bank `PA[7:6]` or sub-bank `PA[9:8]`. Instances share one drawing. Their index
    goes in the title ("Bank 2 · sub-bank 1"), and which row is lit comes from the decoded address (§2.7).
- **Moves.** `planFrom(s, t)` walks up to the common ancestor, then down, with each step's length
  `L = ln(frame.w / target.w)`. `zoomSeg(lo, hi, …)` takes the two layers instead of `lo` and `lo + 1`.
- **Lazy layers.** A layer is built only when the camera enters it, as `buildShire` and `buildMinion` are now. At most
  the current path is kept in the DOM.
- **The scale control** (`.zc`) shows the current branch as buttons, `−  Shire › Bank › Sub-bank › Panel › Cell  +`.
  Where a node has two children, + goes to the default child and the others are reached by clicking their part. Keys
  are + and −, Backspace goes out, and Enter on a part goes in.
- **Context mini-map** (the chip tour's PIP). When the camera is two or more scales deep, `.pip` shows the parent
  scale's drawing with the lit part ringed. Clicking it zooms out one scale.

### 2.4 A scene (one per level, in the script; its text and numbers come from `D`)

```js
SCENES.l2 = {
  title, short, key: '2', hash: 'l2',
  addr: a => ({bank: bits(a, 7, 6), sub: bits(a, 9, 8), set: bits(a, 16, 10), …}),   // §2.7, et-spec per level
  scales: {shire: {…}, bank: {…}, sub: {…}, panel: {…}, cell: {…}, xing: {…}, xcell: {…}},
  parts: {                                 // clickable parts: key → panel content; `facts` from D.parts.l2[key]
    reqq: {kick, title, badge: 'documented', what: () => `…${n('l2_reqq')}…`, kpis: [...]}, …},
  access: {                                 // one per button; its steps in the same order as D.steps.l2[name]
    'load-hit': {cap: () => `…`, steps: [
      {scale: 'shire', lit: ['nb0', 'xing'], dive: 'xcell',
       acts: [['packet', 'm0→bankfifo'], ['sweep', 'ls.in'], …], say: () => `…`, dur: 2400}, …]}},
  tour: [ …slides (§9)… ]
};
```

- **Where each step plays.** `scale` is where the step is shown when following. `dive` is the deeper scale where its
  circuit animation plays when Dive is on.
- **Acts.** `acts` lists activation primitives (§2.5) against named anchor points in the scale's drawing, the chip
  tour's `AP[level]`. Geometry lives in the script; words, numbers and sources live in `D`.

### 2.5 Activation primitives (new, shared by all five scenes)

Each primitive runs on the pausable clock, draws its end state at once under `tok.ff` or reduced motion, and never
signals by colour alone. Every change of state also changes stroke width, adds a label, or both.

| Primitive | Draws | Used for |
|---|---|---|
| `lit(part)` | the part's outline 5 units wide, a `--c2` glow, and the part name in bold | the block the step is in |
| `sweep(line, from)` | a line coming alive from its driver outward: a `--c2` stroke grows along its length, with a label ("WL 1,023" or "row 0x2C4") | wordlines, clock-gated rows, column-select lines, the CA bus |
| `droop(bl, dir, amt)` | a bitline's level as a thin in-line meter plus a text label ("precharged high" → "droops (tens of mV, generic)"); for DRAM, "VDD/2" → "VDD/2 + δ" | SRAM bitline pairs, DRAM charge sharing |
| `latch(sa)` | a sense amplifier or latch resolving: one output up, one down, labels 1 and 0, full swing | sense amplifiers, the L1 latches, flip-flops |
| `mos(t, on)` | a transistor turning on: its channel fills with `--c2`, a current arrow appears, and the gate node is labelled high; off is a hollow channel | every transistor view |
| `icg(g, en)` | a clock gate: clock pulses drawn as a small square wave pass through only while the enable is high | per-row clock gates (L1), per-macro gates (L2, L3, scratchpad) |
| `mux(m, sel)` | the selected input path lit through a mux or mux tree, the rest dimmed | the L1 read tree, column muxes, crossbars |
| `bus(path, bits)` | a thick trail with a width label ("576 bits", "512-bit ET-Link") and a packet | datapaths, the mesh |
| `counter(where, units)` | a cycle or nanosecond counter that ticks to a documented value; for undocumented splits it shows "—" with a "not split: asked" chip | the per-level cycle clock |
| `wave(strip, events)` | a small timing diagram whose cursor advances; ET-timed for DRAM (§8), untimed and labelled "order only, not to scale (generic)" for the SRAM and latch circuits | DRAM commands and data, SRAM read and write phases |
| `idle(part, why)` | a part greyed with a strike-through label ("not read: scratchpad has no tags"; "not clocked: zero line") | the point of the read-buffer hit, the scratchpad and the zero-line skip |

**Dive (V).** When Dive is on and a step has a `dive` scale:

1. The camera goes down, the circuit animation plays, and the camera comes back up to the step's scale. It is one
   eased chain each way, costing about 0.9 s down and 0.7 s up at the chip tour's 580 ms per log unit.
2. A step deeper than the camera shows while Follow is off is marked on the current scale, as the chip tour's
   `markStage` does.

Default: Dive is **off** in free play, **on** in the tour for the slides that show a cell (§9), and settable with
`?dive=`.

### 2.6 The circuit symbol library and the shared SRAM panel

**Symbols.** Each symbol is a function that draws into a group and returns its anchors:

- `nmos`, `pmos` (gate, drain, source, and the channel rect for `mos()`);
- `cap`, `inv`, `tg` (a transmission gate), `nand2`, `nor2`, `xnor2`;
- `dlatch` (the transmission-gate latch), `ff` (master-slave), `icgCell` (a latch plus an AND);
- `senseAmp` (a cross-coupled pair with its tail), `precharge` (two PMOS and an equaliser), `wlDriver`;
- `levelShifter` (cross-coupled PMOS over an NMOS differential pair), `repeater`, `lvstlDriver`;
- `dramCell` (1T1C), `eq3` (a 3-NMOS equaliser), `blsa` (2N + 2P);
- the wires `rail`, `node`, `wire`, with net labels.

Symbols follow ordinary schematic conventions (PMOS with a bubble; supply at the top, ground at the bottom), and each
view uses 30-50 devices at most. Node labels (BL, BLB, WL, SAE, Q, QB, D, CK, VDD/2, CSL, LIO) are 18-20 units.

**One SRAM panel sub-scene** serves L2, L3 and the scratchpad, because they are row ranges of the same macros
(`l3.same-arrays`, `scp.m0-rows`, `l2.partition.rows`). It is built once and configured by the level:

| Level | Band lit (the M0 partition) |
|---|---|
| L2 | rows for sets 0x280-0x2FF |
| L3 | sets 768-1023 = words 3,072-4,095 |
| Scratchpad | sets 0-639 = rows 0-2,559 |

The panel view shows:

- the ET-documented shell: a 4096 × 144 panel, the macro name and type 1PUHD, the ICG, and the trim box
  RM/RME/RA/WA/WPULSE with the reset row (`l2.macro.data`, `l2.trim`, `l2.trim.reset`, `scp.trim-reset`);
- a generic periphery: address latch, predecoder, wordline drivers, precharge, column mux, sense amplifiers, output
  latch, write drivers;
- the internal geometry dashed as **unknown**: "about 1,024 wordlines × 576 bitline pairs, 4:1 column mux, 4 internal
  banks, if `m4b4` means that" (`l2.macro.name-decode`, `u.macro-geometry`, `scp.u-macro`);
- the arrays themselves as representative grids (8 × 12 cells) with ellipses and counts ("⋮ 4,096 words"). Never
  draw thousands of rows.

**One 6T cell view** (generic) serves all three. It plays:

- **Read** (`g.read`, `scp.g-read`): precharge, then wordline, then one bitline droops, then the sense amplifier
  fires, then the column mux, then the output latch, then precharge again.
- **Half-selected neighbour** (`scp.g-half-select`): a column on the raised wordline that also discharges but is not
  read.
- **Write** (`g.write`, `scp.g-write`): the write drivers pull one bitline to ground, the wordline rises, and the cell
  flips. Write assist (WA) is a documented knob with a generic circuit (`g.assist`).
- **Leakage** (`g.leakage`): arrows through the off transistors, labelled with the measured bound of at most 19.6 mW
  per MB at 80 °C (`l3.leakage`, `scp.leak`).

The cell frame always carries two badges: **generic illustration** and **unknown: the bitcell is not documented; the
spec says SRAM, the lab lead said not SRAM (asked)** (`l2.storage-question`, `u.bitcell`, `scp.u-cell`).

**Insets.** These are small circuit cards opened from a part's panel ("Show the circuit"). Each is a small
one-device-deep scale node reached by Enter:

- tag comparator (XNOR per bit plus an AND tree; `g.compare`, `g.tag-compare`);
- SECDED XOR tree (`g.ecc`, `scp.g-ecc`);
- ICG (`g.icg`);
- level shifter and 2-flop synchroniser (`g.crossing`, `scp.g-level-shifter`);
- router stage (`g.router`);
- repeater (`g.wire-energy`).

### 2.7 The address strip, the ledger and the ladder

**The address strip** is a 40-bit physical-address bar under the header of the drawing. It shows the example address
in hex, and one level's fields overlaid as labelled brackets. "New address" re-draws the address, as the chip tour's
`newpa` action does, so which bank, sub-bank, row, home, memory shire or DRAM bank lights up follows it. The default is
the chip tour's `mkPA(13, 0x2468A)` in the DRAM region `0x80_0000_0000` (`dram.addr.region`). The scratchpad tab has
its own format and its own example address. Fields, all et-spec:

| Level | Fields |
|---|---|
| L1 | set PA[9:6] (`l1.size`); in the firmware's mode the two set MSBs are forced to 11 (DCache Description §3.2.1, pdf p.30), with sets 12-13 for hart 0 and 14-15 for hart 1 (`l1.modes`, PRM Table 8.4); block PA[4:3]; LRAM row {set, PA[5], way} (`l1.lram-addr`); tag PA[39:7] (`l1.metadata`). **Check hart 0's set bit against PRM §8.3.1 before drawing it.** |
| L2 | bank PA[7:6], sub-bank PA[9:8], set PA[16:10] under M0's 7-bit mask, which puts the rows at 0x280-0x2FF (`l2.decode`, `l2.partition.rows`) |
| L3 | home PA[10:6], bank PA[12:11], sub-bank PA[14:13], set PA[22:15], tag from PA[17] (`l3.decode`); the mesh lane is the home bank PA[12:11] (`l3.lane`, §12) |
| Scratchpad | [39:31] = 9'h1, shire [30:23], set [22:12], way [11:10], sub-bank [9:8], bank [7:6]; panel row PA[21:10] (`scp.addr`, `scp.addr-row`); format 1 (`scp.format1`) as a toggle |
| DRAM | memory shire PA[8:6] (`dram.addr.memshire`), channel PA[9] (`dram.addr.channel`), PA[9:6] stripped (`dram.addr.strip`), bank PA[12:10], column PA[17:13] + PA[5:1], row PA[34:18] (`dram.addr.pa-map`); PA[5] picks the burst half |

**The ledger** is the details panel's table for the running access, extending the chip tour's `legRows` to the
columns step, what happens, cycles, energy and badge. The row of the current step is highlighted.

- A cycle or energy value is printed only where a fact gives it for that step.
- Where only a total is documented, the undocumented steps share one merged cell, hatched, reading "not split: asked
  (<ask id>)". A **Measured total** row follows, with its card coverage.
- Units are explicit:
  - "cycles" means minion cycles at 600 MHz;
  - "shire clocks" is the spec's unit, 1:1 with minion cycles by `scp.clock-ratio` (derived, and asked);
  - DFI and DRAM clocks are converted to ns.

**The ladder** is one small shared chart at the foot of every level's overview panel, and in the prose. It uses
chartkit, log-scale bars, and the template's tokens only. It has two rows of bars: latency (5.25, 47, 110.5 + 12 per
hop, about 297) and pJ per byte (0.54, 3.11, 2.25-4.40, 14.7, 114.6). The current level is highlighted. The numbers
come from `l1.latency`, `l2.lat.measured`, `scp.lat-own`, `l3.lat-fit`, `dram.lat.chase`, `l1.e-vload`, `l2.e.level`,
`scp.e-own`, `l3.energy` and `dram.e.per-byte`.

### 2.8 Hand-offs between levels

An access that leaves the level ends on a hand-off step:

| Access | Hand-off |
|---|---|
| L1 miss | "Continue at L2" |
| L1 TensorLoad | "Continue at Scratchpad" |
| L2 miss | "Continue at L3" |
| L3 miss | "Continue at DRAM" |
| Scratchpad own load | ends in the L1 scratchpad: "See the L1" |

The step shows a button in the panel and a callout on the drawing. Pressing it, or → in the tour, switches tabs,
keeps the address, and starts the next level's matching access (L2 load-hit, L3 load-hit, DRAM load) from step 1.
Steps that happen at another level (L2's step 1 "the load misses the L1"; L3's step 2 "the requester's L2 misses") are
drawn as a mark with a link, not re-animated.

### 2.9 Pacing

- **Holds and step length.** The hold between steps is 2,300 ms (the chip tour's `HOLD`). A step animates for at most
  4 s, and a dive adds about 1.6 s. The pace of an access within a level is uniform, and the counters give the real
  times. The animation is never to scale with silicon time, and the caption says so once ("slowed about 10⁹ times").
- **Reduced motion.** Each step draws its end state. Wordlines appear lit, bitline labels show their final values, and
  counters show their totals.
- **Pausing.** Space stops the clock, the camera included. Stepping while paused draws the end state, as in the chip
  tour.
- **The tour** never advances on its own between slides. Within a slide an access plays through, then waits for the
  presenter.

---

## 3. Visual system and labelling rules

**Tokens only.** Use the template's tokens: `--c1 --c2 --c3 --c4 --c5 --c7 --ink --ink-2 --muted --grid --axis
--surface --page --border --warn --ok --bad`. The template has no `--c6`. Never write a hex colour, and add no palette.

| Role | Encoding |
|---|---|
| logic and pipelines, controllers | `--c1` outline, 12% fill (chip tour `boxShape`) |
| storage arrays (latch RAM, SRAM panels, DRAM arrays) | `--c3` (the chip tour's memory colour) |
| interconnect (crossbars, mesh, links, NoC, CA/DQ buses) | `--c4` |
| crossings, level shifters, synchronisers | `--c5` |
| activity: the lit part, packets, rising lines | `--c2`, stroke 5, as the chip tour's flows |
| voltage domains | a background band with a **pattern plus a text label**, never a colour: minion rail (LV) diagonal hatch "minion rail, 0.517 V measured" (`l1.voltage`); Shire Channel (HV) dots "SRAM rail, 0.705 V measured" (`l2.voltage.idle`, `scp.rail`); mesh horizontal lines "mesh rail, 0.485 V, 400 MHz" (`l3.mesh-rail`); memory shire vertical lines "VDD_DDR, 767-768 mV measured" (`dram.pwr.droop`, `dram.pwr.rails`); DRAM I/O "VDDQ" (`dram.pwr.rails`) |

**Three badges.** These are what the owner asked for. They extend the chip tour's `.kd` chips.

| Badge | Chip text | Style | In the drawing |
|---|---|---|---|
| **documented** for the ET-SoC-1 | "documented" plus its sub-kind: "measured · 3 cards" (`--ok`), "spec" (`--c1`), "derived" (`--c7`) | solid border | solid outline |
| **generic** illustration | "generic" | `--ink-2`, dotted border | dotted outline (`stroke-dasharray: 2 5`), and one "GENERIC: textbook circuit" tag in the corner of each frame drawn generically |
| **unknown** (asked) | "unknown · asked" | `--warn` border, text mixed toward `--ink` for 4.5:1 | dashed outline (`8 6`, the chip tour's "inferred" dash), a "?" glyph, and a link to the ask |

**Rules for badging.**

1. **Badge each claim at the scale where it is drawn.** A compiled macro's existence, size, ports and trims are
   documented at the panel scale. Its internal geometry is unknown there. Its cell is generic at the cell scale, with
   an unknown overlay.
2. **A frame that mixes kinds shows each kind on its own parts.** The frame's corner tag names the majority kind. The
   L1 LRAM block, for example, is "structure documented; circuit pattern from ET's latch register-file library;
   inside of the silicon macro unknown".
3. **Never let a generic value pass for an ET number.** Generic circuits get qualitative labels only: "precharged
   high", "droops by tens of mV (generic)", "boosted above the array voltage". Voltages and times are printed only
   where an ET fact gives them.
4. **Every printed number** goes through `n(key)`, dotted-underlined with the source on hover or focus, as in the chip
   tour. Card coverage follows a measured number the first time it appears in a panel ("3 cards", "aifoundry2 only").
5. **Words.**
   - Never call the L1 "SRAM".
   - Call the shire-cache arrays "SRAM panels, per the spec", with the contradiction note.
   - Call a DRAM package a "package", never a "bank": the datasheet calls it a bank, which is not a DRAM bank
     (`dram.topo.packages` note).
   - Use "L3 home" and "requester" as the chip tour does.
   - Name the lab lead only as §1.4 allows.
6. **Caveat markers** (§2.1): "re-implementation RTL" (`core-et-main`) and "spec v1.1" appear as small text after the
   badge.

**Text sizes** (SVG units at the 1300-wide frame; about 1.07 px per unit at 1920 × 1080): 17 minimum (`.t-sm`); 20
for labels; 24-30 for titles; 36 for ids. Transistor net labels are 18-20. Halos use `.halo` (the chip tour's
paint-order stroke).

**Strokes** as in the chip tour: components 2, frames 2.5, sub-structure 1.25, moving trails 6. Transistor symbols are
2 units, and lit ones 3.5.

---

## 4. L1 (key 1, `#l1`): latch RAM on the minion rail

**Header line:** "4 KB per minion, not SRAM: latch RAM on the 0.517 V minion rail; a hit takes 5.25 cycles and about
17 pJ per 32 B load" (`l1.size`, `l1.lram`, `l1.voltage`, `l1.latency`, `l1.e-vload`).

### Scales (a tree; the default path is marked ►)

| Scale | Drawn | Parts (facts) | Badge |
|---|---|---|---|
| ► **Minion** | pipeline strip ID → EX → TAG (S1) → MEM (S2) → WB (S3), then S4 write and S5 bypass; the DCache box; TLB; 2 miss handlers; an 8-entry replay queue; the VPU and its 256-bit port; the TensorLoad unit (TL0/TL1); the fill, evict and miss ports at the edge, where the neighbourhood's LV/HV crossing begins; the minion-rail band | `l1.pipeline`, `l1.s0-arb`, `l1.tlb`, `l1.mh`, `l1.rq`, `l1.vpu-port`, `l1.vpu-scp-read`, `l1.tensorload`, `l1.lv-region`, `l1.rail` (83% minion rail, 2% SRAM rail), `l1.voltage`, `l1.no-sleep`; floorplan unknown (`l1.u-floorplan`): the layout is logical, and the frame says so | documented; the layout is a logical drawing |
| ► **Data cache** | metadata: 4 tag latch register files (16 × 35) + 64 valid flip-flops + LRU 4 × 4 matrix per set (flip-flops); 4 tag comparators; PMA; the data array as 4 LRAM blocks × 2 macros (128 × 32), with the block enables; the write-port arbiter (7 clients, static priority); a set-map strip of 16 sets coloured by mode (0-11 scratchpad = 3 KB, 12-13 hart 0, 14-15 hart 1) with the measured knee | `l1.metadata`, `l1.lru`, `l1.phased`, `l1.lram`, `l1.lram-macros`, `l1.bank-enables`, `l1.s4-arb`, `l1.modes`, `l1.scp-impl`, `l1.firmware-mode`, `l1.knee`, `l1.states`, `l1.noncoherent`, `l1.write-policy`, `l1.bits`; `l1.no-parity` (none in the open RTL) + `l1.u-parity` | documented; parity on silicon unknown |
| ► **LRAM block** (instance PA[4:3]) | 128 rows × 64 bits as two 32-bit macros with their own enables. Write side: write-address decoder, then 128 per-row clock gates (HDBULT08_CKGTPLT), then the rows; the write-data latch (low phase, HDBULT08_CKGTNLT). Read side: registered read address, then row select, then the 64-bit output register (synchronous read). 8 representative rows + "⋮ 128 rows", with the addressed row lit | `l1.lram-model`, `l1.latch-rf`, `l1.icg-cells`, `l1.lram-addr` | structure documented; the circuit pattern is from ET's latch register-file library (`rf_latch_1r_1w_reg.v`); inside of the silicon macro **unknown** (`l1.u-cell`, `l1.u-library`) |
| ► **Row and read tree** | one row of 64 latches on one gated clock; for one output bit, the 128:1 mux tree (seven 2:1 levels) with the selected path lit; below it, the write pulse on that row | `g.latch-read`, `g.latch-write`, with ET counts from `l1.lram` | generic, ET-tied counts |
| ► **Latch cell** (transistors) | a transmission-gate D latch (2 TGs, 2 inverters, clock inverter: about 10 transistors), nodes D, CK, Q, QB. Inset: a 6T SRAM cell for contrast ("the kind the shire cache's panels are, per the spec; not used for the L1"). Count: "about 0.26-0.39 M storage transistors per minion at 8-12 per bit (estimate)" | `g.latch-cell`, `g.sram-6t`, `l1.transistors` | **generic**, with an unknown overlay (`l1.u-cell`) |
| Data cache → **Tag comparator** | XNOR × 33 + an AND tree; 4 run on every access, hit or miss | `g.compare`, `l1.phased` | generic |

### Accesses (`D.steps.l1`; step ids `l1.seq.<name>.<n>`)

**Load hit** (6 steps). The cycle counter runs 0 → 5 (`l1.latency-5`, derived; `l1.u-cycles` is asked).

| # | Where | What lights |
|---|---|---|
| 1 | Minion | ID; the six bidders; a replay-queue entry pre-allocated |
| 2 | Minion | EX: the adder forms the virtual address |
| 3 | Data cache | TLB; the four tag register files read the set; 4 comparators (dive: comparator); a one-hot hit; the row address formed |
| 4 | LRAM block | one block enabled (a scalar load) or four (a 32 B vector); row select; output register; LRU rewritten (dive: row and read tree, then latch cell: latch outputs drive the mux tree, with no precharge and no sense amplifier "if the macro is the latch pattern", which is unknown) |
| 5 | Minion | WB: align and extend |
| 6 | Minion | next ID. Ledger: 5.25 cycles measured on 3 cards; 17.3 pJ per 32 B vector load (random), 12.5 on zeros, scalar flw 14.0 pJ, all including the instruction (`l1.latency`, `l1.e-vload`, `l1.e-scalar`). Energy split per step: not split, asked (`l1.u-energy`) |

**Store hit** (6 steps): steps 1-3 as the load; S2 reads the row (read-modify-write, `l1.store-rmw`); S3 merges; S4
writes. In the write, the row clock gate fires and 64 latches turn transparent (dive: latch cell, write). A first store
to a clean line rewrites the metadata to modified. S5 bypasses. The ledger: 23.0 pJ per 32 B store, fsw 25.5 pJ, and
a store/load ratio of 1.82× (`l1.e-vstore`, `l1.e-scalar`, `l1.e-store-ratio`, derived).

**Miss → L2** (7 steps):

1. No way matches; the LRU picks a victim.
2. A miss handler takes the miss (one of 2); the load parks in the replay queue.
3. A dirty victim leaves as two 256-bit reads.
4. The fill request goes to the L2 bank PA[7:6]. **Hand-off: "Continue at L2".**
5. The fill writes two rows across all 4 blocks: 8 row gates, 512 latches.
6. The metadata write.
7. The replay hits.

Ledger: 47 cycles when the line is in the L2, 36 from its read buffer, hart 1 plus 3 (`l1.miss-l2`); 238 pJ to fill a
64 B line from the own scratchpad (`l1.e-fill`, canonical per §12).

**VPU scratchpad read** (3 steps): no TLB or tag check; all 4 blocks read one 256-bit row; delivered 2 cycles later
(`l1.vpu-scp-read`).

**TensorLoad** (3 steps): the FSM keeps 4 in flight; each 512-bit response writes two rows; 160.4 cycles for 16 lines,
about 10 per line (`l1.tensorload`, `l1.tl-latency`, `l1.tl-rate`). Hand-off: "The source is the scratchpad: continue
there".

**Refresh?** (1 step): latches hold while the rail is up; there is no refresh (`l1.seq.refresh.1`,
`l1:g.no-refresh`). The cell view shows a held Q.

**Overview panel KPIs:** 4 KB per minion; 5.25 cycles; 17.3 pJ per 32 B load; 0.517 V; 14.5 TB/s chip-wide
(`l1.bw`).

---

## 5. L2 (key 2, `#l2`): 512 KB of the shire cache

**Header line:** "512 KB per shire in rows 0x280-0x2FF of the shire cache's SRAM panels; a hit takes 47 cycles, 36
from the read buffer" (`l2.partition.default`, `l2.partition.rows`, `l2.lat.measured`).

### Scales

| Scale | Drawn | Facts | Badge |
|---|---|---|---|
| ► **Shire** | 4 neighbourhoods × 8 minions. The neighbourhood request path: 2:1 minion arbiter, 13:1 round-robin, pre-processing, bank FIFO, at least 6 cycles each way. Bank FIFOs are VC FIFOs with built-in level shifters at the LV/HV edge. Request and response crossbars (5 clients × 4 banks + UC), routed over the banks; 4 banks; UC; mesh stop. The LV and HV bands; the **partition bar** of one sub-bank: rows 0-639 scratchpad, 640-767 L2, 768-1023 L3, shared with the L3 and scratchpad tabs | `l2.sc.what`, `l2.partition.*`, `l2.path.*`, `l2.vc-fifo`, `l2.xbar.req`, `l2.xbar.rsp`, `l2.nbr.response`, `l2.domain`, `l2.clock`, `l2.freq`; rail of the HV logic **unknown** (`l2.rail.hv-logic`) | documented; the layout is logical (`l2.floorplan` unknown) |
| ► **Bank** (PA[7:6]) | reqq 64; 3-step arbitration; ordering lists; dataq; RBUF of 8 lines; coalescing buffer of 32; atomic unit; perf monitor; 4 sub-banks; the **pipeline strip** of 15 stages (ag ad rqa tap ta ta0 ta1 te tc dap da da0 da1 de dc) with the sub-bank busy rule; rspmux; the prefetcher as a dashed ghost box | `l2.reqq`, `l2.reqq.arb`, `l2.reqq.order`, `l2.dataq`, `l2.rbuf`, `l2.rbuf.enabled`, `l2.cbuf`, `l2.atomic`, `l2.stages`, `l2.subbank-busy`, `l2.ramdelay`, `l2.throughput`, `l2.perfmon`, `l2.clock-gating`; **unknown**: `l2.rbuf.storage`, `l2.hpf` | documented + 2 unknown parts |
| ► **Sub-bank** (PA[9:8]) | tag macro 1024 × 116 (4 × (23 + 6 ECC)); tag-state 1024 × 40, two-port; 4 data panels 4096 × 144, one per quadword; te and de ECC; 4 comparators; the zero bit; an ICG per macro; panel select; row address {set, way} with the L2 band lit | `l2.tag-ram`, `l2.tag-state-ram`, `l2.data-ram`, `l2.macro.tag`, `l2.macro.state`, `l2.macro.data`, `l2.serial-lookup`, `l2.panel-select`, `l2.ecc`, `l2.zero-state`, `l2.macro.count`, `l2.bits` | documented |
| ► **Panel** | the shared SRAM panel sub-scene (§2.6), L2 band | `l2.macro.data`, `l2.macro.vendor`, `l2.trim`, `l2.trim.reset`, `l2.voltage.idle`, `l2.voltage.limits`; **unknown**: `l2.macro.name-decode` | documented shell, generic periphery, unknown geometry |
| ► **Cell** | the shared 6T view; tag-state inset as a generic 8T two-port cell; "243 M cell transistors per shire, if 6T/8T (estimate)" | `g`-kind rows of L2/L3/scratchpad, `l2.transistors`; **unknown** `l2.storage-question` | generic + unknown |
| Shire → **Crossing** | a VC FIFO cell with a level shifter (cross-coupled PMOS over an NMOS pair) from 0.517 to 0.705 V | `l2.vc-fifo` (the crossing exists, et-spec), circuit generic | generic |

### Accesses (`D.steps.l2`)

**Load hit** (13 steps):

| # | Where | What happens |
|---|---|---|
| 1 | Shire | the L1 misses: a mark linking to the L1 |
| 2 | Shire | neighbourhood to bank FIFO across the LV → HV edge (dive: crossing); at least 6 cycles |
| 3 | Shire | request crossbar |
| 4 | Bank | reqq allocate; RBUF check misses |
| 5 | Bank | rqa |
| 6 | Sub-bank | tag and tag-state read, 2 cycles (dive: panel, then cell read) |
| 7 | Sub-bank | tag ECC |
| 8 | Sub-bank | compare, and the state write through the second port |
| 9 | Sub-bank | 4 panels read {way, set}: 576 bits, 2 cycles (dive) |
| 10 | Sub-bank | data ECC, 8 × SECDED |
| 11 | Bank | dc and RBUF install |
| 12 | Shire | rspmux and response crossbar |
| 13 | Shire | back across HV → LV, Fill FIFO, L1 fill |

Ledger:

- Spec: 21 shire clocks inside the cache (`l2.lat.spec`).
- Measured: 47.00 cycles on 3 cards (`l2.lat.measured`), leaving 26 outside the cache (`l2.lat.overhead`, derived).
- The per-step split is known only for the 2-cycle RAMs and the at-least-6-cycle neighbourhood legs. The rest is "not
  split: asked" (ask-cache-latency).
- Energy: about 199 pJ per line (3.11 pJ/B, 3 cards, `l2.e.level`). The 19 September split was 112 pJ on the SRAM
  rail, 64 on the minion rail and 2 on the NoC rail, of 183, on one card (`l2.e.rails`).

**Read-buffer hit** (4 steps). The point is `idle()` on every macro: the panels stay dark. Spec 10 shire clocks;
measured 36.00. Energy: not measured.

**Write-back** (6 steps): the L1 evicts as 2 × 256; a dataq write; tag and state; the data write enables only the
written panels (dive: cell write); ack. Ledger: a write costs about 2× a read (`l2.e.tload-tstore`); 774 pJ per random
fsw (`l2.e.scalar`).

**Miss → L3** (5 steps): tc misses; Mesh_Read on to_l3 (512-bit, 4 lanes, VCFIFO with 2-stage synchronisers).
**Hand-off: "Continue at L3".** The fill goes to the neighbourhood first; L2_Fill with a victim; the victim is written
back.

**Refresh?** (2 steps): static, no refresh. The SRAM rail idles at 2.0 W for the chip: 1.60 W at 67 °C, 2.63 W at
82 °C (`l2.leak`). No scrub; deep sleep only for non-operational shires; no wake-up measured (`l2.sleep`).

**Overview KPIs:** 512 KB per shire; 47 / 36 cycles; 2.45 TB/s, which is 128 B per shire-cycle, half the spec's 256
(`l2.bw.measured`, `l2.bw.per-bank`); 3.11 pJ/B; 705 mV.

---

## 6. L3 (key 3, `#l3`): the top quarter of every shire's panels, across the mesh

**Header line:** "32 MB in 1 MB slices, homed by PA[10:6]; a hit costs 110.5 + 11.99 cycles per mesh hop and 14.7
pJ/B" (`l3.what`, `l3.homes`, `l3.lat-fit`, `l3.energy`).

### Scales

| Scale | Drawn | Facts | Badge |
|---|---|---|---|
| ► **Chip** | the measured 6 × 6 map from the chip tour's layout (`D.layout`, facts `chip:mesh.logical-map`, `chip:L40`), 32 compute shires. Requester R is shire 0 by default, or picked in the panel as the chip tour's flow 1 does. Home H = PA[10:6]. The route is drawn x first, like the chip tour; the order is unknown (`l3.route`). Hop counter; memory shires at the edges for the miss hand-off; a table of latency by home | `l3.homes`, `l3.decode`, `l3.home-measured`, `l3.lat-fit`, `l3.lat-by-home`, `l3.lat-by-requester`, `l3.mean-hops`, `l3.route`, `l3.alias` | documented and measured; the route order is unknown |
| ► **Home shire** | 4 L3-slave ports off the mesh stop; crossbar; 4 banks with bank PA[12:11] lit; UC. The neighbourhoods are drawn faint but present, because L3-slave requests win arbitration over the shire's own requests | `l3.ports`, `l3.priority`, `l3.slice-arith` | documented; floorplan unknown (`u.slice-floorplan`) |
| ► **Home bank** | L3-slave FIFO; reqq with 21 entries reserved; the RBUF drawn with `idle()` "L3 reads never use it"; the pipeline strip; the MRU write through the second port; atomic block; to_sys port for misses | `l3.reqq`, `l3.no-rbuf`, `l3.pipeline`, `l3.hit-way-read`, `l3.ram-delay`, `l3.mru-write`, `l3.atomic`, `l3.miss-path`, `l3.partial`, `l3.write` | documented |
| ► **Sub-bank and panel** (PA[14:13]) | the shared panel sub-scene with the L3 band (sets 768-1023). The **zero-line path**: a 512-bit NOR, the zero bit, and the data macros not clocked (`idle()`). An ICG per macro; all 4 panels on a read, only the written ones on a write; trims at 705 mV against RM0's 650 | `l3.same-arrays`, `l3.geometry`, `l3.macros`, `l3.vendor`, `l3.zero-state`, `l3.clock-gating`, `l3.panels`, `l3.trim-table`, `l3.trim-reset`, `l3.rail-vs-trim`, `l3.ecc-scrub`; **unknown** `u.macro-geometry`, `u.live-settings` | documented shell, unknown geometry |
| ► **Cell** | the shared 6T view with read assist, write assist and leakage | `g.6t-cell`, `g.read`, `g.write`, `g.assist`, `g.leakage`, `l3.leakage`, `l3.no-refresh`; **unknown** `u.bitcell` | generic + unknown |
| Chip → **Mesh hop** | the requester bank's to_l3 master (lane = home bank PA[12:11]); the VCFIFO (level shifters 705 → 485 mV, 2-flop synchroniser into the 400 MHz NoC); a router; one 3.72 mm repeated link; the next router; the home's L3-slave port and its VCFIFO up. Flit contents: request about 75-85 bits, reply 512 data + control | `l3.ports`, `l3.lane`, `l3.hop`, `l3.hop-noc-cycles`, `l3.flits`, `l3.mesh-rail`, `l3.wire-energy`, `l3.tsend-compare`, `g.crossing`, `g.router`, `g.wire-energy`; **unknown** `u.noc-hop` | documented numbers, generic router, unknown pipeline |
| Mesh hop → **Repeater and level shifter** (transistors) | an inverter-pair repeater toggling with the data (zeros do not toggle); a level shifter | `g.wire-energy`, `g.crossing` | generic |

### Accesses (`D.steps.l3`, from `access_sequence`)

**Load hit** (9 steps):

| # | Where | What happens |
|---|---|---|
| 1 | Chip | R pulses: the L1 missed (a mark, linking to the L1) |
| 2 | Chip | R's L2 misses (a mark, linking to the L2): 34 shire clocks in the spec, both directions |
| 3 | Mesh hop | to_l3 and the crossing |
| 4 | Chip | the request travels R → H hop by hop with the counter; 12 cycles per hop round trip |
| 5 | Home bank | L3-slave port and reqq |
| 6 | Sub-bank | tag phase (dive: cell read) |
| 7 | Sub-bank | data phase and LRU write; with "Zero line" toggled, the data panels stay `idle()` |
| 8 | Chip | the 512-bit reply travels H → R; ledger: about 69 pJ per line per hop derived, 47-59 measured |
| 9 | Chip | R's L2 fill and L1 fill |

Ledger:

- Total: 110.5 + 11.99 × hops cycles, 3 cards (`l3.lat-fit`), which is 109 locally and 218 at 9 hops
  (`l3.lat-by-home`). Its split is 72.2 cycles + 61.4 ns, plus 20 ns per hop (`l3.lat-clock-split`).
- The spec's 34 + 30 shire clocks does not reconcile with that (`l3.lat-reconcile`): the per-step split is "not split:
  asked" (ask-cache-latency).
- Energy: 14.7 pJ/B, 3 cards. Per load with a local home, 643 pJ, of which 306 on the SRAM rail, 120 on the mesh and
  110 on the minions (`l3.energy-per-load`). Zeros cost 7.6 pJ/B against 19.3 for random data on aifoundry2
  (`l3.energy-contents`, `l3.energy-rails`).

**Write-around** (3 steps): scalar store via L2 victim; tensor store coalesced in the requester's L2 buffer; the L3
write at the home, with only the written panels enabled and all-zero lines setting the zero bit.

**Miss → DRAM** (4 steps): tc misses and a victim is picked; the read goes over to_sys to memory shire PA[8:6].
**Hand-off: "Continue at DRAM"** (91 + 12 × hops, `l3.dram-leg`). Then the fill, and the partial-line case.

**Atomic** (1 step): the home bank's atomic block reads, operates and writes. 10.00 cycles per contended atomic;
3.99 W over idle (`l3.atomic`, `l3.atomic-rails`).

**Refresh?** (1 step): none, and leakage of at most 19.6 mW per MB at 80 °C.

**Panel extras:** "Pick the requester" and "New address", as in the chip tour's flow 1. The hop count, the latency
from the fit and the lane update with them.

---

## 7. Scratchpad (key 4, `#scp`): the same panels without the tags

**Header line:** "2.5 MB per shire in rows 0-2,559 of the same panels; never a miss; 47 cycles from the own shire,
99.84 + 12.00 per hop from another" (`scp.size`, `scp.m0-rows`, `scp.lat-own`, `scp.lat-remote`).

### Scales

| Scale | Drawn | Facts | Badge |
|---|---|---|---|
| ► **Chip** | the scratchpad address format bar; own shire against remote shires on the measured map, with the fit and the ~53-cycle cost of leaving the shire; 80 MB over 32 shires; format 1 interleave | `scp.what`, `scp.size`, `scp.addr`, `scp.format1`, `scp.lat-remote`, `scp.lat-remote-split`, `scp.lat-leave`, `scp.bw-remote` | documented |
| ► **Shire** | a minion's TensorLoad (4 in flight) into the **L1 scratchpad, which is latch RAM**, linked to the L1 tab; cooperative TensorLoad broadcast; crossbars; banks. The bottleneck candidates carry "?" markers: sub-bank busy, response crossbar, Fill FIFO, the 256-bit minion port | `scp.tensorload`, `scp.tl-dest`, `scp.coop`, `scp.tl-one`, `scp.tl-pipelining`, `scp.bw-own`, `scp.bw-one-neigh`, `scp.bw-bank-stride`, `scp.bw-spec-port`, `scp.xbar`; **unknown** `scp.u-bw` | documented + unknown |
| ► **Bank and sub-bank** | reqq; RBUF (scratchpad reads install into it, remote ones included); the tag stages elapse but the tag and state reads are squashed, shown `idle()` ("no tags"); no victims; the zero-state shortcut does not apply (`idle()` note); writes of 16 B or more need no RMW; atomic block via the L3 slave; remote requests win arbitration | `scp.always-hit` (derived, re-implementation), `scp.no-victims`, `scp.pipe-stages`, `scp.ram-delay`, `scp.clock-gate`, `scp.rbuf`, `scp.zero-state`, `scp.write-granule`, `scp.reqq`, `scp.atomic`, `scp.starve`, `scp.ecc` | documented |
| ► **Panel** | the shared panel sub-scene with the scratchpad band. A **Vmin inset**: the RM table (585 mV Vmin at RM0 … 855 at RM5) against the three rails: SRAM 705 (120 mV margin), minion 517, mesh 485. This is where the "why the L1 is not these panels" point is drawn, et-derived and asked | `scp.panel`, `scp.panel-others`, `scp.panel-count`, `scp.line-read-panels`, `scp.vendor`, `scp.prm-sram-family`, `scp.trim-knobs`, `scp.vmin-table`, `scp.trim-reset`, `scp.fw-no-trim`, `scp.rail`, `scp.rail-margin`, `scp.regulator`, `scp.hv-region`; **unknown** `scp.u-macro`, `scp.u-trim` | documented shell, unknown geometry |
| ► **Cell** | the shared 6T view. The **differential read**: exactly one bitline discharges whatever the data, so the 2× zeros/random difference on the SRAM rail (about 90 pJ per line) must sit in the periphery or datapath; half-select; write at 2.1× a read | `scp.g-cell`, `scp.g-read`, `scp.g-read-data`, `scp.g-half-select`, `scp.g-write`, `scp.g-assist`, `scp.g-static`, `scp.e-data`, `scp.e-sram-line`, `scp.e-sram-write`; **unknown** `scp.u-cell` | generic + unknown |

### Accesses (`D.steps.scp`)

**Own load** (11 steps):

| # | Where | What happens |
|---|---|---|
| 1 | Shire | TensorLoad FSM, 4 in flight |
| 2 | Shire | address decode: region, local |
| 3 | Shire | neighbourhood crossing |
| 4 | Shire | request crossbar |
| 5 | Bank | reqq: RBUF check, range check, rqa |
| 6 | Bank | tag stages elapse with the tags idle, which is why the scratchpad takes exactly as long as an L2 hit |
| 7 | Panel | 4 panels read row PA[21:10]: 576 bits, 2 cycles; about 182 pJ per line on the SRAM rail for random data, 92 for zeros, aifoundry2 (dive: cell read) |
| 8 | Bank | ECC |
| 9 | Bank | dc, RBUF, rspmux |
| 10 | Shire | response path |
| 11 | Shire | into the L1 scratchpad (latch RAM): the hand-off "See the L1" |

Ledger: 47 cycles for an L1-missing load; 160.1 cycles for 16 lines (`scp.tl-one`); 2.25 / 4.40 pJ/B on zeros /
random, 69% of it on the SRAM rail (`scp.e-own`, `scp.e-rails-load`).

**Own store** (5 steps): only the written quadwords' panels are clocked (dive: cell write). 1.23 TB/s; 4.65 / 8.58
pJ/B; about 389 pJ per line on the SRAM rail.

**Remote load** (6 steps): the mesh leg as in L3's hop scale, 12.00 cycles per hop; at 1 hop the rail split is 50%
SRAM, 27% mesh, 14% minions (`scp.e-rails-remote`); 5.10 / 11.8 pJ/B, plus 0.67 / 1.80 per hop (`scp.e-remote`,
`scp.e-hop`).

**Remote store** (3 steps): the relay hands data to the next shire at 8.92 pJ/B against 116.2 through DRAM
(`scp.relay`, `scp.relay-mech`).

**Fill** (TensorLoadL2Scp, 2 steps): a mesh read of the source; not measured separately (`scp.tl-l2scp`).

**Atomic** (2 steps): 10.00 cycles per atomic at the bank; 22 remote hammering minions stop the host's own reads
(`scp.atomic`, `scp.starve`).

**Miss? Refresh?** (3 steps): no misses, no victims, no refresh; leakage at most 19.6 mW per MB (`scp.leak`).

---

## 8. DRAM (key 5, `#dram`): LPDDR4X behind eight memory shires

**Header line:** "16 x16 LPDDR4X channels at 3,733 MT/s behind 8 memory shires; a typical load takes 299 cycles (500
ns), about 28 of them in the DRAM, and 114.6 pJ/B, 70% of it off the metered rails" (`dram.ctl.clock`,
`dram.lat.typical`, `dram.lat.dram-chip-share`, `dram.e.per-byte`, `dram.e.unmetered`).

### Scales

| Scale | Drawn | Facts | Badge |
|---|---|---|---|
| ► **Card and chip** | 8 memory shires, west 0-3 and east 4-7, on the chip tour's layout; 4 packages × 4 channels, with the package pairing **dashed** (unknown); 2 memory PLLs; the route from L3 home to memory shire PA[8:6] with the fit 91 + 12 per hop; the whole-load model 110 + 12h + 91 + 12h | `dram.topo.memshires`, `dram.topo.packages`, `dram.topo.pll`, `dram.topo.floorplan`, `dram.addr.memshire`, `dram.lat.model`, `dram.lat.ms-hops`, `dram.lat.l3-miss`; **unknown** `dram.topo.pkg-pairing` | documented + unknown pairing |
| ► **Memory shire** | the 512-bit NoC AXI port (32 GB/s); the clock crossing (400 MHz mesh to the 933 MHz DFI; its placement inferred, `dram.seq.load.03` note); the address strip; **2 uMCTL2 controllers** (2 AXI ports with priorities, a CAM with 32 low-priority read entries, runs of 15, the address map, open page, refresh timer, no power-down, no auto-ZQ, DFI updates, ECC off); DFI 1:2; **1 PHY for 2 channels**; the CA[5:0], DQ[15:0] and DQS pins; atomic unit; perf monitor; VDD_DDR. The **≤ 63 cycles** of the memory shire are drawn as one hatched bar, "not split: asked" | `dram.topo.controllers`, `dram.topo.phy` (derived; the datasheet disagrees, §12), `dram.topo.noc-port`, `dram.ctl.*`, `dram.addr.addrmap`, `dram.addr.strip`, `dram.addr.channel`, `dram.pwr.rails`, `dram.pwr.droop`; **unknown** `dram.lat.ms-internal` | documented + unknown split |
| ► **Channel and die** (PA[9]) | 1 rank × 8 banks; each bank 131,072 rows × a 2 KB page (1,024 columns × 16 bits); row decoder, bank array, a sense-amplifier row of 16,384, column decoder, I/O gating, 16n prefetch, serialiser, DQ. The open row with the line's 512 of 16,384 bits lit (1/32). The **command and data timeline**, drawn to scale in ns from the programmed timings | `dram.org.geometry` (derived), `dram.org.line-vs-page`, `dram.addr.pa-map`, `dram.addr.interleave`, `dram.ctl.burst`, `dram.ctl.dbi`, `gen.commands`, `gen.column`, `gen.jedec-match`; **unknown** `dram.org.part` | documented geometry and timings; generic die internals |
| ► **Bank and subarray** (PA[12:10]) | a mat: local wordlines and sub-wordline drivers; bitline pairs; a stripe of bitline sense amplifiers; equalisers; column-select lines; local and global I/O lines. Open or folded bitlines is drawn generic with a note | `gen.wordline`, `gen.sense`, `gen.equalize`, `gen.column`; **unknown** `dram.org.die-internals` | generic |
| ► **Cell and sense amplifier** (transistors) | 1T1C cells on a bitline pair; the 3-NMOS equaliser; the boosted wordline; the 2N + 2P latch sense amplifier; the column-select NMOS pair to the local I/O line | `gen.cell`, `gen.equalize`, `gen.wordline`, `gen.sense`, `gen.column`, `gen.precharge`, `gen.refresh` | generic |
| Memory shire → **PHY and pins** → **DQ driver** (transistors) | an LVSTL driver pulling to VDDQ or ground, with termination to ground, so a driven 1 draws current and a 0 almost none; DBI on | `gen.io`, `dram.ctl.dbi`, `dram.pwr.rails` | generic circuit, documented settings |

**The timeline** (`wave()`, documented). Every duration below is et-spec:

- ACT (two parts) at t = 0; READ #1 at tRCD = 18.2 ns; READ #2 one tCCD = 4.3 ns later.
- The first data after RL = 19.3 ns; two BL16 bursts of 4.3 ns each.
- No precharge, because the page policy is open.
- For writes, WL = 8.6 ns and nWR = 18.2 ns. For conflicts, tRP = 18.2 ns and tRC = 63.2 ns.
- Refresh: REFab every 3.875 µs, lasting 280.7 ns.

Sources: `dram.ctl.tRCD`, `dram.ctl.tRP`, `dram.ctl.tRAS-tRC`, `dram.ctl.RL-WL`, `dram.ctl.burst`,
`dram.ctl.tRRD-tFAW`, `dram.ctl.tWR`, `dram.ctl.refresh-mode`. Each is also shown in minion cycles at 600 MHz.

### Accesses (`D.steps.dram`)

**Load, closed row** (11 steps):

| # | Where | What happens |
|---|---|---|
| 1-2 | Card and chip | the L3 home misses; the request crosses the mesh |
| 3-4 | Memory shire | port, crossing, strip; controller map, CAM and scheduler |
| 5 | Memory shire | ACT on the CA bus |
| 6 | Bank, then cell (dive) | equalisers off; the wordline boosts; 16,384 access transistors turn on |
| 7 | Cell | sense amplifiers fire and restore the cells; tRCD = 11 cycles |
| 8 | Channel | two READs |
| 9 | PHY branch (dive: DQ driver) | DQ bursts with DBI |
| 10 | Memory shire | back through the memory shire; the row stays open |
| 11 | Card and chip | the mesh back to the L3 home and on to the requester |

Ledger:

- About 297-299 cycles in all (`dram.lat.chase`, `dram.lat.typical`).
- The DRAM's share is about 28 cycles, tRCD 11 plus RL and the bursts 17 (derived).
- The memory shire's share is up to 63 cycles, not split: asked.
- 114.6 pJ/B, which is 7.3 nJ per line; 94.6 pJ/B on zeros, 132.6 on random data (`dram.e.data`); about 70% off the
  rails (73 pJ/B, `dram.e.unmetered`). Its split is unknown (`dram.e.split-unknown`, hub rung 20).

**Row hit:** the ACT and sense steps are skipped. 11-12 cycles saved, measured (`dram.lat.row-hit`). The same energy
(`dram.e.rows`).

**Row conflict:** PRE, then ACT. Plus 9-10 cycles when the loads come one after the other (tRP), plus 37 when issued
together (tRC) (`dram.lat.row-conflict`, `dram.lat.row-sequential`). An activate's energy is bounded, not measured.

**Store** (5 steps): from the L3 victim to_sys; the write store drains in runs of up to 15; WRITE after WL; in the
cell view the write drivers overpower the sense amplifiers and nWR elapses. Energy is indistinguishable from a load
(`dram.e.store-vs-load`); the L1 write-back path costs 341.5 pJ/B (`dram.e.writeback`).

**Refresh** (4 steps):

- tREFI 3.875 µs, measured as 2,325.4 cycles (3.876 µs) on every card (`dram.lat.refresh-period`).
- The die's counter activates and precharges about 16 rows per bank per REFab, in all 8 banks, with no column access
  (`gen.refresh`: generic, derived for this density). This is the cell view without the column step.
- A load caught in it waits up to 208 cycles, and 7.2% of loads are (`dram.ctl.refresh-duty`). Refresh closes the
  open row.
- Energy: not measured (`dram.seq.refresh.04`).

**Overview KPIs:** 32 GB; 3,733 MT/s (not 4,266); 119.5 GB/s peak against 76 measured; 299 cycles; 114.6 pJ/B; 30×
the scratchpad per byte read (`dram.e.vs-scp`).

---

## 9. Tours (T for this level; Shift+T for all five in order)

Each slide is the chip tour's `STEPS` shape: `{cap, sub, view: {level, scale, inst}, panel: [part], hi: [parts],
access?, dive?}`. **Access slides** play their access; the arrows step it and move on at its ends. The last slide of
each level offers "Continue to <next level>" when touring all.

| Level | Slides |
|---|---|
| L1 (8) | 1 the minion: where the L1 sits, the rail band, 83% on the minion rail · 2 the data cache: 16 × 4 × 64 B, the firmware's 512 B per hart and 3 KB scratchpad, the knee · 3 **load hit** · 4 the LRAM block: per-row clock gates and a mux-tree read (ET's latch-RF pattern) · 5 the latch cell against a 6T cell (generic), and "not SRAM: why" (derived, asked) · 6 **store hit** (RMW, 1.82×) · 7 **miss → L2** · 8 what is unknown and asked |
| L2 (8) | 1 the shire and the partition bar · 2 the bank and its 15-stage pipeline · 3 **load hit** (dive on 6 and 9) · 4 **read-buffer hit** (the panels stay dark) · 5 the sub-bank's macros · 6 the panel and its trims: RM0 650 mV against 705 measured · 7 the cell: generic 6T, the bitcell unknown, the SRAM contradiction · 8 energy (199 pJ per line; the rail split) and the asks |
| L3 (8) | 1 the chip: homes by PA[10:6] · 2 **load hit** · 3 the mesh hop: crossing, router, wire energy · 4 the home bank: L3 wins arbitration, no read buffer · 5 zero lines skip the panels (7.6 against 19.3 pJ/B) · 6 cell and leakage · 7 **miss → DRAM** · 8 the latency that does not add up (spec against measurement) and the asks |
| Scratchpad (7) | 1 the address format, own against remote · 2 **own load** (TensorLoad, 160 cycles, 4 in flight) · 3 no tags, yet exactly as fast as the L2 · 4 the panel band and the Vmin inset (why the L1 cannot be this) · 5 the cell: a differential read, so where does the zeros/random difference come from · 6 **remote load** and the relay · 7 the bottleneck question and the asks |
| DRAM (9) | 1 card and chip: memory shires, packages, the dashed pairing · 2 the memory shire and its ≤ 63-cycle black box · 3 the controller settings and the timeline · 4 **load, closed row** (dive to cell and sense amplifier) · 5 the sense amplifier and restore up close · 6 **row hit** and **row conflict** · 7 **refresh** · 8 energy: 70% off the rails · 9 the asks |

Tour mode enlarges the panel text and hides the facts lists, as the chip tour does (`#stage.present`).

---

## 10. Accessibility

- **The chip tour's model** carries over:
  - every part is `g.comp`, `role="button"`, `tabindex="0"`, with an `aria-label` of name plus badge (for example
    "Tag RAM, 1,024 by 116 bits, documented");
  - Space shows details, Enter zooms in;
  - focus moves to the part zoomed out of, or to the first part of the new view (`zoomFocus`);
  - skip links go to playback, scale and details.
- **Transistor views.** Each device is a focusable part at the cell scale ("access NMOS, generic"), with 10-20
  focusable parts per view at most.
- **Live regions:**
  - `#st-live`: "Step 4 of 13: tag and tag-state read";
  - `#cap-scale`: "Scale: sub-bank 1 of bank 2";
  - `#pn-live`: the panel title;
  - `#lvl-live`: "Level: L3".
  - These are polite, with no duplicate announcements while playing: announce on step change only.
- **Colour.** Colour is never the only signal:
  - badges carry text;
  - unknown is dashed with "?", and generic is dotted with a "GENERIC" tag;
  - lit parts get a thicker stroke plus the name in the caption;
  - logic levels are "1"/"0" text on nodes;
  - rail bands are patterns with text.
- **Contrast.** Text is at least 4.5:1 and graphics at least 3:1 in both themes. Badge text uses
  `color-mix(… --ink)` as the chip tour's `.kd.inferred` does. Dimmed context stays at 0.38 or more on dark pages
  (the chip tour's dark-mode rule).
- **Reduced motion.** Nothing moves; each step draws its end state. The chip tour's `REDUCED` path is followed, and
  the camera cuts.
- **Text alternative.** The prose's "One load, level by level" (§1.4) states every step with its numbers. The facts
  and asks tables are real tables with headers; on narrow screens they use the template's `.stack` pattern.
- **Keyboard.** Everything is reachable by keyboard. Inside a frame that has not been clicked, the chip tour's
  `.kbd-hint` shows. Keys never fire while focus is in an input or select. Tablist arrow keys are scoped to the
  tablist (§1.2).
- **Touch.** Under `@media (pointer: coarse)` every control is at least 44 × 44 px.

---

## 11. Sizes and responsive behaviour

| Viewport | Layout |
|---|---|
| **1920 × 1080 (presenting)** | One screen. The header is one row of at most 56 px: title, 5 tabs and at most 7 access buttons. The body is the drawing (about 1,410 × 760 px, so 1 unit is about 1.08 px and text is at least 18 px) plus the panel at `clamp(300px, 24vw, 470px)`. The stage bar is about 44 px; the caption row at most 120 px (caption up to 32 px, sub-caption 19 px, two lines kept free). Present mode: panel text at least 18 px, no fact lists. |
| **1280 × 720** (the minimum for presenting, as in the chip tour) | The chip tour's `max-height: 780px` compaction. The drawing is about 930 × 470 px, so text is at least 12 px, 17 units × 0.72. The builder checks legibility here and lets the header wrap to two rows if the access buttons do not fit with the short labels. |
| **900-1450 wide** | Short tab labels; the access buttons show short names ("Load", "Store", "Miss", "RB hit", "Row hit", …); the step bar shows every step's number and only the current step's name (the chip tour's 900-1199 rule). |
| **< 900 wide** | Stacked: header, tabs, drawing, stage bar, caption, panel. The page scrolls; the stage does not. |
| **390 px phone** | Tabs are one horizontally scrollable segmented row (L1 · L2 · L3 · Scratch · DRAM), always visible. The access buttons wrap under the tabs (2-3 rows) or collapse into a labelled `<select>`. **The drawing sits in its own box with `min-width: 760px`**, so text is at least 16 px, and it scrolls sideways inside that box only. A "Fit" toggle shows the whole frame at about 0.5× for orientation, and a one-line hint says "scroll the drawing sideways". The page itself never scrolls horizontally. Steps wrap at about 30% width each. The caption is one column. The panel's list has `max-height: 70vh`. The PIP is 44% wide. Full screen or presenting on a phone: the drawing fills the space left and the panel scrolls below it, at `26vh` (the chip tour's rules). |

**Budgets:**

- The script is at most about 350 KB unminified; the data is at most about 600 KB; the built page is at most about
  1.5 MB (the chip tour's page is about 0.55 MB).
- At most about 2,500 SVG nodes in any built scale layer, and only the current path is built.
- One `requestAnimationFrame` loop (`CLK`).
- 60 fps on a 2020 laptop at 1920 × 1080 with Dive on.

---

## 12. Conflicts and corrections the page must handle

| Topic | Sources disagree | Resolution on the page |
|---|---|---|
| Is the storage SRAM? | spec pdf pp.48, 51, datasheet p.4 and the PRM p.346 say SRAM for the shire cache, against the lab lead's "not using SRAM" | Show the documents as documented, and the bitcell as unknown with the contradiction stated; the L1 is documented as latch RAM. Ask: ask-not-sram. |
| The SRAM rail's voltage | 750 mV in the card's power-tree figure (`l2.rail.sram`, `docs/research/power-telemetry.md:46`); 705 mV "set point" in `scp.rail`; 703-707 mV measured on die (`l2.voltage.idle`, `per-shire-voltage-idle.json`) | Print "705 mV measured on the die (703-707)" and "750 mV in the card's power-tree figure". Check `scp.rail`'s "set point" wording against the telemetry field `reg_mv` before printing it. |
| Filling a 64 B line into the L1 from the scratchpad | 238 pJ random / 101 zeros, 3 cards (`l1.e-fill`, `scp.e-l1fill`: energy manual 04a-fine-grain.md:44), against 205 / 101 with two cards pooled (`l2.e.l1fill`: 05-claims.md:306) | Canonical 238; 205 only in the facts table, marked as the earlier figure. |
| Which mesh lane an L3 request takes | chip tour fact L103 and `docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:69` say PA[7:6]; `l3.lane` says the home bank PA[12:11], with PA[7:6] only for remote scratchpad (verified in `external/core-et-main/hw/ip/shirecache/rtl/shirecache_mesh_master.sv:132-153`, `req_bank_id = remote_scp ? scp_bank_id : l3_bank_id`) | Draw PA[12:11] for L3 with a "re-implementation RTL; to confirm" marker. Tell the coordinator that chip fact L103 and SYNTHESIS.md:69 need the correction, since this page cannot edit them. Asked in ask-silicon-config. |
| PHYs per memory shire | the datasheet says 2 PHYs share 1 controller; the PRM and firmware say 2 controllers and 1 PHY | Draw 2 controllers and 1 PHY, derived, with a note (`dram.topo.phy`). |
| "Bank" | the datasheet §2.2.2 (pdf p.16) calls an LPDDR4X package a bank | Say "package". |
| DRAM address map | chip tour fact L50 inferred it from a tool comment | Now et-spec (`ms_regs.h:160`) plus measured by one-bit flips on 3 cards (`dram.addr.channel`, `dram.addr.pa-map`). Tell the coordinator: chip fact L50, hub rows 26 and 33. |
| `zebumem.c` swizzle | prints a different map, "if using DDR DRAM models" | Ignore for silicon; note it in `dram.addr.pa-map`. |
| L3 latency budget | spec 34 + 30 shire clocks + about 26 against 72.2 clock-scaled cycles measured | Show both; per-step labels "not split: asked". |
| Open RTL against silicon | `external/core-et` is the Erbium branch; spec v1.1 also documents later chips (`l2.spec-version`); `core-et-main` is Ainekko's re-implementation (`l3` meta caveat) | The caveat markers in §2.1; the Sources section says it once. |

---

## 13. Asks for the team (merged and deduplicated)

These are proposed rows for the hub's improvement ladder
(`docs/reports/sources/limits-of-observability.data.json` `.improvements`; the rows today end at rung 36). The
coordinator adds them and their anchors. Each lists the unknown facts it closes and what it settles on this page.

### 13.1 New rows

| Rung (proposed) | Id | Group / status | What | What it settles |
|---|---|---|---|---|
| 37 | `ask-not-sram` | AI Foundry ask / ask_team | **Which of the chip's memories are not SRAM, and what cells they use.** (1) Which memories the lab lead meant by "not using SRAM". (2) The bitcell of the shire-cache macros (6T high-density, 8T, other), against the spec's "SRAM memory panels" (pdf p.48), the Synopsys-named 1PUHD/2PUHDRF macros (pdf p.51), the datasheet's 140 MB of SRAM (pdf p.4) and `core-et-main/AGENTS.md:609`. (3) Inside `dcache_128x32_1r1w_lram`: standard-cell latches placed like ET's `rf_latch_1r_1w_reg` library, or a custom or compiled latch array; transistors per bit; a static mux-tree read or a precharged read bitline. (4) The HDBULT08/HDBULT11 cell families and the "MMI (hand-tuned)" logic. (5) Whether the L1 is latch RAM because the minion's LV region (0.517 V measured) is below the SRAM panels' 585 mV Vmin (our inference); which other minion arrays (the VPU register file `vpu_64x32_3r2w`, the TLB) are latch arrays | The transistor views of every on-chip level: the L1's latch cell and read path (now the generic latch template) and the L2, L3 and scratchpad cell (now a generic 6T marked unknown); whether a shire-cache cell needs refresh (which would add a refresh step); the "why latches" caption confirmed or corrected. Closes `l1.u-cell`, `l1.u-why`, `l1.u-library`, `l2.storage-question`, `u.bitcell`, `scp.u-cell`, and the L3 file's `ask-l3-bitcell`. |
| 38 | `ask-memory-macros` | AI Foundry ask / ask_team | **Datasheets (or .lib summaries) of the memory macros.** For `saduls0g4l1p4096x144m4b4…`, `…1024x116…`, `saculs0g4l2p1024x40…` and `dcache_128x32_1r1w_lram`: rows × columns, column mux and internal banks (is `m4b4` a 4:1 mux and 4 banks?), sense-amplifier type, bitline length, whether a global read bus is precharged, energy per read and per write at the running voltage, and leakage per macro. The same need as hub rung 19 (a cell library and netlist), narrowed to the memories | Arrays and subarrays of L1, L2, L3 and the scratchpad drawn to scale instead of as illustrations; how many bitlines swing per access (half-select energy); the ledgers' energy split between array and periphery (now "not split"). Closes `l2.macro.name-decode`, `u.macro-geometry`, `scp.u-macro`, `l1.u-energy`, and the L3 file's `ask-l3-macro`. |
| 39 | `ask-cache-latency` | AI Foundry ask / ask_team | **Where each cycle of a cache access goes.** Stage-by-stage latencies for: an L1 hit (is it ID-EX-TAG-MEM-WB plus one cycle, with no S3 → EX bypass, and what costs hart 1 3 extra cycles on every L1 miss?); an L2 hit (21 shire clocks inside and 26 outside, of which only about 6 are placed); a read-buffer hit (10); an L3 hit (110 cycles = 72.2 clock-scaled + 61.4 ns, against the spec's 34 + 30 shire clocks); leaving and entering a shire for a remote scratchpad read (about 53 cycles). Confirm that shire_clock equals the minion clock on these cards. The NoC share overlaps `ask-noc-docs` | Per-step cycle labels on every access of L1, L2, L3 and the scratchpad (now only the totals are measured). Closes `l1.u-cycles`, `u.latency-split`, `scp.u-remote-split`, `scp.u-clock`, and the L3 file's `ask-l3-latency`; checks `l2.stages.budget`, `l3.lat-reconcile`. |
| 40 | `ask-silicon-config` | AI Foundry ask / ask_team | **Which options of the open drop the silicon has.** The open core-et is the Erbium branch, and the spec v1.1 also documents later chips. (1) Does the taped-out L1 carry parity or ECC, and can the minion arrays sleep? (2) Is there an L2 hardware prefetcher (`shire_cache_bank_l2hpf`)? (3) What is the read buffer built from (flip-flops in the re-implementation)? (4) Are the v1.1 macros the taped-out ones? (5) Does an L3 request pick its mesh lane by the home bank PA[12:11], as `core-et-main`'s `shirecache_mesh_master.sv:132-153` does? | Check bits drawn per L1 row or not; the prefetcher box drawn or removed; the read buffer's storage drawn; the L3 lane (and the correction to chip fact L103). Closes `l1.u-parity`, `l2.hpf`, `l2.rbuf.storage`; confirms `l3.lane`. |
| 41 | `ask-cache-esrs` | AI Foundry ask / ask_team (alternatively firmware / needs_fw_change) | **The live shire-cache settings on these cards.** `sc_pipe_ctl` (`esr_sc_ram_delay`, `esr_sc_zero_state_enable`, the read-buffer enables) and `shire_cache_ram_cfg1-4` (RM, RME, RA, WA, WPULSE, BC) on each card, at the 705 mV rail. The open firmware never writes them, and the emulator's reset values are the spec's RM0 "650 mV nominal" row. One service-processor read of one shire per card, or an M-mode read, would do | The panel access time drawn (2 cycles = 3.3 ns if 1:1); whether zero lines skip the panels on these cards; which read-assist and write-assist mode the cell animation shows. Closes `u.live-settings`, `scp.u-trim`, and the L3 file's `ask-l3-live-esrs`; checks `l2.trim.reset`, `scp.fw-no-trim`. |
| 42 | `ask-dram-part` | AI Foundry ask / ask_team | **The DRAM part.** The Micron part number, die density, dies per package, and x16 or byte-mode channels. The firmware reads MR5 and MR8 at every boot and logs them (`mem_controller_utils.c`), but no log has been captured; a boot log or the card's BOM line settles it. The part's datasheet gives whatever it publishes of the internal organisation | The DRAM die scale drawn from the actual part (density, dies, x16) instead of from the capacity and JEDEC; the generic die internals narrowed where the datasheet allows. Closes `dram.org.part`; narrows `dram.org.die-internals` (vendor-internal, may stay generic). |
| 43 | `exp-cache-bottleneck` | experiment on the cards / needs_tooling | **What caps a shire at 128 B per cycle.** Own-scratchpad and L2 streams reach exactly 4.0 B per minion-cycle, half the four banks' 256 B. Sweep: tensor-load stride 64 B (rotating banks), 256 B (one bank, rotating sub-banks: 614 GB/s, −33%, already measured), 1 KB (one bank and one sub-bank); 1 to 4 neighbourhoods per shire (one gives about 50 B per cycle). Ask the design team which block is the limit | Which block the diagram highlights when all 1,024 minions stream: sub-bank busy time, response crossbar, Fill FIFO, or the 256-bit minion port. Closes `scp.u-bw` (and the L2 file's bandwidth question). Cost: a mode of an existing benchmark, about ten minutes per card. |
| 44 | `exp-zero-state` | experiment on the cards / needs_fw_change | **How much the zero-line skip saves.** Clear `esr_sc_zero_state_enable` on one card for one L3 run (an M-mode ESR write) and compare zeros against random data. Compare with the scratchpad, where the skip does not apply and zeros still save about 90 pJ per line on the SRAM rail | Whether the L3 view shows the data panels idle for zero lines, and where the rest of the data-dependent energy sits (datapath, ECC, crossings). Closes `u.zero-share` and the L3 file's `ask-l3-zero`; tests `scp.e-data`. |

### 13.2 Existing rows that get a new effect (no new row)

- **`ask-design-docs` (rung 28), the Power Spec:** which rail feeds the shire-cache logic (pipeline, crossbars,
  queues, the high side of the VC FIFOs, the UC block) against the macros alone. It settles the rail band of each
  block and the split of SRAM-rail energy between arrays and logic. Closes `l2.rail.hv-logic`, `u.rail-of-logic`,
  `scp.u-rail`, and the L3 file's `ask-l3-rails`.
- **`ask-shire-floorplan` (rung 23):** add the minion's partition (where the 8 LRAM macros, tag register files and TLB
  sit, and their area) and the placement of the banks, sub-banks and 96 macros relative to the mesh stop and the L3
  slave ports. It settles the physical layer of L1, L2 and L3: the distances an access travels inside the tile. Closes
  `l1.u-floorplan`, `l2.floorplan`, `u.slice-floorplan`, and the L3 file's `ask-l3-floorplan`.
- **`ask-noc-docs` (rung 21) and `exp-route-order` (rung 32):** the router pipeline per hop, which of the 9 main-NoC
  layers carry L3 requests and replies, the flit width, and the dimension order. They settle the mesh-hop scale of L3
  and the remote scratchpad. Closes `u.noc-hop` and the L3 file's `ask-l3-noc`.
- **`ask-memshire` (rung 26):** now narrowed to the latency split. The address map is settled: PA[9] is the channel
  from the SoC's own reset value (`ms_regs.h:160`), and bank and row bits were measured by one-bit flips on 3 cards
  (`dram.addr.pa-map`). What remains is how the memory shire's ≤ 63 cycles split between the port and crossing, the
  controller's queues and the PHY. It settles the hatched bar at the memory-shire scale. Closes
  `dram.lat.ms-internal`.
- **`exp-dram-rows` (rung 33):** effectively done. The one-bit-flip data (`2026-09-19-memprobe-aifoundry2/summary.json`
  `bits[..]`, and the three-card row series) gives bank and row. The coordinator should mark it settled, or nearly, and
  update chip fact L50.
- **`ask-card-schematic` (rung 25):** already asks the package pairing. It settles the dashed pairing on the DRAM chip
  scale. Closes `dram.topo.pkg-pairing`.
- **Rung 20 (current sensing below the regulators):** the DRAM's off-rail 73 pJ/B, split between the memory shire's
  logic, PHY I/O, DRAM core and DRAM I/O, and refresh energy stay unmeasurable on the card. It settles the DRAM
  ledger's hatched energy cells; they stay open. Covers `dram.e.split-unknown` and `dram.seq.refresh.04`.
- **Rung 19 (a cell library and netlist):** `ask-memory-macros` (rung 38) is its memory-specific, more askable part;
  cross-link the two.

### 13.3 Every unknown in the inputs, by ask

| Ask | Unknowns it closes |
|---|---|
| `ask-not-sram` | `l1.u-cell`, `l1.u-why`, `l1.u-library`, `l2.storage-question`, `l3:u.bitcell`, `scp.u-cell` |
| `ask-memory-macros` | `l2.macro.name-decode`, `l3:u.macro-geometry`, `scp.u-macro`, `l1.u-energy` |
| `ask-cache-latency` | `l1.u-cycles`, `l3:u.latency-split`, `scp.u-remote-split`, `scp.u-clock` |
| `ask-silicon-config` | `l1.u-parity`, `l2.hpf`, `l2.rbuf.storage` (and confirms `l3.lane`) |
| `ask-cache-esrs` | `l3:u.live-settings`, `scp.u-trim` |
| `ask-dram-part` | `dram.org.part`, `dram.org.die-internals` (narrows only) |
| `exp-cache-bottleneck` | `scp.u-bw` |
| `exp-zero-state` | `l3:u.zero-share` |
| `ask-design-docs` (existing) | `l2.rail.hv-logic`, `l3:u.rail-of-logic`, `scp.u-rail` |
| `ask-shire-floorplan` (existing) | `l1.u-floorplan`, `l2.floorplan`, `l3:u.slice-floorplan` |
| `ask-noc-docs` + `exp-route-order` (existing) | `l3:u.noc-hop` |
| `ask-memshire` (existing) | `dram.lat.ms-internal` |
| `ask-card-schematic` (existing) | `dram.topo.pkg-pairing` |
| rung 20 (existing, impossible on silicon) | `dram.e.split-unknown`, `dram.seq.refresh.04` |

That is 34 unknown rows in the files (33 facts and one step), before de-duplication. The L3 file's nine `asks[]` map onto `ask-not-sram`,
`ask-memory-macros`, `ask-cache-esrs`, `ask-design-docs`, `ask-cache-latency`, `ask-silicon-config`, `ask-noc-docs`,
`exp-zero-state` and `ask-shire-floorplan`.

**Wording for the hub row `ask-not-sram`.** Quote the remark as "the lab lead said the chip is not using SRAM". Name
him only if the owner wants it on a public page. The owner's request names him, but the repo does not record the
remark.

---

## 14. Build and QA checklist

1. **Build.** `python3 docs/reports/data/2026-09-27-memory-levels/build_facts.py` passes every check in §2.2, then
   `scripts/build-report.py memory-levels …` builds. In a worktree without `node_modules`, set `NODE_PATH` as the
   script's docstring says.
2. **Headless.** Load the page and open every tab via its hash: `#l1`, `#l2`, `#l3`, `#scp`, `#dram`,
   `#l2/load-hit/9/cell`, `#dram/refresh`. There must be no console errors. Each deep link lands on the right level,
   access, step and scale, and the hash is posted to the parent (use a test harness frame).
3. **Every access.** Every access of every level plays to its end with Dive off and with Dive on, paused and stepped
   (end states), and with `prefers-reduced-motion`.
4. **Screenshots** at 1920 × 1080 (presenting), 1280 × 720, 1024 × 768 and 390 × 844, light and dark. The stage shows
   no clipped text. At 390 the page does not scroll horizontally; only the drawing box does.
5. **Keyboard only.** Tab through the header, tabs, parts and panel. Check every key in §1.3, including the tablist's
   arrow keys against the stage's arrow keys.
6. **Source check.** For every printed number, hovering it shows a source; spot-check 20 against their files.
7. **Honesty.** Every unknown part is dashed and links to an ask. Every generic frame carries the GENERIC tag. No
   generic circuit shows an ET-looking number.
8. **Scope.** `git status` shows only the new files of §0. No existing file changed.

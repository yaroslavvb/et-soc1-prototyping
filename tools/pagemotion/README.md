# pagemotion: how smoothly an animated page moves, frame by frame

The tools that found why the memory levels and the chip diagram jumped in the middle of their camera moves (30 September
2026; results and method in [`docs/reports/data/2026-09-30-page-motion/`](../../docs/reports/data/2026-09-30-page-motion/README.md)).
They drive the installed Google Chrome headless over the DevTools protocol with Node's own WebSocket and fetch: no
packages to install. On a Mac, headless Chrome rasterises on the real GPU (ANGLE Metal), so the timings are the machine's.

| File | What it does |
|---|---|
| `drive.mjs PAGE HASH OUT.json [W H DPR MAXSECONDS]` | loads a built page (a file, or a local server's `http://` address), lets an access (or a scenario) play, and saves one row per animation frame; environment: `UDD` a Chrome profile to reuse (**use one**: a fresh profile compiles GPU shaders at every first paint, 50–150 ms spikes a returning visitor does not see), `SCEN` key presses and clicks as JSON (`[{"wait":1500},{"key":"ArrowRight","mod":8}]`), `UNTIL` a JS condition to stop on, `REC`/`STATE`/`STEPTXT` for another page (the chip diagram: `REC=./recorder-chip.js`), `PRE` JS or CSS injected at load (for ablations), `TRACE` a Chrome performance trace, `CAST` a screencast (JPEG frames), `CPU` a slowdown factor |
| `recorder.js`, `recorder-chip.js` | injected before the page's scripts: each frame's time, step, and every shown layer's transform, opacity and label fade (`#mem > g.lay` on the memory levels, `#chip > g.lay` on the chip diagram) |
| `instrument.py IN OUT` | a copy of a memory-levels build that times the camera's suspect functions (`window.__T`) |
| `analyze.py RUN.json [-v]` | frame timing (late frames: > 25 ms) and the camera's moves; `-v` prints every frame |
| `summ.py RUN.json …` | one line per run: the camera's frames, late frames, the worst frame's motion |
| `motion.py RUN.json [STEP]` | the camera's velocity each frame (the frame centre's motion and the zoom rate) |
| `kink.py RUN.json` | per move, the largest frame-to-frame change of that velocity as a share of the move's top speed: an eased move changes a few % a frame; a turn or a change of pace at a scale shows as 60–110% |
| `trace_an.py TRACE.json RUN.json` | what each late frame's main thread and raster threads were doing |
| `sheet.py RUN.json CASTDIR OUT` | a contact sheet of each camera move from a screencast |
| `shot.mjs PAGE HASH OUT.png [W H DPR WAIT JS]` | a screenshot after optional JS (phone widths emulate touch) |
| `ui_test.mjs PAGE` | the memory levels' player bar driven by real key and mouse events |
| `cdp.mjs` | a small DevTools driver for the tests below: open (desktop or touch phone, dark, reduced motion, CPU slowdown), load, real mouse, touch and key events, screenshots |
| `zoom_test.mjs PAGE [--phone] [--only=T1,T4] [--scenes=a,b]` | the chip diagram's zoom tests (its DESIGN §6.2; since 1 Oct 2026 the shared ladder's DESIGN §5.4): T1 a double-click (double-tap) on one part of every kind in each scene, then Up; T2 a click selects without moving; T3 Up from the deepest scale (the Planck length) to the top, round the ring of sizes and in again, and the breadcrumb; T4 the shires' edge links (click, Enter, arrows; each a glide); T5 + from the top of the ladder to the Planck length and round the ring to the top, every layer's scale in [1/30, 30] and every transform a scale and a translation; T6 every stage of every flow lands where it wants the camera, the tour, a flow started far from the chip (the ring included); T7 reduced motion (the wrap too); T9 the page without its folder (images and data); T11 labels, names, announcements, focus; T12 the wrap's two ways back in; T14 the easter egg (no level above the rack named on the page, Up still finds them); T15 the two-state electronics; T16 the dive from the die to a quark by double-clicks. Scenes are `?at=` paths. PAGE may be a local server's `http://` address, so that the page's lazily fetched data loads (file:// forbids the fetch) |
| `zoom_static.py PAGE` | the chip diagram's size, privacy and easter-egg checks (T9, T10, T14): the page, script, data, lazy data and image budgets; no IPv4-like string, no street address, house number, ZIP code, coordinates or listing link for Studio 45, the AI Plumbers event left out, the images' sha256 against the manifest, no EXIF/XMP/ICC; no level above the rack named in the static text |

```bash
cd tools/pagemotion
python3 ../../scripts/build-report.py memory-levels ../../docs/reports/data/2026-09-28-memory-levels/facts.json ../../build/ml.html
UDD=$HOME/.cache/pagemotion-profile node drive.mjs ../../build/ml.html '#dram/load' run.json 1280 800 2 150
python3 summ.py run.json && python3 kink.py run.json
```

Headless frame times depend on the machine and on what else runs: compare before and after on the same machine,
one run at a time, with the same profile, and repeat a run before believing a single late frame.

What the chip diagram's deep zoom taught (30 September; runs in `~/claude/work/chipzoom/motion/` on aifoundry2):

- **Slow the CPU before believing a page is smooth.** At normal speed every build had under 1.5% late frames; with
  `CPU=4` the same build had 50–80%, and the causes were invisible without it. Compare against the page before the
  change with the same flow, interleaving the runs (A, B, A, B): one run of each is not enough at `CPU=4`.
- **A text readout that changes every frame lays out its bar every frame.** The scale readout cost a slowed flow about
  a third of its frames; updating it ten times a second (and at the end of the move) brought it back to the base page.
- **A long table below the stage costs every frame**, even far off screen, once the stage relayouts each frame:
  `content-visibility: auto` on the table's wrapper (with `contain-intrinsic-size`) removed that cost (800 rows: 50–64%
  late frames slowed, 16–20% with it). One price seen in this headless Chrome: its page-content agent
  (`blink.mojom.AIPageContentAgent`, about 1.2–1.7 s after load) forces one layout of the skipped content, a single
  100 ms frame at normal speed. A trace with `TRACE_CATS=...,disabled-by-default-devtools.timeline.invalidationTracking`
  names what invalidates layout and from which line.
- **`pkill -f PATTERN` from a shell whose own command line contains PATTERN kills that shell** (exit 144): stop runs by
  their process id.

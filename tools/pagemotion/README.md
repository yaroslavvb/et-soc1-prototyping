# pagemotion: how smoothly an animated page moves, frame by frame

The tools that found why the memory levels and the chip diagram jumped in the middle of their camera moves (30 September
2026; results and method in [`docs/reports/data/2026-09-30-page-motion/`](../../docs/reports/data/2026-09-30-page-motion/README.md)).
They drive the installed Google Chrome headless over the DevTools protocol with Node's own WebSocket and fetch: no
packages to install. On a Mac, headless Chrome rasterises on the real GPU (ANGLE Metal), so the timings are the machine's.

| File | What it does |
|---|---|
| `drive.mjs PAGE HASH OUT.json [W H DPR MAXSECONDS]` | loads a built page, lets an access (or a scenario) play, and saves one row per animation frame; environment: `UDD` a Chrome profile to reuse (**use one**: a fresh profile compiles GPU shaders at every first paint, 50–150 ms spikes a returning visitor does not see), `SCEN` key presses and clicks as JSON (`[{"wait":1500},{"key":"ArrowRight","mod":8}]`), `UNTIL` a JS condition to stop on, `REC`/`STATE`/`STEPTXT` for another page (the chip diagram: `REC=./recorder-chip.js`), `PRE` JS or CSS injected at load (for ablations), `TRACE` a Chrome performance trace, `CAST` a screencast (JPEG frames), `CPU` a slowdown factor |
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

```bash
cd tools/pagemotion
python3 ../../scripts/build-report.py memory-levels ../../docs/reports/data/2026-09-28-memory-levels/facts.json ../../build/ml.html
UDD=$HOME/.cache/pagemotion-profile node drive.mjs ../../build/ml.html '#dram/load' run.json 1280 800 2 150
python3 summ.py run.json && python3 kink.py run.json
```

Headless frame times depend on the machine and on what else runs: compare before and after on the same machine,
one run at a time, with the same profile, and repeat a run before believing a single late frame.

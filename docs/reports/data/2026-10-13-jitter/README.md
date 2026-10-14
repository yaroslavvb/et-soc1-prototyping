# Text that changed size, and moves that stuttered (13 October 2026)

Request Q108 ([`02-requests.md`](../../../findings/02-requests.md)): the owner, with a screenshot of the chip diagram's
readout "1.3 km · 10³ m" mid-move at `#at=st29`: "The text sometimes changes in size ... when I click while it's
animating, it's larger, and then it goes back to the original size. Go through a diagram and fix various cosmetic
inconsistencies like this." Then: "Also, the animation is sometimes not smooth. It's jittery sometimes. See if you can
identify the issue and make sure there is no jitter." No card time: headless Chrome 155 on the owner's Intel Mac (Core
i9-9880H, macOS 26.6.2), 1440 × 900 at 2× unless noted. The fixes are in the ladder's README, "The readout's one look,
smoother moves, Studio 45 from its plans".

## The tools

| File | What it does |
|---|---|
| `cosmo_probe.py` | The page's chrome on every animation frame (box, type size and weight of the Up button, the crumbs, the readout, − and +, the drawing, the caption, the bars), through the default chain (+ pressed 46 times from `#at=die.metal`: down to the Planck length, round the loop, out past Studio 45 and in again) and, with `--flows`, every flow stage by stage; a screenshot and every label's on-screen size at each rest |
| `cosmo_analyze.py` | What changed type or moved, and in which move; the labels' sizes by class across the scales; `--sheets` makes contact sheets |
| `jit_probe.py` | Frame timing with as little measuring as possible: `performance.now()` and each shown layer's transform per frame, attribute reads only (the cosmetic probe's style reads force layouts of their own); `--cpu 4` slows the CPU four times; `--trace` records a Chrome trace with V8's sampling profiler |
| `jit_analyze.py` | Per move: late frames (over 25 ms) and where in the move they fall |
| `trace_jank.py` | What the main thread did in the late frames: trace events by name and the JS functions on the stack |
| `bench_ops.py` | The cost of each kind of DOM write a camera frame makes, timed with a forced style and layout after each (`VP=390x844` for a phone) |

Run each with `uv run --with playwright python <tool> ...` against a directory holding the built page as
`chip/index.html` beside a copy of `docs/reports/ladder-img/` (and an empty `favicon.ico`).

## What the probes found

**The text that changed size.** Over the walk's 3,623 frames the readout was 13.4 px regular at rest, 18.4 px bold during
the 1,492 frames of jumps, and semi-bold during the loop: CSS classes `.jump` and `.ring` set while the camera moved.
After the fix no element of the chrome changes type size or weight on any frame of the walk, and in the flows only the
caption does, from one flow to the next (below). The other changes found: the drawing 6.7 px shorter whenever a flow
was on (the playback bar kept two lines' room for the stages but not for the hint shown
before a flow is picked: fixed, and over the flows' 10,709 frames after, the drawing's box does not move or change size), and the caption's size, which `fitCap` sets per flow so its longest stage fits two lines
(flow B 20.7 px, flow 6 23.7 px, the rest 24.7 px at 1440 × 900): kept, since it holds for a whole flow.

**The stutter.** A trace of a flow and six zooms logged 466,533 layout invalidations in about 20 seconds, nearly all
"SVG changed". `bench_ops.py` timed the writes a camera frame makes, scale by scale (ms, a write plus the layout it
forces, at the die):

| Write | Before | After |
|---|---|---|
| The layer's transform attribute | 0.8 | 0.9 |
| The six custom properties that dim the context | 1.5 | 1.5 |
| The stroke keeper (every stroked shape's width) | 1.9 | 1.9 |
| The readout's text (ten times a second while moving) | **8.6** | **0.1** |
| The crumbs (at each step) | **7.9** | **0.3** |

Every change in the Up bar laid the whole drawing out again: the drawing's box took its size from the flexbox, so
LayoutNG could not reuse its layout when the column around it changed. Containment alone (`contain: size layout`) did
not help, nor did positioning the drawing absolutely; giving the box its size in pixels did (`pinView`, a wide screen
only: on a phone the drawing's box is sized by its aspect ratio and these writes already cost 0.1 to 0.3 ms). The second
cause was the first build of a scale on the zoom's first frame: a textbook circuit took up to 233 ms (`prebuildNext`
now draws the scale + leads to in an idle moment).

## The numbers

Frames while the camera moves, the walk (46 presses of +) and the flows (each flow's stages, stepped by the arrow key):

| Build | Walk, late frames | Walk, worst frames (ms) | Walk at 4× CPU, late | 4× worst (ms), frames over 100 ms | Flows, late |
|---|---|---|---|---|---|
| The page of 13 Oct, before | 85 of 2,327 (3.7%) | 150, 117, 100 | 517 of 1,646 (31.4%) | 600, 550; 119 | 103 of 794 (13.0%) |
| The drawing's box pinned | 31 of 2,379 (1.3%) | 233, 50, 50 | 247 of 2,175 (11.4%) | 233, 200; 33 | 87 of 808 (10.8%) |
| ... and the next scale drawn ahead (final) | 33 of 2,382 (1.4%) | 50, 33, 33 | 239 of 2,176 (11.0%) | 183, 183; 30 | 93 of 807 (11.5%) |

What is left is in the flows: about one frame in nine is late on this Mac at 2×. Their traces show style and layout
(the inherited custom properties that dim the context, rewritten each frame for the first third of a move, and the
stroke keeper's widths) and the panel's build when a flow starts. Those are the page's design, not a mistake: removing
them means drawing the dimming another way. Not done here.

# Four physical scales in 3D

2026-10-14 (Wed, week 42), Q109. The owner asked for engaging interactive 3D visualizations linked from the chip diagram's metal, FinFET, fin and channel scales.

The standalone source is [`../../chip-3d.html`](../../chip-3d.html). Its four hash routes are `#metal`, `#finfet`, `#fin` and `#channel`. The original page adds a corresponding link immediately below each scale's panel title, plus a four-view index. The integration lives in `sources/chip-diagram.script.js` and `sources/chip-diagram.body.html`; rebuild the original page with the existing `build-report.py` command in MIRROR.md. `tools/publish-gh-pages.sh` also publishes the companion under `chip-3d/`.

The companion uses dimensionless 3D geometry, perspective projection, lit depth-sorted faces and component picking. It has mouse/touch orbit, keyboard orbit and zoom, preset viewpoints, reset, layer separation, gate/oxide separation, fin count, a qualitative gate-drive control, and play/pause. Reduced-motion starts paused. Hidden tabs stop animation.

The models are illustrative. They do not reconstruct ET-SoC-1 layout, process dimensions or metal-layer count. Charge and motion are qualitative. The n-channel example fixes a positive drain–source bias; electrons move from source to drain and conventional current points oppositely. Berkeley's multi-gate model documentation explains that narrow-fin inversion charge can extend into the body: the surface glow is a drawing convention. The source footer links public TSMC interconnect research and Chenming Hu's MOSFET chapters.

Browser QA uses one headless Chrome instance, reused for all cases. Initial checks at 1280 and 390 CSS pixels covered all four companion routes and the four original deep links: no JavaScript errors or horizontal page overflow. Every scene's primary control changed rendered pixels. Component buttons updated selected descriptions; keyboard orbit changed the image. Gate drive at zero removed the illustrated channel, with stable pixels during playback. Final checks include maximum separation, dark theme, narrow phone layout, source/deploy parity and live deep-link forwarding.

No card, lab hardware or private design data was used.

## Perspective correction (Q110)

The owner's follow-up: “Fix the perspective. Dragging things around shouldn't change the zoom.” The first version refitted the projected bounding rectangle on every draw. Turning the model changed that rectangle, so the fit multiplied magnification even while the explicit zoom state stayed at 1. A real pointer drag reproduced a 1.1329× scale change.

The camera now orbits a fixed world-space target at a fixed distance of 16 illustrative units. Scene framing is derived once from an unrotated bounding sphere covering the full range of the scene's controls; only viewport resize recomputes its base focal scale. Dragging, keyboard orbit, view presets, auto-orbit, and geometry controls preserve target-plane magnification. Explicit zoom multiplies that scale. Labels, particles and component picking use the same perspective projection.

`camera-test.mjs` exposes measurements only in an in-memory browser copy. It first reproduces the old failure, then drives real pointer/keyboard input on all four views at 1280 and 390 CSS pixels. It checks target-plane magnification and centering, explicit 1.15× zoom, auto-orbit, maximum geometry controls, a full turn within the fixed frame, and no page errors/overflow. Eight cases passed; the baseline failure was detected. Run with a Playwright installation and installed Chrome: `node docs/reports/data/2026-10-14-chip-3d/camera-test.mjs`; `PLAYWRIGHT_MODULE` and `CHROME_HEADLESS` can select installed runtimes.

## Stable gate labels (Q112)

The owner's next feedback: “When I rotate it around, the gate label keeps jumping.” The collision solver placed Gate after Source and Drain, moving overlapping labels down in 25-pixel increments. Small rotations crossed collision thresholds: the regression reproduced a maximum 50.01-pixel step.

FinFET and channel views now place Gate at the top center and Source/Drain at the lower corners, with the channel pair above the direction legend. Label slots depend only on viewport and scene; leaders attach to each projected physical part and are drawn before the text boxes. The channel gate leader attaches to the electrode's actual top. The gate label is visible on phones as well. Camera projection is unchanged.

`label-test.mjs` measures actual canvas `fillText` positions in an in-memory test copy. It reproduces the old step, then sweeps a full turn across five pitches and three zoom levels at 1280 and 390 pixels for FinFET and channel. Both views at both sizes had zero label drift and zero magnification drift, with no page errors or overflow. The leaders' projected anchors remain continuous. Run with the same runtime overrides as the camera test; screenshots go to ignored `build/chip-3d-labels/`.

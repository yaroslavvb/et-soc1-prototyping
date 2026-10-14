# Four physical scales in 3D

2026-10-14 (Wed, week 42), Q109. The owner asked for engaging interactive 3D visualizations linked from the chip diagram's metal, FinFET, fin and channel scales.

The generated portable artifact is [`../../chip-3d.html`](../../chip-3d.html), published at the same [Spacesheep companion URL](https://spacesheep.dev/@yaroslavvb/et-soc1-in-3d). Its four hash routes remain `#metal`, `#finfet`, `#fin` and `#channel`. The original page adds a corresponding link immediately below each scale's panel title, plus a four-view index. That integration lives in `sources/chip-diagram.script.js` and `sources/chip-diagram.body.html`; rebuild the original page with the existing `build-report.py` command in MIRROR.md. `tools/publish-gh-pages.sh` also publishes the companion under `chip-3d/`.

The current companion uses a researched WebGL renderer with Three.js bundled into the HTML. Its editable sources are under [`../../sources/chip-3d/`](../../sources/chip-3d/):

- `shell.html` and `style.css`: page structure, responsive layout and presentation.
- `app.js`: routes, controls, selection and synchronization of the 3D and section views.
- `viewer.js`: perspective camera, lighting, shadows, material picking and fixed callout slots.
- `models.js`: original geometry for the four scales and symbolic carrier motion.
- `content.js`: explanations, material colors and responsive SVG cross-sections.

Build from the repository root:

```sh
npm ci
node scripts/build-chip-3d.mjs
```

Three.js `0.180.0` and esbuild `0.25.11` are pinned build dependencies. The builder bundles the viewer and library, inlines the CSS, preserves the Three.js license and validates the embedded JavaScript. The resulting HTML needs no runtime network request for its 3D library, textures or lighting environment; the studio reflections are generated procedurally. Edit the source modules and rebuild rather than hand-editing the generated artifact.

The viewer supports mouse/touch orbit, explicit wheel/pinch/button zoom, keyboard controls, preset viewpoints, reset, auto orbit, cutaways, component picking and flow playback. Orbit preserves camera distance and magnification; text callouts occupy fixed viewport slots while their leader endpoints track physical parts. Reduced-motion starts flow paused. Hidden tabs stop animation. Text explanations and SVG sections remain available if WebGL cannot initialize.

The models are illustrative. They do not reconstruct ET-SoC-1 layout, process dimensions or metal-layer count. Thin layers and symbolic electron markers are enlarged for clarity; charge, motion and gate-drive values are qualitative. The n-channel example fixes a positive drain–source bias: electrons move source to drain and conventional current points oppositely. Inversion charge is inside silicon, and the inspection view can make its surface slices translucent. Narrow-fin charge can extend into the body, so near-surface highlights are a teaching convention rather than three independent wires. A low-drive view omits bright charge without claiming zero physical leakage. The footer links Intel, imec, TSMC and Berkeley primary sources; see the [research record](visual-research.md) for figure references and physical caveats.

No card, lab hardware or private design data was used.

## Original renderer checks (Q109, historical)

Browser QA uses one headless Chrome instance, reused for all cases. Initial checks at 1280 and 390 CSS pixels covered all four companion routes and the four original deep links: no JavaScript errors or horizontal page overflow. Every scene's primary control changed rendered pixels. Component buttons updated selected descriptions; keyboard orbit changed the image. Gate drive at zero removed the illustrated channel, with stable pixels during playback. Final checks include maximum separation, dark theme, narrow phone layout, source/deploy parity and live deep-link forwarding.

## Perspective correction (Q110, historical canvas renderer)

The owner's follow-up: “Fix the perspective. Dragging things around shouldn't change the zoom.” The first version refitted the projected bounding rectangle on every draw. Turning the model changed that rectangle, so the fit multiplied magnification even while the explicit zoom state stayed at 1. A real pointer drag reproduced a 1.1329× scale change.

That correction made the canvas camera orbit a fixed world-space target at a fixed distance of 16 illustrative units. Scene framing was derived once from an unrotated bounding sphere covering the full range of the scene's controls; only viewport resize recomputed its base focal scale. Dragging, keyboard orbit, view presets, auto-orbit, and geometry controls preserved target-plane magnification. Explicit zoom multiplied that scale. Labels, particles and component picking used the same perspective projection. The current WebGL viewer preserves this behavior with its own scene bounds and camera implementation.

`camera-test.mjs` exposes measurements only in an in-memory browser copy. It first reproduces the old failure, then drives real pointer/keyboard input on all four views at 1280 and 390 CSS pixels. It checks target-plane magnification and centering, explicit 1.15× zoom, auto-orbit, maximum geometry controls, a full turn within the fixed frame, and no page errors/overflow. Eight cases passed; the baseline failure was detected. Run with a Playwright installation and installed Chrome: `node docs/reports/data/2026-10-14-chip-3d/camera-test.mjs`; `PLAYWRIGHT_MODULE` and `CHROME_HEADLESS` can select installed runtimes.

## Stable gate labels (Q112, historical canvas renderer)

The owner's next feedback: “When I rotate it around, the gate label keeps jumping.” The collision solver placed Gate after Source and Drain, moving overlapping labels down in 25-pixel increments. Small rotations crossed collision thresholds: the regression reproduced a maximum 50.01-pixel step.

That correction placed Gate at the top center and Source/Drain at the lower corners in the FinFET and channel views, with the channel pair above the direction legend. Label slots depended only on viewport and scene; leaders attached to each projected physical part and were drawn before the text boxes. The channel gate leader attached to the electrode's actual top. The gate label was visible on phones as well. The current WebGL viewer extends fixed callout slots to all four scenes.

`label-test.mjs` measures actual canvas `fillText` positions in an in-memory test copy. It reproduces the old step, then sweeps a full turn across five pitches and three zoom levels at 1280 and 390 pixels for FinFET and channel. Both views at both sizes had zero label drift and zero magnification drift, with no page errors or overflow. The leaders' projected anchors remain continuous. Run with the same runtime overrides as the camera test; screenshots go to ignored `build/chip-3d-labels/`.

## Researched WebGL upgrade (2026-10-14, Q113)

The owner's follow-up: “Improve the quality of these diagrams. Do some research to find good visualizations and create a higher-quality visualization with more details.” The [research record](visual-research.md) identifies the inspected Intel transistor diagrams, Hu fin and channel sections, and imec interconnect figures, with explicit limits on transferring their details to this generic model.

The new renderer adds physically shaded materials, rounded and faceted geometry, environment reflections, soft shadows and responsive explanatory sections. The four scenes now show:

- **Metal:** four teaching tiers, barrier/liner rims, connected vias, an animated illustrative route, an optional dielectric envelope and a dielectric cutaway.
- **FinFET:** a fin rooted in bulk silicon, STI, raised source/drain regions, separate contact plugs, spacers and a thin high-k dielectric under a three-sided gate. Gate lift is an exploded inspection view; the dielectric stays on silicon.
- **Fin:** one to four fins under a common gate, shared terminal connections, symbolic height/thickness guides and the idealized perimeter relation `W_eff ≈ N × (2H_fin + T_fin)`.
- **Channel:** inversion volumes within silicon, qualitative gate-drive response, symbolic electron motion and field-direction arrows in the cutaway, with the positive drain bias stated explicitly.

[`quality-test.mjs`](quality-test.mjs) replaces the old `camera-test.mjs` and `label-test.mjs` for the WebGL renderer. Those two earlier tests are retained as historical baseline evidence and do not exercise the current architecture. The quality test checks all four scenes at 1280 and 390 CSS pixels in one reused headless Chrome instance. It checks WebGL initialization, script errors, page overflow, real pointer dragging without zoom/scale or label-slot drift, explicit zoom, geometry controls, preset views and selectable explanations. It also captures dark-theme and 320-pixel channel views. Outputs go to ignored `build/chip-3d-quality/`, including screenshots and `results.json`.

Run after rebuilding, using an installed Playwright package and Chrome:

```sh
node docs/reports/data/2026-10-14-chip-3d/quality-test.mjs
```

Set `PLAYWRIGHT_MODULE` to an installed Playwright module when it is not resolvable locally. Set `PAGE` to a served or deployed companion URL to exercise the same checks there. The test-only introspection API is enabled by the `?qa` query parameter. Final QA and deployment results are recorded separately; this section describes the checks rather than asserting a completed run.


### Final Q113 verification

Local 1280/390px interaction checks passed for all four scenes. `motion-test.mjs` reuses the repository's `tools/pagemotion/recorder.js` for interleaved old/new runs and checks fixed zoom/labels during auto-orbit and a 64-step keyboard sweep. `live-smoke.mjs` verifies the actual Spacesheep viewer iframe and hash forwarding at both widths; all eight cases passed. `quality-results.json` records the results. Run those scripts with the same `PLAYWRIGHT_MODULE` override. For motion comparison, first save the pre-upgrade baseline with `git show bd8e731a:docs/reports/chip-3d.html > build/chip-3d-before.html`.

`PAGE` on `quality-test.mjs` is for an HTML document served directly (such as GitHub Pages). Spacesheep's raw URL redirects top-level browsers into its viewer; use `live-smoke.mjs` for that host. The generic `check_page.sh` disables GPU, so it checks the explanatory fallback and layout rather than the WebGL rendering. Both public mirrors equal the built source; Spacesheep version `7f69884894ba`, successful GitHub workflow `38611452659`.

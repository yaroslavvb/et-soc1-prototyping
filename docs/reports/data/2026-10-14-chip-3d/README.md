# Four physical scales in 3D

2026-10-14 (Wed, week 42), Q109. The owner asked for engaging interactive 3D visualizations linked from the chip diagram's metal, FinFET, fin and channel scales.

The standalone source is [`../../chip-3d.html`](../../chip-3d.html). Its four hash routes are `#metal`, `#finfet`, `#fin` and `#channel`. The original page adds a corresponding link immediately below each scale's panel title, plus a four-view index. The integration lives in `sources/chip-diagram.script.js` and `sources/chip-diagram.body.html`; rebuild the original page with the existing `build-report.py` command in MIRROR.md. `tools/publish-gh-pages.sh` also publishes the companion under `chip-3d/`.

The companion uses dimensionless 3D geometry, perspective projection, lit depth-sorted faces and component picking. It has mouse/touch orbit, keyboard orbit and zoom, preset viewpoints, reset, layer separation, gate/oxide separation, fin count, a qualitative gate-drive control, and play/pause. Reduced-motion starts paused. Hidden tabs stop animation.

The models are illustrative. They do not reconstruct ET-SoC-1 layout, process dimensions or metal-layer count. Charge and motion are qualitative. The n-channel example fixes a positive drain–source bias; electrons move from source to drain and conventional current points oppositely. Berkeley's multi-gate model documentation explains that narrow-fin inversion charge can extend into the body: the surface glow is a drawing convention. The source footer links public TSMC interconnect research and Chenming Hu's MOSFET chapters.

Browser QA uses one headless Chrome instance, reused for all cases. Initial checks at 1280 and 390 CSS pixels covered all four companion routes and the four original deep links: no JavaScript errors or horizontal page overflow. Every scene's primary control changed rendered pixels. Component buttons updated selected descriptions; keyboard orbit changed the image. Gate drive at zero removed the illustrated channel, with stable pixels during playback. Final checks include maximum separation, dark theme, narrow phone layout, source/deploy parity and live deep-link forwarding.

No card, lab hardware or private design data was used.

# Why the interactive pages jumped, and the fix (30 September 2026)

Requests Q74–Q76 ([`02-requests.md`](../../../findings/02-requests.md)): the owner saw the memory levels' animations
"still jumpy in the middle" (`#dram/load`), then asked for a play button and a scrubber on top with the keys shown, and
for the same lessons on the chip diagram with a details panel a beginner can read. No card time: everything here is
headless Chrome 154 on the owner's Mac (Apple M5 Max, macOS 26.6; Chrome rasterises on the GPU through ANGLE Metal),
driven by [`tools/pagemotion/`](../../../../tools/pagemotion/README.md), 1280 × 800 at 2× pixel density unless noted.

## What was measured

Every animation frame's time and the transform, opacity and label fade of every layer shown (`recorder.js`), while an
access or a flow played by itself. From those: the late frames (over 25 ms) and the camera's velocity each frame, the
frame centre's motion and the zoom rate (`motion.py`); `kink.py` gives each move's largest frame-to-frame change of that
velocity as a share of the move's top speed. A Chrome trace (`trace_an.py`) says what a late frame did, and ablations
inject CSS at load (`PRE`).

## What made the memory levels jump (the page of 29 September)

1. **The path.** A move through several scales was a chain of separate zooms, each around its own point and each timed
   by the scale's nominal width `tw`, which was up to 7.7 times off on a log scale (the PHY: a 1.37× zoom timed as an
   11× one). At every scale passed the zoom rate jumped (×1.9 at the channel in step 6) and the pan turned at the
   camera's top speed; a move out and back in (step 9: channel → memory shire → PHY) reversed at full speed. The
   largest frame-to-frame velocity change was 65–114% of the top speed in every move (`results/memory-levels-dram-load.txt`).
2. **The paint.** In a slow frame the raster threads spent 50–85 ms re-rasterising the whole drawing at its new scale,
   and the main thread waited for them. The labels' knockout halos (a stroke under every label) were most of it:
   Blink rasterises a stroked glyph again at every scale. Without the halos the late frames fell from 5.8% to 0.3%,
   with `text-rendering: geometricPrecision` to 0.7%, with both and the halos only off while the camera moves to 0 of
   932 (`results/memory-levels-ablation.txt`); the filters did nothing.
3. **After a stall, a leap.** The clock let one frame move things on by up to 80 ms, so a stall (the page loading)
   became a jump.
4. **Not causes.** Building the next view (6 ms at most) and the other JS at a segment's end (under 30 ms, at rest).
   The frames that were late when a view first appeared came from GPU shader compiles: a fresh Chrome profile compiles
   them at every first paint; with a profile kept between runs, as a visitor's browser keeps one, they were gone.

## The fix

- **Memory levels:** a move is one leg, or two (out to the scale the view and the target share, then in); a leg is
  one pure zoom along its chain of scales, drawn in its root's coordinates, so the camera goes straight at one point
  through every scale; two legs meet at rest; each view's fade, labels and context follow from where the camera is,
  and an outer view stays until the inner covers the screen. Halos are off while the camera moves; faded labels are not
  painted; the clock moves on at most 40 ms a frame. And the player bar on top.
- **Chip diagram:** its moves were already one timeline with correct lengths, so only the path changed: a leg eases
  once, goes through the rest of every scale it passes (drawn whole, as before), and turns smoothly there (the two
  zooms blend over 0.45 of the shorter's log length); out and in meet at rest; the 40 ms clock cap. Its panel leads
  with plain words; the numbers, the address bits and the sources are under Details.

## Results

| | Before | After |
|---|---|---|
| Memory levels, `#dram/load`: late camera frames | 5.8% (max 117 ms), two runs | 0 (max 16.8 ms), two runs |
| … largest frame-to-frame velocity change in a move | 65–114% of the top speed | 3–11% (11%: the two-leg move easing to its rest) |
| … all 28 accesses with Dive on | | every one completes, no console error |
| Chip diagram, flows 1, 8, 11 and the tour: late camera frames | 0–2 | 0 |
| … largest velocity change in a move | 78–92% (dives through a shire) | 11–12% (the blended turn) |

`results/` holds the full outputs; `runs/` four raw recordings (gzipped JSON, one row per frame: the DRAM load before
and after, the chip diagram's flow 1 before and after).

## Also seen

The spacesheep viewer does not pass its address's `#…` into the framed page, at load or on a change, so
`https://spacesheep.dev/@yaroslavvb/et-soc1-memory-levels#dram/load` opens at L1; the raw address
(`https://3ec78e9e-1f89-4258-8e30-eee4ca4a27cc.spacesheep.app/#dram/load`) opens the DRAM load. The viewer's own code
has a forwarder for it (`fwdHash`), which did not act here. The page cannot see the viewer's address, so it cannot work
around this.

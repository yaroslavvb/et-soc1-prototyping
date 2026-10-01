# Gesture checks for the session timeline

Synthesized input for the page's two timeline frames, in the page checker's browser (Playwright's
chrome-headless-shell, driven over the DevTools protocol by `cdp.mjs`; Node 24, no packages). Throwaway browser profiles
go to `$GESTURE_WORK` (default `~/claude/work/timeline-gestures`). Pass the page as an absolute path: the scripts open `file://` + the argument.

| Script | What it does |
|---|---|
| `suite.mjs <page.html> <outdir>` | Phones (390×844 and 360×740, DPR 3, touch, 4× CPU throttle): a vertical swipe, a sideways swipe (its momentum), a 45° swipe, mostly sideways and mostly vertical swipes, a two-finger pinch, a tap on a flag (and a second tap), a tap on a bar and a tap with 6 px of jitter. Desktop (1280×800): a vertical wheel, deltaX, a vertical-then-sideways wheel gesture, Shift + wheel, Ctrl + wheel (the focal point's drift), a mouse drag, the axis's keys and a zoom button's animation. For each: the page's scroll, the view's change, the tooltip, and frame times (rAF intervals, redraw times, long tasks). Writes `results.json` and screenshots |
| `frames.mjs <page.html> <outdir>` | a slow sideways pan on a 390-px phone, one screenshot per step and after the finger lifts, and `sheet.png` |
| `diag.mjs <page.html> <dx> <dy>` | one swipe of 14 steps of (dx, dy) px on the chart: the page's scroll and the pointer events the page saw |
| `count2.mjs <page.html> [width] [cpu]` | redraw times, fast and full, at three zooms, and the number of SVG nodes |
| `profile.mjs <page.html> [width] [trace.json]` | a CPU profile and a trace of a phone pan |

What they found, and the page's answers, are in `../README.md`, "Gestures".

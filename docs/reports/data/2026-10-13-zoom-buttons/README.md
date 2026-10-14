# − and + that keep their place (13 October 2026)

Request Q107 ([`02-requests.md`](../../../findings/02-requests.md)): the owner, with a screenshot of the chip diagram's
Up bar at "… › FinFET › Fin › Channel", the readout's text selected: "Make sure that the plus and minuses don't move.
For instance, I go there and I press - and it moves around." No card time: headless Chrome 155 on the owner's Intel Mac
(Core i9-9880H, macOS 26.6.2), driven through Playwright by [`pmz_probe.py`](pmz_probe.py), at 1× pixel density.

## What was measured

The probe serves a built page with `ladder-img/` beside it, opens it at each width (under 600 px as a touch phone), and
records the boxes of − and + and of the bar on every animation frame while it presses them; each press waits for the
camera to rest. Three paths:

- the chip diagram from `#at=die.metal` (the owner's address, the wiring stack): 6 × −, out past the rack to Studio 45,
  then 12 × +, back in to a multiply-add's compressor tree;
- the same address, 24 × + then 8 × −: down the wiring stack, the FinFET, its fin and channel, the crystal, an atom, its
  nucleus, a proton, a quark and the Planck length, round the loop to the top and in again to the street;
- the memory levels from their default view (the L1): 6 × +, down to the fin, then 8 × −, out to the chip.

"Moved" is the largest spread of either button's position over all the frames of a run; "at rest" the spread over the
moments just before each press, where a person presses again.

## Why they moved

The bar was the Up button, the crumbs, − and +, and the readout. The crumbs take all the width the others leave, so −
and + sat at the bar's right end minus the readout's width, and the readout changes about ten times a second while the
camera moves, in a larger type during a jump. Where its width at rest differs from scale to scale (900–1180 px wide,
where it has no minimum width), − and + also came to rest somewhere else after each press. Under 900 px wide the crumbs'
flex basis was their content's width, so a long trail took a row of its own and pushed − and + to a third.

## The fix

In `docs/reports/sources/ladder.css` and both pages' `body.html` (the ladder's README, "− and + keep their place"):
− and + come last, at the right end of the crumbs' row; the readout gives way last (the Up button and the crumbs shrink
a hundred times as readily); under 900 px wide the crumbs' row never wraps (the crumbs' basis 0, the readout at most
45%); on a phone the row above it keeps one height, a two-line label's, and the readout at most two lines of its own
size, a jump's too; − and + take no text selection and no double-tap zoom.

The first versions failed a check and were changed. With the readout unshrinkable, a quark's "< 4.3 × 10⁻¹⁹ m · no
size measured" at 900 px wide pushed − and + 37 px past the bar's end. With − and + beside the Up button under 900 px
(the readout beside the crumbs on a phone), a jump's larger readout grew that row 10 px for the length of the move, and
the phone's crumbs folded one level sooner, so `ml_ladder_test.mjs --phone` T0 failed ("… › Minion 0 › L1 cache" where
it wants "… › Shire 0 › Minion 0"). And held at a two-line label's height, the phone's first row came out 41 px, under
the 44 px the Up button had; it is now at least 44.

## The numbers

| Width | Chip diagram, before | after | after, deep path | Memory levels, before | after |
|---|---|---|---|---|---|
| 1920 | 60.2 px | 0 | 0 | 60.2 px | 0 |
| 1440 | 47.5 px | 0 | not run | 47.5 px | 0 |
| 1280 | 43.1 px | 0 | 0 | 43.1 px | 0 |
| 1100 | 52.7 px (32.6 at rest) | 0 | 0 | 38.5 px (19.8 at rest) | 0 |
| 1024 | 51.1 px (32.2 at rest) | 0 | 0 | 37.1 px (19.6 at rest) | 0 |
| 900 | 48.5 px (31.6 at rest) | 0 | 0 | 34.7 px across (19.2 at rest), 38 px down: the header (below) | 0 across, 38 px down: the header |
| 820 | 729.4 px (729.4 at rest); bar height ±34 | 0 | 0 | 31 px | 0 |
| 640 | 551.3 px (551.2 at rest); bar height ±34 | 0 | 0 | not run | 0 |
| 390 | 0 | 0 | 0 | 0 | 0 |
| 320 | 0 | 0 | 0 | not run | 0 |

Before, at 1280–1920 px wide, − and + slid 43–60 px during every move and came back; from 900 to 1100 they also came to
rest 20–33 px from where they had been, so the next press could land on the readout (as in the owner's screenshot, its
text selected); at 640 and 820 they jumped between the bar's second row and a third, up to 729 px across and 34 px down,
and at 640 five of the six presses of − found something else where − had first been. On a phone (390, 320) the old
layout did not move on these paths. After: 0 px everywhere, during the moves and at rest, and the bar's height never
changed. Widths from 900 up were measured on a build that differs from the final one only under 900 px, 600–899 on one
that differs only on a phone (its Up button was 41 px tall there, now at least 44); the phones on the final build.

The memory levels at 900 px wide: the whole stage moved 38 px down and back when the level changed, before the fix and
after. That is the page's header: its accesses row (`fitHead()` in the levels' script) still wraps beside the level tabs
at that width for some levels, even with short names, so the header's height changes. − and + no longer move across
there; the header is a fix of its own.

The suites' Up-bar tests, over http, on the final build and on the page of 2 October, the same on both:
`zoom_test.mjs --only=T3,T5,T11,T17` 114/114 on the desktop and on a phone, and
`ml_ladder_test.mjs --only=T0,T3,T5,T25 --chip=…` 53/53 and 40/40. `check_page.sh`: OK at 1280 and 390 px in light,
dark and the OS's dark, both pages. A local server needs a `favicon.ico`: without one, Chrome's request for it counts as
an error at load in both suites.

## Reproduce

```bash
D=$(mktemp -d); mkdir -p "$D/chip" "$D/mem"
python3 scripts/build-report.py chip-diagram docs/reports/data/2026-09-27-chip-diagram/facts.json "$D/chip/index.html"
python3 scripts/build-report.py memory-levels docs/reports/data/2026-09-28-memory-levels/facts.json "$D/mem/index.html"
cp -R docs/reports/ladder-img "$D/chip/"; cp -R docs/reports/ladder-img "$D/mem/"
P="uv run --with playwright python docs/reports/data/2026-10-13-zoom-buttons/pmz_probe.py"
$P "$D/chip" chip.json --vp 1920x1080,1280x800,1024x768,900x800,820x1180,390x844
$P "$D/chip" deep.json --seq p24,m8
$P "$D/mem" mem.json --hash '' --seq p6,m8
```

The page of 2 October (before) is `git show 8c1b73f1:docs/reports/2026-09-27-et-soc1-chip-diagram.html`, and the same
for the memory levels.

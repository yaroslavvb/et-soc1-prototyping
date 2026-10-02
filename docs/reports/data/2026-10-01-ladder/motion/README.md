# Motion check of the ladder's chip diagram (1 October 2026)

The chip diagram built on the shared ladder (branch `ladder`, the candidate `fin4`: the committed page differs from it only in the neighbourhood's fill on the city map and a test hook) against the page as of `bb0eb78`
(`base`), served over http from the work directory, recorded with `tools/pagemotion/drive.mjs` and the chip recorder,
one run at a time on aifoundry2, 1280 by 800 at DPR 1, at CPU 1x and under 4x CPU throttling. The scripts are the ones
used (`run.sh`, `all.sh`, `compare.py`; their paths are the work directory's); the recordings themselves (about 1 MB each)
stay in `~/claude/work/ladder/motion/`.

| Run | What it does |
|---|---|
| A, H, K, tour | flows 1, 8 and B and the guided tour, as in the page's earlier motion checks |
| up | Up from the silicon crystal (the base's deepest scale) to the top |
| dive | + from the top down to the silicon crystal |
| wrap | (the ladder's page only) Up from the Planck length to the top, round the ring, in again at the Planck length and up to the die: 62 presses |

`compare-fin4.txt` (frames during camera motion; late is over 25 ms):

| Run | base, 1x | ladder, 1x | base, 4x | ladder, 4x |
|---|---|---|---|---|
| A | 1 of 241 late, max 33 ms | 1 of 241, 33 ms | 29 of 212 (13.7%), 117 ms | 32 of 209 (15.3%), 117 ms |
| H | 0 of 206, 17 ms | 1 of 205, 33 ms | 24 of 182 (13.2%), 100 ms | 26 of 180 (14.4%), 133 ms |
| K | 1 of 429, 33 ms | 1 of 429, 33 ms | 75 of 353 (21.2%), 117 ms | 77 of 353 (21.8%), 117 ms |
| up | 5 of 1,640 (0.3%), 33 ms | 6 of 1,829 (0.3%), 50 ms | 124 of 1,511 (8.2%), 183 ms | 126 of 1,701 (7.4%), 217 ms |
| dive | 6 of 1,644 (0.4%), 33 ms | 11 of 1,812 (0.6%), 50 ms | 112 of 1,539 (7.3%), 250 ms | 140 of 1,674 (8.4%), 233 ms |
| wrap | - | 10 of 3,192 (0.3%), 50 ms | - | 227 of 2,938 (7.7%), 283 ms |

Every late frame at 1x is the first or second frame of a leg (the scale built and its image decoded, while the eased
speed is still near zero), as on the base page; the ladder's page has more legs (Bernal Heights and 29th Street above
the rack, and the scales below the die). `build-times.txt` (`btimes.mjs`, the page's `__chipTest.buildTimes`): every
new scale draws in 0.1 to 2.6 ms; the slowest scales are the die (7-10 ms) and the multiplier's tree (7-10 ms), both
older. The velocity profiles of the flows (`*-kink.txt`) match the base's at 1x; at 4x both pages drop frames alike.
No console errors in any run.

## After the owner's second update (1 October, about 10:30-11:30)

The candidate `u2d` (every cell's edge links, the loop through one atom, the textbook constructions) against the base
again (the `base-*` files are this rerun), with three more runs: `wrap` now Up from the atom where the ring lands, round
the ring and in again as the same atom, up to the die (52 presses); `vadd`, a vector add (Enter on the multiply-add's
adder, a carry cell, a transistor, the fin, the channel, the crystal and an atom, then Backspace out); `side`, shire 24
west to memory shire 0, south and north, and east back to shire 24 by the links. `vrun.sh` then measured the keyboard's
zooms on both pages (`vtree`: Enter from the multiply-add into its tree, a column, a 4:2, a full adder, an XOR and a
transistor, and back) and `vadd` again on `u2e`, the committed page, whose textbook parts zoom into one of their cells
rather than the whole row (on `u2d` a row's zoom was 1.4 times in 150 ms, a blink).

| Run | base, 1x | ladder, 1x | base, 4x | ladder, 4x |
|---|---|---|---|---|
| A | 1 of 241 late, max 33 ms | 1 of 241, 33 ms | 28 of 213 (13.1%), 117 ms | 32 of 209 (15.3%), 133 ms |
| H | 0 of 206, 17 ms | 0 of 206, 17 ms | 25 of 181 (13.8%), 133 ms | 30 of 176 (17.0%), 150 ms |
| K | 1 of 429, 33 ms | 1 of 429, 33 ms | 74 of 355 (20.8%), 117 ms | 74 of 353 (21.0%), 133 ms |
| up | 4 of 1,640, 34 ms | 5 of 1,832, 33 ms | 128 of 1,504 (8.5%), 200 ms | 122 of 1,706 (7.2%), 217 ms |
| dive | 5 of 1,644, 33 ms | 10 of 1,815, 67 ms | 109 of 1,545 (7.1%), 200 ms | 128 of 1,691 (7.6%), 267 ms |
| vtree (Enter) | 8 of 603 (1.3%), 67 ms | 9 of 600 (1.5%), 67 ms | 103 of 504 (20.4%), 267 ms | 110 of 495 (22.2%), 300 ms |
| wrap (the loop) | - | 5 of 2,626 (0.2%), 50 ms | - | 163 of 2,453 (6.6%), 233 ms |
| vadd (u2e) | - | 8 of 765 (1.0%), 50 ms | - | 110 of 660 (16.7%), 300 ms |
| side | - | 1 of 134, 33 ms | - | 14 of 121 (11.6%), 183 ms |

The flows' velocity kinks are the base's at 1x (at most 12.2% of peak on both; `*-kink.txt`); at 4x both pages drop
frames alike. As before, each late frame at 1x is the first frame of a move, where the eased speed is still zero: for a
move started by a key it is the key's own handler (the panel, the breadcrumb and the next scale drawn, 50-70 ms of
layout), on the base page as on this one (`vtree`). No console errors in any run.

`build-times-u2e.txt`: the new scales (the textbook constructions and the cells' links) each draw in 1 to 5 ms, with 38
to 183 nodes; the deepest path, from the top to the Planck length, keeps 5,629 nodes in the drawing (budget 6,000).

## Part 1b: the last dead ends (1 October, afternoon)

The candidate `p1b6` (nine more scenes: a PCIe lane, a differential pair, a crossbar, rounding, copper wiring, a copper
atom, a buck converter, a power transistor and a boot pin; the fins drawn over the contacts) against `9318844`, the
commit before it (`base`; the build of that commit), with `run1b.sh`: the flows A, H and K and the vector add as above,
and three new paths by Enter on a part and Backspace back out: `lane` (a PCIe lane, its CTLE, the input pair, the fin,
the channel, the crystal and an atom), `reg` (the card's core regulator, a buck converter, its power transistor, the
crystal, an atom) and `wire` (the wiring stack, a copper wire, a copper atom, an electron). One run of each, one at a
time; `p1b-*-summ.txt` and `p1b-*-kink.txt`.

| Run | base, 1x | part 1b, 1x | base, 4x | part 1b, 4x |
|---|---|---|---|---|
| A | 1 of 241 late, max 33 ms | 1 of 241, 33 ms | 23 of 219 (10.5%), 117 ms | 29 of 212 (13.7%), 117 ms |
| H | 0 of 206, 17 ms | 0 of 206, 17 ms | 31 of 175 (17.7%), 167 ms | 28 of 178 (15.7%), 167 ms |
| K | 1 of 429, 33 ms | 1 of 429, 33 ms | 76 of 351 (21.7%), 117 ms | 84 of 345 (24.3%), 117 ms |
| vadd | 8 of 766 (1.0%), 67 ms | 11 of 764 (1.4%), 67 ms | 112 of 660 (17.0%), 300 ms | 110 of 661 (16.6%), 283 ms |
| lane | - | 5 of 741 (0.7%), 33 ms | - | 65 of 677 (9.6%), 283 ms |
| reg | - | 0 of 506, 17 ms | - | 17 of 487 (3.5%), 483 ms |
| wire | - | 1 of 279, 33 ms | - | 19 of 261 (7.3%), 200 ms |

The flows' velocity profiles are the base's (the largest frame-to-frame change at most 12.1% of peak at 1x, the base's
13.8%), and the vector add's matches the base move for move; at 4x both pages drop
frames alike, run to run. The new paths' late frames at 1x are first frames of a move; at 4x the 483 ms frame of `reg`
is the page's first, the card's photo decoded on arrival, before any move. The new scales draw in 1-3 ms each
(`build-times-p1b.txt`, three times each). No console errors in any run.

## Part 2: the memory levels (1 October, evening)

The memory levels on the shared ladder (`p2m`: the final build but for the hand-over's start, below) against the
committed pages of `65a06da` (`base`), served over http from the work directory, one run at a time on aifoundry2
(16:35-17:01, no other tests running), 1280 by 800 at DPR 1, at CPU 1x and under 4x CPU throttling, with `all-p2.sh`
(`run-p2.sh` for the memory levels, `runchip-p2.sh` for the chip diagram); `p2-*-summ.txt`, `p2-*-kink.txt`, and
`p2-compare.txt` from `compare-p2.py`.

| Run | What it does |
|---|---|
| load | the access `#dram/load`, the levels' own camera following it (the check of 30 September) |
| tabs | the level keys 5, 2, 1, 3, 4 and 1: the cross-fades between the maps, the moves out and in between levels |
| out | (the new page only) Up five times from the L3's map: the package (the path camera takes the stage), the card, the host, the rack and "?"; then + five times back in, to the map (the levels' camera takes it back) |
| in | (the new page only) + five times from the L2's 6T cell (the path camera takes the stage): the transistor, the fin, the channel, the crystal, an atom; then Up five times back to the cell |
| A, H, K | the chip diagram's flows, as in part 1 (its page changed only in where its CSS sits, and draws the same to the pixel; the tour run records no camera frames on either page, as in part 1) |

Frames during camera motion (late: over 25 ms; kink: the largest frame-to-frame change of the camera's velocity, as a
share of the move's top speed):

| Run | base, 1x | part 2, 1x | base, 4x | part 2, 4x |
|---|---|---|---|---|
| load | 0 of 625 late, kink 10.7% | 0 of 625, 11.0% | 136 of 486 (28.0%) | 139 of 484 (28.7%) |
| tabs | 0 of 445 | 0 of 447 | 34 of 408 (8.3%) | 40 of 402 (10.0%) |
| out | - | 1 of 354, 58.3% | - | 18 of 340 (5.3%) |
| in | - | 1 of 467, 37.5% | - | 19 of 448 (4.2%) |
| A | 1 of 241, 11.9% | 1 of 241, 11.9% | 25 of 217 (11.5%) | 25 of 217 (11.5%) |
| H | 0 of 206, 12.4% | 0 of 206, 12.2% | 26 of 180 (14.4%) | 21 of 184 (11.4%) |
| K | 1 of 429, 12.4% | 1 of 429, 12.1% | 77 of 354 (21.8%) | 78 of 351 (22.2%) |

The levels' own camera moves as before: the access and the level moves have the same frames and the same kinks at 1x,
and at 4x both pages drop frames alike. The chip diagram's flows are the base's frame for frame. The new flows' one late
frame at 1x, and their largest kinks, were the hand-over's: the path camera's take-over of the stage (its drawing of the
same picture, 4-21 ms, `take.mjs`) and its move's first frame fell in one frame, so that the move
began with a jump, 58% (out) and 37% (in) of its top speed in one frame, where the chip's own Up from the die eases in
from 0.3 px a frame. The final build (`p2n`) gives the take-over two frames of its own, the same picture, before its
move: its out and in flows at 1x have no late frame, and their first moves' kinks are 15.7% and 10.3%; the largest left,
22.8%, is the path camera's own move from the package to the card, as on the chip (`p2-oi-p2n-c1-*`, `outin-p2.sh`). The
final build's full runs (`mlp2n`, 17:01-17:10) are not shown: two other sessions' tests were running on the machine by
then, and its load flow at 4x dropped 35% of its frames against the 28-29% of both quiet runs.

First load (`firstload.mjs`: a phone profile, 390 by 844 at DPR 3, CPU 4x, five interleaved runs of each page, a fresh
profile each, medians; `p2-firstload-*.txt`): the memory levels' first paint 236 → 252 ms (+7%), DOMContentLoaded 1,000 →
1,133 ms (+13%); the chip diagram's +6% and +0.6%. The memory levels' page carries 0.73 MB more (the ladder's code and
its scales, maps and facts); the ladder's own start-up takes 30-45 ms of the difference at 4x (`p2-loadtm.txt`, a build
with markers), the parse of the larger script the rest. The design's gate (±10%) is met by the first paint and missed by
DOMContentLoaded, by 3 points.

## The final check (2 October)

The commit `11b6e45` (`head`) and the final check's build (`fix`: the chip diagram with the address writer's fix, the
ladder README's "The final check"; the memory levels as in `head`) against the pages of `bb0eb78` (`bb0`), served over
http from the work directory, one run at a time on aifoundry2 with nothing else running, 1280 by 800 at DPR 1, a warm
profile per version; at 1x one run of each (the access four times), at 4x two (bb0, head, head, bb0; then fix, fix).
`final-run.sh` (both pages; on `head` also the chip's loop and the memory levels' out and in) and `final-runchip.sh` (the
chip's runs on `fix`), `final-compare.py`, `final-compare-c1.txt` and `final-compare-c4.txt`; the recordings stay in
`~/claude/work/ladder/final/motion/`. Late frames (over 25 ms) of the frames in motion:

| Run | bb0, 1x | head, 1x | fix, 1x | bb0, 4x | head, 4x | fix, 4x |
|---|---|---|---|---|---|---|
| A (flow 1) | 1 of 241 | 1 of 241 | 1 of 241 | 14.3, 13.7% | 5.2, 7.1% | 7.1, 8.6% |
| H (flow 8) | 0 of 206 | 0 of 206 | 0 of 206 | 10.8, 12.0% | 6.7, 6.7% | 6.7, 9.0% |
| K (flow B) | 1 of 429 | 1 of 429 | 1 of 429 | 20.2, 22.0% | 13.2, 12.6% | 11.4, 12.6% |
| up (36 presses, the crystal to the top) | 5 of 1,638 | 5 of 1,824 | 6 of 1,819 | 7.8, 8.2% | 8.4, 8.1% | 7.3, 7.8% |
| dive (+ 36 times, the top to the crystal) | 7 of 1,642 | 10 of 1,810 | 9 of 1,815 | 7.0, 6.7% | 8.2, 8.3% | 8.3, 8.2% |
| loop (Up 5 times from the top) | - | 3 of 328 | 0 of 331 | - | 18.1, 18.6% (longest 350-367 ms) | 1.2, 1.8% (longest 67-133 ms) |
| the access `#dram/load` | 0 of 625 (4 runs) | 1 of 624, then 0 of 625 (3 runs) | as head | 28.6, 25.7% | 30.2, 30.5% | as head |
| the level tabs | 0 of 444 | 0 of 444 | as head | 7.3, 7.5% | 8.9, 9.2% | as head |
| out (Up 5 from the L3's map, + 5 back) | - | 0 of 357 | as head | - | 5.3, 5.3% | as head |
| in (+ 5 from the L2's cell, Up 5 back) | - | 0 of 472 | as head | - | 5.7, 5.2% | as head |

At 1x the shared runs are the base's (every late frame in the chip's runs is the first or second frame of a move, as on
the base; the access's one late frame of its first run, mid-move with no long task, did not come back in three more
runs), and the access's velocity kinks are the base's (at most 11.1% of peak on the base, 11.2% on head). At 4x the
chip's flows drop fewer frames than the base's, Up the same, the dive one or two points more (its path has more legs:
Bernal Heights, 29th Street); the memory levels' access two to five points more and the tabs about 1.5 (the page carries
the ladder's second SVG and code). The loop's run on `head` lost a third of a second at the Planck length: the address
writer's long task (the ladder README, "The final check"); on `fix` it does not.

First load (`final-firstload-*.txt`: the fixer's `firstload.mjs`, a phone profile, 390 by 844 at DPR 3, CPU 4x, six
interleaved runs, a fresh profile each, medians): the chip diagram's first paint 248 → 260 ms (+4.8%), DOMContentLoaded
562 → 630 ms (+12.1%); the memory levels' first paint 228 → 228 ms (0%), DOMContentLoaded 1,002 → 1,141 ms (+13.9%).
The design's gate (the first frame within ±10%) is met by the first paint on both pages; DOMContentLoaded misses it, as
the part 2 and fix rounds found (the larger scripts' parse).

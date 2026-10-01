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

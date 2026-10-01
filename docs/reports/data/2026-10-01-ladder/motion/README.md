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

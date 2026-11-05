# Dated note 2 beside README.md, Wed 4 Nov 2026 (week 45), about 19:4x PST: what E164-U1's FAIL is made of, and a session scale from the random anchors (both post hoc; the card half's records)

*This note sits beside [`README.md`](README.md), not inside it: the README stays as committed in `5eecc457` (17:28:54 PST), and so
does the first dated note, [`README.md.dated-note.md`](README.md.dated-note.md) (`708a0a04`, 18:28:49 PST). It records two readings
the card half's critic made from the committed rows after that note, and the script that reproduces them,
[`posthoc_card_term_anchors.py`](posthoc_card_term_anchors.py), with its output,
[`posthoc-card-term-anchors.txt`](posthoc-card-term-anchors.txt). **Both readings are post hoc: no rule was registered for either,
and neither changes a verdict.** Desk only: no number, band, prediction, rule or frozen file changes, and no device command is
involved. It answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, and the Q139 critic's ranks 1
and 4.*

## 1. E164-U1's FAIL is M6's float card term, not M6's form

**What is registered.** E164-U1 reads M9 − M6 on the 12 kinds aimed at none of the named classes as **+0.078 W, FAIL** (M9 resolved
worse), and M1 NOT RESOLVED (−0.048 W [−0.111, +0.013]) ([`scored.json`](scored.json) › `verdicts`; the README § Results).

**What it is made of (post hoc).** M6's and M7's frozen card-1 predictions carry a float card term of 0.9711 of aifoundry3's
switching; M9 carries M8's, 0.9616. On aifoundry3 every model's card term is 1, so for each priority-1 tile scored on both cards the ratio
(M6 / M9 on card 1) / (M6 / M9 on aifoundry3) isolates the two card terms' ratio on card 1:

| family | tiles | M6's card term over M9's, isolated per tile |
|---|---|---|
| floats | 26 | **1.0099** on every tile (0.9711 / 0.9616) |
| int8 | 22 | 1.0123–1.0124 |

X1 reads card 1's float switching as **0.9621** of aifoundry3's, M9's own term, not M6's. Both 600 MHz sessions read above M9 on the
floats (E163-B1 +0.151 W, E164-B1 +0.164 W). M6's term, 1% higher, absorbs that shared excess on card 1:

| card 1, the floats | M9 as frozen | M9 × 1.0099 | M6 |
|---|---|---|---|
| all 26 priority-1 float kinds, rms / bias (W) | 0.321 / +0.164 | 0.279 / +0.004 | 0.279 / +0.074 |
| the 8 float kinds aimed at nothing (U), rms / bias (W) | 0.171 / +0.146 | **0.077** / −0.049 | **0.081** / −0.002 |

On int8 the same scaling makes M9 worse (0.200 → 0.236 W rms), as X2's 0.9418 says it should.

**So U1 reads:** *"B1 on the unaimed kinds: M6's 1% higher float card term absorbs the float excess both 600 MHz sessions show (post
hoc)"*, never "M6 models unaimed kinds better". The verdict stands as registered: U1 FAIL, M1 NOT RESOLVED, E164-RANK1 FAIL.

## 2. A session scale per family, read from the session's own random anchors (a candidate term, not a result)

Pool 7 carries two random anchors per format (priority 2, never scored). Rank 4's registered rule reads a card's scale from them
against aifoundry3's (RK4 PASS on both families, `rank4-e163-e164.txt`). Read instead against M9 inside each session, per family (the
median over the family's random anchors of measured D / M9's D, the zeros anchors left out), and applied to every priority-1 tile:

| session | the floats' scale | float bias as frozen → scaled (W) | int8's scale | int8 bias as frozen → scaled (W) | rms over 48, as frozen → scaled (W) |
|---|---|---|---|---|---|
| E163, aifoundry3 | 1.0082 | +0.151 → **+0.013** | 1.0025 | +0.051 → +0.036 | 0.278 → 0.259 |
| E164, card 1 | 1.0095 | +0.164 → **+0.010** | 0.9766 | −0.076 → +0.061 | 0.273 → 0.245 |

On the floats the session's own anchors take up the excess on both cards; on card 1 int8's anchors over-correct. Without class S
(the single high B bits) the scaled rms is 0.175 W (aifoundry3) and 0.170 W (card 1) over 41 kinds. **This is a candidate term for
the next model's registration, not a result:** it was chosen after the data, on the data, and is scored on the same rows. The
registered test of whether the excess is a level or a gain, and whether it belongs to the day, the session or the card, has not
been run.

## How to reproduce

From the repository root, standard library only, reading the two committed `scored.json` files:

    python3 -I -B docs/reports/data/2026-11-04-e164-blind7-card1/posthoc_card_term_anchors.py \
        docs/reports/data/2026-11-04-e163-blind7-aifoundry3/scored.json \
        docs/reports/data/2026-11-04-e164-blind7-card1/scored.json

Its output, [`posthoc-card-term-anchors.txt`](posthoc-card-term-anchors.txt), matches the critic's own figures digit for digit (its
checks ran at the desk on the same files). No file in this directory was edited or re-made.

SPDX-License-Identifier: Apache-2.0

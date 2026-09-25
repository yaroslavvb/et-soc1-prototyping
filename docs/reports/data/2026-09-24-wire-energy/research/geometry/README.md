# Die geometry: the tile pitch in millimetres

`measure.py` finds the die frame and the blue shire-outline grid lines on a die plot; `pitch.py` turns the grid-line
positions into a tile pitch in pixels and scales it to the published 570 mm² under three readings of what the area
covers (`pitch.json`, `scale_from_570mm2` A, B and C). The images are not re-hosted; `../README.md` says where they are.

The die boxes in `pitch.py` (the `plots` table: left, top, right and the two bottom readings) are read by hand:
`measure.py`'s bottom-edge detection fails on two of the three images (micro22 and hc33), so the bottom edges in
particular are manual readings.

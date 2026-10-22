# E62 post-hoc analysis (chosen after the data were seen; never the registered test)

The registered statistics are `../analyze_hm.py`'s. These scripts were written on the evening of the run, after the
camera's shutter (FFC) behaviour was seen: it fires every 8–10 s under load and some events move pixels by up to 10 K,
so a few per cent left over after `reduce_hm.py`'s per-pixel bridging is still 100+ mK of pattern. Every number they
produce is labelled **post hoc** on the page and in `docs/findings/03-experiments.md` (E62).

| Script | What |
|---|---|
| `jumps.py` | shared shutter geometry: events under 2.5 s apart merged into one cluster (two events 1.1 s apart had left each other no fit window, so their jump survived), straight-line fit windows that skip shutter-flagged and frozen-thinned bins |
| `dejump_frames.py RED REDc` | per pixel: each cluster's residual step (two lines, before and after, evaluated at its middle), smoothed (sigma 2 binned px) and removed from every later bin; feeds the movies |
| `projection2.py RED1 ANA1 RED2 ANA2 out.json trace.png` | every frame projected onto templates from the OTHER session (session 2's blocks on session 1's E62-ORBIT corner maps; E62-ORBIT on session 2's W12−E12 and N12−S12 maps), 1-D shutter jumps removed, per-lap half-patch contrasts; the page's headline numbers for the two-arm blocks, E62-ORBIT's compass and E62-SWEEP's ramp |
| `make_bloom_cycle.py RED ANA ANAout` | E62-BLOOM as a cycle: the three on/off cycles averaged, each against the 10 s before its own load step (the renderer's own bloom path drew one 396 s on-phase and accumulated shutter residue) |
| `cal_ladder.py RED out.json` | E62-CAL's power ladder: the median of the 10 Hz board samples in the last 4 s of each rung, and the camera session gate |
| `trace.py ANA1 RED2 out.png` | the diagnostic plot that showed the shutter steps |
| `render_titles.py in.json out.json` | protocol copies with plain block titles for the movie frames (the registered titles stay in `../prereg/`) |

The order the page's numbers and movies were made in (each with `uv run -q --with numpy --with scipy --with matplotlib
--with pillow python3`; RED1/RED2 are `reduce_hm.py`'s outputs for `build/e62/runs/e62-card-1021` and `…-1021b` on
aifoundry2):

```bash
python3 posthoc/dejump_frames.py RED1 RED1c ; python3 posthoc/dejump_frames.py RED2 RED2c
python3 analyze_hm.py RED1c --protocol RED1c/protocol.json --out ANA1f
python3 analyze_hm.py RED2c --protocol RED2c/protocol.json --out ANA2f
python3 posthoc/make_bloom_cycle.py RED2c ANA2f ANA2b
python3 posthoc/projection2.py RED1 ANA1f RED2 ANA2f projection2.json trace2.png
python3 posthoc/cal_ladder.py RED1 cal_ladder.json
# movies: render_hm.py ... --die-view camera --min-mk 400 --pct 0 (the bloom: --bloom-block NONE --min-mk 8000 --pct 0)
```

The outputs that are committed are in `docs/reports/data/2026-10-21-e62-heat-movies/`.

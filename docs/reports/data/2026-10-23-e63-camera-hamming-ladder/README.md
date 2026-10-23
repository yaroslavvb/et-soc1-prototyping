# E63 data: the camera half of the Hamming ladder (Q122, Fri 23 Oct 2026, aifoundry2)

Two card sessions of [`tools/claims-v3/hlc`](../../../../tools/claims-v3/hlc/README.md): session 1 (`s1/`, 12:55–13:27
PDT, `protocol.json`, 8 minions in each of the 32 shires) and session 2 (`s2/`, 13:27–14:00 PDT, `protocol-A1.json`,
6 minions per shire, run under amendment A1 after session 1's hold gate failed). The raw frames (about 2.1 GB a session,
the camera's lossless stream with the host's receive time on every frame) stay on aifoundry2 in
`build/e63/runs/e63-card-1023` and `e63-card-1023b`, gitignored, as E62's did.

| Path | What |
|---|---|
| `s*/session/` | the runner's record: `session.json` (protocol and code hashes, operand hashes, git head, stop reason), `protocol.json`, `launches.jsonl` (every launch, its operand file and its timing), `phases.jsonl` (each phase's planned and realised span: the lock-in's laps), `blocks.jsonl`, `marks.jsonl`, `run.log`, the telemetry `tel.jsonl.gz` (10 Hz: board power, rails, clock, 34 shire sensors), and the recorder's `done.json` and `gaps.jsonl` |
| `s*/red/` | from `reduce_hm.py` (E62's, unchanged): `ffc.json` (every shutter event it found), `meta.json`, `scene.npy` (the idle scene, 192 × 256 °C); and `fpa.npz` from `fpa_trace.py` (per frame: the focal-plane thermistor VTEMP and the header's `fpa_c`) |
| `s*/analysis/` | the registered lock-in, `lockin_hlc.py`: `lockin.json` (every block's ROI, frame and power amplitudes, per lap, the transfers, the hold gate, the shutter-phase test, the decision rules) and `E63-*-maps.npz` (per pixel, 96 × 128: the complex amplitude at 0.05 Hz and its SEs, the in-phase map, the ROI) |
| `s*/summary.json`, `s*/dips.json`, `s*/fpa_scene.json` | reported beside the registered numbers with no verdict: `summary_hlc.py` (prices per flipped bit, the camera per watt and per flip rate, the plain lock-in on bridged frames), `dips_hlc.py` (the one-second clock dips inside launches), `fpa_scene.py` (the header's `fpa_c` is the scene's mean, not the focal plane) |
| `s1/figures.json` | the page's folded cycles and map statistics (`figures_hlc.py`) |
| `tiles/` | the pre-session operand check (`tile_check.sh`): each launch's record with `--dump-tiles`, compared byte for byte with E60's files |

Rebuild everything from a RUNDIR (on aifoundry2, from `build/e63/code/`, or on any machine with numpy):

```bash
python3 reduce_hm.py <RUNDIR> --out <RED>
python3 fpa_trace.py <RUNDIR> --out <RED>/fpa.npz
python3 lockin_hlc.py <RED> --protocol protocol.json --template prereg/e62_bloom_dt.npy \
    --scene-ref prereg/e62_scene.npy --fpa <RED>/fpa.npz --out <ANA>      # session 2: protocol-A1.json
python3 summary_hlc.py <RED> <ANA> --out summary.json
python3 dips_hlc.py <RED> --out dips.json
python3 fpa_scene.py <RED> --out fpa_scene.json
```

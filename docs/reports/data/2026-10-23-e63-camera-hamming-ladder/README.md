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
| `s1/figures.json`, `dips.json` | the page's folded cycles and map statistics (`figures_hlc.py`); both sessions' dips in one file (`dips_hlc.py s1/RED s2/RED`), as the page's text reads them |
| `s*/posthoc/h3-rails.json`, `posthoc/h3-rails-pooled.json` | **post hoc, Mon 26 Oct 2026 (Q126), no verdict**: the drive's third harmonic read out of the registered fit as a second transfer point at 0.15 Hz, and the card's minion, SRAM and NoC rails demodulated beside the board ([`tools/claims-v3/hlc/posthoc/`](../../../../tools/claims-v3/hlc/posthoc/README.md)) |
| `tiles/` | the pre-session operand check (`tile_check.sh`): each launch's record with `--dump-tiles`, compared byte for byte with E60's files |

**The prices per flipped bit were corrected on Mon 26 Oct 2026 (Q126).** `summary_hlc.py` hard-coded 256 minions
and 800 MHz. Session 2 ran amendment A1's 6 minions per shire, 192 in all, so its three prices were three quarters
of the truth: **113.8 → 151.7 fJ** (top rung), **114.3 → 152.4** (the top rung again) and **90.2 → 120.3** (the
middle rung), with the camera per 10¹³ flips a second rising the same way (33.59 → 44.79, 29.38 → 39.17, 29.52 →
39.36 mK). Session 1's prices are unchanged. The script now reads both numbers from the session's own records: the
minions from `launches.jsonl`'s `harts`, the clock as the median minion MHz over the same steady windows the board
step's medians are taken in. That record's own `mhz_minion` field is read before a launch opens and says 600 in all
360 records of both sessions, while 99.6% of the in-launch telemetry samples are at 800 — so the telemetry is what
the clock is read from, and the median over the steady windows is 800 MHz in all eight blocks (the mean is 797.4 to
800.0, the one-second dips pulling it down; both are recorded per block in `summary.json`'s `clock`).

**Session 1's reduced cube was rebuilt on aifoundry2 on 26 October.** Session 1's RED was made on the Intel while
session 2 was still running and was not kept; only session 2's was on the host. The rebuild, same code and same raw
capture, reads the same 48,005 packets, 25.001 fps and 3,841 bins, but finds 244 shutter events against the committed
`s1/red/ffc.json`'s 243 — one borderline step crossing the 40 mK detection threshold the other way on a different
machine's numpy,
so session 1's re-run `summary.json` and its post-hoc numbers come from a reduction one event apart from the registered
one. What moved: nothing in `lockin.json` (not re-run), session 1's top rung's plain bridged lock-in 192.507 → 192.507 mK,
and its null's 13.4 → 14.2 mK against an SE of 47. Session 2's RED is the original and reproduces to the last digit.

Rebuild everything from a RUNDIR (on aifoundry2, from `build/e63/code/`, or on any machine with numpy):

```bash
python3 reduce_hm.py <RUNDIR> --out <RED>
python3 fpa_trace.py <RUNDIR> --out <RED>/fpa.npz
python3 lockin_hlc.py <RED> --protocol protocol.json --template prereg/e62_bloom_dt.npy \
    --scene-ref prereg/e62_scene.npy --fpa <RED>/fpa.npz --out <ANA>      # session 2: protocol-A1.json
python3 summary_hlc.py <RED> <ANA> --out summary.json
python3 dips_hlc.py <RED> --out dips.json
python3 fpa_scene.py <RED> --out fpa_scene.json
python3 posthoc/h3_rails_hlc.py <RED> --protocol protocol.json \
    --template prereg/e62_bloom_dt.npy --scene-ref prereg/e62_scene.npy --out posthoc/h3-rails.json
python3 posthoc/pool_h3.py s1/posthoc/h3-rails.json s2/posthoc/h3-rails.json --out posthoc/h3-rails-pooled.json
```

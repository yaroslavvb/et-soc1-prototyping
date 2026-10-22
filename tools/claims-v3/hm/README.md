# V3-HM: heat movies (E62, Q121)

Film how heat on the back of aifoundry2's card moves when compute is scheduled on chosen shires, with the Thermal
Master P3 that has watched that card since 16 Oct 2026 (its live page:
<https://spacesheep.dev/@yaroslavvb/thermal-master-p3-live-camera-stream>). The owner's ask, Wed 21 Oct 2026: *"design
a set of spatial heating experiments … videos of heat spreading in various patterns depending on how the compute is
scheduled … maybe like corners or the center … Use the live stream to make this possible."*

**The rule every movie follows.** The board spreads heat 29–49 mm sideways before it reaches the camera, more than the
22 × 26 mm die, so any pattern arrives as one blob and a pattern-against-idle movie only shows brightness. Every spatial
movie here is therefore a **constant-total-power swap**: equal-hart sets (same shire count × `--per-shire`) cycled
several laps, shown as a phase-averaged **difference** image. The one exception is the bloom (all 32 shires against
idle), which shows what a change in total power looks like and supplies the gain map.

## Pre-registration

`prereg/protocol.json` (sha256 `c227da785f79b54e…`) is the plan the runner executed; `prereg/PROTOCOL.md` explains
every set, block, dwell, order and prediction; `prereg/validate_protocol.py` re-derives every mask from
`hp/placements.py`'s die map and checks hart balance, sign orders, the die-temperature model and the time budget
(`prereg/validate.out`). Both were frozen at 16:58 PDT on Wed 21 Oct 2026, when they were staged on aifoundry2 with
these hashes, before the session's first launch at 17:09; this commit records them after the fact, so the hashes in
the session's own `session.json` are the proof of order. `protocol.json` is committed byte for byte. `PROTOCOL.md`,
`validate_protocol.py` and `validate.out` had their authoring machine's local paths rewritten to repo-relative ones
and nothing else; their sha256 as frozen were `bf2fed63e99a6305…`, `b4ed244cb2142c59…` and `66ba0e6bd52f0eff…`.
One stated detail did not happen as written: raw frames went to `build/e62/runs/<session>/cam/` on aifoundry2
(gitignored), not to the `~/drive.unsynced/e62/` path the protocol names, and the heater's stop file was
`<RUNDIR>/STOP`.

## Files

| File | Runs on | What |
|---|---|---|
| `p3rec.py` | both | decoder: `.p3rec` recordings and raw `/stream.raw.z` captures → headers, InfoLines, 256×192 uint16 planes (1/64 K); shutter (FFC) events |
| `record_cam.py` | aifoundry2 | the recorder: `/stream.raw.z` from the camera phone to `cam.p3rec` with the host's receive time per frame; reconnects, logs gaps, only GET `/health` and `/stream.raw.z` |
| `run_hm.py` | aifoundry2 | the runner: executes `protocol.json` on the card (or `--dry`, with no device access at all) |
| `reduce_hm.py` | aifoundry2 or Intel | RUNDIR → RED: decode, bridge shutter steps, 2×2 bin, 0.5 s bins on the host clock |
| `analyze_hm.py` | Intel | RED → ANA: per-block phase-averaged cycles, steady-state difference maps, lobe and dipole statistics, permutation nulls, orientation |
| `render_hm.py` | Intel | ANA → MOV: 768×960 phone-portrait movies (camera panel, die map, schedule strip), posters, stills |
| `synth_hm.py`, `test_hm.py` | Intel | a synthetic session with planted blobs, drift and shutter steps; the end-to-end recovery and null tests |

## Running it (from `build/e62/code/` on aifoundry2, a gitignored copy of this directory)

```bash
python3 run_hm.py --protocol protocol.json --list                 # the plan and its estimate; touches nothing
python3 run_hm.py --protocol protocol.json --out ../runs/<dir> --dry   # no lock, no heater, no ettelem; the camera still records
bash start_e62.sh ../runs/<dir>                                    # the card session, detached (setsid nohup)
```

The runner keeps the lab framework's etiquette (`lib.sh`, `hp/hplib.sh`): `flock -n` on
`/run/lock/etsoc-shire0.lock` for the session, other-user and foreign-process checks before the session and between
every launch (another user ends the session, exit 3), every heater under `timeout 10` with `--seconds 8 --budget 9.5`
and an explicit `--kernel` and `--stop-file`, one `ettelem sample --every-ms 100 --reset-ms 1000` for the session, a
watcher that stops the heat at 85 °C or 95 W (two consecutive samples) or when telemetry goes stale, no SIGKILL of a
device process, a 64 °C per-launch gate on full-card phases, and a bounded cool-down gate between blocks. A phase is a
launch **count**, and each block's laps run in the order its `lap_phase_orders` lists.

Then, on the Intel: `reduce_hm.py <RUNDIR> --out <RED>`, `analyze_hm.py <RED> --protocol protocol.json --out <ANA>`,
`render_hm.py <ANA> --red <RED> --protocol protocol.json --out <MOV>` (each with `uv run -q --with numpy
[--with matplotlib --with pillow] python3`). Raw frames (~1 MB/s) stay in `build/e62/runs/` on the box, uncommitted.

## The camera's settings were not changed

The live preset (`visualize`: 62.5 mK steps, temporal and spatial filters, automatic shutter) was left as it was, so
the public live page stayed the same during the session. Everything is computed in raw counts, shutter steps are
detected and bridged in software, and no absolute temperature is claimed.

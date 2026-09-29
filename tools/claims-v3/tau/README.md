# TAU: the rails' 1 s filter, measured and undone (the observability ladder's rung 4)

The three rail powers ettelem reports (`sp.minion_w`, `sram_w`, `noc_w`) are the PMIC's running average of each
regulator's output, so a square burst reads as a slow exponential, and the published rail split reads a burst's last
0.6 s and divides by 0.94 ([19-observability-and-the-unmetered.md](../../../docs/findings/19-observability-and-the-unmetered.md)).
`tools/ettelem/deconv.py` undoes the filter. This experiment measures the filter offline on committed data, chooses
the regularisation, and pins the filter per rail on each card with one short block of step bursts.
The predictions are in [PREREG.md](PREREG.md) (machine-readable: `prereg.json`; the bands calibrated on simulated
replicates: `calib.json`).

## Files

| File | What it is |
|---|---|
| `../../ettelem/deconv.py` | the deconvolver (numpy only): pass grid (each sampler segment with its own interval), one-pass lag, exact inverse, zero-phase Gaussian, Tikhonov and TV solvers, per-card tau; the CLI deconvolves each segment on its own and refuses `--reset-ms` streams; `--selftest` |
| `taulib.py` | shared fits (every burst at once, per-burst linear terms, shared tau and delay by grid search), square-recovery measures, board_w's in-burst drift |
| `offline.py` → `offline.json` | the offline check on the 23 September catalogue and enercat data and the version-3 full catalogue (three cards, 5,956 bursts); `--drift` prints board_w's in-burst drift (P4d) |
| `block.sh`, `tau.json` | one pass of step bursts on the local card (below) |
| `reduce.py` | the block's helper (`env`, `wincheck`, `winrec`), the pass check (`check-pass`) and the pre-registered decision code (`report`: items, bands, per-theory verdicts) |
| `prereg.json`, `PREREG.md` | the predictions, the prior and calibrated bands; the theories and decision rules |
| `calibrate.py` → `calib.json` | the bands' calibration on simulated replicates: noise matched to the offline residuals, false-fail rates of the true theories and the power against the rival |
| `stubs/` | dry-run stand-ins for ettelem, enercat_host and et-who (a simulated card with the offline filters, extra delays, noise and board_w's creep, on a virtual clock, with fault injection and the rival "fixed delay" theory), and `simulate.py`, the same card without a clock, for calibration |

## The block

`bash tools/claims-v3/tau/block.sh <pass> [--smoke]` from the tree's root (`V3_DEVICE=1` on aifoundry1).
Passes 1-99 are development passes and run on aifoundry1's card 1 only; 101-199 are validation passes, aifoundry3
only, and refuse to start (a smoke too) unless `LOCK.sha256` and `PREREG.sha256` check; 201-299 run on aifoundry2
only with `TAU_A2_OK=1` (after DV2 ends) and are frozen the same way. aifoundry1's card 0 is refused. Queue lines are
`tau <pass>` (queue.sh unchanged).

A full pass is 13 sampler windows (tau.json `full`): an idle window, then twelve bursts in a seeded order per pass
(`shuffle_seed` + pass, written to `run.log` and `block.json`), eight under the usual 10 Hz sampler (M 2, 3 and 4 s,
D 2, 3, 3 and 4 s, H 3 s) and four under a 20 Hz sampler (M 3, D 3, twice each). M is `fmadd.ps` random on 2 harts
(about 20 W on the minion rail), H the same on zeros (about 10 W: does tau depend on the step?), D the catalogue's
`dramrow/stride8K/random` (about 8 W on each of the SRAM and NoC rails). Each window is one `timeout 10 ettelem sample
--seconds 9 --every-ms <100|50>`; its burst is one `timeout 10 enercat_host <args> --seconds <2-4> --window 240000000
--budget 8` (`build/enercat`, the build with E49's g3log fix; the block checks the fix, the flags and the kernel ELF
compiled into it before it starts, and records the binaries' and the kernel's `.text` hashes), launched 1.5 s after the
sampler's first line (enercat's device setup adds about 0.7 s). enercat launches 0.4 s windows while less than
`--seconds` has passed, so the bursts are 2.0, 3.2 and 4.0 s long. Each window holds about 2 s of idle before the
kernel and at least 2 s after it. The sampler never runs outside a window, never with `--reset-ms` (a reset restarts
the rails' average: E41). The 20 Hz windows lengthen the SP pass (E41: 263 to 320 ms on aifoundry3, 158 to 188 on
aifoundry1's card 1), which separates "the rails are one pass late" from "the rails are a fixed time late".

Rules the block enforces:

- **Before anything touches a card**: STOP files, other users, our own device processes, `et-who --check`, the
  binaries (read only). Off the development card, the freeze (`LOCK.sha256`, `PREREG.sha256`), for a smoke too.
- **The card's lock** (`flock -n /run/lock/etsoc-shire<N>.lock`) is held for the whole block, so every device process
  runs under it; `timeout 10` on every device process; at the end the lock is released and `et-who --check` is
  recorded in `block.json`.
- **The sampler** is stopped with SIGTERM only. A start with no line in 10 s (or a sampler that exits without one) is
  a failed start, retried up to 6 times; on aifoundry3 one drain (`timeout 10 dev_mngt_service ... -n 0`) follows the
  second failure. **On aifoundry1 there is no drain** (its stock `dev_mngt_service` opens card 0's management node
  too): two failed starts in a row, or any sampler killed with SIGKILL (after ignoring SIGTERM for 30 s), write
  `build/claims-v3/aifoundry1-c1/tau/STOP` with the reason ("card 1 mgmt queue may hold a stale reply; drain needs the
  owner") and end the block; no later block starts until the owner drains the queue and removes the file. A SIGKILL
  on any card ends the block. A first line that comes too late for the burst to fit in the sampler's 10 s
  (`timeout - pre - setup_allow - burst - post`: 1.3 s for a 4 s burst, 3.3 s for 2 s) is a late start: the window
  is stopped at once and repeated with no burst. Each window's start latency and failed starts are in
  `windows.jsonl`, and their summary is in `check.json` and `block.json`.
- **Temperature**: the first (idle) window's die mean must be at most 72 C (`start_max_c`), or the block ends with
  exit 3 before any burst (let the card cool, then re-run); a window whose die mean reaches 90 C ends the block and
  writes `tau/STOP` for this card. Start and end die temperatures are in `block.json`.
- **Between windows**: STOP files, another user or a foreign device process end the block (exit 3).
- **A bad window** (no launches, a non-zero exit, a clock off 600 MHz, a starved sampler, a line without `temp_c`,
  `sp` or `board_w`, a crashed check) is recorded and repeated, at most three windows per entry.
- **Passes**: a full pass whose `block.json` says ok is skipped on a re-run; any other attempt is set aside
  (`p<pass>.attempt-<time>`) and the pass runs again. `report` refuses a pass that is not full and ok
  (`--allow-partial` scores it, flagged).

About 2.3 min of card time per pass (13 x ~10.5 s), about 1 min for the smoke.

Data: `build/claims-v3/<card>/tau/p<pass>/`: `tel-NN.jsonl` (each window's telemetry), `windows.jsonl` (each window:
rate, kind, times, start latency, sampler tries and failures, burst exit and launches, its check), `bursts.jsonl`
(each burst's kernel start and end from the ENERCAT lines), `runs.jsonl` (the ENERCAT lines), `check.json`,
`code.sha256` (the code, the binaries and the kernel's `.text`), `manifest.txt` (`et-lab-manifest`), `run.log`,
`block.json`. The smoke goes to `tau-smoke/p<pass>/`.

`reduce.py report <pass dirs of one card> --out FILE` fits every channel (one-pass and fixed-delay models, per rate),
per-burst and per-pass tau, rise against fall (sum of squares over the bursts), M against H, board_w's in-burst drift,
deconvolves every burst with the FROZEN offline tau (Gaussian 0.1 s, the primary; TV 0.03 W, the secondary), scores
each prediction PASS / FAIL / NO-DATA against its calibrated band (`prereg.json` `calibrated`, else the prior band),
and gives each theory's verdict on that card (PREREG.md, "Decision rules").

## Dry runs and calibration (no device access)

```bash
V3_DRY=1 TAU_DRY_CARD=aifoundry1-c1 bash tools/claims-v3/tau/block.sh 1 --smoke      # on aifoundry1 also V3_DEVICE=1
V3_DRY=1 TAU_DRY_CARD=aifoundry3 TAU_DRY_SKIP_LOCK=1 bash tools/claims-v3/tau/block.sh 101
python3 tools/claims-v3/tau/reduce.py report build/claims-v3-dry/aifoundry3/tau/p10{1,2,3} --card aifoundry3
python3 tools/ettelem/deconv.py --selftest
```
`TAU_STUB_SCALE` (default 0.1) compresses time; `TAU_STUB_NOISE=k` makes the simulated residual k times the card's
offline one; `TAU_STUB_FAIL=tel_nostart:<k>,tel_hot:<k>,tel_warm:<k>,tel_slow:<k>,tel_notemp:<k>,tel_ignoreterm:<k>,
enercat_crash:<k>`, `TAU_STUB_ETWHO_RC=1` and `TAU_STUB_FOREIGN=1` inject faults; `TAU_STUB_FIXED_DELAY=<s>` simulates
the rival theory. Real runs refuse any `TAU_STUB_*` or `TAU_DRY_*` variable.

The bands were set by `calibrate.py` (PREREG.md, "Calibration"; about 30 min of one niced core):

```bash
C=tools/claims-v3/tau/calibrate.py; O=build/claims-v3-dry/tau-calib
python3 $C match --card aifoundry3                          # the noise matched to the offline residual (stub-common.py)
python3 $C run --card aifoundry3 --reps 40 --seed0 1000 --noise 1.25 --out $O/a3-true-k125-A.jsonl
python3 $C bands --card aifoundry3 --in $O/a3-true-k125-A.jsonl --write        # into prereg.json "calibrated"
python3 $C run --card aifoundry3 --reps 40 --seed0 2000 --noise 1.0 --out $O/a3-true-k100-B.jsonl      # and k 1.25,
python3 $C run --card aifoundry3 --reps 40 --seed0 4000 --noise 1.0 --fixed-delay 0.263 --out $O/a3-rival-k100-B.jsonl
python3 $C score --card aifoundry3 --in $O/a3-*-B.jsonl                         # false-fail rates and power
```
(the same for aifoundry1-c1, seeds as in `calib.json`).

## Running it on a card

Nothing needs building: the block runs the campaign's `build/ettelem/ettelem` and `build/enercat/host/enercat_host`
(with the g3log fix, `tload_pat`, `--stride` and its kernel ELF present: checked read-only on aifoundry1 and
aifoundry3 on 28 September), and python3 with numpy (lib.sh finds `pylib/` or `.venv/`). From aifoundry2's checkout:

```bash
nice -n 19 rsync -aR --exclude __pycache__ tools/claims-v3/tau tools/ettelem/deconv.py aifoundry1:nekko/
ssh aifoundry1        # then, in ~/nekko: et-who; who; uptime (nobody on either card, no CI job)
V3_DRY=1 V3_DEVICE=1 TAU_DRY_CARD=aifoundry1-c1 bash tools/claims-v3/tau/block.sh 1 --smoke    # stubs only
et-who --check && V3_DEVICE=1 bash tools/claims-v3/tau/block.sh 1 --smoke                      # ~1 min on card 1
python3 -c 'import json; c = json.load(open("build/claims-v3/aifoundry1-c1/tau-smoke/p1/check.json")); print(c["sampler"], c["die_c_start"], c["status"])'
```
Go on to the full passes only if the smoke is ok, no start failed and the slowest first line (`start_ms_max`) is
under about 1000 ms (a 4 s burst needs it under 1300 ms); otherwise record it in the development log and change the
block first. Then:

```bash
setsid nohup bash -c 'cd ~/nekko && for p in 1 2 3; do V3_DEVICE=1 bash tools/claims-v3/tau/block.sh $p || break; sleep 120; done' \
  > ~/nekko/build/claims-v3/tau-dev-aifoundry1-c1.log 2>&1 < /dev/null &
```
Collect `~/nekko/build/claims-v3/aifoundry1-c1/tau/` into `docs/reports/data/<date>-tau-aifoundry1-c1/` and run
`reduce.py report <that>/p{1,2,3} --card aifoundry1-c1 --out <that>/report.json`. Validation on aifoundry3 after the
freeze: the same rsync (with `LOCK.sha256` and `PREREG.sha256`), then passes 101-103 (queue lines `tau 101` ... are
fine there: a one-card host's queue opens no device between blocks). On aifoundry1 run the passes directly as above:
queue.sh reads the die there with `timeout 20` and no card lock before each block.

## Departures and notes

- Bursts are single enercat processes of 0.4 s launches back to back (the catalogue's timing), 2.0, 3.2 and 4.0 s
  long for `--seconds 2, 3, 4`. The catalogue ran `build/enercat_v2`; the block runs `build/enercat` (the same
  patterns, with the g3log fix), so the D burst's kernel binary differs from the catalogue's; tau does not depend on it.
- The pass check at the end of a block (`check-pass`) needs a burst of every scheduled kind and every channel's fit
  to converge (0.3 < tau < 1.8 s, residual under 5% of the step); the decisions are made only by `report` over the
  pooled full, ok passes of a card.
- `queue.sh` on a two-card host reads the die with lib.sh's `die_c` (`timeout 20`, no card lock) before each block;
  on aifoundry1 run the passes directly (above) rather than through the queue.
- `deconv.py` models a stream sampled without `--reset-ms`. The samplers of E52, HP, OH and DV2 reset the SP's
  statistics every second, and a reset restarts the rails' average (E41: 93% of a step gone 1 s after a burst): the
  CLI refuses those streams; they need the reset in the model (not written) before they can be deconvolved.
- `et-who --check` on aifoundry1 counts card 0's holders too, so the block does not start while anyone uses card 0.
- aifoundry2's governor lifts the clock off 600 MHz on a die below about 65 C; its windows would then be marked
  `clock` and repeated, and its start gate (72 C) conflicts with a heat step. Its passes need an amendment first (a
  heat step, its own start temperature, a D burst that does not starve its sampler, and its own calibration).

## Freeze (before the first validation pass)

From the tree's root, after the last development change (the main session does this, and records both hashes):

```bash
sha256sum tools/claims-v3/tau/PREREG.md > tools/claims-v3/tau/PREREG.sha256
sha256sum tools/claims-v3/tau/{block.sh,reduce.py,taulib.py,calibrate.py,tau.json,prereg.json,calib.json} \
  tools/claims-v3/tau/stubs/{stub-common.py,stub-ettelem,stub-enercat,stub-etwho,simulate.py} tools/ettelem/deconv.py \
  tools/claims-v3/lib.sh tools/claims-v3/queue.sh > tools/claims-v3/tau/LOCK.sha256
```
The validation passes (101-199) and aifoundry2's (201-299) refuse to start, a smoke included, unless both check
(`sha256sum -c`), on the host that runs them: copy both files with the rest.

## Development log

(Changes to the block's files after development pass 1 are listed here, each with its reason, before the freeze.)

- 2026-09-28, before any card pass (review fixes): bands calibrated on simulated replicates (the prior ones failed
  true theories on 3-5 of 6 replicates at card-level noise); P3b pooled over the rails; P4b by sum of squares; float
  comparisons rounded; sampler starts waited 10 s with 6 tries, late starts repeated, start latencies logged, a
  ten-window smoke; aifoundry1's no-drain STOP rule; a smoke on the validation card needs the freeze; only ok passes
  count as done; `deconv.passes` per sampler segment; the rails' extra delays and board_w's creep in the stubs; a
  seeded burst order per pass, a start gate on the die and the die's start and end in `block.json`; `build/enercat`
  instead of `enercat_v2`; `et-who --check` after the block.

# E98: what the overnight die-line probes should log (from lane desk-gov, Q132(g)), v1, Sun 1 Nov 2026 ~00:10 PDT

Desk only, from committed data plus the boxes' own 5 s history. Nothing here has touched a card. Numbers are from
`$W/out/desk-gov/{die-lines,drift-paired,room-proxies,rest-decay,rep-noise}.txt`, which go in the lab repo under
`docs/reports/data/2026-11-01-q132-governor-desk/` with this lane's commit.

## The finding E98 is testing

**The "heat path drift" tracks the room at rest.** All three boxes share a daily cycle: aifoundry2's rest die reads
46.1 C at 11:00 PDT and 49.6 C at 20:00 PDT (nine-day hour means). E64 ran at 20:37-21:11 PDT on 23 Oct, at the warm
end; E80 and E83 ran at the cool end. Against the rest die in the 30-5 min before each session (a2 W / die):

| session | start (PDT) | rest W | rest die | line shift from E80, shared kinds |
|---|---|---|---|---|
| E80 | 31 Oct 12:22 | 21.76 | 45.58 | 0 |
| E83 | 31 Oct 13:46 | 22.03 | 46.42 | -0.10 +- 0.20 (5 kinds) |
| E87 | 31 Oct 19:49 | 22.17 | 47.15 | +0.41 +- 0.20 (5 kinds) |
| E64 | 23 Oct 20:37 | 22.69 | 49.28 | +1.12 +- 0.33 (5 kinds) |

Through the origin, weighted: **+0.25 +- 0.07 C of 76 s line per C of rest die**. Fitted on 31 Oct alone (+0.18 +- 0.11)
it predicts E64 at +0.65 +- 0.41 against +1.12 +- 0.33. n = 4 sessions, post hoc, with E80 a common baseline: this is
the hypothesis for E98 to test, not a result.

Why 0.25 and not 1: my reading, untested. A 76 s run from a die gated at 55-57 C keeps part of the gate's start, whatever
the room did. At the trip the same shift is larger in watts: fp16 ones read 49.3 W / 737 MHz in E64 and 53.2 W / 782 MHz
in E80 (about -1 W and +12 MHz per C of rest die).

## What to read, and how often

| # | what | how | cadence | why |
|---|---|---|---|---|
| 1 | **The rest reading: aifoundry2's idle board W and die, in the last 60 s before each probe's first launch, with no launch on the card in the previous 15 min** | your sampler at 10 Hz (no `--reset-ms`), or `~/live/history` (item 3) if the lock is free | once per probe, before work | **the best room proxy tonight.** Idle W has 0.01 W resolution and follows the die at 0.2315 W per C (r 0.978, residual 0.077 W, about 0.33 C). It is the same card and takes no extra sensor |
| 2 | **NIC and NVMe on aifoundry2 at rest** (`temps.nic`, `temps.nvme` in item 3, or `/sys/class/hwmon`: `enp7s0` PHY and MAC, `nvme` Composite and Sensor 2) | item 3; also one `sensors -j` snapshot into your run dir at each probe's start and end | 5 s (item 3) | NIC: r 0.978 against idle W, 0.256 W per C, 0.1 C steps. **Heated by the card itself, so read at rest only.** NVMe has 1 C steps |
| 3 | **All three boxes' own history: `~/live/history/<UTC date>.jsonl`** (`t` ms, `temps.{cpu,nvme,nic}`, `load`, `cards[].{n,held,die,max,w}`). Already written by `tools/lab/live/live-collector.py`; nothing to start | `rsync`/`ssh cat` at the end of E98 from aifoundry1, 2, 3 (read-only). Keep the UTC days covering the run. Files are deleted after 9 days | 5 s, continuous | the shared-room signal from other boxes during your load. Against a2's idle W: a1c0 die r 0.951, a1c1 die 0.942, a1c1 W 0.934, a3 W 0.923, a1 NVMe 0.922, a1 NIC 0.919, a3 NIC 0.903, a3 NVMe 0.899. **A box's rows mean nothing while its own card works: drop rows with `held` true, no `die`, a W over the idle bar (a1c0 22, a1c1 34, a3 27 W) or `load` over 2.** Other lanes run a3 and a1c1 tonight, so expect holes. On aifoundry1 either card held blanks both |
| 4 | Clock: epoch ms everywhere, and `date +%Z` in each probe's record | | | 02:00 PDT goes back tonight; the hour tables below are PDT |
| 5 | Each probe's gate reading, `held_s`, `die_start`, time since the previous launch | as the runner already does | per run | the 76 s line depends on the start; E64's gate held 35.7 s, E80's 0 s |
| 6 | Trace ring after every run, `ettelem config` at the start and end, `et-lab-manifest`, `who`, `et-who` | as E80 | per run / session | etiquette, and the idle-reset view (item 10): a dip inside a probe has to be flagged |

**Rest time.** After a session, idle W is back within 5 min (median +0.03 W), NVMe within 10 min, NIC within 15 min
(+0.06 C), over the session ends in `rest-decay.txt`. So rest at least 15 min before each rest reading; 30 min costs
nothing overnight.

**Do not use:**
- `acpitz` (constants 16.8 and 27.8 C on all three boxes);
- `sar` (the sysstat files hold no temperature group, `SADC_OPTIONS="-S DISK"`, so there is no longer history there);
- the CPU package on a box that is computing (a3 r 0.51);
- outside air in phase (r 0.11: the room's peak lags it by hours, details in `room-proxies.txt`);
- the camera's own thermistors (four session starts, no pattern). the camera phone's sensor page answered nothing from aifoundry2 at 23:5x PDT, so do not make the run depend on it.

**Fans.** Not readable tonight without loading `it87` as root, which I did not do and do not recommend mid-run. aifoundry2's
fans were left at full duty since 6 Oct, so a fan drift is not the leading candidate; say in the README that it was not read.

## What to expect tonight, to freeze predictions against

Nine-day hour means on aifoundry2 at rest (PDT; subtract 1 for PST after 02:00 PDT):

| hour | die | W | a2 NIC | a2 NVMe |
|---|---|---|---|---|
| 00 | 48.45 | 22.50 | 45.88 | 38.78 |
| 02 | 48.18 | 22.42 | 45.56 | 38.52 |
| 04 | 47.48 | 22.26 | 45.04 | 38.00 |
| 06 | 46.84 | 22.11 | 44.44 | 37.56 |
| 08 | 46.54 | 22.03 | 44.10 | 37.25 |
| 11 (the low) | 46.08 | 21.94 | 43.74 | 36.84 |
| 20 (the high) | 49.59 | 22.77 | 46.80 | 39.58 |

Tonight runs below those means: the card read 47 C / 22.13-22.17 W at 23:50 PDT. Expect a fall of about 1.5-2 C of rest
die by 07:15 PST (08:15 PDT), so about **-0.4 to -0.5 C of 76 s line**, on the 0.25 slope. Compare with the whole range
from 23 Oct: 3.7 C of rest, +1.12 C of line. The night's range is half of that, so plan for a small effect.

**Noise, for the number of runs.** Replicate ranges of (die - 0.4573 W) within one session have a median of 0.99 C (12 kinds,
`rep-noise.txt`). The die is a 1 C-step reading and the runs at the trip are the noisiest (E83 fp32 ones 41.12 and 39.99).
A shift of 0.4 C needs **at least 6-9 runs per probe**, with the same kinds and the same gate in every probe, and the first
and last probes as far apart as the window allows.

**Anchors that do not touch the trip** (800 MHz, no clamp, comparable sessions on record):
- fp32 zeros, 35-36 W, die 58-59 C (E64 42.37, E83 41.81, E87 41.58 in die - k W);
- fp16 zeros, 35-36 W, die 58-59 C (E64 42.50, E80 41.63, E83 41.65, E87 41.63);
- int8 zeros, 36-38 W, die 57-59 C (E64 41.82, E80 41.06, E83 40.43, E87 41.65);
- int8 neg_ones, 41 W, die 60 C (E80 41.24, one run);
- int8 sparse50, 49 W, die 63.6 C (E80 41.18, one run), the top of the unclamped range.

**At the trip**, for the speed a reader cares about: fp16 ones or fp32 ones, with replicates. Predicted about +12 MHz per
C the rest die falls (E64 to E80), on a run-to-run spread of 21-23 MHz.

**Worth adding if the budget allows: one long hold per probe.** Hold one unclamped kind (fp32 zeros or int8 neg_ones) for
5-6 min and read the die over the last 2 min. Idle W forgets a session within 5 min, so this should be close to steady. If
the room is the cause, the hold's die should follow the rest die about 1:1 (against 0.25 for the 76 s line), which separates
the room from a real change of the path far better than the small shift above. If it does not follow, the room reading
is wrong.

## Decision rules I would suggest (E98's lane owns the registration)

1. The line (kinds shared across probes, die - 0.4573 W, runs averaged per kind first) against the rest die: slope positive and
   its 95% interval excluding 0 supports the room; an interval excluding 0.25 says this desk slope is wrong.
2. Report the same slope with a2 NIC at rest and with the best other-box proxy that has rows, beside the rest die.
3. A probe with an idle-reset dip in its last 40 s (the 800 to 600 MHz drop with no 700 sample) is flagged and kept in, with the
   dip's samples named. The cause is being written up by this lane; see `result.md` when it exists.

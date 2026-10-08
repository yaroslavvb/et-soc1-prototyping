# aifoundry2's card ran away again at idle, 7 October 2026

On Wed 7 Oct 2026 the owner asked what had happened to aifoundry2 ("I fixed it before, but now it's broken again.
Check maybe the fan speed. Did the fan fall off?"). The idle card had run away and fallen off the PCIe bus at
16:46 PDT, 24.7 hours after the 6 October BIOS fan fix had brought it back. The cause was the cooling at the card. The
card itself had not changed. The published page is
[2026-10-07-aifoundry2-idle-runaway.html](../../2026-10-07-aifoundry2-idle-runaway.html)
(https://spacesheep.dev/@yaroslavvb/aifoundry2-idle-runaway-7-october).

| File | What it is |
|---|---|
| `extract.py` | copies the live collector's 5-second records for Tue 6 Oct 16:00 to Wed 7 Oct 17:10 PDT out of `~/live/history/` on aifoundry2: `python3 extract.py ~/live/history records.jsonl.gz` |
| `records.jsonl.gz` | those records, unchanged: 18,047, of which 17,678 have a card reading (`die` = mean of the 34 minion-shire sensors, `max` = highest since the card started, `w` = board power, `held`); the host's `nvme`, `nic` and `cpu` temperatures and load |
| `kernel.txt` | the kernel's lines about the card and its root port, 16:46:32 to 17:01:20, with where each came from (the 16:46 lines were read at 17:16, before the ring buffer dropped them) |
| `analyze.py` | every number and chart series: refits the 2 October model from `../2026-10-02-idle-runaway-aifoundry2/records.jsonl` by that folder's `fit.py` method, then reads off each minute's air temperature at the card, the steps, the host's sensors, the fit residuals, the crossings and the hourly table; writes `analysis.json` |
| `analysis.json` | `analyze.py`'s output: `numbers`, the per-minute `series`, the last minutes at full rate (`tail`), power by whole degree (`scatter`), `hours` |
| `build_report.py`, `report.css` | build the page from `analysis.json` and `kernel.txt`: `python3 build_report.py analysis.json kernel.txt report.css out.html` |

## Findings (all PDT; numbers from `analyze.py`)

- **Back on the bus** at 16:05:32 on 6 Oct. The fix's load tests held the card at 16:22:30–16:35:05. Nobody held it
  after that. From 17:00 to 03:50 it idled at 63–70 °C and 26.9–30.3 W.
- **03:55, 7 Oct: the cooling at the card got worse in one step.** The card went from 64 °C and 27.6 W to 78 °C and
  34.5 W by 04:50, then held 74–78 °C until 11:30. The host was idle (0.5% CPU), and its sensors did not move across
  the step (NVMe 45.9 → 46.3 °C, network chip 54.1 → 53.8 °C, CPU 39 → 38 °C).
- **About 14:25: worse again.** 85 °C at 14:44:50, 90 °C at 15:30:25 (43.3 W), 100 °C at 16:39:55, 110 °C at 16:44:05,
  120 °C at 16:45:40. The last reading was at 16:46:40: a 138 °C mean, hottest sensor 144 °C, 133.45 W. No reading
  came from 16:46:45 on. On 2 October the last reading was 138 °C, 144 °C and 133.65 W.
- **The card did not change.** At every temperature, its power matched the 2 October leakage law,
  P(T) = 13.56 + 2.025·e^(0.0300·T) W: 0.25 W rms over 17,678 readings, and within 0.44 W at every whole degree with
  at least 12 readings.
- **The air at the card, by the 2 October model** (R 0.897 °C/W, C 296 J/°C; air = T − R·(P − C·dT/dt), dT/dt a
  least-squares slope over 6 minutes): 39.4 °C in the night, 45.6 °C from 05:00 to 11:30, 50.7 °C from 15:00 to 16:15.
  An idle card has no steady temperature with air above 51.5 °C. The model's steady temperatures for air at 39, 46 and
  51 °C (63, 76 and 91 °C) are what the card did. These are model numbers: a loss of airflow shows up as warmer air.
- **The kernel:** 5 corrected receiver errors at 16:46:32–36; the driver's queue read as all ones at 16:55:02; root
  port 00:01.1 reset at 17:01:20, by whom or what is not known. The card did not come back.
- **The fan is not known.** No fan sensor driver is loaded on aifoundry2, and loading one needs root. The BIOS
  setting stands (no reboot since the fix), and Linux never switched a fan (the ACPI fans' `stats/total_trans` is 0).
- **Nothing in the firmware stops an idle runaway.** On the card's build (BL2 0.20.0, release 1.3.1; closest public
  source `ffca4cbb4`) the thermal loop runs at idle above 65 °C but can only step the clock down, and the idle card is
  already at its lowest point, 600 MHz. The PMIC alarm's safe state never moves the PLL (fixed upstream in `e024210bc`),
  and nothing calls `pmic_force_shutdown()`. Upstream `836a4ab` skips the thermal check at idle altogether
  (`check_power_throttle_conditions()`, `thermal_pwr_mgmt.c:864–883`). See `docs/findings/14-card-behaviour.md`.

## To rebuild

```
cd docs/reports/data/2026-10-07-idle-runaway-aifoundry2
python3 analyze.py
python3 build_report.py analysis.json kernel.txt report.css ../../2026-10-07-aifoundry2-idle-runaway.html
```

The deployed page carries the comment anchors that the CLI adds. The committed HTML is the deployed bytes
(`spacesheep read`), so after a rebuild, deploy it to space `1cc2c15c-866a-4735-ad38-983ee5f7b959` and copy the
deployed bytes back (`docs/reports/MIRROR.md`, "Deploying one page").

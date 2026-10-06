# aifoundry2's ET-SoC-1 card after the BIOS fan fix, 6 October 2026

On 6 October between about 15:55 and 16:07 PDT every fan of the machine was set to Full Speed in its BIOS and the
machine was fully reset. The menu is **Smart Fan 6** on this board (Gigabyte Z590 AORUS MASTER) — "TUNE ALL" sets
every header at once — not the "Smart Fan 5" that older notes name. The card has idled at about 64 °C since, where it
used to idle at 71–80 °C and, on 2 October, ran away to 138 °C and fell off the PCIe bus
([that day's data](../2026-10-02-idle-runaway-aifoundry2/README.md)). The published page is
[2026-10-06-aifoundry2-fan-fix.html](../../2026-10-06-aifoundry2-fan-fix.html).

| File | What it is |
|---|---|
| `records.jsonl` | the live collector's 5-second records (`tools/lab/live/live-collector.py`), 16:05:32–16:39:55 PDT, 407 of them. `cards[0]`: `die` = mean minion-shire temperature, `max` = hottest minion shire (°C), `w` = board power (W); `temps` are the host's hwmon sensors. 90 records carry no card reading: the collector does not read a card that someone holds, which covers the burst test and the long run. One 37 s gap at 16:06:52 |
| `manifest.txt` | `et-lab-manifest` at 16:12 PDT: host, kernel, CPU, power profile, clock sync, driver version, the card's link, library hashes |
| `dmesg-card.txt` | the card's kernel lines after the reset |
| `burn.sh`, `burn-c0.log` | the 8-minute sgemm burst test and its log, one line per burst (`rc`, `die`, `max`, `w`) |
| `run-long.sh`, `long-1006/` | the 21 September long-session protocol, run again: `schedule.txt` (`randn 32 600 1`), `starts.jsonl`, `ends.jsonl`, `runs.jsonl` (149 runs), and `telemetry.jsonl.gz` (2,543 `ettelem` samples, 16:30:52–16:35:06, compacted with `tools/ettelem/compact_telemetry.py`) |

## The numbers

**Idle** (16:16–16:22, nobody holding the card, host idle): die **64 °C** median, 63–64 over 72 readings; hottest
shire 67 °C; **27.4 W** median, 27.0–27.7. The host read 45 °C NVMe and 53 °C NIC.

**The 8-minute sgemm burst test** (16:22:25–16:30:30): **44 bursts, every one exit 0**; the die went from 66 °C to
**76 °C**, the hottest sensor reached 79 °C, and the board drew 33 W at the end. Nothing throttled and no kernel
message was logged.

**The long run** (`randn 32 600 1`, the 21 September protocol: start when the die reads 80 °C, stop at a 90 °C cap).
It reached the cap after **37.3 s** (373 samples, `starts.jsonl` → `ends.jsonl`), against **19.3–26.5 s** for the same
run on 21 September (runs 1, 4, 8, 23): with the fans at full speed the card takes about half again as long to heat
through the same 10 °C. Board power peaked at **71.6 W** (68.4 W median) over those 37 s. Three and a half minutes
later, at 16:35:06, the card was back to **75 °C** and 33.1 W.

**One field to read carefully:** `hottest` in the telemetry is the peak since the card's statistics were last reset
(`since_reset_ms` = -1 here, so: since the card started), not a current reading. It stood at 93 °C after the run, which
is the long run's own peak, not a temperature the card was sitting at.

## How to repeat it

`burn.sh` takes the card's device number and a duration; `run-long.sh` reads `long-1006/schedule.txt`. Both take the
card's lock and refuse to start while another process holds it. Nothing here touches the BIOS: the fan settings are a
person at the machine's console (Del at boot → F2 Advanced Mode → Smart Fan 6 → TUNE ALL → Full Speed → F10).

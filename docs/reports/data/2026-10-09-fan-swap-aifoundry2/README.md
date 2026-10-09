# aifoundry2's ET-SoC-1 card after the card-fan swap, 9 October 2026

On Fri 9 October between 14:55 and about 15:17 PDT the 120 mm fan clipped under aifoundry2's card, which had been
stalling since 7 October, was taken out, and a two-fan 92 mm PCI-slot bracket was fitted in the slot beside the card.
One of the bracket's two Pano-mounts fans (CF9225GPU2PACK, 12 V, 0.32 A, 3,000 RPM) was swapped for a Cooler Master
SickleFlow 92 (650–2,300 RPM, 4-pin) because its cable was longer. The machine was booted at 15:07, before the bracket
was back in. The published page is [2026-10-09-aifoundry2-fan-swap.html](../../2026-10-09-aifoundry2-fan-swap.html)
([live](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-9-october)).

| File | What it is |
|---|---|
| `records.jsonl.gz` | the live collector's 5-second records (`tools/lab/live/live-collector.py`), Thu 8 Oct 14:28 – Fri 9 Oct 16:05 PDT: Thursday's idle creep and runaway (the card stopped answering at 19:49:27), the swap, and today's tests. The collector does not read a card that someone holds, which covers the burst test and the heavy run |
| `manifest.txt` | `et-lab-manifest` at 15:35:58 PDT |
| `idle-snapshot.json`, `a3-idle-snapshot.json` | one `ettelem sample` on each card at 15:35:59 and 15:36:10, before the tests |
| `sensors.txt` | the fan controller on both hosts at 15:34 (`sensors it87952-isa-0b10`, as root) |
| `burn.sh`, `burn-c0.log` | the 8-minute sgemm burst test of 6 October, unchanged but for its folder, and its log |
| `run-long.sh`, `long-1009/` | the 6 October heavy run repeated: `schedule.txt` (`randn 32 600 1`), `starts.jsonl`, `ends.jsonl`, `runs.jsonl.gz` (one record per launch), and `telemetry.jsonl.gz` (10 Hz `ettelem` samples, 15:45:13–16:00:53) |

## The numbers

**Before the fans were back** (15:07–15:16, idle): the die heated by about 4.4 °C a minute, from
44 to 87 °C, and the board from 21.6 to 40.8 W. With the fans on it
fell to 51 °C by 15:24.

**Idle** (15:24–15:36, nobody holding the card): die 50.8 °C, 23.2 W. aifoundry3's card read
53.2 °C and 24.3 W in the same minutes. On Thursday 15:00–16:00 this card idled at
71.3 °C and 30.8 W.

**The burst test** (15:36:44–15:44:50): 44 bursts, every one exit 0; the die went from 49 to
63 °C and levelled off at 62–63 °C. On 6 October the same test went from 66 to 76 °C, still climbing.

**The heavy run** (start 15:47:51 at 71 °C; the preheat reached only 71 °C, so the run did not wait):
it ran the full 602 s (`reason: time`), at 56 → 58.7 W, and settled at
75.0 °C (mean of its last 2 minutes; peak 75.1). Three minutes after it the die read
54 °C. On 6 October the same run started at 80 °C and reached the 90 °C cap after 37.3 s. All 1,584
launch records report `ok` with no tensor errors; the driver counted no error events and the root port no PCIe errors.

**The margin** (a one-node steady state; model values): the cooling is the slope between the idle and full-load
plateaus, 0.68 °C/W, with the air at the card at about 35 °C. With the 7 October leakage law
(P = 14.39 + 1.836·e^(0.0308·T) W) the idle card has no resting temperature from 1.26 °C/W
(1.9 times today's) or air 29 °C warmer; under sustained full load
(25.9 W of dynamic power) from 0.81 °C/W (1.2 times) or air
11 °C warmer. Thursday afternoon works out to 1.18 °C/W at today's air.

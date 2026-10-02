# aifoundry2's ET-SoC-1 card: idle thermal runaway after a cold boot, 2 October 2026

`records.jsonl`: the live collector's 5-second records (`tools/lab/live/live-collector.py`) from the full-reset boot at
10:53:16 PDT until the card fell off the PCIe bus at 12:02:01. The host was idle throughout; no process held the card.
`cards[0]`: `die` = mean minion-shire temperature, `max` = hottest minion shire (°C), `w` = board power (W), read once
a second with `ettelem temp`; `temps` are the host's hwmon sensors. 828 records.

Key points: 45 °C / 21.9 W at boot; 85 °C / 39 W after 22 min; 95 °C / 48 W at 56 min; then runaway: 105 °C / 61 W at
11:58, 116 °C / 79 W at 12:00:36, 126 °C / 104 W at 12:01:31, last reading 138 °C (hottest 144) / 134 W at 12:02:01,
link down at the next read (config space all ff, `SQ[0] sync: head mismatched`). No firmware cut-off acted.
The host CPU stayed at 37–46 °C. Same failure as 07:42 that morning (126 °C / 103 W, last reading before the drop).

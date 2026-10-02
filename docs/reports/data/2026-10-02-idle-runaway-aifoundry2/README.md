# aifoundry2's ET-SoC-1 card: idle thermal runaway after a cold boot, 2 October 2026

`records.jsonl`: the live collector's 5-second records (`tools/lab/live/live-collector.py`) from the full-reset boot at
10:53:16 PDT until the card fell off the PCIe bus at 12:02:01. The host was idle throughout; no process held the card.
`cards[0]`: `die` = mean minion-shire temperature, `max` = hottest minion shire (°C), `w` = board power (W), read once
a second with `ettelem temp`; `temps` are the host's hwmon sensors. 828 records.

Key points: 45 °C / 21.9 W at boot; 85 °C / 39 W after 22 min; 95 °C / 48 W at 56 min; then runaway: 105 °C / 61 W at
11:58, 116 °C / 79 W at 12:00:36, 126 °C / 104 W at 12:01:31, last reading 138 °C (hottest 144) / 134 W at 12:02:01,
link down at the next read (config space all ff, `SQ[0] sync: head mismatched`). No firmware cut-off acted.
The host CPU stayed at 37–46 °C. Same failure as 07:42 that morning (126 °C / 103 W, last reading before the drop).

## Why the curve has this shape (`fit.py`, output in `fit.txt`)

The idle card's power grows with its temperature: 13.6 W plus a leakage part that doubles every 23 °C (0.44 W rms over
22–134 W). Its cooling, fitted on the first 45 minutes, sheds heat into air at about 51 °C through about 0.9 °C/W
(time constant about 4.4 minutes). Heating and cooling just touch: at about 97 °C they are within 0.1 W of each
other (the fit cannot tell whether they cross), so the card rises fast at first (the 4-minute time constant), crawls
through 86–94 °C at this tipping point, and runs away once leakage grows faster than cooling (dP/dT above
1/R ≈ 1.1 W/°C). Over the hour the host's NVMe and network-chip sensors rose 3–4 °C as the case air warmed, which is
enough to push it over. aifoundry3's identical
card idles at 53 °C and 24.3 W, which on the same leakage curve means air at about 31 °C. Air only 3 °C cooler would
hold aifoundry2's card at about 81 °C, so the fault is the air reaching this card, not the chip. One run: R and the
air temperature are correlated in the fit; the conclusions hold over the range of fits that match the data.

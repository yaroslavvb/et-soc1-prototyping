# Q145(a): aifoundry3's idle floor across every committed session, split into the room and the card's own part (post hoc)

*Thu 5 Nov 2026 (week 45), about 22:55-23:20 PST, on the Intel, desk only (no card, no lab box), by the lane heat-q145a of Q145(a),
round A (the stock-take's step 4). **Post hoc and descriptive: it reads committed files only and decides nothing.** It is the evidence for
M11's dated amendment A6 ([`REGISTRATION.md.dated-note-A6.md`](../../../../tools/claims-v3/m11/REGISTRATION.md.dated-note-A6.md),
committed with it), which answers the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **items 9 and 8** and E176's G0 refusal.*

## Results

**1. The floor moves with the room and the hour; the card's own tail is gone after an hour.** A session's floor is its first sample (the
34-sensor mean by E97's conversion where the sampler carried the raw codes; else the firmware's whole degree plus 0.94 °C, the mean offset
of the five raw-code sessions, 0.77-1.20, labelled "est"). Settled = at least an hour since the last committed session on the card; M6's
slowest pole (1,500 s) bounds the tail of any earlier run at 0.005 °C there.

| hours (PST), November, settled | sessions | floor (°C) | firmware |
|---|---|---|---|
| before 12:00 | 5 (Sun 1, Mon 2 twice, Tue 3, Thu 5 Nov) | 48.9-49.9 (est) | 48-49 |
| 12:00-17:00 | 4 | 50.9-51.8 | 50-51 |
| 17:00 and after | 3 | 50.9-53.2 | 50-52 |

In September and October, settled floors read firmware 50-55 °C (est 50.9-55.9 °C; 24-25 Sep at midday, 55). The raw-code floors: E89 Sat 31
Oct 17:59 51.773 °C; E144 Mon 2 Nov 22:37 50.888; E154 Tue 3 Nov 17:53 50.982; E166 Wed 4 Nov 14:20 51.838; E176 Thu 5 Nov 17:21 53.202
(4 h 46 min after E171). E97's R0 ended on its slope at 50.559 °C (Sun 1 Nov, early morning).

**2. The split: about four fifths room, one fifth the card's own leakage answering it.** A die at rest sits at T = T_room + R x P_idle(T)
(R = 0.8695 °C per board W, Q138(t)), and P_idle rises with T, so the floor moves by 1 / (1 - g) of a room change, g the loop gain
(0.21-0.25 at 49-53 °C by E97's law). Against E144's 50.888 °C (32 min after E141; at most 0.07 °C of tail):

| session | floor change (°C) | room part, T - R x P (°C) | the card's own part, R x ΔP (°C) | its share (the loop's g) |
|---|---|---|---|---|
| E176, Thu 5 Nov 17:21 | +2.314 | +1.922 | +0.392 (board +0.45 W) | 0.17 (0.24) |
| E166, Wed 4 Nov 14:20 | +0.950 | +0.784 | +0.166 | 0.17 (0.23) |
| E89, Sat 31 Oct 17:59 | +0.885 | +0.780 | +0.105 | 0.12 (0.23) |
| E154, Tue 3 Nov 17:53 | +0.094 | +0.136 | -0.042 | (too small to read) |

The measured share (0.12-0.18) sits under the law's g because the board's idle level also wanders by about ±0.2 W between sessions
(`floor_analysis.json` › `rows[].board_minus_law_w`: −0.01 to +0.18 W on the raw-code floors).

**3. The room proxies agree, where the lab recorded one.** E97's host sensors (`room.txt`: the host NVMe 36.71 °C, the host CPU 32.4 °C over
R0) and E176's host windows (`room-rule/hostwin-base.out`: NVMe 38.85 °C in whole kelvins, coretemp cores 2-9 at 32-34 °C, acpitz_1 27.8 °C):
the floor rose 2.64 °C while the NVMe rose 2.14 °C, a ratio of 1.24 against the loop's predicted 1 / (1 - g) = 1.31. The host was idle in
both (its CPU near 32-34 °C). No other session recorded a room proxy or host load.

**4. G0 against the history** (each settled floor plus the largest committed smoke residue at G0's window, 0.43 °C: E154 0.428, E166 0.087,
E176 0.380): the registered G0 (53.0 °C) passes 17 of 26 settled sessions and 11 of 12 in November (E176 refused); A6's G0 (53.9 °C, residue
at most 0.50 °C) passes 21 of 26 and 12 of 12 in November; five September-October sessions (firmware 53-55 °C) are refused by both. Before
noon in November every floor would pass with more than 3.5 °C to spare and run M11's cool pattern.

**5. Where A6's 53.9 °C comes from** (`plan_rooms.json`, M11's committed exact planner, `design_power_heat_v2.plan_exact`, run unchanged):
H_E's planned in-launch peak (34-sensor mean) reads 68.13 / 68.51 °C at 51.2 / 51.5 °C (cool pattern), 66.15 at 52.0, 67.35 at 53.0, 68.07
at 53.6, **68.44 at 53.9** and 68.56 at 54.0 (warm pattern); the registered envelope over G0's admitted rooms is 68.51 °C (plateau 66.10),
crossed at 53.96 °C. Every other hold stays at or under 65.72 °C at 53.9.

## What this cannot say

- Two committed readings of a room proxy, one of them in whole kelvins; the room part is inferred from the die and the board, not measured.
- The "est" floors carry the firmware's whole degree (±0.5 °C) plus the offset's spread (0.77-1.20 °C).
- A settled floor is a first sample; a room can move within a session (E97 saw the plateau move 0.3-0.8 °C with nothing changed).

## Files and how to reproduce

| file | what |
|---|---|
| `floor_scan.py`, `floors.json` | every committed aifoundry3 pass's first and last sample, grouped into sessions; each session's floor, rest and the M11-family R0 `room` and `start_gate` marks |
| `floor_analysis.py`, `floor_analysis.json` | the floor table, the split, the room proxies, the hours, the smoke residues and both gates on the history |
| `plan_rooms.py`, `plan_rooms.json` | M11's exact planner at rooms 51.2-55.0 °C and the warmest room inside the registered envelope |
| `SHA256SUMS` | the files above |

```bash
# from the lab clone's top, with a python that has numpy (each step takes under a minute)
D=docs/reports/data/2026-11-05-q145a-a3-idle-floor
python3 -B $D/floor_scan.py . <scratch>/floors.json && cmp <scratch>/floors.json $D/floors.json
python3 -B $D/floor_analysis.py $D/floors.json . <scratch>/floor_analysis.json && cmp <scratch>/floor_analysis.json $D/floor_analysis.json
python3 -B $D/plan_rooms.py . <scratch>/plan_rooms.json && cmp <scratch>/plan_rooms.json $D/plan_rooms.json
```

SPDX-License-Identifier: Apache-2.0

# E183's data README, dated note M1 (Fri 13 Nov 2026): october-forecast-model's reported arms v3 and v4, read after the data commit through the day-2 check v2's gate - READER-RC 0, its two outputs beside this note

*Beside [README.md](README.md), which it edits nothing of. Written on aifoundry2, desk only, by the card lane `card-e183g` of Q173, after
the data commit `39970848` (git 16:43:38 PST Fri 13 Nov 2026, pushed). The card lane's brief places the reader after the data commit and
behind the day-2 check v2's gate, never by hand: [CARD-LANE-BRIEF.md.dated-note-2.md](../../../../tools/claims-v3/e183/CARD-LANE-BRIEF.md.dated-note-2.md)
section 3, and its dated note 5's table, last row. It records the gate's run, its `READER-RC` line and the reader's two outputs, as those
notes say. **Reported, never a rule:** october-forecast-model's arms are never one of E183's rules and never one of E183-MECH's lines
([E183.md.dated-note-M1.md](../../../../tools/claims-v3/e183/E183.md.dated-note-M1.md), M1-4, with its
[dated note 1](../../../../tools/claims-v3/e183/E183.md.dated-note-M1.md.dated-note-1.md)). Their readings are the reader's own words, in
[`arm-m1-e183.txt`](arm-m1-e183.txt) and [`arm-m1-e183.json`](arm-m1-e183.json); this note restates none of them.*

## The run

- **The gate:** `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 --data docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3`,
  under the lab clone's commit lock, through the round's CPU slot, 16:43:54-16:43:56 PST, at HEAD `39970848` (`/usr/bin/python3` 3.12.3 on
  aifoundry2).
  - It ran the day-2 check v2's tree check with no pull: E185's box list 27 of 27 repo entries OK; E183's brief list's 10 non-M1 entries
    and 5 M1 entries OK; the M1 list `e185/SHA256SUMS-e185-m1` 21 of 21 at its pinned bytes; no M1 file changed since `6860643c`.
  - It found 114 files added since `6860643c` in the day's 156 directories, none a shadowing module, and 0 untracked files there.
  - The data directory was committed and clean. The gate's line: `M1-READER-GATE-V2 e183 OK at 3997084823ec`.
- **The reader:** `/usr/bin/python3 -B tools/claims-v3/e183/arm_m1_read_e183.py --reduced docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3/reduced-e183.json --scored docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3/scored-e183.json --out docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3/arm-m1-e183`.
- **`READER-RC 0`** (a refusal or a non-zero exit is recorded, never a block). The gate then read "2 new file(s) in
  docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3, nothing else changed".
- **Its two outputs**, the only new files: [`arm-m1-e183.json`](arm-m1-e183.json) (10,460 bytes, sha256 `e7547127...`) and
  [`arm-m1-e183.txt`](arm-m1-e183.txt) (4,262 bytes, sha256 `035ce410...`). [`SHA256SUMS-m1`](SHA256SUMS-m1) pins both and this note.

## The arms it read (their freeze lines, as the reader prints them)

- `october-forecast-model v3, frozen Sat 7 Nov 2026 23:32:50 PST, sha256 292c8c30c1acd5c0d017e3c422e7a1dc147ce0f94015c5fdde045c14493380e5, covering E183's 11 kinds and its 6 trains (fadd.ps one-number, above the fadd.ps zeros)`
- `october-forecast-model v4, frozen Sun 8 Nov 2026 03:59:42 PST, sha256 10bf2782de1411f920dbd596f319b75cb3539e329b967eccf394ee089b659c77, covering E183's 11 kinds and its 6 trains (fadd.ps one-number, above the fadd.ps zeros)`

The reader sets each arm's six trains, b, c, E183-X's and E183-J's statistics beside E183's measured intervals, in watts above the fadd.ps
zeros at E183's rate; it reads neither card 1's figures nor the kinds' levels.

## Labels

- **Modelled:** every figure of october-forecast-model, as frozen (v3 and v4, the lines above), before any E183 datum.
- **Measured, blind:** E183's trains and statistics, as the committed `scored-e183.json` gives them.
- **Reported:** both arms. Nothing here changes a rule, a verdict or README.md.

SPDX-License-Identifier: Apache-2.0

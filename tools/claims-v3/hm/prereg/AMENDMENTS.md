# E62 amendments

Each is recorded before any reduction of the data it touches.

## A1 — the power fallback, Wed 21 Oct 2026 17:14 PDT (during E62-ORBIT; nothing reduced yet)

**What E62-CAL measured** (board power at the end of each 8.5 s rung, from the runner's own 10 Hz `ettelem` reading,
against a 22.7 W idle at 600 MHz; every loaded rung at 800 MHz):

| set | harts | board W | switched W |
|---|---|---|---|
| B4C (4 × 32) | 128 | 35.55 | +12.8 |
| W8B_16 (8 × 16) | 128 | 35.70 | +13.0 |
| INT16_8 (16 × 8) | 128 | 36.09 | +13.4 |
| CEN8 (8 × 32) | 256 | 42.82 | +20.1 |
| W12 (12 × 32) | 384 | 49.40 | +26.7 |
| INT16 (16 × 32) | 512 | 57.61 | +34.9 |

The hart-matched triple agrees within 0.54 W, so power follows harts, not geometry, as predicted. The size does not:
the design priced 40.6 mW per hart from zero (+5.2 W at 128 harts, +15.6 W at 384), and the card draws an offset of
about 6.5 W plus about 53 mW per hart. The die reached 65 °C, the governor's step, during the 384-hart octet.

**Registered branches that fire** (`protocol.json` `conventions.power_fallback`):
- branch 1, a 384-hart arm above 16.0 W switched (measured +26.7 W);
- branch 2, the UNI32 rung above 45 W switched (512 harts already read +34.9 W, so 1,024 harts are about +60 W).

**What is changed, and why one number differs from the registered one.** Branch 1 registers `--per-shire 24`
(288 harts) for every 384-hart block. On the measured curve that is about +22 W and a ~66 °C steady die: still over the
65 °C governor step the branch exists to avoid. So the amendment keeps the branch's intent and picks the number from
the measurement:
- every 12-shire set (W12, E12, N12, S12, W12_A, W12_B, NULLP12, NULLQ12) at `--per-shire 16`, 192 harts, about
  +16.5 W, about 62 °C steady: the operating point the predictions were priced at (15.6 W);
- every 8-shire set (W8B, E8B, SCAN1, SCAN2, CEN8, SCAN4, SCAN5) at `--per-shire 24`, 192 harts, the same power. No
  registered branch covers them (they were priced at 10.4 W); the same intent applies, since at `--per-shire 32` they
  measure +20.1 W and settle near 65 °C;
- branch 2 as registered: UNI32 at `--per-shire 24` (768 harts), E62-BLOOM's off-phase 85.0 → 127.5 s, and E62-WE17
  dropped to pay for it.

Harts stay equal within every swap. Every amplitude is re-anchored per measured watt. E62-CAL and E62-ORBIT ran as
registered (ORBIT's 128-hart arms measure about +13 W instead of 5.2 W and settle near 60 °C, under the step, so its
amplitudes are expected about 2.5 times the frozen predictions).

**How it is carried out.** The runner cannot change its protocol mid-session, so the first session
(`build/e62/runs/e62-card-1021`) is ended cleanly by an operator STOP in the 30 s gap after E62-ORBIT's last launch,
and a second session (`e62-card-1021b`) runs `protocol-A1.json` (sha256 `5d7910c4179b3500…`): E62-BLOOM, E62-WE42,
E62-NS42, E62-NULLAA, E62-NULLGEO, E62-W8BE8B, E62-SWEEP, in the registered order, with its own 90 s idle background.

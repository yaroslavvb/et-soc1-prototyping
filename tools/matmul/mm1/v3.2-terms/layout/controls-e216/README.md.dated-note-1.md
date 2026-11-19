# Dated note 1 to E216's layout controls: the independent check's verdict, and the freeze line

*Thu 19 Nov 2026, Pacific time. Written by land-controls-e216 (round Q229) from 14:41 PST, at the desk on aifoundry2, before any
E216 datum: E216's card lane had not booked the card and had made no folder. It records the verdict of check-controls-e216 (round
Q229), which ran at the desk on this folder and on committed data. Every number below is **desk**. The controls are **REPORTED**
forecasts and never a registered rule of E216; nothing here is measured or blind. This note changes no file of the folder: the seven
files are committed byte for byte as controls-e216 froze them at 14:18:33 PST.*

## What is committed here, and its freeze line

- **The seven files** (`README.md`, `constants-verify-lay.json`, `controls-e216.csv`, `controls-e216.json`, `controls_e216.py`,
  `work/features-e216.json` and `SHA256SUMS`) were final at **14:18:33 PST**. Their sha256 were posted as post **#2.8.3.1** on the
  owner's coordination thread at **14:22:22 PST**:

      8b5ab4b41d8fb70ec612785db3420bc3e529cb7559f7712982521217f269556c  controls-e216.csv
      8ff71a820dbf72a2b73cdb27cf42450e88ca521dd67ec6e7989edc11ded53050  controls-e216.json
      475e1ce095987a8ac43e7672750d9a224bdd82060a74018a7159dc50ef8de3d7  controls_e216.py
      fdd662c8b0e706672a14158cab90d85a3965ea3bf7e5f9886ede981c40af2f95  SHA256SUMS

  That post is their freeze line; this commit is a later record of it. When it was posted, E216's card lane had not booked
  aifoundry2's card and had made no folder, so the post came before E216's first card command and before any E216 datum. The
  orchestrator's answer to E216's registration (its question 2) asked for exactly this: the controls frozen by a post before E216's
  card lane books, never a registered rule, the registration unchanged.
- **`SHA256SUMS`** covers the six other files: `sha256sum -c SHA256SUMS` in this folder prints 6 of 6 OK. This note is not in it.
- **Before this commit** the land lane checked again: every posted sha256 equals its file (4 of 4), `sha256sum -c` gives 6 of 6, and
  the seven files equal controls-e216's land byte for byte.

## The check: check-controls-e216 HOLDS

*14:21-14:33 PST, at the desk. `/usr/bin/python3` 3.12.3 with numpy 1.26.4, run as `-I -B`, single-threaded in the round's CPU slots.
No card and no simulator were used, and no E216 or E215 data file was opened: of E215 it read only the registered point list and the
frozen forecasts.*

- **Every value, re-made independently.** The check's own caller, written from `v02_fits.py`'s text, and its own features re-made all
  **690** control values (46 points x 3 clocks x 5 controls) **bit for bit**. Its features came from the committed masked walk's
  `chip_steps` as the request generator, its own two-capacity strict LRU at 24 and 32 MB, and its own hop mean from the mesh map's
  text. The 230 factors and the 96 subset features are bit-equal, and so are the v3.1 and F1 columns at 138 of 138 rows. Its CSV,
  in this file's column layout, is `controls-e216.csv` byte for byte.
- **The features.** n, requested lines, fresh lines at 24 and 32 MB and the hop mean equal `work/features-e216.json` at 24 of 24
  configurations, bit for bit. They also equal the registration's frozen walk features (largest difference 0.0 at 32 MB).
- **The constants.** `constants-verify-lay.json` equals verify-lay's fit table (its `v02_fits.json`, sha256 `1bfec7fc...`, written
  at 10:22:51 PST) at every float and every repr.
- **F1.** The frozen constant times the check's own Phi_fresh equals E216's frozen 'v3.1 + contention' cycles at 138 of 138 rows, bit
  for bit. Phi is equal at 48 of 48 subset rows and the layout factor at 138 of 138.
- **The E215 reproduction.** The check's caller re-made `../controls-e215/v02_e215_controls.csv` byte for byte (`c5bc2394...`) from the
  committed `../controls-e215/work/v01_map.json`. It did so again from its own features for E215's 43 configurations, which equal the
  committed records at 43 of 43. All 470 unrounded values are bit-equal to verify-lay's rows.
- **The README's REPORTED statements.** The subset factor ranges are bit-equal, and every sign statement holds.
- **No E216 datum.** At 14:21 and at 14:31 PST there was no booking, no E216 card-lane folder, no E216 readiness result and no
  quiet-desk flag, and GitHub main (`4f648f24`) held no path naming E216. controls-e216's scripts test the card lane's folder for
  existence only.

The check's findings, which this note records. None changes a frozen file:

1. **(info) The layout-blind F1 is not among the frozen controls.** The orchestrator's answer named it beside the four count and hop
   controls. The round's brief bound exactly the columns of E215's file, and the README says "Not made", with its reason. None of
   E216's 8 Y shapes is among MM1-v3.1's fit points.
2. **(info) The inputs were the registration lane's own files**, made before E216's registration was on GitHub main:
   `points-e216.csv` `a83b5e1c...` and `forecast-e216.json` `92c9444a...` (the README's input table). Once the registration is
   committed, compare the committed files' sha256 with these two. If they differ, re-run the caller on the committed files (0.02 s in
   the check's own run) and record both hashes; if only the forecast file's made and ended times differ, the values still hold.
   **NOT RUN here:** when this note was written, E216's registration was not on GitHub main.
3. **(nit) The within-pair ln values** in `controls-e216.json`'s meta are ln(factor a / factor b). They equal ln(cycles a / cycles b)
   up to rounding, because MM1-v3.1's forecast is equal within each pair: 36 of 40 control values and 7 of 8 F1 values are bit-equal,
   and the rest differ by at most 2.2e-16. The 4-decimal table and every sign are unchanged.
4. **(info) NOT RUN by the check:** a re-derivation of verify-lay's constants by re-running `v02_fits.py`, and a re-run of
   controls-e216's own caller. For the first, land-terms' re-run of that script on a lab clone of main `21ba4b45` re-made E215's file
   byte for byte (`../controls-e215/README.md`).

## How to read it

These are REPORTED desk forecasts, made before any E216 datum, from constants fitted on committed data that existed before E215 and
E216. None of them enters a registered rule of E216. Score them beside F1 and MM1-v3.1 as the README says.

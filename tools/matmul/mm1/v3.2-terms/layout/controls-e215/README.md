# REPORTED controls for E215's points beside the layout term (posted as #1.29.1.1 before any E215 datum)

*Thu 19 Nov 2026, Pacific time. Committed by land-terms (round Q225); made by verify-lay (round Q225, track C). Desk and post hoc:
every constant here was fitted on committed data that existed before it. The forecasts were made before any E215 datum, but they are
**REPORTED**: they were never a registered rule of E215, and E215's registration scores none of them.*

## What this is

`v02_e215_controls.csv` holds, for each of E215's 94 registered rows (arm A's 60 points and 2 references, arm B's 30 points and 2
references), the wall cycles an op forecast by MM1-v3.1, by the frozen 'MM1-v3.1 + contention' term F1 (the folder above), and by five
controls that verify-lay fitted to ask whether F1's held-out gain needs placement at all (`../README.md.dated-note-1.md`, corrections
1-4). verify-lay wrote it at **10:22:51 PST**, before any E215 datum existed (no E215 card command had run, and both arms were held),
and it was posted by its sha256 as post **#1.29.1.1** on the owner's coordination thread at **10:31:36 PST**, with its maker's sha256:

    c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d  v02_e215_controls.csv
    4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8  v02_fits.py (verify-lay's copy; see "The maker" below)

The CSV is committed here byte for byte. That post is its freeze line; this commit is a later record of it.

## The columns

Each control is T = T_v31 x (1 + sum a_i x_i) on the wall cycles an op, with every x_i = 0 at the full mask, so every column equals
MM1-v3.1 at the 66 full-mask rows. The constants are all-data, two-stage (fitted on MM1-v3.1's committed fold records' residuals, the
base's constants not refitted), as for F1. n is the number of active shires.

| column | form | constants |
|---|---|---|
| `v31_cycles_per_op_wall` | MM1-v3.1 (2c971828), its frozen E215 forecast | - |
| `F1_frozen_cycles_per_op_wall` | the frozen F1: x = Phi_fresh, the walk's DRAM lines per requested line minus the full chip's (32 MB L3) | a = -0.0831659 |
| `REPORTED_N3_cycles_per_op_wall` | x = 32/n - 1 (shire count only) | a = +0.00100737 |
| `REPORTED_N1+N2_cycles_per_op_wall` | x1 = 1 - n/32, x2 = (1 - n/32)^2 (shire count only) | a1 = -0.0934896, a2 = +0.117657 |
| `REPORTED_G1_cycles_per_op_wall` | x = the active shires' mean L3 latency over the 32 homes (110 + 12 x hops) over the full chip's, minus 1 | a = +0.303143 |
| `REPORTED_G1+N1_cycles_per_op_wall` | G1 and 1 - n/32 | a1 = +0.602213, a2 = -0.0216757 |
| `REPORTED_fresh24_cycles_per_op_wall` | Phi_fresh with a 24 MB L3 | a = -0.0899132 |

Held out on the committed data (verify-lay; LOLO (b), pooled LOEO with no twins, in %): MM1-v3.1 6.319, 4.723; F1 6.248, 4.710;
N1+N2 6.066, 4.699; 32/n - 1 6.127, 4.702; G1 6.172, 4.703; G1+N1 5.888, 4.700; Phi_fresh at 24 MB 6.190, 4.718.

## The maker, and what was changed in it

| file | what | sha256 |
|---|---|---|
| `v02_e215_controls.csv` | the controls, **byte for byte** as posted | `c5bc2394...` |
| `v02_fits.py` | verify-lay's maker: its two-stage fits, the alternatives, the placebos and bootstraps, and the E215 columns | see `../SHA256SUMS-note1` |
| `v01_map.py` | verify-lay's own request-to-slice mapping and LRU, which makes `v02_fits.py`'s feature input | see `../SHA256SUMS-note1` |
| `work/v01_map.json` | that feature input, **byte for byte** as verify-lay made it | `096fa1a9...` |

The two scripts are committed with **three lines each rewritten**: the lines that named this box's lab clone and the round's working
folders now find the lab from the script's own place (or from `ET_LAB`), read and write `work/` in this folder, and read the layout
folder above (lay-contention's land, byte for byte). Every other byte is verify-lay's. verify-lay's own copies had sha256
`4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8` (`v02_fits.py`, lines 22, 24 and 25 rewritten here) and
`b1650360e6c88d435a61bfad09631583872c40a348a59df7cdcb7796f948a369` (`v01_map.py`, lines 32-34 rewritten here).

**Re-made from the rewritten copies** (land-terms, 12:10-12:14 PST, desk, `/usr/bin/python3` 3.12.3 with numpy 1.26.4, `-I -B`,
single-threaded, under a 4 GB cap, in a scratch copy of this folder with `ET_LAB` at a lab clone of main 21ba4b45): `v01_map.py`
re-made `work/v01_map.json` equal on every key but its run time (`secs`), and then `v02_fits.py` re-made `v02_e215_controls.csv`
**byte for byte** (sha256 `c5bc2394...`).

To re-run from a checkout of the lab, from this folder: `/usr/bin/python3 -I -B v01_map.py`, then `/usr/bin/python3 -I -B v02_fits.py`,
with OMP_NUM_THREADS=1 and the like. They read MM1-v3.1's code and fit records (`tools/matmul/mm1/v3.1/`), the masked walk, the mesh
map in `workloads/nocbench/analyze.py`, E215's registered point list and the layout folder above, and write `work/v01_map.json`,
`work/v02_fits.json`, `work/v02_bases.npz` and `work/v02_e215_controls.csv` (compare the last with this folder's
`v02_e215_controls.csv`). Neither reads an E215 datum.

## How to use it

After E215's data, score these columns beside F1 and MM1-v3.1 on E215's subset rows (family L), as REPORTED numbers. E215 can tell
them apart only weakly: F1 gives one factor to every layout of a shape at an equal shire count (12 rows at 0.999505, 2 at 1.0), and
only the other 14 subset rows, small-count rows of distinct shapes, move, by -0.6% to +1.4% (`../README.md.dated-note-1.md`,
correction 6).

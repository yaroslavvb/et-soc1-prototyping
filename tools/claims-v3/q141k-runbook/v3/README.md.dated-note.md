# Dated note beside v3's README.md, Wed 4 Nov 2026 (week 45), about 22:00 PST: v3.1 supersedes v3 (Q142(s), after v3's verifier)

*Written beside [`README.md`](README.md) and not inside it: v3 stays as committed (lab `326f1293`, 20:14:12 PST), byte for byte. Desk
only: no card, no device command, no lab box.*

**For any later step or card day, use v3.1: [`../v3.1/README.md`](../v3.1/README.md).** v3's verifier (4 Nov 2026, about 20:18-21:05
PST) read v3 and found it holds with fixes. Its end-to-end run of the real collectors reproduced E163's registered collection byte for
byte by v3's route, with no desk path. v3.1 is v3 with these changes:
- `s22_collect.sh`, `s13_a1_launch.sh` and `nopath_q142s.py` are corrected;
- in `rb_common.sh`, `rb_nopath` gets a message for an output that is not there, and the step names carry `_v3.1`;
- `ccdone_q142s.py` is new;
- every other file is v3's byte for byte (v3.1's desk test, case V).

What in this README the verifier corrected:
1. **§ Results first, "This read of it found 12 faults".** The read missed a 13th, which v2 and v3 share. No version of `s22` read
   whether a collection's check of C finished. `ccheck.py` exits 1 both on a crash and on a C FAIL, and it writes its `--out` file only
   at its end. So a check that crashed was scored as if C had failed or gone unrecorded, and the step said "collected and scored". v3
   stopped it only when the crash's traceback happened to hold a desk path (16, the wrong reason). The verifier found this in e163 and
   e166. It holds in e164, e165 and e167 too. v3.1's fault 1 fixes all five.
2. **§ What the read checked and found sound, "The exit codes … In v3: 10 also covers a launcher's refusal".** It did not cover exit 9,
   whose line is `check_e164.py`'s `HARNESS DIFFERS - refusing:`. v3 read that refusal as 14, against `s13_a1_launch.sh`'s own header.
   This is v3.1's nit 5.
3. **§ What v3 changes, fault 2, "A hit stops the step (16)".** A path that is not there was no hit: `nopath_q142s.py` printed
   `MISSING` and read CLEAN, so a collector that wrote somewhere else passed the gate unread. This is v3.1's nit 8.

"None bit on 4 Nov" stands, and covers v3.1's fault 1 too. Every check of C that the card half's collections ran finished, all PASS
(v3.1's case Z0, on the ten committed checks).

The watcher fix this README links, [`../../hpl/run_hpl.py.dated-note.md`](../../hpl/run_hpl.py.dated-note.md), has five corrections of
its own in [`../../hpl/run_hpl.py.dated-note-2.md`](../../hpl/run_hpl.py.dated-note-2.md): its blind window, the committed records'
bound, the incidence counts, the 8.4 s / 8.1 s timing and a path.

SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E191's second session's data commit 7156ac15; KIT.md.dated-note-3.md): step 9 v3
and step 11 v3 made from their v2 files by EXACT REPLACEMENTS, each applied exactly once (the generator refuses otherwise), so that "v3 is v2
with these replacements and nothing else" can be checked by anyone: --check rebuilds both in memory from the committed v2 files and compares
them with the committed v3 files byte for byte (V3-FROM-V2 SAME, or DIFFERS); --write writes them (the lane ran it once).
    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/v3from_v2_e191.py --check
A desk check of code: nothing is measured. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import os
import sys

E = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rb") + os.sep

H9 = """#!/usr/bin/env bash
# E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after E191's
# second session's data commit 7156ac15 of Sun 15 Nov 2026, 14:32:17 PST; KIT.md.dated-note-3.md): STEP 9 v3, for E191.md's dated amendment
# A2's THIRD SESSION (a REPEAT, REPORTED). It is rb/s11_a1_session_e191_v2.sh (unchanged beside it) with seven exact replacements and nothing
# else: this header; the step's name (s11_a1_session_v3); THE LAST LAUNCH's reference when RB_OUT holds no T0, now the SECOND session's T0
# 1794780355 (7156ac15: 14:05:55 PST Sun 15 Nov 2026), the box's last E191 launch before A2's (v2's reference, the first session's T0
# 1794766494, now refuses: the box's build/q141k/e191.T0 reads the second session's), and the words that name it; the refusal's words for an
# RB_OUT whose launch sent a card command (A2's third session is E191's last); the LAUNCHED line and the step's last line naming A2's third
# session. Session v2 and runner
# v2 run unchanged (kit note 2), so steps 10 v2 and 11 v3 read the session as kit note 2's.
#   bash tools/claims-v3/e191/rb/s11_a1_session_e191_v3.sh FULL      (never --rapl-allowed: A2 does not allow the package counter)
# v2's header follows:
"""

H11 = """#!/usr/bin/env bash
# E191's kit, dated note 3 (Q190, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after E191's
# second session's data commit 7156ac15 of Sun 15 Nov 2026, 14:32:17 PST; KIT.md.dated-note-3.md): STEP 11 v3, for E191.md's dated amendment
# A2's THIRD SESSION (a REPEAT, REPORTED). It is rb/s22_collect_e191_v2.sh (unchanged beside it) with five exact replacements and nothing else:
# this header; the step's name (s22_collect_v3); the data directory docs/reports/data/<the window's day>-e191-blind-day-aifoundry1-c1-s3/
# (the first session's ...-c1/ and the second session's ...-c1-s2/ are committed and never merged into), with two gates made stricter for
# safety before anything is read or copied: RB_OUT's T0 must not be an earlier E191 session's (the first's 1794766494, the second's
# 1794780355: the second session's log names kit note 2 too, so v2's start-line test alone would not refuse it), and no ...-c1-s3 directory
# of ANY day may exist already (A2 allows one third session); the refusal's words on the box; and the step's last line naming step 13 v3.
#   bash tools/claims-v3/e191/rb/s22_collect_e191_v3.sh
# v2's header follows:
"""

SPECS = {
    "s11_a1_session_e191_v3.sh": ("s11_a1_session_e191_v2.sh", [
        ("#!/usr/bin/env bash\n", H9),
        ("rb_init s11_a1_session_v2\n", "rb_init s11_a1_session_v3\n"),
        ("E191_FIRST_T0=1794766494          # the first session's T0 (1a4bc1e3: 10:14:54 PST Sun 15 Nov 2026), the box's last E191 launch before A1's\n",
         "E191_FIRST_T0=1794780355          # A2: the SECOND session's T0 (7156ac15: 14:05:55 PST Sun 15 Nov 2026), the box's last E191 launch before A2's\n"),
        ("KW=\"the first session's T0 (1a4bc1e3; this RB_OUT has launched nothing)\"",
         "KW=\"the second session's T0 (7156ac15; this RB_OUT has launched nothing; A2's third session)\""),
        ("one session an RB_OUT; A1's second session is the day's last\"", "one session an RB_OUT; A2's third session is E191's last\""),
        ("(session v2, kit note 2; programs $PROG;", "(session v2, kit note 2; A2's third session, a REPEAT; programs $PROG;"),
        ("rb_say \"e191 (session v2, kit note 2) launched", "rb_say \"e191 (session v2, kit note 2; A2's third session, a REPEAT) launched"),
    ]),
    "s22_collect_e191_v3.sh": ("s22_collect_e191_v2.sh", [
        ("#!/usr/bin/env bash\n", H11),
        ("rb_init s22_collect_v2\n", "rb_init s22_collect_v3\n"),
        ("DATA=docs/reports/data/${RB_DAY:-DAY}-e191-blind-day-aifoundry1-c1-s2\n",
         "DATA=docs/reports/data/${RB_DAY:-DAY}-e191-blind-day-aifoundry1-c1-s3\n"
         "case \"$t0\" in 1794766494|1794780355) rb_die $RB_E_USAGE \"RB_OUT's T0 $t0 is an earlier E191 session's (the first, 1a4bc1e3, or the second, "
         "7156ac15): step 11 v3 collects A2's third session only; nothing read or copied\" ;; esac\n"
         "for d3 in \"$RB_REPO\"/docs/reports/data/*-e191-blind-day-aifoundry1-c1-s3; do      # A2: one third session, whatever its day\n"
         "  [ -n \"${RB_DRY:-}\" ] || [ ! -e \"$d3\" ] || rb_die $RB_E_USAGE \"${d3#$RB_REPO/} exists already: A2 allows one third session; never merge "
         "into an earlier copy\"\n"
         "done\n"),
        ("step 11 v2 collects the second session only\"", "step 11 v3 collects a kit note 2 session only, A2's third\""),
        ("then run s24_score_e191_v2.sh on the committed data\"", "then run s24_score_e191_v3.sh on the committed data (REPORTED beside the registered verdicts)\""),
    ]),
}


def build():
    out = {}
    for name, (src, reps) in SPECS.items():
        t = open(E + src).read()
        for a, b in reps:
            n = t.count(a)
            if n != 1:
                raise SystemExit(f"V3-FROM-V2 REFUSED {name}: {a[:70]!r} matches {n} times in {src}")
            t = t.replace(a, b)
        out[name] = (src, len(reps), t)
    return out


def main(argv):
    if argv not in (["--check"], ["--write"]):
        print(__doc__)
        return 2
    built = build()
    if argv == ["--write"]:
        for name, (src, n, t) in built.items():
            open(E + name, "w").write(t)
            print(f"WROTE rb/{name} from rb/{src}: {n} exact replacements")
        return 0
    bad = [name for name, (src, n, t) in built.items() if not os.path.exists(E + name) or open(E + name).read() != t]
    print(("V3-FROM-V2 SAME: " if not bad else "V3-FROM-V2 DIFFERS: " + ", ".join(bad) + "; ") +
          "; ".join(f"rb/{name} = rb/{src} with {n} exact replacements" for name, (src, n, t) in built.items()))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""E213 Amendment A3 (Q219, lane a3-e213, Wed 18 Nov 2026, before any datum of E213's arm B): THE RUNNER'S WRAPPER for ARM B in A3's order. A3
moves arm B's four 'rgm136 gemmLnc' points (k40, k37, k38, k39: runs 39-42 of pass 1 and 44-47 of pass 2 in the registered order of 85) to the
END of arm B's session, in their own registered order and reversal (pass 1's k40, k37, k38, k39, then pass 2's k39, k38, k37, k40); every other
run keeps its registered order (the tie t02, pass 1 without them, the tie, pass 2 without them, the tie), so the session is the same 85 runs, the
same multiset of (block, point), and only the places change. Nothing else of the runner changes: this file runs E213's runner
tools/claims-v3/e213/run_e213.py, UNCHANGED, with ONE function of tools/claims-v3/e213/e213_common.py, UNCHANGED on disk, replaced in memory for
this process: e213_common.sequence (the order's runs, read by the runner once, when its runs start) answers arm B with A3's order from this
folder's sequence-B-a3.json (sha256-pinned below); every other reading of the runner (the points and their host arguments, the plan, the stops,
the gates, the card-time rule, the smoke, the identity gate per process, the walk check, the closing) stays the kit's.
Python's own modules only; it runs on aifoundry1 under the system python3 (3.12.3), as the runner does, and at the desk under /usr/bin/python3.

    python3 -B tools/claims-v3/e213-a3/run_e213_a3.py session --arm B --t0 T0 --out build/e213/T<T0>-B [--deadline-epoch E] [the runner's options]
        the session (A3's session_e213.sh starts it, as the kit's session_e213.sh starts run_e213.py): THE CHECK below first; a refusal prints
        "A3-STOP: ..." and exits 3 before the runner is imported (no device, no lock, no session folder written by the runner); else
        "A3-ORDER OK: ..." and the runner's main with these same arguments (its exit is this process's). --arm A is refused (exit 2): A3 is arm
        B's alone, and arm A's day has run (its data c69a12aa).
    python3 -I -B tools/claims-v3/e213-a3/run_e213_a3.py check
        THE CHECK alone (row 5b and row 9 run it on the box, the desk tests at the desk): "A3-ORDER OK: ..." (exit 0) or "A3-STOP: ..." (exit 3)
    python3 -I -B tools/claims-v3/e213-a3/run_e213_a3.py order
        the check, then the 85 runs as the runner reads them under A3, one a line (n, block, point, its family, its registered place), then the
        same-multiset line (the dry listing prints it)
    python3 -I -B tools/claims-v3/e213-a3/run_e213_a3.py make
        A3's order derived from the registered order, in sequence-B-a3.json's bytes, to stdout (how that file was made; the check compares)

THE CHECK: (1) points-e213.json at its registered sha256 f122b625... (the frozen scorer's pin; the box's harness pins it too); (2) this folder's
sequence-B-a3.json at SEQ_PIN; (3) its runs EQUAL to A3's order DERIVED here from the registered order at run time (points-e213.json > arms > B >
order > sequence): the runs of the points whose loop is 'rgm136 gemmLnc' (k37, k38, k39, k40 and no other) taken out in their registered order
and put after the last registered run, every run renumbered by its place (n = 1..85) and carrying its registered place; (4) the facts that follow,
read again: 85 runs, the same multiset of (block, point) as registered, the first run the tie, ties at runs 1, 39 and 77, the last eight runs
pass 1's k40 k37 k38 k39 then pass 2's k39 k38 k37 k40, the 77 other runs in their registered relative order; (5) the file's own fields (E213,
A3, arm B, 85 runs, the registered sequence's sha256); (6) THE DEVICE-COMMAND AUDIT of A3's two files the session runs (this file and A3's
session_e213.sh): the lab's checker tools/claims-v3/dmcmd_audit_v2.py (the harness's copy, which the kit's step 5 syncs) reads "dmcmd_audit: GO
(0 send site(s), 0 disallowed" - the kit's preflight, run by the runner before its first device access, audits the kit's files, among which A3's
two are not, so A3 audits its own: neither may send any device command. Each check that fails is named on its own "A3-STOP:" line.
THE REPLACEMENT: e213_common.sequence(arm) for arm B returns A3's runs as the kit's function returns the registered ones ({"n", "block", "id",
"name"}: the place in the session, the registered block "pass1" / "pass2" / "tie", the point, and the point's registered name, read from the
registered order by its id); for any other arm it is the kit's function itself. The sequence file carries no name (the points' names are read
from the registration), and so no file of this folder spells a shape. The runner, its reducer and the frozen scorer read a run by its point and
block (run.json's "id" and "block"); its place "n" names the run's folder (NNN-block-id) and appears in messages only (E213.md A3).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E213_DIR = os.path.normpath(os.path.join(HERE, "..", "e213"))
SEQ_F = os.path.join(HERE, "sequence-B-a3.json")
SESSION_F = os.path.join(HERE, "session_e213.sh")
SEQ_PIN = "6aea5d8c6333bb89ffadd4ac383167e28e947f673bdaf261f90264c8a05b3842"
POINTS_PIN = "f122b62500ce7d0f5e924f7454adb074d9ca673c328fe3c98c64a9b906d65d15"   # points-e213.json, registered (291c8201); score_e213.py's pin
MOVED = ("k37", "k38", "k39", "k40")                    # arm B's 'rgm136 gemmLnc' points (points-e213.json; the kit's self-check names the same four)
MOVED_LOOP = "rgm136 gemmLnc"
TAIL = [("pass1", "k40"), ("pass1", "k37"), ("pass1", "k38"), ("pass1", "k39"),
        ("pass2", "k39"), ("pass2", "k38"), ("pass2", "k37"), ("pass2", "k40")]
TIES_AT = [1, 39, 77]
RUNS = 85
WHAT = ("E213 arm B's run order under Amendment A3: the registered order (points-e213.json > arms > B > order > sequence) with the eight runs of "
        "the four 'rgm136 gemmLnc' points (k40, k37, k38, k39 in pass 1; k39, k38, k37, k40 in pass 2) moved, in their registered order, to the "
        "end of the session; every other run in its registered order; n renumbered by the place in the session; registered_n the registered "
        "place; the same 85 runs, the same multiset of (block, point)")

sys.path.insert(0, E213_DIR)
import e213_common as C  # noqa: E402  (the kit's module, unchanged on disk)

REGISTERED_SEQUENCE = C.sequence                         # the kit's own function, kept: the registered order of either arm


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def registered_b():
    return REGISTERED_SEQUENCE("B")


def derive(reg=None):
    """A3's order from the registered order (the rule, applied at run time): the moved points' runs out, in their order, then after the rest."""
    reg = registered_b() if reg is None else reg
    lnc = sorted(p["id"] for p in C.points()["arms"]["B"]["points"] if p["loop"] == MOVED_LOOP)
    if tuple(lnc) != MOVED:
        raise ValueError(f"arm B's '{MOVED_LOOP}' points are {lnc}, not {list(MOVED)}")
    rest = [r for r in reg if r["id"] not in MOVED]
    tail = [r for r in reg if r["id"] in MOVED]
    return [{"n": i, "block": r["block"], "id": r["id"], "registered_n": r["n"]} for i, r in enumerate(rest + tail, 1)]


def make_bytes():
    """sequence-B-a3.json's bytes: the header fields (sorted), then the runs one a line."""
    reg = registered_b()
    seq = derive(reg)
    head = {"experiment": "E213", "amendment": "A3", "arm": "B", "card": "aifoundry1 card 1", "what": WHAT,
            "registered_points_sha256": POINTS_PIN, "registered_sequence_sha256": hashlib.sha256(canon(reg).encode()).hexdigest(),
            "moved": list(MOVED), "moved_loop": MOVED_LOOP, "runs": len(seq), "ties_at": TIES_AT,
            "tail": [{"block": b, "id": i} for b, i in TAIL]}
    lines = ["{"]
    for k in sorted(head):
        lines.append(f" {json.dumps(k)}: {json.dumps(head[k])},")
    lines.append(' "sequence": [')
    for j, x in enumerate(seq):
        lines.append("  " + json.dumps({"n": x["n"], "block": x["block"], "id": x["id"], "registered_n": x["registered_n"]}) + ("," if j < len(seq) - 1 else ""))
    lines.append(" ]")
    lines.append("}")
    return ("\n".join(lines) + "\n").encode()


def load_seq():
    with open(SEQ_F, "rb") as f:
        return json.loads(f.read().decode())


def problems():
    """THE CHECK: [] when A3's order holds, else every failed check's words."""
    bad = []
    try:
        got = sha256_file(C.PTS_F)
        if got != POINTS_PIN:
            bad.append(f"points-e213.json is not the registered file (sha256 {got[:12]}, want {POINTS_PIN[:12]})")
    except OSError as e:
        bad.append(f"points-e213.json unreadable ({type(e).__name__})")
    audit = os.path.join(C.REPO, "tools", "claims-v3", "dmcmd_audit_v2.py")
    try:
        r = subprocess.run([sys.executable, "-I", "-B", audit, os.path.abspath(__file__), SESSION_F], cwd=C.REPO, capture_output=True, text=True,
                           timeout=120, stdin=subprocess.DEVNULL)
        said = r.stdout + "\n" + r.stderr          # the checker prints its verdict line on stderr, its summary on stdout
        if r.returncode != 0 or not re.search(r"^dmcmd_audit: GO \(0 send site\(s\), 0 disallowed", said, re.M):
            bad.append(f"the device-command audit of A3's two session files did not read GO with 0 send sites (rc {r.returncode}: "
                       f"{[x for x in said.splitlines() if x.startswith('dmcmd_audit')][:1]})")
    except (OSError, subprocess.SubprocessError) as e:
        bad.append(f"the device-command audit of A3's two session files could not run ({type(e).__name__})")
    try:
        got = sha256_file(SEQ_F)
        if got != SEQ_PIN:
            bad.append(f"sequence-B-a3.json is not A3's pinned file (sha256 {got[:12]}, want {SEQ_PIN[:12]})")
        F = load_seq()
    except (OSError, ValueError) as e:
        return bad + [f"sequence-B-a3.json unreadable ({type(e).__name__})"]
    try:
        reg = registered_b()
        want = derive(reg)
    except (KeyError, ValueError, OSError) as e:
        return bad + [f"the registered order could not be read ({type(e).__name__}: {str(e)[:120]})"]
    if (F.get("experiment"), F.get("amendment"), F.get("arm"), F.get("runs")) != ("E213", "A3", "B", RUNS):
        bad.append(f"the file's fields {F.get('experiment')}, {F.get('amendment')}, {F.get('arm')}, {F.get('runs')} are not E213, A3, B, {RUNS}")
    if F.get("registered_sequence_sha256") != hashlib.sha256(canon(reg).encode()).hexdigest():
        bad.append("the file names another registered order (registered_sequence_sha256)")
    runs = [{"n": x.get("n"), "block": x.get("block"), "id": x.get("id"), "registered_n": x.get("registered_n")} for x in F.get("sequence", [])]
    if runs != want:
        diff = [f"{a} vs {b}" for a, b in zip(runs, want) if a != b][:2]
        bad.append(f"the file's runs are not A3's order derived from the registered one ({len(runs)} runs; first differences: {diff or 'lengths'})")
    if len(want) != RUNS or len(reg) != RUNS:
        bad.append(f"{len(want)} runs under A3 and {len(reg)} registered, not {RUNS}")
    if sorted((r["block"], r["id"]) for r in want) != sorted((r["block"], r["id"]) for r in reg):
        bad.append("A3's runs are not the registered multiset of (block, point)")
    if [r["n"] for r in want] != list(range(1, len(want) + 1)):
        bad.append("A3's places are not 1..85")
    if [r["n"] for r in want if r["block"] == "tie"] != TIES_AT or any(r["id"] != C.ARMS["B"]["tie"] for r in want if r["block"] == "tie"):
        bad.append(f"the ties are not t02 at runs {TIES_AT}")
    if [(r["block"], r["id"]) for r in want[-len(TAIL):]] != TAIL:
        bad.append(f"the last eight runs are not {TAIL}")
    if [(r["block"], r["id"]) for r in want if r["id"] not in MOVED] != [(r["block"], r["id"]) for r in reg if r["id"] not in MOVED]:
        bad.append("the other 77 runs are not in their registered relative order")
    if sorted({r["id"] for r in want if r["block"] != "tie"}) != sorted(p["id"] for p in C.points()["arms"]["B"]["points"]):
        bad.append("A3's points are not arm B's registered 41")
    return bad


def a3_sequence(arm):
    """e213_common.sequence as A3 has it: arm B's runs in A3's order (each with the point's registered name); any other arm the kit's own."""
    if arm != "B":
        return REGISTERED_SEQUENCE(arm)
    names = {r["id"]: r["name"] for r in registered_b()}
    return [{"n": x["n"], "block": x["block"], "id": x["id"], "name": names[x["id"]]} for x in load_seq()["sequence"]]


def ok_line():
    F = load_seq()
    tail = " ".join(f"{x['n']}:{x['id']}" for x in F["sequence"][-len(TAIL):])
    return (f"A3-ORDER OK: arm B {len(F['sequence'])} runs, the registered multiset of (block, point); ties at runs "
            f"{', '.join(str(n) for n in TIES_AT)}; the 'rgm136 gemmLnc' runs last ({tail}); sequence-B-a3.json {SEQ_PIN[:12]}, "
            f"points-e213.json {POINTS_PIN[:12]}")


def say_stop(bad):
    for b in bad:
        print(f"A3-STOP: {b}")
    sys.stdout.flush()


def arm_of_argv(argv):
    """the --arm the runner's own parser will read (its abbreviations too), or None"""
    import argparse
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--arm")
    try:
        ns, _ = p.parse_known_args(argv)
    except SystemExit:
        return None
    return ns.arm


def main(argv):
    if not argv or argv[0] not in ("session", "check", "order", "make"):
        print("usage: run_e213_a3.py session --arm B ... | check | order | make")
        return 2
    what = argv[0]
    if what == "make":
        sys.stdout.buffer.write(make_bytes())
        return 0
    if what == "session":
        arm = arm_of_argv(argv[1:])
        if arm != "B":
            print(f"A3-STOP: Amendment A3 is E213 arm B's alone (aifoundry1 card 1); --arm {arm} refused before the runner (no device, nothing written)")
            return 2
    bad = problems()
    if bad:
        say_stop(bad)
        return 3
    if what == "check":
        print(ok_line())
        return 0
    if what == "order":
        print(ok_line())
        seq = load_seq()["sequence"]
        print("A3's order (n, block, point, family, registered n):")
        for x in seq:
            print(f"  {x['n']:3d} {x['block']:5s} {x['id']:4s} {C.family(x['id']):15s} registered {x['registered_n']:3d}"
                  + ("" if x["id"] not in MOVED else "  <- moved by A3"))
        a3 = sorted((x["block"], x["id"]) for x in seq)
        reg = sorted((r["block"], r["id"]) for r in registered_b())
        same = a3 == reg
        print(f"A3-ORDER: {len(a3)} runs; the same multiset of (block, point) as the registered {len(reg)} runs: {'yes' if same else 'NO'}; "
              f"the 'rgm136 gemmLnc' runs at {[x['n'] for x in seq if x['id'] in MOVED]} (registered at "
              f"{[x['registered_n'] for x in seq if x['id'] in MOVED]})")
        return 0 if same else 3
    # the session: the replacement, then the runner, unchanged
    C.sequence = a3_sequence
    import run_e213 as R  # noqa: E402  (the kit's runner, unchanged; it imports e213_common, the module replaced above)
    if R.C is not C or R.C.sequence is not a3_sequence:
        say_stop(["the runner did not take A3's order (its e213_common is not this process's)"])
        return 3
    print(ok_line())
    print("A3: E213's runner (tools/claims-v3/e213/run_e213.py, unchanged) runs arm B's session in A3's order; every other reading is the kit's")
    sys.stdout.flush()
    return R.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): the double of RGM211'S HOST for family G under --dry (and the
real-path desk test's stand-in host for it): E208's doubles (src/fake_card_mms.py, unchanged, imported: its toy card, its state file, its
stop file, its scenario words MMS_FAKE_*) with what rgm211's host prints beside E208's records. THE TOY CARD IS A TEST DOUBLE, NOT A FORECAST.

    fake_card_e224b.py host <rgm211's host argv...>

What it adds to E208's host double, for a gemmLnc<MB>x<NB>x<KB> arm (any other arm: refused with rgm211's host's own words, exit 1):
  - the arm read as gemmL<MB>x<NB>x<KB> by E208's double (the same ops, the toy card's same timing law), its records printed with the arm's
    own name and rgm211's walk fields: "walk": "mn", "walk_tagged": 0, "walk_ok": true on every fma launch (gemmLnc: no hart tags a launch),
    and the check record's "walk": "mn", "walk_launches_bad": 0;
  - the toy card's state names the running arm "nc<MB>x<NB>x<KB>-<type>-<kind>" (E208's double names gemmL's "<MB>x<NB>x<KB>-..."), so a desk
    test's MMS_FAKE_TRIP_ARM=nc trips a stop line in the G block alone;
  - rgm211's early refusals of a malformed arm (validateArm: "want gemmL<MB>x<NB>x<KB>", "unknown gen", "cannot read 2 x 1024 bytes"),
    before anything opens, exit 1.
The desk knobs (each names a G point by the double's arm id "nc<MB>x<NB>x<KB>-<type>-<kind>", or 'all'):
  E224B_FAKE_WALK_FAIL=<id>      every launch of that process prints walk_ok false and ok false; the check record walk_launches_bad = launches
  E224B_FAKE_CHECK_WRONG=<id>    its check record reads "wrong", ok false (exit 1, as rgm211's host on a wrong C)
  E224B_FAKE_TENSOR_ERROR=<id>   its first counted launch reads tensor_errors 3 and ok false
  E224B_FAKE_SLOW=<id>           it sleeps 12 s (real time, SIGTERM honoured) before its first launch: `timeout 10` ends it (rc 124)
(The runner's --g-extra-w W sets E208's own MMS_FAKE_TRIP=W and MMS_FAKE_TRIP_ARM=nc for the session: the toy board then gains W while a G
process runs, and only then.)
SPDX-License-Identifier: Apache-2.0
"""
import contextlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fake_card_mms as F  # noqa: E402  (E208's doubles, unchanged)


def knob(name, arm_id):
    v = os.environ.get(name) or ""
    return bool(v) and (v == "all" or v == arm_id)


def refuse(why):
    sys.stderr.write(f"error: {why}\n")
    return 1


def cmd_host(argv):
    a = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--") and not argv[i + 1].startswith("--")}
    vals = a.get("--values", "")
    try:
        arm, gen, files = vals.split(":", 2)
    except ValueError:
        return refuse(f"--values: want <arm>:<gen>:<files>, got {vals}")
    if not arm.startswith("gemmLnc"):
        return refuse(f"the E224 double of rgm211's host runs gemmLnc arms only, not {arm}")
    body = arm[len("gemmLnc"):].split("x")
    if len(body) != 3 or not all(x.isdigit() and int(x) > 0 for x in body):
        return refuse(f"--values: want gemmL<MB>x<NB>x<KB>: {arm}")
    if gen not in ("tiles", "randn", "sparse50", "sparse25", "e37"):
        return refuse(f"--values: unknown gen {gen}")
    for p in files.split(","):
        try:
            if len(open(p, "rb").read(2048)) < 2048:
                return refuse(f"cannot read 2 x 1024 bytes of tiles from {p}")
        except OSError:
            return refuse(f"cannot read 2 x 1024 bytes of tiles from {p}")
    if a.get("--per-shire") != "32":
        return refuse("gemm needs --per-shire 32: every minion of a coop group must take part")
    mb, nb, kb = (int(x) for x in body)
    kind = "rnd" if gen == "randn" else ("zeros" if files.endswith("zeros.bin") else "ones")
    shires = bin(int(a["--shires"], 16)).count("1")
    arm_id = f"nc{mb}x{nb}x{kb}-{a['--type']}-{kind}" + ("" if shires == 32 else f"-s{shires}")
    if knob("E224B_FAKE_SLOW", arm_id):
        sys.stderr.write("a test double that is slow to its first launch: 12 s (SIGTERM ends it)\n")
        sys.stderr.flush()
        time.sleep(12.0)
    # the toy card's state names the G arm apart from its cooperative twin
    w0 = F.write_state

    def ws(d):
        if isinstance(d, dict) and d.get("arm"):
            d = dict(d, arm="nc" + d["arm"])
        return w0(d)
    F.write_state = ws
    argv2 = list(argv)
    argv2[argv2.index("--values") + 1] = f"gemmL{mb}x{nb}x{kb}:{gen}:{files}"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = F.cmd_host(argv2)
    walk_fail, chk_wrong, terr = (knob("E224B_FAKE_WALK_FAIL", arm_id), knob("E224B_FAKE_CHECK_WRONG", arm_id),
                                  knob("E224B_FAKE_TENSOR_ERROR", arm_id))
    n_fma, te_done = 0, False
    for ln in buf.getvalue().splitlines():
        if not ln.startswith("SPARSITY "):
            print(ln, flush=True)
            continue
        r = json.loads(ln[9:])
        r["arm"] = arm
        if r.get("test") == "fma":
            n_fma += 1
            r.update(walk="mn", walk_tagged=0, walk_ok=not walk_fail)
            if walk_fail:
                r["ok"] = False
            if terr and not te_done and (r.get("launch") or 0) >= 0:
                r["tensor_errors"], r["ok"], te_done = 3, False, True
        elif r.get("test") == "check":
            r.update(walk="mn", walk_launches_bad=n_fma if walk_fail else 0)
            if walk_fail:
                r["ok"] = False
            if chk_wrong:
                r.update(result="wrong", ok=False, within=0, exact=0)
        print("SPARSITY " + json.dumps(r), flush=True)
    if chk_wrong or walk_fail:
        return 1
    return rc


def main(argv):
    if argv[:1] == ["host"]:
        return cmd_host(argv[1:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): step 13's check before the frozen scorer and its readings after it
(E209's rb/post_e209.py form, E209.md A1 items 2 and 3, for E216), never a verdict. Python's own modules only.

    /usr/bin/python3 -I -B tools/claims-v3/e216/rb/post_e216.py labels RANBEFORE.json
    /usr/bin/python3 -I -B tools/claims-v3/e216/rb/post_e216.py after DATA.json SCORED.json --out POST.json
    /usr/bin/python3 -I -B tools/claims-v3/e216/rb/post_e216.py --selftest

labels: every entry of "ran_before_points" names a point of points-e216.json: "LABELS OK" (exit 0); otherwise "LABELS REFUSED: ..." naming each
  entry that names nothing (exit 10): the frozen scorer echoes such a label as applied and goes on scoring the point (score_e216.py reads the
  labels as a set and never checks them). The file's other keys (step 6n's dating) are not read.
after, every figure REPORTED: NO DATA, NAMED - each point of points-e216.json that the frozen scorer leaves out of its rules, unless labelled:
  no run read (it did not run, or every run was set aside: the scorer's flags say why), runs read on route m only (no route-c reading: the
  governor held another clock or stepped inside the window), and a route-c time reading with no energy reading (capped or thin: out of E1-E4
  and the energy head-to-heads); by family (G, Gt, Y, F), with the kernel stop or the identity gate stop of the session, if any, named from
  the reducer's run flags. Nothing is decided here.
Refuses (exit 4) unless points-e216.json is at its registered sha256.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
POINTS_SHA = "63899cae4e7122cf665f9ab37d146bb209d2294669f20c89ac87dbd689753e3c"


def points():
    p = os.path.join(E, "points-e216.json")
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != POINTS_SHA:
        print("post_e216: REFUSED, points-e216.json is not at its registered sha256")
        sys.exit(4)
    return {x["id"]: x for x in json.load(open(p))["points"]}


def labels_check(path):
    P = points()
    try:
        L = json.load(open(path))
    except (OSError, ValueError) as e:
        return 10, f"LABELS REFUSED: {path} unreadable ({type(e).__name__})"
    if not isinstance(L, dict):
        return 10, "LABELS REFUSED: not a JSON object"
    v = L.get("ran_before_points", [])
    if not isinstance(v, list):
        return 10, "LABELS REFUSED: ran_before_points is not a list"
    bad = [x for x in v if x not in P]
    if bad:
        return 10, f"LABELS REFUSED: {len(bad)} entr{'y' if len(bad) == 1 else 'ies'} naming no point of points-e216.json: {bad}"
    return 0, f"LABELS OK: {len(v)} point(s) labelled ran before ({', '.join(v) or 'none'})"


def after(data_path, scored_path):
    P = points()
    S = json.load(open(scored_path))
    D = json.load(open(data_path))
    lab = set(S.get("labels_applied") or [])
    out = {"no_run": [], "route_m_only": [], "no_energy": [], "labelled": sorted(lab), "by_family": {}, "session_stop": None}
    for pid, p in P.items():
        if pid in lab:
            continue
        rec = (S.get("points") or {}).get(pid) or {}
        c = rec.get("measured_route_c")
        m = rec.get("measured_route_m_REPORTED") or {}
        fam = p["family"]
        if not c and not m:
            why = [f.get("set_aside") for f in (S.get("flags") or {}).get(pid, []) if f.get("set_aside")]
            out["no_run"].append({"id": pid, "family": fam, "why": why or ["no run in the data"]})
        elif not c:
            out["route_m_only"].append({"id": pid, "family": fam, "routes": sorted(m)})
        elif c.get("W") is None:
            out["no_energy"].append({"id": pid, "family": fam})
    for k in ("no_run", "route_m_only", "no_energy"):
        for x in out[k]:
            out["by_family"].setdefault(x["family"], {}).setdefault(k, []).append(x["id"])
    for r in D.get("runs") or []:
        for f in r.get("flags") or []:
            if "KERNEL STOP" in f or "IDENTITY GATE STOP" in f or "a stop:" in f:
                out["session_stop"] = out["session_stop"] or {"run": r.get("run"), "flag": f}
    return out


def selftest():
    import tempfile
    P = points()
    ok = n = 0
    with tempfile.TemporaryDirectory() as d:
        cases = [({"ran_before_points": ["g01", "f03"]}, 0), ({"ran_before_points": ["g1"]}, 10), ({"ran_before_points": "g01"}, 10),
                 ({"ran_before_points": []}, 0), (["g01"], 10), ({"ran_before_points": ["G01"]}, 10)]
        for i, (obj, want) in enumerate(cases):
            p = os.path.join(d, f"l{i}.json")
            json.dump(obj, open(p, "w"))
            rc, w = labels_check(p)
            n += 1
            ok += rc == want
            print(f"L{i + 1} {obj}: rc {rc} (want {want}): {w}")
        p = os.path.join(d, "bad.json")
        open(p, "w").write("{not json")
        rc, w = labels_check(p)
        n += 1
        ok += rc == 10
        print(f"L7 not JSON: rc {rc} (want 10): {w}")
        sc = {"points": {pid: {} for pid in P}, "flags": {"g07": [{"set_aside": "did not run"}]}, "labels_applied": ["f01"]}
        sc["points"]["y01a"] = {"measured_route_c": {"W": 8.0}}
        sc["points"]["y01b"] = {"measured_route_c": {"W": None}}
        sc["points"]["f02"] = {"measured_route_m_REPORTED": {"m@700.0": {}}}
        dj = {"runs": [{"run": "060-g07", "flags": ["a stop: THE KERNEL STOP (family G): runs/060-g07/proc-00: rc 1"]}]}
        sp, dp = os.path.join(d, "s.json"), os.path.join(d, "d.json")
        json.dump(sc, open(sp, "w"))
        json.dump(dj, open(dp, "w"))
        a = after(dp, sp)
        good = ({x["id"] for x in a["no_run"]} == set(P) - {"f01", "y01a", "y01b", "f02"} and [x["id"] for x in a["no_energy"]] == ["y01b"]
                and [x["id"] for x in a["route_m_only"]] == ["f02"] and a["labelled"] == ["f01"] and "KERNEL STOP" in a["session_stop"]["flag"]
                and [x for x in a["no_run"] if x["id"] == "g07"][0]["why"] == ["did not run"])
        n += 1
        ok += good
        print(f"A1 after: no run {len(a['no_run'])}, route m only {[x['id'] for x in a['route_m_only']]}, no energy "
              f"{[x['id'] for x in a['no_energy']]}, labelled {a['labelled']}, the session's stop {a['session_stop']}: {'PASS' if good else 'FAIL'}")
    print(f"SELFTEST-POST-E216 {ok} of {n} {'PASS' if ok == n else 'FAIL'}")
    return 0 if ok == n else 1


def main(argv):
    if argv[:1] == ["labels"] and len(argv) == 2:
        rc, w = labels_check(argv[1])
        print(w)
        return rc
    if argv[:1] == ["after"] and len(argv) == 5 and argv[3] == "--out":
        a = after(argv[1], argv[2])
        json.dump(a, open(argv[4], "w"), indent=1, sort_keys=True)
        print(f"NO DATA, NAMED (REPORTED): no run {[x['id'] for x in a['no_run']]}; route m only {[x['id'] for x in a['route_m_only']]}; "
              f"no energy {[x['id'] for x in a['no_energy']]}; labelled {a['labelled']}; by family {json.dumps(a['by_family'], sort_keys=True)}; "
              f"the session's stop {a['session_stop']}")
        return 0
    if argv[:1] == ["--selftest"]:
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

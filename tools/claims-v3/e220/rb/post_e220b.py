#!/usr/bin/env python3
"""E220 ARM B (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): step 13's check before the frozen scorer and its readings after it
(E216's rb/post_e216.py form, landed in 59f5288b; E209's), for E220's frozen scorer (score_e220.py --b), never a verdict. Python's own modules only.

    /usr/bin/python3 -I -B tools/claims-v3/e220/rb/post_e220b.py labels LABELS.json
    /usr/bin/python3 -I -B tools/claims-v3/e220/rb/post_e220b.py after DATA.json SCORES.json --out POST.json
    /usr/bin/python3 -I -B tools/claims-v3/e220/rb/post_e220b.py --selftest

labels: the file is the frozen scorer's --labels form for arm B, {"ran_before_points": {"B": [...]}}, and every entry names a point of arm B in
  points-e220.json: "LABELS OK" (exit 0); otherwise "LABELS REFUSED: ..." (exit 10). (Step 13 runs desk/neverrun_card_e220.py check-labels,
  the same rule; this is the readings' own copy of it.)
after, every figure REPORTED: NO DATA, NAMED - each point of arm B that the frozen scorer leaves out of its rules, unless labelled: no run read
  (it did not run, or every run was set aside: the scorer's flags say why), runs read on route m only (no route-c reading: the governor held
  another clock or stepped inside the window), and a route-c time reading with no energy reading (capped or thin: out of E1-E4 and the energy
  head-to-heads); by family (X, L3, Y2, G2, G2t), with the kernel stop or the identity gate stop of the session, if any, named from the
  reducer's run flags. Nothing is decided here.
Refuses (exit 4) unless points-e220.json is at its registered sha256.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
POINTS_SHA = "2451ca9d3763c17b2366a4c1b88e680a15a30a01a7a93e0cbf1c041d9f87bd28"


def points():
    p = os.path.join(E, "points-e220.json")
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != POINTS_SHA:
        print("post_e220b: REFUSED, points-e220.json is not at its registered sha256")
        sys.exit(4)
    return {x["id"]: x for x in json.load(open(p))["points"]["B"]}


def labels_check(path):
    P = points()
    try:
        L = json.load(open(path))
    except (OSError, ValueError) as e:
        return 10, f"LABELS REFUSED: {path} is not readable JSON ({type(e).__name__})"
    if not isinstance(L, dict) or not isinstance(L.get("ran_before_points"), dict) or set(L["ran_before_points"]) != {"B"}:
        return 10, "LABELS REFUSED: not the scorer's arm B form {\"ran_before_points\": {\"B\": [...]}}"
    v = L["ran_before_points"]["B"]
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        return 10, "LABELS REFUSED: ran_before_points > B is not a list of point ids"
    bad = [x for x in v if x not in P]
    if bad:
        return 10, f"LABELS REFUSED: {bad} name no point of arm B in points-e220.json"
    return 0, f"LABELS OK: {len(v)} point(s) labelled ran before ({', '.join(v) or 'none'})"


def after(data_path, scored_path):
    P = points()
    S = json.load(open(scored_path))
    D = json.load(open(data_path))
    B = (S.get("arms") or {}).get("B") or {}
    meas, mm, flags = B.get("measured") or {}, B.get("route_m_REPORTED") or {}, B.get("flags") or []
    lab = sorted(pid for pid, m in meas.items() if m.get("ran_before"))
    out = {"no_run": [], "route_m_only": [], "no_energy": [], "labelled": lab, "by_family": {}, "session_stop": None}
    for pid, p in P.items():
        if pid in lab:
            continue
        c, m, fam = meas.get(pid), mm.get(pid) or {}, p["family"]
        if not c and not m:
            why = [f.split(":", 1)[1].strip() for f in flags if f.startswith(f"{pid} run ")]
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
        cases = [({"ran_before_points": {"B": ["xg04", "l03"]}}, 0), ({"ran_before_points": {"B": ["xg4"]}}, 10),
                 ({"ran_before_points": {"B": "xg04"}}, 10), ({"ran_before_points": {"B": []}}, 0), (["xg04"], 10),
                 ({"ran_before_points": {"B": ["XG04"]}}, 10), ({"ran_before_points": {"A": ["xg04"]}}, 10), ({"ran_before_points": ["xg04"]}, 10)]
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
        print(f"L9 not JSON: rc {rc} (want 10): {w}")
        sc = {"arms": {"B": {"measured": {"xy01a": {"W": 8.0}, "xy01b": {"W": None}, "xf01": {"W": 9.0, "ran_before": True}},
                             "route_m_REPORTED": {"xf02": {"700.0": {}}}, "flags": ["s03 run 87: [] did not run", "xg04 run 92: [] did not run"]}}}
        dj = {"runs": [{"run": "092-xg04", "flags": ["a stop: THE KERNEL STOP (family G): runs/092-xg04/proc-00: rc 1"]}]}
        sp, dp = os.path.join(d, "s.json"), os.path.join(d, "d.json")
        json.dump(sc, open(sp, "w"))
        json.dump(dj, open(dp, "w"))
        a = after(dp, sp)
        good = ({x["id"] for x in a["no_run"]} == set(P) - {"xf01", "xy01a", "xy01b", "xf02"} and [x["id"] for x in a["no_energy"]] == ["xy01b"]
                and [x["id"] for x in a["route_m_only"]] == ["xf02"] and a["labelled"] == ["xf01"] and "KERNEL STOP" in a["session_stop"]["flag"]
                and [x for x in a["no_run"] if x["id"] == "xg04"][0]["why"] == ["[] did not run"])
        n += 1
        ok += good
        print(f"A1 after: no run {len(a['no_run'])}, route m only {[x['id'] for x in a['route_m_only']]}, no energy "
              f"{[x['id'] for x in a['no_energy']]}, labelled {a['labelled']}, the session's stop {a['session_stop']}: {'PASS' if good else 'FAIL'}")
    print(f"SELFTEST-POST-E220B {ok} of {n} {'PASS' if ok == n else 'FAIL'}")
    return 0 if ok == n else 1


def main(argv):
    if argv[:1] == ["labels"] and len(argv) == 2:
        rc, w = labels_check(argv[1])
        print(w)
        return rc
    if argv[:1] == ["after"] and len(argv) == 5 and argv[3] == "--out":
        out = after(argv[1], argv[2])
        json.dump(out, open(argv[4], "w"), indent=1, sort_keys=True)
        print(f"REPORTED: no run read {len(out['no_run'])}, route m only {len(out['route_m_only'])}, no energy {len(out['no_energy'])}, "
              f"labelled {out['labelled']}; by family {json.dumps({k: {kk: len(vv) for kk, vv in v.items()} for k, v in out['by_family'].items()})}; "
              f"the session's stop {out['session_stop']}")
        return 0
    if argv[:1] == ["--selftest"]:
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

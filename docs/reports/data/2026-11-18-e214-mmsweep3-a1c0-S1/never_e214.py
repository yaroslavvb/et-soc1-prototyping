#!/usr/bin/env python3
"""data-e214 (Q220): the never-run labels of one E214 session's arms, RE-READ at this session's data commit (E214.md section 11: "the
round's data lane re-reads them for each session against the lab's committed data at that session's commit (a configuration first
committed on its card after this file is labelled then; nothing is dropped either way)"). LABELS ONLY, REPORTED; nothing is dropped.

It starts from the registration's own labels (tools/claims-v3/e214/desk/neverrun-e214.json, the rows for this session's card and arms)
and adds what was committed on that card after the registration's index was made (its configs-e214.json, 12:47 PST Wed 18 Nov):
  (1) E214's own sessions already committed on the same card (their data folders in the lab at the commit's base: every run record of
      role arm, time or anchor that ran; the configuration of each arm from the registration's rows);
  (2) E213 arm B (aifoundry1 card 1), if its data folder is in the lab at the commit's base: the registration's rows name, for each arm,
      the arm B points with the same configuration or the same shape (e213b_planned_same_config, e213b_planned_same_shape); a point
      counts as committed when arm B's committed run records hold a run of it that ran (its data json's runs, by point id).
The re-read label: REPEAT when the configuration has a committed run on the card (the registration's or a new one); SHAPE-ONLY when only
its shape has; otherwise the registration's label (NEVER or NEVER-BY-INDEX) stands. Python's own modules only; reads only.

    /usr/bin/python3 -I -B never_e214.py <label> <registration's desk dir> <src dir> <lab data dir> --out never.json --txt never.txt
"""
import argparse
import glob
import json
import os
import sys

CARD = {"a1c1": "aifoundry1 card 1", "a1c0": "aifoundry1 card 0"}


def pid_of(x):
    """the registration names arm B's points as 'E213 k41': the point id is the last word"""
    return str(x).split()[-1] if str(x).split() else str(x)


def key(r):
    return (r["token"], r["fmt"], r["data"], r["mask"])


def ran_arms_e214(d):
    """arm names with a run that ran (roles arm, time, anchor) in a committed E214 session folder"""
    out = set()
    for p in glob.glob(os.path.join(d, "session", "runs", "*", "run.json")):
        r = json.load(open(p))
        if r.get("ran") and r.get("role") in ("arm", "time", "anchor"):
            out.add(r["arm"])
    return out


def e213b_ran_points(data_dir):
    """point ids of E213 arm B with a run that ran (every process rc 0), read from its committed reduction data-e213.json
    (arms -> <arm> -> points -> <point id> -> runs, each run's rcs in its 'detail')"""
    pts = set()
    for p in glob.glob(os.path.join(data_dir, "data-e213*.json")):
        try:
            d = json.load(open(p))
        except ValueError:
            continue
        for arm in (d.get("arms") or {}).values() if isinstance(d, dict) else []:
            for pid, pv in ((arm or {}).get("points") or {}).items():
                for r in (pv or {}).get("runs") or []:
                    rcs = r.get("rcs") or (r.get("detail") or {}).get("rcs") or []
                    if rcs and all(x == 0 for x in rcs):
                        pts.add(str(pid))
                        break
    return pts


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("desk")
    ap.add_argument("src")
    ap.add_argument("labdata")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    card_code, sess = a.label.split("-")
    card = CARD[card_code]
    nr = json.load(open(os.path.join(a.desk, "neverrun-e214.json")))
    rows = {(r["arm"], r["card"]): r for r in nr["rows"]}
    sched = json.load(open(os.path.join(a.src, "sched", a.label + ".json")))
    arms = []
    for r in sched["runs"]:
        if r.get("role") in ("arm", "time", "anchor") and r["arm"] not in arms:
            arms.append(r["arm"])
    # (1) E214's own committed sessions on this card (not this one)
    mine = {}
    for d in sorted(glob.glob(os.path.join(a.labdata, f"*-e214-mmsweep3-{card_code}-S*"))):
        lab = d.rsplit("-e214-mmsweep3-", 1)[1]
        if lab == a.label:
            continue
        for arm in ran_arms_e214(d):
            rr = rows.get((arm, card))
            if rr:
                mine.setdefault(key(rr), set()).add(f"E214 {lab}")
    mine_shapes = {}
    for k, v in mine.items():
        mine_shapes.setdefault(k[0], set()).update(v)
    # (2) E213 arm B on card 1
    b_dirs = sorted(d for d in glob.glob(os.path.join(a.labdata, "*-e213-*")) if "aifoundry1" in d)
    b_pts = set()
    for d in b_dirs:
        b_pts |= e213b_ran_points(d)
    out_rows, changed = [], []
    tally = {}
    for arm in arms:
        rr = rows.get((arm, card))
        if rr is None:
            out_rows.append({"arm": arm, "card": card, "registered": "NO ROW", "now": "NO ROW"})
            continue
        reg = rr["label"]
        why = []
        now = reg
        k = key(rr)
        if k in mine:
            why.append("configuration committed by " + ", ".join(sorted(mine[k])))
        b_same = [p for p in (rr.get("e213b_planned_same_config") or []) if pid_of(p) in b_pts] if card_code == "a1c1" else []
        b_shape = [p for p in (rr.get("e213b_planned_same_shape") or []) if pid_of(p) in b_pts] if card_code == "a1c1" else []
        if b_same:
            why.append("configuration committed by E213 arm B " + ", ".join(pid_of(x) for x in b_same))
        if (k in mine or b_same) and reg != "REPEAT":
            now = "REPEAT"
        elif reg in ("NEVER", "NEVER-BY-INDEX"):
            sh = sorted(mine_shapes.get(k[0], set()) - mine.get(k, set()))
            if sh:
                why.append(f"shape {k[0]} committed by " + ", ".join(sh))
            if b_shape:
                why.append(f"shape {k[0]} committed by E213 arm B " + ", ".join(pid_of(x) for x in b_shape))
            if sh or b_shape:
                now = "SHAPE-ONLY"
        row = {"arm": arm, "card": card, "token": k[0], "fmt": k[1], "data": k[2], "mask": k[3], "registered": reg, "now": now,
               "why": why}
        out_rows.append(row)
        tally[now] = tally.get(now, 0) + 1
        if now != reg:
            changed.append(row)
    res = {"what": "data-e214's re-read of E214's never-run labels for one session at its data commit (E214.md section 11; labels only, "
                   "REPORTED, nothing dropped)", "session": a.label, "card": card, "arms": len(arms), "tally_now": tally,
           "changed": len(changed), "e214_sessions_committed_on_card": sorted({s for v in mine.values() for s in v}),
           "e213_armB_data_dirs": [os.path.basename(d) for d in b_dirs], "e213_armB_points_ran": len(b_pts),
           "registration_labels_sha256": nr.get("configs_sha256"), "rows": out_rows,
           "python": sys.version.split()[0], "interpreter": sys.executable}
    json.dump(res, open(a.out, "w"), indent=1)
    L = [f"N never-run labels re-read for {a.label} ({card}): {len(arms)} arms; now {dict(sorted(tally.items()))}; changed from the "
         f"registration's labels: {len(changed)}; E214 sessions committed on the card before this one: "
         f"{res['e214_sessions_committed_on_card'] or 'none'}; E213 arm B data folders: {res['e213_armB_data_dirs'] or 'none'} "
         f"({len(b_pts)} points ran)"]
    for r in changed[:40]:
        L.append(f"  {r['arm']}: {r['registered']} -> {r['now']} ({'; '.join(r['why'])})")
    open(a.txt, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

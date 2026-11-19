#!/usr/bin/env python3
"""E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): THE NEVER-RUN SEARCH REPEATED right before E216's first card command
(runbook step 6n), and its judgement. E216.md section 4: "Every E216 point's token, and every G point's twin's, passes (point_rule_e216.py
applied it to every candidate; the land lane's and the kit's step 6n re-read it at their HEAD)". E215's step-6n form (desk/neverrun_card_e215.py:
the registration's own scanner and rule, then the judgement by each point's own reading, every counted file dated against the freeze line).
Standard library here; the scan reads MM1-v3's and MM1-v3.1's measured points through their data loaders (numpy through them).

    /usr/bin/python3 -I -B tools/claims-v3/e216/desk/neverrun_card_e216.py run DIR --lab LAB --lanes OUT
        writes DIR/scan-e216-card.json, DIR/neverrun-e216-card.json and .txt, DIR/ranbefore-e216.json (the scorer's --labels form, always
        written, its list empty when nothing ran before); its last line "NEVER-RUN-E216: ..."

THE SCAN: E213's scanner (tools/claims-v3/e213/desk/neverrun_e213.py at its pin d603ff8b..., loaded by the registration's own
desk/neverrun_e216.py e213_module(), that file at its registered sha256 88fea667...): its token rule, roots (every committed data folder of the
lab, E212's and E208's committed schedules), folder classes and reader, over the lab at HEAD and the round's card and data lane folders, plus
MM1-v3's and MM1-v3.1's measured points; the registration's rule (desk/neverrun_e216.ran_on_a2, unchanged): a token ran on aifoundry2 card 0
when a file COUNTED for that card holds it (a folder naming aifoundry2 or a2c0, or naming no card) or a measured point of either model holds it
on that card. THE LANE VIEW is the registration's: card-, data-, a1, a2 and a3 lanes, leaving out by name (never opened) every lane whose name
holds 'e216' (E216's own records: the card lane's box root, dry passes and copies would name every E216 token) and every lane whose name holds
'e215' (E215's arms ran on aifoundry3 card 0 and aifoundry1 card 1 by their bookings, and E215's kit refuses any other box; the registration's
scan left them out too, by Q227's rule). E216'S ONE DEPARTURE FROM THE REGISTRATION'S SCAN (stated before any E216 datum): the registration's
scan refuses a lab that holds an E215 data folder (no E215 datum before E216's freeze); this one refuses it only while the lab's history
holds no E216 registration commit (the commit that added tools/claims-v3/e216/E216.md), and after that commit reads E215's committed data
like any other (its folders name aifoundry3 and aifoundry1-c1: E213's classes never count them for aifoundry2 card 0).
THE JUDGEMENT (the kit's reading, stated before any E216 datum): a point is judged by ITS OWN token and, for a G point, its cooperative twin's
token too (the registration's G rule). For a token the scan reads as ran on this card, every file that holds it under the scanner's own
rules and is counted for this card is listed again (the same roots and classes) with its date - a lab file by the commit that added it
(git log --diff-filter=A, its committer time), a lane file by its modification time - and every measured point of either model on this card
is evidence of a run by construction (committed before the models' lands). A point is labelled 'ran before' on EVIDENCE OF A RUN ON THIS CARD
dated before E216's FREEZE LINE (the registration commit's committer time), or undated: a measured point; a committed lab file counted for
this card (a data folder naming aifoundry2 or a2c0, or naming no card); a lane file counted for this card BY NAME (its folder names
aifoundry2 or a2c0); or a lane file in a folder naming no card that is a SESSION RECORD by its name (queue.json, run.json, status.json,
session.log, smoke.json, telemetry.jsonl[.gz], launches.jsonl[.gz], proc*.out, proc*.err, data-*.json, reduce-*.txt). A lane file counted
only because its folder names no card and that is not a session record (an arm list, a schedule copy, a plan, a desk scan) is REPORTED with
its file and dates and never labels a point by itself (E216's kit, Thu 19 Nov 2026 11:4x PST, before any E216 datum: the kit's own desk run
of this step found the model session's E217 plan copy W/out/data-e217/work/src/arms.json, copied into the round's folders at 11:20 PST
after the registration's scan, naming gemmL1x8x24 (y08's token) for its aifoundry1 sessions; verify-e209's finding 9 on such hits). A point
whose every counted file is dated after the freeze line is REPORTED ('ran after') and kept. REPORTED, never a gate: the card lane writes a
dated note before the data commit when any point is labelled, and passes ranbefore-e216.json to the scorer at step 13 (rb/post_e216.py labels
checks it first).
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REG_SCANNER = ("tools/claims-v3/e216/desk/neverrun_e216.py", "88fea667ea033f034bd8b2c29bfd446c77a3cd456a8dc791c244ed24dd3e4f95")
POINTS_SHA = "63899cae4e7122cf665f9ab37d146bb209d2294669f20c89ac87dbd689753e3c"
A2 = "aifoundry2 card 0"
LANE_PREFIXES = ("card-", "data-", "a1", "a2", "a3")
SESSION_RECORD = re.compile(r"^(queue\.json|run\.json|status\.json|session\.log|smoke\.json|telemetry\.jsonl(\.gz)?|launches\.jsonl(\.gz)?|"
                            r"proc[^/]*\.(out|err)|data-[^/]*\.json|reduce-[^/]*\.txt)$")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def git(lab, *a):
    r = subprocess.run(["git", "-C", lab] + list(a), capture_output=True, text=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    return r.returncode, r.stdout.strip()


def load_reg(lab):
    p = os.path.join(lab, REG_SCANNER[0])
    if sha(p) != REG_SCANNER[1]:
        print("neverrun_card_e216: REFUSED, the registration's scanner is not at its registered sha256")
        sys.exit(4)
    spec = importlib.util.spec_from_file_location("neverrun_e216", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def freeze(lab):
    rc, out = git(lab, "log", "--diff-filter=A", "--format=%H %ct", "--", "tools/claims-v3/e216/E216.md")
    rows = [ln.split() for ln in out.splitlines() if ln.strip()]
    if rc != 0 or not rows:
        return None, None
    h, ct = rows[-1]
    return h, int(ct)


def run(d, lab, lanes):
    t0 = now()
    os.makedirs(d, exist_ok=True)
    pts = os.path.join(E, "points-e216.json")
    if sha(pts) != POINTS_SHA:
        print("neverrun_card_e216: REFUSED, points-e216.json is not at its registered sha256")
        return 4
    P = json.load(open(pts))["points"]
    reg_c, f_ct = freeze(lab)
    if reg_c is None:
        print("neverrun_card_e216: REFUSED, the lab's history holds no E216 registration commit (no freeze line to date against)")
        return 10
    e215_data = [x for x in sorted(os.listdir(os.path.join(lab, "docs", "reports", "data"))) if "e215" in x.lower()]
    rc, pushed = git(lab, "branch", "-r", "--contains", reg_c)
    on_main = rc == 0 and any(b.strip() in ("origin/main", "origin/HEAD -> origin/main") for b in pushed.splitlines())
    if e215_data and not on_main:
        print(f"neverrun_card_e216: REFUSED, the lab holds an E215 data folder {e215_data[:2]} and E216's registration {reg_c[:12]} is not on "
              "GitHub's main (no E215 datum before E216's freeze)")
        return 5
    R = load_reg(lab)
    E213 = R.e213_module(lab)
    view = os.path.join(d, "lane-view")
    if os.path.isdir(view):
        shutil.rmtree(view)
    os.makedirs(view)
    kept, left_out = [], []
    for x in sorted(os.listdir(lanes)):
        if not x.startswith(LANE_PREFIXES):
            continue
        if "e215" in x.lower() or "e216" in x.lower():
            left_out.append(x)
            continue
        os.symlink(os.path.join(lanes, x), os.path.join(view, x))
        kept.append(x)
    E213.scan(lab, view, d)
    S = json.load(open(os.path.join(d, "scan-e213.json")))
    os.remove(os.path.join(d, "scan-e213.json"))
    v31 = os.path.join(lab, "tools", "matmul", "mm1", "v3.1")
    sys.path.insert(0, v31)
    import data_v31 as DV  # noqa: E402
    m31 = {}
    for p in DV.time_points():
        m31.setdefault(p["arm"], set()).add((p.get("kernel"), p["card"], "time"))
    for e in DV.energy_points():
        m31.setdefault(e["arm"], set()).add((e.get("kernel"), e["card"], "energy"))
    S["mm1_v31_measured_points"] = {t: sorted(f"{k} on {c} ({w})" for k, c, w in v) for t, v in sorted(m31.items())}
    S.update({"what": "E216's step-6n scan (the registration's scan form; E216's own lanes and E215's card lanes left out by name)",
              "lanes_read": kept, "lanes_left_out_never_opened": left_out, "lab_e215_data_folders": e215_data,
              "registration_commit": reg_c, "registration_on_main": on_main, "started_e216": t0})
    json.dump(S, open(os.path.join(d, "scan-e216-card.json"), "w"), indent=1, sort_keys=True)
    # the judgement
    expmap = E213.exp_cards(lab)
    want = {}
    for p in P:
        toks = [p["arm"]] + ([x["arm"] for x in P if x["id"] == p.get("twin")] if p["family"] == "G" else [])
        want[p["id"]] = toks
    ran_toks = {t for ts in want.values() for t in ts if R.ran_on_a2(S, t)}
    files = {t: [] for t in ran_toks}
    if ran_toks:
        rx = E213.RX
        roots = [os.path.join(lab, "docs", "reports", "data"), os.path.join(lab, "tools", "claims-v3", "e212", "proposal", "src", "sched"),
                 os.path.join(lab, "tools", "claims-v3", "e208", "proposal", "src")]
        lane_roots = sorted(os.path.join(view, x) for x in kept)
        for top in roots + lane_roots:
            for dp, dn, fns in os.walk(top):
                if ".git" in dn or ".git" in fns:
                    dn[:] = []
                    continue
                for fn in sorted(fns):
                    p = os.path.join(dp, fn)
                    if fn.endswith(E213.SKIP_EXT) or os.path.islink(p):
                        continue
                    try:
                        if os.path.getsize(p) > E213.MAX_BYTES:
                            continue
                        found = set(rx.findall(E213.read_text(p))) & ran_toks
                    except (OSError, EOFError):
                        continue
                    if not found:
                        continue
                    if p.startswith(lab + os.sep):
                        rel, kind = os.path.relpath(p, lab), "lab"
                    else:
                        rel, kind = "W/out/" + os.path.relpath(p, view), "lane"
                    c = E213.lane_card(rel) or E213.folder_card(rel, expmap) or E213.NONE
                    if c not in (A2, E213.NONE):
                        continue
                    if kind == "lab":
                        rc, out = git(lab, "log", "--diff-filter=A", "--format=%ct", "-1", "--", rel)
                        when = int(out) if rc == 0 and out.isdigit() else None
                    else:
                        when = int(os.path.getmtime(p))
                    record = kind == "lab" or c == A2 or bool(SESSION_RECORD.match(fn))
                    for t in found:
                        files[t].append({"file": rel, "class": c, "epoch": when, "evidence_of_a_run": record,
                                         "ctime": int(os.stat(p).st_ctime) if kind == "lane" else None})
    rows, labels, after = [], [], []
    for p in P:
        ev, why_before, plans = [], [], []
        for t in want[p["id"]]:
            if t not in ran_toks:
                continue
            for x in R.ran_on_a2(S, t):
                if "measured point" in x:
                    why_before.append(f"{t}: {x}")
            for f in files.get(t, []):
                ev.append(dict(f, token=t))
                if f["evidence_of_a_run"] and (f["epoch"] is None or f["epoch"] < f_ct):
                    why_before.append(f"{t}: {f['file']} ({f['class']}, {'undated' if f['epoch'] is None else datetime.datetime.fromtimestamp(f['epoch']).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')})")
                elif not f["evidence_of_a_run"]:
                    plans.append(f"{t}: {f['file']} ({f['class']}; not a session record: REPORTED)")
            if t in ran_toks and not files.get(t) and not [x for x in R.ran_on_a2(S, t) if "measured point" in x]:
                why_before.append(f"{t}: the scan counts it but no file was found again")
        runs_ev = [f for f in ev if f["evidence_of_a_run"]]
        if not any(t in ran_toks for t in want[p["id"]]):
            verdict = "never ran"
        elif why_before:
            verdict = "ran before"
        elif runs_ev:
            verdict = "ran after (REPORTED)"
        else:
            verdict = "never ran (hits REPORTED: no session record)"
        if verdict == "ran before":
            labels.append(p["id"])
        elif verdict.startswith("ran after"):
            after.append(p["id"])
        rows.append({"id": p["id"], "family": p["family"], "tokens": want[p["id"]], "verdict": verdict, "why_before": why_before[:8],
                     "not_records_REPORTED": plans[:8], "files_counted": ev[:12]})
    freeze_s = datetime.datetime.fromtimestamp(f_ct).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    rep = {"what": "E216's never-run search repeated (step 6n), judged by each point's own reading", "started": t0, "ended": now(),
           "freeze_line": {"commit": reg_c, "committer_time": freeze_s, "on_github_main": on_main}, "points": rows,
           "never_ran": [r["id"] for r in rows if r["verdict"].startswith("never ran")],
           "hits_not_records_REPORTED": [r["id"] for r in rows if r["verdict"].startswith("never ran (hits")], "ran_before": labels,
           "ran_after_REPORTED": after,
           "lanes_left_out_never_opened": left_out, "files_read": S.get("files_read"), "interpreter": "/usr/bin/python3 " + sys.version.split()[0]}
    shutil.rmtree(view)
    json.dump(rep, open(os.path.join(d, "neverrun-e216-card.json"), "w"), indent=1, sort_keys=True)
    json.dump({"ran_before_points": labels, "after_freeze_REPORTED": after, "freeze_line": reg_c}, open(os.path.join(d, "ranbefore-e216.json"), "w"),
              indent=1, sort_keys=True)
    line = (f"NEVER-RUN-E216: {len(rep['never_ran'])} of {len(P)} points never ran on aifoundry2 card 0 (their own tokens, a G point's twin's too; "
            f"{len(rep['hits_not_records_REPORTED'])} of them with hits that are no session record, REPORTED: {rep['hits_not_records_REPORTED'] or 'none'}); "
            f"ran before the freeze line {reg_c[:12]} ({freeze_s}): {labels or 'none'}; ran after (REPORTED): {after or 'none'}; "
            f"{S.get('files_read')} files read, lanes left out {left_out}")
    with open(os.path.join(d, "neverrun-e216-card.txt"), "w") as f:
        for r in rows:
            f.write(f"{r['id']} {r['family']} {' '.join(r['tokens'])}: {r['verdict']}" + (f" ({'; '.join(r['why_before'][:3])})" if r["why_before"] else "")
                    + (f" [REPORTED: {'; '.join(r['not_records_REPORTED'][:3])}]" if r["not_records_REPORTED"] else "") + "\n")
        f.write(line + "\n")
    print(line)
    return 0


def main(argv):
    if len(argv) == 6 and argv[0] == "run" and argv[2] == "--lab" and argv[4] == "--lanes":
        return run(os.path.abspath(argv[1]), os.path.abspath(argv[3]), os.path.abspath(argv[5]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

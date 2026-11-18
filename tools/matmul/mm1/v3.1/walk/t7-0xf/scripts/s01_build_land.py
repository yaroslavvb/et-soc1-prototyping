#!/usr/bin/env python3
"""t7-0xf (Q221) s01: build the land dir OUT/t7-0xf/land/tools/matmul/mm1/v3.1/walk/ (new files only) from v31-trace's walk and traces,
verify-v31trace's run u1 and scripts, and this lane's run u2 and scripts, with every home path and login scrubbed, and record the old and
new sha256 of every rewritten file beside the frozen predictions (unchanged bytes). Desk; standard library; /usr/bin/python3 3.12.3.

THE SCRUB (the lab's convention, as land-v31prep's counts land: the box's paths replaced by placeholders):
  the round's work folder W -> <W>; the lab clone LAB -> <LAB>; the home directory -> ~; then any remaining bare login (the owner and group
  columns of `ls -l` output in run logs) -> <login>. Text files: byte-level replacement. summary.json.gz and mine.json.gz: the same
  replacement inside the decompressed JSON text, re-gzipped deterministically (mtime 0, level 9), and the parsed JSON checked equal to the
  original's parse with the same replacement applied to every string. Two Python files get a code change, not a text replacement:
  walk/test_walk_v31.py (LAB from ET_LAB or this file's place in the lab; mm-timing's counted run read from walk/testdata/, a byte copy) and
  walk/layout_table_v31.py (LAB the same way). walk/walk_predictions.json.sha256 is rewritten with a bare file name.
  The frozen walk/walk_predictions.json is copied byte for byte and checked: 10f2f3da...
Refuses if the land dir already exists. Writes SCRUB.json (the record) into the land dir and prints a summary.
    /usr/bin/python3 -I -B s01_build_land.py
"""
import gzip
import hashlib
import json
import os
import shutil
import sys

W = "<W>"
LAB = "<LAB>"
HOME = os.path.expanduser("~")
LOGIN = os.path.basename(HOME)
OUT = W + "/out"
V = OUT + "/v31-trace"
VV = OUT + "/verify-v31trace"
L = OUT + "/t7-0xf"
LAND = L + "/land/tools/matmul/mm1/v3.1/walk"
FROZEN = "10f2f3da0dd543a088830edb67584713e5b66b986faae1d1c0327d041bc2bf57"
SUBS = [(W, "<W>"), (LAB, "<LAB>"), (HOME, "~")]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def scrub_text(t):
    n = {}
    for a, b in SUBS:
        n[b] = t.count(a)
        t = t.replace(a, b)
    n["<login>"] = t.count(LOGIN)
    t = t.replace(LOGIN, "<login>")
    return t, {k: v for k, v in n.items() if v}


def scrub_obj(o):
    if isinstance(o, str):
        return scrub_text(o)[0]
    if isinstance(o, list):
        return [scrub_obj(x) for x in o]
    if isinstance(o, dict):
        return {scrub_text(k)[0]: scrub_obj(v) for k, v in o.items()}
    return o


CODE_EDITS = {
    "walk/test_walk_v31.py": [
        ('LAB = "<LAB>"\n'
         'OUT = os.path.normpath(os.path.join(HERE, "..", ".."))\n'
         'MMT = os.path.join(OUT, "mm-timing", "work", "a3", "counted", "c-gemmL1x1x1-fp32", "counts-log.json")\n',
         '# t7-0xf (Q221) scrub: the lab checkout is read from the environment variable ET_LAB, else found from this file\'s place in it\n'
         '# (tools/matmul/mm1/v3.1/walk/walk/); mm-timing\'s counted simulator run (c-gemmL1x1x1-fp32, aifoundry3) is read from its byte copy in\n'
         '# testdata/ beside this file. Nothing else in this file changed.\n'
         'LAB = os.environ.get("ET_LAB") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))\n'
         'MMT = os.path.join(HERE, "testdata", "counts-log-c-gemmL1x1x1-fp32.json")\n'),
    ],
    "walk/layout_table_v31.py": [
        ('LAB = "<LAB>"\n',
         '# t7-0xf (Q221) scrub: the lab checkout from ET_LAB, else from this file\'s place in it (tools/matmul/mm1/v3.1/walk/walk/).\n'
         'LAB = os.environ.get("ET_LAB") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))\n'),
    ],
}


def plan():
    P = []   # (source, land path, mode)
    for f in ["walk_v31.py", "predict_v31.py", "walk_predictions.json", "walk_predictions_final.json", "layout_table_v31.json",
              "levels_runs_v31.py", "levels_runs_v31.json"]:
        P.append((V + "/walk/" + f, "walk/" + f, "frozen" if f == "walk_predictions.json" else "text"))
    # walk/README.md: v31-trace's README rewritten by this lane (the trace verifier's findings 3-5; the log paths); the top README is new
    P.append((L + "/work/docs/walk-README.md", "walk/README.md", "doc:" + V + "/walk/README.md"))
    P.append((L + "/work/docs/README.md", "README.md", "text"))
    P.append((V + "/walk/test_walk_v31.py", "walk/test_walk_v31.py", "code"))
    P.append((V + "/walk/layout_table_v31.py", "walk/layout_table_v31.py", "code"))
    P.append((V + "/walk/walk_predictions.json.sha256", "walk/walk_predictions.json.sha256", "sha256file"))
    P.append((OUT + "/mm-timing/work/a3/counted/c-gemmL1x1x1-fp32/counts-log.json", "walk/testdata/counts-log-c-gemmL1x1x1-fp32.json", "text"))
    for f in ["trace_run.py", "check_v31.py", "make_fake_log.py", "traced_numbers.py", "collect_checks.py", "make_plan.py", "plan.json",
              "README.md", "check_summary.json", "check_summary.md", "frozen_vs_traced.json", "a3_send.sh", "a3_fetch.sh", "wait_a3.sh",
              "prep_payload.sh", "run_chain.sh", "r_prep.sh", "r_update.sh", "r_trace.sh", "r_peek.sh", "r_peek2.sh", "r_final_look.sh",
              "r_rm_errlog_t1.sh"]:
        P.append((V + "/traces/" + f, "traces/" + f, "text"))
    for d in sorted(os.listdir(V + "/traces/runs")):
        for f in sorted(os.listdir(V + "/traces/runs/" + d)):
            P.append((V + "/traces/runs/%s/%s" % (d, f), "traces/runs/%s/%s" % (d, f), "gzjson" if f.endswith(".json.gz") else "text"))
    for f in ["summary.json.gz", "mine.json.gz", "check_v31.json", "out.json", "RUN.txt", "sandbox-check.txt", "err.log"]:
        P.append((VV + "/work/u1/" + f, "traces/runs/u1/" + f, "gzjson" if f.endswith(".json.gz") else "text"))
    P.append((VV + "/work/v04_u1.json", "traces/runs/u1/v04_u1.json", "text"))
    P.append((VV + "/work/v06_u1.json", "traces/runs/u1/v06_u1.json", "text"))
    for f in ["summary.json.gz", "mine.json.gz", "check_v31.json", "out.json", "RUN.txt", "sandbox-check.txt", "err.log"]:
        P.append((L + "/work/u2/" + f, "traces/runs/u2/" + f, "gzjson" if f.endswith(".json.gz") else "text"))
    P.append((L + "/work/v04_u2.json", "traces/runs/u2/v04_u2.json", "text"))
    P.append((L + "/work/v06_u2.json", "traces/runs/u2/v06_u2.json", "text"))
    P.append((L + "/work/u2.SHA256SUMS.fetched", "traces/runs/u2/SHA256SUMS.as-fetched", "text"))
    for f in sorted(os.listdir(V + "/scripts")):
        P.append((V + "/scripts/" + f, "scripts/" + f, "text"))
    for f in sorted(os.listdir(V + "/logs")):
        P.append((V + "/logs/" + f, "logs/" + f, "text"))
    for f in ["a3.sh", "r_prep.sh", "r_look1.sh", "r_run.sh", "r_rm_excerpts.sh", "vt_run.py", "fake_host.py", "wait_for.sh",
              "v01_read_checks.py", "v02_strays.py", "v03_rerun_walk_tests.sh", "v04_independent.py", "v04_run.sh",
              "v05_desk_test_runner.sh", "v06_rawparse.py", "v07_posthoc.py", "v07_run.sh", "v08_fetch.sh", "v09_check_u1.sh",
              "v10_negative_controls.py"]:
        P.append((VV + "/scripts/" + f, "verify-v31trace/scripts/" + f, "text"))
    for f in ["v01_checks.json", "v02_strays.txt", "v04_independent.json", "v07_posthoc.json", "v10_negative_controls.json"]:
        P.append((VV + "/work/" + f, "verify-v31trace/work/" + f, "text"))
    for f in ["progress.txt", "u1.out", "v03_repredict.log", "v03_walk_tests.log", "v09_check_v31_u1.out"]:
        P.append((VV + "/logs/" + f, "verify-v31trace/logs/" + f, "text"))
    for f in sorted(os.listdir(L + "/scripts")):
        # vt_run.py and fake_host.py are verify-v31trace's, byte for byte (landed under verify-v31trace/scripts/); the public-text
        # scanner and its runner hold the scan's own word lists (the lab's land lanes never land their scanners)
        if (f.endswith(".py") or f.endswith(".sh")) and f not in ("vt_run.py", "fake_host.py", "public_scan_walk.py", "s06_scan.sh",
                                                                 "s02_scrub_scan.py", "c05_bigjson_scan.py"):
            P.append((L + "/scripts/" + f, "t7-0xf/scripts/" + f, "text"))
    # r_look1.log (the read-only look before the run) is not landed: its `ls -l` of the sandbox binary names the system owner; its facts are
    # in the README and the lane's result
    for f in ["u2.out", "r_prep.log", "f01_fetch.log", "r_rm_excerpts.log", "d01_desk_test.log", "c01.log",
              "c01_check_v31_u2.out", "s03_recheck_1.log", "s03_recheck_2.log", "s03_recheck_3.log", "s03_recheck_4.log",
              "s03_recheck_5.log", "s03_recheck_6.log", "s03_recheck_7.log"]:
        P.append((L + "/logs/" + f, "t7-0xf/logs/" + f, "text"))
    P.append((L + "/work/criteria/runs-orig.json", "t7-0xf/work/runs-orig.json", "text"))
    P.append((L + "/work/criteria/criteria-orig.json", "t7-0xf/work/criteria-orig.json", "text"))
    # the check re-run on the land (s03, s04, c04): outputs; the 10 re-check JSONs are byte-equal to the original checks (remade-compare.json)
    # and the re-made predictions and layout table are recorded by hash (predict-compare.json, remade-compare.json), so neither is copied
    R = L + "/work/recheck"
    for f in sorted(os.listdir(R)):
        if (f.startswith("check-") and f.endswith(".out")) or f in (
                "compare-checks.json", "remade-compare.json", "predict-compare.json", "criteria-land.json", "runs-land.json", "pairs.json",
                "t7_v31_check.json", "t7_v31_check.out", "v04_all10.json", "walk_tests_land.log", "predict_land.log", "layout_land.log"):
            P.append((R + "/" + f, "t7-0xf/work/" + f, "text"))
    return P


def main():
    if os.path.exists(L + "/land"):
        print("land dir exists: " + L + "/land (not rebuilding over it)")
        return 8
    rec = {"what": "t7-0xf (Q221): the scrub record of the land dir tools/matmul/mm1/v3.1/walk/: every file copied, its source (lane and "
                   "file, paths shown with the placeholders), and for every file whose bytes changed the old and new sha256",
           "placeholders": {"<W>": "the round's work folder on aifoundry2", "<LAB>": "the lab clone on aifoundry2", "~": "the home directory",
                            "<login>": "the box's login (in ls -l owner and group columns)"},
           "frozen": None, "rewritten": [], "copied_unchanged": 0, "python": sys.version.split()[0]}
    for src, dst, mode in plan():
        out = os.path.join(LAND, dst)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        b = open(src, "rb").read()
        label = scrub_text(src)[0]
        if mode == "frozen":
            assert sha(b) == FROZEN, "frozen predictions hash differs"
            open(out, "wb").write(b)
            rec["frozen"] = {"land": dst, "source": label, "old_sha256": sha(b), "new_sha256": sha(open(out, "rb").read()),
                             "unchanged_bytes": sha(open(out, "rb").read()) == FROZEN, "made_pst": json.loads(b)["made_pst"]}
            continue
        if mode.startswith("doc:"):
            old = open(mode[4:], "rb").read()
            t2, n = scrub_text(b.decode("utf-8"))
            assert not n, (dst, n)
            nb = t2.encode("utf-8")
            open(out, "wb").write(nb)
            rec["rewritten"].append({"land": dst, "source": scrub_text(mode[4:])[0], "kind": "document rewritten by t7-0xf (the trace "
                                     "verifier's findings: distinct tiles per shire-step with its caveat, the tallies per pair, the three "
                                     "model limits; log paths; the check's verdict)", "old_sha256": sha(old), "new_sha256": sha(nb)})
            continue
        if mode == "sha256file":
            nb = (FROZEN + "  walk_predictions.json\n").encode()
            assert b.decode().split()[0] == FROZEN
            open(out, "wb").write(nb)
            rec["rewritten"].append({"land": dst, "source": label, "kind": "sha256 line with a bare file name", "old_sha256": sha(b),
                                     "new_sha256": sha(nb), "substitutions": {"path -> bare name": 1}})
            continue
        if mode == "code":
            t = b.decode()
            for a, c in CODE_EDITS[dst]:
                assert t.count(a) == 1, (dst, a[:40])
                t = t.replace(a, c)
            t2, n = scrub_text(t)
            assert not n, (dst, n)
            nb = t2.encode()
            open(out, "wb").write(nb)
            rec["rewritten"].append({"land": dst, "source": label, "kind": "code change (LAB/OUT constants)", "old_sha256": sha(b),
                                     "new_sha256": sha(nb), "edits": len(CODE_EDITS[dst])})
            continue
        if mode == "gzjson":
            raw = gzip.decompress(b)
            t = raw.decode("utf-8")
            t2, n = scrub_text(t)
            if not n:
                open(out, "wb").write(b)
                rec["copied_unchanged"] += 1
                continue
            assert json.loads(t2) == scrub_obj(json.loads(t)), dst
            nraw = t2.encode("utf-8")
            nb = gzip.compress(nraw, compresslevel=9, mtime=0)
            open(out, "wb").write(nb)
            rec["rewritten"].append({"land": dst, "source": label, "kind": "gzip JSON, strings scrubbed, re-gzipped (mtime 0)",
                                     "old_sha256": sha(b), "new_sha256": sha(nb), "old_json_sha256": sha(raw), "new_json_sha256": sha(nraw),
                                     "json_equal_after_scrub": True, "substitutions": n})
            continue
        # text
        try:
            t = b.decode("utf-8")
        except UnicodeDecodeError:
            t = None
        if t is None:
            assert LOGIN.encode() not in b and HOME.encode() not in b, dst
            open(out, "wb").write(b)
            rec["copied_unchanged"] += 1
            continue
        t2, n = scrub_text(t)
        nb = t2.encode("utf-8")
        open(out, "wb").write(nb)
        if n:
            rec["rewritten"].append({"land": dst, "source": label, "kind": "text, paths and logins scrubbed", "old_sha256": sha(b),
                                     "new_sha256": sha(nb), "substitutions": n})
        else:
            rec["copied_unchanged"] += 1
    json.dump(rec, open(os.path.join(LAND, "SCRUB.json"), "w"), indent=1)
    n_files = sum(len(fs) for _, _, fs in os.walk(LAND))
    print("land %s: %d files; rewritten %d; copied unchanged %d; frozen %s unchanged %s" % (
        scrub_text(LAND)[0], n_files, len(rec["rewritten"]), rec["copied_unchanged"], rec["frozen"]["new_sha256"][:16],
        rec["frozen"]["unchanged_bytes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E151 reduction (Q139; a port of E145's reduce_e145.py): E78's registered reduction, tools/claims-v3/kinds/reduce_e78.py, run UNCHANGED
on E151's blocks (aifoundry3 card 0), with E151's items installed on the shared e78_common module (e151_common.install(): E78's 51 kinds
and the tie plus Q136(a)'s 26 tiles), so that the per-run gates (600 MHz, the voltage band, the records, cycles per op, the window's
samples and duty, the dumped tile equal to the item's registered sha256) and every per-run quantity (p_raw, p80, rail_raw, the rate)
are E78's own. E130's blocks are trains with no anchors and no tie, so E78's anchor and tie pass gates have nothing to act on; its
failed-run and configuration gates still apply (aifoundry3's reads, TDP 0 W / threshold 65 C, are the ones E78's gate accepts: E145's
card-1 substitution is not needed here and is dropped). The step over each item's OWN zero and every rule are score_e151.py's, from
the per-run table this writes (--csv). Each arm registered in README.md before any E151 data:

  --drop-dips     the board-meter dips removed from the telemetry before the reduction reads it, E82 amendment A2's definition,
                  board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W (E145's primary had it, as E138's did).
  --rail-filter   E151's registered minion-rail filter (railfilter_e151.py: F1, the rail more than 4.0 W above both samples two steps
                  away; F2, the rail equal to the running maximum the sample reports), whole samples removed.
  E151's REGISTERED PRIMARY is --drop-dips --rail-filter: both rules read the block's telemetry as the sampler wrote it, and the union
  of the samples they mark is removed (E145's post-hoc arm did exactly this with F1 alone). The labelled arms: dips only (the rail
  filter off: E145's registered primary form), the filter with the dips kept, and the pass gates opened.
  --gates-off     E78's five pass gates opened in memory (every per-run gate stays), to show what the set-aside moved; the
                  labelled gates-off arm (with score_e151.py's train gate off too).

    python3 tools/claims-v3/e151/reduce_e151.py <pass dir> ... --out e151.json [--drop-dips] [--rail-filter] [--gates-off]
        [--csv] [--txt] [--leak auto|<k>] [--tau 0.95] [--delay 0.2] [--c-rb 0.81] [--no-refit]   (every reduce_e78.py option)

Before it runs it checks reduce_e78.py, e78_common.py and kinds.json against predictions-e151.json (E78's freeze values) and Q136(a)'s
tile manifest against its frozen sha256, and refuses on any difference. After reduce_e78 writes --out, its "experiment" becomes "E151"
and a "reducer" block records the code, the hashes, the arm and every sample each rule removed; the --txt file gets a header line.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
REG = os.path.join(HERE, "predictions-e151.json")
DIP_W = 4.0


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def dips(rows):
    """E82 A2: sample i when board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W. Returns the set of indices."""
    B = [r.get("board_w") for r in rows]
    bad = set()
    for i in range(2, len(rows) - 2):
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    return bad


def main():
    reg = json.load(open(REG))
    want = reg["harness"]["card_code_unchanged_sha256"]
    bad = []
    for rel in ("tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py",
                "tools/claims-v3/kinds/kinds.json"):
        have = sha(os.path.join(ROOT, rel))
        if have != want[rel]:
            bad.append(f"{rel}: sha256 {have} != registered {want[rel]}")
    for rel in ("tools/claims-v3/e151/railfilter_e151.py", "tools/claims-v3/e151/e151_common.py"):
        w = reg["harness"]["e151_card_files_sha256"].get(rel)
        have = sha(os.path.join(ROOT, rel))
        if have != w:
            bad.append(f"{rel}: sha256 {have} != registered {w}")
    import e151_common as e130  # noqa: E402
    import railfilter_e151 as rf  # noqa: E402
    e = e130.check_frozen()
    if e:
        bad.append(e)
    if bad:
        raise SystemExit("refusing to reduce - the reused E78 code, the rail filter or Q136(a)'s tile manifest changed:\n  " + "\n  ".join(bad))
    flags = {}
    for f in ("--drop-dips", "--rail-filter", "--gates-off"):
        flags[f] = f in sys.argv
        if flags[f]:
            sys.argv.remove(f)
    e130.install()
    import reduce_e78 as r  # noqa: E402  (after the check and the install; tools/claims-v3/kinds is on the path)
    if flags["--gates-off"]:
        r.GATES.update({"pass_max_failed_runs": 10 ** 6, "zero_mid_departure_w": 1e9, "zero_range_w": 1e9,
                        "tie_drift_w": 1e9, "random_range_w": 1e9})
    removed = {}
    if flags["--drop-dips"] or flags["--rail-filter"]:
        orig_load = r.load_jsonl

        def load_jsonl(path):
            rows = orig_load(path)
            if os.path.basename(path).startswith("telemetry.jsonl"):
                d = dips(rows) if flags["--drop-dips"] else set()
                fl = rf.flags(rows) if flags["--rail-filter"] else {"F1": set(), "F2": set(), "union": set()}
                gone = d | fl["union"]
                removed[os.path.basename(os.path.dirname(path))] = {
                    "samples": len(rows), "board_dips": len(d), "rail_F1": len(fl["F1"]), "rail_F2": len(fl["F2"]),
                    "rail_union": len(fl["union"]), "removed": len(gone),
                    "rail_t_ms": [rows[i].get("t_ms") for i in sorted(fl["union"])][:200],
                    "dip_t_ms": [rows[i].get("t_ms") for i in sorted(d)][:200]}
                rows = [x for i, x in enumerate(rows) if i not in gone]
            return rows

        r.load_jsonl = load_jsonl
    raw_reads = {}
    orig_rop = r.runs_of_pass

    def runs_of_pass(d, by, a):
        out, meta = orig_rop(d, by, a)
        if meta:
            p = out[0]["pass"] if out else os.path.basename(d.rstrip("/"))
            raw_reads[str(p)] = {nm: meta.get(nm) for nm in ("config_start", "config_end")}
        return out, meta

    r.runs_of_pass = runs_of_pass
    out_path = txt_path = None
    for i, x in enumerate(sys.argv):
        if x == "--out" and i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]
        if x == "--txt" and i + 1 < len(sys.argv):
            txt_path = sys.argv[i + 1]
    r.main()
    parts = [w for f, w in (("--drop-dips", "dips removed (E82 A2)"), ("--rail-filter", "rail glitches removed (E151's filter)"),
                            ("--gates-off", "pass gates opened")) if flags[f]]
    arm = " + ".join(parts)
    if out_path and os.path.exists(out_path):
        res = json.load(open(out_path))
        res["experiment"] = "E151"
        res["reducer"] = {
            "code": "tools/claims-v3/kinds/reduce_e78.py (E78's registered reduction, unchanged) via tools/claims-v3/e151/reduce_e151.py",
            "reduce_e78_sha256": sha(os.path.join(e130.KINDS, "reduce_e78.py")),
            "e78_common_sha256": sha(os.path.join(e130.KINDS, "e78_common.py")),
            "kinds_json_sha256": sha(os.path.join(e130.KINDS, "kinds.json")),
            "e130_items_json_sha256": sha(e130.ITEMS_JSON),
            "e151_common_sha256": sha(os.path.join(HERE, "e151_common.py")),
            "railfilter_sha256": sha(os.path.join(HERE, "railfilter_e151.py")),
            "wrapper_sha256": sha(os.path.abspath(__file__)),
            "items": "e78_common.load_items returns E78's items plus Q136(a)'s 26 tiles (e151_common.install)",
            "config_gate": "E78's own (it accepts aifoundry3's TDP 0 W, threshold 65 C); no substitution",
            "config_reads_raw": raw_reads,
            "arm": arm or "nothing removed",
            "pass_gates": "opened (the labelled gates-off arm)" if flags["--gates-off"] else "E78's, unchanged",
            "dips": "removed (E82 A2's definition)" if flags["--drop-dips"] else "kept",
            "rail_filter": "on (railfilter_e151.py: F1 or F2)" if flags["--rail-filter"] else "off",
            "samples_removed": removed,
        }
        json.dump(res, open(out_path, "w"), indent=1, default=lambda o: None)
    if txt_path and os.path.exists(txt_path):
        body = open(txt_path).read()
        open(txt_path, "w").write(f"E151: reduce_e78.py unchanged via reduce_e151.py (E151's items; {arm or 'nothing removed'})\n" + body)


if __name__ == "__main__":
    main()

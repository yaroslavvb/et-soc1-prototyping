#!/usr/bin/env python3
"""E199 (Q190, lane reg-e199): the core-rail glitch filter applied before E192's registered reducer (E199.md section 6.5), written
and tested before any card-1 X01 datum. Standard library only.

WHY. On aifoundry1 card 1 the minion rail's reading (`sp.minion_w[0]`) now and then returns the service processor's running maximum
for one or two samples (E145; docs/findings/14-card-behaviour.md: "Register a rail-spike filter on this card before the data"). One
such sample inside a run's rail window moves that run's rail power by about 1 W, which is several pJ an instruction at E192's rates.
E192's reducer (`reduce_intbits.py`, registered at 715fddaa..., run unchanged) has a board-dip rule and no rail rule.

THE RULE IS E151's, UNCHANGED: `tools/claims-v3/e151/railfilter_e151.py` (sha256 87bffb5f..., imported only at that sha256): a sample
is a rail glitch when F1 its rail reading is more than 4.0 W above both samples two steps away, or F2 it equals the running maximum the
same sample reports (`sp.minion_w[0] == sp.minion_w[2]`). A glitch sample's telemetry line is removed whole (its board reading too)
before the reducer reads the telemetry, as E151's registered primary does. The rule reads only the telemetry samples, in the order the
sampler wrote them: never a run, an arm, a price or a result.

WHAT THIS SCRIPT DOES. It writes a copy of a session's run directory for the reducer: `runs.jsonl` and `marks.jsonl` copied byte for
byte, and `telemetry.jsonl` with every glitch sample's line left out and every other line copied byte for byte (lines that are not
JSON objects are copied as they are: the reducer skips them). It writes `railfilter-e199.json` beside them: the census (samples,
F1, F2, union, the removed samples' times and readings). On aifoundry3's E192 session it removes nothing (desk/pipeline-e192.txt), so
the same pipeline re-makes `intbits-e192.json` byte for byte: the forecast is what this pipeline gives on aifoundry3's data.

    /usr/bin/python3 -I -B tools/claims-v3/e199/prefilter_e199.py <run dir: runs.jsonl, marks.jsonl, telemetry.jsonl[.gz]> <out dir>

SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RAILFILTER = os.path.join(TOP, "tools/claims-v3/e151/railfilter_e151.py")
RAILFILTER_SHA = "87bffb5fdc762c5ed21f023dee2812768bde241f3075424012a0909cc00840d4"


def load_rule():
    with open(RAILFILTER, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != RAILFILTER_SHA:
        raise SystemExit("REFUSED: railfilter_e151.py at %s, not its registered %s" % (got, RAILFILTER_SHA))
    spec = importlib.util.spec_from_file_location("railfilter_e151_pinned", RAILFILTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_lines(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rb") as f:
        return f.read().split(b"\n")


def filter_lines(raw_lines, rule):
    """(kept raw lines, census): rows are the lines that start with '{' and parse, in order, as railfilter_e151.load() reads them."""
    rows, idx = [], []
    for i, b in enumerate(raw_lines):
        s = b.decode("utf-8", errors="replace")
        if s.startswith("{"):
            try:
                rows.append(json.loads(s))
                idx.append(i)
            except ValueError:
                pass
    fl = rule.flags(rows)
    drop = {idx[j] for j in fl["union"]}
    kept = [b for i, b in enumerate(raw_lines) if i not in drop]
    removed = [{"t_ms": rows[j].get("t_ms"), "rail_w": rows[j]["sp"]["minion_w"][0],
                "running_max_w": (rows[j]["sp"]["minion_w"][2] if len(rows[j]["sp"]["minion_w"]) > 2 else None),
                "board_w": rows[j].get("board_w"), "F1": j in fl["F1"], "F2": j in fl["F2"]} for j in sorted(fl["union"])]
    maxes = sorted({r["sp"]["minion_w"][2] for r in rows if isinstance(r.get("sp"), dict)
                    and isinstance(r["sp"].get("minion_w"), list) and len(r["sp"]["minion_w"]) > 2})
    census = {"rule": "E151's railfilter_e151.py at 87bffb5f..., unchanged: F1 rail > max(rail[i-2], rail[i+2]) + 4.0 W; "
                      "F2 rail == sp.minion_w[2]; a glitch is F1 or F2; its line removed whole",
              "lines": len(raw_lines), "samples": len(rows), "F1": len(fl["F1"]), "F2": len(fl["F2"]), "union": len(fl["union"]),
              "removed": removed, "running_max_field_w": maxes[-5:]}
    return kept, census


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: prefilter_e199.py <run dir> <out dir>")
    src, dst = sys.argv[1], sys.argv[2]
    rule = load_rule()
    tel = os.path.join(src, "telemetry.jsonl")
    if not os.path.exists(tel) and os.path.exists(tel + ".gz"):
        tel = tel + ".gz"
    for need in (os.path.join(src, "runs.jsonl"), os.path.join(src, "marks.jsonl"), tel):
        if not os.path.exists(need):
            raise SystemExit("REFUSED: missing %s" % need)
    if os.path.exists(dst) and os.listdir(dst):
        raise SystemExit("REFUSED: %s exists and is not empty" % dst)
    os.makedirs(dst, exist_ok=True)
    shutil.copyfile(os.path.join(src, "runs.jsonl"), os.path.join(dst, "runs.jsonl"))
    shutil.copyfile(os.path.join(src, "marks.jsonl"), os.path.join(dst, "marks.jsonl"))
    kept, census = filter_lines(read_lines(tel), rule)
    with open(os.path.join(dst, "telemetry.jsonl"), "wb") as f:
        f.write(b"\n".join(kept))
    census["input"] = os.path.basename(tel)
    with open(os.path.join(dst, "railfilter-e199.json"), "w") as f:
        f.write(json.dumps(census, indent=1) + "\n")
    print("PREFILTER-E199: %d samples, %d removed (F1 %d, F2 %d); running-maximum field %s" % (
        census["samples"], census["union"], census["F1"], census["F2"], census["running_max_field_w"]))


if __name__ == "__main__":
    main()

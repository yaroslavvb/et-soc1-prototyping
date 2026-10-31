#!/usr/bin/env python3
"""E85, the thermal camera's view of different kinds of numbers: the session runner.

    python3 run_hlk.py --protocol protocol-e85.json --out <RUNDIR> [--dry] [--list] ...

This is E63's runner, `run_hlc.py` (tools/claims-v3/hlc), IMPORTED AND RUN UNCHANGED, with one
addition made here and nowhere else:

  * a set may carry its own "type" ("fp32", "fp16" or "int8"), which becomes the heater's --type for
    that set's launches.  E63 ran fp32 only, so its runner takes --type from the protocol's heater
    section for every launch; E85 switches each kind against ITS OWN TYPE'S zeros, so an fp16 or
    int8 set must launch with --type fp16 / int8.

How: `Session._spawn_heater` is wrapped.  For the one call that launches a set, the heater's "type"
is set to that set's type, the original method runs, and the heater's type is put back.  The set is
identified by its "values" string (the operand file), so every set's values must name exactly one
type: the wrapper refuses a protocol where one values string appears under two types, or a type
outside fp32 / fp16 / int8.  Every launch's full command line, --type included, is already recorded
by run_hlc.py in launches.jsonl ("cmd"), and run_hlc.py hashes every .py and .json beside it into
session.json, so this file's sha256 is in the session record too.

Everything else - the card lock, the other-user checks before the session and between launches,
`timeout 10` on every device process, the sampler, the camera recorder, the safety stops, the
pad-to-dwell grid - is run_hlc.py's code, byte for byte.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# the staged copy (build/e85/code) keeps run_hlc.py beside this file; the repo keeps it in ../hlc
for p in (HERE, os.path.join(HERE, "..", "hlc")):
    if os.path.exists(os.path.join(p, "run_hlc.py")):
        sys.path.insert(0, os.path.abspath(p))
        break
import run_hlc as R  # noqa: E402

TYPES = ("fp32", "fp16", "int8")


def type_map(raw):
    """{values string: type} for every non-idle set that names a type; a list of problems."""
    out, problems = {}, []
    default = ((raw.get("heater") or {}).get("type")) or "fp32"
    for name, s in (raw.get("sets") or {}).items():
        if not isinstance(s, dict) or s.get("idle") or s.get("values") is None:
            continue
        t = s.get("type", default)
        if t not in TYPES:
            problems.append(f"set {name}: type {t!r} is not one of {', '.join(TYPES)}")
            continue
        v = str(s["values"]).strip()
        if v in out and out[v] != t:
            problems.append(f"set {name}: values {v!r} already runs as {out[v]}, not {t}")
            continue
        out[v] = t
    return out, problems


def install(tmap):
    """Wrap Session._spawn_heater so a launch of a set runs with that set's --type (once only)."""
    if getattr(R.Session._spawn_heater, "_hlk", False):
        return
    orig = R.Session._spawn_heater

    def spawn_with_type(self, mask, per_shire, values=None):
        v = (values or self.proto.heater["values"]).strip()
        t = tmap.get(v, self.proto.heater["type"])
        before = self.proto.heater["type"]
        self.proto.heater["type"] = t
        try:
            return orig(self, mask, per_shire, values)
        finally:
            self.proto.heater["type"] = before

    spawn_with_type._hlk = True
    R.Session._spawn_heater = spawn_with_type


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    proto_path = None
    for i, a in enumerate(argv):
        if a == "--protocol" and i + 1 < len(argv):
            proto_path = argv[i + 1]
        elif a.startswith("--protocol="):
            proto_path = a.split("=", 1)[1]
    if proto_path is None:
        print("--protocol is required", file=sys.stderr)
        return R.EXIT_REFUSE
    try:
        with open(proto_path) as f:
            raw = json.load(f)
    except (OSError, ValueError) as e:
        print(f"protocol {proto_path}: {e}", file=sys.stderr)
        return R.EXIT_REFUSE
    tmap, problems = type_map(raw)
    if problems:
        print("protocol refused (run_hlk.py):", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return R.EXIT_REFUSE

    install(tmap)
    if "--list" in argv:
        for v, t in sorted(tmap.items(), key=lambda kv: kv[0]):
            print(f"  type {t:4s}  {v}")
    return R.main(argv)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Q141(t2), fix pass of Wed 4 Nov 2026 (README.md.dated-note.md beside this file): B1 restated with its evidence.

B1 as committed compared Verilator's own record of the files each build read (obj_vpu/Vtb__verFiles.dat, copied into
build-record-intel.json and build-record-mini.json as verilator_files_read). That record holds 156 entries, but only 155 carry a
content hash: Verilator writes "unhashed" for its own binary, verilator_bin, on both builds. So the record shows 155 content-hashed
inputs identical, and nothing about the two Verilator binaries, which are different builds of 5.052 (one per machine).

This script adds the other half of the check: the C++ model Verilator generated. Each build's obj_vpu/*.cpp and *.h are hashed raw
and again with the build's own directory prefixes replaced by fixed markers (the generated code embeds the RTL's absolute paths), so
two builds made in different directories can be compared. It also reads each build's Vtb__verFiles.dat: entries, content hashes,
and the size of every unhashed entry. Output holds file names, hashes and counts only, never a machine path.

    python3 -B check_b1_generated.py hash <obj_vpu dir> <prefix>=<marker> [<prefix>=<marker> ...] > <build>.json
    python3 -B check_b1_generated.py compare <intel.json> <mini.json> > check-b1-generated.json

Prefixes are replaced longest first. The markers used here: the core-et tree -> @CE@, the bench directory -> @B@.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import platform
import re
import sys

sys.dont_write_bytecode = True
ABS = tuple(b"/" + d + b"/" for d in (b"Users", b"tmp", b"private", b"home", b"var/folders"))  # absolute-path prefixes left


def hash_build(obj, subs):
    subs = sorted(subs, key=lambda s: -len(s[0]))
    files = {}
    for f in sorted(os.listdir(obj)):
        if not f.endswith((".cpp", ".h")):
            continue
        raw = open(os.path.join(obj, f), "rb").read()
        norm = raw
        for a, t in subs:
            norm = norm.replace(a, t)
        files[f] = {"raw_sha256": hashlib.sha256(raw).hexdigest(), "norm_sha256": hashlib.sha256(norm).hexdigest(),
                    "raw_has_abs_path": any(p in raw for p in ABS), "abs_paths_left": sum(norm.count(p) for p in ABS)}
    ver = {"entries": 0, "content_hashed": 0, "unhashed": []}
    for line in open(os.path.join(obj, "Vtb__verFiles.dat"), encoding="utf-8", errors="replace"):
        if not line.startswith("S "):
            continue
        ver["entries"] += 1
        q = re.findall(r'"([^"]*)"', line)
        size = int(line.split()[1])
        if q and q[0] == "unhashed":
            name = q[1] if len(q) > 1 else line.split()[-1]
            ver["unhashed"].append({"name": os.path.basename(name.strip('"')), "size_bytes": size})
        elif q and re.fullmatch(r"[A-Za-z0-9+/=_-]{40}", q[0]):
            ver["content_hashed"] += 1
    return {"machine": {"arch": platform.machine(), "system": platform.system()}, "markers": sorted({t.decode() for _, t in subs}),
            "n_files": len(files), "files": files, "verilator_files_read": ver}


def compare(a, b):
    na, nb = set(a["files"]), set(b["files"])
    both = sorted(na & nb)
    raw_same = [f for f in both if a["files"][f]["raw_sha256"] == b["files"][f]["raw_sha256"]]
    norm_same = [f for f in both if a["files"][f]["norm_sha256"] == b["files"][f]["norm_sha256"]]
    return {
        "_note": "Q141(t2) fix pass, Wed 4 Nov 2026: B1's generated-model check (check_b1_generated.py); names, hashes and counts only",
        "builds": {"intel": a["machine"], "mini": b["machine"]},
        "n_files": {"intel": a["n_files"], "mini": b["n_files"]},
        "same_file_names": na == nb,
        "raw_identical": len(raw_same),
        "identical_after_prefix_markers": len(norm_same),
        "differ_raw_only_in_prefixes": sorted(set(norm_same) - set(raw_same)),
        "differ_after_prefix_markers": sorted(set(both) - set(norm_same)),
        "abs_paths_left_after_markers": {"intel": sum(v["abs_paths_left"] for v in a["files"].values()),
                                        "mini": sum(v["abs_paths_left"] for v in b["files"].values())},
        "raw_files_with_abs_paths": {"intel": sum(v["raw_has_abs_path"] for v in a["files"].values()),
                                     "mini": sum(v["raw_has_abs_path"] for v in b["files"].values())},
        "markers": {"intel": a["markers"], "mini": b["markers"]},
        "verilator_files_read": {"intel": a["verilator_files_read"], "mini": b["verilator_files_read"]},
        "per_build": {"intel": a["files"], "mini": b["files"]},
    }


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "hash":
        subs = []
        for s in sys.argv[3:]:
            p, t = s.rsplit("=", 1)
            subs.append((p.encode(), t.encode()))
        print(json.dumps(hash_build(sys.argv[2], subs), indent=1, sort_keys=True))
    elif len(sys.argv) == 4 and sys.argv[1] == "compare":
        print(json.dumps(compare(json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))), indent=1, sort_keys=True))
    else:
        sys.exit(__doc__)

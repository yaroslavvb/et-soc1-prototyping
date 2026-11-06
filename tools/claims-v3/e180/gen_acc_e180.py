#!/usr/bin/env python3
"""E180's two accumulating modes for the energy catalogue: c += v on eight read-write chains (Q146(f)).

    python3 tools/claims-v3/e180/gen_acc_e180.py --src workloads/enercat --dst build/enercat-e180-src
    python3 tools/claims-v3/e180/gen_acc_e180.py --src workloads/enercat --print      # the appended text only
    cmake -B build/enercat-e180 -S build/enercat-e180-src -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/enercat-e180 -j4

It copies the committed workloads/enercat (nothing there is edited: the repo's rule is new files only) into a build
tree and appends two generated modes after gen_ops.py's last one, in gen_ops.py's own form (its case(), run() and
emit_vec text), so every existing mode keeps its id and its code text:

    261  fadd.ps.acc   fxor.pi f(8+i), f0, f0 (c = 0, once a launch), then RUN(8 x "fadd.ps f(8+i), f(8+i), f(i)")
    262  fadd.pi.acc   the same with fadd.pi

The block reads and writes f8..f15 (the accumulators) and reads f0..f7 (the image, loaded by load_vsrc as for every
vector mode); it rewrites no source and reads no other sink, so the one change from the plain mode is that each op's
destination is also its first source. A launch (one kernel run, --window cycles) starts every chain at 0.
The host's table (enercat_modes.h, enercat_modes.json) gains the two entries; EC_GEN_COUNT becomes 163.
The catalogue's own build trees (build/enercat, build/enercat_v2) and every committed file are untouched.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

VSINK = '"f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"'
MODES = [("fadd.ps.acc", "fadd.ps"), ("fadd.pi.acc", "fadd.pi")]
NOTE = "8-lane vector, c += v on eight chains (E180)"


def case_text(mid, name, op):
    zero = "\\n".join(f"fxor.pi f{8 + i}, f0, f0" for i in range(8))
    body = "\\n".join(f"{op} f{8 + i}, f{8 + i}, f{i}" for i in range(8))
    return (f"    case {mid}: /* {name} */\n"
            f"        load_vsrc(src);\n"
            f"        __asm__ __volatile__(\"{zero}\" : : : {VSINK});\n"
            f"        RUN(do {{ uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;\n"
            f"            __asm__ __volatile__(\"{body}\" :  :  : {VSINK}); }} while (0));\n"
            f"        break;\n")


def appended(src):
    modes = json.load(open(os.path.join(src, "enercat_modes.json")))
    first = 100 + len(modes)
    new = [{"name": n, "mode": first + i, "ops_per_iter": 64, "unit": "instruction", "hart0_only": False, "note": NOTE}
           for i, (n, _op) in enumerate(MODES)]
    inc = "".join(case_text(first + i, n, op) for i, (n, op) in enumerate(MODES))
    return modes, new, inc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the committed workloads/enercat")
    ap.add_argument("--dst", help="the build tree to write (created; must not exist or be an earlier gen_acc_e180 tree)")
    ap.add_argument("--print", action="store_true")
    a = ap.parse_args()
    modes, new, inc = appended(a.src)
    if a.print or not a.dst:
        sys.stdout.write(inc)
        return
    if os.path.exists(a.dst):
        if not os.path.exists(os.path.join(a.dst, "E180-ACC-MODES.json")):
            raise SystemExit(f"{a.dst} exists and is not a gen_acc_e180 tree: refusing to overwrite it")
        shutil.rmtree(a.dst)
    shutil.copytree(a.src, a.dst, ignore=shutil.ignore_patterns("build", "__pycache__", "*.pyc"))
    with open(os.path.join(a.dst, "kernel", "enercat_ops.inc"), "a") as f:
        f.write(inc)
    allm = modes + new
    hdr_path = os.path.join(a.dst, "enercat_modes.h")
    hdr = open(hdr_path).read()
    old_count = f"#define EC_GEN_COUNT {len(modes)}"
    if old_count not in hdr or "};\n#endif" not in hdr:
        raise SystemExit("enercat_modes.h is not in gen_ops.py's form")
    hdr = hdr.replace(old_count, f"#define EC_GEN_COUNT {len(allm)}")
    rows = "".join(f'  {{"{m["name"]}", {m["mode"]}, {m["ops_per_iter"]}, "{m["unit"]}", false, "{m["note"]}"}},\n' for m in new)
    hdr = hdr.replace("};\n#endif", rows + "};\n#endif")
    open(hdr_path, "w").write(hdr)
    json.dump(allm, open(os.path.join(a.dst, "enercat_modes.json"), "w"), indent=1)
    files = {}
    for root, _dirs, fs in os.walk(a.dst):
        for fn in sorted(fs):
            p = os.path.join(root, fn)
            files[os.path.relpath(p, a.dst)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    json.dump({"src": a.src, "new_modes": new, "appended_inc_sha256": hashlib.sha256(inc.encode()).hexdigest(),
               "files": dict(sorted(files.items()))}, open(os.path.join(a.dst, "E180-ACC-MODES.json"), "w"), indent=1)
    print(f"{a.dst}: {len(modes)} catalogue modes kept, {len(new)} appended ({new[0]['mode']}-{new[-1]['mode']})")


if __name__ == "__main__":
    main()

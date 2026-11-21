#!/usr/bin/env bash
# E223 (reg-e223, Q239): the desk checks of the registered source, run on the committed copy (no device, no simulator; it writes
# nothing but its standard output). E221's desk_checks_e221.sh (itself E219's, E217's, E214's, E212's and E208's), with this sweep's
# files: gemmL arms only (part 10's block-arm line prints only if there are block arms), part 9 against the fourth, fifth and sixth
# sweeps' K (E217's, E219's and E221's committed arms.json), and part 13: the masks and the post's planning claims, per card, with
# the arms the plan tags L3R or L3R2 beside E221's L3served. From the repository's top:
#   bash tools/claims-v3/e223/desk/desk_checks_e223.sh tools/claims-v3/e223/proposal . > out.txt 2>&1
# $1 is the kit root holding src/ (the proposal copy); $2 the lab tree whose committed files the copied ones are compared with.
#   1. sha256sum -c src/SRC-SHA256SUMS (every file the model session listed, at its sha256), and the list's own sha256
#   2. src/check_mms.py --check (the list re-made in memory equals the file: CHECK PASS)
#   3. src/make_schedule2.py --check: it re-makes arms.json and the schedules from the plan (plan.json, "in the request's folder,
#      beside src/"), which did not reach the lab: with no plan it prints MAKE CHECK FAIL (src/ holds what a plan made). The lab's
#      re-make without the plan is desk/remake_e223.py (desk/remake-e223.txt).
#   4. src/mms_common.py (its self-check, the arm grammar's cases among them) and 5. src/mms_ident.py (its self-check)
#   6. src/tiles_gen.py --check (no plan: this sweep designs no tiles)
#   7. the lab's device-command audit (tools/claims-v3/dmcmd_audit.py with its table) on the ten files src/preflight_mms.sh names,
#      no --allow: it must read GO, every send site a READ
#   8. the 23 files src/README.md says are copied from the lab, against the lab's committed files, sha256 by sha256; and that
#      src/tiles holds the lab's nine kind files alone (no plan tile)
#   9. the gemmL arms past the first sweep's largest K (fp32 16,384, fp16 8,192, int8 32,768, make_schedule2.py's FIRST_SWEEP_K) and
#      past the fourth, fifth and sixth sweeps' (E217's, E219's and E221's committed arms.json) largest K a type
#  10. THE ARM GRAMMAR, read independently of src/mms_common.py arm_of: every arm's --values string parsed by the rules of rgm136's
#      host as the lab reads them in src/rgm136/host/main.cpp (parseArm's prefix order tenb, mmp, mm, gemmnc, gemmc, gemmv, gemmh,
#      gemmL, gemm; gemmTail's r<R> then s; testArm's ops a pass, calibration passes and check launch) and the block constants of
#      src/rgm136/sparsity_args.h, against the arm's record in arms.json (ops a minion a pass, M x N x K, footprint, first and check
#      passes) and against arm_of; that no arm is gemmnc, gemmv, mmp or the plain fma test; every block, stream and TenB arm on the
#      whole chip and on the lab's kinds; B and R at most 32, N at most 256; tenb's gen tiles; and the host's own lines the kit's
#      desk tests name (selftest_mms.py HOST_LINES) standing in main.cpp in that order
#  11. the pair check: no plan tile, so nothing to pair (arms.json's "tiles" is empty)
#  12. the host rules the README names: the build's one job (build_mms.sh) and the preflight's NO-GO at a one-minute load of 6 or
#      more (preflight_mms.sh), as lines of code, with the lines that show the runner's own preflight call is --audit-only, which
#      returns before the load is read
#  13. the masks (each arm's shires mask: its shire count, the id's -s<n> / -m<hex> suffix by the README's rule) and the post's
#      planning claims as the schedules hold them, per card: the highest planned run and smoke against 66.6 W (card 1, aifoundry2
#      card 0) and 52 W (card 0) and the card's planning line; no run in the time role on aifoundry2; the fp random runs on
#      aifoundry2 and the arms the plan tags L3served (E221's tag) or L3R / L3R2 (this sweep's)
# Python: /usr/bin/python3 -I -B (3.12.3 on aifoundry2 when first run). SPDX-License-Identifier: Apache-2.0
set -u
K=$(cd "${1:?the kit root holding src/}" && pwd)
LAB=$(cd "${2:?the lab tree}" && pwd)
PY=${PY:-/usr/bin/python3}
cd "$K" || exit 3
echo "# E223 desk checks on the registered source (run $(TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'))"
echo "# interpreter: $PY $($PY -c 'import sys; print(sys.version.split()[0])') -I -B; no device opened, no simulator"
echo
echo "## 1. sha256sum -c src/SRC-SHA256SUMS"
n_ok=$(sha256sum -c src/SRC-SHA256SUMS 2>&1 | grep -c ': OK$'); n_all=$(grep -c . src/SRC-SHA256SUMS)
echo "OK $n_ok of $n_all listed files; files in src/: $(find src -type f | wc -l) (the list and the $n_all it names)"
echo "sha256 of src/SRC-SHA256SUMS: $(sha256sum src/SRC-SHA256SUMS | cut -c1-64)"
echo
echo "## 2. src/check_mms.py --check"
$PY -I -B src/check_mms.py --check; echo "rc $?"
echo
echo "## 3. src/make_schedule2.py --check (plan.json beside src/: $( [ -e plan.json ] && echo present || echo absent))"
$PY -I -B src/make_schedule2.py --check | cut -c1-160; echo "rc ${PIPESTATUS[0]}"
echo
echo "## 4. src/mms_common.py (self-check)"
$PY -I -B src/mms_common.py; echo "rc $?"
echo
echo "## 5. src/mms_ident.py (self-check)"
$PY -I -B src/mms_ident.py; echo "rc $?"
echo
echo "## 6. src/tiles_gen.py --check (plan.json beside src/: $( [ -e plan.json ] && echo present || echo absent))"
$PY -I -B src/tiles_gen.py --check | cut -c1-160; echo "rc ${PIPESTATUS[0]}"
echo
echo "## 7. the lab's device-command audit on the session's files"
echo "audit tool: tools/claims-v3/dmcmd_audit.py, sha256 $(sha256sum "$LAB/tools/claims-v3/dmcmd_audit.py" | cut -c1-64); src/dmcmd/dmcmd_audit.py $(sha256sum src/dmcmd/dmcmd_audit.py | cut -c1-64)"
$PY -I -B "$LAB/tools/claims-v3/dmcmd_audit.py" src/run_mms.py src/mms_common.py src/mms_ident.py src/session_mms.sh src/start_mms.sh \
  src/status_mms.sh src/stop_mms.sh src/build_mms.sh src/guard_ettelem.sh src/rgm136/host/main.cpp 2>&1
echo "rc ${PIPESTATUS[0]}"
echo
echo "## 8. the copied files against the lab's committed files (the mapping of src/README.md); src/tiles holds the lab's nine alone"
same=0; n=0
while read -r here there; do
  n=$((n + 1))
  a=$(sha256sum "src/$here" | cut -c1-64)
  if [ -f "$LAB/$there" ]; then b=$(sha256sum "$LAB/$there" | cut -c1-64); else b=MISSING; fi
  if [ "$a" = "$b" ]; then v=EQUAL; same=$((same + 1)); else v="DIFFERENT (lab $b)"; fi
  echo "$v $a src/$here = $there"
done <<'EOF'
rgm136/CMakeLists.txt tools/claims-v3/e136/rgm136/CMakeLists.txt
rgm136/README.md tools/claims-v3/e136/rgm136/README.md
rgm136/sparsity_args.h tools/claims-v3/e136/rgm136/sparsity_args.h
rgm136/host/CMakeLists.txt tools/claims-v3/e136/rgm136/host/CMakeLists.txt
rgm136/host/Constants.h.in tools/claims-v3/e136/rgm136/host/Constants.h.in
rgm136/host/main.cpp tools/claims-v3/e136/rgm136/host/main.cpp
rgm136/kernel/CMakeLists.txt tools/claims-v3/e136/rgm136/kernel/CMakeLists.txt
rgm136/kernel/crt.S tools/claims-v3/e136/rgm136/kernel/crt.S
rgm136/kernel/sections.ld tools/claims-v3/e136/rgm136/kernel/sections.ld
rgm136/kernel/sparsity.c tools/claims-v3/e136/rgm136/kernel/sparsity.c
ettelem/ettelem.cpp tools/ettelem/ettelem.cpp
ettelem/CMakeLists.txt tools/ettelem/CMakeLists.txt
dmcmd/dmcmd_audit.py tools/claims-v3/dmcmd_audit.py
dmcmd/dmcmd_table.json tools/claims-v3/dmcmd_table.json
tiles/fp32/randn.bin tools/claims-v3/kinds/tiles/fp32/randn.bin
tiles/fp32/zeros.bin tools/claims-v3/kinds/tiles/fp32/zeros.bin
tiles/fp32/ones.bin tools/claims-v3/kinds/tiles/fp32/ones.bin
tiles/fp16/randn.bin tools/claims-v3/kinds/tiles/fp16/randn.bin
tiles/fp16/zeros.bin tools/claims-v3/kinds/tiles/fp16/zeros.bin
tiles/fp16/ones.bin tools/claims-v3/kinds/tiles/fp16/ones.bin
tiles/int8/full.bin tools/claims-v3/kinds/tiles/int8/full.bin
tiles/int8/zeros.bin tools/claims-v3/kinds/tiles/int8/zeros.bin
tiles/int8/ones.bin tools/claims-v3/kinds/tiles/int8/ones.bin
EOF
echo "EQUAL $same of $n (the README's copies)"
echo "tile files in src/tiles: $(find src/tiles -type f | wc -l) (the lab's nine kinds: $( [ "$(find src/tiles -type f | wc -l)" = 9 ] && echo yes || echo NO)); plan tiles: 0"
echo "the kit's own files: $(find src -type f ! -path 'src/rgm136/*' ! -path 'src/ettelem/*' ! -path 'src/dmcmd/*' ! -path 'src/tiles/*' | wc -l); tile files: $(find src/tiles -type f | wc -l)"
echo
echo "## 9. gemmL arms past the first sweep's largest K (fp32 16,384, fp16 8,192, int8 32,768) and past the fourth, fifth and sixth sweeps' (E217's, E219's and E221's committed arms.json)"
$PY -I -B - src/arms.json "$LAB/tools/claims-v3/e217/proposal/src/arms.json" "$LAB/tools/claims-v3/e219/proposal/src/arms.json" "$LAB/tools/claims-v3/e221/proposal/src/arms.json" <<'EOF'
import json, sys
A = json.load(open(sys.argv[1]))
FK = {"fp32": 16384, "fp16": 8192, "int8": 32768}
gl = [a for a in A["arms"] if "arm" not in a]
deep = [a for a in gl if a["K"] > FK[a["type"]]]
print("gemmL arms: %d (with the anchor); largest K a type: %s" % (len(gl), ", ".join("%s %d" % (t, max([a["K"] for a in gl if a["type"] == t] or [0])) for t in FK)))
print("past the first sweep's largest K: %d arm(s)%s" % (len(deep), (": " + ", ".join("%s (K %d)" % (a["id"], a["K"]) for a in deep)) if deep else ""))
for name, p in (("fourth (E217)", sys.argv[2]), ("fifth (E219)", sys.argv[3]), ("sixth (E221)", sys.argv[4])):
    B = json.load(open(p))
    TK = {t: max([a["K"] for a in B["arms"] if a["type"] == t and "arm" not in a] or [0]) for t in FK}
    print("the %s sweep's largest gemmL K a type: %s" % (name, ", ".join("%s %d" % (t, TK[t]) for t in FK)))
    d = [a for a in gl if a["K"] > TK[a["type"]]]
    print("past the %s sweep's largest K: %d arm(s)%s" % (name, len(d), (": " + ", ".join("%s (K %d)" % (a["id"], a["K"]) for a in d)) if d else ""))
EOF
echo
echo "## 10. THE ARM GRAMMAR read independently (rgm136's host rules as the lab reads src/rgm136/host/main.cpp and sparsity_args.h)"
$PY -I -B - src <<'EOF'
import json, os, re, sys
src = sys.argv[1]
sys.path.insert(0, src)
import mms_common as MC
A = json.load(open(os.path.join(src, "arms.json")))
hdr = open(os.path.join(src, "rgm136", "sparsity_args.h")).read()
cpp = open(os.path.join(src, "rgm136", "host", "main.cpp")).read()
def const(name):
    m = re.search(r"#define %s (\d+)u" % name, hdr)
    return int(m.group(1))
KT, MT, NT, TB = const("SP_GEMM_KT"), const("SP_GEMM_MT"), const("SP_GEMM_NT"), const("SP_TILE_BYTES")
print("sparsity_args.h: SP_GEMM_KT %d, SP_GEMM_MT %d, SP_GEMM_NT %d, SP_TILE_BYTES %d" % (KT, MT, NT, TB))
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
def host_parse(tok):
    """the lab's reading of parseArm + testArm (no other code): (family, n, reps, cshared, halfk, ops_pass, first, check, MB)"""
    if tok == "tenb":
        return ("tenb", 1, 1, False, False, 1, 64000, 32, (TB + TB) / 1048576.0 + 1.0)
    m = re.fullmatch(r"(mmp|mm)(\d+)", tok)
    if m:
        priv, n = m.group(1) == "mmp", int(m.group(2))
        tiles = (1024 if priv else 1) * n
        return (m.group(1), n, 1, False, False, n, 20 if priv else max(1, 64000 // n), 2, 2 * tiles * TB / 1048576.0 + 1.0)
    for pre in ("gemmnc", "gemmc", "gemmv", "gemmh"):
        if tok.startswith(pre):
            break
    else:
        pre = "gemmL" if tok.startswith("gemmL") else ("gemm" if tok.startswith("gemm") else None)
    if pre is None:
        return None
    if pre == "gemmL":
        m = re.fullmatch(r"gemmL(\d+)x(\d+)x(\d+)", tok)
        mb, nb, kb = (int(x) for x in m.groups())
        ops = mb * nb * 2 * kb * KT
        a_t, b_t, c_b = mb * kb * MT * KT, kb * nb * KT * NT, mb * nb * MT * NT * TB
        return ("gemmL", mb * nb * kb, 1, False, False, ops, max(1, 64000 // ops), 1, (a_t * TB + b_t * TB + c_b) / 1048576.0)
    m = re.fullmatch(pre + r"(\d+)(?:r(\d+))?(s?)", tok)
    if not m:
        return None
    n, r, s = int(m.group(1)), int(m.group(2) or 1), m.group(3) == "s"
    halfk = pre == "gemmh"
    ops = n * r * 2 * (KT // 2 if halfk else KT)
    a_t, b_t = n * MT * KT, n * KT * NT
    c_b = (1 if s else n) * MT * NT * TB
    return (pre, n, r, s, halfk, ops, max(1, 64000 // ops), 1, (a_t * TB + b_t * TB + c_b) / 1048576.0)
bad, nblk = [], 0
fams = {}
for a in A["arms"]:
    tok, gen, files = a["values"].split(":", 2)
    h = host_parse(tok)
    g = MC.arm_of(a["values"])
    if h is None or g is None:
        bad.append("%s: not parsed (host %s, arm_of %s)" % (a["id"], h, g))
        continue
    fam, n, r, s, halfk, ops, first, chk, foot = h
    fams[fam] = fams.get(fam, 0) + 1
    if fam in ("gemmnc", "gemmv", "mmp"):
        bad.append("%s: family %s (not in this kit)" % (a["id"], fam))
    if (g["family"], g["ops_pass"], g["first_passes"], g["check_passes"]) != (fam, ops, first, chk) or abs(g["footprint_mb"] - foot) > 1e-6:
        bad.append("%s: arm_of %s vs the host's reading %s" % (a["id"], (g["family"], g["ops_pass"], g["first_passes"], g["check_passes"], g["footprint_mb"]), h))
    if a["ops_per_minion_pass"] != ops or a["M"] * a["N"] * a["K"] != 1024 * ops * MACS[a["type"]]:
        bad.append("%s: record ops %s, M N K %s %s %s vs the host's %d ops a pass" % (a["id"], a["ops_per_minion_pass"], a["M"], a["N"], a["K"], ops))
    if fam != "gemmL":
        nblk += 1
        if abs(a["footprint_mb"] - foot) > 1e-6 or a.get("first_passes") != first or a.get("check_passes") != chk:
            bad.append("%s: record footprint/first/check %s %s %s vs %s %s %s" % (a["id"], a["footprint_mb"], a.get("first_passes"), a.get("check_passes"), foot, first, chk))
        if a["shires"] != "0xffffffff":
            bad.append("%s: mask %s (block arms run on the whole chip)" % (a["id"], a["shires"]))
        if a["kind"] not in ("rnd", "zeros", "ones"):
            bad.append("%s: kind %s" % (a["id"], a["kind"]))
        if fam in ("gemmc", "gemmh", "gemm") and (n > 32 or r > 32):
            bad.append("%s: B %d R %d" % (a["id"], n, r))
        if fam == "mm" and n > 256:
            bad.append("%s: N %d" % (a["id"], n))
        if fam == "tenb" and gen != "tiles":
            bad.append("%s: tenb gen %s" % (a["id"], gen))
        if fam in ("gemmc", "gemmh", "gemm") and a.get("nblocks") != n or (fam in ("gemmc", "gemmh", "gemm") and (a.get("repeats") != r or bool(a.get("c_shared")) != s)):
            bad.append("%s: record blocks/repeats/shared" % a["id"])
print("arms parsed: %d; by the host's family: %s; block, stream and TenB arms: %d" % (len(A["arms"]), ", ".join("%s %d" % kv for kv in sorted(fams.items())), nblk))
blk = [a for a in A["arms"] if "arm" in a]
if blk:
    print("ops a minion a pass over the block arms: %d-%d; first (calibration) passes %d-%d; footprints %g-%g MB" % (
        min(a["ops_per_minion_pass"] for a in blk), max(a["ops_per_minion_pass"] for a in blk), min(a["first_passes"] for a in blk),
        max(a["first_passes"] for a in blk), min(a["footprint_mb"] for a in blk), max(a["footprint_mb"] for a in blk)))
else:
    print("block, stream and TenB arms: none (this sweep's arms are gemmL arms only)")
gla = [a for a in A["arms"] if "arm" not in a]
print("gemmL arms: ops a minion a pass %d-%d; M %d-%d, N %d-%d, K %d-%d; footprints %g-%g MB" % (
    min(a["ops_per_minion_pass"] for a in gla), max(a["ops_per_minion_pass"] for a in gla), min(a["M"] for a in gla), max(a["M"] for a in gla),
    min(a["N"] for a in gla), max(a["N"] for a in gla), min(a["K"] for a in gla), max(a["K"] for a in gla),
    min(a["footprint_mb"] for a in gla), max(a["footprint_mb"] for a in gla)))
# the host's own lines the kit's desk tests read the grammar from (selftest_mms.py HOST_LINES), in the host's prefix order: the
# list read by the ast module from the file's text (the file is not imported or run)
import ast
tree = ast.parse(open(os.path.join(src, "selftest_mms.py")).read())
lines = []
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "HOST_LINES" for t in node.targets):
        lines = ast.literal_eval(node.value)
pos = [cpp.find(x) for x in lines]
print("selftest_mms.py HOST_LINES: %d lines; found in main.cpp: %d; the first nine (parseArm's branches) in order: %s" % (
    len(lines), sum(1 for p in pos if p >= 0), all(p >= 0 for p in pos[:9]) and pos[:9] == sorted(pos[:9])))
print("ARM GRAMMAR %s (%d finding(s))" % ("PASS" if not bad else "FAIL", len(bad)))
for b in bad[:40]:
    print("  " + b)
EOF
echo
echo "## 11. the pair check: arms.json's plan tiles"
$PY -I -B - src/arms.json <<'EOF'
import json, sys
A = json.load(open(sys.argv[1]))
print("plan tiles in arms.json: %d; arms on a plan tile: %d (nothing to pair: the pair check reads plan tiles only)" % (
    len(A["tiles"]), sum(1 for a in A["arms"] if a["kind"] not in ("rnd", "zeros", "ones"))))
EOF
echo
echo "## 12. the host rules the README names, as lines of code, and the runner's own preflight call"
grep -n -E 'cmake --build .* -j[0-9]' src/build_mms.sh
grep -n -E 'LOAD1|loadavg' src/preflight_mms.sh
PY_LOADS=$(grep -c -E 'nogo .*one-minute load' src/preflight_mms.sh); echo "preflight NO-GO lines on the load: $PY_LOADS"
grep -n -E 'audit-only' src/preflight_mms.sh src/run_mms.py
echo "files of the session's path that name the preflight: $(grep -l -E 'preflight_mms' src/run_mms.py src/start_mms.sh src/session_mms.sh src/status_mms.sh src/stop_mms.sh 2>/dev/null | paste -sd ' ')"
echo
echo "## 13. the masks and the post's planning claims, per card (as the schedules hold them)"
$PY -I -B - src <<'EOF'
import collections, json, os, sys
src = sys.argv[1]
A = {a["id"]: a for a in json.load(open(os.path.join(src, "arms.json")))["arms"]}
LOW = {1: "0x1", 4: "0xf", 8: "0xff", 16: "0xffff", 24: "0xffffff"}
bad = []
pc = collections.Counter()
for a in A.values():
    m = int(a["shires"], 16)
    n = bin(m).count("1")
    pc[n] += 1
    if not (0 < m <= 0xffffffff) or a["shires"] != "0x%x" % m:
        bad.append("%s: mask %s not a 32-bit mask in the host's form" % (a["id"], a["shires"]))
    base = "%dx%dx%d-%s-%s" % (a["mb"], a["nb"], a["kb"], a["type"], a["kind"])
    if m == 0xffffffff:
        want = base
    elif m == (1 << n) - 1:
        want = base + "-s%d" % n
    else:
        want = base + "-m%x" % m
    if a["id"] != want:
        bad.append("%s: id, by the README's naming rule %s" % (a["id"], want))
print("masks: %d distinct; shires a mask (count of arms): %s" % (len({a["shires"] for a in A.values()}),
      ", ".join("%d: %d" % kv for kv in sorted(pc.items()))))
print("subset masks of more than 24 shires (the README says 'here 1 to 24 shires'): %s" % (
    ", ".join(sorted({a["shires"] for a in A.values() if 24 < bin(int(a["shires"], 16)).count("1") < 32})) or "none"))
print("MASK NAMES %s (%d finding(s))" % ("PASS" if not bad else "FAIL", len(bad)))
for b in bad[:20]:
    print("  " + b)
CLAIM = {"a1c1": 66.6, "a2c0": 66.6, "a1c0": 52.0}
for fn in sorted(os.listdir(os.path.join(src, "sched"))):
    s = json.load(open(os.path.join(src, "sched", fn)))
    card = s["card"]
    runs = [r for r in s["runs"] if r["role"] != "null"]
    hi = max(runs, key=lambda r: r["est_peak_w"])
    sm = max(s["smoke"], key=lambda r: r["est_peak_w"])
    roles = collections.Counter(r["role"] for r in s["runs"])
    rnd = [r for r in runs if A[r["arm"]]["kind"] == "rnd" and A[r["arm"]]["type"] in ("fp32", "fp16")]
    l3 = [r["arm"] for r in rnd if "L3served" in A[r["arm"]]["families"]]
    print("%s: highest planned run %.1f W (%s), smoke %.1f W (%s); the post's line %.1f W: %s; the card's planning line %s W; "
          "time-role runs %d; fp random runs %d (footprints %s MB; tagged L3served %d)" % (
              fn, hi["est_peak_w"], hi["arm"], sm["est_peak_w"], sm["arm"], CLAIM[card],
              "AT OR UNDER" if max(hi["est_peak_w"], sm["est_peak_w"]) <= CLAIM[card] else "OVER", s["line_w"], roles.get("time", 0),
              len(rnd), ",".join(str(x) for x in sorted({A[r["arm"]]["footprint_mb"] for r in rnd})) or "-", len(l3)))
print("arms tagged L3served: %s" % (", ".join("%s (%g MB)" % (a["id"], a["footprint_mb"]) for a in sorted(A.values(), key=lambda a: a["id"])
                                            if "L3served" in a["families"]) or "none"))
for tag in ("L3R", "L3R2"):
    xs = sorted((a for a in A.values() if tag in a["families"]), key=lambda a: a["id"])
    print("arms tagged %s: %d: %s" % (tag, len(xs), ", ".join("%s (%g MB)" % (a["id"], a["footprint_mb"]) for a in xs) or "none"))
EOF

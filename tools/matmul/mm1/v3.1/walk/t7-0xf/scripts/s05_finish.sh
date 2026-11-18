#!/bin/bash
# t7-0xf (Q221) s05: finish the land dir (after s01's build): (1) the verdict file T7-TRACE-CHECK.json by c03_verdict.py from the re-check
# outputs and the land dir; (2) the scrub scan (s02) of every file; (3) SHA256SUMS of every file, paths relative to the folder (the lab's
# form), checked with sha256sum -c from the folder. Desk; one slot job at a time under THE CPU RULE; writes only the land dir.
set -u
W=<W>
L=$W/out/t7-0xf
LW=$L/land/tools/matmul/mm1/v3.1/walk
PY="/usr/bin/python3 -I -B"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
[ -d "$LW" ] || { echo "no land dir"; exit 3; }
[ -e "$LW/SHA256SUMS" ] && { echo "SHA256SUMS exists: the land dir is finished already"; exit 8; }
bash "$W/slot.sh" $PY "$L/scripts/c03_verdict.py" "$L/work/recheck" "$LW" > "$LW/T7-TRACE-CHECK.json" 2> "$L/logs/c03.err"
echo "c03 rc=$?: $(grep -m1 '"verdict"' "$LW/T7-TRACE-CHECK.json") $(grep -m1 '"why"' "$LW/T7-TRACE-CHECK.json" | cut -c1-200)"
bash "$W/slot.sh" $PY "$L/scripts/s02_scrub_scan.py" "$LW" | tail -6
echo "scrub scan rc=${PIPESTATUS[0]}"
$PY - "$LW" <<'EOF'
import hashlib, os, sys
top = sys.argv[1]
rows = []
for dp, dn, fn in os.walk(top):
    dn.sort()
    for f in sorted(fn):
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, top)
        if rel == "SHA256SUMS":
            continue
        rows.append((rel, hashlib.sha256(open(p, "rb").read()).hexdigest()))
rows.sort()
open(os.path.join(top, "SHA256SUMS"), "w").write("".join("%s  %s\n" % (h, r) for r, h in rows))
print("SHA256SUMS: %d files" % len(rows))
EOF
cd "$LW" && sha256sum -c --quiet SHA256SUMS && echo "sha256sum -c: all $(wc -l < SHA256SUMS) OK"
echo "SHA256SUMS sha256 $(sha256sum "$LW/SHA256SUMS" | cut -d' ' -f1); files $(find "$LW" -type f | wc -l); size $(du -sh "$LW" | cut -f1)"
find "$LW" -name __pycache__ | head -3

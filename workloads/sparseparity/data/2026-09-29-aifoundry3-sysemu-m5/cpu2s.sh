#!/bin/bash
# CPU two-stage screens (vexh) at the card's (m1, tau1) and alternatives, 6 threads pinned to cores 0-5, niced,
# 5 reps; each only while nobody holds the card. Output: JSON lines.
cd ~/nekko/build
V=./sparseparity-s-cpu/spbase
OUT=${1:-sparseparity-s/cpu2s.jsonl}
run() {
  until et-who --check > /dev/null 2>&1; do sleep 15; done
  local t0=$(date +%s.%N)
  OMP_PROC_BIND=close OMP_PLACES="{0},{1},{2},{3},{4},{5}" OMP_NUM_THREADS=6 OMP_WAIT_POLICY=passive nice -n 19 "$V" "$@" > /tmp/cpu2s.$$ 2>&1
  local rc=$?
  python3 -c '
import json, sys
rc, t1, t0, argv, path = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
lines = open(path).read().strip().splitlines()
try:
    d = json.loads(lines[-1])
except Exception:
    d = {"parse_error": "\n".join(lines[-3:])}
d.update(rc=rc, process_s=round(t1 - t0, 3), argv="spbase " + argv)
print(json.dumps(d))
' "$rc" "$(date +%s.%N)" "$t0" "$*" /tmp/cpu2s.$$ >> "$OUT"
  tail -1 "$OUT" | python3 -c 'import json,sys; d=json.loads(sys.stdin.read()); print(d.get("argv"), "stage1 med", d.get("wall_med_s"), "stage2", d.get("stage2_s"), "surv", d.get("survivors"), "kept", d.get("secret_survived"), "ok", d.get("stage2_ok"))'
}
L2="n=512 k=4 eta=0.4 seed=1"; F5="n=256 k=5 eta=0.4 seed=1"; L1="n=512 k=4 eta=0.3 seed=1"
run vexh $L1 m=320 tau=66 m2=448 threads=6 reps=5
run vexh $L2 m=1152 tau=106 m2=1850 threads=6 reps=5
run vexh $L2 m=1024 tau=88 m2=1850 threads=6 reps=5
run vexh $L2 m=1280 tau=124 m2=1850 threads=6 reps=5
run vexh $L2 m=1024 tau=104 m2=1850 threads=6 reps=5
run vexh $F5 m=1152 tau=106 m2=1925 threads=6 reps=5
run vexh $F5 m=1024 tau=88 m2=1925 threads=6 reps=5
run vexh $F5 m=1280 tau=124 m2=1925 threads=6 reps=5
run vexh $F5 m=1024 tau=104 m2=1925 threads=6 reps=5

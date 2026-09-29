#!/usr/bin/env bash
# sparseparity: every kernel path in sys_emu, the functional simulator, before any card time. No card is opened:
# every command carries --sysemu (checked below). The simulator's checkers are on (mem_check, l1/l2_scp_check,
# flb_check, tstore_check: the runtime's defaults) plus -vpurf_warn, filtered to the kernel's PCs (the relocated
# kernel runs at 0x8005...; the firmware's own hazards, at 0x40... and 0x8000..., are not ours).
#
#   bash workloads/sparseparity/sysemu_check.sh [--quick] [--build DIR] [--cpu DIR] [--keep]   from the tree's root
#
# The M0 cross-check (unless --quick): M0's planner writes the work list (tools/planner.py plan --topm 0), the kernel
# runs it (--plan, --out), and tools/sptest.py card compares every hart's record with M0's reference, spref, field
# by field. It needs numpy and spref in --cpu DIR (default build/sparseparity-cpu:
# make -C workloads/sparseparity/cpu O=$PWD/build/sparseparity-cpu); without them those cases are skipped.
#
# Refuses on aifoundry2 (its DV2 validation treats any sys_emu or *_host process as a foreign device process) and
# while any tools/claims-v3 queue, block or series runs on the host. Runs niced (19), one simulator at a time.
# Each run boots the simulated firmware (about 47 s). Output: <build>/sysemu/<time>/<case>/ (out.json, err.txt =
# stderr without the runtime's INFO lines, and sysemu.log for failed cases or with --keep); the summary goes to
# stdout. Exit 0 when every case behaves as expected (negative controls must FAIL on the checksums and nothing else;
# the abort case must fail cleanly, with the harts' error flags and no hang).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 2
BUILD=build/sparseparity-m1
CPU=build/sparseparity-cpu
QUICK=; KEEP=
while [ $# -gt 0 ]; do
  case "$1" in
    --quick) QUICK=1 ;;
    --keep) KEEP=1 ;;
    --build) BUILD=$2; shift ;;
    --cpu) CPU=$2; shift ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
  shift
done
HOST_BIN=$PWD/$BUILD/host/sparseparity_host
SELFTEST=$PWD/$BUILD/host/spp_selftest
say() { echo "$(date +%T) sysemu: $*"; }
[ "$(hostname)" = aifoundry2 ] && [ "${SPP_ALLOW_AIFOUNDRY2:-}" != 1 ] && { say "aifoundry2: refused (DV2 validation)"; exit 2; }
p=$(pgrep -af '[t]ools/claims-v3/(queue\.sh|[a-z0-9_/-]+/(block|series|run_queue)\.sh)' 2>/dev/null | cut -c1-120 | tr '\n' ';')
[ -n "$p" ] && { say "a claims-v3 queue, block or series runs here ($p): refused"; exit 2; }
[ -x "$HOST_BIN" ] || { say "missing $HOST_BIN"; exit 2; }
[ -x "$SELFTEST" ] || { say "missing $SELFTEST"; exit 2; }
[ -x /opt/et/bin/sys_emu ] || { say "no /opt/et/bin/sys_emu"; exit 2; }
case "$(hostname)" in aifoundry1) export ET_DEVICES=1 ;; esac   # belt and braces: nothing here opens a card

WD=$PWD/$BUILD/sysemu/$(date +%Y%m%d-%H%M%S)
mkdir -p "$WD"
# inputs: the tie instance (C0's shape, two candidates at c = m) and R1's wide text plan (32 minions, one row tile
# each, 1-2 column tiles, n = 512, m = 2304: the scratchpad layout ends at exactly 2,560 KB with 1 buffer)
"$SELFTEST" --tie-instance "$WD/tie.spi" > /dev/null || { say "cannot write the tie instance"; exit 2; }
for i in $(seq 0 31); do echo "0 $i $((1250000 + 4000 * i)) 1"; done > "$WD/plan_hi.txt"

# name|expect|args   (expect: PASS; TIMING = a --timing-only run that must finish cleanly; NEG = the closed-form
# checksums must fail and every other check pass; NEGM = the mask control: the count holds, both closed forms and
# the oracle fail; TIE = PASS with the answer reported not unique; ABORT = the harts give up (tiny poll limit) and
# the run fails cleanly on its records; REJECT = the simulator's L1 scratchpad checker must stop the run:
# --nowait-a reloads an A buffer that an issued TensorIMA8A32 may still read, which the PRM forbids)
cases=(
  "c0-scalar|PASS|--mode scalar --dump"
  "c0-tensor|PASS|--mode tensor --dump"
  "s4-tensor|PASS|--mode tensor --dump --n 48 --k 3 --eta 0.1 --m 256 --seed 9"
  "shire8-s5|PASS|--mode tensor --dump --n 64 --k 3 --eta 0.2 --m 320 --seed 2 --per-shire 8"
)
if [ -z "$QUICK" ]; then
  cases+=(
    "c0-scalar-2h|PASS|--mode scalar --two-hart --dump"
    "s4-nbuf1|PASS|--mode tensor --dump --n 48 --k 3 --eta 0.1 --m 256 --seed 9 --nbuf 1"
    "s4-dram|PASS|--mode tensor --dump --n 48 --k 3 --eta 0.1 --m 256 --seed 9 --stage dram"
    "s4-nowait|REJECT|--mode tensor --dump --n 48 --k 3 --eta 0.1 --m 256 --seed 9 --nowait-a"
    "k4-2shires|PASS|--mode tensor --dump --n 40 --k 4 --eta 0.1 --m 192 --seed 5 --shires 0x3 --per-shire 2"
    "k5|PASS|--mode tensor --dump --n 24 --k 5 --eta 0.1 --m 128 --seed 3"
    "k2-m100|PASS|--mode tensor --dump --n 40 --k 2 --eta 0.1 --m 100 --seed 4"
    "k1|PASS|--mode tensor --dump --n 20 --k 1 --eta 0.1 --m 40 --seed 2"
    "k4-scalar-2shires|PASS|--mode scalar --two-hart --dump --n 40 --k 4 --eta 0.1 --m 192 --seed 5 --shires 0x3 --per-shire 2"
    "s4-timing|TIMING|--mode tensor --timing-only --n 48 --k 3 --eta 0.1 --m 256 --seed 9"
    "neg-drop|NEG|--mode tensor --perturb drop"
    "neg-dup|NEG|--mode tensor --perturb dup"
    "neg-mask|NEGM|--mode tensor --perturb mask"
    "tie|TIE|--mode tensor --instance $WD/tie.spi"
    "tie-8|TIE|--mode tensor --instance $WD/tie.spi --per-shire 8"
    "tie-scalar|TIE|--mode scalar --instance $WD/tie.spi"
    "probe|PASS|--mode tensor --n 48 --k 3 --eta 0.1 --m 256 --seed 9 --per-shire 4 --probe narrow:6 --oracle on"
    "reps2|PASS|--mode tensor --dump --n 48 --k 3 --eta 0.1 --m 256 --seed 9 --per-shire 2 --reps 2"
    "abort|ABORT|--mode tensor --n 48 --k 3 --eta 0.1 --m 256 --seed 9 --per-shire 4 --poll-limit 2"
    "hi-auto|PASS|--mode tensor --n 512 --k 4 --eta 0.4 --m 2304 --seed 7 --per-shire 32 --plan $WD/plan_hi.txt --oracle on"
  )
fi

fails=0
printf '%-18s %-6s %-6s %-8s %-8s %-6s %-22s %-8s %-5s %s\n' case expect status sum_c sum_c2 oracle dump solved vpurf mem
for c in "${cases[@]}"; do
  name=${c%%|*}; rest=${c#*|}; expect=${rest%%|*}; args=${rest#*|}
  d=$WD/$name; mkdir -p "$d"
  cmd=("$HOST_BIN" --sysemu --sim-args "-vpurf_warn" $args)
  [[ " ${cmd[*]} " == *" --sysemu "* ]] || { say "internal: no --sysemu in $name"; exit 2; }
  t0=$(date +%s)
  ( cd "$d" && timeout 1800 nice -n 19 "${cmd[@]}" > out.json 2> err.log < /dev/null ); rc=$?
  line=$(python3 - "$d" "$expect" "$rc" <<'EOF'
import json, re, sys
d, expect, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
try:
    j = json.loads(open(d + "/out.json").read().strip().splitlines()[-1])
except Exception:
    j = {}
log = open(d + "/sysemu.log", errors="replace").read() if __import__("os").path.exists(d + "/sysemu.log") else ""
vp = sum(1 for l in log.splitlines() if "VPURF" in l and re.search(r" 0x8005[0-9a-f]+ ", l))
fatal = sum(1 for l in log.splitlines() if "FATAL" in l)
c = j.get("checks", {})
st = j.get("status", "NONE")
res = j.get("result", {})
clean = vp == 0 and fatal == 0
if expect in ("PASS", "TIMING"):
    ok = rc == 0 and st == expect and clean
elif expect == "TIE":
    ok = rc == 0 and st == "PASS" and res.get("unique") is False and res.get("solved") is False and clean
elif expect == "REJECT":
    ok = rc != 0 and fatal > 0 and all("L1-SCP-Checker" in l for l in log.splitlines() if "FATAL" in l)
elif expect == "ABORT":  # the harts give up and say so in their records; the launch itself completes
    ok = st == "FAIL" and c.get("launch") == "ok" and "bad" in c.get("records", "") and fatal == 0
elif expect == "NEGM":   # the mask control: the count holds, both closed forms and the oracle catch it
    ok = (st == "FAIL" and c.get("count") == "ok" and c.get("sum_c") == "MISMATCH" and c.get("sum_c2") == "MISMATCH"
          and c.get("oracle", "").startswith("MISMATCH") and c.get("records") == "ok" and c.get("launch") == "ok"
          and clean)
else:  # negative control: the closed forms must catch it, everything else must hold
    ok = (st == "FAIL" and "MISMATCH" in (c.get("sum_c", "") + c.get("sum_c2", "")) and
          c.get("oracle", "").startswith("exact") and c.get("records") == "ok" and c.get("launch") == "ok" and clean)
print(("OK " if ok else "BAD ") + f"{st:<6} {c.get('sum_c','-'):<8} {c.get('sum_c2','-'):<8} {c.get('oracle','-')[:6]:<6} "
      f"{c.get('dump','-')[:22]:<22} {str(j.get('result',{}).get('solved','-')):<8} {vp:<5} {fatal}")
EOF
)
  verdict=${line%% *}; rest=${line#* }
  printf '%-18s %-6s %s  (%ss)\n' "$name" "$expect" "$rest" "$(( $(date +%s) - t0 ))"
  [ "$verdict" = OK ] || { fails=$((fails + 1)); grep -v '^I20' "$d/err.log" | tail -3 | sed 's/^/    /'; }
  grep -v '^I20' "$d/err.log" > "$d/err.txt"; rm -f "$d/err.log"   # the runtime's INFO lines run to 100 MB
  [ -z "$KEEP" ] && [ "$verdict" = OK ] && rm -f "$d/sysemu.log" "$d"/*uart*.log
done

# name|n,k,eta,m,seed|planner options
m0cases=()
if [ -z "$QUICK" ]; then
  m0cases=(
    "m0-c0|32,3,0.1,128,1|--shire-mask 0x1 --mps 1"
    "m0-s4-shire8|48,3,0.1,256,9|--shire-mask 0x1 --mps 8 --blocks-per-minion 2"
    "m0-k4-2shires|40,4,0.1,192,5|--shire-mask 0x3 --mps 2"
  )
  if [ ! -x "$CPU/spref" ] || ! python3 -c 'import numpy' 2> /dev/null; then
    say "M0 cross-check skipped: no $CPU/spref or no numpy"
    m0cases=()
  fi
fi
for c in "${m0cases[@]}"; do
  name=${c%%|*}; rest=${c#*|}; inst=${rest%%|*}; popt=${rest#*|}
  IFS=, read -r n k eta m seed <<< "$inst"
  d=$WD/$name; mkdir -p "$d"
  t0=$(date +%s)
  python3 workloads/sparseparity/tools/planner.py plan --n "$n" --k "$k" --m "$m" $popt --topm 0 --out "$d/wl.bin" \
    > "$d/plan.txt" 2>&1 || { say "$name: planner failed"; fails=$((fails + 1)); continue; }
  cmd=("$HOST_BIN" --sysemu --sim-args "-vpurf_warn" --mode tensor --n "$n" --k "$k" --eta "$eta" --m "$m" --seed "$seed"
       --plan "$d/wl.bin" --out "$d/card.out")
  ( cd "$d" && timeout 1800 nice -n 19 "${cmd[@]}" > out.json 2> err.log < /dev/null ); rc=$?
  grep -v '^I20' "$d/err.log" > "$d/err.txt"; rm -f "$d/err.log"
  nice -n 19 python3 workloads/sparseparity/tools/sptest.py card --bin "$CPU" --threads 2 --plan "$d/wl.bin" \
    --out "$d/card.out" --inst "$inst" > "$d/card.txt" 2>&1; crc=$?
  st=$(python3 -c 'import json,sys; print(json.loads(open(sys.argv[1]).read().splitlines()[-1]).get("status","NONE"))' \
       "$d/out.json" 2> /dev/null || echo NONE)
  vp=$(grep VPURF "$d/sysemu.log" 2> /dev/null | grep -c ' 0x8005'); fatal=$(grep -c FATAL "$d/sysemu.log" 2> /dev/null)
  verdict=BAD
  [ $rc -eq 0 ] && [ "$st" = PASS ] && [ $crc -eq 0 ] && [ "${vp:-1}" = 0 ] && [ "${fatal:-1}" = 0 ] && verdict=OK
  printf '%-18s %-6s host %-6s  sptest card: %-10s vpurf %s mem %s  (%ss)\n' "$name" M0 "$st" \
    "$(tail -1 "$d/card.txt")" "$vp" "$fatal" "$(( $(date +%s) - t0 ))"
  [ "$verdict" = OK ] || { fails=$((fails + 1)); grep -E 'FAIL|differs|error' "$d/card.txt" | head -3 | sed 's/^/    /'; }
  [ -z "$KEEP" ] && [ "$verdict" = OK ] && rm -f "$d/sysemu.log" "$d"/*uart*.log
done
total=$(( ${#cases[@]} + ${#m0cases[@]} ))
if [ $fails -eq 0 ]; then say "SYSEMU PASS: $total cases ($WD)"; exit 0; fi
say "SYSEMU FAIL: $fails of $total cases (logs in $WD)"; exit 1

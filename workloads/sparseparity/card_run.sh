#!/usr/bin/env bash
# sparseparity on a card: the M1 and M2 steps (README.md, "M1 on a card" and "M2 on a card"), one process per step.
#
#   bash workloads/sparseparity/card_run.sh <m1|probe|m2|list> [--dry] [--build DIR] [--out DIR] [--from STEP]
#
# Run it from the tree's root on the card's host (~/nekko on aifoundry1 and aifoundry3, the checkout on aifoundry2),
# only with the owner's go-ahead for that card. Every step is one host process run as
#     flock -n /run/lock/etsoc-shire<N>.lock timeout 10 sparseparity_host ... --records-out <step>.rec
# so the lock is held for one process at a time and released between steps, and no process holds the device for
# more than 10 s (the host itself launches only while its timeout ends by 9 s). Before every step the script checks
# `et-who --check` and waits up to 5 minutes for a free card. On aifoundry1 it uses card 1 (ET_DEVICES=1,
# etsoc-shire1.lock); card 0 overheats. It stops at the first step whose result is not the expected one (a
# negative control must FAIL on its checksums and pass everything else), so a person can look before going on.
# After a step whose plan does not cover every candidate, the full per-minion oracle runs offline on the saved
# records (--verify-records: no device, no lock, no timeout).
#
# --dry: every step with the host's --dry (plan and model only; the device is never opened, no lock is taken).
# --from STEP: skip the steps before STEP (after a stop). Output: --out DIR (default
# build/sparseparity-card/<host>-<time>/): <step>.json (the host's JSON line), .err, .rec, .verify.json, summary.txt,
# manifest.txt (et-lab-manifest).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 2
WHAT=${1:-}; shift || true
DRY=; BUILD=build/sparseparity-f; OUT=; FROM=
while [ $# -gt 0 ]; do
  case "$1" in
    --dry) DRY=1 ;;
    --build) BUILD=$2; shift ;;
    --out) OUT=$2; shift ;;
    --from) FROM=$2; shift ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
  shift
done
case "$WHAT" in m1|probe|m2|list) ;; *) echo "usage: $0 <m1|probe|m2|list> [--dry] [--build DIR] [--out DIR] [--from STEP]" >&2; exit 2 ;; esac
HOST_BIN=$PWD/$BUILD/host/sparseparity_host
SELFTEST=$PWD/$BUILD/host/spp_selftest
[ -x "$HOST_BIN" ] && [ -x "$SELFTEST" ] || { echo "build first: $HOST_BIN" >&2; exit 2; }
H=$(hostname)
LOCK=/run/lock/etsoc-shire0.lock
if [ "$H" = aifoundry1 ]; then export ET_DEVICES=1; LOCK=/run/lock/etsoc-shire1.lock; fi
OUT=${OUT:-build/sparseparity-card/$H-$(date +%Y%m%d-%H%M%S)$([ -n "$DRY" ] && echo -dry)}

L2="--n 512 --k 4 --eta 0.4 --m 1850 --seed 1"
L1="--n 512 --k 4 --eta 0.3 --m 448 --seed 1"
C1="--n 128 --k 4 --eta 0.2 --m 192"
F5="--n 256 --k 5 --eta 0.4 --m 1925 --seed 1"
L5="--n 512 --k 5 --eta 0.4 --m 2151 --seed 1"
# name|expect|model kernel time|args   (expect: PASS, TIMING, NEG (drop/dup: a closed form fails, nothing else),
# NEGM (the mask: both closed forms and the oracle fail, the count holds), TIE (PASS, the answer not unique))
M1=(
  "m1-c0-scalar|PASS|1 ms|--mode scalar --dump"
  "m1-c0-tensor|PASS|0.1 ms|--mode tensor --dump"
  "m1-neg-drop|NEG|0.1 ms|--mode tensor --perturb drop"
  "m1-neg-dup|NEG|0.1 ms|--mode tensor --perturb dup"
  "m1-neg-mask|NEGM|0.1 ms|--mode tensor --perturb mask"
  "m1-tie|TIE|0.1 ms|--mode tensor --instance $OUT/tie.spi"
  "m1-c1-timing|TIMING|0.14 s|--mode tensor $C1 --seed 1 --timing-only"
  "m1-c1|PASS|0.14 s|--mode tensor $C1 --seed 1"
  "m1-l1-timing|TIMING|1.2 s|--mode tensor $L1 --slice 0/64 --timing-only"
  "m1-l1|PASS|1.2 s|--mode tensor $L1 --slice 0/64"
  "m1-l2-timing|TIMING|1.5 s|--mode tensor $L2 --slice 0/200 --timing-only"
  "m1-l2|PASS|1.5 s|--mode tensor $L2 --slice 0/200"
)
for s in $(seq 1 20); do M1+=("m1-c1-32-seed$s|PASS|4 ms|--mode tensor $C1 --seed $s --per-shire 32"); done
# The hand-off race probe (review R1, finding 3): 32 minions, each consuming one-column-tile row tiles right after
# hart 1 publishes them, with the full oracle; the streamed path (L2's m) and the resident one (C1's m), every staging.
PROBE=(
  "probe-l2-scp1|PASS|77 ms|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage scp --nbuf 1"
  "probe-l2-scp2|PASS|77 ms|--mode tensor $L2 --per-shire 16 --probe narrow:2000 --oracle on --stage scp --nbuf 2"
  "probe-l2-dram1|PASS|77 ms|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage dram --nbuf 1"
  "probe-l2-dram2|PASS|77 ms|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage dram --nbuf 2"
  "probe-c1-scp2|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage scp --nbuf 2"
  "probe-c1-scp1|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage scp --nbuf 1"
  "probe-c1-dram2|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage dram --nbuf 2"
  "probe-c1-dram1|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage dram --nbuf 1"
)
M2=("m2-c1-32|PASS|4 ms|--mode tensor $C1 --seed 1 --per-shire 32")
for P in 1 2 4 8 16 32; do   # the shire-bandwidth knee: the same work per minion (L1, S = 7, A streamed)
  M2+=("m2-knee-p$P-timing|TIMING|1.2 s|--mode tensor $L1 --per-shire $P --slice 0/$((64 / P)) --timing-only")
  M2+=("m2-knee-p$P|PASS|1.2 s|--mode tensor $L1 --per-shire $P --slice 0/$((64 / P))")
done
M2+=(
  "m2-l1-full|PASS|2.3 s|--mode tensor $L1 --per-shire 32"
  "m2-l2-q0|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4"
  "m2-l2-q0-dram2|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --stage dram --nbuf 2"
  "m2-l2-q0-dram1|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --stage dram --nbuf 1"
  "m2-l2-q0-timing|TIMING|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --timing-only"
  "m2-f5-s0|PASS|2.3 s|--mode tensor $F5 --per-shire 32 --slice 0/16"
  "m2-l5-s0|PASS|2.3 s|--mode tensor $L5 --per-shire 32 --slice 0/512"
  # last: skips the PRM's TensorWait before an A buffer is reloaded (sys_emu's checker rejects it); silicon only
  "m2-l2-q0-nowait|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --nowait-a"
)
case "$WHAT" in m1) STEPS=("${M1[@]}") ;; probe) STEPS=("${PROBE[@]}") ;; m2) STEPS=("${M2[@]}") ;; list) STEPS=("${M1[@]}" "${PROBE[@]}" "${M2[@]}") ;; esac
if [ "$WHAT" = list ]; then
  for c in "${STEPS[@]}"; do IFS='|' read -r n e t a <<< "$c"; printf '%-22s %-6s %-7s %s\n' "$n" "$e" "$t" "$a"; done
  exit 0
fi
mkdir -p "$OUT"
"$SELFTEST" --tie-instance "$OUT/tie.spi" > /dev/null || { echo "cannot write the tie instance" >&2; exit 2; }

say() { echo "$(date +%T) $*" | tee -a "$OUT/summary.txt"; }
card_free() {   # 0 when nobody holds a card node or lock (et-who --check: 0 free, 1 held, 2 failed)
  command -v et-who > /dev/null || return 0
  et-who --check > /dev/null 2>&1
}
[ -z "$DRY" ] && command -v et-lab-manifest > /dev/null && et-lab-manifest > "$OUT/manifest.txt" 2>&1
say "sparseparity card_run $WHAT on $H ($([ -n "$DRY" ] && echo 'DRY: no device' || echo "lock $LOCK${ET_DEVICES:+, ET_DEVICES=$ET_DEVICES}")), out $OUT"
OBJCOPY=objcopy; [ -x /opt/et/bin/riscv64-unknown-elf-objcopy ] && OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
$OBJCOPY -O binary -j .text "$BUILD/kernel/sparseparity.elf" "$OUT/kernel.text" 2> /dev/null
say "kernel $BUILD/kernel/sparseparity.elf: .text sha256 $(sha256sum < "$OUT/kernel.text" | cut -c1-64)"
started=${FROM:+0}; started=${started:-1}
for c in "${STEPS[@]}"; do
  IFS='|' read -r name expect model args <<< "$c"
  [ "$started" = 0 ] && { [ "$name" = "$FROM" ] && started=1 || continue; }
  if [ -z "$DRY" ]; then
    waited=0
    until card_free; do
      [ $waited -ge 300 ] && { say "STOP: the card is held (et-who) for 5 minutes before $name"; exit 3; }
      sleep 10; waited=$((waited + 10))
    done
    # shellcheck disable=SC2086
    flock -n "$LOCK" timeout 10 "$HOST_BIN" $args --records-out "$OUT/$name.rec" > "$OUT/$name.json" 2> "$OUT/$name.err" < /dev/null
    rc=$?
  else
    # shellcheck disable=SC2086
    "$HOST_BIN" --dry $args > "$OUT/$name.json" 2> "$OUT/$name.err" < /dev/null
    rc=$?
  fi
  grep -v '^I20' "$OUT/$name.err" > "$OUT/$name.err.txt" 2> /dev/null; mv -f "$OUT/$name.err.txt" "$OUT/$name.err"
  verdict=$(python3 - "$OUT/$name.json" "$expect" "$rc" "${DRY:-0}" <<'EOF'
import json, sys
path, expect, rc, dry = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4] == "1"
try:
    j = json.loads(open(path).read().strip().splitlines()[-1])
except Exception:
    print("BAD no JSON line (rc %d)" % rc); sys.exit()
st = j.get("status", "NONE")
if dry:
    ok = st == "DRY" and not j.get("refused_on_silicon")
    print(("OK " if ok else "BAD ") + f"DRY model {j.get('model_s', 0):.3g} s est {j.get('est_s', 0):.3g} s "
          f"stage {j.get('stage')} nbuf {j.get('nbuf')} scp {j.get('scp_layout_kb')} KB coverage {j.get('coverage')}")
    sys.exit()
c, res, k = j.get("checks", {}), j.get("result", {}), j.get("kernel", {})
if expect in ("PASS", "TIMING"):
    ok = rc == 0 and st == expect
elif expect == "TIE":
    ok = rc == 0 and st == "PASS" and res.get("unique") is False
elif expect == "NEGM":
    ok = (st == "FAIL" and c.get("count") == "ok" and c.get("sum_c") == "MISMATCH" and c.get("sum_c2") == "MISMATCH"
          and c.get("records") == "ok" and c.get("launch") == "ok")
else:  # NEG
    ok = (st == "FAIL" and c.get("count") == "ok" and "MISMATCH" in c.get("sum_c", "") + c.get("sum_c2", "")
          and c.get("records") == "ok" and c.get("launch") == "ok")
print(("OK " if ok else "BAD ") + f"{st} launch_s {j.get('launch_s')} open_s {j.get('open_s', 0):.2f} "
      f"cyc/op {k.get('cycles_per_op_busiest', 0):.1f} MHz {k.get('clock_mhz_est', 0):.0f} "
      f"cyc max/med {k.get('cycles_max', 0)}/{k.get('cycles_median', 0):.0f} wait {k.get('wait_cycles_max')} "
      f"solved {res.get('solved')} unique {res.get('unique')} sum_c {c.get('sum_c')} sum_c2 {c.get('sum_c2')} "
      f"oracle '{c.get('oracle')}' coverage {j.get('plan', {}).get('coverage')} "
      f"stage {j.get('plan', {}).get('stage')}/{j.get('plan', {}).get('nbuf')} scp_kb_device "
      f"{j.get('plan', {}).get('scp_kb_device')} problems {j.get('problems')}")
EOF
)
  say "$name [$expect, model $model] $verdict"
  if [ "${verdict%% *}" != OK ]; then
    say "STOP at $name: not the expected result; see $OUT/$name.json and $OUT/$name.err (resume: --from $name)"
    exit 1
  fi
  # the offline value check of a partial plan: the full oracle on the saved records (no device)
  if [ -z "$DRY" ] && [ "$expect" = PASS ] && grep -q '"coverage":"partial"' "$OUT/$name.json" && \
     ! grep -q '"oracle":"exact, all' "$OUT/$name.json"; then
    # shellcheck disable=SC2086
    nice -n 10 "$HOST_BIN" $args --verify-records "$OUT/$name.rec" > "$OUT/$name.verify.json" 2> /dev/null
    v=$(python3 -c 'import json,sys; j=json.loads(open(sys.argv[1]).read().splitlines()[-1]); print(j["status"], j["checks"]["oracle"])' "$OUT/$name.verify.json" 2> /dev/null)
    say "  $name offline verify: $v"
    [ "${v%% *}" = PASS ] || { say "STOP at $name: the offline oracle disagrees (resume: --from $name)"; exit 1; }
  fi
done
say "DONE $WHAT: every step as expected"

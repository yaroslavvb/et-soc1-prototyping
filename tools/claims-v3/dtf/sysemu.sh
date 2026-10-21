#!/usr/bin/env bash
# V3-DTF proof step 4 (README): every DF mode once in sys_emu, no card. One shire, hart 0 of each minion, the VPU register
# file checker on (-vpurf_warn, off by default), a budget long enough for a sys_emu boot (~40 s; the host's default 9.5 s
# would end the session before the first launch). Pass: one ENERCAT line per mode with "ok":true and 32 participants.
#   bash tools/claims-v3/dtf/sysemu.sh > build/dtf-sysemu.log 2>&1     # never inside a measured pass: sys_emu is a device process to lib.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export LD_LIBRARY_PATH=/opt/et/lib
H=build/enercat-df/host/enercat_host
GEN=build/dtf-gen/srcs
fail=0
for pair in df.c2.fand:d2B_h32 df.c2.for:d2D_h32 df.c2.fadd:d3_L8 df.c2.fxor:d2X_h32 df.un1a.fnot:d1a_h32 df.un1b.fnot:d1b_h32 \
            df.addr.a0:d5_a0 df.addr.a1:d5_a1 df.addr.a3:d5_a3 df.addr.a5:d5_a5; do
  mode=${pair%%:*}; item=${pair#*:}
  out=build/dtf-sysemu-$mode.log
  timeout 600 "$H" --sysemu --budget 1e9 --sim-args "-vpurf_warn" --harts 1 --shires 0x1 --window 4000 --seconds 0.05 \
    --pattern "$mode" --operands "file:$GEN/$item.bin" > "$out" 2>&1 < /dev/null
  rc=$?
  rec=$(grep -a '^ENERCAT {' "$out" | head -1)
  n=$(grep -a -c '^ENERCAT {' "$out")
  warn=$(grep -a -c -i 'vpurf' "$out")
  ok=no
  case "$rec" in *'"ok":true'*'"participants":32'*|*'"participants":32'*'"ok":true'*) ok=yes ;; esac
  [ "$n" -ge 1 ] && [ "$ok" = yes ] || fail=$((fail + 1))
  echo "$mode ($item): rc=$rc records=$n ok=$ok vpurf_lines=$warn :: ${rec:0:220}"
done
echo "sysemu: $((10 - fail)) of 10 modes PASS"
[ $fail -eq 0 ] && echo PASS || echo FAIL

#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md sections 4 and 5), step 8, v2: E180's build and checks on aifoundry3, as one
# detached job of the runbook (k6's rb_job_start / rb_job_wait), no device opened. It replaces s08_a3_build_e180.sh (v1, which stays as
# committed) in the runbook, with three changes:
#   1. the harness check and the preflight are v2's (check_e180_v2.py harness --binaries; preflight_e180_v2.sh on the v2 file set);
#   2. after the build, the box's own kernel is disassembled with the toolchain's objdump (/opt/et/bin/riscv64-unknown-elf-objdump, the one
#      E61's V3-DTF campaign used on this box, tools/claims-v3/dtf/block.sh) into build/e180-kernel-dis.txt, and ../check_elf_e180.py walks
#      modes 261 and 262 (and 160, the control) into build/e180/elfcheck-e180.txt, which step 22 copies back with the session's logs:
#      REPORTED, not a gate of this step; the registration's dated note A1, rule A1-7, reads it at scoring (a FAIL for 261 makes E180-A
#      NOT SCORED). Its line is printed with the others;
#   3. the job is named a3-build-e180-v2, so step 11 v2 needs this step, not v1's, to have ended rc 0 today.
# Everything else is v1's: build_e180.sh (a recorded build is never rebuilt without --rebuild), the gates on the build, the harness and
# the preflight.
#
#   bash tools/claims-v3/e180/rb/s08_a3_build_e180_v2.sh start       then        ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s08_a3_build_v2
act=${1:-}
case "$act" in
  start)
    body=$(rb_file body)
    cat > "$body" <<'EOF2'
bash tools/claims-v3/e180/build_e180.sh > build/e180-build-rb.txt 2>&1; b=$?; echo "build_e180 rc=$b $(tail -n 1 build/e180-build-rb.txt)"
mkdir -p build/e180
OD=/opt/et/bin/riscv64-unknown-elf-objdump
if [ -x "$OD" ] && [ -f build/enercat-e180/kernel/enercat.elf ]; then
  timeout 120 "$OD" -d build/enercat-e180/kernel/enercat.elf > build/e180-kernel-dis.txt 2>/dev/null
  python3 -B tools/claims-v3/e180/check_elf_e180.py build/e180-kernel-dis.txt --also-160 > build/e180/elfcheck-e180.txt 2>&1; e=$?
else
  echo "UNREAD fadd.ps.acc mode 261: no objdump at $OD or no kernel" > build/e180/elfcheck-e180.txt
  echo "UNREAD fadd.pi.acc mode 262: no objdump at $OD or no kernel" >> build/e180/elfcheck-e180.txt; e=0
fi
echo "elfcheck rc=$e $(tail -n 1 build/e180/elfcheck-e180.txt)"
grep -E '^(PASS|FAIL|UNREAD) ' build/e180/elfcheck-e180.txt | cut -c1-200
python3 -B tools/claims-v3/e180/check_e180_v2.py harness --binaries; c=$?; echo "check_e180_v2 rc=$c"
bash tools/claims-v3/e180/preflight_e180_v2.sh > build/e180-preflight-rb.txt 2>&1; p=$?; echo "preflight_e180_v2 rc=$p $(grep -m1 '^dmcmd_audit:' build/e180-preflight-rb.txt)"
[ "$b" -eq 0 ] && [ "$c" -eq 0 ] && [ "$p" -eq 0 ]
EOF2
    rb_probe aifoundry3
    rb_job_start aifoundry3 a3-build-e180-v2 "$body" 1
    ;;
  wait)
    rb_probe aifoundry3
    rb_job_wait aifoundry3 a3-build-e180-v2; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    if [ "$rc" -eq 0 ] || [ "$rc" -eq "$RB_E_FAIL" ]; then
      for k in 'build_e180 rc=' 'elfcheck rc=' 'HARNESS ' 'check_e180_v2 rc=' 'preflight_e180_v2 rc='; do grep -m1 "^$k" "$RB_CAP" || echo "(no line: $k)"; done
      grep -E '^(PASS|FAIL|UNREAD) ' "$RB_CAP" | cut -c1-200
    fi
    [ "$rc" -eq 0 ] || exit "$rc"
    bad=""
    rb_has '^build_e180 rc=0 ' || bad="$bad build"
    rb_has '^HARNESS OK: ' || bad="$bad harness"
    rb_has '^preflight_e180_v2 rc=0 dmcmd_audit: GO' || bad="$bad preflight_e180_v2"
    [ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry3's build or preflight failed:$bad (a file or binary differs: a dated amendment first)"
    el=$(grep -m1 '^elfcheck rc=' "$RB_CAP" | cut -c1-200)
    rb_say "aifoundry3: build_e180 OK, HARNESS OK with the binaries, preflight_e180_v2 GO; the disassembly walk (reported, A1-7): ${el:-no line}"
    ;;
  *) rb_die $RB_E_USAGE "usage: s08_a3_build_e180_v2.sh start|wait" ;;
esac

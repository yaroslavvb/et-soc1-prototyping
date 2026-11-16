#!/usr/bin/env bash
# E198 dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): step 8 (A1), THE DRY PASS. It is
# s10_a1_dry_e198.sh below (kit-e198, unchanged beside it) with A1's session and listing check: the job is a1-dry-e198a1-<sitting>; it runs
# session_e198a1.sh with DRY=1 (the lab's runner copy's own --dry inside the private /dev) and compares each listing with E193's registered
# one by check_e198a1.py drycmp (check_e198.py's five exact mappings and A1's sixth, `timeout 10` for `timeout -k 1 10`; the listing names no
# `timeout -k`). v1's header, read with these changes:
# E198 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum; ported from E193's file of the same step, unchanged in logic but the names below), the box step "the dry pass" (this file is s10), for this RB_OUT's sitting: THE SESSION'S WRAPPER ITSELF with DRY=1
# on aifoundry1 (session_e198.sh, its dry path: nothing opened, every device call listed by the runner's own --dry; the holder check,
# the two config reads and the smoke gate printed and skipped), into build/e198/T<T0>-dry (the rest rules skip it), then each listing
# compared, byte for byte after check_e198.py's five mappings (the host wrapper, --device 1's prefix, card 1's lock, its ops node, the holder
# check), to E193's registered listings (check_e198.py drycmp): the smoke's
# to desk/dry-e193-smoke-all.txt (10 device calls), the main run's to desk/dry-e193-A.txt (234) or -B.txt (135). As k6's detached job
# a1-dry-e198-<sitting> (one at a time, never beside a session of ours), then `wait` (bounded; 17 while it runs). Step 9 refuses a
# sitting whose dry pass did not end rc 0 today.
#   bash tools/claims-v3/e198/rb/s10_a1_dry_e198.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198a1.sh"
rb_init s10_a1_dry_A1
act=${1:-}
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a1_dry_e198.sh start | wait" ;; esac
e198_window
JOB=a1-dry-e198a1-$E198_SIT
[ -n "${RB_DRY:-}" ] || e198_built_today || rb_die $RB_E_USAGE "x04clock was not built today (RB_OUT/e198-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  hs=$(e198_harness_sha); [ -n "${RB_DRY:-}" ] && hs=${hs:-HARNESS-SHA256}
  [ -n "$hs" ] || rb_die $RB_E_USAGE "harness-e198-a1.json's sha256 could not be read in the lab clone"
  rb_probe aifoundry1
  body=$(rb_file body)
  { echo "SIT=$E198_SIT; HSHA=$hs; ROOT=$E198_ROOT"
    cat <<'EOF2'
T0=$(date +%s)
K=$ROOT/tools/claims-v3/e198
DRY=1 E198_T0=$T0 E198_HARNESS_SHA256=$HSHA bash "$K/session_e198a1.sh" "$SIT" < /dev/null
rc=$?
SD=build/e198/T$T0-dry
grep -E 'session start|HARNESS|preflight|binaries|deadline|smoke|main run|GATE-STOP|session end' "$SD/session.log" 2>/dev/null | cut -c1-220
H=$ROOT/build/x04clock/host/x04clock_host
REG=dry-e193-A.txt; [ "$SIT" = B ] && REG=dry-e193-B.txt
python3 -I -B "$K/check_e198a1.py" drycmp "$SD/smoke-runner.out" "$ROOT/tools/claims-v3/e193/desk/dry-e193-smoke-all.txt" --host "$K/x04host_e198.sh" --holder-check "$K/holdercheck_e198.sh"; s1=$?
python3 -I -B "$K/check_e198a1.py" drycmp "$SD/runner.out" "$ROOT/tools/claims-v3/e193/desk/$REG" --host "$K/x04host_e198.sh" --holder-check "$K/holdercheck_e198.sh"; s2=$?
echo "E198-DRY sitting $SIT rc=$rc smoke=$s1 main=$s2 calls=$(grep -c '^DRY ET_DEVICES=' "$SD/smoke-runner.out" 2>/dev/null)+$(grep -c '^DRY ET_DEVICES=' "$SD/runner.out" 2>/dev/null) manifest=$([ -s "$SD/MANIFEST.sha256" ] && echo written || echo absent)"
[ "$rc" -eq 0 ] && [ "$s1" -eq 0 ] && [ "$s2" -eq 0 ] && [ -s "$SD/MANIFEST.sha256" ]
EOF2
  } > "$body"
  rb_job_start aifoundry1 "$JOB" "$body"
  rb_say "the dry pass $JOB started on aifoundry1: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe aifoundry1
rb_job_wait aifoundry1 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E198-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"

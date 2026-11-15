#!/usr/bin/env bash
# E193 (Q177, the kit), the box step "the dry pass" (this file is s10), for this RB_OUT's sitting: THE SESSION'S WRAPPER ITSELF with DRY=1
# on aifoundry3 (session_e193.sh, its dry path: nothing opened, every device call listed by the runner's own --dry; the holder check,
# the two config reads and the smoke gate printed and skipped), into build/e193/T<T0>-dry (the rest rules skip it), then each listing
# compared, byte for byte with the host's path written as the registration's, to the registration's (check_e193.py drycmp): the smoke's
# to desk/dry-e193-smoke-all.txt (10 device calls), the main run's to desk/dry-e193-A.txt (234) or -B.txt (135). As k6's detached job
# a3-dry-e193-<sitting> (one at a time, never beside a session of ours), then `wait` (bounded; 17 while it runs). Step 9 refuses a
# sitting whose dry pass did not end rc 0 today.
#   bash tools/claims-v3/e193/rb/s10_a3_dry_e193.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e193.sh"
rb_init s10_a3_dry
act=${1:-}
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e193.sh start | wait" ;; esac
e193_window
JOB=a3-dry-e193-$E193_SIT
[ -n "${RB_DRY:-}" ] || e193_built_today || rb_die $RB_E_USAGE "x04clock was not built today (RB_OUT/e193-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  hs=$(e193_harness_sha); [ -n "${RB_DRY:-}" ] && hs=${hs:-HARNESS-SHA256}
  [ -n "$hs" ] || rb_die $RB_E_USAGE "harness-e193.json's sha256 could not be read in the lab clone"
  rb_probe aifoundry3
  body=$(rb_file body)
  { echo "SIT=$E193_SIT; HSHA=$hs; ROOT=$E193_ROOT"
    cat <<'EOF2'
T0=$(date +%s)
K=$ROOT/tools/claims-v3/e193
DRY=1 E193_T0=$T0 E193_HARNESS_SHA256=$HSHA bash "$K/session_e193.sh" "$SIT" < /dev/null
rc=$?
SD=build/e193/T$T0-dry
grep -E 'session start|HARNESS|preflight|binaries|deadline|smoke|main run|GATE-STOP|session end' "$SD/session.log" 2>/dev/null | cut -c1-220
H=$ROOT/build/x04clock/host/x04clock_host
REG=dry-e193-A.txt; [ "$SIT" = B ] && REG=dry-e193-B.txt
python3 -I -B "$K/check_e193.py" drycmp "$SD/smoke-runner.out" "$K/desk/dry-e193-smoke-all.txt" --host "$H"; s1=$?
python3 -I -B "$K/check_e193.py" drycmp "$SD/runner.out" "$K/desk/$REG" --host "$H"; s2=$?
echo "E193-DRY sitting $SIT rc=$rc smoke=$s1 main=$s2 calls=$(grep -c '^DRY ET_DEVICES=' "$SD/smoke-runner.out" 2>/dev/null)+$(grep -c '^DRY ET_DEVICES=' "$SD/runner.out" 2>/dev/null) manifest=$([ -s "$SD/MANIFEST.sha256" ] && echo written || echo absent)"
[ "$rc" -eq 0 ] && [ "$s1" -eq 0 ] && [ "$s2" -eq 0 ] && [ -s "$SD/MANIFEST.sha256" ]
EOF2
  } > "$body"
  rb_job_start aifoundry3 "$JOB" "$body"
  rb_say "the dry pass $JOB started on aifoundry3: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe aifoundry3
rb_job_wait aifoundry3 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && exit 0
[ "$rc" -eq 0 ] && { rb_say "the dry pass ended rc 0: $(grep -m1 '^E193-DRY' "$RB_CAP")"; exit 0; }
exit "$rc"

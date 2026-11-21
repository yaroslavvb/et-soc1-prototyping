#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day), the box step "the build" (this file is s08; step 6): E215 arm A's step 6
# (tools/claims-v3/e215/rb/s08_build_e215.sh, landed in 8bde0182, run on aifoundry3 on Thu 19 Nov 2026) for E222: start runs build_e222.sh as a detached
# runbook job on aifoundry3 (k6's rb_job_start; refused beside a session of ours or under another job; at most two starts a Pacific day:
# NO-THIRD-BUILD); wait reads its verdict (RGM-BUILT rc=0: rgm136 KERNEL OK and rgm211's tree KERNEL OK, the hosts' twelve refusals in a sandbox)
# and then, in one 60 s read, the build record (today's, BUILT, this box, arm A), each build's gate line, the harness, the preflight
# (dmcmd_audit_v2 GO) and both modules' self-checks on the box; RB_OUT/e222-built-A.txt.
#   bash tools/claims-v3/e222/rb/s08_build_e222.sh A start | wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e222.sh"
rb_init s08_build
e222_arm "${1:-}"
act=${2:-}
e222_jobs "$ARM"
JOB=$JOB_BUILD
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_build_e222.sh A start | wait" ;; esac
e222_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe "$BOX"
  f=$(rb_file count)
  { rb_prelude "$BOX"
    echo "JOB=$JOB"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E222's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E222's build starts alone"; exit 3; fi
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f build/e222-build-attempts.txt ] && n=$(grep -cE "^$TODAY .* $JOB started\$" build/e222-build-attempts.txt)
echo "E222-BUILDS-TODAY $n"
if job_ok_today "$JOB" && grep -q '^RGM-BUILT rc=0' "build/q141k/jobs/$JOB.out" 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read "$BOX" "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E222-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "rgm136 and rgm211 were built today on $BOX by E222's build: run this step's wait (a second build would replace the good one)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on $BOX today (Pacific): no E222 session today"
  fi
  body=$(rb_file body)
  { echo "JOB=$JOB"
    cat <<'EOF2'
mkdir -p build/e222-build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build/e222-build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* $JOB started\$" build/e222-build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $JOB started" >> build/e222-build-attempts.txt
L=build/e222-build-logs/$TODAY-start$k.txt
timeout 500 bash tools/claims-v3/e222/build_e222.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $JOB ended rc=$rc: $(grep -E '^RGM-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60)" >> build/e222-build-attempts.txt
exit $rc
EOF2
  } > "$body"
  rb_job_start "$BOX" "$JOB" "$body"
  rb_say "the build job $JOB started on $BOX: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe "$BOX"
rb_job_wait "$BOX" "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e222-built-$ARM.txt from the verdict line; the build record, the harness, the preflight and both self-checks, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today on $BOX: run this step's start"
cap=$RB_CAP
grep -qE '^RGM-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|KERNEL|HOST|HOSTCHECK|ETDEVICES|RGM)' "$cap" | cut -c1-220 | sed 's/^/    /'
grep -q '^RGM-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "rgm136 and rgm211 did not build on $BOX (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no E222 session today"
echo rgm > "$RB_OUT/e222-built-$ARM.txt"
rb_probe "$BOX"
f=$(rb_file checks)
{ rb_prelude "$BOX"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
python3 -B - <<'PY'
import json
r = json.load(open("build/e222rgm/BUILD-e222.json"))
k = r.get("kernels") or {}
print(f"BUILD-RECORD {r.get('verdict')} {r.get('day')} {r.get('box')} builder {r.get('builder')} arm {r.get('arm')} hosts {[(x, (k.get(x) or {}).get('host_sha256', '')[:12]) for x in ('rgm136', 'rgm211')]} checks {r.get('host_checks')}")
for x in ("rgm136", "rgm211"):
    print(f"BUILD-GATE-{x} {(k.get(x) or {}).get('kernel_gate')}")
print(f"BUILD-ETDEVICES {r.get('et_devices')}")
PY
python3 -B tools/claims-v3/e222/check_e222.py --box | tail -n 1
bash tools/claims-v3/e222/preflight_e222.sh 2>&1 | head -n 1
python3 -B tools/claims-v3/e222/e222_common.py | tail -n 1
python3 -B tools/claims-v3/e222/e222_ident.py | tail -n 1
EOF2
} > "$f"
rb_remote read "$BOX" "the build record, the harness, the preflight, both self-checks" "$f"
rb_refused
rb_has "^BUILD-RECORD BUILT $(TZ=America/Los_Angeles date +%F) $BOX builder build_e222.sh arm $ARM " || rb_die $RB_E_GATE "the build record is not today's BUILT by build_e222.sh on $BOX for arm $ARM (the line above): no session"
rb_has '^BUILD-GATE-rgm136 KERNEL OK: rgm136: ' || rb_die $RB_E_GATE "rgm136's kernel gate did not read KERNEL OK on $BOX (the line above): no session"
rb_has '^BUILD-GATE-rgm211 KERNEL OK: rgm211: rgm211.s tree: ' || rb_die $RB_E_GATE "rgm211's tree gate did not read KERNEL OK on $BOX (the line above): no session"
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness did not read OK on $BOX (the line above): no session"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on $BOX: no session"
rb_has '^E222-COMMON SELF-CHECK PASS' || rb_die $RB_E_GATE "the common module's self-check failed on $BOX: no session"
rb_has '^E222-IDENT SELF-CHECK PASS' || rb_die $RB_E_GATE "the identity module's self-check failed on $BOX: no session"
rb_say "built today on $BOX (arm $ARM): rgm136 and rgm211 into build/e222rgm (THE KERNEL GATE on rgm136 and THE TREE GATE on rgm211: KERNEL OK on each; the hosts read by their behaviour in a sandbox); harness, preflight GO and both self-checks read on the box"
exit 0

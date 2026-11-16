#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the build" (this file
# is s08): the two programs built on aifoundry2 (the box tree ~/claude/et-soc1-prototyping) and read by their BEHAVIOUR, no device opened.
# E191's step 6 (tools/claims-v3/e191/rb/s08_a1_build_e191.sh, unchanged beside it) with E194's box, job and build: ONE DETACHED JOB,
# a2-build-e194 (build_e194.sh under `timeout -k 15 500`: cmake against /opt/et into build/e194ledger and build/e194spp, nice 10, -j4; each
# kernel through THE KERNEL GATE, check_e194.py --kernel: its .text the registered one, its whole ELF a pinned one (E189's or the
# "() 15.1.0" toolchain's, made on this box) or its loadable identity the pinned one; each host by E189's hostcheck_e189.py with ET_DEVICES
# and V3_DEVICE unset; the ET_DEVICES reading RECORDED, never a gate on this one-card box), refused beside a session of ours (ours_live) or
# a runbook job (jobs_live), and only with THE QUIET DESK FLAG raised. THE BUILD-ATTEMPT COUNT (NO-THIRD-BUILD): the box's
# build/e194-build-attempts.txt counts the starts each Pacific day; a third start the same day is refused with 16, and the programs not
# built that day are SKIPPED (E194.md 12: no data, never a failed prediction). A second start only when the first built fewer than both
# programs. After the job, `wait` reads its verdict lines (LEDGER-BUILT / LEDGER-BUILD-FAILED, SPP-BUILT / SPP-BUILD-FAILED), writes
# RB_OUT/e194-built.txt (the programs built today, which step 9 passes to the session), and reads, in one 60 s call: each built program's
# record BUILD-e194.json (today, BUILT, builder build_e194.sh, box aifoundry2: the runner's box check reads the same), the harness with the
# built kernels, the preflight (dmcmd_audit GO) and both modules' self-checks. A cut WAIT CALL is not a failed build (14, "no reading").
#   RB_QUIET=<the flag file> bash tools/claims-v3/e194/rb/s08_build_e194.sh start      then      ... wait   (repeat while it says 17)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s08_build
act=${1:-}
JOB=a2-build-e194
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_build_e194.sh start | wait" ;; esac
e194_window
e194_quiet
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry2
  f=$(rb_file count)
  { rb_prelude aifoundry2
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E194's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E194's build starts alone"; exit 3; fi
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f build/e194-build-attempts.txt ] && n=$(grep -c "^$TODAY .* a2-build-e194 started\$" build/e194-build-attempts.txt)
echo "E194-BUILDS-TODAY $n"
if job_ok_today a2-build-e194 && grep -q '^LEDGER-BUILT rc=0' build/q141k/jobs/a2-build-e194.out 2>/dev/null && grep -q '^SPP-BUILT rc=0' build/q141k/jobs/a2-build-e194.out 2>/dev/null; then
  echo "BOTH-BUILT-TODAY"
fi
EOF2
  } > "$f"
  rb_remote read aifoundry2 "the build-attempt count today and the last build's verdicts" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E194-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BOTH-BUILT-TODAY' && rb_die $RB_E_USAGE "both programs were built today: run this step's wait (a second build would remove the good ones)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry2 today (Pacific): the programs not built today are SKIPPED (E194.md 12: no data, never a failed prediction); go on with what step 6's wait recorded, or no session"
  fi
  body=$(rb_file body)
  cat > "$body" <<'EOF2'
mkdir -p build/e194-build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build/e194-build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* a2-build-e194 started\$" build/e194-build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a2-build-e194 started" >> build/e194-build-attempts.txt
L=build/e194-build-logs/$TODAY-start$k.txt
timeout -k 15 500 nice -n 10 bash tools/claims-v3/e194/build_e194.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a2-build-e194 ended rc=$rc: $(grep -E '^(LEDGER|SPP)-(BUILT|BUILD-FAILED)' "$L" | cut -c1-40 | tr '\n' ' ')" >> build/e194-build-attempts.txt
exit $rc
EOF2
  rb_job_start aifoundry2 "$JOB" "$body"
  rb_say "the build job $JOB started on aifoundry2: run this step's wait (bounded) until it ends"
  exit 0
fi
# wait
rb_probe aifoundry2
rb_job_wait aifoundry2 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: RB_OUT/e194-built.txt from the verdict lines; the build records, the harness with the built kernels, the preflight and both self-checks, one 60 s read"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
if ! grep -qE '^(LEDGER|SPP)-(BUILT|BUILD-FAILED)' "$cap"; then
  rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict lines (a cut wait is not a failed build): wait again"
fi
built=""
grep -q '^LEDGER-BUILT rc=0' "$cap" && built="ledger"
grep -q '^SPP-BUILT rc=0' "$cap" && built="${built:+$built,}spp"
grep -E '^(COMPILER|LEDGER|SPP)' "$cap" | cut -c1-200 | sed 's/^/    /'
if [ -z "$built" ]; then
  rb_die $RB_E_GATE "neither program built (the lines above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no session today"
fi
echo "$built" > "$RB_OUT/e194-built.txt"
rb_probe aifoundry2
f=$(rb_file checks)
{ rb_prelude aifoundry2
  echo "BUILT=$built"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
TODAY=$(TZ=America/Los_Angeles date +%F)
for p in ${BUILT//,/ }; do
  d=build/e194ledger; [ "$p" = spp ] && d=build/e194spp
  python3 -B - "$d/BUILD-e194.json" "$p" "$TODAY" <<'PY'
import json, sys
p, prog, today = sys.argv[1:4]
try:
    r = json.load(open(p))
except (OSError, ValueError):
    r = {}
ok = r.get("builder") == "build_e194.sh" and r.get("verdict") == "BUILT" and r.get("day") == today and r.get("box") == "aifoundry2"
print(f"BUILD-RECORD {prog} {'ok' if ok else 'NOT ok'}: builder {r.get('builder')}, {r.get('verdict')}, {r.get('day')}, box {r.get('box')}")
PY
done
python3 -B tools/claims-v3/e194/check_e194.py --box --built "$BUILT" | tail -n 1
bash tools/claims-v3/e194/preflight_e194.sh 2>&1 | head -n 1
python3 -B tools/claims-v3/e194/e194_common.py | tail -n 1
python3 -B tools/claims-v3/e194/e194_ident.py | tail -n 1
EOF2
} > "$f"
rb_remote read aifoundry2 "the build records, the harness with today's kernels, the preflight, both self-checks" "$f"
rb_refused
for p in ${built//,/ }; do
  rb_has "^BUILD-RECORD $p ok: " || rb_die $RB_E_GATE "$p's build record is not today's BUILT by build_e194.sh on aifoundry2 (the line above): no session on these binaries"
done
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the harness with today's built kernels did not read OK (the line above): no session on these binaries"
rb_has '^dmcmd_audit: GO' || rb_die $RB_E_GATE "the preflight is not GO on the box: no session"
rb_has '^E194-COMMON SELF-CHECK PASS' || rb_die $RB_E_GATE "the common module's self-check failed on the box: no session"
rb_has '^E194-IDENT SELF-CHECK PASS' || rb_die $RB_E_GATE "the identity module's self-check failed on the box: no session"
rb_say "built today on aifoundry2: $built (the other program, if any, is SKIPPED today); the build records, harness, preflight GO and both self-checks read on the box"
exit 0

#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "the build" (this file is s08): BOTH HOSTS AND THE
# KERNEL built on aifoundry3 in E196's own root, no device opened. E192's step 6's form (tools/claims-v3/e192/rb/s08_a3_build_e192.sh): ONE
# DETACHED JOB, a3-build-e196 (build_e196.sh under `timeout -k 15 900`: cmake with the box's /opt/et into build/sparsity-lab (the lab's
# unchanged workloads/sparsity) and build/x14 (the request's proposal/src); both kernels' .text 8798e43c... (a gate); the hosts by their
# behaviour (every registered command parses; refusals before anything); make_x14.py --check and arms.json; the hashes recorded in
# build/BUILD-E196.txt), refused beside a session of ours (ours_live) or a runbook job (jobs_live). THE BUILD-ATTEMPT COUNT: E196's root's
# build-attempts.txt counts the starts each Pacific day; AT MOST TWO BUILD STARTS A PACIFIC DAY: a third is refused with 16 (NO-THIRD-BUILD:
# no session that day). A second start is allowed only when the first did not build. Each start's log is kept (build-logs/<day>-start<k>.txt);
# an earlier build directory is moved aside, never removed. After the job, `wait` reads its verdict (E196-BUILT / E196-BUILD-FAILED), then,
# in one 60 s read, THE BOX'S TOOLS AND PINS (boxcheck_e196.sh), and writes RB_OUT/e196-built.txt (the hashes), which steps 8 and 9 read.
# A cut WAIT CALL is not a failed build (14, "no reading": wait again).
#   bash tools/claims-v3/e196/rb/s08_a3_build_e196.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
rb_init s08_a3_build
act=${1:-}
JOB=a3-build-e196
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_a3_build_e196.sh start | wait" ;; esac
e196_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  f=$(rb_file count)
  { rb_prelude aifoundry3
    echo "ER=$E196_R"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E196's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E196's build starts alone"; exit 3; fi
[ -d "$ER/tools/claims-v3/e196" ] || { echo "REFUSED: E196's files are not synced (step 5)"; exit 3; }
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f "$ER/build-attempts.txt" ] && n=$(grep -c "^$TODAY .* a3-build-e196 started\$" "$ER/build-attempts.txt")
echo "E196-BUILDS-TODAY $n"
if job_ok_today a3-build-e196 && grep -q '^E196-BUILT rc=0' build/q141k/jobs/a3-build-e196.out 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read aifoundry3 "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E196-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "E196 was built today: run this step's wait (a second build would move the good one aside)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry3 today (Pacific): no E196 session today (E196.md section 11: no data, never a failed check)"
  fi
  body=$(rb_file body)
  { echo "ER=$E196_R"
    cat <<'EOF2'
cd "$ER" || exit 3
mkdir -p build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* a3-build-e196 started\$" build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e196 started" >> build-attempts.txt
L=build-logs/$TODAY-start$k.txt
timeout -k 15 900 bash tools/claims-v3/e196/build_e196.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e196 ended rc=$rc: $(grep -E '^E196-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60)" >> build-attempts.txt
exit $rc
EOF2
  } > "$body"
  rb_job_start aifoundry3 "$JOB" "$body"
  rb_say "the build job $JOB started on aifoundry3: run this step's wait (bounded) until it ends"
  exit 0
fi
# wait
rb_probe aifoundry3
rb_job_wait aifoundry3 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: the verdict line; the box's tools and pins (boxcheck_e196.sh), a 60 s read; RB_OUT/e196-built.txt"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
grep -qE '^E196-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|PYTHON|E196-|kernel_|lab_|x14_|hosts_|arm_table)' "$cap" | cut -c1-200 | sed 's/^/    /'
grep -q '^E196-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "the build failed (the line above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no session today"
grep -E '^(kernel_elf_sha256_(lab|x14)|kernel_text_sha256_(lab|x14)|lab_host_sha256|x14_host_sha256|kernel_elf_same_as_desk_build|hosts_behaviour|E196-BUILT) ' "$cap" > "$RB_OUT/e196-built.txt.new"
rb_probe aifoundry3
f=$(rb_file checks)
{ rb_prelude aifoundry3
  echo "ER=$E196_R"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
cd "$ER" || { echo "REFUSED: no E196 root"; exit 3; }
bash tools/claims-v3/e196/boxcheck_e196.sh 2>&1 | cut -c1-300
EOF2
} > "$f"
rb_remote read aifoundry3 "the box's tools and pins after the build (boxcheck_e196.sh)" "$f"
rb_refused
rb_has '^BOXCHECK-E196 OK: ' || { rm -f "$RB_OUT/e196-built.txt.new"; rb_die $RB_E_GATE "the box's tools or pins did not read OK (the lines above): no session on this build"; }
grep -E '^(host:|sampler:|E196-PREFLIGHT)' "$RB_CAP" | cut -c1-200 >> "$RB_OUT/e196-built.txt.new"
mv "$RB_OUT/e196-built.txt.new" "$RB_OUT/e196-built.txt"
rb_say "built today on aifoundry3 (both hosts and the kernel; hashes in RB_OUT/e196-built.txt); the box's tools and pins read OK"
exit 0

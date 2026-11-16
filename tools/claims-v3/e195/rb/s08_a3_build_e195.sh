#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the build" (this file is s08): the x09mem host and
# kernel built on aifoundry3 from the registered source, no device opened. E192's step 6's form (rb/s08_a3_build_e192.sh): ONE DETACHED
# JOB, a3-build-e195 (build_e195.sh under `timeout -k 15 900`: cmake with the box's /opt/et into E195's root, build/x09mem; check_elf.py
# CHECK OK; the loops' heads; the hashes beside the registration's desk build; the host's --list --json and --list byte for byte the
# registration's arm table; make_x09.py --check --no-ms from the host's bytes against gen-e195-noms/ where the tree has numpy; the box's
# two tools linked into E195's root and read; the record build/x09mem-built.txt), refused beside a session of ours (ours_live) or a runbook
# job (jobs_live). THE BUILD-ATTEMPT COUNT: E195's root's build-attempts.txt counts the starts each Pacific day; AT MOST TWO BUILD STARTS A
# PACIFIC DAY: a third is refused with 16 (NO-THIRD-BUILD: no session that day). A second start is allowed only when the first did not
# build. Each start's log is kept (build-logs/<day>-start<k>.txt); an earlier build directory is moved aside, never removed. After the job,
# `wait` reads its verdict (X09MEM-BUILT / X09MEM-BUILD-FAILED), then, in one 60 s read, THE BOX'S PINS AND TOOLS (harness_e195.py --box
# in E195's root; the host's name aifoundry3; one card node and the lock file; et-who --check answering; the record), and writes
# RB_OUT/e195-built.txt (the hashes), which steps 8 and 9 read. A cut WAIT CALL is not a failed build (14, "no reading": wait again).
#   bash tools/claims-v3/e195/rb/s08_a3_build_e195.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s08_a3_build
act=${1:-}
JOB=a3-build-e195
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_a3_build_e195.sh start | wait" ;; esac
e195_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry3
  f=$(rb_file count)
  { rb_prelude aifoundry3
    echo "ER=$E195_R"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E195's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E195's build starts alone"; exit 3; fi
[ -d "$ER/tools/claims-v3/e195" ] || { echo "REFUSED: E195's files are not synced (step 5)"; exit 3; }
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f "$ER/build-attempts.txt" ] && n=$(grep -c "^$TODAY .* a3-build-e195 started\$" "$ER/build-attempts.txt")
echo "E195-BUILDS-TODAY $n"
if job_ok_today a3-build-e195 && grep -q '^X09MEM-BUILT rc=0' build/q141k/jobs/a3-build-e195.out 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read aifoundry3 "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E195-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "E195 was built today: run this step's wait (a second build would move the good one aside)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry3 today (Pacific): no E195 session today (E195.md section 12: no data, never a failed check)"
  fi
  body=$(rb_file body)
  { echo "ER=$E195_R"
    cat <<'EOF2'
cd "$ER" || exit 3
mkdir -p build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* a3-build-e195 started\$" build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e195 started" >> build-attempts.txt
L=build-logs/$TODAY-start$k.txt
timeout -k 15 900 bash tools/claims-v3/e195/build_e195.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e195 ended rc=$rc: $(grep -E '^X09MEM-(BUILT|BUILD-FAILED)' "$L" | tail -n 1 | cut -c1-60)" >> build-attempts.txt
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
[ -n "${RB_DRY:-}" ] && { rb_say "then: the verdict line; the box's pins and tools, a 60 s read; RB_OUT/e195-built.txt"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
grep -qE '^X09MEM-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|PYTHON|X09MEM|host |kernel|ettelem |sparsity_host |same_as|check_elf|generator|heater:|loops_e195)' "$cap" | cut -c1-220 | sed 's/^/    /'
grep -q '^X09MEM-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "the build failed (the line above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no session today"
grep -E '^(X09MEM-BUILT |host |kernel |kernel_text |kernel_disassembly |ettelem |sparsity_host |same_as_registration_desk_build |check_elf |generator )' "$cap" > "$RB_OUT/e195-built.txt.new"
rb_probe aifoundry3
f=$(rb_file checks)
{ rb_prelude aifoundry3
  echo "ER=$E195_R"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
cd "$ER" || { echo "REFUSED: no E195 root"; exit 3; }
bad=""
h=$(python3 -I -B tools/claims-v3/e195/harness_e195.py --box --root . 2>&1 | tail -n 1)
echo "harness: $h"; case "$h" in "HARNESS OK: "*) ;; *) bad="$bad harness" ;; esac
[ "$(hostname)" = aifoundry3 ] || bad="$bad hostname"
ops=$(ls -1d /dev/et*_ops 2>/dev/null | grep -cE '^/dev/et[0-9]+_ops$'); echo "ops nodes: $ops"; [ "$ops" = 1 ] && [ -e /dev/et0_ops ] || bad="$bad ops-nodes"
[ -e /run/lock/etsoc-shire0.lock ] || bad="$bad lock-file"
et-who --check > /dev/null 2>&1; w=$?; echo "et-who --check: exit $w (0 free, 1 held, 2 failed)"; [ "$w" -eq 0 ] || [ "$w" -eq 1 ] || bad="$bad et-who"
[ -f build/x09mem-built.txt ] && grep -q '^X09MEM-BUILT ' build/x09mem-built.txt || bad="$bad record"
[ -L build/ettelem/ettelem ] && [ -L build/sparsity/host/sparsity_host ] || bad="$bad tools"
[ -z "$bad" ] && echo "BOXCHECK-E195 OK: E195's root at its pins, aifoundry3, one card node and its lock file, et-who --check answers, today's record, the two tools linked" || echo "BOXCHECK-E195 FAIL:$bad"
EOF2
} > "$f"
rb_remote read aifoundry3 "the box's pins and tools after the build" "$f"
rb_refused
rb_has '^BOXCHECK-E195 OK: ' || { rm -f "$RB_OUT/e195-built.txt.new"; rb_die $RB_E_GATE "the box's pins or tools did not read OK (the lines above): no session on this build"; }
mv "$RB_OUT/e195-built.txt.new" "$RB_OUT/e195-built.txt"
rb_say "built today on aifoundry3 (the kernel and the host; hashes in RB_OUT/e195-built.txt); the box's pins and tools read OK"
exit 0

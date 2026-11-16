#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum; E192's file, a6fe5c20, unchanged beside it, ported to aifoundry1 card 1), the box step "the build" (this file is s08): the intbits host and
# kernel built on aifoundry1 from the registered source, no device opened. E189's step 6's form (rb/s08_a3_build_e189.sh): ONE DETACHED
# JOB, a1-build-e199 (build_e199.sh under `timeout -k 15 900`: cmake with the box's /opt/et into E199's root, build/intbits; check_elf.py
# "loops 16, bad 0", E192's loop_order_e192.py 16 of 16; the host's --list --json and --list byte for byte E192's arm table; ET_DEVICES in
# the host and the device layer; the hashes recorded beside E192's, reported), refused beside a
# session of ours (ours_live) or a runbook job (jobs_live). THE BUILD-ATTEMPT COUNT: E199's root's build-attempts.txt counts the starts each
# Pacific day; AT MOST TWO BUILD STARTS A PACIFIC DAY: a third is refused with 16 (NO-THIRD-BUILD: no session that day). A second start is
# allowed only when the first did not build. Each start's log is kept (build-logs/<day>-start<k>.txt); an earlier build directory is moved
# aside, never removed. After the job, `wait` reads its verdict (INTBITS-BUILT / INTBITS-BUILD-FAILED), then, in one 60 s read, THE BOX'S
# TOOLS AND PINS (boxcheck_e199.sh: the host's name aifoundry1, aifoundry1's two cards' nodes and card 1's lock file, et-who --check answering, the selection (ET_DEVICES) in the host, the reader and the heater, the sampler, E78's
# heater and its option parser by behaviour, the per-sensor sampler at its pin, every synced file at its pin, today's build record, the
# preflight's plain chain GO), and writes RB_OUT/e199-built.txt (the hashes), which steps 8 and 9 read. A cut WAIT CALL is not a failed
# build (14, "no reading": wait again).
#   bash tools/claims-v3/e199/rb/s08_a1_build_e199.sh start      then      ... wait   (repeat while it says 17; after its 14, wait again)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s08_a1_build
act=${1:-}
JOB=a1-build-e199
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s08_a1_build_e199.sh start | wait" ;; esac
e199_window
if [ "$act" = start ]; then
  rb_need_start
  rb_probe aifoundry1
  f=$(rb_file count)
  { rb_prelude aifoundry1
    echo "ER=$E199_R"
    cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E199's build never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E199's build starts alone"; exit 3; fi
[ -d "$ER/tools/claims-v3/e199" ] || { echo "REFUSED: E199's files are not synced (step 5)"; exit 3; }
TODAY=$(TZ=America/Los_Angeles date +%F)
n=0; [ -f "$ER/build-attempts.txt" ] && n=$(grep -c "^$TODAY .* a1-build-e199 started\$" "$ER/build-attempts.txt")
echo "E199-BUILDS-TODAY $n"
if job_ok_today a1-build-e199 && grep -q '^INTBITS-BUILT rc=0' build/q141k/jobs/a1-build-e199.out 2>/dev/null; then echo "BUILT-TODAY"; fi
EOF2
  } > "$f"
  rb_remote read aifoundry1 "the build-attempt count today and the last build's verdict" "$f"
  rb_refused
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the count read exited $RB_RC: nothing started (no reading)"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(rb_val '^E199-BUILDS-TODAY ([0-9]+)$')
    [ -n "$n" ] || rb_die $RB_E_FAIL "no count came back: nothing started"
    rb_has '^BUILT-TODAY' && rb_die $RB_E_USAGE "E199 was built today: run this step's wait (a second build would move the good one aside)"
    [ "$n" -lt 2 ] || rb_die $RB_E_GATE "NO-THIRD-BUILD: $n builds were started on aifoundry1 today (Pacific): no E199 session today (E199.md section 11: no data, never a failed check)"
  fi
  body=$(rb_file body)
  { echo "ER=$E199_R"
    cat <<'EOF2'
cd "$ER" || exit 3
mkdir -p build-logs
TODAY=$(TZ=America/Los_Angeles date +%F)
k=1; [ -f build-attempts.txt ] && k=$(( $(grep -c "^$TODAY .* a1-build-e199 started\$" build-attempts.txt) + 1 ))
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a1-build-e199 started" >> build-attempts.txt
L=build-logs/$TODAY-start$k.txt
timeout -k 15 900 bash tools/claims-v3/e199/build_e199.sh > "$L" 2>&1
rc=$?
cat "$L"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a1-build-e199 ended rc=$rc: $(grep -E '^INTBITS-(BUILT|BUILD-FAILED)' "$L" | cut -c1-60)" >> build-attempts.txt
exit $rc
EOF2
  } > "$body"
  rb_job_start aifoundry1 "$JOB" "$body"
  rb_say "the build job $JOB started on aifoundry1: run this step's wait (bounded) until it ends"
  exit 0
fi
# wait
rb_probe aifoundry1
rb_job_wait aifoundry1 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then: the verdict line; the box's tools and pins (boxcheck_e199.sh), a 60 s read; RB_OUT/e199-built.txt"; exit 0; }
[ "$rc" -eq "$RB_E_AGAIN" ] && exit $RB_E_AGAIN
[ "$rc" -eq "$RB_E_USAGE" ] && rb_die $RB_E_USAGE "no build job was started today: run this step's start"
cap=$RB_CAP
grep -qE '^INTBITS-(BUILT|BUILD-FAILED)' "$cap" || rb_die $RB_E_FAIL "no reading: the wait came back without the build's verdict line (a cut wait is not a failed build): wait again"
grep -E '^(COMPILER|PYTHON|INTBITS|kernel_|host_|same_as|check_elf|loop_order|selection)' "$cap" | cut -c1-200 | sed 's/^/    /'
grep -q '^INTBITS-BUILT rc=0' "$cap" || rb_die $RB_E_GATE "the build failed (the line above): run start once more if this was today's first build (one re-run); after a second, NO-THIRD-BUILD: no session today"
grep -E '^(kernel_elf_sha256|kernel_text_sha256|host_sha256|same_as_e192_desk_build|same_as_e192_card_day_build|check_elf|loop_order|selection) ' "$cap" > "$RB_OUT/e199-built.txt.new"
rb_probe aifoundry1
f=$(rb_file checks)
{ rb_prelude aifoundry1
  echo "ER=$E199_R"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX"; exit 3; fi
cd "$ER" || { echo "REFUSED: no E199 root"; exit 3; }
bash tools/claims-v3/e199/boxcheck_e199.sh 2>&1 | cut -c1-300
EOF2
} > "$f"
rb_remote read aifoundry1 "the box's tools and pins after the build (boxcheck_e199.sh)" "$f"
rb_refused
rb_has '^BOXCHECK-E199 OK: ' || { rm -f "$RB_OUT/e199-built.txt.new"; rb_die $RB_E_GATE "the box's tools or pins did not read OK (the lines above): no session on this build"; }
grep -E '^(host:|heater:|reader:|selection:|card nodes:|PVT-CHAIN|PLAIN-CHAIN)' "$RB_CAP" | cut -c1-200 >> "$RB_OUT/e199-built.txt.new"
mv "$RB_OUT/e199-built.txt.new" "$RB_OUT/e199-built.txt"
rb_say "built today on aifoundry1 (the kernel and the host; hashes in RB_OUT/e199-built.txt); the box's tools and pins read OK"
exit 0

#!/usr/bin/env bash
# E185, step 22 v2: collect E185 at the desk, gate it, and only then score it, on the Intel (it needs this Mac's tree and its ssh to the box),
# at nice 10 with at most 2 jobs, every copy bounded, after the session has ended (s20_wait_e185.sh read its end) and step 12's end window.
# It is s22_collect_e185.sh (33cdccf6, which stays as committed) with the E185 kit verifier's faults 2, 4 and 5 fixed (Fri 6 Nov 2026; the
# kit's README.md.dated-note-1.md), each marked v2. In order:
#   1. before any box call, the files as committed: M11's SHA256SUMS-score-m11-v4, -a9 and -score-m11-v3, E185's kit-e185.sha256, this
#      runbook's SHA256SUMS-rb-e185 and the kit's SHA256SUMS-note1, else 16 (nothing collected);
#   2. v2: the collector collect_e185.sh: a pass directory copied only when it is on the box (no failed copy after an A6-1 stop or a failed
#      smoke), the session-written files kept only when the session's own last block records them (the rest set aside in
#      logs/not-this-session/), the check of C, NO scorer (a failed copy: 14);
#   3. the session's own gates from its marks (cclaunch_e185.py --gates-only): F0-STOPPED (A6-1) or G0-REFUSED (G0-A6 with A8-4): 16;
#   4. v2: the session's own stops from its log (its last block in logs/session.log), which no mark names: "the smoke or its gate failed"
#      (SMOKE-STOPPED), "STOP file: no measured pass" (STOP-FILE), "no device opened" (NO-DEVICE), or no session log at all: 16, nothing
#      scored, the collection kept as the stop's evidence;
#   5. v3.1's cc_gate (ccdone_q142s.py: the check finished, written since this step began), else 14;
#   6. the launch gate (cclaunch_e185.py: every launch the marks record checked, process by process, distinct t_start_ms), else 14;
#   7. v2: the login scrub's --check in EVERY directory of the data directory, each .gz unpacked beside it outside the repo
#      (rb/scrub_all_e185.py; v1 read logs/ only), and the desk-path gate over the collection, else 16;
#   8. no scored file in the data directory yet (nor a staging file), else 16;
#   9. ONLY NOW the score v2 (score_e185.sh: M11's scorer v4 on E176's committed pass and E185's measured pass with its smoke named and
#      its host windows read; v4 writes nothing before its own gate check and leaves no file on a refusal); "score rc=0" must be read, else
#      14 (and no scored file is left: the step checks);
#  10. the desk-path gate over the scored files, else 16; then "E185 collected and scored".
# It commits nothing. Desk-test stand-ins (E185_COLLECT, E185_SCORE) are read only with RB_DESKTEST=1; set without it, the step refuses (10).
#
#   bash tools/claims-v3/e185/rb/s22_collect_e185.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
D=docs/reports/data/$DAY-e185-m11-session3-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && { [ -n "${E185_COLLECT:-}" ] || [ -n "${E185_SCORE:-}" ]; }; then
  rb_die $RB_E_USAGE "E185_COLLECT and E185_SCORE are desk-test stand-ins, read only with RB_DESKTEST=1: unset them"
fi
C181=${E185_COLLECT:-tools/claims-v3/e185/collect_e185.sh}
S181=${E185_SCORE:-tools/claims-v3/e185/score_e185.sh}
scrub_all() {  # v2: E164's scrub, --check only (it rewrites nothing), in every directory of the data directory, .gz unpacked outside the repo
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "every directory of $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_e185.sh)"; return 0; fi
  rb_local desk local "et-who lines in every directory of $d (E164's scrub, --check; .gz unpacked outside the repo)" "$RB_PY" -B \
    "$RB_DIR/scrub_all_e185.py" "$d" --owner "$own" --work "$RB_OUT/scrub-$(date +%H%M%S)-$$"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d (the LOGIN-LEFT lines above): scrub that directory (scrub_etwho_e164.py without --check) before any commit"
}
for l in tools/claims-v3/m11/SHA256SUMS-score-m11-v5 tools/claims-v3/m11/SHA256SUMS-score-m11-v4 tools/claims-v3/m11/SHA256SUMS-a10 \
         tools/claims-v3/e185/SHA256SUMS-e185-registration tools/claims-v3/e185/SHA256SUMS-e185-kit tools/claims-v3/e185/rb/SHA256SUMS-rb-e185; do
  rb_local read local "the files as committed ($(basename "$l"))" shasum -a 256 -c "$l"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "a file of $l differs from its committed hash (the FAILED lines above): nothing was collected"
done
rb_probe aifoundry3
t_cc=$(date +%s)
rb_local desk aifoundry3 "collect_e185.sh (a presence read, then its rsyncs bounded at 300/120 s; the session's files by its last block; the check of C; no scorer)" \
  env PY=/usr/bin/python3 nice -n 10 bash "$C181" "$D"
if [ -z "${RB_DRY:-}" ] && rb_has '^COPY-BACK (DIFFERS|EXTRA|NO-MANIFEST|NO-T0)'; then                          # e185: the exact copy-back
  rb_die $RB_E_GATE "$(grep -m1 -E '^COPY-BACK (DIFFERS|EXTRA|NO-MANIFEST|NO-T0)' "$RB_CAP" | cut -c1-300): the copy is not the session's; remove $D, read the box (read-only), then collect again"
fi
if [ -z "${RB_DRY:-}" ] && rb_has '^rsync .* rc=[0-9]+'; then
  rb_die $RB_E_FAIL "a copy inside the collector failed ($(grep -m1 -E '^rsync .* rc=' "$RB_CAP")): $D holds a partial copy; remove $D, then run this step again"
fi
[ -z "${RB_DRY:-}" ] && rb_has '^refusing: ' && rb_die $RB_E_GATE "$(grep -m1 '^refusing: ' "$RB_CAP")"
rb_local read local "E185's own gates (cclaunch_e185.py --gates-only)" "$RB_PY" -B "$RB_DIR/cclaunch_e185.py" --gates-only "$D"
if [ -z "${RB_DRY:-}" ] && rb_has '^(F0-STOPPED|G0-REFUSED) '; then    # cclaunch's exit 5; rb_run.py reports any non-zero exit as 14
  rb_die $RB_E_GATE "$(grep -m1 -E '^(F0-STOPPED|G0-REFUSED)' "$RB_CAP"). Nothing is scored, and no scored file was written; $D is the gate's evidence (a records round decides its commit)"
fi
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the gates' reading exited $RB_RC: read the output above"
if [ -n "${RB_DRY:-}" ]; then   # v2 step 4
  echo "--- gate: the session's own stops from its last block in $D/logs/session.log (SMOKE-STOPPED, STOP-FILE, NO-DEVICE, or no log): 16"
else
  SL=$D/logs/session.log
  [ -f "$SL" ] || rb_die $RB_E_GATE "NO-SESSION-LOG: the box held no build/e185/T<T0>/session.log, so no real session of E185 ran there: nothing to score; $D is the evidence"
  blk=$(awk '/session start/ {b = ""} {b = b $0 "\n"} END {printf "%s", b}' "$SL")
  if printf '%s' "$blk" | grep -q 'the smoke or its gate failed: no measured pass'; then
    rb_die $RB_E_GATE "SMOKE-STOPPED: the session's last block says the smoke or its gate failed, so no measured pass ran: nothing to score; $D is the stop's evidence (logs/session.log, logs/smoke-gate.json)"
  fi
  if printf '%s' "$blk" | grep -q 'STOP file: no measured pass'; then
    rb_die $RB_E_GATE "STOP-FILE: the session's last block says a STOP file stopped it before the measured pass: nothing to score; $D is the stop's evidence"
  fi
  if printf '%s' "$blk" | grep -q 'no device opened'; then
    rb_die $RB_E_GATE "NO-DEVICE: the session's last block ended at a session gate with no device opened ($(printf '%s' "$blk" | grep -m1 'no device opened' | cut -c1-200)): nothing to score"
  fi
  rb_say "the session's last block names no stop before the measured pass"
fi
rb_local read local "E185's checks of C finished (ccdone_q142s.py)" "$RB_PY" -B "$RB_V31/ccdone_q142s.py" --since "$t_cc" "$D/ccheck/ccheck-all.json"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E185's check of C did not finish (the CCHECK- lines above): nothing is scored. Read its ccheck output, remove what the collector wrote, then collect again"
rb_local read local "E185's passes carry their C logs, and the check read every launch their marks record (cclaunch_e185.py)" "$RB_PY" -B \
  "$RB_DIR/cclaunch_e185.py" "$D"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E185's check of C does not cover the launches its passes' marks record (the MISSING-/NO-LAUNCH/COUNT-/ORPHAN lines above): nothing is scored. Find the C log on the box (read-only), remove what the collector wrote, then collect again"
scrub_all "$D" aifoundry3
rb_nopath "$D"
if [ -z "${RB_DRY:-}" ]; then
  for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl scored-m11-lines.jsonl.staging; do
    [ -e "$D/$f" ] && rb_die $RB_E_GATE "$D/$f exists before the score: something wrote a score before the gates; remove $D and collect again"
  done
  for h in host-start.out host-end.out; do [ -f "$D/logs/$h" ] || rb_say "A6-5: logs/$h was not collected (step 12 not run?): the scorer reports it as not read"; done
fi
rb_local desk local "score_e185.sh (M11's scorer v4, after every gate)" env PY=/usr/bin/python3 bash "$S181" "$D"
if ! rb_has '^score rc=0$'; then
  left=""
  [ -z "${RB_DRY:-}" ] && for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl scored-m11-lines.jsonl.staging; do [ -e "$D/$f" ] && left="$left $f"; done
  rb_die $RB_E_FAIL "M11's scorer did not read rc 0: read the output above (the gates passed; the collection stands; scored files left:${left:- none})"
fi
rb_nopath "$D/scored-m11.json" "$D/scored-m11.md" "$D/scored-m11-lines.jsonl"
rb_say "E185 collected and scored: $D (the copy-back exact; scored-m11.json, scored-m11.md, scored-m11-lines.jsonl, written after the gates: A10's reading, E185's rules, A6-5's host readings)"

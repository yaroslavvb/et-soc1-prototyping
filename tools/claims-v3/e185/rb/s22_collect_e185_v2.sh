#!/usr/bin/env bash
# E185, the runbook's step 14 (the collection), v2: the kit's dated note 1 (KIT.md.dated-note-1.md, Sat 7 Nov 2026). It is
# s22_collect_e185.sh (460c352f, which stays as committed) with these changes, each marked v2:
#   - it runs the collector v2, ../collect_e185_v2.sh: the two pass directories copied by name (an earlier try's p18501.try1 and a block's
#     p185xx.attempt-* stay on the box and are named, not copied: the kit verifier's major fault 1), and a data directory that holds any
#     file refused before any box call (its nit (b));
#   - the lists it checks before any box call, named here as the code checks them: M11's SHA256SUMS-score-m11-v5, -score-m11-v4 and -a10;
#     E185's SHA256SUMS-e185-registration, -e185-kit and -e185-a1 (E185's dated amendment A1, df4e6763); this runbook's SHA256SUMS-rb-e185;
#     and the kit note's SHA256SUMS-e185-kit-note1 (else 16, nothing collected). v1's header named lists it does not check (nit (a));
#   - the collector's "left on the box" line goes into the runbook's log, for the records;
#   - after a failed score, the message says how to collect again: remove the data directory first (the collector v2 refuses a used one).
# Everything else is v1's, line for line. In order: the lists; the collector (a failed copy: 14; a copy-back fault: 16; a refusal: 16);
# the session's own gates from its marks (cclaunch_e185.py --gates-only: F0-STOPPED or G0-REFUSED, 16); the session's own stops from its
# last block in logs/session.log (SMOKE-STOPPED, STOP-FILE, NO-DEVICE, or no session log: 16); v3.1's cc_gate (else 14); the launch gate
# (else 14); E164's scrub in every directory (else 16); the desk-path gate (else 16); no scored file yet (else 16); ONLY THEN M11's
# scorer v5 (score_e185.sh: A10's reading primary, E185's rules; "score rc=0" must be read, else 14); the desk-path gate over the
# scored files (else 16); "E185 collected and scored". It commits nothing. The desk-test stand-ins E185_COLLECT and E185_SCORE are read
# only with RB_DESKTEST=1; set without it, the step refuses (10).
#
#   bash tools/claims-v3/e185/rb/s22_collect_e185_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
rb_init s22_collect_v2
rb_window
DAY=$RB_DAY
D=docs/reports/data/$DAY-e185-m11-session3-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && { [ -n "${E185_COLLECT:-}" ] || [ -n "${E185_SCORE:-}" ]; }; then
  rb_die $RB_E_USAGE "E185_COLLECT and E185_SCORE are desk-test stand-ins, read only with RB_DESKTEST=1: unset them"
fi
C185=${E185_COLLECT:-tools/claims-v3/e185/collect_e185_v2.sh}                                                  # v2
S185=${E185_SCORE:-tools/claims-v3/e185/score_e185.sh}
scrub_all() {  # E164's scrub, --check only (it rewrites nothing), in every directory of the data directory, .gz unpacked outside the repo
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "every directory of $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_e185.sh)"; return 0; fi
  rb_local desk local "et-who lines in every directory of $d (E164's scrub, --check; .gz unpacked outside the repo)" "$RB_PY" -B \
    "$RB_DIR/scrub_all_e185.py" "$d" --owner "$own" --work "$RB_OUT/scrub-$(date +%H%M%S)-$$"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d (the LOGIN-LEFT lines above): scrub that directory (scrub_etwho_e164.py without --check) before any commit"
}
for l in tools/claims-v3/m11/SHA256SUMS-score-m11-v5 tools/claims-v3/m11/SHA256SUMS-score-m11-v4 tools/claims-v3/m11/SHA256SUMS-a10 \
         tools/claims-v3/e185/SHA256SUMS-e185-registration tools/claims-v3/e185/SHA256SUMS-e185-kit tools/claims-v3/e185/SHA256SUMS-e185-a1 \
         tools/claims-v3/e185/rb/SHA256SUMS-rb-e185 tools/claims-v3/e185/SHA256SUMS-e185-kit-note1; do                 # v2: A1's and the note's
  rb_local read local "the files as committed ($(basename "$l"))" shasum -a 256 -c "$l"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "a file of $l differs from its committed hash (the FAILED lines above): nothing was collected"
done
rb_probe aifoundry3
t_cc=$(date +%s)
rb_local desk aifoundry3 "collect_e185_v2.sh (a refusal of a used data directory; one presence read; the two pass directories by name, rsyncs bounded at 300/120 s; the exact copy-back; the check of C; no scorer)" \
  env PY=/usr/bin/python3 nice -n 10 bash "$C185" "$D"
if [ -z "${RB_DRY:-}" ] && rb_has '^refusing: '; then                                                              # v2: before the copy faults
  rb_die $RB_E_GATE "$(grep -m1 '^refusing: ' "$RB_CAP" | cut -c1-300)"
fi
if [ -z "${RB_DRY:-}" ] && rb_has '^COPY-BACK (DIFFERS|EXTRA|NO-MANIFEST|NO-T0)'; then
  rb_die $RB_E_GATE "$(grep -m1 -E '^COPY-BACK (DIFFERS|EXTRA|NO-MANIFEST|NO-T0)' "$RB_CAP" | cut -c1-300): the copy is not the session's; remove $D, read the box (read-only), then collect again"
fi
if [ -z "${RB_DRY:-}" ] && rb_has '^rsync .* rc=[0-9]+'; then
  rb_die $RB_E_FAIL "a copy inside the collector failed ($(grep -m1 -E '^rsync .* rc=' "$RB_CAP")): $D holds a partial copy; remove $D, then run this step again"
fi
if [ -z "${RB_DRY:-}" ] && rb_has '^left on the box '; then                                                       # v2: for the records
  echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^left on the box ' "$RB_CAP" | cut -c1-400)" >> "$RB_LOG"
  rb_say "$(grep -m1 '^left on the box ' "$RB_CAP" | cut -c1-300)"
fi
rb_local read local "E185's own gates (cclaunch_e185.py --gates-only)" "$RB_PY" -B "$RB_DIR/cclaunch_e185.py" --gates-only "$D"
if [ -z "${RB_DRY:-}" ] && rb_has '^(F0-STOPPED|G0-REFUSED) '; then    # cclaunch's exit 5; rb_run.py reports any non-zero exit as 14
  rb_die $RB_E_GATE "$(grep -m1 -E '^(F0-STOPPED|G0-REFUSED)' "$RB_CAP"). Nothing is scored, and no scored file was written; $D is the gate's evidence (a records round decides its commit)"
fi
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the gates' reading exited $RB_RC: read the output above"
if [ -n "${RB_DRY:-}" ]; then
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
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E185's check of C did not finish (the CCHECK- lines above): nothing is scored. Read its ccheck output, remove $D, then collect again"
rb_local read local "E185's passes carry their C logs, and the check read every launch their marks record (cclaunch_e185.py)" "$RB_PY" -B \
  "$RB_DIR/cclaunch_e185.py" "$D"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E185's check of C does not cover the launches its passes' marks record (the MISSING-/NO-LAUNCH/COUNT-/ORPHAN lines above): nothing is scored. Find the C log on the box (read-only), remove $D, then collect again"
scrub_all "$D" aifoundry3
rb_nopath "$D"
if [ -z "${RB_DRY:-}" ]; then
  for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl scored-m11-lines.jsonl.staging; do
    [ -e "$D/$f" ] && rb_die $RB_E_GATE "$D/$f exists before the score: something wrote a score before the gates; remove $D and collect again"
  done
  for h in host-start.out host-end.out; do [ -f "$D/logs/$h" ] || rb_say "A6-5: logs/$h was not collected (step 12 not run?): the scorer reports it as not read"; done
fi
rb_local desk local "score_e185.sh (M11's scorer v5, after every gate)" env PY=/usr/bin/python3 bash "$S185" "$D"
if ! rb_has '^score rc=0$'; then
  left=""
  [ -z "${RB_DRY:-}" ] && for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl scored-m11-lines.jsonl.staging; do [ -e "$D/$f" ] && left="$left $f"; done
  rb_die $RB_E_FAIL "M11's scorer v5 did not read rc 0: read the output above (the gates passed, and $D stands as their evidence; scored files left:${left:- none}). To collect again, remove $D first: collect_e185_v2.sh refuses a data directory that holds any file"
fi
rb_nopath "$D/scored-m11.json" "$D/scored-m11.md" "$D/scored-m11-lines.jsonl"
rb_say "E185 collected and scored: $D (the copy-back exact; scored-m11.json, scored-m11.md, scored-m11-lines.jsonl, written after the gates: A10's reading, E185's rules, A6-5's host readings; E185-C governed by its F line, E185.md's dated amendment A1)"

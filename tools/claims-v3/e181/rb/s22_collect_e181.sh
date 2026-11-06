#!/usr/bin/env bash
# E181, step 22: collect E181 at the desk, gate it, and only then score it, on the Intel (it needs this Mac's tree and its ssh to the box), at
# nice 10 with at most 2 jobs, every copy bounded, after the session has ended (s20_wait_e181.sh read the session end). It is
# ../../q143k-runbook/s22_collect_q143k_v2.sh (6b013ad9, which stays as committed) with the order fixed (E176's runbook note 2, section 3; the
# Q143(k) code verifier's fault 2: "the scorer writes before the gates"). In order:
#   1. before any box call, the files as committed: M11's SHA256SUMS-score-m11-v3, E181's kit-e181.sha256 and this runbook's
#      SHA256SUMS-rb-e181, else 16 (nothing collected);
#   2. the collector collect_e181.sh: the copies (bounded) and the check of C, NO scorer (a failed copy: 14);
#   3. the session's own gates (cclaunch_e181.py --gates-only): F0-STOPPED (A6-1) or G0-REFUSED (G0-A6 with A8-4): 16, nothing scored, the
#      collection kept as the gate's evidence;
#   4. v3.1's cc_gate (ccdone_q142s.py: the check finished, written since this step began), else 14;
#   5. the launch gate (cclaunch_e181.py: every launch the marks record checked, process by process, distinct t_start_ms), else 14;
#   6. the login scrub check (E164's scrub, --check) and the desk-path gate over the collection, else 16;
#   7. no scored file in the data directory yet, else 16;
#   8. ONLY NOW the score (score_e181.sh: M11's scorer v3 on E176's committed pass and E181's measured pass); "score rc=0" must be read, else 14;
#   9. the desk-path gate over the scored files, else 16; then "E181 collected and scored".
# It commits nothing. Desk-test stand-ins (E181_COLLECT, E181_SCORE) are read only with RB_DESKTEST=1; set without it, the step refuses (10).
#
#   bash tools/claims-v3/e181/rb/s22_collect_e181.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
D=docs/reports/data/$DAY-e181-m11-session2-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && { [ -n "${E181_COLLECT:-}" ] || [ -n "${E181_SCORE:-}" ]; }; then
  rb_die $RB_E_USAGE "E181_COLLECT and E181_SCORE are desk-test stand-ins, read only with RB_DESKTEST=1: unset them"
fi
C181=${E181_COLLECT:-tools/claims-v3/e181/collect_e181.sh}
S181=${E181_SCORE:-tools/claims-v3/e181/score_e181.sh}
scrub_check() {  # E164's scrub, --check only (it rewrites nothing); v3.1's backstop
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "logs/ in $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_e181.sh)"; return 0; fi
  rb_local read local "et-who lines in $d (E164's scrub, --check)" "$RB_PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$d" --owner "$own"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d: scrub it (scrub_etwho_e164.py without --check) before any commit"
}
for l in tools/claims-v3/m11/SHA256SUMS-score-m11-v3 tools/claims-v3/e181/kit-e181.sha256 tools/claims-v3/e181/rb/SHA256SUMS-rb-e181; do
  rb_local read local "the files as committed ($(basename "$l"))" shasum -a 256 -c "$l"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "a file of $l differs from its committed hash (the FAILED lines above): nothing was collected"
done
rb_probe aifoundry3
t_cc=$(date +%s)
rb_local desk aifoundry3 "collect_e181.sh (its rsyncs bounded at 300/120 s; the check of C; no scorer)" env PY=/usr/bin/python3 nice -n 10 bash "$C181" "$D"
if [ -z "${RB_DRY:-}" ] && rb_has '^rsync .* rc=[0-9]+'; then
  rb_die $RB_E_FAIL "a copy inside collect_e181.sh failed ($(grep -m1 -E '^rsync .* rc=' "$RB_CAP")): $D holds a partial copy; remove $D, then run this step again"
fi
[ -z "${RB_DRY:-}" ] && rb_has '^refusing: ' && rb_die $RB_E_GATE "$(grep -m1 '^refusing: ' "$RB_CAP")"
rb_local read local "E181's own gates (cclaunch_e181.py --gates-only)" "$RB_PY" -B "$RB_DIR/cclaunch_e181.py" --gates-only "$D"
if [ -z "${RB_DRY:-}" ] && rb_has '^(F0-STOPPED|G0-REFUSED) '; then    # cclaunch's exit 5; rb_run.py reports any non-zero exit as 14
  rb_die $RB_E_GATE "$(grep -m1 -E '^(F0-STOPPED|G0-REFUSED)' "$RB_CAP"). Nothing is scored, and no scored file was written; $D is the gate's evidence (a records round decides its commit)"
fi
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the gates' reading exited $RB_RC: read the output above"
rb_local read local "E181's checks of C finished (ccdone_q142s.py)" "$RB_PY" -B "$RB_V31/ccdone_q142s.py" --since "$t_cc" "$D/ccheck/ccheck-all.json"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E181's check of C did not finish (the CCHECK- lines above): nothing is scored. Read its ccheck output, remove what the collector wrote, then collect again"
rb_local read local "E181's passes carry their C logs, and the check read every launch their marks record (cclaunch_e181.py)" "$RB_PY" -B \
  "$RB_DIR/cclaunch_e181.py" "$D"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E181's check of C does not cover the launches its passes' marks record (the MISSING-/NO-LAUNCH/COUNT-/ORPHAN lines above): nothing is scored. Find the C log on the box (read-only), remove what the collector wrote, then collect again"
scrub_check "$D/logs" aifoundry3
rb_nopath "$D"
if [ -z "${RB_DRY:-}" ]; then
  for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl; do
    [ -e "$D/$f" ] && rb_die $RB_E_GATE "$D/$f exists before the score: something wrote a score before the gates; remove $D and collect again"
  done
fi
rb_local desk local "score_e181.sh (M11's scorer v3, after every gate)" env PY=/usr/bin/python3 bash "$S181" "$D"
rb_has '^score rc=0$' || rb_die $RB_E_FAIL "M11's scorer did not read rc 0: read the output above (the gates passed; the collection stands)"
rb_nopath "$D/scored-m11.json" "$D/scored-m11.md" "$D/scored-m11-lines.jsonl"
rb_say "E181 collected and scored: $D (scored-m11.json, scored-m11.md, scored-m11-lines.jsonl, written after the gates)"

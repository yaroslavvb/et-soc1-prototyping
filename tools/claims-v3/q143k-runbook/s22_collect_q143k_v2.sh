#!/usr/bin/env bash
# Q143(k), step 22 v2 (Q143(k)'s fix pass, Thu 5 Nov 2026, before any E176 data): collect and score E176 at the desk, on the Intel (it needs
# this Mac's tree and its ssh to the box), at nice 10 with at most 2 jobs, every copy bounded, after the session has ended (s20_wait_q143k.sh
# read the session end). s22_collect_q143k.sh (lab 92a1b27f) stays as committed; v2 is it with four changes (the verifier of Q143(k), its
# fault 2: v1's cc_gate passed with the measured pass's C log missing, on the smoke's log alone):
#   (1) first, before any box call, the v2 files are checked as committed: tools/claims-v3/m11/SHA256SUMS-score-m11-v2 (M11's scorer v2)
#       and SHA256SUMS-q143k-v2 (this step, its gate and data maker, the collector v2, their notes and logs), else 16;
#   (2) the collector is collect_e176_v2.sh (M11's scorer v2, score_m11_v2.py, with its lines file);
#   (3) after v3.1's cc_gate (ccdone_q142s.py: the check finished, written since this step began), the launch gate cclaunch_q143k.py: the
#       measured pass p17620 must show a launch and carry a collected C log; the smoke p17601 must carry one whenever its marks show a
#       launch; and for each, the check's launches must equal, process by process, the records its launch marks hold, with none outside
#       them, else 14;
#   (4) it says "E176 collected and scored" only after both gates, the login scrub check and the desk-path gate.
# The rest is v1's: a failed copy inside the collector stops the step (14); "score rc=0" must be read (14); it commits nothing. A desk-test
# stand-in for the collector (Q143K_COLLECT_E176) is read only with RB_DESKTEST=1; set without it, the step refuses (10).
#
#   bash tools/claims-v3/q143k-runbook/s22_collect_q143k_v2.sh [<an earlier M11 aifoundry3 pass dir, committed> ...]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s22_collect_v2
rb_window
DAY=$RB_DAY
D=docs/reports/data/$DAY-e176-m11-holds-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${Q143K_COLLECT_E176:-}" ]; then
  rb_die $RB_E_USAGE "Q143K_COLLECT_E176 is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it"
fi
C176=${Q143K_COLLECT_E176:-tools/claims-v3/e176/collect_e176_v2.sh}
scrub_check() {  # E164's scrub, --check only (it rewrites nothing); v3.1's backstop
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "logs/ in $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_q143k.sh)"; return 0; fi
  rb_local read local "et-who lines in $d (E164's scrub, --check)" "$RB_PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$d" --owner "$own"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d: scrub it (scrub_etwho_e164.py without --check) before any commit"
}
cc_gate() {  # v3.1's: cc_gate <run> <since, epoch s> <ccheck --out json> ...: every check of C the collection ran finished, else 14
  local run=$1 since=$2; shift 2
  rb_local read local "$run's checks of C finished (ccdone_q142s.py)" "$RB_PY" -B "$RB_V31/ccdone_q142s.py" --since "$since" "$@"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$run's check of C did not finish (the CCHECK- lines above): nothing is scored as registered. Read its ccheck output, remove what the collector wrote, then collect again"
}
launch_gate() {  # v2: launch_gate <run> <data dir>: the passes that must carry a C log carry one, and the check read every launch their marks record, else 14
  local run=$1 d=$2
  rb_local read local "$run's passes carry their C logs, and the check read every launch their marks record (cclaunch_q143k.py)" "$RB_PY" -B \
    "$RB_DIR/cclaunch_q143k.py" "$d"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$run's check of C does not cover the launches its passes' marks record (the MISSING-/NO-LAUNCH/COUNT-/ORPHAN lines above): nothing is scored as registered. Find the C log on the box (read-only), remove what the collector wrote, then collect again"
}
for l in tools/claims-v3/m11/SHA256SUMS-score-m11-v2 tools/claims-v3/q143k-runbook/SHA256SUMS-q143k-v2; do
  rb_local read local "the v2 files as committed ($(basename "$l"))" shasum -a 256 -c "$l"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "a file of $l differs from its committed hash (the FAILED lines above): nothing was collected"
done
rb_probe aifoundry3
t_cc=$(date +%s)
rb_local desk aifoundry3 "collect_e176_v2.sh (its rsyncs bounded at 300/120 s; the check of C; M11's scorer v2)" env PY=/usr/bin/python3 \
  nice -n 10 bash "$C176" "$D" "$@"
if [ -z "${RB_DRY:-}" ] && rb_has '^rsync .* rc=[0-9]+'; then
  rb_die $RB_E_FAIL "a copy inside collect_e176_v2.sh failed ($(grep -m1 -E '^rsync .* rc=' "$RB_CAP")): $D holds a partial copy, and any score in it is not the session's; remove $D, then run this step again"
fi
rb_has '^score rc=0$' || rb_die $RB_E_FAIL "M11's scorer did not read rc 0 (collect_e176_v2.sh exits 0 even then): read the output above"
cc_gate E176 "$t_cc" "$D/ccheck/ccheck-all.json"
launch_gate E176 "$D"
scrub_check "$D/logs" aifoundry3
rb_nopath "$D"
rb_say "E176 collected and scored: $D (scored-m11.json, scored-m11.md, scored-m11-lines.jsonl)"

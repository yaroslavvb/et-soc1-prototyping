#!/usr/bin/env bash
# Q143(k), step 22: collect and score E176 at the desk, on the Intel (it needs this Mac's tree and its ssh to the box), at nice 10 with at
# most 2 jobs, every copy bounded, after the session has ended (s20_wait_q143k.sh read the session end). v3.1's s22_collect.sh e166 route,
# ported: collect_e176.sh (its rsyncs bounded at 300 / 120 s; the check of C; M11's scorer over this session and any earlier M11 aifoundry3
# pass dirs named on the command line); a failed copy inside it stops the step (14); "score rc=0" must be read (14); then cc_gate (v3.1's
# ccdone_q142s.py: the check's --out file there, holding ccheck.py's summary and written since this step began, else 14); the login scrub
# check; and the desk-path gate (16). It commits nothing. A desk-test stand-in for the collector (Q143K_COLLECT_E176) is read only with
# RB_DESKTEST=1; set without it, the step refuses (10).
#
#   bash tools/claims-v3/q143k-runbook/s22_collect_q143k.sh [<an earlier M11 aifoundry3 pass dir, committed> ...]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
D=docs/reports/data/$DAY-e176-m11-holds-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${Q143K_COLLECT_E176:-}" ]; then
  rb_die $RB_E_USAGE "Q143K_COLLECT_E176 is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it"
fi
C176=${Q143K_COLLECT_E176:-tools/claims-v3/e176/collect_e176.sh}
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
rb_probe aifoundry3
t_cc=$(date +%s)
rb_local desk aifoundry3 "collect_e176.sh (its rsyncs bounded at 300/120 s; the check of C; M11's scorer)" env PY=/usr/bin/python3 \
  nice -n 10 bash "$C176" "$D" "$@"
if [ -z "${RB_DRY:-}" ] && rb_has '^rsync .* rc=[0-9]+'; then
  rb_die $RB_E_FAIL "a copy inside collect_e176.sh failed ($(grep -m1 -E '^rsync .* rc=' "$RB_CAP")): $D holds a partial copy, and any score in it is not the session's; remove $D, then run this step again"
fi
rb_has '^score rc=0$' || rb_die $RB_E_FAIL "M11's scorer did not read rc 0 (collect_e176.sh exits 0 even then): read the output above"
cc_gate E176 "$t_cc" "$D/ccheck/ccheck-all.json"
scrub_check "$D/logs" aifoundry3
rb_nopath "$D"
rb_say "E176 collected and scored: $D (scored-m11.json, scored-m11.md)"

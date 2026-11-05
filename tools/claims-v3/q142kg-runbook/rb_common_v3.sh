# Q142(v2) fix pass, Thu 5 Nov 2026 (week 45), PST: the part the v3 step drivers' collect sources (tools/claims-v3/e173/box/step_e173_v3.sh and
# tools/claims-v3/e174/box/step_e174_v3.sh; bash 3.2 or later). It SOURCES this directory's rb_common_v2.sh (lab 34436d68, which sources v1's
# rb_common.sh and v3.1's, all unchanged), so every rule of v2, v1 and v3.1 holds: the 15 s hard-killed probe; every call under its bound; a login
# link kills the call, appends "<HH:MM:SS> <host> needs a check" to $RB_LOCK and exits 11; nothing prompts; every call is logged. It changes two
# things only:
#   - rb_cc_gate reads cclist_q142kg_v3.py (E173.md.dated-note-2.md and E174.md.dated-note-2.md, section 2; the first verifier of v2's fault 3):
#     v2's list, plus a session the queue's record names only in a session_end line, with its start line and directory lost, which v1's rule for
#     a session with no directory requires. v3 only adds sessions to v2's list. Then v3.1's ccdone_q142s.py reads every listed check, as in v2;
#   - every step's name carries "_q142kg3" in the log, its messages and the dry listing's header.
# Exit codes are v3.1's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero (or a check of C that did
# not finish, a required C log missing, the queue's record missing); 15 a holder after 30 minutes; 16 a gate says stop; 17 not yet.
# SPDX-License-Identifier: Apache-2.0

# shellcheck disable=SC1091
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/rb_common_v2.sh"

eval "rb_init_kg2() $(declare -f rb_init | tail -n +2)"
rb_init() {  # rb_init <step>: v2's, with the step named <step>_q142kg3 (the dry listing's header too: v2's is held back and printed here)
  local dry=${RB_DRY:-}
  RB_DRY=
  rb_init_kg2 "$1"
  RB_DRY=$dry
  RB_STEP=${1}_q142kg3
  [ -n "${RB_DRY:-}" ] && echo "=== [$RB_STEP] dry listing: nothing below is run"
  return 0
}

rb_cc_gate() {  # rb_cc_gate <run> <since, epoch s> <the queue's runs dir in the data dir> <the dir its ccheck-<session>.json files are in>:
  #               v2's gate with v3's list: cclist_q142kg_v3.py names every session that must carry a C log; the queue's record missing, or a
  #               required session with no C log, stops the step (14); then v3.1's ccdone_q142s.py reads every listed check: there, with
  #               ccheck.py's summary, written since <since>; else 14. A C FAIL is a finished check: it reaches the rules
  local run=$1 since=$2 q=$3 cdir=$4 f
  RB_CC_FILES=()
  if [ -n "${RB_DRY:-}" ]; then
    rb_local read local "$run: the sessions that must carry a C log (cclist_q142kg_v3.py)" "$RB_PY" -B "$RB_KG_DIR/cclist_q142kg_v3.py" "$q" "$cdir"
    rb_local read local "$run: every listed check of C finished (v3.1's ccdone_q142s.py)" "$RB_PY" -B "$RB_DIR/ccdone_q142s.py" --since "$since" \
      "$cdir/ccheck-<each listed session>.json"
    return 0
  fi
  rb_local read local "$run: the sessions that must carry a C log (cclist_q142kg_v3.py)" "$RB_PY" -B "$RB_KG_DIR/cclist_q142kg_v3.py" "$q" "$cdir"
  if [ "$RB_RC" -ne 0 ]; then
    rb_has '^MISSING-QUEUE' && rb_die $RB_E_FAIL "$run: the collected runs dir holds no queue.jsonl, so the sessions that must carry a C log cannot be read: nothing is scored as registered"
    rb_die $RB_E_FAIL "$run: a session that must carry a C log has none (the MISSING-CLOG lines above): nothing is scored as registered"
  fi
  while read -r tag s p; do [ "$tag" = REQUIRED ] && RB_CC_FILES+=("$p"); done < "$RB_CAP"
  [ ${#RB_CC_FILES[@]} -gt 0 ] || rb_die $RB_E_FAIL "$run: the C-log list is empty (no session ran a work launch): nothing is scored as registered"
  rb_local read local "$run: every listed check of C finished (v3.1's ccdone_q142s.py)" "$RB_PY" -B "$RB_DIR/ccdone_q142s.py" --since "$since" "${RB_CC_FILES[@]}"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$run's check of C did not finish for a listed session (the CCHECK- lines above): nothing is scored as registered. Read its ccheck output, remove what the collector wrote, then collect again"
  f=${#RB_CC_FILES[@]}
  rb_say "$run: $f listed sessions carry a C log and a finished check of it (v3's list)"
}

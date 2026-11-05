# Q142(kg) fix pass, Thu 5 Nov 2026 (week 45), PST: the part the v2 step drivers source (tools/claims-v3/e173/box/step_e173_v2.sh and
# tools/claims-v3/e174/box/step_e174_v2.sh; bash 3.2 or later). It SOURCES this directory's rb_common.sh (v1, lab 5a2a9ba0, which sources v3.1's
# rb_common.sh unchanged), so every rule of v1 and v3.1 holds: the 15 s hard-killed probe; every call under its bound; a login link kills the call,
# appends "<HH:MM:SS> <host> needs a check" to $RB_LOCK and exits 11; nothing prompts; every call is logged. It changes three things only:
#   - RB_BASE defaults to the kits' commit, 5a2a9ba0 (v1: the registrations' c8064454, so v1's README said to pass RB_BASE=5a2a9ba0 on the day);
#     a later port sets its own;
#   - rb_cc_gate reads cclist_q142kg_v2.py, the stricter list of the sessions that must carry a C log (E173.md.dated-note-1.md and
#     E174.md.dated-note-1.md, section 3; the kits' verifier's fault 7): the queue's record must be in the collected runs dir, and a session whose
#     records show it ran a launch must carry a C log even when its launches.jsonl is lost. v2 only adds sessions to v1's list. Then v3.1's
#     ccdone_q142s.py reads every listed check, as in v1;
#   - every step's name carries "_q142kg2" in the log, its messages and the dry listing's header.
# Exit codes are v3.1's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero (or a check of C that did
# not finish, a required C log missing, the queue's record missing); 15 a holder after 30 minutes; 16 a gate says stop; 17 not yet.
# SPDX-License-Identifier: Apache-2.0

RB_BASE=${RB_BASE:-5a2a9ba0}          # E173's and E174's kits (Thu 5 Nov 2026 04:35:57 PST), after their registrations (c8064454)
# shellcheck disable=SC1091
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/rb_common.sh"

eval "rb_init_kg1() $(declare -f rb_init | tail -n +2)"
rb_init() {  # rb_init <step>: v1's, with the step named <step>_q142kg2 (the dry listing's header too: v1's is held back and printed here)
  local dry=${RB_DRY:-}
  RB_DRY=
  rb_init_kg1 "$1"
  RB_DRY=$dry
  RB_STEP=${1}_q142kg2
  [ -n "${RB_DRY:-}" ] && echo "=== [$RB_STEP] dry listing: nothing below is run"
  return 0
}

rb_cc_gate() {  # rb_cc_gate <run> <since, epoch s> <the queue's runs dir in the data dir> <the dir its ccheck-<session>.json files are in>:
  #               v1's gate with v2's list: cclist_q142kg_v2.py names every session that must carry a C log; the queue's record missing, or a
  #               required session with no C log, stops the step (14); then v3.1's ccdone_q142s.py reads every listed check: there, with
  #               ccheck.py's summary, written since <since>; else 14. A C FAIL is a finished check: it reaches the rules
  local run=$1 since=$2 q=$3 cdir=$4 f
  RB_CC_FILES=()
  if [ -n "${RB_DRY:-}" ]; then
    rb_local read local "$run: the sessions that must carry a C log (cclist_q142kg_v2.py)" "$RB_PY" -B "$RB_KG_DIR/cclist_q142kg_v2.py" "$q" "$cdir"
    rb_local read local "$run: every listed check of C finished (v3.1's ccdone_q142s.py)" "$RB_PY" -B "$RB_DIR/ccdone_q142s.py" --since "$since" \
      "$cdir/ccheck-<each listed session>.json"
    return 0
  fi
  rb_local read local "$run: the sessions that must carry a C log (cclist_q142kg_v2.py)" "$RB_PY" -B "$RB_KG_DIR/cclist_q142kg_v2.py" "$q" "$cdir"
  if [ "$RB_RC" -ne 0 ]; then
    rb_has '^MISSING-QUEUE' && rb_die $RB_E_FAIL "$run: the collected runs dir holds no queue.jsonl, so the sessions that must carry a C log cannot be read: nothing is scored as registered"
    rb_die $RB_E_FAIL "$run: a session that must carry a C log has none (the MISSING-CLOG lines above): nothing is scored as registered"
  fi
  while read -r tag s p; do [ "$tag" = REQUIRED ] && RB_CC_FILES+=("$p"); done < "$RB_CAP"
  [ ${#RB_CC_FILES[@]} -gt 0 ] || rb_die $RB_E_FAIL "$run: the C-log list is empty (no session ran a work launch): nothing is scored as registered"
  rb_local read local "$run: every listed check of C finished (v3.1's ccdone_q142s.py)" "$RB_PY" -B "$RB_DIR/ccdone_q142s.py" --since "$since" "${RB_CC_FILES[@]}"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$run's check of C did not finish for a listed session (the CCHECK- lines above): nothing is scored as registered. Read its ccheck output, remove what the collector wrote, then collect again"
  f=${#RB_CC_FILES[@]}
  rb_say "$run: $f listed sessions carry a C log and a finished check of it (v2's list)"
}

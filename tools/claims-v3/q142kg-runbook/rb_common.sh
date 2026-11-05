# Q142(kg), the pool-8 card day's runbook for E173 (aifoundry2) and E174 (aifoundry1 card 0): the part every step script sources (bash 3.2 or
# later; the Intel's /bin/bash is 3.2). It is v3.1's runbook, ported (Q142(s), tools/claims-v3/q141k-runbook/v3.1/, lab 0d2cb5dd): it SOURCES
# v3.1's rb_common.sh unchanged, so rb_run.py, nopath_q142s.py and ccdone_q142s.py are v3.1's committed files, and every rule of v3.1 holds (the
# 15 s hard-killed probe; every call under its bound, 60 s for a read, 600 s for a copy or a wait, 60 s for a launch, 5,400 s for a desk collector; a
# login link kills the call, appends "<HH:MM:SS> <host> needs a check" to $RB_LOCK and exits 11; nothing prompts; every call logged). It adds one
# function, rb_cc_gate (the C-log gate, below: v3.1's s22 cc_gate with its list of checks taken from the registrations' C-log list), and it
# overrides four things only:
#   - RB_BASE defaults to E173's and E174's registration commit (c8064454): every box tree the day uses descends from it; the kit's own bytes are
#     checked file by file by each kit's harness check (check_e173.py, check_e174.py), so a box that lacks the kit commit refuses there;
#   - the window: rb_window reads $RB_OUT/window-q142kg.env, written by s02_window_q142kg.sh (the day's last start and last end; v3.1's s02 names
#     E163-E169's plans), or v3.1's window.env if a later port writes one;
#   - ours_live (the remote prelude) also counts, by name, the pool-8 day's runs: E171-E174's queue_e17N.py, run_e17N.py, session_e17N.sh and
#     block_e17N processes, and E170's (v3.1's pattern already counts any queue_eNNN.py or session_eNNN.sh of ours);
#   - every step's name carries "_q142kg" in the log and its messages.
# Exit codes are v3.1's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero (or a check of C that did
# not finish, or a required C log missing); 15 a holder after 30 minutes; 16 a gate says stop; 17 not yet.
# SPDX-License-Identifier: Apache-2.0

RB_KG_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_BASE=${RB_BASE:-c8064454}          # E173's and E174's registrations (Thu 5 Nov 2026 03:45:13 PST); a later port sets its own
# shellcheck disable=SC1091
. "$RB_KG_DIR/../q141k-runbook/v3.1/rb_common.sh"

eval "rb_init_v31() $(declare -f rb_init | tail -n +2)"
rb_init() {  # rb_init <step>: v3.1's, with the step named <step>_q142kg (the dry listing's header too: v3.1's is held back and printed here)
  local dry=${RB_DRY:-}
  RB_DRY=
  rb_init_v31 "$1"
  RB_DRY=$dry
  RB_STEP=${1}_q142kg
  [ -n "${RB_DRY:-}" ] && echo "=== [$RB_STEP] dry listing: nothing below is run"
  return 0
}

rb_window() {  # the day's window: s02_window_q142kg.sh's file, else v3.1's
  if [ -f "$RB_OUT/window-q142kg.env" ]; then
    # shellcheck disable=SC1091
    . "$RB_OUT/window-q142kg.env"
  elif [ -f "$RB_OUT/window.env" ]; then
    # shellcheck disable=SC1091
    . "$RB_OUT/window.env"
  else
    rb_die $RB_E_USAGE "no window yet: run s02_window_q142kg.sh with the day, the last start and the last end"
  fi
  RB_NOW=$(date +%s)
}

rb_cc_gate() {  # rb_cc_gate <run> <since, epoch s> <the queue's runs dir in the data dir> <the dir its ccheck-<session>.json files are in>:
  #               v3.1's cc_gate (s22_collect.sh), with the list of checks it reads taken from the registration's C-log list (the Q142 critic's
  #               fault 3): cclist_q142kg.py names every session that must carry a C log (smoke, stoptest-board, every BURST session the queue
  #               started that ran a work launch); a required session with no C log stops the step (14); then v3.1's ccdone_q142s.py reads every
  #               listed check: there, with ccheck.py's summary, written since <since>; else 14. A C FAIL is a finished check: it reaches the rules
  local run=$1 since=$2 q=$3 cdir=$4 f
  RB_CC_FILES=()
  if [ -n "${RB_DRY:-}" ]; then
    rb_local read local "$run: the sessions that must carry a C log (cclist_q142kg.py)" "$RB_PY" -B "$RB_KG_DIR/cclist_q142kg.py" "$q" "$cdir"
    rb_local read local "$run: every listed check of C finished (v3.1's ccdone_q142s.py)" "$RB_PY" -B "$RB_DIR/ccdone_q142s.py" --since "$since" \
      "$cdir/ccheck-<each listed session>.json"
    return 0
  fi
  rb_local read local "$run: the sessions that must carry a C log (cclist_q142kg.py)" "$RB_PY" -B "$RB_KG_DIR/cclist_q142kg.py" "$q" "$cdir"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$run: a session the registration requires to carry a C log has none (the MISSING-CLOG lines above): nothing is scored as registered"
  while read -r tag s p; do [ "$tag" = REQUIRED ] && RB_CC_FILES+=("$p"); done < "$RB_CAP"
  [ ${#RB_CC_FILES[@]} -gt 0 ] || rb_die $RB_E_FAIL "$run: the C-log list is empty (no session ran a work launch): nothing is scored as registered"
  rb_local read local "$run: every listed check of C finished (v3.1's ccdone_q142s.py)" "$RB_PY" -B "$RB_DIR/ccdone_q142s.py" --since "$since" "${RB_CC_FILES[@]}"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$run's check of C did not finish for a listed session (the CCHECK- lines above): nothing is scored as registered. Read its ccheck output, remove what the collector wrote, then collect again"
  f=${#RB_CC_FILES[@]}
  rb_say "$run: $f listed sessions carry a C log and a finished check of it"
}

eval "rb_prelude_v31() $(declare -f rb_prelude | tail -n +2)"
rb_prelude() {  # rb_prelude <box>: v3.1's prelude, then ours_live redefined to name the pool-8 day's runs as well
  rb_prelude_v31 "$1" || return 1
  cat <<'EOF'
ours_live() {  # Q142(kg): v3.1's rule, and E171-E174's (and E170's) queue, runner, session and block processes by name
  n=0
  for pid in $(pgrep -u "$(id -u)" -f '(queue|session)_e[0-9]+[a-z0-9_]*\.(py|sh)|session_e16[346]\.sh|queue_e16[5-9]\.py|(queue|run)_e17[0-9]\.py|session_e17[0-9]\.sh|block_e17[0-9]' 2>/dev/null); do
    case "$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null)" in *--dry*) continue ;; esac
    tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | grep -q '^V3_DRY=' && continue
    n=$((n + 1))
  done
  echo "$n"
}
EOF
}

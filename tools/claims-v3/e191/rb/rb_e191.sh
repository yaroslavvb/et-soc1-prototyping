# E191 (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): the part every E191 runbook step
# sources (bash 3.2 or later; the desk is aifoundry2, Linux; the box aifoundry1, card 1, tree ~/nekko). E189's runbook file's form
# (tools/claims-v3/e189/rb/rb_e189.sh, b42dc95c, unchanged beside it): it sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe, its login-link
# stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried, its prelude with each box's tree
# (aifoundry1: ~/nekko), its holder read, its guard (rb_guard_text: no launch during a dry pass or beside a session of ours, and on
# aifoundry1 none on a host booted after E82's firmware read of record), its detached jobs, its desk-path gate and its exit codes), and
# changes only:
#   - rb_init names every step "<step>_e191";
#   - E190's ours_live (tools/claims-v3/e190/rb/rb_e190.sh, its kit's runbook desk test's finding): our sessions and queues by each
#     process's OWN script (the first word of its command line after the interpreter and its options, never a shell's -c string), so a
#     command string that only names a session script is never counted, and `ours_live <glob>` counts one name (session_e191.sh: steps
#     10 and 11); E190 arm B's session_e190_v2.sh, E164's, E172's and any session_eNNN*.sh of ours on aifoundry1 count; E191 adds one
#     condition (its step 10 desk test, case N1, found it): the command's first word is an interpreter (bash, sh, dash, python, python3),
#     so `grep -q session_e191.sh <file>`, whose first argument after its options is that name, is not counted;
#   - RB_E191_REG, E191's registration commit 300d76e4 (12:14:24 PST Fri 13 Nov 2026) and its tools/claims-v3/e191 subtree 766e2463, and
#     THE NOTE COMMIT 8c8f825f (E191's dated note 1); THE KIT COMMIT is found by its content (the commit that added
#     tools/claims-v3/e191/KIT.md), since it lands after this file is written;
#   - E191's box (aifoundry1, card 1), its plan's budget: the session's cap, 110 card-minutes (6,600 s; E191.md 10);
#   - THE WINDOW RULE (E189's): e191_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific calendar, and
#     names today as its day and E191 as its runbook;
#   - THE LAB-GIT LOCK (E189's): e191_pull runs `git pull --ff-only` under RB_GITLOCK with /usr/bin/flock -w 600 -E 75 (or
#     /usr/bin/lockf -k -t 600 where it exists): step 2 takes it itself for the pull alone, so step 2 is NEVER run inside that lock.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E191_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E191_REG=${RB_E191_REG:-300d76e4c9ab5a76e5a1fc23f0ed08ac2477b868}
RB_E191_NOTE1=8c8f825f9adf39b8bcbe76987e75e5adf47e568d
E191_REG_SUBTREE=766e24631138fdac09c3dd247d504b138c4a2ded
E191_BOX=aifoundry1
E191_BUDGET_S=6600
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E191_DESK_BUDGET_S:-}" ] && E191_BUDGET_S=$E191_DESK_BUDGET_S

e191_live_text() {
  cat <<'EOF'
ours_live() {  # E191's (E190's rb_e190.sh form): our sessions and queues by each process's own script, never by a command string's text
  local n=0 pid w s first dashc interp want=${1:-}
  for pid in $(pgrep -u "$(id -u)" . 2>/dev/null); do
    s=""; first=1; dashc=0; interp=0
    while IFS= read -r -d '' w; do
      if [ "$first" = 1 ]; then
        first=0
        case "${w##*/}" in bash|sh|dash|python|python3|python3.[0-9]*) interp=1 ;; esac     # E191: an interpreter's script only
        continue
      fi
      case "$w" in -c) dashc=1; break ;; -*) continue ;; *) s=$w; break ;; esac
    done 2>/dev/null < "/proc/$pid/cmdline"
    [ "$interp" = 1 ] && [ "$dashc" = 0 ] && [ -n "$s" ] || continue
    if [ -n "$want" ]; then
      case "${s##*/}" in $want) ;; *) continue ;; esac
    else
      case "${s##*/}" in session_e[0-9]*.sh|queue_e[0-9]*.py|queue_e[0-9]*.sh|block_e17[12].sh|run_e17[012].py) ;; *) continue ;; esac
    fi
    case "$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)" in *--dry*) continue ;; esac
    tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null | grep -q '^V3_DRY=' && continue
    n=$((n + 1))
  done
  echo "$n"
}
EOF
}
eval "$(declare -f rb_prelude | sed '1s/^rb_prelude /rb_prelude_k6 /')"     # k6's prelude, kept whole under another name
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E191's ours_live (above)
  rb_prelude_k6 "$@" || return 1
  e191_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e191"
  RB_STEP=${1}_e191
  [ -n "${RB_OUT:-}" ] || { echo "[$RB_STEP] RB_OUT is not set (this card day's own directory, outside the repo)"; exit $RB_E_USAGE; }
  [ -n "${RB_LOCK:-}" ] || { echo "[$RB_STEP] RB_LOCK is not set (the lock file a login check is appended to)"; exit $RB_E_USAGE; }
  mkdir -p "$RB_OUT/calls" || exit $RB_E_USAGE
  local o r
  o=$(cd "$RB_OUT" && pwd -P); r=$(cd "$RB_REPO" && pwd -P)
  case "$o/" in "$r/"*) echo "[$RB_STEP] RB_OUT is inside the lab repo: refused"; exit $RB_E_USAGE ;; esac
  export RB_LOG="$RB_OUT/runbook.log" RB_LINKS="$RB_OUT/links.txt" RB_LOCK
  cd "$RB_REPO" || exit $RB_E_USAGE
  RB_N=0
  [ -n "${RB_DRY:-}" ] && echo "=== [$RB_STEP] dry listing: nothing below is run"
  return 0
}

e191_kit_commit() {  # the kit commit, by its content (the commit that added tools/claims-v3/e191/KIT.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e191/KIT.md 2>/dev/null | tail -n 1
}

e191_window() {  # the window rule: window.env written today (Pacific), its day today, for E191; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E191 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e191.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e191.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e191.sh for today"
  [ "${RB_PLAN:-}" = e191 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E191: one RB_OUT per runbook"
  return 0
}

e191_lockcmd() {  # e191_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e191_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e191_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
    RB_RC=0; return 0
  fi
  [ -n "${RB_GITLOCK:-}" ] || rb_die $RB_E_USAGE "RB_GITLOCK is not set (the lab-git lock every commit to the shared lab clone takes; a path outside the repo)"
  case "$(cd "$(dirname "$RB_GITLOCK")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_GITLOCK is inside the lab repo: refused" ;; esac
  local lt=600; [ "${RB_DESKTEST:-}" = 1 ] && lt=${RB_GITLOCK_T:-600}     # the desk test's short wait for its nested-lock case only
  if [ -x /usr/bin/lockf ]; then
    rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/lockf -k -t "$lt" "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
  elif [ -x /usr/bin/flock ]; then
    rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/flock -w "$lt" -E 75 "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
  else
    rb_die $RB_E_USAGE "neither /usr/bin/lockf nor /usr/bin/flock is here: the lab-git lock cannot be taken"
  fi
}

e191_programs() {  # the programs built today on the box, from step 6's job output (RB_OUT/e191-built.txt, written by step 6's wait)
  if [ -f "$RB_OUT/e191-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e191-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then
    cat "$RB_OUT/e191-built.txt"
  fi
}

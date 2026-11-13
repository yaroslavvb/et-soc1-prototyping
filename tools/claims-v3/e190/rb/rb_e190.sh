# E190 (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the part every E190 runbook step sources (bash 3.2 or later; the desk is
# aifoundry2, Linux). E189's runbook file's form (tools/claims-v3/e189/rb/rb_e189.sh, as fix-e189b left it): it sources the k6 runbook's
# common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe,
# its login-link stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried, its prelude (each box's
# tree: aifoundry2 ~/claude/et-soc1-prototyping, aifoundry1 ~/nekko), its holder rule, its guard, its detached jobs, its desk-path gate and
# its exit codes), and changes only:
#   - rb_init names every step "<step>_e190";
#   - THE TWO ARMS: e190_box maps arm A to aifoundry2 (card 0) and arm B to aifoundry1 (card 1); every box step takes the arm as its first
#     word, and every file it leaves in RB_OUT carries the arm (e190-built-A.txt, e190-T0-B.txt);
#   - RB_E190_REG, the registration commit 508d48d9 (12:21:56 PST, Fri 13 Nov 2026), and its tools/claims-v3/e190 subtree 4d4f7440...: an
#     E190 tree descends from it; THE KIT COMMIT is found by its content (the commit that added tools/claims-v3/e190/KIT.md), since it
#     lands after this file is written;
#   - THE WINDOW RULE (E188's and E189's): e190_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific
#     calendar, and names today as its day and E190 as its runbook; E190_BUDGET_S, 2,700 s, is the session's 40-minute cap plus 5 minutes
#     of closing and margin before the last end at the launch;
#   - THE LAB-GIT LOCK (E188 v2's way, ported as E189's): e190_pull runs `git pull --ff-only` under RB_GITLOCK with /usr/bin/flock -w 600
#     -E 75 (or /usr/bin/lockf -k -t 600 where it exists): step 2 takes it itself for the pull alone, so step 2 is NEVER run inside that
#     lock (a nested flock exits 75 and step 2 stops with 16).
# k6's ours_live counts any session_eNNN.sh of ours (the lab's naming rule), so E190's session (session_e190.sh) is counted with no change,
# and k6's guard refuses a launch beside any session of ours on that box: never two of our sessions on aifoundry1 (E191 shares card 1).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E190_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E190_REG=${RB_E190_REG:-508d48d9a889ee91a9ff41140a906d103594978a}
E190_REG_SUBTREE=4d4f74406dd09a454ec105244f07a433555109d0
E190_BUDGET_S=2700
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E190_DESK_BUDGET_S:-}" ] && E190_BUDGET_S=$E190_DESK_BUDGET_S

# ---- E190's ours_live (found by this kit's runbook desk test, cases C and C2): k6's ours_live counts a process whose WHOLE command text
# holds "session_eNNN.sh" (or another session or queue name) anywhere. On aifoundry2 the desk and arm A's box are ONE machine, reached by
# ssh to itself, so the desk's own commands are not ancestors of the box's read and are counted: step 9's own name (s11_session_e190.sh
# holds "session_e190.sh"), and any shell wrapper whose command string names such a file, refused arm A's launch and its copy-back as "a
# card session of ours". E190's prelude keeps k6's prelude whole and then redefines ours_live to read each process's OWN script: the first
# word of its command line after the interpreter and its options, never a shell's `-c` string; a session or queue of ours is a process
# whose script's name is session_eNNN*.sh, queue_eNNN*.py or queue_eNNN*.sh (k6's patterns), or one of k6's named E171/E172/E170 runs,
# a dry one (--dry, V3_DRY) excepted. `ours_live <glob>` counts only scripts of that name (session_e190.sh: steps 10 and 11). k6's
# rb_common.sh is unchanged; rb_job_start, rb_job_wait and rb_guard_text call rb_prelude and ours_live, so they read E190's.
e190_live_text() {
  cat <<'EOF'
ours_live() {  # E190's (rb/rb_e190.sh): our sessions and queues by each process's own script, never by a command string's text
  local n=0 pid w s first dashc want=${1:-}
  for pid in $(pgrep -u "$(id -u)" . 2>/dev/null); do
    s=""; first=1; dashc=0
    while IFS= read -r -d '' w; do
      if [ "$first" = 1 ]; then first=0; continue; fi
      case "$w" in -c) dashc=1; break ;; -*) continue ;; *) s=$w; break ;; esac
    done 2>/dev/null < "/proc/$pid/cmdline"
    [ "$dashc" = 0 ] && [ -n "$s" ] || continue
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
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E190's ours_live (above)
  rb_prelude_k6 "$@" || return 1
  e190_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e190"
  RB_STEP=${1}_e190
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

e190_arm() {  # e190_arm <word>: sets ARM and BOX, or refuses (10)
  case "${1:-}" in
    A) ARM=A; BOX=aifoundry2 ;;
    B) ARM=B; BOX=aifoundry1 ;;
    *) rb_die $RB_E_USAGE "the first word is the arm: A (aifoundry2 card 0) or B (aifoundry1 card 1)" ;;
  esac
}

e190_window() {  # the window rule: window.env written today (Pacific), its day today, for E190; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E190 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e190.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e190.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e190.sh for today"
  [ "${RB_PLAN:-}" = e190 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E190: one RB_OUT per runbook"
  return 0
}

e190_lockcmd() {  # e190_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e190_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e190_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e190_kit_commit() {  # the kit commit, by its content (the commit that added tools/claims-v3/e190/KIT.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e190/KIT.md 2>/dev/null | tail -n 1
}

e190_built() {  # e190_built <arm>: "rgm" if step 6's wait recorded today's build for that arm (RB_OUT/e190-built-<arm>.txt), else nothing
  local f="$RB_OUT/e190-built-$1.txt"
  if [ -f "$f" ] && [ "$(TZ=America/Los_Angeles date -r "$f" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then cat "$f"; fi
}

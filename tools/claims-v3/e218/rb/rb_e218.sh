# E218 (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum): the part every E218 runbook step sources (bash 3.2 or later; the desk is
# aifoundry2, Linux). E215 arm A's runbook file (tools/claims-v3/e215/rb/rb_e215.sh, landed in 8bde0182, which ran E215 arm A FULL on aifoundry3
# today) for E218's one arm; E211's and E206's form behind it, E190's behind them. It sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe, its login-link stop,
# which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried, its prelude (aifoundry3's tree ~/aifoundry), its
# holder rule, its guard, its detached jobs, its desk-path gate and its exit codes; rb_run.py bounds and, past a bound, ends the DESK'S own ssh,
# rsync or local call, never a process on a box: every device process on the box runs under the runner's plain `timeout 10` and nothing of
# E218's ever sends it a SIGKILL), and changes only:
#   - rb_init names every step "<step>_e218";
#   - THE ONE ARM: e218_arm maps arm A to aifoundry3 (card 0) and refuses any other word (10); every box step takes the arm as its first word, and
#     every file it leaves in RB_OUT carries it (e218-built-A.txt, e218-T0-A.txt). ONE RB_OUT for the card day: the window file names its arm and
#     runbook, and every step refuses (10) a window written for another;
#   - E218's two pinned ancestors, each found by its CONTENT (both land after this file is written): the registration commit (the commit that
#     added tools/claims-v3/e218/E218.md, whose tools/claims-v3/e218 subtree reads deb6726f..., reg-e218's land) and the kit commit (the commit
#     that added tools/claims-v3/e218/KIT.md); and the freeze line of E218's points and forecasts, MM1-v3.2's land 4e386f75 (pinned: on GitHub
#     main since 19:50:09 PST Thu 19 Nov 2026);
#   - THE WINDOW RULE (E190's, E206's, E211's, E215's): e218_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the
#     Pacific calendar, names today as its day, E218 as its runbook and this step's arm; E218_BUDGET_S is the cap plus 5 minutes of closing and
#     margin before the last end at the launch (70 + 5 minutes, 4,500 s); k6's rb_need_start keeps the launch inside the registered last start
#     G + 1:30 (the budget alone would allow G + 2:15: the last start binds);
#   - THE LAB-GIT LOCK (E190's): e218_pull runs `git pull --ff-only` under RB_GITLOCK with /usr/bin/flock -w 600 -E 75: step 2 takes it itself for
#     the pull alone, so step 2 is NEVER run inside that lock (a nested flock exits 75 and step 2 stops with 16);
#   - E218's ours_live (E215's, E206's, E211's and E190's, line for line): k6's prelude is kept whole and then ours_live is redefined to read each
#     process's OWN script (the first word of its command line after the interpreter and its options; a shell's -c string never counts): a session
#     or queue of ours is a process whose script's name is session_eNNN*.sh, queue_eNNN*.py or queue_eNNN*.sh, a dry one (--dry, V3_DRY) excepted;
#     `ours_live <glob>` counts only scripts of that name (session_e218.sh: steps 10 and 11).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E218_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E218_REG_SUBTREE=deb6726f8823b6dd08a10d72ddd68837862c2a92
E218_FREEZE=4e386f7519a236fb0bf8c43d26f8303be57e09a2      # the points' and forecasts' freeze line: MM1-v3.2's land, committed 19:50:04 PST Thu 19 Nov 2026

e218_live_text() {
  cat <<'EOF'
ours_live() {  # E218's (rb/rb_e218.sh; E215's, E206's, E211's and E190's): our sessions and queues by each process's own script, never by a command string's text
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
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E218's ours_live (above)
  rb_prelude_k6 "$@" || return 1
  e218_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e218"
  RB_STEP=${1}_e218
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

e218_arm() {  # e218_arm <word>: sets ARM, BOX, CARD, DATA_SUFFIX, CAP_MIN and E218_BUDGET_S, or refuses (10)
  case "${1:-}" in
    A) ARM=A; BOX=aifoundry3; CARD=0; DATA_SUFFIX=aifoundry3; CAP_MIN=70 ;;
    *) rb_die $RB_E_USAGE "the first word is the arm: A (aifoundry3 card 0, E218's one arm)" ;;
  esac
  E218_BUDGET_S=$(( (CAP_MIN + 5) * 60 ))
  # the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
  [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E218_DESK_BUDGET_S:-}" ] && E218_BUDGET_S=$E218_DESK_BUDGET_S
  return 0
}

e218_window() {  # the window rule: window.env written today (Pacific), its day today, for E218 and this arm; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E218 arm $ARM and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e218.sh $ARM with the day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e218.sh $ARM for today first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e218.sh $ARM for today"
  [ "${RB_PLAN:-}" = e218 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E218: one RB_OUT per runbook"
  [ "${RB_ARM:-}" = "$ARM" ] || rb_die $RB_E_USAGE "RB_OUT's window was written for E218 arm ${RB_ARM:-?}, not arm $ARM: one RB_OUT per arm"
  return 0
}

e218_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): /usr/bin/flock -w 600 -E 75 <RB_GITLOCK> git -C <lab clone> pull --ff-only"
    RB_RC=0; return 0
  fi
  [ -n "${RB_GITLOCK:-}" ] || rb_die $RB_E_USAGE "RB_GITLOCK is not set (the lab-git lock every commit to the shared lab clone takes; a path outside the repo)"
  case "$(cd "$(dirname "$RB_GITLOCK")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_GITLOCK is inside the lab repo: refused" ;; esac
  [ -x /usr/bin/flock ] || rb_die $RB_E_USAGE "no /usr/bin/flock here: the lab-git lock cannot be taken"
  local lt=600; [ "${RB_DESKTEST:-}" = 1 ] && lt=${RB_GITLOCK_T:-600}     # the desk test's short wait for its nested-lock case only
  rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/flock -w "$lt" -E 75 "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
}

e218_reg_commit() {  # the registration commit, by its content (the commit that added tools/claims-v3/e218/E218.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e218/E218.md 2>/dev/null | tail -n 1
}

e218_kit_commit() {  # the kit commit, by its content (the commit that added tools/claims-v3/e218/KIT.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e218/KIT.md 2>/dev/null | tail -n 1
}

e218_jobs() {  # e218_jobs <arm>: sets J (a3), JOB_BUILD and JOB_DRY (the runbook's detached job names on the box)
  J=a3
  JOB_BUILD=$J-build-e218
  JOB_DRY=$J-dry-e218
}

e218_built() {  # e218_built <arm>: "rgm" if step 6's wait recorded today's build of both trees for that arm (RB_OUT/e218-built-<arm>.txt)
  local f="$RB_OUT/e218-built-$1.txt"
  if [ -f "$f" ] && [ "$(TZ=America/Los_Angeles date -r "$f" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then cat "$f"; fi
}

e218_homes_text() {  # the remote lines that print the box's home in every form the scrub masks (steps 8 and 11)
  cat <<'EOF'
echo "BOXHOME $HOME"
ph=$(getent passwd "$(id -u)" 2>/dev/null | cut -d: -f6); [ -n "$ph" ] && echo "BOXHOME $ph"
rp=$(cd "$HOME" 2>/dev/null && pwd -P); [ -n "$rp" ] && echo "BOXHOME $rp"
EOF
}

e218_hung_text() {  # THE HUNG MARKER (E202's fix-e202 form, E206's, E211's, E215's), the remote lines step 9 sends before the launch
  cat <<'EOF'
hung=$(grep -RhsE --include='*.log' --exclude-dir='*-dry*' --exclude-dir='*dry-t*' \
  '^[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}:[0-9]{2}([^ ]*)( [A-Z]+)? HUNG[: ]' build 2>/dev/null | head -n 3)
[ -z "$hung" ] || { echo "REFUSED: a HUNG marker of ours on the box ($(printf '%s\n' "$hung" | head -n 1 | cut -c1-220)): a device process of ours did not end after its timeout's TERM, so the card may hold a hung hart: stop and report to the owner; only his word and a dated kit amendment lift this"; exit 3; }
echo "hung: no HUNG marker in our session logs on the box"
EOF
}

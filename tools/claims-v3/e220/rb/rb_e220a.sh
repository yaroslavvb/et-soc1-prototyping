# E220 ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): the part every E220 arm A runbook step sources (bash 3.2 or later;
# the desk is aifoundry2, Linux). E218's runbook file (tools/claims-v3/e218/rb/rb_e218.sh, landed in 5582edfc, which ran E218 FULL on aifoundry3;
# E215 arm A's behind it) with E215 ARM B's box (tools/claims-v3/e215/rb/rb_e215.sh's arm B: aifoundry1 card 1, the jobs a1, the data suffix
# aifoundry1-c1). It sources the k6 runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded
# runner rb_run.py, its 15 s hard-killed probe, its login-link stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with
# nothing retried, its prelude (the box's tree: ~/nekko on aifoundry1), its holder rule, its guard, its detached jobs, its desk-path gate and its
# exit codes; rb_run.py bounds and, past a bound, ends the DESK'S own ssh, rsync or local call, never a process on a box: every device process on
# the box runs under the runner's plain timeout and nothing of E220's ever sends it a SIGKILL), and changes only:
#   - rb_init names every step "<step>_e220a";
#   - THE ARM: e220a_arm maps arm A to aifoundry1 (card 1) and refuses any other word (10); every box step takes the arm as its first word, and
#     every file it leaves in RB_OUT carries it (e220a-built-A.txt, e220a-T0-A.txt). ONE RB_OUT for the card day: the window file names its arm and
#     runbook, and every step refuses (10) a window written for another;
#   - E220's two ancestors found by their CONTENT (both land after this file is written): THE REGISTRATION COMMIT (the commit that added
#     tools/claims-v3/e220/E220.md, whose tools/claims-v3/e220 subtree reads 46dde0fd..., reg-e220's: ITS PUSH IS THE FREEZE LINE OF EVERY E220
#     FORECAST, E220.md section 0) and the kit commit (the commit that added tools/claims-v3/e220/KIT.md); and MM1-v3.2's land 4e386f75 (pinned:
#     the models the registration's forecasts were made by, on GitHub main since 19:50:09 PST Thu 19 Nov 2026);
#   - THE WINDOW RULE (E190's, E206's, E211's, E215's, E218's): e220a_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by
#     the Pacific calendar, names today as its day, E220 as its runbook and this step's arm; E220A_BUDGET_S is the cap plus 5 minutes of closing
#     and margin before the last end at the launch (70 + 5 minutes, 4,500 s); k6's rb_need_start keeps the launch inside the registered last start
#     G + 1:30 (the budget alone would allow G + 2:15: the last start binds);
#   - THE LAB-GIT LOCK (E190's): e220a_pull runs `git pull --ff-only` under RB_GITLOCK with /usr/bin/flock -w 600 -E 75: step 2 takes it itself for
#     the pull alone, so step 2 is NEVER run inside that lock (a nested flock exits 75 and step 2 stops with 16);
#   - E220's ours_live (E218's, E215's, E206's, E211's and E190's, line for line): k6's prelude is kept whole and then ours_live is redefined to
#     read each process's OWN script (the first word of its command line after the interpreter and its options; a shell's -c string never counts):
#     a session or queue of ours is a process whose script's name is session_eNNN*.sh, queue_eNNN*.py or queue_eNNN*.sh, a dry one (--dry, V3_DRY)
#     excepted; `ours_live <glob>` counts only scripts of that name (session_e220a.sh: steps 10 and 11).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E220A_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E220A_REG_SUBTREE=46dde0fdaac96f58bb9a33e09eb47748654754c5
E220A_FREEZE=4e386f7519a236fb0bf8c43d26f8303be57e09a2      # MM1-v3.2's land (the models E220's forecasts were made by), committed 19:50:04 PST Thu 19 Nov 2026

e220a_live_text() {
  cat <<'EOF'
ours_live() {  # E220's (rb/rb_e220a.sh; E215's, E206's, E211's and E190's): our sessions and queues by each process's own script, never by a command string's text
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
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E220's ours_live (above)
  rb_prelude_k6 "$@" || return 1
  e220a_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e220a"
  RB_STEP=${1}_e220a
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

e220a_arm() {  # e220a_arm <word>: sets ARM, BOX, CARD, DATA_SUFFIX, CAP_MIN and E220A_BUDGET_S, or refuses (10)
  case "${1:-}" in
    A) ARM=A; BOX=aifoundry1; CARD=1; DATA_SUFFIX=aifoundry1-c1; CAP_MIN=70 ;;
    *) rb_die $RB_E_USAGE "the first word is the arm: A (aifoundry1 card 1, E220 arm A's runbook; arm B, aifoundry2 card 0, has its own: rb/rb_e220b.sh)" ;;
  esac
  E220A_BUDGET_S=$(( (CAP_MIN + 5) * 60 ))
  # the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
  [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E220A_DESK_BUDGET_S:-}" ] && E220A_BUDGET_S=$E220A_DESK_BUDGET_S
  return 0
}

e220a_window() {  # the window rule: window.env written today (Pacific), its day today, for E220 and this arm; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E220 arm $ARM and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e220a.sh $ARM with the day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e220a.sh $ARM for today first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e220a.sh $ARM for today"
  [ "${RB_PLAN:-}" = e220a ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E220: one RB_OUT per runbook"
  [ "${RB_ARM:-}" = "$ARM" ] || rb_die $RB_E_USAGE "RB_OUT's window was written for E220 arm ${RB_ARM:-?}, not arm $ARM: one RB_OUT per arm"
  return 0
}

e220a_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
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

e220a_reg_commit() {  # the registration commit, by its content (the commit that added tools/claims-v3/e220/E220.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e220/E220.md 2>/dev/null | tail -n 1
}

e220a_kit_commit() {  # the kit commit, by its content (the commit that added tools/claims-v3/e220/KIT.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e220/KIT.md 2>/dev/null | tail -n 1
}

e220a_jobs() {  # e220a_jobs <arm>: sets J (a1), JOB_BUILD and JOB_DRY (the runbook's detached job names on the box)
  J=a1
  JOB_BUILD=$J-build-e220a
  JOB_DRY=$J-dry-e220a
}

e220a_built() {  # e220a_built <arm>: "rgm" if step 6's wait recorded today's build of both trees for that arm (RB_OUT/e220a-built-<arm>.txt)
  local f="$RB_OUT/e220a-built-$1.txt"
  if [ -f "$f" ] && [ "$(TZ=America/Los_Angeles date -r "$f" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then cat "$f"; fi
}

e220a_homes_text() {  # the remote lines that print the box's home in every form the scrub masks (steps 8 and 11)
  cat <<'EOF'
echo "BOXHOME $HOME"
ph=$(getent passwd "$(id -u)" 2>/dev/null | cut -d: -f6); [ -n "$ph" ] && echo "BOXHOME $ph"
rp=$(cd "$HOME" 2>/dev/null && pwd -P); [ -n "$rp" ] && echo "BOXHOME $rp"
EOF
}

e220a_hung_text() {  # THE HUNG MARKER (E202's fix-e202 form, E206's, E211's, E215's), the remote lines step 9 sends before the launch
  cat <<'EOF'
hung=$(grep -RhsE --include='*.log' --exclude-dir='*-dry*' --exclude-dir='*dry-t*' \
  '^[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}:[0-9]{2}([^ ]*)( [A-Z]+)? HUNG[: ]' build 2>/dev/null | head -n 3)
[ -z "$hung" ] || { echo "REFUSED: a HUNG marker of ours on the box ($(printf '%s\n' "$hung" | head -n 1 | cut -c1-220)): a device process of ours did not end after its timeout's TERM, so the card may hold a hung hart: stop and report to the owner; only his word and a dated kit amendment lift this"; exit 3; }
echo "hung: no HUNG marker in our session logs on the box"
EOF
}

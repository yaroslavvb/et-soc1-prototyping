# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): the part every E213 runbook step sources (bash 3.2 or later; the desk is
# aifoundry2, Linux). E211's runbook file (tools/claims-v3/e211/rb/rb_e211.sh, landed in 2b7f261f, which ran E211 FULL on aifoundry3) with E206's
# two arms (tools/claims-v3/e206/rb/rb_e206.sh, landed in 906699ea, which ran E206 arm A on aifoundry3 and arm B on aifoundry1 card 1); E190's form
# behind both. It sources the k6 runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner
# rb_run.py, its 15 s hard-killed probe, its login-link stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing
# retried, its prelude (each box's tree: aifoundry3 ~/aifoundry, aifoundry1 ~/nekko), its holder rule, its guard, its detached jobs, its desk-path
# gate and its exit codes; rb_run.py bounds and, past a bound, ends the DESK'S own ssh, rsync or local call, never a process on a box: every device
# process on a box runs under the runner's plain `timeout 10` and nothing of E213's ever sends it a SIGKILL), and changes only:
#   - rb_init names every step "<step>_e213";
#   - THE TWO ARMS: e213_arm maps arm A to aifoundry3 (card 0) and arm B to aifoundry1 (card 1); every box step takes the arm as its first word,
#     and every file it leaves in RB_OUT carries the arm (e213-built-A.txt, e213-T0-B.txt). ONE RB_OUT PER ARM: the window file names its arm,
#     and every step refuses (10) a window written for the other arm (each arm is its own card lane, G its own booking);
#   - E213's two pinned ancestors, each found by its CONTENT (both land after this file is written): the registration commit (the commit that
#     added tools/claims-v3/e213/E213.md, whose tools/claims-v3/e213 subtree reads 75778ad3..., reg-e213's land) and the kit commit (the commit
#     that added tools/claims-v3/e213/KIT.md);
#   - THE WINDOW RULE (E190's, E206's, E211's): e213_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific
#     calendar, names today as its day, E213 as its runbook and this step's arm; E213_BUDGET_S is the arm's cap plus 5 minutes of closing and
#     margin before the last end at the launch (arm A 70 + 5 minutes, 4,500 s; arm B 48 + 5, 3,180 s); k6's rb_need_start keeps the launch inside
#     the registered last start G + 1:30 (the budget alone would allow G + 2:15 for arm A and G + 2:37 for arm B: the last start binds);
#   - THE LAB-GIT LOCK (E190's): e213_pull runs `git pull --ff-only` under RB_GITLOCK with /usr/bin/flock -w 600 -E 75: step 2 takes it itself for
#     the pull alone, so step 2 is NEVER run inside that lock (a nested flock exits 75 and step 2 stops with 16);
#   - E213's ours_live (E206's, E211's and E190's, line for line): k6's prelude is kept whole and then ours_live is redefined to read each
#     process's OWN script (the first word of its command line after the interpreter and its options; a shell's -c string never counts): a session
#     or queue of ours is a process whose script's name is session_eNNN*.sh, queue_eNNN*.py or queue_eNNN*.sh, a dry one (--dry, V3_DRY) excepted;
#     `ours_live <glob>` counts only scripts of that name (session_e213.sh: steps 10 and 11).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E213_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E213_REG_SUBTREE=75778ad39efc1ed128ac413cfe3c53144c0101a2
E213_ARM_A_FREEZE=b149308280a73396516937304037af57a5563c16      # arm A's freeze line: MM1-v3's land, pushed 20:52:46 PST Tue 17 Nov 2026

e213_live_text() {
  cat <<'EOF'
ours_live() {  # E213's (rb/rb_e213.sh; E206's, E211's and E190's): our sessions and queues by each process's own script, never by a command string's text
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
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E213's ours_live (above)
  rb_prelude_k6 "$@" || return 1
  e213_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e213"
  RB_STEP=${1}_e213
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

e213_arm() {  # e213_arm <word>: sets ARM, BOX, CARD, DATA_SUFFIX, CAP_MIN and E213_BUDGET_S, or refuses (10)
  case "${1:-}" in
    A) ARM=A; BOX=aifoundry3; CARD=0; DATA_SUFFIX=aifoundry3; CAP_MIN=70 ;;
    B) ARM=B; BOX=aifoundry1; CARD=1; DATA_SUFFIX=aifoundry1-c1; CAP_MIN=48 ;;
    *) rb_die $RB_E_USAGE "the first word is the arm: A (aifoundry3 card 0) or B (aifoundry1 card 1)" ;;
  esac
  E213_BUDGET_S=$(( (CAP_MIN + 5) * 60 ))
  # the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
  [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E213_DESK_BUDGET_S:-}" ] && E213_BUDGET_S=$E213_DESK_BUDGET_S
  return 0
}

e213_window() {  # the window rule: window.env written today (Pacific), its day today, for E213 and this arm; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E213 arm $ARM and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e213.sh $ARM with the day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e213.sh $ARM for today first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e213.sh $ARM for today"
  [ "${RB_PLAN:-}" = e213 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E213: one RB_OUT per runbook"
  [ "${RB_ARM:-}" = "$ARM" ] || rb_die $RB_E_USAGE "RB_OUT's window was written for E213 arm ${RB_ARM:-?}, not arm $ARM: one RB_OUT per arm"
  return 0
}

e213_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
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

e213_reg_commit() {  # the registration commit, by its content (the commit that added tools/claims-v3/e213/E213.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e213/E213.md 2>/dev/null | tail -n 1
}

e213_kit_commit() {  # the kit commit, by its content (the commit that added tools/claims-v3/e213/KIT.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e213/KIT.md 2>/dev/null | tail -n 1
}

e213_jobs() {  # e213_jobs <arm>: sets J (a3 or a1), JOB_BUILD and JOB_DRY (the runbook's detached job names on the box)
  J=$([ "$1" = A ] && echo a3 || echo a1)
  JOB_BUILD=$J-build-e213
  JOB_DRY=$J-dry-e213
}

e213_built() {  # e213_built <arm>: "rgm" if step 6's wait recorded today's build of both kernels for that arm (RB_OUT/e213-built-<arm>.txt)
  local f="$RB_OUT/e213-built-$1.txt"
  if [ -f "$f" ] && [ "$(TZ=America/Los_Angeles date -r "$f" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then cat "$f"; fi
}

e213_homes_text() {  # the remote lines that print the box's home in every form the scrub masks (steps 8 and 11)
  cat <<'EOF'
echo "BOXHOME $HOME"
ph=$(getent passwd "$(id -u)" 2>/dev/null | cut -d: -f6); [ -n "$ph" ] && echo "BOXHOME $ph"
rp=$(cd "$HOME" 2>/dev/null && pwd -P); [ -n "$rp" ] && echo "BOXHOME $rp"
EOF
}

e213_hung_text() {  # THE HUNG MARKER (E202's fix-e202 form, E206's, E211's), the remote lines step 9 sends before the launch
  cat <<'EOF'
hung=$(grep -RhsE --include='*.log' --exclude-dir='*-dry*' --exclude-dir='*dry-t*' \
  '^[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}:[0-9]{2}([^ ]*)( [A-Z]+)? HUNG[: ]' build 2>/dev/null | head -n 3)
[ -z "$hung" ] || { echo "REFUSED: a HUNG marker of ours on the box ($(printf '%s\n' "$hung" | head -n 1 | cut -c1-220)): a device process of ours did not end after its timeout's TERM, so the card may hold a hung hart: stop and report to the owner; only his word and a dated kit amendment lift this"; exit 3; }
echo "hung: no HUNG marker in our session logs on the box"
EOF
}

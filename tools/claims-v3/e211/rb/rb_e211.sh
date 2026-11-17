# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): the part every E211 runbook step sources (bash 3.2 or later; the desk is
# aifoundry2, Linux). E206's runbook file (tools/claims-v3/e206/rb/rb_e206.sh, landed in 906699ea, which ran E206 arm A FULL on this card), as
# E207's kit ported it to one arm (Q199), for E211's one arm; E190's form behind it. It sources the k6 runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED
# (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe, its login-link stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK
# and exits 11 with nothing retried, its prelude (aifoundry3's tree ~/aifoundry), its holder rule, its guard, its detached jobs, its desk-path
# gate and its exit codes; rb_run.py bounds and, past a bound, ends the DESK'S own ssh, rsync or local call, never a process on a box: every
# device process on the box runs under the runner's plain `timeout 10` and nothing of E211's ever sends it a SIGKILL), and changes only:
#   - rb_init names every step "<step>_e211";
#   - THE ONE ARM: e211_arm maps A (E206's word for it, kept so the scorer's data form holds) to aifoundry3 (card 0) and refuses any other
#     word; every box step takes A as its first word, and every file it leaves in RB_OUT carries it (e211-built-A.txt, e211-T0-A.txt);
#   - E211's two pinned ancestors, each found by its CONTENT (both land after this file is written): the registration commit (the commit that
#     added tools/claims-v3/e211/E211.md, whose tools/claims-v3/e211 subtree reads fa109d01..., reg-e211's land as fix-e211 amended it) and the kit
#     commit (the commit that added tools/claims-v3/e211/KIT.md);
#   - THE WINDOW RULE (E190's, E206's): e211_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific calendar,
#     names today as its day, E211 as its runbook and arm A; E211_BUDGET_S, 2,400 s, is the session's 35-minute cap plus 5 minutes of closing
#     and margin before the last end at the launch; k6's rb_need_start keeps the launch inside the registered last start G + 1:30 (with the
#     35-minute cap the budget alone would allow G + 2:50: the last start is the binding rule here);
#   - THE LAB-GIT LOCK (E190's): e211_pull runs `git pull --ff-only` under RB_GITLOCK with /usr/bin/flock -w 600 -E 75: step 2 takes it
#     itself for the pull alone, so step 2 is NEVER run inside that lock (a nested flock exits 75 and step 2 stops with 16);
#   - E211's ours_live (E206's and E190's, line for line): k6's prelude is kept whole and then ours_live is redefined to read each process's
#     OWN script (the first word of its command line after the interpreter and its options; a shell's -c string never counts): a session or
#     queue of ours is a process whose script's name is session_eNNN*.sh, queue_eNNN*.py or queue_eNNN*.sh, a dry one (--dry, V3_DRY)
#     excepted; `ours_live <glob>` counts only scripts of that name (session_e211.sh: steps 10 and 11).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E211_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E211_REG_SUBTREE=fa109d016f5e0497a5ee5d34a69806ad2b3be511
E211_BUDGET_S=2400
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E211_DESK_BUDGET_S:-}" ] && E211_BUDGET_S=$E211_DESK_BUDGET_S

e211_live_text() {
  cat <<'EOF'
ours_live() {  # E211's (rb/rb_e211.sh; E206's and E190's): our sessions and queues by each process's own script, never by a command string's text
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
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E211's ours_live (above)
  rb_prelude_k6 "$@" || return 1
  e211_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e211"
  RB_STEP=${1}_e211
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

e211_arm() {  # e211_arm <word>: sets ARM, BOX, CARD and DATA_SUFFIX, or refuses (10); E211 has one arm, A (aifoundry3 card 0)
  case "${1:-}" in
    A) ARM=A; BOX=aifoundry3; CARD=0; DATA_SUFFIX=aifoundry3 ;;
    *) rb_die $RB_E_USAGE "the first word is the arm: A (aifoundry3 card 0), E211's one arm" ;;
  esac
}

e211_window() {  # the window rule: window.env written today (Pacific), its day today, for E211 and its arm; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E211 arm $ARM and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e211.sh $ARM with the day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e211.sh $ARM for today first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e211.sh $ARM for today"
  [ "${RB_PLAN:-}" = e211 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E211: one RB_OUT per runbook"
  [ "${RB_ARM:-}" = "$ARM" ] || rb_die $RB_E_USAGE "RB_OUT's window was written for arm ${RB_ARM:-?}, not E211's arm $ARM"
  return 0
}

e211_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
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

e211_reg_commit() {  # the registration commit, by its content (the commit that added tools/claims-v3/e211/E211.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e211/E211.md 2>/dev/null | tail -n 1
}

e211_kit_commit() {  # the kit commit, by its content (the commit that added tools/claims-v3/e211/KIT.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e211/KIT.md 2>/dev/null | tail -n 1
}

e211_jobs() {  # e211_jobs <arm>: sets J (a3), JOB_BUILD and JOB_DRY (the runbook's detached job names on the box)
  J=a3
  JOB_BUILD=$J-build-e211
  JOB_DRY=$J-dry-e211
}

e211_built() {  # e211_built <arm>: "rgm" if step 6's wait recorded today's build of both kernels (RB_OUT/e211-built-<arm>.txt), else nothing
  local f="$RB_OUT/e211-built-$1.txt"
  if [ -f "$f" ] && [ "$(TZ=America/Los_Angeles date -r "$f" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then cat "$f"; fi
}

e211_hung_text() {  # THE HUNG MARKER (E202's fix-e202 form, E206's), the remote lines step 9 sends before the launch
  cat <<'EOF'
hung=$(grep -RhsE --include='*.log' --exclude-dir='*-dry*' --exclude-dir='*dry-t*' \
  '^[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}:[0-9]{2}([^ ]*)( [A-Z]+)? HUNG[: ]' build 2>/dev/null | head -n 3)
[ -z "$hung" ] || { echo "REFUSED: a HUNG marker of ours on the box ($(printf '%s\n' "$hung" | head -n 1 | cut -c1-220)): a device process of ours did not end after its timeout's TERM, so the card may hold a hung hart: stop and report to the owner; only his word and a dated kit amendment lift this"; exit 3; }
echo "hung: no HUNG marker in our session logs on the box"
EOF
}

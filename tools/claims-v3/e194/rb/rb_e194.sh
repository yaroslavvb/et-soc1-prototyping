# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the part every E194 runbook step
# sources (bash 3.2 or later). THE DESK AND THE BOX ARE ONE MACHINE: E194 runs on aifoundry2's own card 0, orchestrated from aifoundry2,
# as E190's arm A did (Fri 13 Nov 2026): every box call goes through k6's drivers to aifoundry2 itself (ssh to this box, its tree
# ~/claude/et-soc1-prototyping, k6's rb_tree for aifoundry2), and no other box is ever reached. E191's runbook file's form
# (tools/claims-v3/e191/rb/rb_e191.sh, eb1ac923, unchanged beside it): it sources the k6 runbook's common library,
# tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed probe, its login-link
# stop, its prelude with each box's tree, its holder read, its guard (rb_guard_text: no launch during a dry pass or beside a session of
# ours, and on aifoundry2 none on a host booted after E69's firmware read of record, 2026-10-27 13:56:26 PDT), its detached jobs, its
# desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e194";
#   - E191's ours_live (E190's by each process's OWN script, with E191's interpreter condition): on this box the desk's own commands run
#     beside the box's reads (E190's kit section 4, item 18, found k6's text-matched count reading the desk's own step names as sessions:
#     the transient refusals of E190 arm A's day), so only a process whose own script is session_eNNN*.sh, queue_eNNN* or one of k6's
#     named runs counts; `ours_live <glob>` counts one name (session_e194.sh: steps 10 and 11);
#   - THE REGISTRATION, found by its CONTENT (it is not landed when this file is written, so no commit is pinned): the commit that added
#     tools/claims-v3/e194/E194.md; step 2 pins its list SHA256SUMS-e194-registration (17 entries, its own sha256 788af7da...) and
#     E194.md's own sha256 (a8ed7f50...); THE KIT COMMIT is found by its content (the commit that added tools/claims-v3/e194/KIT.md);
#   - E194's box (aifoundry2, card 0), its plan's budget: the session's cap, 110 card-minutes (6,600 s; E194.md 10);
#   - THE WINDOW RULE (E189's): e194_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific calendar, and
#     names today as its day and E194 as its runbook;
#   - THE LAB-GIT LOCK (E189's): e194_pull runs `git pull --ff-only` in the lab clone under RB_GITLOCK (flock -w 600 -E 75): step 2 takes
#     it itself for the pull alone, so step 2 is NEVER run inside that lock;
#   - THE QUIET DESK FLAG (E194.md 13; E190's card-lane brief, dated note 1, section 4): RB_QUIET names the round's quiet-desk flag file for
#     aifoundry2 (outside the repo); rb/quiet_e194.sh raises it right before the look and lowers it after the copy-back; every step from
#     the look (4) to the collection (11) refuses (10) unless it is raised (e194_quiet).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E194_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E194_BOX=aifoundry2
E194_BUDGET_S=6600
E194_REG_LIST_SHA=788af7da85edd049db1a1e6cf8f273018472b1e576ab131ba9ffeb0d6dc8b7d0      # SHA256SUMS-e194-registration (17 entries)
E194_MD_SHA=a8ed7f5027c8bbd442cea70142565a7ae61bb327988406290565807c00d84905           # E194.md as registered
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E194_DESK_BUDGET_S:-}" ] && E194_BUDGET_S=$E194_DESK_BUDGET_S

e194_live_text() {
  cat <<'EOF'
ours_live() {  # E194's (E191's, E190's form): our sessions and queues by each process's own script, never by a command string's text
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
p2_count() {  # E194: THE QUIET DESK FLAG's count on this box (E190's card-lane brief, dated note 1, section 4): device-named processes of
  #            ours (lib.sh's DEV_COMM on ps's comm) and session or queue scripts of ours (ours_live); prints "P2 <n> (<a> device-named, <b> scripts)"
  local a b
  a=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  b=$(ours_live)
  echo "P2 $((a + b)) ($a device-named process(es) of ours, $b session or queue script(s) of ours)"
}
EOF
}
eval "$(declare -f rb_prelude | sed '1s/^rb_prelude /rb_prelude_k6 /')"     # k6's prelude, kept whole under another name
rb_prelude() {  # rb_prelude <box>: k6's prelude, then E194's ours_live and P2 count (above)
  rb_prelude_k6 "$@" || return 1
  e194_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e194"
  RB_STEP=${1}_e194
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

e194_kit_commit() {  # the kit commit, by its content (the commit that added tools/claims-v3/e194/KIT.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e194/KIT.md 2>/dev/null | tail -n 1
}

e194_reg_commit() {  # the registration commit, by its content (the commit that added tools/claims-v3/e194/E194.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e194/E194.md 2>/dev/null | tail -n 1
}

e194_window() {  # the window rule: window.env written today (Pacific), its day today, for E194; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E194 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e194.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e194.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e194.sh for today"
  [ "${RB_PLAN:-}" = e194 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E194: one RB_OUT per runbook"
  return 0
}

e194_quiet() {  # THE QUIET DESK FLAG must be raised (rb/quiet_e194.sh raise) for every step from the look to the collection
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: THE QUIET DESK FLAG raised (RB_QUIET, the round's flag file for aifoundry2, outside the repo)"; return 0; fi
  [ -n "${RB_QUIET:-}" ] || rb_die $RB_E_USAGE "RB_QUIET is not set (the round's quiet-desk flag file for aifoundry2, outside the repo)"
  case "$(cd "$(dirname "$RB_QUIET")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_QUIET is inside the lab repo: refused" ;; esac
  [ -f "$RB_QUIET" ] || rb_die $RB_E_USAGE "THE QUIET DESK FLAG is not raised ($RB_QUIET absent): run rb/quiet_e194.sh raise right before the look"
  return 0
}

e194_lockcmd() {  # e194_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e194_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e194_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e194_programs() {  # the programs built today on the box, from step 6's job output (RB_OUT/e194-built.txt, written by step 6's wait)
  if [ -f "$RB_OUT/e194-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e194-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then
    cat "$RB_OUT/e194-built.txt"
  fi
}

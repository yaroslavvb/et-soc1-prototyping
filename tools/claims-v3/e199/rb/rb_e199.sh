# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): the part every E199 runbook step sources (bash 3.2 or later; the
# desk is aifoundry2, Linux; the box aifoundry1, card 1, k6's tree there ~/nekko). E192's runbook file (tools/claims-v3/e192/rb/rb_e192.sh,
# a6fe5c20, unchanged beside it) in E191's form for aifoundry1 (tools/claims-v3/e191/rb/rb_e191.sh, unchanged beside it): it sources the k6
# runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s
# hard-killed probe, THE LOGIN CHECK: a printed login link stops the step with 11 and appends "<HH:MM:SS> <box> needs a check" to RB_LOCK,
# nothing retried; its prelude with aifoundry1's tree ~/nekko, its holder read, its guard rb_guard_text (no launch during a dry pass or
# beside a session of ours, and on aifoundry1 none on a host booted after E82's firmware read of record, 2026-10-31 13:45:24 PDT: THE
# REBOOT GATE), its detached jobs, its desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e199";
#   - E191's ours_live (E190's form: our sessions and queues by each process's OWN script, an interpreter's first word, never a command
#     string that only names one), appended to k6's prelude as E191's rb_e191.sh does, so every remote script's ours_live counts E190 arm
#     B's session_e190_v2.sh, E191's session_e191(_v2).sh, E198's and E199's own session_e199.sh, and skips a dry pass (--dry);
#   - E199's registration found by its content (the commit that added tools/claims-v3/e199/E199.md, whose tools/claims-v3/e199 subtree
#     reads 070b4e2d..., Sun 15 Nov 2026, fixed Mon 16 Nov 2026 by fix-e199, before any datum), its list at 4d05fe0a... (17), and E192's registration list at dd0a8963... (30),
#     whose proposal E199 runs;
#   - E199's box (aifoundry1 card 1; k6's tree ~/nekko), E199's root there (build/claims-v3/aifoundry1-c1/e199: lib.sh's card-1 data root;
#     the synced files at their repository paths and the build), the session's cap, 65 card-minutes (3,900 s; E199.md section 8);
#   - THE WINDOW RULE (E188's, E189's): e199_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific
#     calendar, names today as its day and E199 as its runbook;
#   - THE LAB-GIT LOCK (E188's step 2 v2's way): e199_pull runs `git pull --ff-only` under RB_GITLOCK, `/usr/bin/flock -w 600 -E 75` on
#     Linux (aifoundry2's commit script takes the same lock); a timeout exits 75, so step 2 run INSIDE that lock stops with 16.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E199_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E199_REG_SUBTREE=070b4e2d9135c952cac0dcf61e212efd732ada8e
E199_REG_LIST_SHA=4d05fe0a7e6cadb6e3a2f0bf303d5f6804345c4ce9f738033a598ae926fff35f
E192_REG_LIST_SHA=dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326
E199_BOX=aifoundry1
E183_BOX=aifoundry1          # read by E183's desk-path gate (rb/nopath_desk_e183.sh, sourced unchanged by step 11)
E199_R=build/claims-v3/aifoundry1-c1/e199
E199_BUDGET_S=3900
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E199_DESK_BUDGET_S:-}" ] && E199_BUDGET_S=$E199_DESK_BUDGET_S

e199_live_text() {
  cat <<'EOF'
ours_live() {  # E191's (rb_e191.sh, itself E190's rb_e190.sh form), unchanged: our sessions and queues by each process's own script, never by a command string's text
  local n=0 pid w s first dashc interp want=${1:-}
  for pid in $(pgrep -u "$(id -u)" . 2>/dev/null); do
    s=""; first=1; dashc=0; interp=0
    while IFS= read -r -d '' w; do
      if [ "$first" = 1 ]; then
        first=0
        case "${w##*/}" in bash|sh|dash|python|python3|python3.[0-9]*) interp=1 ;; esac     # E191's: an interpreter's script only
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
  e199_live_text
}

rb_init() {  # rb_init <step>: k6's, with the step named "_e199"
  RB_STEP=${1}_e199
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

e199_window() {  # the window rule: window.env written today (Pacific), its day today, for E199; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E199 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e199.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e199.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e199.sh for today"
  [ "${RB_PLAN:-}" = e199 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E199: one RB_OUT per runbook"
  return 0
}

e199_lockcmd() {  # e199_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e199_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e199_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e199_kitlist_sha() {  # the kit list's sha256 in the lab clone (step 2 pins it; steps 8 and 9 pass it to the session, which checks the box's copy)
  [ -n "${RB_DRY:-}" ] && { echo "<the kit list's sha256>"; return 0; }
  sha256sum "$RB_REPO/tools/claims-v3/e199/SHA256SUMS-e199-kit" 2>/dev/null | cut -d' ' -f1
}

e199_built() {  # what step 6's wait recorded today (RB_OUT/e199-built.txt), or nothing
  if [ -f "$RB_OUT/e199-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e199-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then
    cat "$RB_OUT/e199-built.txt"
  fi
}

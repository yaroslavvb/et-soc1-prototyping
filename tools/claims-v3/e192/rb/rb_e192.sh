# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): the part every E192 runbook step sources (bash 3.2 or later; the
# desk is aifoundry2, Linux, or a Mac). E189's runbook file's form (tools/claims-v3/e189/rb/rb_e189.sh): it sources the k6 runbook's
# common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s hard-killed
# probe, THE LOGIN CHECK: a printed login link stops the step with 11 and appends "<HH:MM:SS> <box> needs a check" to RB_LOCK, nothing
# retried; its prelude, its holder rule, its detached jobs, its desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e192";
#   - E192's registration is found by its content (the commit that added tools/claims-v3/e192/E192.md, whose tools/claims-v3/e192 subtree
#     reads c78351f9..., the registration with both freeze lines, Sat 14 Nov 2026, before any datum), its list at dd0a8963... (30);
#   - E192's box (aifoundry3 card 0; k6's tree ~/aifoundry), E192's root there (build/claims-v3/aifoundry3/e192: the synced files at their
#     repository paths and the build), the session's cap, 65 card-minutes (3,900 s; E192.md section 10);
#   - THE WINDOW RULE (E188's, E189's): e192_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific
#     calendar, names today as its day and E192 as its runbook;
#   - THE LAB-GIT LOCK (E188's step 2 v2's way): e192_pull runs `git pull --ff-only` under RB_GITLOCK, `/usr/bin/flock -w 600 -E 75` on Linux
#     (aifoundry2's commit script takes the same lock), `/usr/bin/lockf -k -t 600` where it exists (a Mac); both exit 75 on a timeout, so
#     step 2 run INSIDE that lock stops with 16. RB_GITLOCK (a path outside the repo) is required by step 2.
# k6's ours_live counts any session_eNNN.sh of ours by the lab's naming rule, so E192's session (session_e192.sh) is counted with no change;
# its dry pass runs with --dry on its command line, which ours_live skips.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E192_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E192_REG_SUBTREE=c78351f9309b65a02a2a4d589cfb8b93fd77c2ba
E192_REG_LIST_SHA=dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326
E192_BOX=aifoundry3
E183_BOX=aifoundry3          # read by E183's desk-path gate (rb/nopath_desk_e183.sh, sourced unchanged by step 11)
E192_R=build/claims-v3/aifoundry3/e192
E192_BUDGET_S=3900
# the runbook desk test's short budget (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E192_DESK_BUDGET_S:-}" ] && E192_BUDGET_S=$E192_DESK_BUDGET_S

rb_init() {  # rb_init <step>: k6's, with the step named "_e192"
  RB_STEP=${1}_e192
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

e192_window() {  # the window rule: window.env written today (Pacific), its day today, for E192; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E192 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e192.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e192.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e192.sh for today"
  [ "${RB_PLAN:-}" = e192 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E192: one RB_OUT per runbook"
  return 0
}

e192_lockcmd() {  # e192_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e192_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e192_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e192_kitlist_sha() {  # the kit list's sha256 in the lab clone (step 2 pins it; steps 8 and 9 pass it to the session, which checks the box's copy)
  [ -n "${RB_DRY:-}" ] && { echo "<the kit list's sha256>"; return 0; }
  sha256sum "$RB_REPO/tools/claims-v3/e192/SHA256SUMS-e192-kit" 2>/dev/null | cut -d' ' -f1
}

e192_built() {  # what step 6's wait recorded today (RB_OUT/e192-built.txt), or nothing
  if [ -f "$RB_OUT/e192-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e192-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then
    cat "$RB_OUT/e192-built.txt"
  fi
}

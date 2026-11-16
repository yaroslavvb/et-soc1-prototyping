# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): the part every E195 runbook step sources (bash 3.2 or later; the
# desk is aifoundry2, Linux, or a Mac). E192's runbook file's form (tools/claims-v3/e192/rb/rb_e192.sh, itself E189's): it sources the k6
# runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s
# hard-killed probe, THE LOGIN CHECK: a printed login link stops the step with 11 and appends "<HH:MM:SS> <box> needs a check" to RB_LOCK,
# nothing retried; its prelude, its holder rule, its guard, its detached jobs, its desk-path gate and its exit codes), and changes only:
#   - rb_init names every step "<step>_e195";
#   - E195's registration is found by its content (the commit that added tools/claims-v3/e195/E195.md, whose tools/claims-v3/e195 subtree
#     reads 7b9aa484..., the registration with its freeze line, Sun 15 Nov 2026, before any datum), its list at ba6849ce... (41 entries);
#     RB_E195_BASE, the commit an E195 tree must descend from: e8a85229 (GitHub main when E195 was registered);
#   - E195's box (aifoundry3 card 0; k6's tree ~/aifoundry), E195's root there (build/claims-v3/aifoundry3/e195: the synced files at their
#     repository paths, the build, the data folders), the session's cap, 45 card-minutes (2,700 s; E195.md sections 6 and 11);
#   - THE WINDOW RULE (E188's, E189's, E192's): e195_window refuses (10) unless RB_OUT's window.env exists, was written TODAY by the Pacific
#     calendar, names today as its day and E195 as its runbook;
#   - THE LAB-GIT LOCK (E192's way): e195_pull runs `git pull --ff-only` under RB_GITLOCK, `/usr/bin/flock -w 600 -E 75` on Linux,
#     `/usr/bin/lockf -k -t 600` where it exists (a Mac); both exit 75 on a timeout, so step 2 run INSIDE that lock stops with 16.
# k6's ours_live counts any session_eNNN.sh of ours by the lab's naming rule, so E195's session (session_e195.sh) is counted with no change;
# its dry pass runs with --dry on its command line, which ours_live skips.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E195_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E195_BASE=${RB_E195_BASE:-e8a85229}
E195_REG_SUBTREE=7b9aa48497a4b763abec3c9eb0c1f2412ebfd5b2
E195_REG_LIST_SHA=ba6849ce6e3d17cde3c46a2cba4ca9e70afd38fca831ac7edb91cf956a163cec
E195_BOX=aifoundry3
E183_BOX=aifoundry3          # read by E183's desk-path gate (rb/nopath_desk_e183.sh, sourced unchanged by step 11)
E195_R=build/claims-v3/aifoundry3/e195
E195_CAP_S=2700
# the runbook desk test's short cap (its window is today's last minutes): read only with RB_DESKTEST=1; the card day never sets it
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E195_DESK_CAP_S:-}" ] && E195_CAP_S=$E195_DESK_CAP_S

rb_init() {  # rb_init <step>: k6's, with the step named "_e195"
  RB_STEP=${1}_e195
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

e195_window() {  # the window rule: window.env written today (Pacific), its day today, for E195; then k6's rb_window reads it
  if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT's window.env written today (Pacific) for E195 and naming today; its last start and last end read"; rb_window; return 0; fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e195.sh with his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e195.sh with his go's day, last start and last end first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e195.sh for today"
  [ "${RB_PLAN:-}" = e195 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E195: one RB_OUT per runbook"
  return 0
}

e195_lockcmd() {  # e195_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e195_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e195_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e195_harness_sha() {  # the committed harness-e195.json's sha256 in the lab clone (step 2 pins it by the kit's list; steps 8 and 9 pass it)
  [ -n "${RB_DRY:-}" ] && { echo "<harness-e195.json's sha256>"; return 0; }
  sha256sum "$RB_REPO/tools/claims-v3/e195/harness-e195.json" 2>/dev/null | cut -d' ' -f1
}

e195_built() {  # what step 6's wait recorded today (RB_OUT/e195-built.txt), or nothing
  if [ -f "$RB_OUT/e195-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e195-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then
    cat "$RB_OUT/e195-built.txt"
  fi
}

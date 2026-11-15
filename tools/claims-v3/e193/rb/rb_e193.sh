# E193 (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): the part every E193 runbook step sources (bash 3.2 or later; the
# desk is aifoundry2, Linux, or the Intel, macOS). E189's runbook file's form (tools/claims-v3/e189/rb/rb_e189.sh, b42dc95c): it sources
# the k6 runbook's common library, tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED (its v3.1 bounded runner rb_run.py, its 15 s
# hard-killed probe, its login-link stop, which appends "<HH:MM:SS> <box> needs a check" to RB_LOCK and exits 11 with nothing retried,
# its prelude, its holder rule, its detached jobs, its desk-path gate and its exit codes), then E183 note 5's desk-path gate
# (tools/claims-v3/e183/rb/nopath_desk_e183.sh, UNCHANGED: the gate for a desk whose home has the box account's shape, aifoundry2's), and
# changes only:
#   - rb_init names every step "<step>_e193";
#   - RB_E193_BASE, the commit an E193 tree must descend from: 49a4152e (GitHub main when E193 was registered, Sat 14 Nov 2026), E193's
#     registration commit found by its content (the commit that added tools/claims-v3/e193/E193.md, whose tools/claims-v3/e193 subtree
#     reads 03ae7f5a...), and the kit's commit by its content (the one that added tools/claims-v3/e193/KIT.md);
#   - E193's box (aifoundry3 card 0, tree ~/aifoundry, E193's root there build/claims-v3/aifoundry3/e193) and its two sittings: A
#     (blocks S, D, W, T; cap 60 card-minutes, 3,600 s) and B (block C; cap 50, 3,000 s) (E193.md 6);
#   - THE WINDOW RULE, PER SITTING (E189's, with the sitting): e193_window refuses (10) unless RB_OUT's window.env exists, was written TODAY
#     by the Pacific calendar, names today as its day, E193 as its runbook and a sitting, A or B; ONE RB_OUT PER SITTING (sitting B's
#     steps read sitting B's window; a step given a sitting refuses another's window); the sync, the build, the dry pass and the launch
#     read the last start, the launch its sitting's cap before the last end, the collection the copy class's 600 s before it;
#   - THE LAB-GIT LOCK (E189's way): e193_pull runs `git pull --ff-only` under RB_GITLOCK, `/usr/bin/lockf -k -t 600` where it exists,
#     else `/usr/bin/flock -w 600 -E 75` (both exit 75 on a timeout), so step 2 is NEVER run inside that lock (nested: 75, then 16).
# k6's ours_live counts any session_eNNN.sh of ours by the lab's naming rule, so E193's session (session_e193.sh) is counted unchanged.
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E193_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E193_BASE=${RB_E193_BASE:-49a4152e}
E193_REG_SUBTREE=03ae7f5acae03784d228738755f4dd9ff725e947
E193_BOX=aifoundry3
E183_BOX=aifoundry3                              # nopath_desk_e183.sh's name for the box whose tree it leaves out
E193_ROOT=build/claims-v3/aifoundry3/e193        # E193's root under the box's tree (~/aifoundry)
. "$RB_E193_DIR/../../e183/rb/nopath_desk_e183.sh"

rb_init() {  # rb_init <step>: k6's, with the step named "_e193"
  RB_STEP=${1}_e193
  [ -n "${RB_OUT:-}" ] || { echo "[$RB_STEP] RB_OUT is not set (this sitting's own directory, outside the repo)"; exit $RB_E_USAGE; }
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

e193_cap_s() {  # e193_cap_s <A|B>: the sitting's cap in seconds (E193.md 6)
  case "$1" in A) echo 3600 ;; B) echo 3000 ;; *) return 1 ;; esac
}

e193_window() {  # e193_window [<A|B>]: the window rule; sets E193_SIT from window.env; refuses a window of another sitting
  local want=${1:-}
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- gate: RB_OUT's window.env written today (Pacific) for E193 sitting ${want:-A or B} and naming today; its last start and last end read"
    rb_window; E193_SIT=${want:-${RB_SITTING:-A}}; return 0
  fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e193.sh with the sitting and his go's day, last start and last end first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e193.sh first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e193.sh for today"
  [ "${RB_PLAN:-}" = e193 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E193: one RB_OUT per sitting"
  case "${RB_SITTING:-}" in A|B) ;; *) rb_die $RB_E_USAGE "RB_OUT's window names no sitting: run s02_window_e193.sh <A|B> ..." ;; esac
  [ -z "$want" ] || [ "$want" = "$RB_SITTING" ] || rb_die $RB_E_USAGE "RB_OUT's window is sitting $RB_SITTING's, not sitting $want's: one RB_OUT per sitting"
  E193_SIT=$RB_SITTING
  return 0
}

e193_lockcmd() {  # e193_lockcmd <seconds> <lock file>: the lab-git lock's command words on this desk, exit 75 on a timeout either way
  if [ -x /usr/bin/lockf ]; then echo "/usr/bin/lockf -k -t $1 $2"
  elif [ -x /usr/bin/flock ]; then echo "/usr/bin/flock -w $1 -E 75 $2"
  else return 1; fi
}

e193_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): $(e193_lockcmd 600 '<RB_GITLOCK>' || echo '<no lockf or flock: refused>') git -C <lab clone> pull --ff-only"
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

e193_built_today() {  # true when step 6's wait recorded X04-BUILT in this RB_OUT today
  [ -f "$RB_OUT/e193-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e193-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] &&
    grep -q '^X04-BUILT' "$RB_OUT/e193-built.txt"
}

e193_harness_sha() {  # the committed harness-e193.json's sha256 in the lab clone (step 2 pins it by the kit's list)
  shasum -a 256 "$RB_REPO/tools/claims-v3/e193/harness-e193.json" 2>/dev/null | cut -d' ' -f1
}

# E198 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): the part every E198 runbook step sources. E193's runbook file
# (tools/claims-v3/e193/rb/rb_e193.sh, unchanged beside it) for aifoundry1 card 1, from aifoundry2: it sources the k6 runbook's common library
# (tools/claims-v3/q141k-runbook/k6/rb_common.sh, UNCHANGED: its bounded runner, its 15 s probe, its login-link stop, its prelude with the
# holder rule's reads, ours_live, which counts session_e198.sh by the lab's naming rule, its detached jobs, its rb_guard_text with THE REBOOT
# GATE for aifoundry1 (booted before E82's firmware read of 2026-10-31 13:45:24 PDT, else IDENTITY-STOP), its desk-path gate rb_nopath, its
# exit codes), and changes only. E193's E183-note-5 desk-path gate is NOT sourced: it refuses (16) on a desk whose home holds an entry named
# as the box's tree, and aifoundry2's home holds ~/nekko, aifoundry1's tree; the collection uses k6's rb_nopath after its scrub, as E191's
# collection on aifoundry1 does (s22_collect_e191_v2.sh).
#   - rb_init names every step "<step>_e198";
#   - RB_E198_BASE f74c81e3 (GitHub main when E198 was registered), the registration found by its content (the commit that added
#     tools/claims-v3/e198/E198.md, whose e198 subtree reads 5434394b...), the kit by its content (the commit that added .../e198/KIT.md);
#   - E198's box (aifoundry1 card 1, tree ~/nekko, E198's root build/claims-v3/aifoundry1/e198) and its two sittings: A (blocks S, D, W, T;
#     cap 3,600 s) and B (block C; cap 3,000 s);
#   - THE WINDOW RULE, PER SITTING, FROM G (E198.md 12): s02 writes RB_OUT's window.env from G, the card lane's booking of aifoundry1 for the
#     sitting (for sitting B under one booking, sitting A's session end + 40 minutes): last start G+1:30, last end G+3:30, each rounded up
#     to the whole minute, both inside G's Pacific day; e198_window refuses (10) unless window.env was written TODAY for E198 and the sitting;
#   - THE LAB-GIT LOCK (E193's way): e198_pull under RB_GITLOCK, never nested (75, then 16).
# Exit codes (k6's): 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder after 30 minutes;
# 16 a gate says stop; 17 call again.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../q141k-runbook/k6/rb_common.sh"
RB_E198_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RB_E198_BASE=${RB_E198_BASE:-f74c81e3}
E198_REG_SUBTREE=5434394b27bb98ae433b05df3e30f372461c518b
E198_BOX=aifoundry1
E198_ROOT=build/claims-v3/aifoundry1/e198        # E198's root under the box's tree (~/nekko)
E198_SEALED=tools/claims-v3/sealed-card1/e198-freeze-lines.md   # a later dated note (CONTEXT 122), outside the pinned subtree: accepted

rb_init() {  # rb_init <step>: k6's, with the step named "_e198"
  RB_STEP=${1}_e198
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

e198_cap_s() {  # e198_cap_s <A|B>: the sitting's cap in seconds (E198.md 10)
  case "$1" in A) echo 3600 ;; B) echo 3000 ;; *) return 1 ;; esac
}

e198_window() {  # e198_window [<A|B>]: the window rule; sets E198_SIT from window.env; refuses a window of another sitting
  local want=${1:-}
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- gate: RB_OUT's window.env written today (Pacific) for E198 sitting ${want:-A or B} from G and naming today; its last start and last end read"
    rb_window; E198_SIT=${want:-${RB_SITTING:-A}}; return 0
  fi
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e198.sh with the sitting, the day and G (the booking) first"
  [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
    rb_die $RB_E_USAGE "RB_OUT's window was not written today (Pacific): run s02_window_e198.sh first"
  rb_window
  [ "${RB_DAY:-}" = "$(TZ=America/Los_Angeles date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window is for ${RB_DAY:-no day}, not today: run s02_window_e198.sh for today"
  [ "${RB_PLAN:-}" = e198 ] || rb_die $RB_E_USAGE "RB_OUT's window was written for ${RB_PLAN:-another runbook}, not E198: one RB_OUT per sitting"
  case "${RB_SITTING:-}" in A|B) ;; *) rb_die $RB_E_USAGE "RB_OUT's window names no sitting: run s02_window_e198.sh <A|B> ..." ;; esac
  [ -z "$want" ] || [ "$want" = "$RB_SITTING" ] || rb_die $RB_E_USAGE "RB_OUT's window is sitting $RB_SITTING's, not sitting $want's: one RB_OUT per sitting"
  E198_SIT=$RB_SITTING
  return 0
}

e198_pull() {  # git pull --ff-only in the lab clone under the lab-git lock (RB_GITLOCK, required; never nested)
  if [ -n "${RB_DRY:-}" ]; then
    echo "--- copy, run on the desk (git pull --ff-only under the lab-git lock): /usr/bin/flock -w 600 -E 75 <RB_GITLOCK> git -C <lab clone> pull --ff-only"
    RB_RC=0; return 0
  fi
  [ -n "${RB_GITLOCK:-}" ] || rb_die $RB_E_USAGE "RB_GITLOCK is not set (the lab-git lock every commit to the shared lab clone takes; a path outside the repo)"
  case "$(cd "$(dirname "$RB_GITLOCK")" 2>/dev/null && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "RB_GITLOCK is inside the lab repo: refused" ;; esac
  local lt=600; [ "${RB_DESKTEST:-}" = 1 ] && lt=${RB_GITLOCK_T:-600}
  [ -x /usr/bin/flock ] || rb_die $RB_E_USAGE "no /usr/bin/flock here: the lab-git lock cannot be taken"
  rb_local copy github "git pull --ff-only (the public repo), under the lab-git lock" /usr/bin/flock -w "$lt" -E 75 "$RB_GITLOCK" git -C "$RB_REPO" pull --ff-only
}

e198_built_today() {  # true when step 6's wait recorded X04-BUILT in this RB_OUT today
  [ -f "$RB_OUT/e198-built.txt" ] && [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/e198-built.txt" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] &&
    grep -q '^X04-BUILT' "$RB_OUT/e198-built.txt"
}

e198_harness_sha() {  # the committed harness-e198.json's sha256 in the lab clone (step 2 pins it by the kit's list)
  sha256sum "$RB_REPO/tools/claims-v3/e198/harness-e198.json" 2>/dev/null | cut -d' ' -f1
}

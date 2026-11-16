#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum), the box step "the tree" (this file is
# s07, in the place of a sync): aifoundry2's box tree, ~/claude/et-soc1-prototyping, is a git checkout of the lab repository (k6's rb_tree
# for aifoundry2; E190 arm A's tree), so NOTHING IS COPIED into it (an untracked copy of a file a later merge brings would stop that merge):
# E190's step 5 v2 for arm A (tools/claims-v3/e190/rb/s07_sync_e190_v2.sh, unchanged beside it) with E194's commit and harness:
#   1. the window rule first (written today for E194; now before the last start); THE QUIET DESK FLAG raised;
#   2. the box read first: E194's ours_live (any session or queue of ours, by its own script) and jobs_live (a runbook job still running);
#      either above 0 is REFUSED on the box and 10 here, before anything is pulled;
#   3. the tree's HEAD must descend from E194's KIT COMMIT (found by its content in the lab clone: the commit that added
#      tools/claims-v3/e194/KIT.md), with E194's paths clean there; not yet: 17, call again; with the word `pull` the step first runs
#      `git pull -q --ff-only` there (bounded, 120 s, over HTTPS by an environment-only rewrite, as E190 arm A's step did on Fri 13 Nov
#      2026), only if those paths are clean; then every file of harness-e194.json at its sha256 there (check_e194.py --box: HARNESS OK).
#   RB_QUIET=<the flag file> bash tools/claims-v3/e194/rb/s07_tree_e194.sh [pull]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e194.sh"
rb_init s07_tree
pull=${1:-}
case "$pull" in ""|pull) ;; *) rb_die $RB_E_USAGE "the only word is pull" ;; esac
e194_window
rb_need_start
e194_quiet
kit=$(e194_kit_commit)
[ -n "${RB_DRY:-}" ] && kit=${kit:-KITCOMMIT}
[ -n "$kit" ] || rb_die $RB_E_USAGE "no kit commit in the lab clone (the commit that added tools/claims-v3/e194/KIT.md): run step 2 first"
rb_probe aifoundry2
f=$(rb_file notours)
{ rb_prelude aifoundry2
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E194's tree step never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E194's tree step never runs under one"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read aifoundry2 "no card session of ours and no runbook job on the box before the tree step" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the tree step exited $RB_RC: nothing pulled"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the tree step gave no answer: nothing pulled"
f=$(rb_file tree)
{ rb_prelude aifoundry2
  echo "KIT=$kit; PULL=$(printf '%q' "$pull")"
  cat <<'EOF3'
P="tools/claims-v3/e194 tools/claims-v3/e189 tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json workloads/ledger workloads/sparseparity/host workloads/sparseparity/kernel workloads/sparseparity/tools"
d=$(git status --porcelain --untracked-files=all -- $P | wc -l | tr -d ' ')
[ "$d" -eq 0 ] || { echo "REFUSED: $d path(s) of E194's modified or untracked in the box tree: nothing pulled, nothing run"; exit 3; }
if ! git merge-base --is-ancestor "$KIT" HEAD 2>/dev/null; then
  if [ "$PULL" = pull ]; then
    GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com: timeout 120 git pull -q --ff-only < /dev/null
    echo "PULL rc $?"
  fi
fi
if git merge-base --is-ancestor "$KIT" HEAD 2>/dev/null; then echo "TREE-HAS-KIT HEAD $(git rev-parse --short=12 HEAD)"
else echo "TREE-LACKS-KIT HEAD $(git rev-parse --short=12 HEAD) does not hold E194's kit commit ${KIT:0:12} yet"; exit 0; fi
python3 -B tools/claims-v3/e194/check_e194.py --box | tail -n 1
EOF3
} > "$f"
rb_remote read aifoundry2 "the box tree holds E194's kit commit, E194's paths clean, the harness at its sha256$([ "$pull" = pull ] && echo ' (after a pull --ff-only)')" "$f"
rb_refused
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the tree read exited $RB_RC"
rb_has '^TREE-LACKS-KIT' && { rb_say "$(grep -m1 '^TREE-LACKS-KIT' "$RB_CAP"): call again with the word pull"; exit $RB_E_AGAIN; }
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the box tree's files differ from harness-e194.json (the line above): no build, no session"
rb_say "aifoundry2's tree holds E194's kit commit; HARNESS OK there (nothing copied)"
exit 0

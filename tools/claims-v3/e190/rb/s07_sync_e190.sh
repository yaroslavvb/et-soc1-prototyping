#!/usr/bin/env bash
# E190 (Q169, the kit), the box step "the sync" (this file is s07), for one arm, after the look read FREE:
#   arm A (aifoundry2, ~/claude/et-soc1-prototyping, a git checkout that fast-forwards to GitHub main by itself): NOTHING IS COPIED into it
#     (an untracked copy of a file the next merge brings would stop that merge): the box read first (no session of ours, no runbook job),
#     then its HEAD must descend from the kit commit (found by content in the lab clone) with E190's paths clean there, and every file of
#     harness-e190.json at its sha256 there (check_e190.py --box: HARNESS OK); not merged yet: 17, call again; with the word `pull` the
#     step first runs `git pull --ff-only` there (bounded, over HTTPS by an environment-only rewrite), only if those paths are clean;
#   arm B (aifoundry1, ~/nekko, no git: E164's and E172's rsynced copy): E189's form: the box read first, the lab clone's copies of
#     harness-e190.json's files committed and at their sha256, ONE rsync -a -c -R -i into aifoundry1:nekko/ (its itemized lines name every
#     file whose content it sent), then check_e190.py --box on the box: HARNESS OK.
#   bash tools/claims-v3/e190/rb/s07_sync_e190.sh A [pull]  |  B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
rb_init s07_sync
e190_arm "${1:-}"
pull=${2:-}
e190_window
rb_need_start
kit=$(e190_kit_commit)
[ -n "${RB_DRY:-}" ] && kit=${kit:-KITCOMMIT}
[ -n "$kit" ] || rb_die $RB_E_USAGE "no kit commit in the lab clone (the commit that added tools/claims-v3/e190/KIT.md): run step 2 first"
rb_probe "$BOX"
f=$(rb_file notours)
{ rb_prelude "$BOX"
  cat <<'EOF3'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: E190's sync never runs beside one"; exit 3; fi
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: $(jobs_live) runbook job(s) still run on $BOX: E190's sync never runs under one"; exit 3; fi
echo "NOT-BESIDE-OURS: no card session of ours and no runbook job on $BOX"
EOF3
} > "$f"
rb_remote read "$BOX" "no card session of ours and no runbook job on the box before the sync" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read before the sync exited $RB_RC: nothing synced"
[ -n "${RB_DRY:-}" ] || rb_has '^NOT-BESIDE-OURS: ' || rb_die $RB_E_FAIL "the read before the sync gave no answer: nothing synced"
if [ "$ARM" = A ]; then
  f=$(rb_file tree)
  { rb_prelude "$BOX"
    echo "KIT=$kit; PULL=$(printf '%q' "$pull")"
    cat <<'EOF3'
P="tools/claims-v3/e190 tools/claims-v3/e136/rgm136 tools/claims-v3/kinds/tiles tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json"
d=$(git status --porcelain --untracked-files=all -- $P | wc -l | tr -d ' ')
[ "$d" -eq 0 ] || { echo "REFUSED: $d path(s) of E190's modified or untracked in the box tree: nothing pulled, nothing run"; exit 3; }
if ! git merge-base --is-ancestor "$KIT" HEAD 2>/dev/null; then
  if [ "$PULL" = pull ]; then
    GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com: timeout 120 git pull -q --ff-only < /dev/null
    echo "PULL rc $?"
  fi
fi
if git merge-base --is-ancestor "$KIT" HEAD 2>/dev/null; then echo "TREE-HAS-KIT HEAD $(git rev-parse --short=12 HEAD)"
else echo "TREE-LACKS-KIT HEAD $(git rev-parse --short=12 HEAD) does not hold the kit commit ${KIT:0:12} yet"; exit 0; fi
python3 -B tools/claims-v3/e190/check_e190.py --box | tail -n 1
EOF3
  } > "$f"
  rb_remote read "$BOX" "the box tree holds the kit commit, E190's paths clean, the harness at its sha256$([ "$pull" = pull ] && echo ' (after a pull --ff-only)')" "$f"
  rb_refused
  [ -n "${RB_DRY:-}" ] && exit 0
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the tree read exited $RB_RC"
  rb_has '^TREE-LACKS-KIT' && { rb_say "$(grep -m1 '^TREE-LACKS-KIT' "$RB_CAP"): call again (or with the word pull)"; exit $RB_E_AGAIN; }
  rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the box tree's files differ from harness-e190.json (the line above): no build, no session"
  rb_say "aifoundry2's tree holds the kit commit; HARNESS OK there (nothing copied)"
  exit 0
fi
P=()
while IFS= read -r p; do [ -n "$p" ] && P+=("$p"); done <<EOF2
$(/usr/bin/python3 -I -B tools/claims-v3/e190/check_e190.py --list)
EOF2
[ "${#P[@]}" -gt 10 ] || rb_die $RB_E_USAGE "the sync list could not be read from check_e190.py --list"
P+=(tools/claims-v3/e190/harness-e190.json)
rb_local read local "the synced paths clean before the sync" git -C "$RB_REPO" status --short "${P[@]}"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted changes: sync only the pushed commit"
rb_local read local "the lab clone's copies of harness-e190.json's files at their sha256" /usr/bin/python3 -I -B tools/claims-v3/e190/check_e190.py --box
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "a file the sync would send differs from harness-e190.json: nothing is synced"
rb_probe "$BOX"
rb_local copy "$BOX" "aifoundry1's rsync: harness-e190.json's files (itemized)" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" "${P[@]}" "$BOX:$(rb_tree "$BOX")/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync exited non-zero"
rs=$RB_CAP
f=$(rb_file harness)
{ rb_prelude "$BOX"; echo 'python3 -B tools/claims-v3/e190/check_e190.py --box | tail -n 1'; } > "$f"
rb_remote read "$BOX" "the harness at its sha256 on the box" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^HARNESS OK: ' || rb_die $RB_E_GATE "the box's copies differ from harness-e190.json after the sync (the line above)"
rb_say "synced to $BOX:$(rb_tree "$BOX")/ (${#P[@]} paths); the rsync sent $(grep -cE '^[<>]f' "$rs") files' contents there; HARNESS OK on the box"
exit 0

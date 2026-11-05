#!/usr/bin/env bash
# Q142(v2) fix pass, Thu 5 Nov 2026: the desk test of step 3b (s03b_lists_k6.sh) and its checker (lists22_k6.py). It reads the lab clone and
# writes only under <scratch dir> (never in the repo): a shadow tree there (symlinks into the clone, with one file of a case a changed copy) stands
# in for a work tree whose file differs. No box, no ssh, no device. The cases:
#   T1  at <rev> (default HEAD, after this pass's commit): every list passes, 22 of 22 and 2 of 2, exit 0
#   T2  at 1a76a870 (the readiness critic's revision): the 22 pass and this pass's two are not there: exit 4
#   T3  at 37f11663 (before Q142(x)): the round's ten lists are not there (12 of 22 pass): exit 4
#   T4  a work-tree file of this pass's scorer list differs (score_p8_600_v3.py, one byte added): 22 of 22, 1 of 2, exit 4, the file named
#   T5  a work-tree file of the 22 differs (pool 8's aifoundry3 predictions, one byte added): exit 4, the lists that pin it named
#   T6  a list's own work-tree copy differs (p8-600's SHA256SUMS-v2, a line added): exit 4
#   T7  a revision that is not a commit: exit 2
#   S1  s03b_lists_k6.sh on the clone: exit 0, its LISTS22 and LISTS-V3 lines
#   S2  s03b with T4's shadow tree (K6_LISTS_WT, RB_DESKTEST=1): exit 16, "a hash list does not match"
#   S3  s03b with K6_LISTS_WT set but no RB_DESKTEST: exit 10, the checker never run
#   S4  s03b with RB_DRY=1: exit 0, the checker listed, never run
#
#   bash tools/claims-v3/q141k-runbook/k6/selftest_lists22_k6.sh <a new, empty scratch dir outside the repo> [<rev>] > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?usage: selftest_lists22_k6.sh <a new, empty scratch dir outside the repo> [<rev>]}
REV=${2:-HEAD}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
[ -d "$S" ] && [ -n "$(ls -A "$S" 2>/dev/null)" ] && { echo "refused: $S is not empty"; exit 2; }
mkdir -p "$S" || exit 2
K6=tools/claims-v3/q141k-runbook/k6
L=$SRC/$K6/lists22_k6.py
PY=/usr/bin/python3
N=0; F=0
ok() { N=$((N + 1)); if [ "$1" = 1 ]; then echo "PASS $2"; else F=$((F + 1)); echo "FAIL $2"; fi; }
show() { grep -E '^(FAIL|LISTS|ALL|A LIST|usage)' "$1" | sed "s#$S#<scratch>#g" | cut -c1-230; }
shadow() {  # shadow <name> <repo-relative file> <append-line>: a tree of symlinks into the clone in which only that file is a changed copy
  local top=$S/$1 rel=$2 add=$3 cur=$SRC dst part e
  mkdir -p "$top"; dst=$top
  local IFS=/; set -- $rel; unset IFS
  local n=$#
  while [ "$#" -gt 0 ]; do
    part=$1; shift
    for e in "$cur"/* "$cur"/.[!.]*; do
      [ -e "$e" ] || [ -L "$e" ] || continue
      [ "$(basename "$e")" = "$part" ] && continue
      ln -s "$e" "$dst/$(basename "$e")"
    done
    if [ "$#" -gt 0 ]; then mkdir -p "$dst/$part"; dst=$dst/$part; cur=$cur/$part
    else cp -p "$cur/$part" "$dst/$part"; printf '%s\n' "$add" >> "$dst/$part"; fi
  done
  [ "$n" -gt 0 ]
}
echo "== at $(git -C "$SRC" rev-parse --short "$REV" 2>/dev/null) ($REV); the clone's HEAD $(git -C "$SRC" rev-parse --short HEAD)"

$PY -B "$L" --repo "$SRC" --rev "$REV" > "$S/t1.txt" 2>&1; r=$?; show "$S/t1.txt"
ok "$([ "$r" = 0 ] && grep -q '^LISTS22: 22 of 22 PASS$' "$S/t1.txt" && grep -q '^LISTS-V3: 2 of 2 PASS$' "$S/t1.txt" && grep -q '^ALL LISTS PASS$' "$S/t1.txt" && echo 1 || echo 0)" \
   "T1 at $REV: 22 of 22 and 2 of 2, exit $r"
$PY -B "$L" --repo "$SRC" --rev 1a76a870 > "$S/t2.txt" 2>&1; r=$?; show "$S/t2.txt"
ok "$([ "$r" = 4 ] && grep -q '^LISTS22: 22 of 22 PASS$' "$S/t2.txt" && grep -q '^LISTS-V3: 0 of 2 PASS$' "$S/t2.txt" && [ "$(grep -c 'the list is not in the revision' "$S/t2.txt")" = 2 ] && echo 1 || echo 0)" \
   "T2 at 1a76a870: the 22 pass, this pass's two are not there, exit $r"
$PY -B "$L" --repo "$SRC" --rev 37f11663 > "$S/t3.txt" 2>&1; r=$?; show "$S/t3.txt" | tail -n 4
ok "$([ "$r" = 4 ] && grep -q '^LISTS22: 12 of 22 PASS$' "$S/t3.txt" && echo 1 || echo 0)" "T3 at 37f11663: 12 of 22 (the round's ten not there), exit $r"
shadow t4 tools/claims-v3/p8-600/score_p8_600_v3.py "# one line more"
$PY -B "$L" --repo "$SRC" --rev "$REV" --worktree "$S/t4" > "$S/t4.txt" 2>&1; r=$?; show "$S/t4.txt"
ok "$([ "$r" = 4 ] && grep -q '^LISTS22: 22 of 22 PASS$' "$S/t4.txt" && grep -q '^LISTS-V3: 1 of 2 PASS$' "$S/t4.txt" && grep -q '^FAIL p8-600/SHA256SUMS-v3: .*work-tree file(s) differ: tools/claims-v3/p8-600/score_p8_600_v3.py' "$S/t4.txt" && echo 1 || echo 0)" \
   "T4 score_p8_600_v3.py changed in the work tree: exit $r, the file named"
shadow t5 tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry3.json " "
$PY -B "$L" --repo "$SRC" --rev "$REV" --worktree "$S/t5" > "$S/t5.txt" 2>&1; r=$?; show "$S/t5.txt"
nf=$(grep -c '^FAIL .*predictions-pool8-aifoundry3.json' "$S/t5.txt")
ok "$([ "$r" = 4 ] && [ "$nf" -ge 1 ] && echo 1 || echo 0)" "T5 pool 8's aifoundry3 predictions changed in the work tree: exit $r, $nf list(s) that pin it FAIL"
shadow t6 tools/claims-v3/p8-600/SHA256SUMS-v2 "# a line added"
$PY -B "$L" --repo "$SRC" --rev "$REV" --worktree "$S/t6" > "$S/t6.txt" 2>&1; r=$?; show "$S/t6.txt"
ok "$([ "$r" = 4 ] && grep -q "^FAIL p8-600/SHA256SUMS-v2: .*the list's work-tree copy is not its committed blob" "$S/t6.txt" && echo 1 || echo 0)" \
   "T6 a list's own work-tree copy changed (SHA256SUMS-v2): exit $r"
$PY -B "$L" --repo "$SRC" --rev not-a-commit-0000 > "$S/t7.txt" 2>&1; r=$?
ok "$([ "$r" = 2 ] && echo 1 || echo 0)" "T7 a revision that is not a commit: exit $r"

export RB_OUT="$S/out" RB_LOCK="$S/lock.txt" RB_REPO="$SRC"
mkdir -p "$S/out"; : > "$RB_LOCK"
bash "$SRC/$K6/s03b_lists_k6.sh" > "$S/s1.txt" 2>&1; r=$?; grep -E 'lists:|STOP' "$S/s1.txt" | sed "s#$S#<scratch>#g" | cut -c1-260
ok "$([ "$r" = 0 ] && grep -q 'lists: LISTS22: 22 of 22 PASS; LISTS-V3: 2 of 2 PASS; lists22_k6.py sha256 ' "$S/s1.txt" && echo 1 || echo 0)" "S1 s03b on the clone: exit $r"
RB_DESKTEST=1 K6_LISTS_WT="$S/t4" bash "$SRC/$K6/s03b_lists_k6.sh" > "$S/s2.txt" 2>&1; r=$?; grep -E 'STOP' "$S/s2.txt" | cut -c1-200
ok "$([ "$r" = 16 ] && grep -q 'a hash list does not match' "$S/s2.txt" && echo 1 || echo 0)" "S2 s03b with T4's changed work tree: exit $r"
rm -f "$S/out/lists22.json"
K6_LISTS_WT="$S/t4" bash "$SRC/$K6/s03b_lists_k6.sh" > "$S/s3.txt" 2>&1; r=$?; grep -E 'STOP' "$S/s3.txt" | cut -c1-200
ok "$([ "$r" = 10 ] && [ ! -e "$S/out/lists22.json" ] && echo 1 || echo 0)" "S3 the stand-in set without RB_DESKTEST: exit $r, the checker never run"
RB_DRY=1 bash "$SRC/$K6/s03b_lists_k6.sh" > "$S/s4.txt" 2>&1; r=$?; grep -E 'lists22_k6.py' "$S/s4.txt" | head -n 1 | cut -c1-220
ok "$([ "$r" = 0 ] && grep -q 'lists22_k6.py' "$S/s4.txt" && [ ! -e "$S/out/lists22.json" ] && echo 1 || echo 0)" "S4 the dry listing: exit $r, the checker listed and never run"
echo "selftest_lists22_k6: $((N - F)) of $N checks pass"
[ "$F" -eq 0 ]

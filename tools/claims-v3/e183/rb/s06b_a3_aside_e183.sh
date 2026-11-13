#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): KIT.md box step 5b, NEW, "the aside":
# before a second E183 session the same day (E183.md's dated amendment A1), move the FIRST session's smoke and stop-path test directories on
# aifoundry3, build/claims-v3/aifoundry3/e183-smoke/p18301 and build/claims-v3/aifoundry3/e183-stoptest/p18302 and nothing else, to a dated
# aside name outside both, build/claims-v3/aifoundry3/e183-aside-<day>-t<T0>/{e183-smoke/p18301,e183-stoptest/p18302} (<T0> the first
# session's), ONLY after the desk's read-only copy of them is shown exact. Why: block v2 and v3 keep an earlier smoke inside e183-smoke/ (as
# p18301.attempt-<epoch>) and write a new stop-path test into the earlier p18302 in place (V3_FORCE), and step 11 copies e183-smoke/ and
# e183-stoptest/ whole; with the two moved aside, the second session's collection holds its own smoke and stop test alone, and the first
# session's (set aside by amendment A1, read by no rule) stay on the box under the aside name, byte for byte, beside the desk's copy.
#   1. at the desk, before any call: the copy (<copy>, laid out at the box's paths) against the box's own manifest of it (<manifest>,
#      "SUM <sha256> <box path>" lines, written when the copy was made): every file the manifest lists under the two directories is in the
#      copy at its sha256, and the copy holds no other file there; both directories are listed; the manifest names exactly one session log,
#      build/e183/session-t<T0>.log, whose T0 and Pacific day name the aside. Else 16 (or 10 for a missing argument), and nothing is called;
#   2. ONE bounded call on the box (k6's probe first): refused (REFUSED, 10) while a runbook job or a card session of ours runs (k6's
#      jobs_live and ours_live); the two directories must be plain directories of ours holding only regular files and directories, and their
#      files, by sha256, exactly the copy's list (else ASIDE-DIFFERS, 16, nothing moved); the aside name must not exist (ASIDE-EXISTS, 16);
#      then mkdir of the aside's two parents and two renames (mv -T, one file system), and the list read again under the aside name: the
#      same files at the same sha256, and neither old path left (ASIDE-DONE). Run again after it has moved them: ASIDE-ALREADY (0), nothing
#      moved. Nothing is removed, written into or copied on the box; the card is not touched;
#   3. at the desk: RB_OUT/aside-e183.txt (the expected list and the box's reading). Exit codes are k6's: 0 done; 10 refused or usage;
#      11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 16 a gate says stop.
#   bash tools/claims-v3/e183/rb/s06b_a3_aside_e183.sh <the first session's read-only copy> [<its box manifest, default <copy>.box-manifest.txt>]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s06b_a3_aside
COPY=${1:-}
MAN=${2:-${COPY:+$COPY.box-manifest.txt}}
D1=build/claims-v3/aifoundry3/e183-smoke/p18301
D2=build/claims-v3/aifoundry3/e183-stoptest/p18302
EXP=""; T0=""; DAY=""
if [ -n "$COPY" ] && [ -d "$COPY" ] && [ -f "$MAN" ]; then
  EXP=$(awk -v a="$D1/" -v b="$D2/" '$1 == "SUM" && NF == 3 && (index($3, a) == 1 || index($3, b) == 1) {print $2 " " $3}' "$MAN" | LC_ALL=C sort)
  T0=$(sed -nE 's#^SUM [0-9a-f]{64} build/e183/session-t([0-9]+)\.log$#\1#p' "$MAN")
elif [ -z "${RB_DRY:-}" ]; then
  rb_die $RB_E_USAGE "usage: s06b_a3_aside_e183.sh <the first session's read-only copy> [<its box manifest>]: the copy or its manifest is not there"
fi
if [ -z "${RB_DRY:-}" ]; then
  [ "$(printf '%s\n' "$T0" | grep -c .)" -eq 1 ] || rb_die $RB_E_GATE "the manifest names $(printf '%s\n' "$T0" | grep -c .) session logs, not one: the first session's T0 cannot be read: nothing called"
  n1=$(printf '%s\n' "$EXP" | grep -c " $D1/"); n2=$(printf '%s\n' "$EXP" | grep -c " $D2/")
  { [ "$n1" -gt 0 ] && [ "$n2" -gt 0 ]; } || rb_die $RB_E_GATE "the manifest lists $n1 files under $D1 and $n2 under $D2: both are needed: nothing called"
  bad=""
  while read -r sum rel; do
    [ -f "$COPY/$rel" ] && [ ! -L "$COPY/$rel" ] || { bad="$bad; missing in the copy: $rel"; continue; }
    [ "$(sha256sum "$COPY/$rel" | cut -d' ' -f1)" = "$sum" ] || bad="$bad; differs from the manifest: $rel"
  done <<EOF2
$EXP
EOF2
  for d in "$D1" "$D2"; do
    [ -d "$COPY/$d" ] || { bad="$bad; no $d in the copy"; continue; }
    extra=$(cd "$COPY" && find "$d" -mindepth 1 ! -type d | LC_ALL=C sort | while IFS= read -r f; do
      printf '%s\n' "$EXP" | awk -v f="$f" '$2 == f {k = 1} END {exit !k}' || echo "$f"; done)
    [ -z "$extra" ] || bad="$bad; in the copy but not the manifest: $(printf '%s ' $extra)"
  done
  [ -z "$bad" ] || rb_die $RB_E_GATE "the desk's copy is not exact against its box manifest${bad}: nothing called, nothing moved"
  DAY=$(TZ=America/Los_Angeles date -d "@$T0" +%F)
  rb_say "the desk's copy is exact: $n1 files of $D1 and $n2 of $D2 at the box manifest's sha256 (the first session, T0 $T0, $DAY)"
fi
A=build/claims-v3/aifoundry3/e183-aside-${DAY:-<day>}-t${T0:-<T0>}
f=$(rb_file aside)
{ rb_prelude aifoundry3
  echo "D1=$D1; D2=$D2; A=$A"
  echo "EXP=\$(cat <<'RB_EXP_EOF'"
  if [ -n "$EXP" ]; then printf '%s\n' "$EXP"; else echo "<the copy's SUM lines under the two directories, sorted>"; fi
  echo "RB_EXP_EOF"
  echo ")"
  cat <<'EOF2'
mkdir -p build/q141k
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: a runbook job still runs on $BOX: nothing moved"; exit 3; fi
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours runs on $BOX: nothing moved"; exit 3; fi
lst() {  # lst <dir> <as>: "<sha256> <as>/<path>" for each regular file under <dir>; any entry but a file or a directory, or not ours, is named
  ( cd "$1" || exit 1
    find . -mindepth 1 ! -type f ! -type d | sed 's#^\./#OTHER #'
    find . -mindepth 1 ! -user "$(id -u)" | sed 's#^\./#NOT-OURS #'
    find . -type f | LC_ALL=C sort | while IFS= read -r p; do echo "$(sha256sum "$p" | cut -d' ' -f1) $2/${p#./}"; done ) | LC_ALL=C sort
}
both() { { lst "$1" "$D1"; lst "$2" "$D2"; } | LC_ALL=C sort; }
n=$(printf '%s\n' "$EXP" | grep -c .)
if [ ! -e "$D1" ] && [ ! -e "$D2" ] && [ -d "$A/e183-smoke/p18301" ] && [ -d "$A/e183-stoptest/p18302" ]; then
  if [ "$(both "$A/e183-smoke/p18301" "$A/e183-stoptest/p18302")" = "$EXP" ]; then
    echo "ASIDE-ALREADY: the two directories are already at $A, their $n files at the copy's sha256: nothing moved"; exit 0
  fi
  echo "ASIDE-DIFFERS: $A holds other files than the copy lists: nothing moved"; exit 3
fi
for d in "$D1" "$D2"; do
  { [ -d "$d" ] && [ ! -L "$d" ] && [ -O "$d" ]; } || { echo "ASIDE-MISSING: $d is not a directory of ours here: nothing moved"; exit 3; }
done
[ -e "$A" ] && { echo "ASIDE-EXISTS: $A already exists beside the two directories: nothing moved"; exit 3; }
got=$(both "$D1" "$D2")
if [ "$got" != "$EXP" ]; then
  echo "ASIDE-DIFFERS: the box's files are not the copy's: nothing moved"
  diff <(printf '%s\n' "$EXP") <(printf '%s\n' "$got") | grep -E '^[<>]' | head -n 12 | sed 's/^</  the copy:/; s/^>/  the box: /'
  exit 3
fi
mkdir -p "$A/e183-smoke" "$A/e183-stoptest" || { echo "ASIDE-FAILED: mkdir $A: nothing moved"; exit 3; }
mv -T -- "$D1" "$A/e183-smoke/p18301" || { echo "ASIDE-FAILED: mv $D1: nothing moved"; exit 3; }
mv -T -- "$D2" "$A/e183-stoptest/p18302" || { echo "ASIDE-FAILED: mv $D2 (after $D1 moved to $A/e183-smoke/p18301)"; exit 3; }
after=$(both "$A/e183-smoke/p18301" "$A/e183-stoptest/p18302")
{ [ ! -e "$D1" ] && [ ! -e "$D2" ] && [ "$after" = "$EXP" ]; } || { echo "ASIDE-FAILED: the list under $A is not the copy's after the move"; exit 3; }
echo "ASIDE-DONE: $n files of the first session's smoke and stop-path test moved to $A, each at the copy's sha256; nothing removed"
EOF2
} > "$f"
rb_probe aifoundry3
rb_remote read aifoundry3 "move the first session's smoke and stop-path test aside, after the copy's list matches the box's" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
{ echo "$(date '+%F %T %Z') step 5b, the aside: $A"; echo "expected (the desk copy's box manifest):"; printf '%s\n' "$EXP"
  echo "the box's reading:"; grep -E '^(ASIDE|REFUSED|  the)' "$RB_CAP"; } > "$RB_OUT/aside-e183.txt"
rb_refused
rb_has '^ASIDE-(DONE|ALREADY): ' && { rb_say "$(grep -m1 -E '^ASIDE-(DONE|ALREADY): ' "$RB_CAP")"; echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 -E '^ASIDE-(DONE|ALREADY): ' "$RB_CAP")" >> "$RB_LOG"; exit 0; }
rb_has '^ASIDE-' && rb_die $RB_E_GATE "$(grep -m1 '^ASIDE-' "$RB_CAP")"
rb_die $RB_E_FAIL "the aside call exited $RB_RC with no reading: read the output above (nothing is known to have moved: run this step again)"

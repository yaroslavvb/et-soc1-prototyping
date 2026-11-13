#!/usr/bin/env bash
# E183 (the kit's dated note 5, KIT.md.dated-note-5.md, Fri 13 Nov 2026, before any E183 datum; revised before its land by the lane
# fix-note5 of Q170, after the verifier verify-note5): the desk test of note 5's desk-path gate (rb/nopath_desk_e183.sh, with
# rb/nopath_spell_e183.py) and of step 11 v3 (rb/s22_collect_e183_v3.sh). Desk only: it reads committed data and writes stand-in files in
# <scratch dir> and in two temporary directories under /tmp (removed after); it reaches no box and no network, and opens no device. Run it
# on the desk the card lane orchestrates from, with a scratch directory under the desk's home (as its log was made): G20 and G21 need their
# stand-in homes under /home/, and are reported, not asserted, elsewhere.
#   G1  k6's rb_nopath (step 11 v2's gate) on committed aifoundry3 data holding the box's own paths (E180's vector add, E183's parent; E185's
#       session 3; E186's run 3): on a desk whose home is under /home/ it stops (16, "this user's home"): the failure note 5 answers;
#   G2  nopath_desk on the same data: 0 (nopath and the spelling check both clean);
#   G3  a stand-in output holding only aifoundry3's own tree path (<home>/aifoundry/build/...): nopath_desk 0 (rb_nopath 16 on such a desk);
#   G4  a path under a real entry of the desk's home (the first directory that is neither a link nor a name that begins the box's tree):
#       16, and the hit names that entry's needle (the forbidden path <home>/<entry>);
#   G5  the lab clone's path: 16;  G6 RB_OUT's path: 16;  G7 a Mac home path: 16 (nopath's own needle, kept);
#   G8  the session scratch root /tmp/claude-<uid> (when it exists; else reported): 16;
#   G9  an output that is not there: 16 (MISSING);
#   G10 a desk whose account home is not under /home/ (the account's home redefined, in the test's subshell, to a directory under /tmp, and
#       HOME the same): nopath_desk is k6's rb_nopath (no note 5 line), and the box path stand-in of G3 reads 0;
#   G11 step 11 v3 is step 11 v2 with exactly note 5's lines changed (the header, one source line, rb_init's name, the early check, the gate,
#       the closing line), and the early check comes before the step's first copy;
#   G12 step 11 v3's dry listing (RB_DRY=1, a window in a scratch RB_OUT): 0, and it names note 5's early check and gate;
#   G13-G16 the desk's home followed by '..', '.' or '/', and the box's tree followed by '..' (<home>/../<login>/<entry>/x, <home>/./<entry>/x,
#       <home>//<entry>/x, <home>/aifoundry/../<entry>/x): 16 each, by the spelling check (verify-note5's finding 1);
#   G17 a deeper climb out of the tree (<home>/aifoundry/build/../../<entry>/x): 16;  G18 a climb that stays in the tree
#       (<home>/aifoundry/external/build/../include): 0;
#   G19 the home's own directory spelled otherwise (/home//<login>/<entry>/x, /home/./<login>/<entry>/x): 16 each;
#   G20 a stand-in home (the account's home redefined to it) with a link and names that begin the tree (a, aif): a path under each 16 (by
#       the spelling check: verify-note5's nit 2), the tree's own form 0;
#   G21 a stand-in home with an entry named as the box's tree: nopath_desk_ready and nopath_desk refuse (16);
#   G22 HOME set but empty, relative, missing, or a subdirectory of the home: nopath_desk_ready refuses (10) each; HOME unset: 0; HOME a link to
#       the home: 0, and a desk path written through that link: 16 (verify-note5's nit 3).
#   bash tools/claims-v3/e183/rb/selftest_nopath_e183.sh <scratch dir>      # prints SELFTEST-NOPATH-E183 PASS|FAIL (<k> of <n>)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
mkdir -p "$S"; S=$(cd "$S" && pwd -P)
R=$SRC/tools/claims-v3/e183/rb
HP=$(cd ~ && pwd -P)
LG=$(basename "$HP")
TMPL=$(mktemp -d /tmp/e183-nopath-link.XXXXXX)
D180=$SRC/docs/reports/data/2026-11-06-e180-vector-add-aifoundry3
D185=$SRC/docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3
D186=$SRC/docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3
main() {
rm -rf "${S:?}/out" "${S:?}/data" "${S:?}/home2" "${S:?}/fh" "${S:?}/fh2"
mkdir -p "$S/out" "$S/data" "$S/home2"
: > "$S/lock.txt"
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
# gate <rb_nopath|nopath_desk|nopath_desk_ready> <keep|unset|set> <HOME value> <the account's home, redefined, or ""> <path> ...: the
# function in a subshell, as step 11 runs it; its output in $S/g.txt, its exit status returned
gate() {
  local fn=$1 hm=$2 hv=$3 ah=$4; shift 4
  ( case "$hm" in unset) unset HOME ;; set) export HOME="$hv" ;; esac
    export RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
    . "$R/rb_e183.sh"; . "$R/nopath_desk_e183.sh"
    [ -n "$ah" ] && eval "nopath_desk_account_home() { printf '%s\n' '$ah'; }"
    rb_init selftest_nopath > /dev/null
    "$fn" "$@"
    rb_say "gate passed" ) > "$S/g.txt" 2>&1
}
hits() { grep -c '^HIT' "$S/g.txt"; }
kinds() { grep '^HIT' "$S/g.txt" | sed -E 's/^HIT [^:]*: //; s/ \([0-9]+ times?\)$//' | LC_ALL=C sort | uniq -c | tr -s ' ' | tr '\n' ';'; }
shape=other; case "$HP" in /home/?*) shape=home ;; esac
ENT=""
while IFS= read -r e; do
  [ -n "$e" ] || continue
  case aifoundry in "$e"*) continue ;; esac
  [ -L "$HP/$e" ] && continue
  [ -d "$HP/$e" ] && { ENT=$e; break; }
done <<EOF_ENT
$(ls -A "$HP")
EOF_ENT
echo "the desk's home: $([ "$shape" = home ] && echo 'under /home/ (the box account'"'"'s shape)' || echo 'not under /home/ (the Intel'"'"'s shape)'); box tree aifoundry; $(ls -A "$HP" | grep -c .) entries, $(find "$HP" -maxdepth 1 -type l | grep -c .) links; the entry the cases below write under: $HP/$ENT"
[ -n "$ENT" ] || { echo "no directory entry in the desk's home to write under"; return 1; }
echo
echo "== G1/G2: committed aifoundry3 data with the box's own paths"
for d in "$D180" "$D185" "$D186"; do
  b=$(basename "$d")
  [ -d "$d" ] || { ok 1 "$b present in the lab"; continue; }
  echo "-- $b: $(find "$d" -type f | wc -l | tr -d ' ') files, $(find "$d" -type f -print0 | xargs -0 zgrep -l -s -F "$HP/aifoundry/" | wc -l | tr -d ' ') naming <home>/aifoundry/"
  gate rb_nopath keep "" "" "$d"; r=$?
  echo "rb_nopath (step 11 v2's gate): rc $r; HIT lines $(hits): $(kinds)"
  if [ "$shape" = home ]; then [ "$r" -ne 0 ] && grep -q "this user's home" "$S/g.txt"; ok $? "G1 v2's gate stops on $b here (this user's home)"
  else echo "(reported: on this desk v2's gate reads rc $r)"; fi
  gate nopath_desk keep "" "" "$d"; r=$?
  echo "nopath_desk (step 11 v3's gate): rc $r; HIT lines $(hits); $(grep -m1 '^nopath_spell:' "$S/g.txt" | sed 's/:.*; \([0-9]* hit(s)\)/: \1/')"
  [ "$r" -eq 0 ] && [ "$(hits)" -eq 0 ] && grep -q '^nopath_spell: .* 0 hit(s): CLEAN' "$S/g.txt"; ok $? "G2 v3's gate passes $b (nopath and the spelling check)"
done
echo
echo "== G3-G9: stand-in outputs"
w() { mkdir -p "$S/data/$1"; printf '%s\n' "line before" "$2" "line after" > "$S/data/$1/f.txt"; }
w box "cwd $HP/aifoundry/build/e183/stand-in, as the box writes it"
gate nopath_desk keep "" "" "$S/data/box"; r=$?; echo "nopath_desk: rc $r; HIT lines $(hits)"
[ "$r" -eq 0 ]; ok $? "G3 aifoundry3's own tree path passes v3's gate"
gate rb_nopath keep "" "" "$S/data/box"; r=$?; echo "(rb_nopath on the same: rc $r)"
w desk "a path under a real entry of the desk's home: $HP/$ENT/x"
gate nopath_desk keep "" "" "$S/data/desk"; r=$?; echo "nopath_desk: rc $r; $(kinds)"
[ "$r" -eq 16 ] && grep -q "^HIT .*: the forbidden path $HP/$ENT (" "$S/g.txt"; ok $? "G4 a path under a real desk home entry stops v3's gate, on that entry's needle"
w repo "the lab clone: $SRC/build/e183-raw"
gate nopath_desk keep "" "" "$S/data/repo"; r=$?; echo "nopath_desk: rc $r; $(kinds)"
[ "$r" -ne 0 ] && grep -q "the forbidden path $SRC" "$S/g.txt"; ok $? "G5 the lab clone's path stops v3's gate"
w rbout "RB_OUT: $S/out/calls/x"
gate nopath_desk keep "" "" "$S/data/rbout"; r=$?; echo "nopath_desk: rc $r; $(kinds)"
[ "$r" -ne 0 ] && grep -q "the forbidden path $S/out" "$S/g.txt"; ok $? "G6 RB_OUT's path stops v3's gate"
w mac "a Mac home: /Us""ers/someone/x"
gate nopath_desk keep "" "" "$S/data/mac"; r=$?; echo "nopath_desk: rc $r; $(kinds)"
[ "$r" -ne 0 ] && grep -q 'a Mac home path' "$S/g.txt"; ok $? "G7 a Mac home path stops v3's gate"
if [ -d "/tmp/claude-$(id -u)" ]; then
  w scr "a session scratch: /tmp/claude-$(id -u)/x/y"
  gate nopath_desk keep "" "" "$S/data/scr"; r=$?; echo "nopath_desk: rc $r; HIT lines $(hits)"
  [ "$r" -ne 0 ] && grep -q "the forbidden path /tmp/claude-$(id -u)" "$S/g.txt"; ok $? "G8 the session scratch root stops v3's gate"
else echo "(G8 reported: no /tmp/claude-<uid> on this desk)"; fi
gate nopath_desk keep "" "" "$S/data/not-there"; r=$?; echo "nopath_desk: rc $r; $(grep -c '^MISSING' "$S/g.txt") MISSING"
[ "$r" -ne 0 ] && grep -q '^MISSING' "$S/g.txt"; ok $? "G9 an output that is not there stops v3's gate"
echo
echo "== G10: a desk whose account home is not under /home/"
H2=$(mktemp -d /tmp/e183-nopath-home.XXXXXX)
gate nopath_desk set "$H2" "$H2" "$S/data/box"; r=$?
rm -rf "${H2:?}"
echo "nopath_desk with the account's home and HOME outside /home/: rc $r; the note 5 line $(grep -c 'note 5' "$S/g.txt") times"
[ "$r" -eq 0 ] && ! grep -q 'note 5' "$S/g.txt"; ok $? "G10 elsewhere nopath_desk is k6's rb_nopath (no note 5 line), and the box path passes"
echo
echo "== G11: step 11 v3 against v2"
diff "$R/s22_collect_e183_v2.sh" "$R/s22_collect_e183_v3.sh" > "$S/v2v3.diff"
sed -n 's/^\([<>]\) .*/\1/p' "$S/v2v3.diff" | LC_ALL=C sort | uniq -c | tr -s ' ' | tr '\n' ';'; echo
gone=$(grep '^< ' "$S/v2v3.diff" | sed 's/^< //')
new=$(grep '^> ' "$S/v2v3.diff" | sed 's/^> //' | grep -v '^#')
want_gone=$(printf '%s\n' 'rb_init s22_collect_v2' 'rb_nopath "$OUT"' "$(grep '^rb_say "E183 collected and scored' "$R/s22_collect_e183_v2.sh")")
first_copy=$(grep -n '^rb_local copy ' "$R/s22_collect_e183_v3.sh" | head -n 1 | cut -d: -f1)
ready_at=$(grep -n '^nopath_desk_ready ' "$R/s22_collect_e183_v3.sh" | head -n 1 | cut -d: -f1)
raw_at=$(grep -n '^RAW=build/e183-raw' "$R/s22_collect_e183_v3.sh" | head -n 1 | cut -d: -f1)
echo "the early check at line ${ready_at:-none}; RAW made at line ${raw_at:-none}; the first copy at line ${first_copy:-none}"
[ "$gone" = "$want_gone" ] && [ "$(printf '%s\n' "$new" | grep -c .)" -eq 5 ] &&
  printf '%s\n' "$new" | grep -qx '. "$(dirname "${BASH_SOURCE\[0\]}")/nopath_desk_e183.sh"     # note 5' &&
  printf '%s\n' "$new" | grep -qx 'rb_init s22_collect_v3' && printf '%s\n' "$new" | grep -q '^nopath_desk "$OUT" ' &&
  printf '%s\n' "$new" | grep -q '^nopath_desk_ready ' &&
  printf '%s\n' "$new" | grep -q '^rb_say "E183 collected and scored (step 11 v3: v2 with note 5'"'"'s desk-path gate; the reduction v2)' &&
  [ -n "$ready_at" ] && [ -n "$raw_at" ] && [ -n "$first_copy" ] && [ "$ready_at" -lt "$raw_at" ] && [ "$ready_at" -lt "$first_copy" ]
ok $? "G11 v3 is v2 with exactly three lines replaced and two added (the source line, the early check before any copy), and comment lines"
echo
echo "== G12: step 11 v3's dry listing"
mkdir -p "$S/out-dry"
( export RB_DRY=1 RB_OUT="$S/out-dry" RB_LOCK="$S/lock.txt"
  bash "$R/s02_window_e183.sh" 2026-11-13 12:00 13:00 > /dev/null 2>&1
  bash "$R/s22_collect_e183_v3.sh" ) > "$S/g.txt" 2>&1; r=$?
echo "rc $r; $(grep -c . "$S/g.txt") lines; $(grep -c 'gate (note 5)' "$S/g.txt") naming note 5's gate, $(grep -c 'check (note 5)' "$S/g.txt") its early check; ssh or rsync run: $(grep -c '^rb_run' "$S/g.txt")"
if [ "$shape" = home ]; then
  [ "$r" -eq 0 ] && grep -q 'gate (note 5)' "$S/g.txt" && grep -q 'check (note 5)' "$S/g.txt"; ok $? "G12 step 11 v3's dry listing exits 0 and names note 5's early check and gate"
else
  [ "$r" -eq 0 ]; ok $? "G12 step 11 v3's dry listing exits 0 (this desk's home is not under /home/: rb_nopath's line)"
fi
echo
echo "== G13-G19: the desk's home, or the box's tree, followed by '..', '.' or '/' (the spelling check)"
sp() {  # sp <case> <what> <line> <want rc>
  w "$1" "$3"
  gate nopath_desk keep "" "" "$S/data/$1"; r=$?
  echo "nopath_desk: rc $r; $(kinds)"
  if [ "$4" = 16 ]; then [ "$r" -eq 16 ] && grep -q "^HIT .*: a path under the desk's home written with '.', '..' or '//', outside the box's tree" "$S/g.txt"
  else [ "$r" -eq 0 ]; fi
  ok $? "$1 $2"
}
if [ "$shape" = home ]; then
  sp G13 "the home followed by '..' stops v3's gate (16)" "$HP/../$LG/$ENT/x" 16
  sp G14 "the home followed by '.' stops v3's gate (16)" "$HP/./$ENT/x" 16
  sp G15 "the home followed by '/' stops v3's gate (16)" "$HP//$ENT/x" 16
  sp G16 "the box's tree followed by '..' stops v3's gate (16)" "$HP/aifoundry/../$ENT/x" 16
  sp G17 "a deeper climb out of the box's tree stops v3's gate (16)" "$HP/aifoundry/build/e183/../../../$ENT/x" 16
  sp G18 "a climb that stays in the box's tree passes v3's gate (0)" "-I$HP/aifoundry/external/build/../include" 0
  sp G19a "the home's own directory written with '//' stops v3's gate (16)" "$(dirname "$HP")//$LG/$ENT/x" 16
  sp G19b "the home's own directory written with '/./' stops v3's gate (16)" "$(dirname "$HP")/./$LG/$ENT/x" 16
else echo "(G13-G19 reported: this desk's home is not under /home/)"; fi
echo
echo "== G20/G21: stand-in homes with entries the gate cannot forbid by name"
case "$S" in
  /home/?*)
    FH=$S/fh
    mkdir -p "$FH/a" "$FH/aif" "$FH/realdir"; ln -s /usr "$FH/lnk-system"; ln -s "$FH/realdir" "$FH/lnk-inside"
    for c in "G20a $FH/a/x" "G20b $FH/aif/x" "G20c $FH/lnk-system/x" "G20d $FH/lnk-inside/x"; do
      id=${c%% *}; p=${c#* }
      w "$id" "$p"
      gate nopath_desk set "$FH" "$FH" "$S/data/$id"; r=$?
      echo "nopath_desk: rc $r; $(kinds); $(grep -o 'read as whole path components instead:.*' "$S/g.txt" | head -n 1)"
      [ "$r" -eq 16 ] && grep -q "^HIT .*: a path under an entry of the desk's home the gate leaves out by name" "$S/g.txt"
      ok $? "$id a path under an entry left out by name ($(basename "$(dirname "$p")")) stops v3's gate (16)"
    done
    w G20e "$FH/aifoundry/build/e183/x (the box tree's form)"
    gate nopath_desk set "$FH" "$FH" "$S/data/G20e"; r=$?; echo "nopath_desk: rc $r; HIT lines $(hits)"
    [ "$r" -eq 0 ]; ok $? "G20e the box tree's form passes beside those entries (0)"
    FH2=$S/fh2; mkdir -p "$FH2/aifoundry"
    gate nopath_desk_ready set "$FH2" "$FH2"; r1=$?; s1=$(grep -c "holds an entry named as aifoundry3's tree" "$S/g.txt")
    gate nopath_desk set "$FH2" "$FH2" "$S/data/box"; r2=$?; s2=$(grep -c "holds an entry named as aifoundry3's tree" "$S/g.txt")
    echo "an entry named as the box's tree: nopath_desk_ready rc $r1, nopath_desk rc $r2"
    [ "$r1" -eq 16 ] && [ "$s1" -eq 1 ] && [ "$r2" -eq 16 ] && [ "$s2" -eq 1 ]; ok $? "G21 an entry named as the box's tree: the early check and the gate refuse (16)"
    ;;
  *) echo "(G20/G21 reported: the scratch directory is not under /home/, so its stand-in homes cannot take the box account's shape)" ;;
esac
echo
echo "== G22: HOME"
if [ "$shape" = home ]; then
  for c in "empty|" "relative|$(basename "$S")" "missing|/nonexistent-e183-selftest" "a subdirectory|$HP/$ENT"; do
    what=${c%%|*}; hv=${c#*|}
    gate nopath_desk_ready set "$hv" ""; r=$?
    echo "HOME $what: nopath_desk_ready rc $r: $(grep -m1 'STOP' "$S/g.txt" | sed 's/^\[[^]]*\] STOP: //' | cut -c1-90)"
    [ "$r" -eq 10 ]; ok $? "G22 HOME $what: the early check refuses (10)"
  done
  gate nopath_desk_ready unset "" ""; r=$?; echo "HOME unset: nopath_desk_ready rc $r"
  [ "$r" -eq 0 ]; ok $? "G22 HOME unset: the early check passes (the account database's home)"
  ln -s "$HP" "$TMPL/home"
  w G22link "a desk path through HOME's link: $TMPL/home/$ENT/x"
  gate nopath_desk set "$TMPL/home" "" "$S/data/G22link"; r=$?
  echo "HOME a link to the home: nopath_desk on a desk path written through it: rc $r; $(kinds)"
  [ "$r" -eq 16 ] && grep -q "^HIT .*: the forbidden path $TMPL/home/$ENT (" "$S/g.txt"; ok $? "G22 HOME a link to the home: a desk path written through it stops v3's gate (16)"
  gate nopath_desk set "$TMPL/home" "" "$S/data/box"; r=$?; echo "HOME a link to the home: nopath_desk on the box's tree path: rc $r"
  [ "$r" -eq 0 ]; ok $? "G22 HOME a link to the home: the box's tree path passes (0)"
else echo "(G22 reported: this desk's home is not under /home/)"; fi
echo
echo "SELFTEST-NOPATH-E183 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase)"
return "$fail"
}
main 2>&1 | sed -e "s#$S#<scratch>#g" -e "s#$SRC#<repo>#g" -e "s#$TMPL#<a link dir>#g" -e "s#$HP#<home>#g" -e "s#/tmp/claude-$(id -u)#/tmp/claude-<uid>#g"
rc=${PIPESTATUS[0]}
rm -rf "${TMPL:?}"
exit "$rc"

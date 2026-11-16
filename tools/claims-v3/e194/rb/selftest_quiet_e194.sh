#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the desk test of THE QUIET DESK FLAG
# (rb/quiet_e194.sh, and e194_quiet in every step from the look to the collection). No box, no device: the steps run with a stand-in ssh,
# rsync and scp first on PATH that count every call (want 0), and the P2 counts run in a private PID namespace (bubblewrap) so that no
# process of another lane is counted. Run inside the round's sandbox (W/nodev.sh). Cases (verdicts stated first):
#   QF1 raise with RB_QUIET unset, or naming a file inside the lab repo: refused (10), no flag;
#   QF2 raise by the card lane: the flag holds "e194 <lane> <time>"; check 0; raise again by the same lane 0; raise by another lane 10, the
#       flag unchanged; a flag another lane raised first (other words): raise 10, never overwritten;
#   QF3 lower by another lane: 10, the flag kept; lower by its owner: 0, the flag gone; check 10; lower again 0 (nothing to lower);
#   QF4 EVERY STEP FROM THE LOOK TO THE COLLECTION refuses (10) with the flag down, before any box call: s05 (the look), s07 (the tree),
#       s08 (the build, start and wait), s09 (the reads), s10 (the dry pass), s11 (the session), s22 (the collection); 0 calls to the stand-ins;
#   QF5 with the flag up, the steps go past the flag (each stops later, at its first box call: the stand-in ssh answers nothing, 12);
#   QF6 THE P2 COUNT in a private PID namespace: nothing of ours: P2 0 (exit 0); a stand-in process named ledger_host: P2 1 (16); one named
#       ettelem that ends after 3 s, with --wait: 0 after a re-read; sys_emu: 16; a script session_e194.sh run by bash: counted (16); a
#       `grep session_e194.sh`, a `bash -c` string naming it and a --dry run of it: not counted (0).
#   bash tools/claims-v3/e194/rb/selftest_quiet_e194.sh <scratch dir outside the repo> > selftest-quiet-e194.txt
# The last line: SELFTEST-QUIET-E194 <n> of <m> PASS (or FAIL). A desk check of code. SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
Q=$SRC/tools/claims-v3/e194/rb/quiet_e194.sh
R=$SRC/tools/claims-v3/e194/rb
n=0; m=0
ok() { m=$((m + 1)); if [ "$1" = "$2" ]; then n=$((n + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fi; }
main() {
echo "selftest_quiet_e194: $(date '+%F %T %Z') on $(hostname)"
mkdir -p "$S/standin" "$S/rbout"
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 255\n' "$c" "$S" > "$S/standin/$c"; chmod +x "$S/standin/$c"; done
: > "$S/box-calls.txt"
F=$S/quiet-flag
rm -f "$F"
# ---- QF1
a=$( (unset RB_QUIET; bash "$Q" raise card-e194) > "$S/o.txt" 2>&1; echo $?); b=$(RB_QUIET="$SRC/tools/claims-v3/e194/flag" bash "$Q" raise card-e194 > /dev/null 2>&1; echo $?)
ok "$a.$b.$([ -e "$SRC/tools/claims-v3/e194/flag" ] && echo made || echo none)" "10.10.none" "QF1 raise with RB_QUIET unset, or naming a file inside the repo: refused (10), no flag"
# ---- QF2
export RB_QUIET=$F
a=$(bash "$Q" raise card-e194 > "$S/o.txt"; echo $?); w=$(cut -d' ' -f1-2 "$F" 2>/dev/null)
b=$(bash "$Q" check > /dev/null; echo $?); c=$(bash "$Q" raise card-e194 > /dev/null; echo $?)
h1=$(sha256sum "$F" | cut -c1-16); d=$(bash "$Q" raise other-lane > /dev/null; echo $?); h2=$(sha256sum "$F" | cut -c1-16)
cp "$F" "$S/flag-ours"; echo "e190 card-e190 2026-11-13 16:05:59 PST" > "$F"; e=$(bash "$Q" raise card-e194 > /dev/null; echo $?)
f=$(cut -d' ' -f1 "$F"); cp "$S/flag-ours" "$F"
ok "$a.$w.$b.$c.$d.$([ "$h1" = "$h2" ] && echo same).$e.$f" "0.e194 card-e194.0.0.10.same.10.e190" \
  "QF2 raised by the card lane (e194 <lane> <time>); check 0; again by it 0; by another lane 10, unchanged; another lane's flag never overwritten (10)"
# ---- QF3
a=$(bash "$Q" lower other-lane > /dev/null; echo $?); k1=$([ -e "$F" ] && echo kept || echo gone)
b=$(bash "$Q" lower card-e194 > /dev/null; echo $?); k2=$([ -e "$F" ] && echo kept || echo gone)
c=$(bash "$Q" check > /dev/null; echo $?); d=$(bash "$Q" lower card-e194 > /dev/null; echo $?)
ok "$a.$k1.$b.$k2.$c.$d" "10.kept.0.gone.10.0" "QF3 lower by another lane refused (kept); by its owner 0 (gone); check 10; lower again 0"
# ---- QF4 / QF5: the steps, with a window written today
export RB_OUT=$S/rbout RB_LOCK=$S/lock.txt RB_DESKTEST=1 E194_DESK_BUDGET_S=60 PATH="$S/standin:$PATH"
bash "$R/s02_window_e194.sh" "$(TZ=America/Los_Angeles date +%F)" 23:58 23:59 > "$S/w.txt" 2>&1 || { echo "the window step failed:"; cat "$S/w.txt"; }
echo ledger,spp > "$RB_OUT/e194-built.txt"; echo 1794700000 > "$RB_OUT/e194-T0.txt"; echo us > "$RB_OUT/box-login-aifoundry2.txt"
rm -f "$F"
res=""
for st in "s05_look_e194.sh" "s07_tree_e194.sh pull" "s08_build_e194.sh start" "s08_build_e194.sh wait" "s09_reads_e194.sh" \
          "s10_dry_e194.sh start" "s11_session_e194.sh FULL" "s22_collect_e194.sh"; do
  set -- $st
  bash "$R/$1" ${2:+"$2"} > "$S/o.txt" 2>&1; rc=$?
  q=$(grep -c "THE QUIET DESK FLAG is not raised" "$S/o.txt")
  echo "   QF4 $st: rc $rc; $(grep -m1 'STOP' "$S/o.txt" | cut -c1-150)"
  res="$res$rc:$q "
done
ok "$res|$(grep -c . "$S/box-calls.txt")" "10:1 10:1 10:1 10:1 10:1 10:1 10:1 10:1 |0" \
  "QF4 every step from the look to the collection refuses (10) with the flag down, before any box call (0 calls)"
bash "$Q" raise card-e194 > /dev/null
res=""
for st in "s05_look_e194.sh" "s09_reads_e194.sh" "s11_session_e194.sh FULL" "s22_collect_e194.sh"; do
  set -- $st
  bash "$R/$1" ${2:+"$2"} > "$S/o.txt" 2>&1; rc=$?
  q=$(grep -c "THE QUIET DESK FLAG is not raised" "$S/o.txt")
  echo "   QF5 $st: rc $rc; $(grep -m1 'STOP' "$S/o.txt" | cut -c1-150)"
  res="$res$rc:$q "
done
ok "$res" "12:0 12:0 12:0 12:0 " "QF5 with the flag up, the steps go past it and stop at their first box call (the stand-in ssh answers nothing: 12)"
bash "$Q" lower card-e194 > /dev/null
unset RB_DESKTEST E194_DESK_BUDGET_S
# ---- QF6: THE P2 COUNT in a private PID namespace
cat > "$S/p2.sh" <<EOF
set -u
mkdir -p "$S/bin6"
for nm in ledger_host ettelem sys_emu; do cp /usr/bin/sleep "$S/bin6/\$nm"; done
printf 'sleep 30\n' > "$S/bin6/session_e194.sh"
r() { bash "$Q" count \${1:-} > "$S/p2-\$2.txt" 2>&1; echo -n "\$?"; }
echo -n "none:"; r "" none; echo
"$S/bin6/ledger_host" 20 & p=\$!; sleep 0.5; echo -n "host:"; r "" host; echo; kill \$p; wait \$p 2>/dev/null
"$S/bin6/ettelem" 3 & p=\$!; sleep 0.3; echo -n "ettelem-wait:"; r --wait ettelem; echo; wait \$p 2>/dev/null
"$S/bin6/sys_emu" 20 & p=\$!; sleep 0.5; echo -n "sysemu:"; r "" sysemu; echo; kill \$p; wait \$p 2>/dev/null
bash "$S/bin6/session_e194.sh" & p=\$!; sleep 0.5; echo -n "session:"; r "" session; echo; kill \$p; wait \$p 2>/dev/null
grep -q session_e194.sh /dev/null; ( exec -a grep sleep 20 ) & g=\$!
bash -c "sleep 20; echo session_e194.sh" & c=\$!
bash "$S/bin6/session_e194.sh" --dry & d=\$!
sleep 0.5; echo -n "notcounted:"; r "" notcounted; echo; kill \$g \$c \$d 2>/dev/null; wait 2>/dev/null
EOF
/usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- bash "$S/p2.sh" > "$S/p2.txt" 2>&1
sed 's/^/   QF6 /' "$S/p2.txt"
for x in none host ettelem sysemu session notcounted; do sed "s/^/      $x: /" "$S/p2-$x.txt" 2>/dev/null | tail -n 2; done
ok "$(tr '\n' ' ' < "$S/p2.txt")" "none:0 host:16 ettelem-wait:0 sysemu:16 session:16 notcounted:0 " \
  "QF6 the P2 count: 0 with nothing; a ledger_host 16; an ettelem that ends, read again with --wait: 0; sys_emu 16; session_e194.sh run by bash 16; a grep, a bash -c string and a --dry run not counted (0)"
echo "SELFTEST-QUIET-E194 $n of $m $([ "$n" -eq "$m" ] && echo PASS || echo FAIL)"
[ "$n" -eq "$m" ]
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g"
exit "${PIPESTATUS[0]}"

#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): THE BUILD'S DESK TEST, E209's form (tools/claims-v3/e209/desk/
# desktest_build_e209.sh) with E216's second build. The box root made by make_box_e216.py sync in a scratch folder of ours (outside the
# repo), then, as runbook step 6 runs them from that root: E208's src/build_mms.sh, unchanged (rgm136 and the lab's ettelem against this
# box's /opt/et; THE KERNEL BY ITS BYTES aace138c...; the host's four refusals; build/BUILD-mms.json), then E216's src/build_e216.sh
# (rgm211 from E211's sources at kernel-e216.json's pins into build/e216rgm211; its host's eight refusals inside a bubblewrap with no
# card node; rgm136's ELF through the identity gate for both families and rgm211's own ELF refused by both; build/BUILD-e216.json).
# The built hosts RUN, so this test runs only inside W/nodev.sh (no /dev/et*); et-who is a stand-in (the builds' quiet-box look).
#   bash W/slot.sh bash W/nodev.sh bash tools/claims-v3/e216/desk/desktest_build_e216.sh <empty scratch dir outside the repo>
# The cases: B1 both builds as step 6 runs them; B2 E216's build refused without E208's build of today; B3 an rgm211 source changed: no
# build; B4 the box lock held: refused; B5 rgm211's ELF in rgm136's place: the gate refuses family G (no record BUILT); B6 the built root
# is kept as <scratch>/root for the real-path and dry tests (its ELFs at E216's pins). Prints DESKTEST-BUILD-E216 <n> of 6 PASS last.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for d in /dev/et*; do
  [ -e "$d" ] || continue
  if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
done
mkdir -p "$S" && S=$(cd "$S" && pwd -P)
[ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
R=$S/root
mkdir -p "$R" "$S/bin"
printf '#!/bin/sh\n# the build test'"'"'s stand-in for et-who: every card free (no card at the desk)\nexit 0\n' > "$S/bin/et-who"
chmod 755 "$S/bin/et-who"
export PATH="$S/bin:$PATH"
N=0; P=0
res() { N=$((N + 1)); if [ "$2" = PASS ]; then P=$((P + 1)); fi; echo "CASE $1: $2 ($3)"; }
echo "== sync"
/usr/bin/python3 -I -B "$SRC/tools/claims-v3/e216/make_box_e216.py" sync "$R"; rc=$?
[ "$rc" -eq 0 ] || { echo "DESKTEST-BUILD-E216 FAIL (the sync, rc $rc)"; exit 1; }
echo "== B1: E208's build, then E216's, from the box root (step 6)"
t0=$(date +%s)
bash "$R/src/build_mms.sh" > "$S/b1-mms.txt" 2>&1; rc1=$?
tail -n 3 "$S/b1-mms.txt"
bash "$R/src/build_e216.sh" > "$S/b1-e216.txt" 2>&1; rc2=$?
cat "$S/b1-e216.txt"
echo "builds rc $rc1 and $rc2 in $(( $(date +%s) - t0 )) s"
B1=$(/usr/bin/python3 -I -B - "$R" "$rc1" "$rc2" <<'PY'
import hashlib, json, os, sys
r, rc1, rc2 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None
m = json.load(open(os.path.join(r, "build", "BUILD-mms.json")))
e = json.load(open(os.path.join(r, "build", "BUILD-e216.json")))
pin = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"
k = sha(os.path.join(r, "build/rgm/kernel/sparsity.elf"))
h211 = sha(os.path.join(r, "build/e216rgm211/host/sparsity_host"))
ok = (rc1 == 0 and rc2 == 0 and m.get("verdict") == "BUILT" and e.get("verdict") == "BUILT" and m.get("box") == e.get("box") == "aifoundry2"
      and k == pin == m.get("kernel_sha256") and h211 == e.get("host_sha256") and len(e.get("host_checks") or []) == 8
      and all(c.endswith(":ok") for c in e["host_checks"]) and str(e.get("family_g_gate", "")).startswith("GATE OK: "))
print(("PASS" if ok else "FAIL") + f"|rgm136 ELF {k[:16] if k else None} (pin {'EQUAL' if k == pin else 'DIFFERENT'}); rgm211 host {h211[:16] if h211 else None}; "
      f"its refusals {len(e.get('host_checks') or [])} ok; rgm211's own ELF {str(e.get('rgm211_elf_sha256'))[:16]} (E211's whole pin: "
      f"{e.get('rgm211_elf_is_e211_whole_pin')}); {e.get('family_g_gate', '')[:60]}")
PY
)
res B1 "${B1%%|*}" "${B1#*|}"
cp -p "$R/build/BUILD-mms.json" "$S/BUILD-mms.json.good"
cp -p "$R/build/BUILD-e216.json" "$S/BUILD-e216.json.good"
echo "== B2: E216's build without E208's build of today"
/usr/bin/python3 -I -B - "$R/build/BUILD-mms.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["day"] = "2026-11-18"; json.dump(d, open(p, "w"), indent=1)
PY
bash "$R/src/build_e216.sh" > "$S/b2.txt" 2>&1; rc=$?
cp -p "$S/BUILD-mms.json.good" "$R/build/BUILD-mms.json"
grep -q "E216-BUILD-FAILED: no E208 build of today" "$S/b2.txt" && [ "$rc" -eq 1 ] && res B2 PASS "rc $rc: $(tail -n 1 "$S/b2.txt" | cut -c1-110)" || res B2 FAIL "rc $rc: $(tail -n 1 "$S/b2.txt")"
echo "== B3: an rgm211 source changed"
cp -p "$R/src/rgm211/host/main.cpp" "$S/main.cpp.good"
echo "// a desk test's change" >> "$R/src/rgm211/host/main.cpp"
bash "$R/src/build_e216.sh" > "$S/b3.txt" 2>&1; rc=$?
cp -p "$S/main.cpp.good" "$R/src/rgm211/host/main.cpp"
grep -q "E216-BUILD-FAILED: the rgm211 sources: SOURCES DIFFER" "$S/b3.txt" && [ "$rc" -eq 1 ] && res B3 PASS "rc $rc: SOURCES DIFFER, no build" || res B3 FAIL "rc $rc: $(tail -n 1 "$S/b3.txt")"
echo "== B4: the box lock held"
( exec 8>>"$R/run/box.lock"; flock -n 8; bash "$R/src/build_e216.sh" > "$S/b4.txt" 2>&1; echo "$?" > "$S/b4.rc" )
rc=$(cat "$S/b4.rc")
grep -q "E216-BUILD-REFUSED: run/box.lock is held" "$S/b4.txt" && [ "$rc" -eq 3 ] && res B4 PASS "rc $rc: refused" || res B4 FAIL "rc $rc: $(tail -n 1 "$S/b4.txt")"
echo "== B5: rgm211's own ELF in rgm136's place"
cp -p "$R/build/rgm/kernel/sparsity.elf" "$S/sparsity.elf.good"
bash "$R/src/build_e216.sh" > /dev/null 2>&1      # a fresh rgm211 build first (B3 left none)
cp -p "$R/build/e216rgm211/kernel/sparsity.elf" "$S/rgm211.elf"
cp -p "$S/rgm211.elf" "$R/build/rgm/kernel/sparsity.elf"
bash "$R/src/build_e216.sh" > "$S/b5.txt" 2>&1; rc=$?
cp -p "$S/sparsity.elf.good" "$R/build/rgm/kernel/sparsity.elf"
V=$(/usr/bin/python3 -I -B -c 'import json,sys; print(json.load(open(sys.argv[1])).get("verdict"))' "$R/build/BUILD-e216.json")
grep -q "E216-BUILD-FAILED: rgm136's ELF does not pass for family G" "$S/b5.txt" && [ "$rc" -eq 1 ] && [ "$V" = BUILD-FAILED ] \
  && res B5 PASS "rc $rc, the record $V: $(grep '^GATE rgm136' "$S/b5.txt" | head -n 1 | cut -c1-120)" || res B5 FAIL "rc $rc, record $V: $(tail -n 1 "$S/b5.txt")"
echo "== B6: the root rebuilt as step 6 leaves it (for the real-path and dry tests)"
bash "$R/src/build_mms.sh" > "$S/b6-mms.txt" 2>&1; r1=$?
bash "$R/src/build_e216.sh" > "$S/b6-e216.txt" 2>&1; r2=$?
[ "$r1" -eq 0 ] && [ "$r2" -eq 0 ] && grep -q "E216-BUILT rc=0" "$S/b6-e216.txt" && res B6 PASS "both BUILT again: $R" || res B6 FAIL "rc $r1 / $r2"
echo "DESKTEST-BUILD-E216 $P of $N $( [ "$P" -eq "$N" ] && echo PASS || echo FAIL)"
[ "$P" -eq "$N" ]

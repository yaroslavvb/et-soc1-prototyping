#!/usr/bin/env bash
# Q141(k), go checklist step 14: aifoundry2's tree and preflights, no device opened (six calls, after the probe):
#   the tree (a copy, 600 s): git pull --ff-only; git merge-base --is-ancestor c31e7ae3 HEAD; git status --porcelain -- tools/claims-v3
#     empty (E165 README steps 3-4, E168 README step 2);
#   E165: e165_common.py (61 tiles, frozen inputs, Q139(k)'s files OK); blind7 91; binaries eae32a15 / 990807f4 / 77a46171;
#   E167: run_e167.sh check, and sha256sum -c frozen-e167-x2.sha256 (README.md.dated-note.md);
#   E168: E136's binaries 76475508 / aace138c / 77a46171; run_e168.py --list (README steps 3-4);
#   E169: shasum -c frozen-sha256-e169.txt (54) and frozen-sha256-e169-tiles.txt (3); score_e169.py check; selftest_kit_e169.py;
#   et-lab-manifest (kept), uptime -s, and the holder rule's counts.
# Each run's verdict goes to $RB_OUT/a2-tree.txt. Exit 0 every planned run reads clean; 16 one does not (skip that run, or a dated
# amendment first); 17 et-who is not clean (look again with s05_look.sh aifoundry2 --wait).
#
#   bash tools/claims-v3/q141k-runbook/v2/s14_a2_tree.sh
#
# v2 (Q141(k)'s verifier, fault 5): aifoundry2's firmware identity is gated, by continuity and never by the firmware-revisions query.
# E69's revisions read (2026-10-27 13:56:26 PDT: release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions 0.25.1) was made inside the host
# boot of 2026-10-26 15:13:03 PDT (E77's CHANGE-RECORD.md, "Firmware identities: by continuity"; E77's G0 row). The read call's
# `uptime -s` must come before E69's read, as look_e164.sh holds aifoundry1 to E82's; a host booted since then exits 16 for every
# aifoundry2 run, because every aifoundry2 kit's commands are classified from BL2 0.22.0's source and E168's README step 5 makes
# another build NO-GO. v1 printed the boot and compared it with nothing (et-lab-manifest reads sysfs and names no firmware).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s14_a2_tree
rb_window
case "$RB_PLAN" in full) planned="e165 e167 e168 e169" ;; b) planned="e165 e167" ;; a) planned="e165" ;; esac
rb_probe aifoundry2
mk() { f=$(rb_file "$1"); rb_prelude aifoundry2 > "$f"; }   # then the body is appended to "$f"
mk tree
cat >> "$f" <<EOF
GIT_TERMINAL_PROMPT=0 git pull --ff-only; echo "pull rc=\$?"
git merge-base --is-ancestor $RB_BASE HEAD; echo "ancestry rc=\$?"
echo "porcelain lines: \$(git status --porcelain -- tools/claims-v3 | wc -l)"
git log -1 --format='HEAD %h %ad' --date=format:'%F %T %z'
EOF
rb_remote copy aifoundry2 "git pull --ff-only; ancestry; tools/claims-v3 clean" "$f"
tree_ok=1
rb_has '^pull rc=0$' && rb_has '^ancestry rc=0$' && rb_has '^porcelain lines: 0$' || tree_ok=0
mk e165
cat >> "$f" <<'EOF'
python3 tools/claims-v3/e165/e165_common.py | tail -n 4
echo "blind7 OK: $(cd tools/claims-v3/kinds/blind7 && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')"
sha256sum build/ccheck/b/host/sparsity_host build/sparsity_t2/kernel/sparsity.elf build/ettelem-hpl/ettelem | cut -c1-8,65-
EOF
rb_remote read aifoundry2 "E165: e165_common, blind7, the binaries" "$f"
v165=1
rb_has '^61 tiles; frozen inputs, Q139\(k\)'"'"'s files and tiles: OK' && rb_has '^blind7 OK: 91$' &&
  rb_has '^eae32a15 +build/ccheck/b/host/sparsity_host' && rb_has '^990807f4 +build/sparsity_t2/kernel/sparsity.elf' &&
  rb_has '^77a46171 +build/ettelem-hpl/ettelem' || v165=0
mk e167
cat >> "$f" <<'EOF'
bash tools/claims-v3/e167/run_e167.sh check
sha256sum -c tools/claims-v3/e167/frozen-e167-x2.sha256 > build/e167-x2-q141k.txt 2>&1; echo "frozen-e167-x2 rc=$? OK $(grep -c ': OK$' build/e167-x2-q141k.txt)"
EOF
rb_remote read aifoundry2 "E167: run_e167.sh check; frozen-e167-x2.sha256" "$f"
v167=1
rb_has '^frozen-e167.sha256: every file as registered$' && rb_has '^frozen-e167-x2 rc=0 OK 15$' || v167=0
mk e168
cat >> "$f" <<'EOF'
sha256sum build/e136/host/sparsity_host build/e136/kernel/sparsity.elf build/ettelem-hpl/ettelem | cut -c1-8,65-
python3 tools/claims-v3/e168/run_e168.py --protocol tools/claims-v3/e168/protocol.json --out build/e168/list --list | tail -n 3; echo "run_e168 list rc=${PIPESTATUS[0]}"
EOF
rb_remote read aifoundry2 "E168: E136's binaries; run_e168.py --list" "$f"
v168=1
rb_has '^76475508 +build/e136/host/sparsity_host' && rb_has '^aace138c +build/e136/kernel/sparsity.elf' &&
  rb_has '^77a46171 +build/ettelem-hpl/ettelem' && rb_has '^run_e168 list rc=0$' || v168=0
mk e169
cat >> "$f" <<'EOF'
cd tools/claims-v3/e169 || exit 1
echo "e169 frozen OK $(shasum -a 256 -c frozen-sha256-e169.txt 2>&1 | grep -c ': OK$') tiles OK $(shasum -a 256 -c frozen-sha256-e169-tiles.txt 2>&1 | grep -c ': OK$')"
python3 -B score_e169.py check | tail -n 1
python3 -B selftest_kit_e169.py | tail -n 1
EOF
rb_remote read aifoundry2 "E169: the two hash lists, score_e169.py check, selftest_kit_e169.py" "$f"
v169=1
rb_has '^e169 frozen OK 54 tiles OK 3$' && rb_has 'CHECK OK' && rb_has 'ALL PASS' || v169=0
mk reads
cat >> "$f" <<'EOF'
mkdir -p build/q141k
et-lab-manifest | tee build/q141k/et-lab-manifest-$(date +%Y%m%dT%H%M%S).txt
echo "booted $(uptime -s)"; uptime
boot=$(date -d "$(uptime -s)" +%s); fw=$(date -d '2026-10-27 13:56:26 PDT' +%s)
if [ "$boot" -lt "$fw" ]; then echo "IDENTITY-OK: the host booted $(uptime -s), before E69's firmware read of 2026-10-27 13:56:26 PDT (BL2 0.22.0 by continuity)"
else echo "IDENTITY-STOP: the host booted $(uptime -s), after E69's firmware read of 2026-10-27 13:56:26 PDT: BL2 0.22.0 is not carried"; fi
hold_read
echo "HOLDER-RULE: $([ "$FREE" -eq 1 ] && echo FREE || echo HELD)"
EOF
rb_remote read aifoundry2 "et-lab-manifest, uptime, et-who, who" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
id_ok=1; rb_has '^IDENTITY-OK: ' || id_ok=0
{ echo "$(date '+%F %T %Z') aifoundry2 tree=$tree_ok e165=$v165 e167=$v167 e168=$v168 e169=$v169 identity=$id_ok (1 = reads clean)"; } >> "$RB_OUT/a2-tree.txt"
[ "$id_ok" -eq 1 ] || rb_die $RB_E_GATE "aifoundry2's firmware identity is not carried: $(grep -m1 '^IDENTITY-' "$RB_CAP" || echo 'no identity line came back'). No aifoundry2 run until it is shown again on a READ path (never the firmware-revisions query) or a dated amendment says what to do"
bad=""
[ "$tree_ok" -eq 1 ] || bad="$bad the-tree"
for r in $planned; do eval "v=\$v${r#e}"; [ "$v" -eq 1 ] || bad="$bad $r"; done
[ -z "$bad" ] || rb_die $RB_E_GATE "aifoundry2 does not read clean for:$bad (skip that run, or a dated amendment first; $RB_OUT/a2-tree.txt)"
rb_has '^HOLDER-RULE: FREE' || rb_die $RB_E_AGAIN "et-who is not clean on aifoundry2: look again (s05_look.sh aifoundry2 --wait)"
rb_say "aifoundry2 reads clean for: $planned (tree at $RB_BASE or later; manifest kept on the box in build/q141k/)"

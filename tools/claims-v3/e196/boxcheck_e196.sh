#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE BOX'S TOOLS AND PINS, read on aifoundry3 after the builds
# (step 6's wait, rb/s08_a3_build_e196.sh), from E196's root R. E192's boxcheck's form (tools/claims-v3/e192/boxcheck_e192.sh). READS ONLY:
# no device is opened and no command is sent (et-who reads /proc).
#   - the host's name, by `hostname` and by Python's socket.gethostname(): aifoundry3 (E196's order is aifoundry3's);
#   - one card node (/dev/et<N>_ops) and the card lock file /run/lock/etsoc-shire0.lock present; `et-who --check` answers (0 or 1, not 2);
#   - the box's sampler <tree>/build/ettelem/ettelem executable (the audit table's reviewed variant 'ettelem', by its build directory),
#     behind E128's guard R/tools/claims-v3/e128/ettelem_guard.sh (synced, at its pin);
#   - every synced file at its pin (the registration's list at 467ede78..., the kit's list, the shared list), every boxfiles path present;
#   - today's build record (build/BUILD-E196.txt: E196-BUILT rc=0, both kernels' .text 8798e43c..., both hosts the files it hashed);
#   - the preflight GO (dmcmd_audit, the stock table, no --allow).
# Prints its readings and BOXCHECK-E196 OK: ... (exit 0) or BOXCHECK-E196 FAIL: ... (exit 16).
#   bash tools/claims-v3/e196/boxcheck_e196.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
R=$(pwd -P); TREE=$(cd "$R/../../../.." && pwd -P)
K=tools/claims-v3/e196
TEXT=8798e43c4869a124690bc652d574d5ab78d686faa70293cbcff658d24c30a399
bad=()
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
echo "host: hostname $hn; Python $pyhn; $(command -v python3) $(python3 -V 2>&1)"
[ "$hn" = aifoundry3 ] && [ "$pyhn" = aifoundry3 ] || bad+=("the host's name is '$hn' / '$pyhn', not aifoundry3")
n=$(ls /dev/et*_ops 2>/dev/null | wc -l | tr -d ' ')
echo "card nodes: $n; lock file: $([ -e /run/lock/etsoc-shire0.lock ] && echo present || echo absent)"
[ "$n" = 1 ] || bad+=("$n card nodes, not 1")
[ -e /run/lock/etsoc-shire0.lock ] || bad+=("no card lock file")
timeout 30 et-who --check > /dev/null 2>&1; w=$?
echo "et-who --check: exit $w (0 free, 1 held, 2 failed)"
[ "$w" -eq 0 ] || [ "$w" -eq 1 ] || bad+=("et-who --check exit $w")
[ -x "$TREE/build/ettelem/ettelem" ] || bad+=("no executable sampler build/ettelem/ettelem in the box's tree")
echo "sampler: build/ettelem/ettelem $(sha256sum "$TREE/build/ettelem/ettelem" 2>/dev/null | cut -c1-16)..."
[ "$(sha256sum $K/SHA256SUMS-e196-registration | cut -d' ' -f1)" = 467ede7827f5ed33df6c883c9641caccb1e10ed78f88fbadc322a15a90137ce5 ] || bad+=("the registration's list is off its sha256")
pins=0
for L in $K/SHA256SUMS-e196-registration $K/SHA256SUMS-e196-kit $K/SHA256SUMS-e196-shared; do
  while read -r h p; do
    [ -e "$p" ] || continue
    pins=$((pins + 1))
    [ "$(sha256sum "$p" | cut -d' ' -f1)" = "$h" ] || bad+=("$p is off its pin")
  done < "$L"
done
while IFS= read -r p; do case "$p" in ''|'#'*) continue ;; esac; [ -e "$p" ] || bad+=("the synced $p is absent"); done < $K/boxfiles-e196.txt
echo "pins: $pins synced files read at their lists' sha256"
TODAY=$(TZ=America/Los_Angeles date +%F)
B=build/BUILD-E196.txt
if [ -f "$B" ] && grep -q "^built $TODAY " "$B" && grep -q '^E196-BUILT rc=0' "$B" &&
   [ "$(grep -c "^kernel_text_sha256_\(lab\|x14\) $TEXT\$" "$B")" = 2 ] &&
   [ "$(sha256sum build/sparsity-lab/host/sparsity_host | cut -d' ' -f1)" = "$(sed -n 's/^lab_host_sha256 //p' "$B")" ] &&
   [ "$(sha256sum build/x14/host/x14_host | cut -d' ' -f1)" = "$(sed -n 's/^x14_host_sha256 //p' "$B")" ]; then cat "$B"
else bad+=("no build record from today reading E196-BUILT with both .text 8798e43c... and both hosts at its hashes ($B)"); fi
bash $K/preflight_e196.sh > build/preflight-e196.txt 2>&1
grep -E '^E196-PREFLIGHT' build/preflight-e196.txt
grep -q '^E196-PREFLIGHT: GO' build/preflight-e196.txt || bad+=("the preflight is not GO")
if [ "${#bad[@]}" -gt 0 ]; then printf 'BOXCHECK-E196 FAIL: %s\n' "$(IFS=';'; echo "${bad[*]}")"; exit 16; fi
echo "BOXCHECK-E196 OK: aifoundry3, one card node and its lock file, et-who --check answers, the sampler, $pins files at their pins, today's build record (both .text 8798e43c...), the preflight GO"

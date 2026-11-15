#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE BOX'S TOOLS AND PINS, read on aifoundry3 after the build (step
# 6's wait, rb/s08_a3_build_e192.sh), from E192's root R. READS ONLY: no device is opened and no command is sent (the heater runs only
# its option parser, which exits 2 at an unknown option before anything; et-who reads /proc).
#   - the host's name, by `hostname` and by Python's socket.gethostname(): aifoundry3 (the registered order is drawn on it);
#   - one card node (/dev/et<N>_ops) and the card lock file /run/lock/etsoc-shire0.lock present; `et-who --check` answers (0 or 1,
#     not 2: the 27 Sep et-who with --check);
#   - the box's sampler <tree>/build/ettelem/ettelem executable (the audit table's reviewed variant 'ettelem', by its build directory);
#   - E78's heater <tree>/build/sparsity/host/sparsity_host executable, and its option parser by BEHAVIOUR: the registered heater
#     arguments and --stop-file, then an unknown option: it must stop at the unknown option (exit 2, "unknown option
#     --no-such-option-e192"), so every registered option is one it knows; nothing is grepped from the binary;
#   - E89's per-sensor sampler R/tools/claims-v3/e89/pvt_sample.py at the tables' reviewed sha256 c4e4aed5...;
#   - every synced file at its pin (the registration's list at dd0a8963..., the kit's list, the shared list), and the build's record
#     (build/intbits/BUILD-E192.txt, written by build_e192.sh today);
#   - the preflight: the plain chain GO (the stock table); the per-sensor chain's verdict (E144's table) recorded.
# Prints its readings and BOXCHECK-E192 OK: ... (exit 0) or BOXCHECK-E192 FAIL: ... (exit 16).
#   bash tools/claims-v3/e192/boxcheck_e192.sh
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
R=$(pwd -P); TREE=$(cd "$R/../../../.." && pwd -P)
K=tools/claims-v3/e192
bad=()
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
echo "host: hostname $hn; Python $pyhn; $(command -v python3) $(python3 -V 2>&1)"
[ "$hn" = aifoundry3 ] && [ "$pyhn" = aifoundry3 ] || bad+=("the host's name is '$hn' / '$pyhn', not aifoundry3")
n=$(ls /dev/et*_ops 2>/dev/null | wc -l | tr -d ' ')
echo "card nodes: $n; lock file: $([ -e /run/lock/etsoc-shire0.lock ] && echo present || echo absent)"
[ "$n" = 1 ] || bad+=("$n card nodes, not 1")
[ -e /run/lock/etsoc-shire0.lock ] || bad+=("no card lock file")
et-who --check > /dev/null 2>&1; w=$?
echo "et-who --check: exit $w (0 free, 1 held, 2 failed)"
[ "$w" -eq 0 ] || [ "$w" -eq 1 ] || bad+=("et-who --check exit $w")
[ -x "$TREE/build/ettelem/ettelem" ] || bad+=("no executable sampler build/ettelem/ettelem in the box's tree")
HT=$TREE/build/sparsity/host/sparsity_host
if [ -x "$HT" ]; then
  o=$("$HT" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 \
        --stop-file /nonexistent/e192-stop --no-such-option-e192 2>&1 < /dev/null); hrc=$?
  echo "heater: $(sha256sum "$HT" | cut -c1-16)...; its parser with the registered arguments and an unknown option: exit $hrc, '$(printf '%s' "$o" | head -n 1 | cut -c1-80)'"
  [ "$hrc" -eq 2 ] && printf '%s' "$o" | grep -q 'unknown option --no-such-option-e192' || bad+=("the heater's parser did not stop at the unknown option alone (exit $hrc)")
else
  bad+=("no executable heater build/sparsity/host/sparsity_host in the box's tree")
fi
ps_=$(sha256sum tools/claims-v3/e89/pvt_sample.py 2>/dev/null | cut -d' ' -f1)
echo "per-sensor sampler: ${ps_:0:16}... (reviewed c4e4aed59fbdc08c...)"
[ "$ps_" = c4e4aed59fbdc08ca6155c5a8a877105692d87c80b29b00f5bfd09a9b27c2134 ] || bad+=("pvt_sample.py is not at the reviewed sha256")
[ "$(sha256sum $K/SHA256SUMS-e192-registration | cut -d' ' -f1)" = dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326 ] || bad+=("the registration's list is off its sha256")
pins=0
for L in $K/SHA256SUMS-e192-registration $K/SHA256SUMS-e192-kit $K/SHA256SUMS-e192-shared; do
  while read -r h p; do
    [ -e "$p" ] || continue
    pins=$((pins + 1))
    [ "$(sha256sum "$p" | cut -d' ' -f1)" = "$h" ] || bad+=("$p is off its pin")
  done < "$L"
done
while IFS= read -r p; do case "$p" in ''|'#'*) continue ;; esac; [ -e "$p" ] || bad+=("the synced $p is absent"); done < $K/boxfiles-e192.txt
echo "pins: $pins synced files read at their lists' sha256"
TODAY=$(TZ=America/Los_Angeles date +%F)
if [ -f build/intbits/BUILD-E192.txt ] && grep -q "^built $TODAY " build/intbits/BUILD-E192.txt; then cat build/intbits/BUILD-E192.txt
else bad+=("no build record from today (build/intbits/BUILD-E192.txt)"); fi
bash $K/preflight_e192.sh > build/intbits/preflight.txt 2>&1
grep -E '^(PLAIN|PVT)-CHAIN' build/intbits/preflight.txt
grep -q '^PLAIN-CHAIN: GO' build/intbits/preflight.txt || bad+=("the preflight's plain chain is not GO")
if [ "${#bad[@]}" -gt 0 ]; then printf 'BOXCHECK-E192 FAIL: %s\n' "$(IFS=';'; echo "${bad[*]}")"; exit 16; fi
echo "BOXCHECK-E192 OK: aifoundry3, one card node and its lock file, et-who --check answers, the sampler and the heater (its parser), the per-sensor sampler at its pin, $pins files at their pins, today's build record, the plain chain GO"

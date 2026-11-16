#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE BOX'S TOOLS AND PINS, step 6's wait runs it on aifoundry1 from
# E199's root after the build (one 60 s read; nothing opened, no device command). E192's box check (tools/claims-v3/e192/boxcheck_e192.sh,
# unchanged beside it) made card 1's:
#   - the host's name aifoundry1 (hostname and Python: the registered order draws on it);
#   - AIFOUNDRY1'S TWO CARDS' NODES, by name (exactly /dev/et0_ops /dev/et1_ops and /dev/et0_mgmt /dev/et1_mgmt), card 1's lock file
#     /run/lock/etsoc-shire1.lock present (never created here); et-who --check answering (0 or 1; 2 is a failed check);
#   - the reader <tree>/build/ettelem/ettelem at E191's pin 8008f96f... (E157's, E164's, E172's, E190 arm B's and E191's reader on card 1;
#     the desk test's stand-in reader by E199_DESKTEST=1 and E199_READER_SHA256, the wrapper's own desk variables);
#   - THE SELECTION: the built host, the reader and E78's heater each carry ET_DEVICES (run_session.sh's own grep on a two-card host; the
#     desk alone may report the built host's instead, RB_DESKTEST=1 E199_SELECTION_REPORT_ONLY=1: aifoundry2's /opt/et has none);
#   - E78's heater <tree>/build/sparsity/host/sparsity_host by its behaviour (its parser, given the registered heater arguments,
#     --stop-file and an unknown option, stops at the unknown option alone: exit 2; no device opened) and its sha256 beside the one E157
#     recorded when it ran it as E78's heater on card 1 (e0fbecce..., 3 Nov 2026: reported, never judged);
#   - the per-sensor sampler at the reviewed sha256; E191's identity module at E191's kit pin; every synced file at its list's pin
#     (E192's registration list, E199's registration list, the kit's list and the shared list), every path of boxfiles-e199.txt present;
#   - today's build record (build/intbits/BUILD-E199.txt) and the preflight's plain chain GO (written to build/intbits/preflight.txt).
# Prints BOXCHECK-E199 OK: ... (exit 0) or BOXCHECK-E199 FAIL: <why;...> (exit 16).
#   bash tools/claims-v3/e199/boxcheck_e199.sh          (from E199's root on the box, or the stand-in box of the runbook desk test)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
R=$(pwd -P); TREE=$(cd "$R/../../../.." && pwd -P)
K=tools/claims-v3/e199
bad=()
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
echo "host: hostname $hn; Python $pyhn; $(command -v python3) $(python3 -V 2>&1)"
[ "$hn" = aifoundry1 ] && [ "$pyhn" = aifoundry1 ] || bad+=("the host's name is '$hn' / '$pyhn', not aifoundry1")
ops=""; for d in /dev/et*_ops; do [ -e "$d" ] && ops="$ops $d"; done
mgs=""; for d in /dev/et*_mgmt; do [ -e "$d" ] && mgs="$mgs $d"; done
echo "card nodes:${ops:- none};${mgs:- none}; card 1's lock file: $([ -e /run/lock/etsoc-shire1.lock ] && echo present || echo absent)"
[ "$ops" = " /dev/et0_ops /dev/et1_ops" ] && [ "$mgs" = " /dev/et0_mgmt /dev/et1_mgmt" ] || bad+=("the card nodes are not exactly aifoundry1's two cards'")
[ -e /run/lock/etsoc-shire1.lock ] || bad+=("no card 1 lock file")
et-who --check > /dev/null 2>&1; w=$?
echo "et-who --check: exit $w (0 free, 1 held, 2 failed)"
[ "$w" -eq 0 ] || [ "$w" -eq 1 ] || bad+=("et-who --check exit $w")
RD=$TREE/build/ettelem/ettelem
RPIN=8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325; RW="E191's pin 8008f96f056ae1c2..."
if [ "${E199_DESKTEST:-}" = 1 ] && [ -n "${E199_READER_SHA256:-}" ]; then RPIN=$E199_READER_SHA256; RW="the desk test's stand-in pin ${RPIN:0:16}... (E199_DESKTEST=1, never on the card day)"; fi
rs=$(sha256sum "$RD" 2>/dev/null | cut -d' ' -f1)
echo "reader: ${rs:0:16}... ($RW)"
[ -x "$RD" ] && [ "$rs" = "$RPIN" ] || bad+=("the reader build/ettelem/ettelem is absent or off its pin ($RW)")
HT=$TREE/build/sparsity/host/sparsity_host
H=build/intbits/host/intbits_host
sl=""; for f in "$H" "$RD" "$HT"; do
  if [ -f "$f" ] && grep -aqw ET_DEVICES "$f"; then sl="$sl yes"
  elif [ "$f" = "$H" ] && [ "${RB_DESKTEST:-}" = 1 ] && [ "${E199_SELECTION_REPORT_ONLY:-}" = 1 ]; then sl="$sl no(NOT JUDGED: the desk's built host)"
  else sl="$sl no"; bad+=("$(basename "$f") carries no ET_DEVICES: it would open every card on aifoundry1"); fi
done
echo "selection: ET_DEVICES in the host, the reader, the heater:$sl"
if [ -x "$HT" ]; then
  o=$(ET_DEVICES=1 "$HT" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1 \
        --stop-file /nonexistent/e199-stop --no-such-option-e199 2>&1 < /dev/null); hrc=$?
  hs=$(sha256sum "$HT" | cut -d' ' -f1)
  echo "heater: ${hs:0:16}... (E157's record e0fbecce35f252c5...: $([ "$hs" = e0fbecce35f252c546e6e8390f6a4694519674dc4d6dea359b0db9c4d1a3fbbe ] && echo same || echo different), reported); its parser with the registered arguments and an unknown option: exit $hrc, '$(printf '%s' "$o" | head -n 1 | cut -c1-80)'"
  [ "$hrc" -eq 2 ] && printf '%s' "$o" | grep -q 'unknown option --no-such-option-e199' || bad+=("the heater's parser did not stop at the unknown option alone (exit $hrc)")
else
  bad+=("no executable heater build/sparsity/host/sparsity_host in the box's tree")
fi
ps_=$(sha256sum tools/claims-v3/e89/pvt_sample.py 2>/dev/null | cut -d' ' -f1)
echo "per-sensor sampler: ${ps_:0:16}... (reviewed c4e4aed59fbdc08c...)"
[ "$ps_" = c4e4aed59fbdc08ca6155c5a8a877105692d87c80b29b00f5bfd09a9b27c2134 ] || bad+=("pvt_sample.py is not at the reviewed sha256")
[ "$(sha256sum tools/claims-v3/e191/e191_ident.py 2>/dev/null | cut -d' ' -f1)" = 3fabb60379c81b097473f1cd9b52ccda24dbd924aa00533535aec4ca4256f959 ] || bad+=("e191_ident.py is not at E191's kit pin")
[ "$(sha256sum tools/claims-v3/e192/SHA256SUMS-e192-registration | cut -d' ' -f1)" = dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326 ] || bad+=("E192's registration list is off its sha256")
[ "$(sha256sum $K/SHA256SUMS-e199-registration | cut -d' ' -f1)" = 4d05fe0a7e6cadb6e3a2f0bf303d5f6804345c4ce9f738033a598ae926fff35f ] || bad+=("E199's registration list is off its sha256")
pins=0
for L in tools/claims-v3/e192/SHA256SUMS-e192-registration $K/SHA256SUMS-e199-registration $K/SHA256SUMS-e199-kit $K/SHA256SUMS-e199-shared; do
  while read -r h p; do
    [ -e "$p" ] || continue
    pins=$((pins + 1))
    [ "$(sha256sum "$p" | cut -d' ' -f1)" = "$h" ] || bad+=("$p is off its pin")
  done < "$L"
done
while IFS= read -r p; do case "$p" in ''|'#'*) continue ;; esac; [ -e "$p" ] || bad+=("the synced $p is absent"); done < $K/boxfiles-e199.txt
echo "pins: $pins synced files read at their lists' sha256"
TODAY=$(TZ=America/Los_Angeles date +%F)
if [ -f build/intbits/BUILD-E199.txt ] && grep -q "^built $TODAY " build/intbits/BUILD-E199.txt; then cat build/intbits/BUILD-E199.txt
else bad+=("no build record from today (build/intbits/BUILD-E199.txt)"); fi
bash $K/preflight_e199.sh > build/intbits/preflight.txt 2>&1
grep -E '^(PLAIN|PVT)-CHAIN' build/intbits/preflight.txt
grep -q '^PLAIN-CHAIN: GO' build/intbits/preflight.txt || bad+=("the preflight's plain chain is not GO")
if [ "${#bad[@]}" -gt 0 ]; then printf 'BOXCHECK-E199 FAIL: %s\n' "$(IFS=';'; echo "${bad[*]}")"; exit 16; fi
echo "BOXCHECK-E199 OK: aifoundry1, its two cards' nodes and card 1's lock file, et-who --check answers, the reader at E191's pin, ET_DEVICES in the host, the reader and the heater (its parser), the per-sensor sampler and E191's identity module at their pins, $pins files at their pins, today's build record, the plain chain GO"

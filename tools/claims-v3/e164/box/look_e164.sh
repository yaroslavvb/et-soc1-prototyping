#!/usr/bin/env bash
# E164 box step 1 (after the approvals; READ ONLY: no device opened, no lock taken). From the Intel:
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e164/box/look_e164.sh
# Prints the host's state for the claim decision. et-who and who name people: read them, never copy names into a file or a commit.
cd ~/nekko || exit 1
date '+%F %T %Z'; uptime
boot=$(date -d "$(uptime -s)" +%s); e82=$(date -d '2026-10-31 13:45:24 PDT' +%s)
if [ "$boot" -lt "$e82" ]; then echo "identity: the host booted $(uptime -s), before E82's firmware read of 2026-10-31 13:45:24 PDT: ok"
else echo "identity: the host booted $(uptime -s), AFTER E82's firmware read: STOP (E164.md, Device commands sent)"; fi
echo "--- et-who (card 1's own lines decide: /dev/et1_*, lock:etsoc-shire1.lock; card 0 must show none of ours)"; timeout 20 et-who 2>&1 | tail -20
echo "--- logins: $(who | wc -l) (an idle login does not block, D1)"
df -h /home | tail -1
echo "--- binaries against E157's pins (harness-e164.json box_binaries_sha256)"
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem build/sparsity/kernel/sparsity.elf build/ccheck/b/host/sparsity_host \
  build/ccheck/src/host/main.cpp workloads/sparsity/host/main.cpp 2>&1
ls -la /run/lock/etsoc-shire*.lock 2>&1
echo "--- our own processes (must be none before a claim: never two of our sessions on aifoundry1)"
pgrep -u "$USER" -fa "sparsity_host|ettelem|session_e|queue_e|block_e|run_e" | head
ls tools/claims-v3/ | grep -E 'e16[0-9]|ccheck' | tr '\n' ' '; echo; ls tools/claims-v3/kinds | grep blind | tr '\n' ' '; echo
python3 --version

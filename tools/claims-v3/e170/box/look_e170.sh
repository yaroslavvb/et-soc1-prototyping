#!/usr/bin/env bash
# E170 box step 1 (READ ONLY: no device opened, no lock taken). From the Intel, through Q141(k)'s bounded runner (box/step_e170.sh look):
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e170/box/look_e170.sh
# Prints the host's state for the go decision: the host's boot against E84's identity read (it must precede 2026-10-31 15:42:00 PDT), et-who (card 0's
# own lines must be empty, and nothing of ours on card 1: E164 has ended), E164's session end, the login count, /home's room, E170's three binaries
# against their pins, the card locks, our own device processes (none), python. et-who and who name people: read them, never copy a name.
# SPDX-License-Identifier: Apache-2.0
cd ~/nekko || exit 1
date '+%F %T %Z'; uptime
boot=$(date -d "$(uptime -s)" +%s); e84=$(date -d '2026-10-31 15:42:00 PDT' +%s)
if [ "$boot" -lt "$e84" ]; then echo "host boot: $(uptime -s), before E84's identity read of 2026-10-31 15:42:00 PDT: ok"
else echo "host boot: $(uptime -s), AFTER E84's identity read: STOP (E170.md, Card 0's state: the image cannot be carried)"; fi
echo "--- et-who (card 0's lines /dev/et0_*, lock:etsoc-shire0.lock must be empty; nothing of ours on card 1)"; timeout 20 et-who 2>&1 | tail -20
echo "--- E164's session: $(grep -c 'session end' build/e164/session.log 2>/dev/null) 'session end' lines; last: $(tail -1 build/e164/session.log 2>/dev/null | cut -c1-100)"
echo "--- logins: $(who | wc -l) (an idle login does not block)"
df -h /home | tail -1
echo "--- E170's binaries against e170_common.BOX_BINARIES (4f0956ce / 990807f4 / 87c1c38c)"
sha256sum build/ccheck/b/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem-e84/ettelem 2>&1
ls -la /run/lock/etsoc-shire*.lock 2>&1
echo "--- our device processes (must be none before E170's launch: never two of our sessions on aifoundry1)"
pgrep -u "$USER" -fa "sparsity_host|ettelem|queue_e1|session_e1|run_e1|block_e1" | cut -c1-120 | head
echo "--- E170's tree: $(ls tools/claims-v3/e170 2>/dev/null | wc -l) files; build/e170: $(ls build/e170 2>/dev/null | tr '\n' ' ')"
python3 --version

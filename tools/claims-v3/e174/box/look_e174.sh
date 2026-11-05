#!/usr/bin/env bash
# E174 box step 1 (READ ONLY: no device opened, no lock taken). From the Intel, through the q142kg runbook's bounded runner (v3.1's) (box/step_e174.sh look):
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' < tools/claims-v3/e174/box/look_e174.sh
# Prints the host's state for the go decision: the host's boot against E84's identity read (it must precede 2026-10-31 15:42:00 PDT), et-who (card 0's
# own lines must be empty, and nothing of ours on card 1: E172 has ended), E172's end if its records are here, the login count, /home's room, E174's three binaries
# against their pins, the card locks, our own device processes (none), python. et-who and who name people: read them, never copy a name.
# SPDX-License-Identifier: Apache-2.0
cd ~/nekko || exit 1
date '+%F %T %Z'; uptime
boot=$(date -d "$(uptime -s)" +%s); e84=$(date -d '2026-10-31 15:42:00 PDT' +%s)
if [ "$boot" -lt "$e84" ]; then echo "host boot: $(uptime -s), before E84's identity read of 2026-10-31 15:42:00 PDT: ok"
else echo "host boot: $(uptime -s), AFTER E84's identity read: STOP (E174.md, Card 0's state: the image cannot be carried)"; fi
echo "--- et-who (card 0's lines /dev/et0_*, lock:etsoc-shire0.lock must be empty; nothing of ours on card 1)"; timeout 20 et-who 2>&1 | tail -20
echo "--- E172 (card 1, the k6 lane's kit; read its records if they are here): session.log 'session end' lines $(grep -c 'session end' build/e172/session.log 2>/dev/null); status $(cut -c1-160 build/e172/runs/status.json 2>/dev/null)"
echo "--- logins: $(who | wc -l) (an idle login does not block)"
df -h /home | tail -1
echo "--- E174's binaries against e174_common.BOX_BINARIES (4f0956ce / 990807f4 / 87c1c38c)"
sha256sum build/ccheck/b/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem-e84/ettelem 2>&1
ls -la /run/lock/etsoc-shire*.lock 2>&1
echo "--- our device processes (must be none before E174's launch: never two of our sessions on aifoundry1)"
pgrep -u "$USER" -fa "sparsity_host|ettelem|queue_e1|session_e1|run_e1|block_e1" | cut -c1-120 | head
echo "--- E174's tree: $(ls tools/claims-v3/e174 2>/dev/null | wc -l) files; build/e174: $(ls build/e174 2>/dev/null | tr '\n' ' ')"
python3 --version

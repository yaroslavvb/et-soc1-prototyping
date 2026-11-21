#!/bin/bash
# amend-e223 (Q239a) step 5: the forecasts hashed (logs/step3-sha256.txt), then FROZEN.txt (the sha256 lines and the time) and the one-line
# message for the orchestrator. Never rewrites a frozen file. Run: bash s05_frozen.sh <lane dir>
set -euo pipefail
L="${1:?lane dir}"
cd "$L"
[ ! -e FROZEN.txt ] || { echo "FROZEN.txt exists already: never rewritten"; exit 3; }
sha256sum forecasts-nominal-e223-amend1.csv forecasts-nominal-e223-amend1.json > logs/step3-sha256.txt
T3=$(TZ=America/Los_Angeles date '+%Y-%m-%d %H:%M:%S %Z')
echo "$T3 step 4: forecasts-nominal-e223-amend1.csv $(cut -c1-64 logs/step3-sha256.txt | sed -n 1p), forecasts-nominal-e223-amend1.json $(cut -c1-64 logs/step3-sha256.txt | sed -n 2p) (written 02:38:24 PST by s04_write.py in a slot, 2085 rows = 695 cases x 3 columns, mode 444) hashed rc=0" >> logs/progress.txt
sha256sum -c logs/step2-sha256.txt > /dev/null
TF=$(TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z')
{
  echo "# amend-e223 (round Q239a): FROZEN at $TF (Pacific): DATED AMENDMENT 1 to decl-e223's declaration of the lab's BLIND test of E223 (its FROZEN.txt 5551c2d7b7b6b5bc..., posted #16 02:23:46 PST) and the amendment's nominal forecasts, before any E223 datum"
  echo "# the freeze line (post these on #16): the amendment, then its nominal forecasts"
  cat logs/step2-sha256.txt logs/step3-sha256.txt
  echo "# the order: the amendment written and hashed Sat 21 Nov 2026 02:36:29 PST (logs/step2-sha256.txt), then the nominal forecasts made 02:36:41-02:37:56 PST, written 02:38:24 PST and hashed $T3 (logs/step3-sha256.txt), then this file"
  sha256sum logs/step2-sha256.txt logs/step3-sha256.txt work/step3/fc-amend1.json work/step2/twin-keys-amend1.json work/step1/frozen-checks.json
  echo "# adds, REPORTED and deciding nothing: 'MM1-v3.2 + mesh' (Q238 mask-mesh, FROZEN.txt 487188c7f0ddce24..., posted #1.30.1.2.1.1.1.1.1.1.2 02:23:42 PST) and 'MM1-v3.2 + AF4 + mesh' (by construction, no refit; = mesh at every E223 case); 'MM1-v3.2 + mask-ceiling', a REPORTED reference, never a model candidate (Q238 mask-ceiling, the posted FROZEN.txt 1649ba5ba69e1061... of 02:21:44 PST; every file called equal under its on-disk bf6e2d9643bd8869... too)"
  echo "# scored exactly as the declaration scores 'MM1-v3.2 + posimb-mask': on the placement class (PLACE, 421 cases) each vs MM1-v3.2 on H1, H2, H3, H5 by the exact sign test, per card and pooled; the subset cases (513), MASKE221 (353) and each held-out set REPORTED; by construction: AF4 + mesh = mesh, the reference's H2 = MM1-v3.2's (NO DATA), E1 = MM1-v3.2's for all three"
  echo "# 695 cases x 3 columns, all IN the domain (mesh in scope 513, the reference 454); no E223 datum read by this lane (no EE/sessions/, no ssh, no E223 data folder); /usr/bin/python3 3.12.3"
} > FROZEN.txt
chmod 444 FROZEN.txt
FS=$(sha256sum FROZEN.txt | cut -c1-64)
mkdir -p msg
echo "$TF amend-e223 FROZEN (DATED AMENDMENT 1 to decl-e223's blind test of E223: 'MM1-v3.2 + mesh' and 'MM1-v3.2 + AF4 + mesh' REPORTED, 'MM1-v3.2 + mask-ceiling' a REPORTED reference; scored as the declaration's posimb-mask; before any E223 datum): FROZEN.txt sha256 $FS" > msg/to-orchestrator-frozen.txt
echo "$(TZ=America/Los_Angeles date '+%Y-%m-%d %H:%M:%S %Z') step 5: FROZEN.txt written ($TF) sha256 $FS; msg/to-orchestrator-frozen.txt written rc=0" >> logs/progress.txt
cat FROZEN.txt
echo "----"
cat msg/to-orchestrator-frozen.txt

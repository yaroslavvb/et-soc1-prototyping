#!/usr/bin/env bash
# E184 (Q154), kit note 2 (KIT.md.dated-note-2.md section 5; kit v5's lesson "the readers' interpreter pinned"): interp_check_e184_v2.sh (v2,
# which stays as committed) on kit note 2's desk readers: reduce_e184_v3.py and score_e184_v3.py give the same bytes under the pinned
# /usr/bin/python3 (3.9) and the PATH's python3 (3.13 on the Intel), on one synthetic session of each arm (fake_card_e184_v2.py, seed 11 and
# 21, partial dips at 0.3% in arm S so A2-5's rule runs), with arm S's end config read emptied and step 7's read beside it, so A3-3's
# replacement (an ISO time with its offset, read back as epoch seconds) runs under both.
#   bash tools/claims-v3/e184/interp_check_e184_v3.sh <scratch dir>        (prints "INTERP-E184-V3 SAME" or "DIFFERS"; exit 0 or 1)
# SPDX-License-Identifier: Apache-2.0
set -u
K=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?a scratch directory outside the repository}
mkdir -p "$S"
/usr/bin/python3 -B "$K/fake_card_e184_v2.py" "$S/raw" --arm S --seed 11 --dip-rate 0.003 && /usr/bin/python3 -B "$K/fake_card_e184_v2.py" "$S/raw" --arm B --seed 21 || exit 1
L3=$S/raw/aifoundry3/logs; T0=1794500000
: > "$L3/config-S-t$T0-end.json"
echo "2026-11-12T08:14:00-08:00" > "$L3/config-S-t$T0-start.json.time"
echo "2026-11-12T10:23:20-08:00" > "$L3/config-S-t$T0-end.json.time"
echo '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600,"synthetic":true}' > "$L3/config-S-step7-1794507920.json"
sums=()
for py in /usr/bin/python3 python3; do
  tag=$($py -B -c 'import sys; print("%d.%d" % sys.version_info[:2])')
  $py -B "$K/reduce_e184_v3.py" "$S/raw" --arm S > "$S/red-s-$tag.json" && $py -B "$K/reduce_e184_v3.py" "$S/raw" --arm B > "$S/red-b-$tag.json" || exit 1
  $py -B "$K/score_e184_v3.py" --s "$S/red-s-$tag.json" --b "$S/red-b-$tag.json" --out "$S/scored-$tag" > /dev/null || exit 1
  dep=$($py -B -c 'import json, sys; print(len(json.load(open(sys.argv[1]))["session"]["departures"]))' "$S/red-s-$tag.json")
  line=$(cat "$S/red-s-$tag.json" "$S/red-b-$tag.json" "$S/scored-$tag/scored-e184-v3.json" "$S/scored-$tag/scored-e184-v3.md" | shasum -a 256 | cut -c1-16)
  echo "python $tag: reduced S (A3-3 departures: $dep), reduced B, scored json and md: sha256 $line"
  sums+=("$line")
done
[ "${sums[0]}" = "${sums[1]}" ] && { echo "INTERP-E184-V3 SAME"; exit 0; }
echo "INTERP-E184-V3 DIFFERS"; exit 1

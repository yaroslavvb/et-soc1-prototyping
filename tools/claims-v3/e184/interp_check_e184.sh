#!/usr/bin/env bash
# E184 (Q153, the kit; kit v5's lesson "the readers' interpreter pinned"): the reducer and the scorer give the same bytes under the pinned
# /usr/bin/python3 (3.9) and the PATH's python3 (3.13 on the Intel), on one synthetic session of each arm (fake_card_e184.py, seed 11 and 21).
#   bash tools/claims-v3/e184/interp_check_e184.sh <scratch dir>        (prints "INTERP-E184 SAME" or "DIFFERS"; exit 0 or 1)
# SPDX-License-Identifier: Apache-2.0
set -u
K=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=${1:?a scratch directory outside the repository}
mkdir -p "$S"
/usr/bin/python3 -B "$K/fake_card_e184.py" "$S/raw" --arm S --seed 11 && /usr/bin/python3 -B "$K/fake_card_e184.py" "$S/raw" --arm B --seed 21 || exit 1
sums=()
for py in /usr/bin/python3 python3; do
  tag=$($py -c 'import sys; print("%d.%d" % sys.version_info[:2])')
  $py -B "$K/reduce_e184.py" "$S/raw" --arm S > "$S/red-s-$tag.json" && $py -B "$K/reduce_e184.py" "$S/raw" --arm B > "$S/red-b-$tag.json" || exit 1
  $py -B "$K/score_e184.py" --s "$S/red-s-$tag.json" --b "$S/red-b-$tag.json" --out "$S/scored-$tag" > /dev/null || exit 1
  line=$(cat "$S/red-s-$tag.json" "$S/red-b-$tag.json" "$S/scored-$tag/scored-e184.json" "$S/scored-$tag/scored-e184.md" | sha256sum | cut -c1-16)
  echo "python $tag: reduced S, reduced B, scored json and md: sha256 $line"
  sums+=("$line")
done
[ "${sums[0]}" = "${sums[1]}" ] && { echo "INTERP-E184 SAME"; exit 0; }
echo "INTERP-E184 DIFFERS"; exit 1

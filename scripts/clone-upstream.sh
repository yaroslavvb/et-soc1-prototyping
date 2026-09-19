#!/usr/bin/env bash
# Clone the upstream ET repositories into external/, checked out at the commits this repo's results were
# produced with. Repos already present are left alone, with a note if they sit at a different commit.
# UPSTREAM_LATEST=1 keeps the branch tips instead of the pins.
set -euo pipefail
EXT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/external"
mkdir -p "$EXT"
clone() {  # url dir commit [branch]
  local url=$1 dir=$2 pin=$3 branch=${4:-} head
  if [[ -d "$EXT/$dir/.git" ]]; then
    head=$(git -C "$EXT/$dir" rev-parse HEAD)
    [[ "$head" == "$pin" ]] || echo "note: external/$dir is at ${head:0:9}; the pinned commit is ${pin:0:9}" >&2
    return
  fi
  git clone ${branch:+-b "$branch"} "$url" "$EXT/$dir"
  if [[ -z "${UPSTREAM_LATEST:-}" ]]; then
    git -C "$EXT/$dir" -c advice.detachedHead=false checkout -q "$pin"
  fi
}
# Firmware, runtime, sys_emu and gp-sdk (built into /opt/et by scripts/provision-vm.sh, with patches/ applied).
clone https://github.com/aifoundry-org/et-platform.git et-platform 836a4ab600e93c3059bb58c898edbc37744cd8d0
# The manuals: PRM, datasheet, errata.
clone https://github.com/aifoundry-org/et-man.git et-man 5fe80a34e9e1b799d0378968c5f76352b4ba7e55
# RTL and micro-architecture docs (the on-chip communication report cites both).
clone https://github.com/openhwfoundation/core-et.git core-et b38a1a31da67efe00c61e983e64b892c58080115 erbium
# marty1885's minimal host + kernel project: the template for workloads/, and a quick hello world on a card.
clone https://github.com/marty1885/et-testdrive.git et-testdrive c2035c57917206f2f286a87cf569b5cd51ec385d
# marty1885's NoC topology scanner, the source of the shire map the on-chip communication report checks.
clone https://github.com/marty1885/etTopoScan.git etTopoScan ee3e9f2741b9f4fbce958520767630c53f057631

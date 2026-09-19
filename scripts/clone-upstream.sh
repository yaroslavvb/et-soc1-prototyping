#!/usr/bin/env bash
# Clone the upstream ET repositories into external/ (skips ones already present).
set -euo pipefail
EXT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/external"
mkdir -p "$EXT"
clone() {  # url dir [branch]
  [[ -d "$EXT/$2/.git" ]] && return
  git clone ${3:+-b "$3"} "$1" "$EXT/$2"
}
clone https://github.com/aifoundry-org/et-platform.git et-platform
clone https://github.com/aifoundry-org/et-man.git et-man
clone https://github.com/openhwfoundation/core-et.git core-et erbium

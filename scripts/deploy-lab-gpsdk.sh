#!/usr/bin/env bash
# Build this repo's gp-sdk kernels and launchers (kernels/, launchers/, e.g. mmbench) on an
# AI Foundry lab machine, against that machine's own /opt/et.
#   scripts/deploy-lab-gpsdk.sh aifoundry2
#
# The lab machines' /opt/et is et-platform 353f20e (Dec 2025), older than the gp-sdk in
# external/et-platform. Current gp-sdk requires Erbium components that install lacks. So
# this script:
#   1. copies the repo's sources (not build/ or external/) to ~/nekko on the host
#   2. exports gp-sdk at 06605ab, the last version before Erbium, from external/et-platform,
#      applies patches/lab-gp-sdk-06605ab.patch (see patches/README.md), and installs the
#      result at ~/nekko/external/et-platform/gp-sdk, where the Makefile looks for it
#   3. builds kernels and launchers there with nice and -j4, because the machines are shared
# Then, on the host (check that the card is free first; see docs/getting-started.md):
#   cd ~/nekko && make mmbench-check DEVICE=silicon && make bench-power
set -euo pipefail
host=${1:?usage: $0 <host>}
GPSDK_COMMIT=06605ab8230f56440f3a52ba248363122e1ad949
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ETP=external/et-platform
[[ -d $ETP/.git ]] || { echo "no $ETP: run scripts/clone-upstream.sh first" >&2; exit 1; }
git -C "$ETP" cat-file -e "$GPSDK_COMMIT^{commit}" 2>/dev/null || git -C "$ETP" fetch -q origin "$GPSDK_COMMIT"

# macOS bsdtar would otherwise add AppleDouble files and xattr headers that GNU tar complains about.
tar_create() {
  if tar --version 2>/dev/null | grep -q bsdtar; then
    COPYFILE_DISABLE=1 tar --no-xattrs --no-mac-metadata "$@"
  else
    tar "$@"
  fi
}

echo "== copying sources to $host:~/nekko"
git ls-files -z --cached --others --exclude-standard |
  tar_create --null -T - -czf - |
  ssh -o BatchMode=yes "$host" 'mkdir -p ~/nekko && tar xzf - -C ~/nekko'

echo "== installing gp-sdk ${GPSDK_COMMIT:0:7} + patches/lab-gp-sdk-06605ab.patch"
git -C "$ETP" archive --format=tar "$GPSDK_COMMIT" gp-sdk |
  ssh -o BatchMode=yes "$host" 'set -e
    d=~/nekko/external/et-platform
    mkdir -p "$d" && rm -rf "$d/gp-sdk" && tar xf - -C "$d"
    cd "$d" && patch -p1 -s --no-backup-if-mismatch < ~/nekko/patches/lab-gp-sdk-06605ab.patch'

echo "== building on $host (nice, -j4)"
ssh -o BatchMode=yes "$host" 'set -e
  v=$(grep -m1 -o "PACKAGE_VERSION \"[^\"]*\"" /opt/et/lib/cmake/runtime/runtimeConfigVersion.cmake || true)
  echo "/opt/et runtime: $v"
  [[ $v == *\"0.19.0\"* ]] || echo "warning: the patch was made for runtime 0.19.0 (et-platform 353f20e)" >&2
  cd ~/nekko
  rm -rf build/kernels build/launchers && mkdir -p build
  nice -n 10 make kernels launchers JOBS=4 > build/lab-build.log 2>&1 || { tail -30 build/lab-build.log; exit 1; }
  ls -la build/kernels/nekko/*.elf build/launchers/*_launcher
  echo "~/nekko uses $(du -sh ~/nekko | cut -f1) on $(hostname)"'

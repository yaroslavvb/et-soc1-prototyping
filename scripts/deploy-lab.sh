#!/usr/bin/env bash
# Copy a workload's sources to an AI Foundry lab machine and build it there, against that
# machine's own /opt/et (x86_64, and its ET install can differ from the laptop VM's).
#   scripts/deploy-lab.sh aifoundry3 workloads/sgemm
# Then run it on the card with a hard time cap, e.g.
#   ssh aifoundry3 'cd ~/nekko/build/sgemm && timeout 10 host/sgemm_host -n 512'
# The cards are shared: check `uptime` / `ps` for other users first, keep each run short
# (device held < 10 s), and keep the footprint small (sources only, nice -j4 build).
set -euo pipefail
host=${1:?usage: $0 <host> <workload-dir>}
dir=${2:?usage: $0 <host> <workload-dir>}
dir=${dir%/}
name=$(basename "$dir")
cd "$(dirname "${BASH_SOURCE[0]}")/.."
[[ -f "$dir/CMakeLists.txt" ]] || { echo "$dir has no CMakeLists.txt" >&2; exit 1; }

COPYFILE_DISABLE=1 tar --no-xattrs --no-mac-metadata -czf - "$dir" |
  ssh -o BatchMode=yes "$host" "set -e
    mkdir -p ~/nekko && tar xzf - -C ~/nekko
    cd ~/nekko
    nice -n 10 cmake -S '$dir' -B 'build/$name' -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > 'build-$name.log' 2>&1 ||
      { tail -30 'build-$name.log'; exit 1; }
    nice -n 10 cmake --build 'build/$name' -j4 >> 'build-$name.log' 2>&1 || { tail -30 'build-$name.log'; exit 1; }
    grep -E 'warning:' 'build-$name.log' || true
    rm -f 'build-$name.log'
    echo \"built ~/nekko/build/$name on \$(hostname); ~/nekko uses \$(du -sh ~/nekko | cut -f1)\""

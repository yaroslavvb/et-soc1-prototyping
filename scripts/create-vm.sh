#!/usr/bin/env bash
# Create the `et` Lima VM (Ubuntu 24.04, arm64, Apple Virtualization.framework)
# used to build and run the ET-SoC-1 software stack on macOS, then provision it.
# The repo is mounted read-write at the same path inside the VM.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VM="${ET_VM:-et}"

command -v limactl >/dev/null || brew install lima
if ! limactl list -q | grep -qx "$VM"; then
  limactl start --name="$VM" --tty=false \
    --cpus "${VM_CPUS:-16}" --memory "${VM_MEMORY_GB:-48}" --disk "${VM_DISK_GB:-200}" \
    --vm-type vz --mount-only "$REPO_ROOT:w" template:ubuntu-24.04
fi
"$REPO_ROOT/scripts/clone-upstream.sh"
cd "$REPO_ROOT" && scripts/vm scripts/provision-vm.sh all

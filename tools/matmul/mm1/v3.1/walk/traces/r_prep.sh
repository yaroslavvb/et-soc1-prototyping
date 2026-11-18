#!/bin/bash
# v31-trace (Q217), run ON aifoundry3 (sent by a3_send.sh only while no lane books it): unpack the payload into ~/claude/work/q217-v31-trace,
# check its sums, copy the four built files (rgm136's and rgm211's host and kernel ELF, built there by kit-e211 from the registered trees)
# read-only from kit-e211's build tree into bin/, and check each kernel's .text and whole-ELF sha256 against E211's pins (kernel-e211.json);
# read the installed sys_emu's identity. No build, no simulator run, no device, nothing written outside ~/claude/work/q217-v31-trace.
set -u
D="$HOME/claude/work/q217-v31-trace"
T="$HOME/claude/work/q217-v31-trace.tgz"
[ -f "$T" ] || { echo "no payload tgz"; exit 3; }
if [ ! -d "$D" ]; then mkdir -p "$D" && tar xzf "$T" -C "$D" --strip-components=1 || exit 3; fi
cd "$D" || exit 3
sha256sum -c --quiet SHA256SUMS && echo "payload sums OK ($(wc -l < SHA256SUMS) files)" || { echo "PAYLOAD SHA MISMATCH"; exit 4; }
K="$HOME/claude/work/q204-kit-e211/build"
mkdir -p bin/rgm136 bin/rgm211
for e in rgm136 rgm211; do
  [ -f "bin/$e/sparsity_host" ] || cp "$K/e211$e/host/sparsity_host" "bin/$e/sparsity_host" || exit 5
  [ -f "bin/$e/sparsity.elf" ] || cp "$K/e211$e/kernel/sparsity.elf" "bin/$e/sparsity.elf" || exit 5
done
OC=/opt/et/bin/riscv64-unknown-elf-objcopy
pin136_text=61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763
pin211_text=82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069
for e in rgm136 rgm211; do
  "$OC" -O binary -j .text "bin/$e/sparsity.elf" "bin/$e/text.bin" || exit 6
  t=$(sha256sum "bin/$e/text.bin" | cut -d' ' -f1)
  want=$([ $e = rgm136 ] && echo $pin136_text || echo $pin211_text)
  [ "$t" = "$want" ] && echo "$e .text $t = E211's pin" || { echo "$e .text $t != pin $want"; exit 7; }
  echo "$e elf $(sha256sum "bin/$e/sparsity.elf" | cut -d' ' -f1) ($(stat -c %s "bin/$e/sparsity.elf") B); host $(sha256sum "bin/$e/sparsity_host" | cut -d' ' -f1)"
done
echo "sys_emu: $(ls -la /opt/et/bin/sys_emu | awk '{print $5, $6, $7, $8}') sha256 $(sha256sum /opt/et/bin/sys_emu | cut -c1-16)"
strings /opt/et/bin/sys_emu | grep -E 'Log given Threads|SDK_RELEASE|Redirect log output|log_at_pc' | head -5
echo "python $(/usr/bin/python3 -c 'import sys;print(sys.version.split()[0])'); nproc $(nproc); $(free -g | awk '/Mem:/{print "mem total", $2, "GB, available", $7, "GB"}'); load $(cut -d' ' -f1-3 /proc/loadavg)"
df -h "$HOME" | tail -1
command -v et-who >/dev/null && timeout 20 et-who 2>&1 | head -3
ls -la "$D" bin/*

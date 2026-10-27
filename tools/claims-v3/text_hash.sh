#!/usr/bin/env bash
# The identity of what actually ran: for every binary named, the sha256 of the whole file and of its .text
# section, and — for an enercat host binary — of the device kernel ELF it launches (../kernel/enercat.elf,
# KERNEL_ELF in host/CMakeLists.txt) and of that ELF's .text.
#
#   bash tools/claims-v3/text_hash.sh <binary> [binary...]
#
# Why .text and not the file: the host binaries are built on each box against its own /opt/et, so two boxes'
# files differ in paths and build ids while the code that runs on the card can be identical. A kernel's .text is
# what the minions execute, and E61's trap (docs/findings/14-card-behaviour.md: a kernel's issue rate is set by
# where its loop sits) makes it the thing to compare between two builds before their numbers are compared.
set -u
# The device kernel's code is not in a section called .text (crt.S puts _start in .text.init and the linker
# script keeps .text.*), so an `--only-section=.text` of it hashes nothing: the sha256 of the empty string,
# e3b0c442..., which would compare equal between two different kernels. Hash the DISASSEMBLY, which is the code
# that runs whatever the sections are called, and keep the plain .text hash beside it when it is not empty.
EMPTY=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
hash_one() {
  local f=$1 kind=$2 t= d= od=objdump
  [ -e "$f" ] || { echo "MISSING $kind $f"; return; }
  echo "file   $kind $(sha256sum "$f" | cut -d' ' -f1) $(stat -c %s "$f" 2>/dev/null || stat -f %z "$f") $f"
  # a device kernel is RISC-V: the host objdump cannot read it, so prefer the cross objdump when there is one
  case "$kind" in kernel) [ -x /opt/et/riscv64-unknown-elf/bin/objdump ] && od=/opt/et/riscv64-unknown-elf/bin/objdump ;; esac
  if command -v objcopy > /dev/null 2>&1; then
    t=$(objcopy -O binary --only-section=.text "$f" /dev/stdout 2>/dev/null | sha256sum | cut -d' ' -f1)
    [ -n "$t" ] && [ "$t" != "$EMPTY" ] && echo "text   $kind $t $f"
  fi
  if command -v "$od" > /dev/null 2>&1 || [ -x "$od" ]; then
    # drop objdump's first two lines, which name the file
    d=$("$od" -d "$f" 2>/dev/null | tail -n +3 | sha256sum | cut -d' ' -f1)
    [ -n "$d" ] && echo "code   $kind $d $f"
  fi
}
for b in "$@"; do
  hash_one "$b" host
  k=$(dirname "$b")/../kernel/enercat.elf
  [ -e "$k" ] && hash_one "$k" kernel
done

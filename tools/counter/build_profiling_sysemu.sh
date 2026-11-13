#!/usr/bin/env bash
# The profiling simulator: sw-sysemu at the lab cards' et-platform commit (353f20e), built as the installed one was
# (no optimisation flags, no debug info: CMAKE_BUILD_TYPE empty) plus the per-block profile, into a NEW folder, and a
# shadow prefix beside it in which bin/sys_emu and lib/libsw-sysemu.a are this build and every other entry links to
# the installed ET tree. Nothing outside the new folder is written; nothing here opens a device.
#
#   on the Intel (or any clone with external/et-platform), the source:
#     git -C external/et-platform archive --format=tar --prefix=et-platform-353f20e/ 353f20e98 sw-sysemu \
#       | gzip -n > sw-sysemu-353f20e.tar.gz        # the tar (before gzip) has sha256 TAR_SHA256 below
#   on a lab box (Linux, the ET install in /opt/et, cmake >= 3.21, GCC 13):
#     bash tools/counter/build_profiling_sysemu.sh sw-sysemu-353f20e.tar.gz ~/q166-counter-b/official [/opt/et]
#
# Why each option: PROFILING=ON only adds sys_emu/profiling.cpp to the sources (CMakeLists.txt line 179); the hooks
# are compiled in by two defines the CMake build never sets (the old sys_emu/Makefile sets both when PROFILING=1):
# BEMU_PROFILING makes every taken branch, jump, trap and return call profiling_write_pc (insn_util.h), and
# SYSEMU_PROFILING adds the -dump_prof option and the dump at the end (sys_emu.cpp, sys_emu_parse_args.cpp,
# SysEmuImp.cpp). A Release build of 353f20e does not link (mmu.cpp's `inline` effective_execution_mode, fixed
# upstream in d4d830f00), and the installed binary carries the un-inlined stubs of a build without -O, so this one
# has no -O either. -fmacro-prefix-map takes the build folder out of the assert() strings, so the binary's sha256
# does not depend on where it was built.
#
# The runtime links the emulator INTO the host program (libsw-sysemu.a; sys_emu's executable is not used by
# `--sysemu`), so a host must be built against the shadow prefix to profile: cmake ... -DCMAKE_PREFIX_PATH=<out>/prefix.
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
TAR_SHA256=737a1166b615a3b4e3ac48e26a1ecc1e5b35ab5c286abcdc291f838851178451   # git archive of 353f20e98 sw-sysemu, prefix et-platform-353f20e/
tarball=${1:?usage: build_profiling_sysemu.sh <sw-sysemu tar.gz> <new folder> [et prefix]}
out=${2:?usage: build_profiling_sysemu.sh <sw-sysemu tar.gz> <new folder> [et prefix]}
etp=${3:-/opt/et}
[ -e "$out" ] && { echo "build_profiling_sysemu: $out exists; give a new folder" >&2; exit 2; }
[ -x "$etp/bin/sys_emu" ] && [ -f "$etp/lib/libsw-sysemu.a" ] || { echo "no ET install at $etp" >&2; exit 2; }
if command -v et-who > /dev/null; then
  et-who 2>&1 | grep -q -i 'No process holds an ET-SoC-1 device node or card lock' || {
    echo "build_profiling_sysemu: a card on this host is held (et-who): build later" >&2; exit 3; }
fi
mkdir -p "$out/src" "$out/logs"
out=$(cd "$out" && pwd)
tar_sum=$(gzip -dc "$tarball" | sha256sum | cut -d' ' -f1)
echo "source tar sha256 $tar_sum"
[ "$tar_sum" = "$TAR_SHA256" ] || { echo "build_profiling_sysemu: not the 353f20e sw-sysemu export" >&2; exit 4; }
tar -xzf "$tarball" -C "$out/src"
src="$out/src/et-platform-353f20e/sw-sysemu"
flags="-DBEMU_PROFILING -DSYSEMU_PROFILING -fmacro-prefix-map=$out/src/=/"
cmake -S "$src" -B "$out/build" -DCMAKE_BUILD_TYPE= -DPROFILING=ON "-DCMAKE_CXX_FLAGS=$flags" -Wno-dev \
  > "$out/logs/configure.log" 2>&1
nice -n 19 cmake --build "$out/build" --target sys_emu -j4 > "$out/logs/build.log" 2>&1
# the shadow prefix: real bin/ and lib/ folders of links, with this build's two files in them
P="$out/prefix"
mkdir -p "$P/bin" "$P/lib"
for e in "$etp"/*; do b=$(basename "$e"); case "$b" in bin|lib) ;; *) ln -s "$e" "$P/$b" ;; esac; done
for e in "$etp"/bin/*; do b=$(basename "$e"); [ "$b" = sys_emu ] || ln -s "$e" "$P/bin/$b"; done
for e in "$etp"/lib/*; do b=$(basename "$e"); [ "$b" = libsw-sysemu.a ] || ln -s "$e" "$P/lib/$b"; done
install -m 755 "$out/build/sys_emu" "$P/bin/sys_emu"
install -m 644 "$out/build/libsw-sysemu.a" "$P/lib/libsw-sysemu.a"
# what differs from the installed build
"$etp/bin/sys_emu" -h > "$out/logs/installed-help.txt" 2>&1 || true
"$P/bin/sys_emu" -h > "$out/logs/profiling-help.txt" 2>&1 || true
diff "$out/logs/installed-help.txt" "$out/logs/profiling-help.txt" > "$out/logs/help.diff" || true
ar t "$etp/lib/libsw-sysemu.a" | sort > "$out/logs/ar-installed.txt"
ar t "$P/lib/libsw-sysemu.a" | sort > "$out/logs/ar-profiling.txt"
diff "$out/logs/ar-installed.txt" "$out/logs/ar-profiling.txt" > "$out/logs/ar.diff" || true
{
  echo "source: et-platform 353f20e982f4efd99019d04f8022681cc727c4f2, sw-sysemu tree 877c09cf1c0c4c7d2a7bd9d56641cd4536640287"
  echo "source tar sha256: $tar_sum"
  echo "cmake: $(cmake --version | head -1); compiler: $(c++ --version | head -1)"
  echo "options: CMAKE_BUILD_TYPE= PROFILING=ON CMAKE_CXX_FLAGS='-DBEMU_PROFILING -DSYSEMU_PROFILING -fmacro-prefix-map=<out>/src/=/'"
  sha256sum "$P/bin/sys_emu" "$P/lib/libsw-sysemu.a" | sed "s#$out/##"
  echo "help diff (installed -> profiling):"; sed 's/^/  /' "$out/logs/help.diff"
  echo "archive members diff:"; sed 's/^/  /' "$out/logs/ar.diff"
} | tee "$out/BUILD-INFO.txt"

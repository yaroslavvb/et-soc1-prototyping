#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): THE BUILD ON THE BOX, run by step 6 (rb/s08_build_e200.sh) as k6's
# detached job under `timeout 900` (no -k: nothing of this kit is ever sent a KILL), from E200's root on aifoundry2 (<box tree>/build/
# claims-v3/aifoundry2/e200, the synced files at their repository paths: a build folder of ours, never the box tree's own files). E197's
# build (tools/claims-v3/e197/build_e197.sh, unchanged beside it) on this box, with E200's runner (E200.md 19.1). It never opens a device,
# takes no card lock and sends no device command:
#   1. the harness: every synced file at its pin (harness_e200.py --box), E197's registration's 35 among them;
#   2. the toolchain's versions, then E197's proposal's own build as its BUILD.md and E197.md 17.3 give it: `cmake -S <E197's proposal/src>
#      -B build/regfile -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev`, `cmake --build build/regfile -j4`, nice 10, into E200's root only (a new
#      start removes build/regfile first; nothing is written into proposal/src: the harness is read again after the build);
#   3. E197'S OWN CHECKS (E197.md 11; E200.md 13: a failure is "no sitting: no data, never a failed check"): `make_images.py --check .`
#      (34 kinds, 17 forms, OK) and `check_elf.py` on the box's kernel (17 loops, every one 131 instructions, the frame word for word, bad 0);
#   4. THE ELF REPORT: the kernel ELF's and its .text's sha256 beside E197's desk build's on this very box (E197.md 17.5: feafba8d...,
#      ce8c93c6...), SAME or DIFFERENT, never a gate; path strings counted;
#   5. THE HOST'S TABLE: `regfile_host --list --json` and `--list` (no device) byte for byte E197's desk/host-list-e197.jsonl and .txt (the
#      host's --list against E197.md 2, E200.md 13): HOST-TABLE SAME, else no sitting;
#   6. THE HOST READ BY ITS BEHAVIOUR, four refusals BEFORE the device layer, with ET_DEVICES=99 and an unreadable --kernel as two barriers
#      besides the refusal itself (E197's four, as main.cpp writes them);
#   7. THE HOST'S SIGNAL HANDLING RE-READ ON THIS BUILD (reported, never a gate: a host that does not end on TERM is the hang watch's);
#   8. E200'S RUNNER (E200.md 4, W1): E197's lab runner (lab/run_trains.py, at E197's registration's sha256) with lab/run_trains-e200-W1.diff
#      (at its sha256 24224f12...) applied by `patch -o` into build/run_trains-e200.py: at E200's runner sha256 8774027b..., two lines
#      changed, each the window, else no sitting (E200.md 13: "the runner made from W1 is not at its sha256");
#   9. THE SESSION'S DRY LISTINGS WITH THIS HOST AND E200'S RUNNER: the reference session's own DRY mode (E197's run_session.sh with E200's
#      runner, from a scratch folder holding the four files, H this host) for the full, short and ext plans, each E197's registered listing
#      desk/dry-e197-<plan>.txt but W1 (check_e200.py drycmp: every device call with --window 320000000, none with 240000000, and line for
#      line E197's once the window is written back: LISTING SAME x3, 429, 331 and 277 device calls), else no sitting;
#  10. the reader the session uses, <box tree>/build/ettelem-hpl/ettelem behind E200's guard: present, executable and at its pin
#      (77a46171...: this card's reader since E136; E194's pin), else no sitting (never run here);
#  11. on every gate passed: build/regfile-built.txt (REGFILE-BUILT, the kernel's, .text's, host's, runner's and reader's sha256), which
#      the session checks its host against; a start removes the last record first, so no session runs on a failed start's binaries.
# Prints COMPILER / ELF / CHECK / HOST-TABLE / HOST-BEHAVIOUR / SIGNAL-READ / RUNNER / LISTING / SAMPLER lines, then REGFILE-BUILT rc=0, or
# REGFILE-BUILD-FAILED <why> (exit 1). E200_ET_BIN (default /opt/et/bin) names the toolchain's folder; E200_READER_SHA256 is read only
# with E200_DESKTEST=1 (the desk tests' stand-in reader).
#   bash <R>/tools/claims-v3/e200/build_e200.sh
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
KIT=$RR/tools/claims-v3/e200
K197=$RR/tools/claims-v3/e197
SRC=$K197/proposal/src
B=$RR/build/regfile
BUILT=$RR/build/regfile-built.txt
X=${E200_ET_BIN:-/opt/et/bin}
H=$B/host/regfile_host
K=$B/kernel/regfile.elf
DESK_ELF=feafba8d819cb4cb53e5db82f3d726ded67008ab279c9933e22e25dabad1c464
DESK_TEXT=ce8c93c6a79781dd4fb295bdf221a8befad33fd359f1c5caf608650cf2e919bb
W1=$KIT/lab/run_trains-e200-W1.diff
W1_SHA=24224f12eea201614358a40272525825e81dd1d9376912b6d3c65ee36f203349
RUNNER_SHA=8774027b4bba78c6b532988c46446987f75eec6d32985bd7b400cbb963eb5a41
SBIN=build/ettelem-hpl/ettelem
SBIN_SHA=77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5
[ "${E200_DESKTEST:-}" = 1 ] && SBIN_SHA=${E200_READER_SHA256:-$SBIN_SHA}
fail() { echo "REGFILE-BUILD-FAILED $*"; exit 1; }
echo "E200 build on $(hostname), $(TZ=America/Los_Angeles date '+%F %T %Z'), root $RR"
[ "$RR" = build/claims-v3/aifoundry2/e200 ] || fail "E200's root must be build/claims-v3/aifoundry2/e200 in the box tree, not '$RR'"
mkdir -p "$RR/build" || fail "cannot make $RR/build"
rm -f "$BUILT"
python3 -I -B "$KIT/harness_e200.py" --box --root "$RR" | tail -n 1
python3 -I -B "$KIT/harness_e200.py" --box --root "$RR" > /dev/null || fail "the harness: a synced file is not at its pin"
echo "COMPILER cmake: $(cmake --version 2>&1 | head -n 1)"
echo "COMPILER riscv gcc: $("$X/riscv64-unknown-elf-gcc" --version 2>&1 | head -n 1)"
echo "COMPILER host c++: $(c++ --version 2>&1 | head -n 1)"
echo "COMPILER $(python3 --version 2>&1); $(patch --version 2>&1 | head -n 1)"
[ -d "$B" ] && rm -rf "${R:?}/build/regfile"
nice -n 10 cmake -S "$SRC" -B "$B" -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > "$RR/build/cmake-configure.txt" 2>&1 || fail "cmake configure (build/cmake-configure.txt)"
nice -n 10 cmake --build "$B" -j4 > "$RR/build/cmake-build.txt" 2>&1 || fail "cmake build (build/cmake-build.txt)"
echo "COMPILER warnings in the build's output: $(grep -c 'warning:' "$RR/build/cmake-build.txt")"
[ -f "$K" ] || fail "no kernel ELF at $K"
[ -x "$H" ] || fail "no host at $H"
python3 -I -B "$KIT/harness_e200.py" --box --root "$RR" > /dev/null || fail "the harness after the build: a synced file changed"
( cd "$SRC" && python3 -I -B make_images.py --check . ) > "$RR/build/make-images-check.txt" 2>&1
echo "CHECK make_images.py --check: $(tail -n 1 "$RR/build/make-images-check.txt" | cut -c1-120)"
tail -n 1 "$RR/build/make-images-check.txt" | grep -q '^check: 34 kinds, 17 forms, OK' || fail "make_images.py --check (build/make-images-check.txt): no sitting (E200.md 13)"
python3 -I -B "$SRC/check_elf.py" "$K" > "$RR/build/check-elf.txt" 2>&1; ce=$?
echo "CHECK check_elf.py: $(tail -n 1 "$RR/build/check-elf.txt" | cut -c1-120) (rc $ce)"
[ "$ce" -eq 0 ] && tail -n 1 "$RR/build/check-elf.txt" | grep -q '^loops 17 (forms 17), frame 00150513 c03026f3 dfc6ece3, bad 0$' ||
  fail "check_elf.py (build/check-elf.txt): no sitting (E200.md 13)"
python3 -I -B "$KIT/harness_e200.py" --box --root "$RR" > /dev/null || fail "the harness after the request's checks: a synced file changed"
kh=$(sha256sum "$K" | cut -d' ' -f1)
T=$RR/build/regfile-text.bin
"$X/riscv64-unknown-elf-objcopy" -O binary --only-section=.text "$K" "$T" || fail "objcopy of .text"
th=$(sha256sum "$T" | cut -d' ' -f1)
echo "ELF kernel sha256 $kh: $([ "$kh" = "$DESK_ELF" ] && echo SAME AS || echo DIFFERENT FROM) E197's desk build's (E197.md 17.5, on this box); request.md states none (reported, never a gate)"
echo "ELF .text sha256 $th ($(stat -c %s "$T") B): $([ "$th" = "$DESK_TEXT" ] && echo SAME AS || echo DIFFERENT FROM) E197's desk build's .text (reported, never a gate)"
echo "ELF path strings in the kernel: $(strings -a "$K" | grep -c -E '/home/|/tmp/|/Users/')"
"$H" --list --json > "$RR/build/host-list.jsonl" 2> "$RR/build/host-list.err" || fail "the host's --list --json failed"
"$H" --list > "$RR/build/host-list.txt" 2>> "$RR/build/host-list.err" || fail "the host's --list failed"
cmp -s "$RR/build/host-list.jsonl" "$K197/desk/host-list-e197.jsonl" && cmp -s "$RR/build/host-list.txt" "$K197/desk/host-list-e197.txt" ||
  fail "the host's table differs from E197's desk/host-list-e197.jsonl or .txt: no sitting (E200.md 13)"
echo "HOST-TABLE SAME: --list --json and --list byte for byte E197's registered table ($(grep -c . "$RR/build/host-list.jsonl") kinds)"
hr() {  # hr <want rc> <want stderr text> <args>: a refusal before the device layer (ET_DEVICES=99, an unreadable kernel)
  local want=$1 text=$2 out rc; shift 2
  out=$(env ET_DEVICES=99 LD_LIBRARY_PATH=/opt/et/lib timeout 10 "$H" --kernel /nonexistent-e200/regfile.elf "$@" 2>&1 > /dev/null)
  rc=$?
  local what="ET_DEVICES=99 --kernel <unreadable> $*"
  if [ "$rc" -eq "$want" ] && printf '%s\n' "$out" | grep -qF -- "$text"; then echo "HOST-REFUSAL ok: $what -> exit $rc, '$text'"; return 0; fi
  echo "HOST-REFUSAL FAILED: $what -> exit $rc (want $want), stderr: $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-200)"; return 1
}
hb=0
hr 2 "unknown option --no-such-option" --kind nop.z --no-such-option || hb=1
hr 1 "FAIL: --budget must be in (0, 9] seconds" --kind nop.z --budget 9.6 || hb=1
hr 1 "FAIL: unknown kind no.such (see --list)" --kind no.such || hb=1
hr 1 "FAIL: ET_DEVICES=99: no such card node" --kind nop.z --seconds 1 || hb=1
[ "$hb" -eq 0 ] || fail "the host's behaviour: a refusal did not read as built (the lines above)"
echo "HOST-BEHAVIOUR OK: four refusals before the device layer, as main.cpp writes them"
sig() {  # sig <file>: its dynamic imports of a signal installer, and of a logging library's crash-handler installer
  local s c
  s=$(nm -D --undefined-only "$1" 2>/dev/null | awk '{print $NF}' | sed 's/@.*//' | grep -E '^(sigaction|signal|sigset|bsd_signal)$' | sort -u | tr '\n' ' ')
  c=$(nm -D --undefined-only "$1" 2>/dev/null | awk '{print $NF}' | grep -E 'installCrashHandler|InstallFailureSignalHandler' | sort -u | tr '\n' ' ')
  echo "${s:-none}|${c:-none}"
}
hs=$(sig "$H"); IFS='|' read -r hsg hcr <<EOF
$hs
EOF
echo "SIGNAL-READ host: imports of a signal installer: $hsg; of a crash-handler installer: $hcr"
ldd "$H" 2>/dev/null | awk '$3 ~ /^\// {print $1, $3}' > "$RR/build/host-ldd.txt"
while read -r name path; do
  case "$path" in /opt/et/*) ;; *) continue ;; esac
  ls=$(sig "$path"); IFS='|' read -r lsg lcr <<EOF
$ls
EOF
  echo "SIGNAL-READ $name ($path, sha256 $(sha256sum "$path" | cut -c1-12)): imports of a signal installer: $lsg; of a crash-handler installer: $lcr"
done < "$RR/build/host-ldd.txt"
echo "SIGNAL-READ (reported, never a gate): a host that does not end on its timeout's TERM is the kit's hang watch's: a STOP and a report, never a kill (E197 D1)"
RN=$RR/build/run_trains-e200.py
rm -f "$RN"
[ "$(sha256sum "$W1" 2>/dev/null | cut -d' ' -f1)" = "$W1_SHA" ] || fail "E200's W1 diff is not at its sha256 ${W1_SHA:0:12}: no sitting (E200.md 13)"
patch -s --no-backup-if-mismatch -r - -o "$RN" "$K197/lab/run_trains.py" < "$W1" > "$RR/build/runner-patch.txt" 2>&1 || fail "W1 did not apply to E197's lab runner (build/runner-patch.txt): no sitting (E200.md 13)"
rh=$(sha256sum "$RN" | cut -d' ' -f1)
nd=$(diff "$K197/lab/run_trains.py" "$RN" | grep -c '^>')
[ "$rh" = "$RUNNER_SHA" ] && [ "$nd" -eq 2 ] || fail "the runner made from E197's lab runner and W1 reads ${rh:0:12} with $nd changed line(s), not E200's ${RUNNER_SHA:0:12} with 2: no sitting (E200.md 13)"
echo "RUNNER E197's lab runner with W1: sha256 $rh, E200's (E200.md 4), $nd lines changed: $(diff "$K197/lab/run_trains.py" "$RN" | grep '^>' | grep -c 'window", "320000000"') of them the window 320000000"
LD=$RR/build/listing-$(date +%s)
mkdir -p "$LD/ref" || fail "cannot make $LD"
for f in run_session.sh stopwatch.py trains.tsv; do cp "$SRC/$f" "$LD/ref/$f"; done
cp "$RN" "$LD/ref/run_trains.py"
lb=0
for plan in full short ext; do
  ( unset CAP_S SAMPLER SAMPLER_S ET_DEVICES; DRY=1 H="$H" LOCK=/run/lock/etsoc-shire0.lock GAP=30 bash "$LD/ref/run_session.sh" "$LD/out-$plan" "$plan" ) > "$LD/$plan.txt" 2>&1
  python3 -I -B "$KIT/check_e200.py" drycmp "$LD/$plan.txt" "$K197/desk/dry-e197-$plan.txt" --host "$H" --out "$LD/out-$plan" || lb=1
done
[ "$lb" -eq 0 ] || fail "the session's dry listing with this host and E200's runner differs from E197's but W1 (the lines above): no sitting (E200.md 13)"
[ -x "$SBIN" ] || fail "the box's reader $SBIN is missing or not executable"
sh=$(sha256sum "$SBIN" | cut -d' ' -f1)
[ "$sh" = "$SBIN_SHA" ] || fail "the box's reader $SBIN reads ${sh:0:12}, not its pin ${SBIN_SHA:0:12}: no sitting"
hh=$(sha256sum "$H" | cut -d' ' -f1)
echo "SAMPLER the box's $SBIN, sha256 $sh, at its pin (not run here; the session runs it behind E200's guard)"
echo "HOST regfile_host sha256 $hh"
{ echo "REGFILE-BUILT $(TZ=America/Los_Angeles date '+%F %T %Z')"; echo "kernel $kh"; echo "text $th"; echo "host $hh"; echo "runner $rh"
  echo "sampler $sh"; echo "signal host $hsg| $hcr"; } > "$BUILT"
echo "REGFILE-BUILT rc=0"

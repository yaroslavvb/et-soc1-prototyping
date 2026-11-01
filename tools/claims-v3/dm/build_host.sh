#!/usr/bin/env bash
# E99: build the host with the lines: operand, with enercat-hl's own compile and link lines and against its Constants.h, so it
# launches enercat-hl's kernel ELF unchanged (no device tool, no card). First a verify build of the unchanged main.cpp, to
# show that these lines reproduce E81's host .text. Run it from the tree (aifoundry3: ~/aifoundry), with nothing on the card:
# compiling loads the host.
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
H=build/enercat-hl/host/CMakeFiles/enercat_host.dir
B=build/enercat-e99
mkdir -p "$B/host" "$B/verify/host"
ln -sfn "$ROOT/build/enercat-hl/kernel" "$B/kernel"
ln -sfn "$ROOT/build/enercat-hl/kernel" "$B/verify/kernel"
DEFS=$(sed -n 's/^CXX_DEFINES = //p' "$H/flags.make")
INCS=$(sed -n 's/^CXX_INCLUDES = //p' "$H/flags.make")
FLAGS=$(sed -n 's/^CXX_FLAGS = //p' "$H/flags.make")
build_one() {  # build_one <source> <output binary>
  local src=$1 out=$2
  # shellcheck disable=SC2086
  c++ $DEFS $INCS $FLAGS -c "$src" -o "$out.o"
  local link
  link=$(sed -e "s#CMakeFiles/enercat_host.dir/main.cpp.o#$ROOT/$out.o#" -e "s#-o enercat_host#-o $ROOT/$out#" "$H/link.txt")
  ( cd build/enercat-hl/host && eval "$link" )
}
python3 tools/claims-v3/dm/make_host_src.py workloads/enercat/host/main.cpp "$B/main_e99.cpp"
build_one workloads/enercat/host/main.cpp "$B/verify/host/enercat_host"
build_one "$B/main_e99.cpp" "$B/host/enercat_host"
echo "== enercat-hl (E81's) =="
bash tools/claims-v3/text_hash.sh build/enercat-hl/host/enercat_host
echo "== the unchanged main.cpp, rebuilt =="
bash tools/claims-v3/text_hash.sh "$B/verify/host/enercat_host"
echo "== the E99 host =="
bash tools/claims-v3/text_hash.sh "$B/host/enercat_host"
a=$(bash tools/claims-v3/text_hash.sh build/enercat-hl/host/enercat_host | awk '$1=="text"&&$2=="host"{print $3}')
b=$(bash tools/claims-v3/text_hash.sh "$B/verify/host/enercat_host" | awk '$1=="text"&&$2=="host"{print $3}')
if [ "$a" = "$b" ]; then echo "verify: rebuilt host .text == E81's"; else echo "verify: rebuilt host .text DIFFERS from E81's"; fi
strings "$B/host/enercat_host" | grep -c 'lines: needs a whole number' || true

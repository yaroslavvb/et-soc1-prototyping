#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): THE FILES, on the box (step 6's job runs it after the build) and
# on the desk (its desk tests): every input the host reads, made or fetched and checked by its sha256, as E202.md section 2 orders:
#   - the four public MNIST files FETCHED ON THE BOX by the program's recipe (workloads/mnistmlp/model/fetch_mnist.sh: two mirrors, each
#     file accepted only by its sha256 in MNIST-SHA256SUMS, then decompressed and checked again);
#   - the TRAINED weights decompressed from the registration's durable home (tools/claims-v3/e202/weights/mnist-int8-trained.mlpw.gz)
#     and checked by the pin 82d3f71f...; never retrained;
#   - the RANDOM weights regenerated on the box by `mnist_model.py make-random` and checked by the pin 00f060b1...;
#   - the expected outputs (labels, group checksums, raw layer-5 tiles) of both weight configurations on both splits regenerated on the
#     box by `mnist_model.py expect` and checked by their pins (integer arithmetic: identical on any machine);
#   - the program's PINS-SHA256SUMS copied beside them (the host's --pins: it checks every input it reads by name and sha256).
# A file already present at its pin is kept (a second build start the same day does not redo it). numpy at 4 threads, nice 10, under 4 GB
# of address space. Prints E202-FILES OK: 18 of 18 ... and exits 0, or E202-FILES-FAILED: <why> and exits 1. No device is opened.
#   bash tools/claims-v3/e202/files_e202.sh [DIR, default build/e202files]       (from the tree's root)
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 2
D=${1:-build/e202files}
M=workloads/mnistmlp/model
P=$M/PINS-SHA256SUMS
fail() { echo "E202-FILES-FAILED: $*"; exit 1; }
pin() { awk -v f="$1" '$2 == f { print $1 }' "$P"; }
at_pin() { [ -s "$1" ] && [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$(pin "$(basename "$1")")" ]; }
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4
PY="prlimit --as=4294967296 nice -n 10 python3 -I -B $M/mnist_model.py"
mkdir -p "$D/mnist" "$D/files" || fail "cannot make $D"
echo "files: $(date '+%F %T %Z') into $D"
out=$(bash "$M/fetch_mnist.sh" "$D/mnist" 2>&1); echo "$out" | tail -n 5
echo "$out" | grep -q '^FETCH-MNIST OK$' || fail "the MNIST fetch: $(echo "$out" | tail -n 1)"
( cd "$D/mnist" && sha256sum -c --quiet "$OLDPWD/$M/MNIST-SHA256SUMS" ) || fail "an MNIST file is not at its sha256"
W=$D/files/mnist-int8-trained.mlpw
if ! at_pin "$W"; then
  gzip -dc tools/claims-v3/e202/weights/mnist-int8-trained.mlpw.gz > "$W.part" && mv -f "$W.part" "$W" || fail "the trained weights' .gz"
fi
at_pin "$W" || fail "the trained weights are not at the pin $(pin mnist-int8-trained.mlpw)"
echo "files: the trained weights decompressed from the registration's .gz, at their pin"
W=$D/files/mnist-int8-random.mlpw
if ! at_pin "$W"; then
  $PY make-random --train-images "$D/mnist/train-images-idx3-ubyte" --out "$W.part" > "$D/files/make-random.json" || fail "make-random"
  mv -f "$W.part" "$W"
fi
at_pin "$W" || fail "the random weights are not at the pin $(pin mnist-int8-random.mlpw)"
echo "files: the random weights regenerated here, at their pin"
for cfg in trained random; do
  for sp in train t10k; do
    tag=$sp; [ "$sp" = t10k ] && tag=test
    E=$D/files/expect-$cfg-$tag.mlpe; L=$D/files/logits-$cfg-$tag.mlpl
    if ! at_pin "$E" || ! at_pin "$L"; then
      $PY expect --weights "$D/files/mnist-int8-$cfg.mlpw" --images "$D/mnist/$sp-images-idx3-ubyte" \
        --true-labels "$D/mnist/$sp-labels-idx1-ubyte" --out-expect "$E.part" --out-logits "$L.part" > "$D/files/expect-$cfg-$tag.json" \
        || fail "expect $cfg $tag"
      mv -f "$E.part" "$E" && mv -f "$L.part" "$L"
    fi
    at_pin "$E" && at_pin "$L" || fail "the expected outputs $cfg $tag are not at their pins"
    echo "files: expected outputs $cfg $tag regenerated here, at their pins"
  done
done
cp -f "$P" "$D/files/PINS-SHA256SUMS" || fail "the pins file"
n=0
while read -r h f; do
  [ -n "$f" ] || continue
  case "$f" in *idx*) p=$D/mnist/$f ;; *) p=$D/files/$f ;; esac
  [ -s "$p" ] && [ "$(sha256sum "$p" | cut -d' ' -f1)" = "$h" ] || fail "$f is not at its pin"
  n=$((n + 1))
done < "$P"
[ "$n" -eq 18 ] || fail "$n pinned files, not 18"
rm -f "${D:?}"/files/*.part "${D:?}"/mnist/*.part
echo "E202-FILES OK: $n of 18 pinned files at their sha256 (MNIST fetched and checked by sha256; the trained weights from the registration's .gz; the random weights and the expected outputs regenerated here)"
exit 0

#!/usr/bin/env bash
# Fetch the four public MNIST files into DIR, accept each only by its sha256 (MNIST-SHA256SUMS beside this script),
# and decompress them (the host reads the decompressed idx files, also checked). The original site often refuses
# scripted downloads, so two mirrors are tried in turn; their bytes were identical when E202 was designed (Sun 15 Nov
# 2026) and their md5 is torchvision's published value. Large data is never committed: run this on the box.
#   bash fetch_mnist.sh DIR        prints FETCH-MNIST OK and exits 0, or names the file that failed and exits 1
# SPDX-License-Identifier: Apache-2.0
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="${1:?usage: fetch_mnist.sh DIR}"
mkdir -p "$D" || exit 1
MIRRORS="https://ossci-datasets.s3.amazonaws.com/mnist https://storage.googleapis.com/cvdf-datasets/mnist"
want() { awk -v f="$1" '$2 == f { print $1 }' "$here/MNIST-SHA256SUMS"; }
for f in train-images-idx3-ubyte train-labels-idx1-ubyte t10k-images-idx3-ubyte t10k-labels-idx1-ubyte; do
  gz="$f.gz"
  if [ ! -s "$D/$gz" ] || [ "$(sha256sum "$D/$gz" | cut -d' ' -f1)" != "$(want "$gz")" ]; then
    rm -f "$D/$gz.part"
    ok=0
    for m in $MIRRORS; do
      if curl -sS -f -m 300 -A 'generic-client' -o "$D/$gz.part" "$m/$gz" &&
         [ "$(sha256sum "$D/$gz.part" | cut -d' ' -f1)" = "$(want "$gz")" ]; then
        mv -f "$D/$gz.part" "$D/$gz"; ok=1; break
      fi
      echo "fetch_mnist: $gz from $m failed or did not match" >&2
    done
    [ "$ok" = 1 ] || { rm -f "$D/$gz.part"; echo "FETCH-MNIST FAILED $gz"; exit 1; }
  fi
  if [ ! -s "$D/$f" ] || [ "$(sha256sum "$D/$f" | cut -d' ' -f1)" != "$(want "$f")" ]; then
    gzip -dc "$D/$gz" > "$D/$f.part" && mv -f "$D/$f.part" "$D/$f"
  fi
  [ "$(sha256sum "$D/$f" | cut -d' ' -f1)" = "$(want "$f")" ] || { echo "FETCH-MNIST FAILED $f (decompressed)"; exit 1; }
  echo "fetch_mnist: $gz and $f OK"
done
echo "FETCH-MNIST OK"

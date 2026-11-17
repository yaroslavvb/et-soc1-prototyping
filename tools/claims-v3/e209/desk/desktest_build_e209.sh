#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): THE BUILD'S DESK TEST. The box root made by make_box_e209.py sync
# in a scratch folder of ours (outside the repo), then E208's src/build_mms.sh, unchanged, from that root, as runbook step 6 runs it:
# rgm136 and the lab's ettelem built against this box's /opt/et (nice 10, 2 jobs); THE KERNEL BY ITS BYTES (E136's pin aace138c...);
# the host's four refusals before it opens a device (the built host RUN, so this test runs only inside W/nodev.sh: no /dev/et*);
# build/BUILD-mms.json. et-who is a stand-in here (the build's quiet-box look: no card at the desk); everything else is real.
#   bash W/slot.sh bash W/nodev.sh bash tools/claims-v3/e209/desk/desktest_build_e209.sh <empty scratch dir outside the repo>
# Prints DESKTEST-BUILD-E209 PASS or FAIL last, and the record's three sha256 (kernel, host, reader).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for d in /dev/et*; do
  [ -e "$d" ] || continue
  if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node here: run this inside W/nodev.sh"; exit 2; fi
done
mkdir -p "$S" && S=$(cd "$S" && pwd -P)
[ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
R=$S/root
mkdir -p "$R" "$S/bin"
printf '#!/bin/sh\n# the build test'"'"'s stand-in for et-who: every card free (no card at the desk)\nexit 0\n' > "$S/bin/et-who"
chmod 755 "$S/bin/et-who"
echo "== sync"
/usr/bin/python3 -I -B "$SRC/tools/claims-v3/e209/make_box_e209.py" sync "$R"; rc=$?
[ "$rc" -eq 0 ] || { echo "DESKTEST-BUILD-E209 FAIL (the sync, rc $rc)"; exit 1; }
echo "== build (E208's src/build_mms.sh, unchanged, from the box root)"
t0=$(date +%s)
PATH="$S/bin:$PATH" bash "$R/src/build_mms.sh"; rc=$?
echo "build rc $rc in $(( $(date +%s) - t0 )) s"
echo "== the record"
/usr/bin/python3 -I -B - "$R" "$rc" <<'PY'
import hashlib, json, os, sys
r, rc = sys.argv[1], int(sys.argv[2])
rec = json.load(open(os.path.join(r, "build", "BUILD-mms.json")))
pin = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None
k, h, t = (sha(os.path.join(r, p)) for p in ("build/rgm/kernel/sparsity.elf", "build/rgm/host/sparsity_host", "build/ettelem/ettelem"))
checks = rec.get("host_checks") or []
print(json.dumps({k_: rec.get(k_) for k_ in ("box", "day", "verdict", "kernel_sha256", "kernel_text_sha256", "host_sha256", "ettelem_sha256",
                                              "host_checks", "compilers", "et_devices")}, indent=1))
ok = (rc == 0 and rec.get("verdict") == "BUILT" and rec.get("box") == "aifoundry2" and k == pin == rec.get("kernel_sha256")
      and h == rec.get("host_sha256") and t == rec.get("ettelem_sha256") and len(checks) == 4 and all(c.endswith(":ok") for c in checks))
print(f"kernel {k} (pin {'EQUAL' if k == pin else 'DIFFERENT'}); host {h}; reader {t}; the host's refusals {checks}")
print("DESKTEST-BUILD-E209 " + ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
PY

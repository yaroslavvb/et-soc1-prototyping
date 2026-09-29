#!/usr/bin/env bash
# After the sys_emu suite: a two-stage sys_emu run with --records-out, then --verify-records on it (no device), then
# card_run.sh's packing of FILE.surv (sha256, headers alone, gzip) and a re-verify from the gunzipped copy, then a
# flipped c1 bit in one entry (must fail). Niced, one simulator; waits for the suite and for et-who --check.
while pgrep -f 'sysemu_check.sh' > /dev/null; do sleep 10; done
cd ~/nekko/build/sparseparity-t-src || exit 2
H=$HOME/nekko/build/sparseparity-t/host/sparseparity_host
W=$HOME/nekko/build/sparseparity-t-verify
rm -rf $W; mkdir -p $W; cd $W
until et-who --check > /dev/null 2>&1; do sleep 15; done
A="--mode tensor --variant m1 --cost fit --gen inc --n 48 --k 3 --eta 0.1 --m 512 --seed 9 --m1 256 --tau1 30 --per-shire 2 --oracle on"
echo "== sysemu run with --records-out"
timeout 1800 nice -n 19 $H --sysemu --sim-args "-vpurf_warn" $A --records-out $W/rec.bin > run.json 2> run.err < /dev/null
echo "rc $?"; python3 -c 'import json; j=json.loads(open("run.json").read().splitlines()[-1]); c=j["checks"]; t=j["two_stage"]; print(j["status"], c["survivors"], "|", c["survivors_oracle"], "|", c["stage2"], "| poison_s", t["poison_s"], "| host_cpu_s", j["host_cpu_s"])'
ls -la rec.bin rec.bin.surv
echo "== verify-records"
nice -n 19 $H $A --verify-records $W/rec.bin > v1.json 2> v1.err; echo "rc $?"
python3 -c 'import json; j=json.loads(open("v1.json").read().splitlines()[-1]); c=j["checks"]; print(j["status"], c["oracle"], "|", c["survivors"], "|", c["survivors_oracle"], "|", c["stage2"])'
echo "== card_run.sh packing"
f=$W/rec.bin.surv
(cd $W && sha256sum "$(basename "$f")") > "$f.sha256"
head -c 65536 "$f" | gzip -9 > "$f.hdr.gz"
nice -n 19 gzip -f -1 "$f"
ls -la $W | grep surv; cat $f.sha256
gunzip -k $f.gz && (cd $W && sha256sum -c rec.bin.surv.sha256)
zcat $f.hdr.gz | cmp - <(head -c 65536 $f) && echo "hdr = the first 64 KB"
nice -n 19 $H $A --verify-records $W/rec.bin > v2.json 2> v2.err; echo "re-verify rc $?"
python3 -c 'import json; j=json.loads(open("v2.json").read().splitlines()[-1]); print(j["status"])'
echo "== one entry's c1 bit flipped"
python3 - $f <<'PY'
import sys, struct
p = sys.argv[1]; b = bytearray(open(p, "rb").read())
off = 65536 + 8 * 3            # the 4th stored entry of the first slot with entries
v = struct.unpack_from("<Q", b, off)[0] ^ (1 << 53)
struct.pack_into("<Q", b, off, v); open(p, "wb").write(b)
PY
nice -n 19 $H $A --verify-records $W/rec.bin > v3.json 2> v3.err; echo "rc $?"
python3 -c 'import json; j=json.loads(open("v3.json").read().splitlines()[-1]); c=j["checks"]; print(j["status"], "|", c["survivors"], "|", c["survivors_oracle"], "|", c["stage2"])'
echo DONE

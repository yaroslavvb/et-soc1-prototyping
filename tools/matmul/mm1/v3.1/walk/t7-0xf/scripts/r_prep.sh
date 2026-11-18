#!/bin/bash
# t7-0xf (Q221), run ON aifoundry3 by a3.sh look: make this lane's own folder and copy into it (reading only) v31-trace's built kit copies
# that t7/t8 and verify-v31trace's u1 ran (rgm136's host and ELF, the fp32 zeros tile) and v31-trace's trace_run.py (its Summary class);
# check every hash against t7/t8/u1's records and the ELF's .text against E211's pin prefix 61315bf6a449c282. No simulator, no device.
set -u
V="$HOME/claude/work/q217-v31-trace"
D="$HOME/claude/work/q221-t7-0xf"
mkdir -p "$D/bin/rgm136" "$D/tiles/fp32" "$D/runs" || exit 3
cp "$V/bin/rgm136/sparsity_host" "$D/bin/rgm136/sparsity_host" || exit 3
cp "$V/bin/rgm136/sparsity.elf" "$D/bin/rgm136/sparsity.elf" || exit 3
cp "$V/tiles/fp32/zeros.bin" "$D/tiles/fp32/zeros.bin" || exit 3
cp "$V/trace_run.py" "$D/trace_run_v31.py" || exit 3
chmod +x "$D/bin/rgm136/sparsity_host"
ok=0
chk() { got=$(sha256sum "$1" | cut -d' ' -f1); if [ "$got" = "$2" ]; then echo "OK   $(basename "$1") $got"; else echo "BAD  $(basename "$1") $got want $2"; ok=1; fi; }
chk "$D/bin/rgm136/sparsity_host" 09bba984e3361d511f0a4a33321bfb8f2b5ea43d8193e3b743f371cb865b2054
chk "$D/bin/rgm136/sparsity.elf" ff2723b81e2ce409d14e4ee54ae5a91b6fb3a11827097023c8c35ac088608684
chk "$D/tiles/fp32/zeros.bin" e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad
chk "$D/trace_run_v31.py" 87161c2a6af5158b125948e8a8ccbec3447354bcd95e470b08729e0149f4cae4
/usr/bin/python3 -I -B - "$D/bin/rgm136/sparsity.elf" <<'PY'
import hashlib, struct, sys
b = open(sys.argv[1], "rb").read()
assert b[:4] == b"\x7fELF" and b[4] == 2, "not ELF64"
shoff, = struct.unpack_from("<Q", b, 0x28)
shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x3A)
def sec(i):
    return struct.unpack_from("<IIQQQQIIQQ", b, shoff + i * shentsize)
names = sec(shstrndx)
for i in range(shnum):
    s = sec(i)
    nm = b[names[4] + s[0]:].split(b"\0", 1)[0].decode()
    if nm == ".text":
        h = hashlib.sha256(b[s[4]:s[4] + s[5]]).hexdigest()
        print(".text sha256", h, "E211 pin prefix 61315bf6a449c282:", "MATCH" if h.startswith("61315bf6a449c282") else "NO MATCH")
PY
ls -la "$D" "$D/bin/rgm136"
exit $ok

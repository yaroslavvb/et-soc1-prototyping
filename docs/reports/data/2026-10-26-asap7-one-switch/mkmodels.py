"""Turn ASAP7's HSPICE BSIM-CMG card (level 72) into an ngspice OSDI card."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
drop = set(a.lower() for a in sys.argv[3:])
out = []
for line in open(src):
    m = re.match(r'^\.model\s+(\S+)\s+(nmos|pmos)\s+level\s*=\s*\d+', line, re.I)
    if m:
        out.append(f".model {m.group(1)} bsimcmg_va TYPE="
                   f"{1 if m.group(2).lower()=='nmos' else -1}\n")
        continue
    if line.startswith('+') and drop:
        # keep the line but strip dropped "name = value" pairs
        kept = []
        for k, v in re.findall(r'([A-Za-z_]\w*)\s*=\s*(\S+)', line):
            if k.lower() not in drop:
                kept.append(f"{k} = {v}")
        out.append("+" + "   ".join(kept) + "\n" if kept else "*\n")
        continue
    out.append(line)
open(dst, 'w').writelines(out)
print("wrote", dst)

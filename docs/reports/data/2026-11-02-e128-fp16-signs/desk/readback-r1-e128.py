# usage: python3 readback-r1-e128.py ../aifoundry1-c1/e128/readback-p12802/readback.jsonl
# E128: the read-back rule alone, from the read-back file (no power data), to report the lane's status while the passes run (as E106 and E108 did)
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "tools", "claims-v3", "e128"))
import score_e128 as s
reg = json.load(open(s.REG)); spec = json.load(open(s.SPEC))
rows = s.read_rows(sys.argv[1], spec)
rr, rt = s.score_read(rows, reg)
print(json.dumps(rr, indent=1))
print("tiles and the readings they equal:", json.dumps(rt))

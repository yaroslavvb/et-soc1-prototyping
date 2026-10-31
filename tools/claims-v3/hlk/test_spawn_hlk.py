"""E85: unit test of run_hlk.install - every set launches with its own --type (a fake Popen, no device).

    python3 test_spawn_hlk.py
"""
import json, os, sys, types
HLK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HLK)
import run_hlk as K
R = K.R
raw = json.load(open(os.path.join(HLK, "protocol-e85.json")))
tmap, prob = K.type_map(raw)
assert not prob, prob
K.install(tmap)
seen = []
class FakeP:
    pid = 4242
    returncode = 0
    def __init__(self, cmd, **kw): seen.append(cmd)
    def communicate(self, timeout=None): return ("", "")
R.subprocess.Popen = FakeP
proto = R.Protocol(raw, os.path.join(HLK, "protocol-e85.json"))
fake = types.SimpleNamespace(dry=False, proto=proto, heater_bin="/x/sparsity_host", kernel="/x/k.elf",
                             stop_file="/x/STOP", root="/root", _heater_pids=set(), orphans=[],
                             touch=lambda p: None, mark=lambda *a, **k: None, say=lambda *a, **k: None)
fake._values_arg = types.MethodType(R.Session._values_arg, fake)
ok = True
for name, s in raw["sets"].items():
    seen.clear()
    R.Session._spawn_heater(fake, int(s["mask"], 16), s["per_shire"], s["values"])
    cmd = seen[0]
    got = cmd[cmd.index("--type") + 1]
    vals = cmd[cmd.index("--values") + 1]
    good = got == s["type"] and vals.endswith(s["values"][5:])
    ok &= good
    print(f"{name:7s} want {s['type']} got {got}  {vals[-45:]}  {'ok' if good else 'WRONG'}")
assert proto.heater["type"] == "fp32", "heater type not restored"
print("SPAWN TYPE TEST", "PASS" if ok else "FAIL")

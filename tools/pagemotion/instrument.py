"""instrument.py IN OUT: a diagnostic copy of the memory-levels page that times the camera's suspect functions
(window.__T: [name, start, ms]) and records long animation frames (window.__LOAF)."""
import sys
s = open(sys.argv[1], encoding='utf-8').read()
anchor = '/* a read-only view of the state, for the page\'s tests (headless Chrome) */'
assert s.count(anchor) == 1, s.count(anchor)
names = sys.argv[3].split(',') if len(sys.argv) > 3 else ['buildLayer', 'strokeKeeper', 'scaleUI', 'clearFx', 'clearDim', 'dimLevel', 'ctxMark', 'ctxClear', 'pipUpdate', 'fitTexts', 'kbTexts', 'ringAll', 'showStep', 'renderBar', 'legendUI']
wrap = "window.__T = []; const __wrap = (name, fn) => function (...a) { const t = performance.now(); try { return fn.apply(this, a); } finally { window.__T.push([name, t, performance.now() - t]); } };\n"
for n in names:
    wrap += f"try {{ {n} = __wrap('{n}', {n}); }} catch (e) {{ console.log('nowrap {n}', e.message); }}\n"
s = s.replace(anchor, wrap + anchor)
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('wrote', sys.argv[2])

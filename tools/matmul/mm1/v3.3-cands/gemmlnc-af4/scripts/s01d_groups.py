import json, sys, os
import numpy as np
R=os.environ['LNC_FORM_DIR'] + '/work/repo'
sys.path.insert(0, os.path.join(R,'tools/matmul/mm1/v3'))
import mm1_core_v3 as C
import engine_v3 as EN
P=json.load(open(os.path.join(R,'tools/matmul/mm1/v3.2/out/mm1_v32_params.json')))
th=P['time']['theta']; form=P['time']['form']
rp=EN.ret_params(th, form if isinstance(form,dict) else {}); ret=EN.Ret(rp)
print('ret', rp)
D=json.load(open(os.path.join(os.path.dirname(R),'s01_points.json')))
rows=[]
for p in sorted(D['points'], key=lambda p: p['e_meas_pJ']):
    MB,NB,KB=p['MB'],p['NB'],p['KB']
    g={n:(cnt,l2,np.array(ds)) for n,cnt,l2,ds in C.groups_masked(MB,NB,KB)}
    def r(name, fn):
        if name not in g: return None
        return float(np.mean(fn(g[name][2])))
    phi = g['A_near'][0]/64
    rAn=r('A_near',ret.rA); rAf=r('A_far',ret.rA); rB1=r('B_r1',ret.rB); rB0=r('B_r0',ret.rB)
    Rm=(p['e_meas_pJ']-26*208)/600
    print('%-14s %-15s R %5.1f | phi %.2f rAn %s rAf %s | rB1 %.2f rB0 %.2f | dAn %s dAf %s dB1 %s dB0 %s'%(p['id'][-14:],p['arm'],Rm,phi,
      '%.2f'%rAn if rAn is not None else '  - ','%.2f'%rAf if rAf is not None else '  - ',rB1,rB0,
      '%.0f-%.0f'%(g['A_near'][2].min(),g['A_near'][2].max()), ('%.0f'%g['A_far'][2][0]) if 'A_far' in g else '-', '%.0f'%g['B_r1'][2][0], '%.0f-%.0f'%(g['B_r0'][2].min(),g['B_r0'][2].max())))

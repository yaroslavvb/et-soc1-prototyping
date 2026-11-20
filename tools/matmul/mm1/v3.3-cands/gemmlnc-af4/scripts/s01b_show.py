import os
import json
D=json.load(open(os.environ['LNC_FORM_DIR'] + '/work/s01_points.json'))
print('%-16s %-10s %4s %4s %4s %6s %6s %6s | %5s %5s %5s | %5s %5s %5s | %6s %6s %7s %6s'%('id','arm','MB','NB','KB','fpMB','e','eF3','qA2','qA3','qAF','qB2','qB3','qBF','Ttw','Tm/Tp','beyond','first'))
for p in sorted(D['points'], key=lambda p: p['e_meas_pJ']):
    tw=p.get('twin') or {}
    qa=p['qA_L2_L3_F']; qb=p['qB_L2_L3_F']
    beyond = 14*(1-qa[0])+12*(1-qb[0])
    print('%-16s %-14s %3d %3d %3d %6.0f %6.0f %6.0f | %5.2f %5.2f %5.2f | %5.2f %5.2f %5.2f | %6.3f %6.3f %6.2f %6.2f %s'%(p['id'][-14:],p['arm'],p['MB'],p['NB'],p['KB'],p['footprint_MB'] or -1,p['e_meas_pJ'],p['e_F3_v32_pJ'],qa[0],qa[1],qa[2],qb[0],qb[1],qb[2],(p['T']/tw['T']) if tw else float('nan'),p['T']/p['v32_T_pred_us'],beyond,p['first'],p['card'][-6:]))

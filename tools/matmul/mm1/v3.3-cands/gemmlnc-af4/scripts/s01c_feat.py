import os
import json
D=json.load(open(os.environ['LNC_FORM_DIR'] + '/work/s01_points.json'))
print('%-14s %-15s %6s %6s | %5s %5s %5s | %6s %6s %6s | %6s %6s | %6s %6s %6s'%('id','arm','e','extra','n2','n3','nF','GBs3','GBsF','GBsT','Ttw','Tlnc','cyc_tw','Apan','Bpan'))
for p in sorted(D['points'], key=lambda p: p['e_meas_pJ']):
    tw=p.get('twin') or {}
    n2,n3,nF = p['lines_L2_L3_F_per_shire_op']
    T = tw.get('T', p['v32_T_pred_us'])  # coop twin's measured op time (us), else MM1's
    bw3 = n3*32*64/(T*1e-6)/1e9; bwF = nF*32*64/(T*1e-6)/1e9
    by = {'fp32':4,'fp16':2,'int8':1}[p['fmt']]
    Apan = 1024*p['KB']*512*by/2**20; Bpan = p['KB']*512*512*by/2**20
    extra = p['e_meas_pJ'] - 26*208
    print('%-14s %-15s %6.0f %6.0f | %5.1f %5.1f %5.1f | %6.1f %6.1f %6.1f | %6.3f %6.3f %6.0f | %6.1f %6.1f %s'%(p['id'][-14:],p['arm'],p['e_meas_pJ'],extra,n2,n3,nF,bw3,bwF,bw3+bwF,T,p['T'],T*p['f'],Apan,Bpan,p['card'][-6:]))

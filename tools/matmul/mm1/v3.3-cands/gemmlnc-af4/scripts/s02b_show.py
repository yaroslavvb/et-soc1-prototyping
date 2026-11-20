import os
import json
O=json.load(open(os.environ['LNC_FORM_DIR'] + '/work/s02_fit.json'))
D=json.load(open(os.environ['LNC_FORM_DIR'] + '/work/s01_points.json'))
v32={p['id']:100*(p['v32_W_given_t']/p['w']-1) for p in D['points']}
fe={r['id']:r for r in O['features_per_point']}
A=O['forms']['AF4']['per_point']; F=O['forms']['F3r']['per_point']; A3=O['forms']['AF3']['per_point']
print('%-16s %-15s %5s %5s %4s | %6s | %7s %7s | %7s %7s | %7s | %5s'%('id','arm','R4','first','Lres','v32','F3r-LO','F3r-LC','AF4-LO','AF4-LC','AF3-LO','meas'))
for a,f,a3 in zip(A,F,A3):
    r=fe[a['id']]
    print('%-16s %-15s %5.1f %5.1f %4.0f | %+6.1f | %+7.1f %+7.1f | %+7.1f %+7.1f | %+7.1f | %5.2f'%(a['id'][-16:], [p['arm'] for p in D['points'] if p['id']==a['id']][0], r['R4'], r['first'], r['Lres'], v32[a['id']], f['LOEO_err_pct'], f['LOCO_err_pct'], a['LOEO_err_pct'], a['LOCO_err_pct'], a3['LOEO_err_pct'], a['meas_W']))
for form in ['F3r','AF4','AF3','AF2','AF1']:
    print(form, 'LOCO', {k:[round(x,2) for x in v] for k,v in O['forms'][form]['LOCO_by_fold'].items()}, 'consts', {k:[round(x,1) for x in v] for k,v in O['forms'][form]['LOCO_consts'].items()})
    print(form, 'LOEO consts', {k:[round(x,1) for x in v] for k,v in O['forms'][form]['LOEO_consts'].items()})
print(O['placebo'])
print(O['twins_summary'])

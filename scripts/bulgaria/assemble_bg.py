import json
B='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/bg/'
D=json.load(open(B+'D.json'));g=json.load(open(B+'geo.json'))
d2=dict(mirs=D['mirs'],land=[dict(label=l['label'],label2=l['label2'],mirs=l['mirs'],area=l['area']) for l in D['land']],nat=D['nat'])
t=open(B+'template_bg.html').read()
data='const GEO='+json.dumps(g,separators=(',',':'),ensure_ascii=False)+';\nconst D='+json.dumps(d2,separators=(',',':'),ensure_ascii=False)+';'
out=t.replace('/*DATA*/',data)
open(B+'bulgaria_tap_morph.html','w').write(out);print(len(out))

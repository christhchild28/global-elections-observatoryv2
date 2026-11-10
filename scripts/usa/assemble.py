import json,sys
sys.path.insert(0,'.')
from build import states,EV
D='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/us/'
g=json.load(open(D+'geo.json'))
for c in g['cells']: c['gr']=[int(round(v)) for v in c.pop('g')]
g['names']={k:s['name'] for k,s in states.items()};g['el']=EV
d=json.load(open(D+'data.json'))
t=open(D+'template_us.html').read()
data='const GEO='+json.dumps(g,separators=(',',':'),ensure_ascii=False)+';\nconst RES='+json.dumps(d['RES'],separators=(',',':'))+';\nconst SPLIT='+json.dumps(d['SPLIT'],separators=(',',':'))+';'
out=t.replace('/*DATA*/',data);open(D+'us_tap_morph.html','w').write(out);print(len(out),len(g['cells']))

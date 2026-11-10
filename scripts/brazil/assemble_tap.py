import json,sys
sys.path.insert(0,'.')
from results import R
from build import states,ELEC
D='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/br/'
g=json.load(open(D+'geo.json'))
for c in g['cells']:
    c['gr']=[int(round(v)) for v in c.pop('g')]
g['names']={k:s['name'] for k,s in states.items()}
g['el']=ELEC
t=open(D+'template_tap.html').read()
data='const GEO='+json.dumps(g,separators=(',',':'),ensure_ascii=False)+';\nconst RES='+json.dumps({k:list(v) for k,v in R.items()})+';'
out=t.replace('/*DATA*/',data)
open(D+'brazil_tap_morph.html','w').write(out)
print(len(out))

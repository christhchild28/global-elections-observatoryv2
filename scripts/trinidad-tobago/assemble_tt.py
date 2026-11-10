import re,json
B='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/'
t=open(B+'tt/src.html').read()
RES=json.loads(re.search(r'const RES=(\{.*?\});\n',t,re.S).group(1))
D=json.loads(re.search(r'const D=(\{.*?\});\n',t,re.S).group(1))
G=json.loads(re.search(r'const GEO=(\{.*?\});\n',t,re.S).group(1))
CODE=json.loads(re.search(r'const CODE=(\{.*?\});\n',t,re.S).group(1))
eb={n:G['seats'][n]['code'] for n in G['seats']}
g=dict(S=D['S'],N=G['N'],bounds=D['bounds'],ghost='',
  cells=[dict(x=c['x'],y=c['y'],st=eb[c['seat']],gr=G['rings'][i]) for i,c in enumerate(D['cells'])],
  extras=[dict(st=eb[e['seat']],d=e['d']) for e in G['extras']],
  outlines={eb[n]:s['d'] for n,s in G['seats'].items()},
  labels={eb[n]:s['lp'] for n,s in G['seats'].items()},
  area={eb[n]:s['area'] for n,s in G['seats'].items()},
  names={eb[n]:n for n in G['seats']},short={eb[n]:(CODE.get(n) or '') for n in G['seats']},
  island={eb[s['name']]:s['island'] for s in D['seats']},el={eb[s['name']]:s['el'] for s in D['seats']})
tpl=open(B+'br/template_tt.html').read()
data='const GEO='+json.dumps(g,separators=(',',':'),ensure_ascii=False)+';\nconst RES='+json.dumps(RES,separators=(',',':'),ensure_ascii=False)+';'
open(B+'br/tt_tap_morph.html','w').write(tpl.replace('/*DATA*/',data))
print(len(tpl)+len(data))

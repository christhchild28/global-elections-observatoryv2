import sys, json, time
sys.path.insert(0,'/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/br')
sys.path.insert(0,'.')
from build import states, EV
from hexpack import Packer
iters=int(sys.argv[1]); seed=int(sys.argv[2]); out=sys.argv[3]; w=json.loads(sys.argv[4])
polys={k:s['geom'] for k,s in states.items()}
pk=Packer(polys,EV,S=78.0,seed=seed,w=w)
t=time.time(); own=pk.run(iters); print('time',round(time.time()-t))
rep=pk.report(own); print(json.dumps(rep))
json.dump(dict(S=78.0,cells=pk.to_cells(own),report=rep),open(out,'w'))

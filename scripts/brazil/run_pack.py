import sys, json, time
sys.path.insert(0,'.')
from build import states, ELEC
from hexpack import Packer, counts_from_values
iters=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1
polys={k:s['geom'] for k,s in states.items()}
cnt=counts_from_values(ELEC,1_000_000)
w=json.loads(sys.argv[4]) if len(sys.argv)>4 else None
pk=Packer(polys,cnt,S=112.0,seed=seed,w=w)
t=time.time(); own=pk.run(iters); print('time',round(time.time()-t))
rep=pk.report(own); print(json.dumps(rep,indent=1))
out=sys.argv[3] if len(sys.argv)>3 else 'layout_new.json'
json.dump(dict(S=112.0,cells=pk.to_cells(own),report=rep),open(out,'w'))

"""Join NZ electorate geometry + electoral population + preliminary winners into <cache>/counties.json.
Unit = one electorate. The engine's two-candidate fields are reused: d = winning margin in votes, r = index into config 'parties'
(the page reads them back that way). Every electorate in the layer must have a population and a result."""
import csv, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from common import cfg as C_
cfg = C_.load(); feat = cfg.features()
layer = cfg.c['layer']; parties = [p['name'] for p in cfg.c['parties']]
rows = lambda key: list(csv.DictReader(open(cfg.inp(cfg.c[key]['file']), encoding='utf-8')))
pop = {r['electorate']: int(r['population']) for r in rows('population') if r['kind'] == layer}
res = {r['electorate']: r for r in rows('results') if r['kind'] == layer}
byname = {f['properties']['name']: fid for fid, f in feat.items()}
miss = sorted(set(byname) - set(pop)) + sorted(set(byname) - set(res)) + sorted(set(pop) - set(byname)) + sorted(set(res) - set(byname))
if miss: raise SystemExit('JOIN FAILED, names that do not line up: %s' % miss)
unk = sorted({r['party'] for r in res.values()} - set(parties))
if unk: raise SystemExit('JOIN FAILED, parties missing from config: %s' % unk)
def centroid(geom):
    polys = geom['coordinates']; A = cx = cy = 0
    for p in polys:
        ring = p[0]
        for i in range(len(ring) - 1):
            x0, y0 = ring[i]; x1, y1 = ring[i + 1]; c = x0 * y1 - x1 * y0; A += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    A /= 2; return cx / (6 * A), cy / (6 * A)
out = []
for name in sorted(byname):
    fid = byname[name]; lon, lat = centroid(feat[fid]['geometry']); r = res[name]
    out.append(dict(name=name, fips=fid, pop=pop[name], lon=round(lon, 4), lat=round(lat, 4), d=int(r['margin']), r=parties.index(r['party'])))
print(len(out), 'electorates joined (%s layer); population total %d' % (layer, sum(o['pop'] for o in out)))
import collections
print('seats by party:', dict(collections.Counter(parties[o['r']] for o in out)))
json.dump(out, open(cfg.tmp('counties.json'), 'w'))

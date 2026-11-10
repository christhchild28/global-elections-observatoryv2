#!/usr/bin/env python3
"""Split the Stats NZ 2025 electorate boundaries into data/geometry-general.geojson and data/geometry-maori.geojson.

Source: Stats NZ General Electorates 2025 and Māori Electorates 2025 (CC BY 4.0, Representation Commission / Stats NZ),
generalised by the source file's author (maxAllowableOffset 0.002 degrees). Only change made here: parts of a boundary
that lie east of the antimeridian (the Chatham Islands, longitude < 0) are dropped, because they sit about 800 km off the
main islands and would stretch the map; coordinates are rounded to 4 decimals. Each feature gets id = electorate slug.

Land clip: the Stats NZ electorates include coastal water, so they touch across Cook Strait. Each electorate is intersected with
the Natural Earth 10m land polygon (public domain; extract in data/nz-land.geojson) so the North and South Islands are separate
landmasses and area means land area. An electorate that would lose all its land to the coarser coastline keeps its original shape."""
import json, os, sys
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
land = shape(json.load(open(os.path.join(HERE, 'data', 'nz-land.geojson')))['features'][0]['geometry']).buffer(0.004)   # small buffer: the 10m coast is coarser than the electorate edges
src = json.load(open(os.path.join(HERE, 'data', 'boundaries-2025.source.json'), encoding='utf-8'))
for grp in ('general', 'maori'):
    feats = []
    for f in src['features']:
        p = f['properties']
        if p['group'] != grp: continue
        g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        keep = []
        for poly in polys:
            if min(x for x, _ in poly[0]) < 0: continue            # Chatham Islands
            keep.append(poly)
        orig = [q for q in keep]
        g0 = unary_union([shape(dict(type='Polygon', coordinates=q)).buffer(0) for q in keep])
        c = g0.intersection(land)
        cp = [x for x in (list(c.geoms) if c.geom_type == 'MultiPolygon' else [c]) if x.geom_type == 'Polygon' and x.area > 2e-5]
        if cp: keep = [[[list(pt) for pt in x.exterior.coords]] + [[list(pt) for pt in r.coords] for r in x.interiors] for x in cp]
        else: print('  kept original (no land after clip):', p['name'])
        keep = [[[[round(x, 4), round(y, 4)] for x, y in ring] for ring in poly] for poly in keep]
        feats.append(dict(type='Feature', id=p['electorate_slug'], properties=dict(name=p['name'], group=grp, parts=len(keep)),
                          geometry=dict(type='MultiPolygon', coordinates=keep)))
    out = os.path.join(HERE, 'data', 'geometry-%s.geojson' % grp)
    json.dump(dict(type='FeatureCollection', features=feats), open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(grp, len(feats), 'features ->', out, os.path.getsize(out), 'bytes')

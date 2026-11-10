import json, math, warnings, random
warnings.filterwarnings('ignore')
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, MultiPoint, Point, LineString
from shapely.ops import voronoi_diagram, unary_union
from scipy.optimize import linear_sum_assignment
import sys
sys.path.insert(0,'.')
from build import states, EV
D='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/us/'

import os
LAYOUT = os.environ.get('LAYOUT', 'layout.json')
L = json.load(open(D + LAYOUT))
S = L['S']
N = int(os.environ.get('HEXN', 60))
LAYOUT = os.environ.get('LAYOUT', 'layout.json')
rng = np.random.default_rng(7)

# flip y (screen coords)
def flip(g):
    return shapely.transform(g, lambda a: a * np.array([1, -1]))
from shapely.geometry import Point as _P
for k, s in states.items():
    s['g'] = flip(s['geom'])
    if k == 'DC': s['g'] = _P(*s['g'].centroid.coords[0]).buffer(26, 12)

cells = [dict(x=c['x'], y=-c['y'], st=c['st']) for c in L['cells']]
ang = lambda k: math.radians(90 + 60 * k)

def hex_ring(cx, cy):
    v = [(cx + S * math.cos(ang(k)), cy + S * math.sin(ang(k))) for k in range(6)]
    per = N // 6; out = []
    for k in range(6):
        a, b = v[k], v[(k + 1) % 6]
        for j in range(per):
            u = j / per; out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return np.array(out[::-1])

def sample_pts(g, step):
    minx, miny, maxx, maxy = g.bounds
    xs = np.arange(minx, maxx, step); ys = np.arange(miny, maxy, step)
    pts = [(x, y) for x in xs for y in ys]
    pts = shapely.points(np.array(pts))
    m = shapely.contains(g, pts)
    return np.array([(p.x, p.y) for p in pts[m]])

def kmeans(P, k, iters=60):
    # k-means++ init
    C = [P[rng.integers(len(P))]]
    for _ in range(k - 1):
        d = np.min([((P - c) ** 2).sum(1) for c in C], axis=0)
        C.append(P[rng.choice(len(P), p=d / d.sum())])
    C = np.array(C)
    for _ in range(iters):
        lab = np.argmin(((P[:, None, :] - C[None]) ** 2).sum(2), axis=1)
        for j in range(k):
            m = lab == j
            if m.any(): C[j] = P[m].mean(0)
    return C

def resample(ring_coords, n):
    ls = LineString(ring_coords)
    tot = ls.length
    return np.array([ls.interpolate(tot * i / n).coords[0] for i in range(n)])

def signed_area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

def align(ring, hx):
    # match orientation and best circular shift to hexagon ring
    if signed_area(ring) * signed_area(hx) < 0: ring = ring[::-1]
    best = None
    for s in range(N):
        r = np.roll(ring, -s, axis=0)
        c = ((r - hx) ** 2).sum()
        if best is None or c < best[0]: best = (c, r)
    return best[1]

def polys(g):
    if g.geom_type == 'Polygon': return [g]
    return [p for p in g.geoms if p.geom_type == 'Polygon']

out_cells = []; extras = []; outlines = {}; labels = {}
for k, s in states.items():
    g = s['g'].buffer(0)
    cs = [c for c in cells if c['st'] == k]
    n = len(cs)
    if n == 1:
        parts = [g]
    else:
        P = sample_pts(g, math.sqrt(g.area / 6000))
        C = kmeans(P, n)
        vor = voronoi_diagram(MultiPoint([tuple(c) for c in C]), envelope=g.buffer(5000))
        parts = []
        for cell in vor.geoms:
            inter = cell.intersection(g)
            if inter.is_empty: parts.append(Polygon()); continue
            parts.append(inter)
        # order parts by center to match C ordering not needed; we match geometrically below
    # match parts to hexes by normalized centroid positions
    pc = np.array([p.centroid.coords[0] if not p.is_empty else (0, 0) for p in parts])
    hc = np.array([(c['x'], c['y']) for c in cs])
    def norm(A):
        B = A - A.mean(0); r = np.sqrt((B ** 2).sum(1).mean()) or 1; return B / r
    cost = ((norm(pc)[:, None, :] - norm(hc)[None]) ** 2).sum(2) if n > 1 else np.zeros((1, 1))
    ri, ci = linear_sum_assignment(cost)
    for a, b in zip(ri, ci):
        part = parts[a]; c = cs[b]
        pl = sorted(polys(part), key=lambda p: -p.area)
        main = pl[0]
        for q in pl[1:]:
            if q.area > 400: extras.append(dict(st=k, d=q))
        ring = resample(list(main.exterior.coords), N)
        ring = align(ring, hex_ring(c['x'], c['y']))
        c['g'] = ring
    # outline (true boundary), simplified
    gs = g.simplify(5, preserve_topology=True)
    outlines[k] = gs
    # label spot
    mic = shapely.maximum_inscribed_circle(max(polys(g), key=lambda p: p.area), tolerance=8)
    c0 = mic.coords[0]; rad = mic.length
    labels[k] = [c0[0], c0[1], rad]

def path(g, d=1):
    f = lambda p: f'{p[0]:.{d}f},{p[1]:.{d}f}'
    o = ''
    for pg in polys(g):
        for ring in [pg.exterior] + list(pg.interiors):
            cc = list(ring.coords)[:-1]
            o += 'M' + 'L'.join(f(p) for p in cc) + 'Z'
    return o

ex_out = []
for e in extras:
    es = e['d'].simplify(7)
    ex_out.append(dict(st=e['st'], d=path(es, 0)))

allx = [c['x'] for c in cells]; ally = [c['y'] for c in cells]
bx = [min(min(allx) - S, min(s['g'].bounds[0] for s in states.values())), min(min(ally) - S, min(s['g'].bounds[1] for s in states.values())),
      max(max(allx) + S, max(s['g'].bounds[2] for s in states.values())), max(max(ally) + S, max(s['g'].bounds[3] for s in states.values()))]

ghost = unary_union([s['g'].buffer(0) for s in states.values()]).buffer(3).simplify(7)
data = dict(ghost=path(ghost, 0), S=S, N=N, bounds=[round(v) for v in bx],
            cells=[dict(x=round(c['x'], 3), y=round(c['y'], 3), st=c['st'], g=[round(float(v), 1) for v in c['g'].flatten()]) for c in cells],
            extras=ex_out,
            outlines={k: path(g) for k, g in outlines.items()},
            labels={k: [round(v) for v in labels[k]] for k in labels},
            area={k: round(states[k]['area']) for k in states})
data['cells'].sort(key=lambda c: c['st']=='DC')
json.dump(data, open(D + 'geo.json', 'w'), separators=(',', ':'))
import os
print('bytes', os.path.getsize(D + 'geo.json'), 'bounds', data['bounds'], 'extras', len(ex_out))

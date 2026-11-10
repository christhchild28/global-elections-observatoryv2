import json, math, re, warnings
warnings.filterwarnings('ignore')
import numpy as np, shapely
from shapely.geometry import Polygon, MultiPoint, LineString
from shapely.ops import voronoi_diagram, unary_union
from scipy.optimize import linear_sum_assignment
D = json.load(open('D.json'))
S = D['S']; W = math.sqrt(3) * S; N = 60
rng = np.random.default_rng(7)
lat = D['lat']
def snap(x, y):
    r = round((y - lat['y0']) / (1.5 * S))
    c = round((x - lat['x0'] - (W / 2 if r % 2 else 0)) / W)
    return lat['x0'] + (W / 2 if r % 2 else 0) + c * W, lat['y0'] + r * 1.5 * S
ang = lambda k: math.radians(90 + 60 * k)
def hex_ring(cx, cy, s=S):
    v = [(cx + s * math.cos(ang(k)), cy + s * math.sin(ang(k))) for k in range(6)]
    per = N // 6; out = []
    for k in range(6):
        a, b = v[k], v[(k + 1) % 6]
        for j in range(per):
            u = j / per; out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return np.array(out[::-1])
def parse(d):
    pts = [tuple(map(float, p.split(','))) for p in re.findall(r'-?[\d.]+,-?[\d.]+', d)]
    return Polygon(pts).buffer(0)
def sample_pts(g, step):
    minx, miny, maxx, maxy = g.bounds
    pts = shapely.points(np.array([(x, y) for x in np.arange(minx, maxx, step) for y in np.arange(miny, maxy, step)]))
    m = shapely.contains(g, pts)
    return np.array([(p.x, p.y) for p in pts[m]])
def kmeans(P, k, iters=60):
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
def resample(coords, n):
    ls = LineString(coords); tot = ls.length
    return np.array([ls.interpolate(tot * i / n).coords[0] for i in range(n)])
def sarea(P):
    x, y = P[:, 0], P[:, 1]; return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
def align(ring, hx):
    if sarea(ring) * sarea(hx) < 0: ring = ring[::-1]
    best = None
    for s in range(N):
        r = np.roll(ring, -s, axis=0); c = ((r - hx) ** 2).sum()
        if best is None or c < best[0]: best = (c, r)
    return best[1]
def polys(g):
    return [g] if g.geom_type == 'Polygon' else [p for p in g.geoms if p.geom_type == 'Polygon']
def path(g, d=1):
    f = lambda p: f'{p[0]:.{d}f},{p[1]:.{d}f}'
    o = ''
    for pg in polys(g):
        for ring in [pg.exterior] + list(pg.interiors):
            o += 'M' + 'L'.join(f(p) for p in list(ring.coords)[:-1]) + 'Z'
    return o
cells = []
for c in D['cells']:
    x, y = snap(c['x'], c['y']); cells.append(dict(x=x, y=y, m=c['m'], assert_d=math.hypot(x - c['x'], y - c['y'])))
print('max snap error', max(c['assert_d'] for c in cells))
shape_of = {}
for L in D['land']:
    for m in L['mirs']: shape_of[m] = L['label']
out_cells = []; outlines = {}; labels = {}; area = {}; names = {}; geoms = []
for L in D['land']:
    code = L['label']; g = parse(L['d']); geoms.append(g)
    cs = [c for c in cells if shape_of.get(c['m']) == code]; n = len(cs)
    if n == 1: parts = [g]
    else:
        P = sample_pts(g, math.sqrt(g.area / 6000)); C = kmeans(P, n)
        vor = voronoi_diagram(MultiPoint([tuple(c) for c in C]), envelope=g.buffer(5000))
        parts = [cell.intersection(g) if not cell.intersection(g).is_empty else Polygon() for cell in vor.geoms]
    pc = np.array([p.centroid.coords[0] if not p.is_empty else (0, 0) for p in parts])
    hc = np.array([(c['x'], c['y']) for c in cs])
    def norm(A):
        B = A - A.mean(0); r = np.sqrt((B ** 2).sum(1).mean()) or 1; return B / r
    cost = ((norm(pc)[:, None, :] - norm(hc)[None]) ** 2).sum(2) if n > 1 else np.zeros((1, 1))
    ri, ci = linear_sum_assignment(cost)
    for a, b in zip(ri, ci):
        main = sorted(polys(parts[a]), key=lambda p: -p.area)[0]
        c = cs[b]; c['st'] = code
        c['g'] = align(resample(list(main.exterior.coords), N), hex_ring(c['x'], c['y']))
    outlines[code] = path(g, 1)
    mic = shapely.maximum_inscribed_circle(max(polys(g), key=lambda p: p.area), tolerance=0.5)
    c0 = mic.coords[0]; labels[code] = [round(c0[0], 1), round(c0[1], 1), round(mic.length, 1)]
    area[code] = L['area']; names[code] = L['label2']
for c in cells:
    if 'st' not in c:
        c['st'] = 'ABR'; c['g'] = hex_ring(c['x'], c['y'], S * 0.2)
outlines['ABR'] = ''; labels['ABR'] = [0, 0, 0]; area['ABR'] = 0; names['ABR'] = 'Abroad'
ghost = unary_union([g.buffer(0) for g in geoms]).buffer(1.5).simplify(1.2)
bx = D['bounds']
data = dict(S=S, N=N, bounds=[round(v, 1) for v in bx], ghost=path(ghost, 1), extras=[],
    cells=[dict(x=round(c['x'], 6), y=round(c['y'], 6), st=c['st'], gr=[round(float(v), 1) for v in c['g'].flatten()]) for c in cells],
    outlines=outlines, labels=labels, area=area, names=names)
json.dump(data, open('geo.json', 'w'), separators=(',', ':'))
import os; print('bytes', os.path.getsize('geo.json'), 'cells', len(cells), {k: sum(1 for c in cells if c['st'] == k) for k in ['PLD', 'SOF', 'ABR', 'BLG']})

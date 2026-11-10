#!/usr/bin/env python3
"""
hexpack: arrange hexagon tiles into a solid hex cartogram whose clusters stay where
the real regions are and fit together like puzzle pieces.

Inputs : planar (equal-area, km) region polygons + a hex count per region.
Output : lattice cells {x, y, st} (north-up km coordinates) ready for a morphing page.

How it works
  1. Seed   : contract the region centroids, relax them so hex-sized circles don't overlap,
              then assign lattice cells to regions with an optimal-transport (Hungarian) match.
  2. Refine : simulated annealing over two connectivity-safe moves
                swap     - exchange one boundary cell between two touching clusters
                relocate - slide one boundary cell of a cluster into an empty neighbouring slot
              minimising
                + cluster perimeter                       (compact, tight jigsaw)
                + outer perimeter of the whole blob       (solid silhouette)
                + real neighbours that do not touch       (and a bonus for long real borders)
                + touching regions that are not real neighbours
                + distance of each cluster from its target position (global scale and shift are refit,
                  so the whole map can shrink uniformly but stay in place relatively)
                + direction between neighbouring clusters vs the real direction
                + cluster long-axis vs the real region's long axis (only for elongated regions)
              Hard rules: every cluster stays connected, the blob stays connected and has no holes.

CLI:
  hexpack.py regions.geojson --id-prop sigla --values values.json --per 1000000 --out layout.json
  (values.json = {id: number}; or pass --counts counts.json = {id: hex count})
"""
import json, math, random, argparse, sys, time
from collections import defaultdict
import numpy as np
from scipy.optimize import linear_sum_assignment

DIRS = [(2, 0), (-2, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]   # pointy-top lattice, kx+ky even


def counts_from_values(values, per):
    tot = sum(values.values())
    raw = {k: v / per for k, v in values.items()}
    cnt = {k: max(1, int(math.floor(r))) for k, r in raw.items()}
    need = round(tot / per) - sum(cnt.values())
    order = sorted(raw, key=lambda k: -(raw[k] - math.floor(raw[k])))
    i = 0
    while need > 0:
        cnt[order[i % len(order)]] += 1; need -= 1; i += 1
    return cnt


def real_geometry(polys, adj_tol=12.0, min_border=25.0):
    """centroids, shared-border lengths, long-axis angle + elongation of each region (km, north-up)."""
    ids = list(polys)
    cen = {k: np.array(polys[k].centroid.coords[0]) for k in ids}
    border = {}
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if not polys[a].buffer(adj_tol).intersects(polys[b]): continue
            L = polys[a].boundary.intersection(polys[b].buffer(adj_tol)).length / 1.0
            if L >= min_border: border[(a, b)] = L
    axis = {}
    for k in ids:
        r = polys[k].minimum_rotated_rectangle
        c = list(r.exterior.coords)[:4]
        e = [(c[(i + 1) % 4][0] - c[i][0], c[(i + 1) % 4][1] - c[i][1]) for i in range(4)]
        ln = [math.hypot(*v) for v in e]
        j = int(np.argmax(ln[:2]))
        phi = math.atan2(e[j][1], e[j][0])
        ratio = max(ln[:2]) / max(1e-9, min(ln[:2]))
        axis[k] = (phi, ratio)
    return ids, cen, border, axis


class Packer:
    def __init__(self, polys, counts, S=112.0, seed=1, w=None):
        self.S = S; self.W = math.sqrt(3) * S
        self.ids, self.cen, self.border, self.axis = real_geometry(polys)
        self.n = len(self.ids); self.ix = {k: i for i, k in enumerate(self.ids)}
        self.cnt = [counts[k] for k in self.ids]
        self.rng = random.Random(seed)
        self.w = dict(per=0.5, outer=0.45, adj=6.0, contact=1.2, false=0.9, pos=0.35, dir=1.6, orient=1.0, comp=3.0, hole=1.5, iso=0.6, conn=12.0, anchor=0.0)
        if w: self.w.update(w)
        self.adj = []
        for (a, b), L in self.border.items():
            i, j = self.ix[a], self.ix[b]
            if i > j: i, j = j, i
            need = 1 if L < 300 else 2 if L < 800 else 3
            d = self.cen[self.ids[j]] - self.cen[self.ids[i]]
            self.adj.append((i, j, need, d / (np.linalg.norm(d) + 1e-9), min(1.0, L / 300)))
        self.adjset = {(i, j) for i, j, *_ in self.adj}
        self.Q = None; self.relax = False; self.shrink = 0.7
        self.polys = polys; self.anchor_k = None; self.D = None
        if w and 'relax' in w: self.relax = bool(w.pop('relax'))
        if w and 'shrink' in w: self.shrink = w.pop('shrink')
        if w and 'anchor_k' in w: self.anchor_k = w.pop('anchor_k')

    # ---------- coordinates ----------
    def xy(self, k):
        return np.array([k[0] * self.W / 2, k[1] * self.S * 1.5])

    # ---------- seed ----------
    def seed_layout(self):
        S, W = self.S, self.W
        P0 = np.array([self.cen[k] for k in self.ids])
        NH = sum(self.cnt)
        tot_area = sum(0 for _ in [])  # not needed
        hexA = 1.5 * math.sqrt(3) * S * S
        # contraction: a bit tighter than area-preserving so clusters can settle
        rad = np.array([math.sqrt(c) * W * 0.62 + W * 0.25 for c in self.cnt])
        areaR = sum(self.polys_area.values()) if hasattr(self, 'polys_area') else None
        k = self.shrink
        ctr = P0.mean(0) + np.array([0, -300])
        P = ctr + (P0 - ctr) * k; T0 = P.copy()
        for it in range(900 if self.relax else 0):
            F = (T0 - P) * 0.03
            for a in range(self.n):
                for b in range(a + 1, self.n):
                    d = P[a] - P[b]; dist = np.linalg.norm(d) + 1e-9
                    ov = rad[a] + rad[b] - dist
                    if ov > 0:
                        u = d / dist * ov * 0.5
                        F[a] += u * 0.5; F[b] -= u * 0.5
            P += F
        self.Q = P
        xs = P[:, 0]; ys = P[:, 1]
        kx0 = int(math.floor(xs.min() / (W / 2))) - 14; kx1 = int(math.ceil(xs.max() / (W / 2))) + 14
        ky0 = int(math.floor(ys.min() / (1.5 * S))) - 8; ky1 = int(math.ceil(ys.max() / (1.5 * S))) + 8
        lat = [(kx, ky) for ky in range(ky0, ky1 + 1) for kx in range(kx0, kx1 + 1) if (kx + ky) % 2 == 0]
        XY = np.array([self.xy(c) for c in lat])
        NH = sum(self.cnt)
        # 1. choose a solid blob of NH cells: highest smoothed "mass" density around the target positions
        wts = np.array(self.cnt, float)
        blob = None
        for sig in np.arange(1.0, 3.01, 0.2):
            sg = sig * W
            d2 = ((XY[:, None, :] - P[None, :, :]) ** 2).sum(2)
            dens = (wts[None, :] * np.exp(-d2 / (2 * sg * sg))).sum(1)
            top = np.argsort(-dens)[:NH]
            cand = {lat[i]: 0 for i in top}
            if self.solid_pen_cells(set(cand)) == 0:
                blob = [lat[i] for i in top]; break
        if blob is None: blob = [lat[i] for i in np.argsort(-dens)[:NH]]
        # 2. split the blob into clusters with optimal transport (squared distance => compact, convex pieces)
        BXY = np.array([self.xy(c) for c in blob])
        slots = []
        for i in range(self.n): slots += [i] * self.cnt[i]
        cost = np.zeros((len(blob), len(slots)))
        for j, s_ in enumerate(slots): cost[:, j] = ((BXY - P[s_]) ** 2).sum(1)
        ri, ci = linear_sum_assignment(cost)
        return {blob[a_]: slots[b_] for a_, b_ in zip(ri, ci)}

    def solid_pen_cells(self, cells):
        saved = self.w['comp'], self.w['hole']
        r = self.solid_pen({c: 0 for c in cells})
        return r

    # ---------- anchored mode: keep every cluster near its real territory ----------
    def prepare_anchor(self):
        import shapely
        from shapely.affinity import scale as shp_scale
        from shapely.ops import unary_union
        S, W = self.S, self.W
        U = unary_union(list(self.polys.values())); c0 = U.centroid
        self.sp_polys = [shp_scale(self.polys[k], self.anchor_k, self.anchor_k, origin=c0) for k in self.ids]
        minx, miny, maxx, maxy = unary_union(self.sp_polys).bounds
        kx0 = int(math.floor(minx / (W / 2))) - 14; kx1 = int(math.ceil(maxx / (W / 2))) + 14
        ky0 = int(math.floor(miny / (1.5 * S))) - 8; ky1 = int(math.ceil(maxy / (1.5 * S))) + 8
        self.lat = [(kx, ky) for ky in range(ky0, ky1 + 1) for kx in range(kx0, kx1 + 1) if (kx + ky) % 2 == 0]
        XY = np.array([self.xy(c) for c in self.lat]); pts = shapely.points(XY)
        self.D = []
        for pg in self.sp_polys:
            d = shapely.distance(pg, pts) / W
            self.D.append(dict(zip(self.lat, d.tolist())))
        self.sc_cen = np.array([[p.centroid.x, p.centroid.y] for p in self.sp_polys])

    def seed_anchored(self):
        W = self.W
        XY = np.array([self.xy(c) for c in self.lat])
        slots = []
        for i in range(self.n): slots += [i] * self.cnt[i]
        cost = np.zeros((len(self.lat), len(slots)))
        for j, s_ in enumerate(slots):
            dpoly = np.array([self.D[s_][c] for c in self.lat])
            dcen = ((XY - self.sc_cen[s_]) ** 2).sum(1) / W ** 2
            cost[:, j] = dpoly ** 2 + self.w.get('seedc', 0.03) * dcen
        ri, ci = linear_sum_assignment(cost)
        return {self.lat[a]: slots[b] for a, b in zip(ri, ci)}

    # ---------- structural helpers ----------
    @staticmethod
    def nbrs(c):
        return [(c[0] + dx, c[1] + dy) for dx, dy in DIRS]

    def ncomp(self, cells):
        cs = set(cells); n = 0; seen = set()
        for c in cs:
            if c in seen: continue
            n += 1; st = [c]; seen.add(c)
            while st:
                u = st.pop()
                for v in self.nbrs(u):
                    if v in cs and v not in seen: seen.add(v); st.append(v)
        return n

    @staticmethod
    def hdist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1]); return max(dy, (dx + dy) // 2)

    def components(self, cells):
        cs = set(cells); out = []; seen = set()
        for c in cs:
            if c in seen: continue
            comp = [c]; st = [c]; seen.add(c)
            while st:
                u = st.pop()
                for v in self.nbrs(u):
                    if v in cs and v not in seen: seen.add(v); st.append(v); comp.append(v)
            out.append(comp)
        return out

    def repair(self, own, max_steps=200):
        """reconnect any cluster the seed left in pieces: walk the stranded piece towards the main body,
        swapping owners with the cell in front of it, preferring swaps that break nothing else."""
        for _ in range(max_steps):
            broken = None
            for i in range(self.n):
                comps = self.components([c for c, s_ in own.items() if s_ == i])
                if len(comps) > 1: broken = (i, sorted(comps, key=len)); break
            if not broken: return True
            i, comps = broken
            small, rest = comps[0], [c for cc in comps[1:] for c in cc]
            u, m = min(((a, b) for a in small for b in rest), key=lambda ab: self.hdist(*ab))
            fwd = [v for v in self.nbrs(u) if v in own and own[v] != i and self.hdist(v, m) < self.hdist(u, m)]
            if not fwd: return False
            best = None
            for v in fwd:
                t = own[v]; before = self.ncomp([c for c, s_ in own.items() if s_ == t])
                own[u] = t; own[v] = i
                after = self.ncomp([c for c, s_ in own.items() if s_ == t])
                mine = self.ncomp([c for c, s_ in own.items() if s_ == i])
                own[u] = i; own[v] = t
                score = (after - before, mine)
                if best is None or score < best[0]: best = (score, v)
            v = best[1]; t = own[v]; own[u] = t; own[v] = i
        return False

    def repair_relocate(self, own):
        """last resort: move stray cells of a split cluster to free slots touching its main body."""
        for i in range(self.n):
            comps = sorted(self.components([c for c, s_ in own.items() if s_ == i]), key=len)
            if len(comps) < 2: continue
            main = set(comps[-1])
            for comp in comps[:-1]:
                for u in comp:
                    free = {v for m in main for v in self.nbrs(m) if v not in own}
                    if not free: return False
                    e = min(free, key=lambda v: self.hdist(u, v))
                    del own[u]; own[e] = i; main.add(e)
        return True

    def comps_ok(self, own, cells):
        if not cells: return True
        cs = set(cells); st = [next(iter(cs))]; seen = {st[0]}
        while st:
            u = st.pop()
            for v in self.nbrs(u):
                if v in cs and v not in seen: seen.add(v); st.append(v)
        return len(seen) == len(cs)

    def solid_pen(self, own):
        """soft penalty: extra components of the blob and enclosed empty cells (holes)."""
        if self.w['comp'] == 0 and self.w['hole'] == 0: return 0.0
        cells = set(own); seen = set(); comps = 0
        for c in cells:
            if c in seen: continue
            comps += 1; st = [c]; seen.add(c)
            while st:
                u = st.pop()
                for v in self.nbrs(u):
                    if v in cells and v not in seen: seen.add(v); st.append(v)
        xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
        x0, x1, y0, y1 = min(xs) - 2, max(xs) + 2, min(ys) - 1, max(ys) + 1
        start = (x0 if (x0 + y0) % 2 == 0 else x0 + 1, y0)
        out = {start}; st = [start]
        while st:
            u = st.pop()
            for v in self.nbrs(u):
                if x0 <= v[0] <= x1 and y0 <= v[1] <= y1 and v not in cells and v not in out: out.add(v); st.append(v)
        empty = sum(1 for ky in range(y0, y1 + 1) for kx in range(x0, x1 + 1) if (kx + ky) % 2 == 0 and (kx, ky) not in cells)
        return self.w['comp'] * (comps - 1) + self.w['hole'] * (empty - len(out))

    def solid(self, own):
        cells = set(own)
        if not self.comps_ok(own, cells): return False
        xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
        x0, x1, y0, y1 = min(xs) - 2, max(xs) + 2, min(ys) - 1, max(ys) + 1
        start = (x0 if (x0 + y0) % 2 == 0 else x0 + 1, y0)
        seen = {start}; st = [start]
        while st:
            u = st.pop()
            for v in self.nbrs(u):
                if x0 <= v[0] <= x1 and y0 <= v[1] <= y1 and v not in cells and v not in seen: seen.add(v); st.append(v)
        total_empty = sum(1 for ky in range(y0, y1 + 1) for kx in range(x0, x1 + 1) if (kx + ky) % 2 == 0 and (kx, ky) not in cells)
        return len(seen) == total_empty

    # ---------- energy ----------
    def energy(self, own, parts=False):
        w = self.w; n = self.n
        pair = defaultdict(int); outer = 0; bnd = [0] * n
        sx = [0.0] * n; sy = [0.0] * n; sxx = [0.0] * n; sxy = [0.0] * n; syy = [0.0] * n
        cl = [[] for _ in range(n)]
        for c, s in own.items():
            kx, ky = c
            sx[s] += kx; sy[s] += ky; sxx[s] += kx * kx; sxy[s] += kx * ky; syy[s] += ky * ky
            cl[s].append(c)
            for dx, dy in DIRS:
                t = own.get((kx + dx, ky + dy))
                if t is None: outer += 1; bnd[s] += 1
                elif t != s:
                    bnd[s] += 1
                    if s < t: pair[(s, t)] += 1
        per = sum(pair.values())
        false = sum(v for p, v in pair.items() if p not in self.adjset)
        hw, hh = self.W / 2, 1.5 * self.S
        C = np.array([[sx[i] / self.cnt[i] * hw, sy[i] / self.cnt[i] * hh] for i in range(n)])
        # refit global scale/shift of targets
        T = self.T
        pos = 0.0
        for i in range(n):
            d = C[i] - T[i]
            pos += math.sqrt(self.cnt[i]) * (d @ d) / (self.W ** 2)
        e_adj = 0.0; e_dir = 0.0
        for i, j, need, u, wt in self.adj:
            c = pair.get((i, j), 0)
            if c == 0:
                A = np.array(cl[i]); B = np.array(cl[j])
                dx = np.abs(A[:, None, 0] - B[None, :, 0]); dy = np.abs(A[:, None, 1] - B[None, :, 1])
                dmin = np.maximum(dy, (dx + dy) // 2).min()
                e_adj += w['adj'] * (dmin - 1) ** 2
            e_adj += w['contact'] * max(0, need - c)
            v = C[j] - C[i]; nv = np.linalg.norm(v) + 1e-9
            e_dir += wt * (1 - (v @ u) / nv)
        e_or = 0.0
        for i in range(n):
            phi_r, er = self.axis[self.ids[i]]
            if self.cnt[i] < 5 or er < 1.35: continue
            m = self.cnt[i]
            mx = sx[i] / m; my = sy[i] / m
            vx = (sxx[i] / m - mx * mx) * hw * hw; vy = (syy[i] / m - my * my) * hh * hh; cv = (sxy[i] / m - mx * my) * hw * hh
            tr = vx + vy; det = vx * vy - cv * cv; disc = math.sqrt(max(0, tr * tr / 4 - det))
            l1 = tr / 2 + disc; l2 = max(1e-6, tr / 2 - disc)
            elong = 1 - math.sqrt(l2 / max(l1, 1e-9))
            phi = 0.5 * math.atan2(2 * cv, vx - vy)
            e_or += (1 - math.cos(2 * (phi - phi_r))) * min(er - 1, 1.5) * elong
        e_anchor = 0.0
        if self.D is not None:
            for c, s_ in own.items(): e_anchor += self.D[s_].get(c, 6.0) ** 2
        e_conn = sum(self.ncomp(cl[i]) - 1 for i in range(n))
        e_iso = sum(max(0.0, bnd[i] - 2 * math.sqrt(12 * self.cnt[i] - 3)) for i in range(n))
        parts_ = dict(anchor=w['anchor'] * e_anchor, conn=w['conn'] * e_conn, iso=w['iso'] * e_iso, per=w['per'] * per, outer=w['outer'] * outer, adj=e_adj, false=w['false'] * false,
                      pos=w['pos'] * pos, dir=w['dir'] * e_dir, orient=w['orient'] * e_or)
        tot = sum(parts_.values())
        return (tot, parts_, pair, C) if parts else tot

    def refit_targets(self, own):
        n = self.n; hw, hh = self.W / 2, 1.5 * self.S
        sx = np.zeros(n); sy = np.zeros(n)
        for c, s in own.items(): sx[s] += c[0]; sy[s] += c[1]
        C = np.stack([sx / self.cnt * hw, sy / self.cnt * hh], 1)
        wts = np.sqrt(np.array(self.cnt, float))
        q = self.Q; mq = (wts[:, None] * q).sum(0) / wts.sum(); mc = (wts[:, None] * C).sum(0) / wts.sum()
        qq = q - mq; cc = C - mc
        kappa = float((wts * (qq * cc).sum(1)).sum() / (wts * (qq * qq).sum(1)).sum())
        kappa = min(1.15, max(0.55, kappa))
        self.T = mc + kappa * qq

    # ---------- moves ----------
    def try_move(self, own, cells_of):
        r = self.rng
        keys = list(own)
        if r.random() < 0.6:
            u = r.choice(keys); s = own[u]
            others = [own[v] for v in self.nbrs(u) if v in own and own[v] != s]
            if not others: return None
            t = r.choice(others)
            wc = [c for c in cells_of[t] if any(own.get(v) == s for v in self.nbrs(c))]
            if not wc: return None
            wcell = r.choice(wc)
            b_s, b_t = self.ncomp(cells_of[s]), self.ncomp(cells_of[t])
            own[u] = t; own[wcell] = s
            cells_of[s].remove(u); cells_of[s].add(wcell); cells_of[t].remove(wcell); cells_of[t].add(u)
            ok = self.ncomp(cells_of[s]) <= max(1, b_s) and self.ncomp(cells_of[t]) <= max(1, b_t)
            def undo():
                own[u] = s; own[wcell] = t
                cells_of[s].add(u); cells_of[s].remove(wcell); cells_of[t].add(wcell); cells_of[t].remove(u)
            return ok, undo, False
        else:
            u = r.choice(keys); s = own[u]
            empt = [v for v in self.nbrs(u) if v not in own]
            if not empt: return None
            e = r.choice(empt)
            b_s = self.ncomp(cells_of[s])
            del own[u]; own[e] = s
            cells_of[s].remove(u); cells_of[s].add(e)
            ok = self.ncomp(cells_of[s]) <= max(1, b_s)
            def undo():
                del own[e]; own[u] = s
                cells_of[s].remove(e); cells_of[s].add(u)
            return ok, undo, True

    def run(self, iters=80000, T0=2.5, T1=0.04, log=True):
        if self.anchor_k:
            self.prepare_anchor(); self.Q = np.array([self.cen[k] for k in self.ids]); own = self.seed_anchored()
        else:
            own = self.seed_layout()
        if not self.repair(own) and log: print('  warning: seed repair incomplete')
        cells_of = [set() for _ in range(self.n)]
        for c, s in own.items(): cells_of[s].add(c)
        self.T = self.Q.copy(); self.refit_targets(own)
        self.sp = self.solid_pen(own)
        E = self.energy(own) + self.sp; best = (E, dict(own), self.sp)
        t0 = time.time(); acc = 0
        for it in range(iters):
            temp = T0 * (T1 / T0) ** (it / iters)
            if it % 2000 == 0:
                self.refit_targets(own); E = self.energy(own) + self.sp
                if log and it % 10000 == 0: print(f'  it {it:6d}  E={E:8.2f}  T={temp:.3f}  acc={acc}  {time.time()-t0:.0f}s', flush=True)
            mv = self.try_move(own, cells_of)
            if mv is None: continue
            ok, undo, reloc = mv
            if not ok: undo(); continue
            sp2 = self.solid_pen(own) if reloc else self.sp
            E2 = self.energy(own) + sp2
            if E2 <= E or self.rng.random() < math.exp((E - E2) / temp):
                E = E2; self.sp = sp2; acc += 1
                if E < best[0]: best = (E, dict(own), sp2)
            else: undo()
        # restore best and finish with a greedy pass
        own = best[1]; self.sp = best[2]
        if not self.repair(own): self.repair_relocate(own)
        cells_of = [set() for _ in range(self.n)]
        for c, s in own.items(): cells_of[s].add(c)
        self.refit_targets(own); E = self.energy(own) + self.sp
        for it in range(8000):
            mv = self.try_move(own, cells_of)
            if mv is None: continue
            ok, undo, reloc = mv
            if not ok: undo(); continue
            sp2 = self.solid_pen(own) if reloc else self.sp
            E2 = self.energy(own) + sp2
            if E2 < E - 1e-9: E = E2; self.sp = sp2
            else: undo()
        self.own = own
        return own

    def report(self, own):
        tot, parts, pair, C = self.energy(own, parts=True)
        missing = [(self.ids[i], self.ids[j]) for i, j, need, u, wt in self.adj if pair.get((i, j), 0) == 0]
        false = sum(v for p, v in pair.items() if p not in self.adjset)
        disp = [float(np.linalg.norm(C[i] - self.T[i]) / self.W) for i in range(self.n)]
        cs = []
        for i, j, need, u, wt in self.adj:
            v = C[j] - C[i]; cs.append(float(v @ u / (np.linalg.norm(v) + 1e-9)))
        cl = defaultdict(list)
        for c, s_ in own.items(): cl[s_].append(c)
        disc = [self.ids[i] for i in range(self.n) if self.ncomp(cl[i]) > 1]
        return dict(disconnected=disc, energy=round(tot, 2), parts={k: round(v, 2) for k, v in parts.items()},
                    adjacent_pairs=len(self.adj), touching=len(self.adj) - len(missing), missing=missing,
                    false_contact_edges=false, cluster_perimeter_edges=sum(pair.values()),
                    mean_disp_hex=round(float(np.mean(disp)), 2), dir_cos_mean=round(float(np.mean(cs)), 2), dir_cos_negative=int(sum(1 for c in cs if c < 0)), max_disp_hex=round(max(disp), 2))

    def to_cells(self, own):
        return [dict(x=float(self.xy(c)[0]), y=float(self.xy(c)[1]), st=self.ids[s]) for c, s in sorted(own.items())]


def project_auto_albers(geojson, id_prop):
    """equal-area Albers fitted to the data's bbox, returns {id: shapely polygon in km}."""
    from shapely.geometry import shape
    import shapely
    feats = geojson['features']
    allb = [shape(f['geometry']).bounds for f in feats]
    lon0 = (min(b[0] for b in allb) + max(b[2] for b in allb)) / 2
    lat_lo = min(b[1] for b in allb); lat_hi = max(b[3] for b in allb)
    lat1, lat2, lat0 = map(math.radians, (lat_lo + (lat_hi - lat_lo) / 6, lat_hi - (lat_hi - lat_lo) / 6, (lat_lo + lat_hi) / 2))
    lon0 = math.radians(lon0); R = 6371.0088
    nn = (math.sin(lat1) + math.sin(lat2)) / 2; C = math.cos(lat1) ** 2 + 2 * nn * math.sin(lat1)
    rho0 = R * math.sqrt(C - 2 * nn * math.sin(lat0)) / nn
    def pr(a):
        lon = np.radians(a[:, 0]); lat = np.radians(a[:, 1])
        rho = R * np.sqrt(C - 2 * nn * np.sin(lat)) / nn; th = nn * (lon - lon0)
        return np.stack([rho * np.sin(th), rho0 - rho * np.cos(th)], 1)
    out = {}
    for f in feats:
        g = shapely.transform(shape(f['geometry']), pr).buffer(0)
        out[f['properties'][id_prop]] = g
    return out


def main():
    ap = argparse.ArgumentParser(description='Pack hexagons into a position-faithful, tightly fitted cartogram.')
    ap.add_argument('geojson'); ap.add_argument('--id-prop', required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--counts'); g.add_argument('--values')
    ap.add_argument('--per', type=float, default=1.0, help='value per hexagon when --values is used')
    ap.add_argument('--S', type=float, default=112.0, help='hex circumradius in km')
    ap.add_argument('--iters', type=int, default=80000); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    gj = json.load(open(a.geojson)); polys = project_auto_albers(gj, a.id_prop)
    counts = json.load(open(a.counts)) if a.counts else counts_from_values(json.load(open(a.values)), a.per)
    pk = Packer(polys, counts, S=a.S, seed=a.seed)
    own = pk.run(a.iters)
    rep = pk.report(own); print(json.dumps(rep, indent=1))
    json.dump(dict(S=a.S, cells=pk.to_cells(own), report=rep), open(a.out, 'w'))


if __name__ == '__main__':
    main()

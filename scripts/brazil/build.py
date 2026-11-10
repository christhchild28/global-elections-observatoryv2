import json, math, sys
import numpy as np
from shapely.geometry import shape, Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union, transform
from shapely import affinity
from scipy.optimize import linear_sum_assignment

D = '/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/br/'
g = json.load(open(D + 'states.geojson'))

# ---- Albers equal-area (Brazil) in km ----
R = 6371.0088
lat1, lat2, lat0, lon0 = map(math.radians, (-2, -22, -12, -54))
n = (math.sin(lat1) + math.sin(lat2)) / 2
C = math.cos(lat1) ** 2 + 2 * n * math.sin(lat1)
rho0 = R * math.sqrt(C - 2 * n * math.sin(lat0)) / n
def proj(lon, lat, z=None):
    lon = np.radians(lon); lat = np.radians(lat)
    rho = R * np.sqrt(C - 2 * n * np.sin(lat)) / n
    th = n * (lon - lon0)
    return rho * np.sin(th), rho0 - rho * np.cos(th)

ELEC = dict(AC=613700, AL=2400000, AM=2800000, AP=577000, BA=11321005, CE=7000000, DF=2300000, ES=3000000,
            GO=5100000, MA=5200000, MG=16377659, MS=2000000, MT=2600000, PA=6300000, PB=3200000, PE=7200000,
            PI=2700000, PR=8609026, RJ=12857000, RN=2700000, RO=1300000, RR=401500, RS=8500000, SC=5700000,
            SE=1700000, SP=34104226, TO=1200000)

states = {}
for f in g['features']:
    sg = f['properties']['sigla']
    geom = shape(f['geometry'])
    pg = transform(proj, geom)
    pg = pg.buffer(0)
    states[sg] = dict(name=f['properties']['name'], reg=f['properties']['regiao_id'], geom=pg, area=pg.area)

if __name__ == '__main__':
    tot = sum(s['area'] for s in states.values())
    print('total km2', round(tot))
    for k, s in sorted(states.items(), key=lambda kv: -kv[1]['area']):
        print(k, s['name'], round(s['area']))
    print('sum elec', sum(ELEC.values()))

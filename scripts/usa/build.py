import json, math, numpy as np
from shapely.geometry import shape
from shapely.ops import transform
from shapely import affinity
D='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/us/'
g=json.load(open(D+'states.geojson'))
AB=dict(Alabama='AL',Alaska='AK',Arizona='AZ',Arkansas='AR',California='CA',Colorado='CO',Connecticut='CT',Delaware='DE',**{'District of Columbia':'DC'},Florida='FL',Georgia='GA',Hawaii='HI',Idaho='ID',Illinois='IL',Indiana='IN',Iowa='IA',Kansas='KS',Kentucky='KY',Louisiana='LA',Maine='ME',Maryland='MD',Massachusetts='MA',Michigan='MI',Minnesota='MN',Mississippi='MS',Missouri='MO',Montana='MT',Nebraska='NE',Nevada='NV',**{'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND'},Ohio='OH',Oklahoma='OK',Oregon='OR',Pennsylvania='PA',**{'Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD'},Tennessee='TN',Texas='TX',Utah='UT',Vermont='VT',Virginia='VA',Washington='WA',**{'West Virginia':'WV'},Wisconsin='WI',Wyoming='WY')
EV=dict(AL=9,AK=3,AZ=11,AR=6,CA=54,CO=10,CT=7,DE=3,DC=3,FL=30,GA=16,HI=4,ID=4,IL=19,IN=11,IA=6,KS=6,KY=8,LA=8,ME=4,MD=10,MA=11,MI=15,MN=10,MS=6,MO=10,MT=4,NE=5,NV=6,NH=4,NJ=4+10,NM=5,NY=28,NC=16,ND=3,OH=17,OK=7,OR=8,PA=19,RI=4,SC=9,SD=3,TN=11,TX=40,UT=6,VT=3,VA=13,WA=12,WV=4,WI=10,WY=3)
assert sum(EV.values())==538,sum(EV.values())
R=6371.0088
def albers(lat1,lat2,lat0,lon0):
    lat1,lat2,lat0,lon0=map(math.radians,(lat1,lat2,lat0,lon0))
    n=(math.sin(lat1)+math.sin(lat2))/2;C=math.cos(lat1)**2+2*n*math.sin(lat1);rho0=R*math.sqrt(C-2*n*math.sin(lat0))/n
    def f(lon,lat,z=None):
        lon=np.radians(lon);lat=np.radians(lat);rho=R*np.sqrt(C-2*n*np.sin(lat))/n;th=n*(lon-lon0)
        return rho*np.sin(th),rho0-rho*np.cos(th)
    return f
P_US=albers(29.5,45.5,37.5,-96);P_AK=albers(55,65,50,-154);P_HI=albers(8,18,3,-157)
states={}
for f in g['features']:
    nm=f['properties']['name']
    if nm not in AB: continue
    k=AB[nm];geom=shape(f['geometry'])
    if k=='AK':
        from shapely.geometry import MultiPolygon
        geom=MultiPolygon([q for q in geom.geoms if q.centroid.x<0])
    pr={'AK':P_AK,'HI':P_HI}.get(k,P_US)
    pg=transform(pr,geom).buffer(0)
    states[k]=dict(name=nm,area=pg.area,geom=pg)
# project y up (north-up km): flip later by consumers. Insets: Alaska 0.4 linear, Hawaii 1.0
def put(k,sc,x0,y0):
    pg=states[k]['geom'];minx,miny,maxx,maxy=pg.bounds
    pg=affinity.scale(pg,sc,sc,origin=(minx,miny));pg=affinity.translate(pg,x0-minx,y0-miny);states[k]['geom']=pg
cx0=min(s['geom'].bounds[0] for k,s in states.items() if k not in('AK','HI'));cy0=min(s['geom'].bounds[1] for k,s in states.items() if k not in('AK','HI'))
print('contig bounds',cx0,cy0,max(s['geom'].bounds[2] for k,s in states.items() if k not in('AK','HI')),max(s['geom'].bounds[3] for k,s in states.items() if k not in('AK','HI')))
put('AK',0.4,cx0+30,cy0-170);put('HI',1.0,cx0+1350,cy0-170)
if __name__=='__main__':
    tot=sum(s['area'] for s in states.values());print(len(states),'total km2',round(tot))
    for k in ['AK','TX','CA','DC','RI','HI']: print(k,round(states[k]['area']),[round(v) for v in states[k]['geom'].bounds])

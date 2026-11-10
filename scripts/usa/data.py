import pandas as pd, json
from build import AB, EV
TURN="""Alabama,58.8,61.8
Alaska,63.7,68.4
Arizona,63.6,68.6
Arkansas,53.5,56.5
California,62.1,68.6
Colorado,73.1,77.6
Connecticut,67.1,70.7
Delaware,67.0,70.1
District of Columbia,63.6,65.8
Florida,66.7,72.3
Georgia,68.3,68.2
Hawaii,50.3,55.7
Idaho,63.4,67.6
Illinois,62.6,66.1
Indiana,58.6,61.5
Iowa,70.8,72.9
Kansas,63.2,65.7
Kentucky,62.1,64.8
Louisiana,60.8,64.2
Maine,74.2,75.8
Maryland,69.3,69.9
Massachusetts,68.0,71.0
Michigan,74.6,73.5
Minnesota,76.4,79.8
Mississippi,57.5,60.4
Missouri,64.3,66.0
Montana,68.2,72.8
Nebraska,68.0,69.5
Nevada,65.8,66.1
New Hampshire,74.1,74.9
New Jersey,67.0,72.0
New Mexico,59.6,61.0
New York,57.9,61.1
North Carolina,70.3,72.8
North Dakota,63.1,63.4
Ohio,65.4,67.0
Oklahoma,53.3,55.3
Oregon,70.7,76.2
Pennsylvania,71.4,70.1
Rhode Island,63.5,63.1
South Carolina,62.1,65.9
South Dakota,64.0,66.4
Tennessee,57.6,59.7
Texas,56.6,60.8
Utah,64.2,69.2
Vermont,70.9,72.2
Virginia,71.0,72.8
Washington,70.2,76.2
West Virginia,55.5,57.2
Wisconsin,76.9,75.3
Wyoming,61.3,64.3"""
T={l.split(',')[0]:(float(l.split(',')[1]),float(l.split(',')[2])) for l in TURN.split('\n')}
assert len(T)==51
D={}
for y in (2024,2020):
    d=pd.read_csv(f'2024_US_County_Level_Presidential_Results.csv' if y==2024 else '2020_US_County_Level_Presidential_Results.csv')
    g=d.groupby('state_name')[['votes_gop','votes_dem','total_votes']].sum()
    D[y]=g
RES={}
for nm,k in AB.items():
    a=D[2024].loc[nm];b=D[2020].loc[nm]
    RES[k]=[int(a.votes_gop),int(a.votes_dem),int(a.total_votes),int(b.votes_gop),int(b.votes_dem),int(b.total_votes),T[nm][0],T[nm][1]]
SPLIT={'ME':{'L':3,'F':1},'NE':{'L':1,'F':4}}
json.dump(dict(RES=RES,EV=EV,SPLIT=SPLIT),open('data.json','w'),separators=(',',':'))
w={'L':0,'F':0}
for k,r in RES.items():
    s=SPLIT.get(k) or {('F' if r[0]>r[1] else 'L'):EV[k]}
    for p,v in s.items(): w[p]+=v
print(w, sum(r[2] for r in RES.values()))
print([k for k,r in RES.items() if (r[0]>r[1])!=(r[3]>r[4])])

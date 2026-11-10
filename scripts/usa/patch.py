t=open('template_src.html').read()
def rep(a,b,cnt=1):
    global t
    assert t.count(a)==cnt,(t.count(a),a[:80]); t=t.replace(a,b)
def splice(s,e,new):
    global t
    i=t.index(s);j=t.index(e,i);t=t[:i]+new+t[j:]
t=t.replace('--lula','--dem').replace('--flavio','--rep')
rep("<title>Brazil State Morph</title>","<title>US Presidential Morph</title>")
rep("--dem:#c8323c;--rep:#1f5fbf;","--dem:#1f5fbf;--rep:#c8323c;")
rep("--dem:#e0545c;--rep:#4a8de0;","--dem:#4a8de0;--rep:#e0545c;",2)
rep('<h1>Brazil: land vs people</h1><p class="sub">The 2026 presidential runoff by state. Tap a state to resize it from its land area to its share of voters, or flip the whole map.</p>','<h1>United States: land vs people</h1><p class="sub">The 2024 presidential election by state. Tap a state to resize it from its land area to its electoral votes, or flip the whole map.</p>')
rep('<button id="bPop" aria-pressed="false">Electorate</button>','<button id="bPop" aria-pressed="false">Electoral votes</button>')
rep('<span class="val" id="ddVal">All 27 states</span>','<span class="val" id="ddVal">All 51 states &amp; DC</span>')
rep('<button data-s="p" aria-pressed="false">Voters</button>','<button data-s="p" aria-pressed="false">Elec. votes</button>')
rep("aria-label=\"Map of Brazil's 27 states; tap a state to resize it by its electorate\"","aria-label=\"Map of the 50 US states and DC; tap a state to resize it by its electoral votes\"")
rep('<span>◀ Flávio</span>','<span>◀ Trump</span>');rep('<span>Lula ▶</span>','<span>Harris ▶</span>')
rep("Flipped since 2022 · shade shows size of swing (full colour at 5+ pts)","Flipped since 2020 · shade shows size of the two-party swing (full colour at 6+ pts)")
# ---- data ----
splice("const REG={","const cells=GEO.cells;","""const cand={L:{n:'Kamala Harris',s:'Harris',p:'Democratic',v:'--dem'},F:{n:'Donald Trump',s:'Trump',p:'Republican',v:'--rep'}};
const ST={};
Object.keys(GEO.area).forEach(k=>{const r=RES[k],f=r[0],l=r[1],tot=r[2],f20=r[3],l20=r[4],t20=r[5],ev=GEO.el[k],sp=SPLIT[k]||(l>f?{L:ev,F:0}:{L:0,F:ev}),ls=l/(l+f)*100,ls20=l20/(l20+f20)*100;
 ST[k]={code:k,name:GEO.names[k],area:GEO.area[k],el:ev,ev,sp,f,l,o:tot-f-l,tot,hs:l/tot*100,ts:f/tot*100,os:(tot-f-l)/tot*100,hs20:l20/t20*100,ts20:f20/t20*100,os20:(t20-f20-l20)/t20*100,ls,ls20,sw:ls-ls20,flip:(ls20>50)!==(ls>50),tn:r[6],tn20:r[7],win:l>f?'L':'F',margin:Math.abs(l-f)/tot*100,lead:Math.abs(l-f)}});
const sgn=(v,u)=>(v>0?'+':v<0?'−':'')+Math.abs(v).toFixed(1)+(u||'');
const states=Object.values(ST),codes=Object.keys(ST);
const totArea=d3.sum(states,s=>s.area),totEl=d3.sum(states,s=>s.el),totF=d3.sum(states,s=>s.f),totL=d3.sum(states,s=>s.l),totAll=d3.sum(states,s=>s.tot);
states.forEach(s=>{s.aPct=s.area/totArea;s.pPct=s.el/totEl;s.nh=0});
""")
rep("const pct=v=>v>=.1?Math.round(v*100)+'%':(v*100).toFixed(1)+'%';","const pct=v=>v>=.1?Math.round(v*100)+'%':v>=.01?(v*100).toFixed(1)+'%':(v*100).toFixed(2)+'%';")
rep(".pn-hd{display:flex;justify-content:space-between;",".pn-hd{display:flex;flex-wrap:wrap;justify-content:space-between;")
rep(".pn-n{font:600 20px/1.15 var(--display);display:block}",".pn-n{font:600 20px/1.15 var(--display);display:block;overflow-wrap:anywhere}")
rep("Math.abs(s.sw)/5","Math.abs(s.sw)/6")
rep("target?'Sized by <b>electorate</b> · 1 hex ≈ 250k voters':mor.size?`<b>${mor.size}</b> resized to voters · 1 hex ≈ 250k · tap to revert`:'Real boundaries · tap a state to resize it'","target?'Sized by <b>electoral votes</b> · 1 hex = 1 electoral vote':mor.size?`<b>${mor.size}</b> resized to electoral votes · tap to revert`:'Real boundaries · tap a state to resize it'")
rep("const elTxt=s=>'≈'+fmt(Math.round(s.el/1e5)*1e5>=1e6?Math.round(s.el/1e5)*1e5:Math.round(s.el/1e3)*1e3);\n","const p1=v=>(v*100).toFixed(1)+'%';\n")
splice("// national strip","const emptyHTML=","""// national strip
const evW={L:0,F:0};states.forEach(s=>{evW.L+=s.sp.L||0;evW.F+=s.sp.F||0});
const agg=Object.fromEntries(['L','F'].map(p=>{const ss=states.filter(s=>s.win===p);return [p,{n:ss.length,a:d3.sum(ss,s=>s.aPct),p:d3.sum(ss,s=>s.pPct),v:(p==='L'?totL:totF)/totAll,ev:evW[p]}]}));
function drawNat(){const lead=evW.F>evW.L?'F':'L',oth=lead==='L'?'F':'L';
 document.getElementById('nat').innerHTML=[lead,oth].map(p=>{const a=agg[p],c=cand[p];return `<div class="nat-r"><span class="nat-n"><i class="dot" style="background:var(${c.v})"></i>${c.s}<small>${c.p}</small></span><span class="nat-s"><b>${a.ev}</b> electoral votes · <b>${a.n}</b> states</span><span class="nat-m">${pct(a.a)} land · <b>${p1(a.v)}</b> of votes</span></div>`}).join('')+
 `<div class="nat-g">${cand[oth].s} won <b>${agg[oth].n}</b> states &amp; DC covering <b>${pct(agg[oth].a)}</b> of the land and <b>${pct(agg[oth].p)}</b> of electoral votes, with <b>${p1(agg[oth].v)}</b> of all votes. State counts go by popular-vote winner; Maine and Nebraska split their electoral votes.</div>`}
// ---- merged panel ----
const sheet=document.getElementById('sheet'),pnBody=document.getElementById('pnBody');
let full=false;
function chipsHTML(){if(mor.size<2||target)return '';const ss=[...mor].map(n=>ST[n]),la=d3.sum(ss,s=>s.aPct),pa=d3.sum(ss,s=>s.pPct);
 return `<div class="pn-chips"><div class="pn-chl">${ss.map(s=>`<button class="chip${s.code===cur?' on':''}" data-k="${s.code}"><i class="dot" style="background:var(${cand[s.win].v})"></i>${s.code}</button>`).join('')}</div><div class="pn-sum"><b>${ss.length} resized</b> hold ${pct(la)} of the land and ${pct(pa)} of electoral votes</div></div>`}
function panelHTML(k){const s=ST[k],c=cand[s.win],rel=(s.ev/s.area)/(totEl/totArea),res=mor.has(k)||target===1,split=SPLIT[k];
 const rtxt=rel>=1.05?`<b>${rel>=10?Math.round(rel):rel.toFixed(1)}×</b> as many electoral votes per km² as the national average`:rel<=.95?`<b>${rel.toFixed(2)}×</b> the national electoral-vote density`:'about the national electoral-vote density';
 const rows=[['L',cand.L.n,s.l,s.hs,s.hs-s.hs20,'var(--dem)'],['F',cand.F.n,s.f,s.ts,s.ts-s.ts20,'var(--rep)'],['O','Other candidates',s.o,s.os,s.os-s.os20,'var(--mute)']].sort((a,b)=>b[2]-a[2]).map((r,i)=>`<tr class="${i===0?'win':''}"><td><span class="nm"><i style="background:${r[5]}"></i><span>${r[1]}</span></span></td><td class="num">${fmt(r[2])}</td><td class="num">${r[3].toFixed(1)}%</td><td class="num">${sgn(r[4])}</td></tr>`).join('');
 const tw=s.sw>0?'L':'F',swH=`<div class="pn-sw"><b style="color:var(${cand[tw].v})">${s.sw>0?'▲':'▼'} ${Math.abs(s.sw).toFixed(1)} pts</b> toward ${cand[tw].s} since 2020${s.flip?` <span class="pn-flip">Flipped to ${c.s}</span>`:''}</div>`;
 const evTxt=split?`${cand.L.s} ${split.L} · ${cand.F.s} ${split.F}`:String(s.ev);
 return `<div class="pn-bar" style="background:var(${c.v})"></div>
 <div class="pn-hd"><div style="min-width:0;flex:1 1 170px"><span class="pn-n">${escH(s.name)}</span><span class="pn-c">${s.code} · ${s.ev} ELECTORAL VOTE${s.ev>1?'S':''}</span></div><div class="pn-r"><span class="pn-p" style="background:var(${c.v})">${c.s} won</span>${mor.has(k)&&!target?'<button class="pn-b pn-rv" data-k="'+k+'">Revert</button>':''}<button class="pn-b pn-tgl" aria-expanded="${full}">${full?'Less':'More'}</button>${peek?'':'<button class="pn-b pn-x" aria-label="Close">✕</button>'}</div></div>
 <div class="pn-key">${barHTML('Land',s.aPct,`var(${c.v})`,!res)}${barHTML('EVs',s.pPct,`var(${c.v})`,res)}<div class="pn-rel">${rtxt}</div>${swH}</div>
 <div class="pn-more"><div class="pn-st"><span>Electoral votes <b>${evTxt}</b></span><span>Votes cast <b>${fmt(s.tot)}</b></span><span>Turnout <b>${s.tn.toFixed(1)}%</b> (${sgn(s.tn-s.tn20)} vs 2020)</span><span>Area <b>${fmt(s.area)} km²</b></span><span>Hexes <b>${s.nh}</b></span><span>Margin <b>${s.margin.toFixed(1)} pts</b> (${fmt(s.lead)})</span></div>
 <table class="pn-t"><thead><tr><th>Candidate</th><th class="num">Votes</th><th class="num">Share</th><th class="num">vs 2020</th></tr></thead><tbody>${rows}</tbody></table></div>`}
""")
rep("<h2>Tap a state</h2><p>It resizes to its share of voters (1 hexagon ≈ 250k) while a dashed line keeps its real shape. Tap again to revert, or tap several to compare.</p>","<h2>Tap a state</h2><p>It resizes to its electoral votes (1 hexagon each) while a dashed line keeps its real shape. Tap again to revert, or tap several to compare. Tiny states such as DC and Rhode Island are easier to pick from the menu.</p>")
rep("(mor.size?mor.size+' resized':'All 27 states')","(mor.size?mor.size+' resized':'All 51 states & DC')")
rep("<span class=\"nm\">All 27 states</span></li>`","<span class=\"nm\">All 51 states &amp; DC</span></li>`")
rep("function metric(s){return sortBy==='p'?'≈'+d3.format('.3~s')(s.el):sortBy==='a'?fmt(s.area)+' km²':s.code}","function metric(s){return sortBy==='p'?s.ev+' EV':sortBy==='a'?fmt(s.area)+' km²':s.code}")
rep("a.name.localeCompare(b.name,'pt')","a.name.localeCompare(b.name)")
rep("const LS='br-tap-morph-v1';","const LS='us-tap-morph-v1';")
i=t.index("document.getElementById('note').textContent='");j=t.index("';",i)+2
t=t[:i]+"document.getElementById('note').textContent='Land view: state boundaries from the US Census cartographic files (us-atlas), drawn in an equal-area projection; areas are boundary areas including coastal water. Alaska is shown at 40% scale and Hawaii at full scale as insets, and DC is drawn as an enlarged circle so it can be seen; the area bars use true sizes. A resized state keeps its centre and gets one hexagon per electoral vote (538 in all), with a dashed line marking its real shape. Results are the 2024 and 2020 certified state totals aggregated from county data (tonmcg/US_County_Level_Election_Results_08-24; Alaska reported by district). Swing is the change in Harris’s share of the two-party vote against Biden’s in 2020; a state is flipped if its popular winner changed. Maine and Nebraska split electoral votes by congressional district: Harris won ME 3–1 and NE 1–4. Turnout is ballots counted as a share of eligible voters as compiled by Ballotpedia, and the change is 2024 minus 2020.';"+t[j:]
rep("window.__mode=setMode;","window.__mode=setMode;window.__ST=ST;")
rep("${s.ev} ELECTORAL VOTE${s.ev>1?'S':''}</span>","${s.ev} EV</span>")
open('template_us.html','w').write(t)
for w in ['Lula','Flávio','L22','AB[','27 states','Brazil','elTxt','.fs','.ls ']:
    print(w,t.count(w))

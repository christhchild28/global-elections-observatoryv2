import re
t=open('template_tap.html').read()
def rep(a,b,cnt=1):
    global t
    assert t.count(a)==cnt,(t.count(a),a[:70]); t=t.replace(a,b)
def splice(s,e,new):
    global t
    i=t.index(s);j=t.index(e,i);t=t[:i]+new+t[j:]
# ---- head/css ----
rep("<title>Brazil State Morph</title>","<title>T&amp;T Seat Morph</title>")
rep("--lula:#c8323c;--flavio:#1f5fbf;","--unc:#e3b13a;--pnm:#c4454f;--tpp:#2a9d8f;")
rep("--lula:#e0545c;--flavio:#4a8de0;","--unc:#e8b94a;--pnm:#d4575f;--tpp:#35b0a1;",2)
rep(".glab{font:600 100px var(--mono);pointer-events:none;text-anchor:middle;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.38);stroke-width:14px;stroke-linejoin:round}",".glab{font:600 1.7px var(--mono);letter-spacing:.02em;pointer-events:none;text-anchor:middle;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.3);stroke-width:.5px;stroke-linejoin:round}")
rep(".slab{font:600 84px var(--mono);pointer-events:none;text-anchor:middle;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.3);stroke-width:12px;stroke-linejoin:round}",".slab{font:600 2.15px var(--mono);letter-spacing:.03em;pointer-events:none;text-anchor:middle;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.3);stroke-width:.4px;stroke-linejoin:round}")
rep("linear-gradient(90deg,var(--flavio),var(--mid),var(--lula))","linear-gradient(90deg,var(--pnm),var(--mid),var(--unc))")
rep(".pn-flip{",".up{color:#2f8f4e}.dn{color:#c0392b}\n.pn-t .inc{color:var(--mute);font:500 9.5px var(--mono);margin-left:4px;letter-spacing:.04em}\n.pn-flip{")
# ---- html ----
rep("<h1>Brazil: land vs people</h1><p class=\"sub\">The 2026 presidential runoff by state. Tap a state to resize it from its land area to its share of voters, or flip the whole map.</p>","<h1>Trinidad &amp; Tobago: land vs people</h1><p class=\"sub\">The 2025 general election, seat by seat. Tap a seat to resize it from its land area to its population, or flip the whole map.</p>")
rep('<button id="bPop" aria-pressed="false">Electorate</button>','<button id="bPop" aria-pressed="false">Population</button>')
rep('<span class="lbl">State</span><span class="val" id="ddVal">All 27 states</span>','<span class="lbl">Seat</span><span class="val" id="ddVal">All 41 seats</span>')
rep('placeholder="Search states"','placeholder="Search seats"');rep('aria-label="Search states"','aria-label="Search seats"')
rep('<button data-s="p" aria-pressed="false">Voters</button>','<button data-s="p" aria-pressed="false">Electors</button>')
rep('aria-label="States"></ul>','aria-label="Seats"></ul>')
rep("aria-label=\"Map of Brazil's 27 states; tap a state to resize it by its electorate\"","aria-label=\"Map of Trinidad and Tobago constituencies; tap a seat to resize it by population\"")
rep('aria-label="State details"','aria-label="Seat details"')
rep('<span>◀ Flávio</span>','<span>◀ PNM</span>');rep('<span>Lula ▶</span>','<span>UNC ▶</span>')
rep("Flipped since 2022 · shade shows size of swing (full colour at 5+ pts)","Flipped since 2020 · shade shows size of swing (full colour at 10+ pts) · Tobago has no 2020 comparison")
# ---- frame ----
rep("pad=S*.6;","pad=S*2;")
splice("const hx0=","const fmt=","const vbH=vb.slice();let vbC=vb.slice();\n")
# ---- data ----
splice("const REG=","const cells=GEO.cells;","""const PCOL={UNC:['var(--unc)','#14243b'],PNM:['var(--pnm)','#fff'],TPP:['var(--tpp)','#fff'],PF:['#8b2be2','#fff']};
const pcol=p=>PCOL[p]||['#6b7785','#fff'];
const pv=p=>'--'+p.toLowerCase();
const PARTIES=['UNC','PNM','TPP'];
const ST={};
Object.keys(GEO.area).forEach(k=>{const r=RES[k],u=r.c.find(c=>c.p==='UNC'),n=r.c.find(c=>c.p==='PNM');
 const prev=(u&&n&&u.d!=null&&n.d!=null)?((u.v-u.d)>(n.v-n.d)?'UNC':'PNM'):null;
 ST[k]={code:k,short:GEO.short[k],name:GEO.names[k],island:GEO.island[k],area:GEO.area[k],el:GEO.el[k],win:r.win,r,sw:r.sw,prev,flip:prev!=null&&prev!==r.win}});
const states=Object.values(ST),codes=Object.keys(ST);
const totArea=d3.sum(states,s=>s.area),totEl=d3.sum(states,s=>s.el);
states.forEach(s=>{s.aPct=s.area/totArea;s.pPct=s.el/totEl;s.nh=0});
const sgn=v=>v==null?'<span style="color:var(--mute)">—</span>':`<span class="${v>0?'up':v<0?'dn':''}">${v>0?'+':v<0?'−':''}${fmt(Math.abs(v))}</span>`;
""")
# ---- colors ----
rep("colors.L=d3.color(cs.getPropertyValue('--lula').trim()||'#c8323c');colors.F=d3.color(cs.getPropertyValue('--flavio').trim()||'#1f5fbf');","['unc','pnm','tpp'].forEach(p=>colors[p.toUpperCase()]=d3.color(cs.getPropertyValue('--'+p).trim()||'#999'));")
rep("states.forEach(s=>{const u=Math.min(1,Math.abs(s.sw)/5);s.swc=d3.interpolateRgb(colors.N,colors[s.sw>0?'L':'F'])(.12+.88*u)})","states.forEach(s=>{if(s.sw==null){s.swc=colors.N;return}const u=Math.min(1,Math.abs(s.sw)/10);s.swc=d3.interpolateRgb(colors.N,colors[s.sw>0?'UNC':'PNM'])(.12+.88*u)})")
# remove Brazil-only 2022/swing assignment line if left
# ---- pieces aria ----
rep("ST[c.st].name+', '+cand[ST[c.st].win].s","ST[c.st].name+', '+ST[c.st].win")
# ---- precision (small units) ----
rep("F=q=>q[0].toFixed(1)+','+q[1].toFixed(1)","F=q=>q[0].toFixed(2)+','+q[1].toFixed(2)")
rep("vbC.map(v=>v.toFixed(1))","vbC.map(v=>v.toFixed(2))")
rep("(g[0]+(h[0]+ox-g[0])*t).toFixed(1)+','+(g[1]+(h[1]+oy-g[1])*t).toFixed(1)","(g[0]+(h[0]+ox-g[0])*t).toFixed(2)+','+(g[1]+(h[1]+oy-g[1])*t).toFixed(2)")
rep("(o[0]*w).toFixed(1)+','+(o[1]*w).toFixed(1)","(o[0]*w).toFixed(2)+','+(o[1]*w).toFixed(2)")
# ---- labels ----
rep("lab:g.append('text').attr('class','slab').text(k).attr('opacity',0)","lab:g.append('text').attr('class','slab').text(ST[k].short).attr('opacity',0).style('fill',ST[k].win==='UNC'?'#14243b':'#fff').style('stroke',ST[k].win==='UNC'?'rgba(255,255,255,.45)':'rgba(0,0,0,.3)')")
rep("if(p[2]<88)return;GL[s.code]=glabG.append('text').attr('class','glab').attr('x',p[0]).attr('y',p[1]+34).text(s.code)","if(p[2]<1)return;const u=s.win==='UNC';GL[s.code]=glabG.append('text').attr('class','glab').attr('x',p[0]).attr('y',p[1]+.6).style('fill',u?'#14243b':'#fff').style('stroke',u?'rgba(227,177,58,.85)':'rgba(0,0,0,.25)').text(s.short)")
rep("SG[n].lab.attr('x',c0.x).attr('y',c0.y+32)","SG[n].lab.attr('x',c0.x).attr('y',c0.y+.8)")
# ---- cap ----
rep("target?'Sized by <b>electorate</b> · 1 hex ≈ 250k voters':mor.size?`<b>${mor.size}</b> resized to voters · 1 hex ≈ 250k · tap to revert`:'Real boundaries · tap a state to resize it'","target?'Sized by <b>population</b> · one hexagon ≈ equal share':mor.size?`<b>${mor.size}</b> resized to population · tap to revert`:'Real boundaries · tap a seat to resize it'")
# ---- national + panel ----
splice("// national strip","const emptyHTML=",r"""// national strip
const vtot={};PARTIES.forEach(p=>vtot[p]=0);let vall=0;
Object.values(RES).forEach(r=>r.c.forEach(c=>{vall+=c.v;if(vtot[c.p]!=null)vtot[c.p]+=c.v}));
const agg=Object.fromEntries(PARTIES.map(p=>{const ss=states.filter(s=>s.win===p);return [p,{n:ss.length,a:d3.sum(ss,s=>s.aPct),p:d3.sum(ss,s=>s.pPct),v:vtot[p]/vall}]}));
function drawNat(){const ps=PARTIES.filter(p=>agg[p].n).sort((a,b)=>agg[b].v-agg[a].v),oth=ps[1];
 document.getElementById('nat').innerHTML=ps.map(p=>{const a=agg[p];return `<div class="nat-r"><span class="nat-n"><i class="dot" style="background:var(${pv(p)})"></i>${p}</span><span class="nat-s"><b>${a.n}</b> seats</span><span class="nat-m">${pct(a.a)} land · ${pct(a.p)} electors · <b>${pct(a.v)}</b> votes</span></div>`}).join('')+
 `<div class="nat-g">${oth} won <b>${agg[oth].n}</b> of 41 seats covering <b>${pct(agg[oth].a)}</b> of the land and <b>${pct(agg[oth].p)}</b> of electors, and took <b>${pct(agg[oth].v)}</b> of all votes cast.</div>`}
// ---- merged panel ----
const sheet=document.getElementById('sheet'),pnBody=document.getElementById('pnBody');
let full=false;
function chipsHTML(){if(mor.size<2||target)return '';const ss=[...mor].map(n=>ST[n]),la=d3.sum(ss,s=>s.aPct),pa=d3.sum(ss,s=>s.pPct);
 return `<div class="pn-chips"><div class="pn-chl">${ss.map(s=>`<button class="chip${s.code===cur?' on':''}" data-k="${s.code}"><i class="dot" style="background:var(${pv(s.win)})"></i>${escH(s.short)}</button>`).join('')}</div><div class="pn-sum"><b>${ss.length} resized</b> hold ${pct(la)} of the land and ${pct(pa)} of electors</div></div>`}
function panelHTML(k){const s=ST[k],r=s.r,pc=pcol(s.win),dens=s.el/s.area,rel=dens/(totEl/totArea),res=mor.has(k)||target===1;
 const rtxt=rel>=1.05?`<b>${rel>=10?Math.round(rel):rel.toFixed(1)}×</b> as many electors per km² as the national average`:rel<=.95?`<b>${rel.toFixed(2)}×</b> the national elector density`:'about the national elector density';
 const top=r.c.slice(0,4),rest=r.c.slice(4);
 const rows=top.map((c,i)=>{const p=pcol(c.p);return `<tr class="${i===0?'win':''}"><td><span class="nm"><i style="background:${p[0]}"></i><span>${escH(c.n)}${c.i?'<span class="inc">INC</span>':''}</span></span></td><td><span class="pn-p" style="background:${p[0]};color:${p[1]}">${escH(c.p)}</span></td><td class="num">${fmt(c.v)}</td><td class="num">${c.s.toFixed(1)}%</td><td class="num">${sgn(c.d)}</td></tr>`}).join('')
  +(rest.length?`<tr><td><span class="nm"><i style="background:#9aa5b1"></i><span style="color:var(--mute)">${rest.length} other${rest.length>1?'s':''}</span></span></td><td></td><td class="num">${fmt(d3.sum(rest,c=>c.v))}</td><td class="num">${d3.sum(rest,c=>c.s).toFixed(1)}%</td><td class="num">${sgn(null)}</td></tr>`:'');
 const tw=s.sw==null?null:s.sw>0?'UNC':'PNM';
 const swH=tw?`<div class="pn-sw"><i class="dot" style="background:var(${pv(tw)});margin-right:6px"></i><b>${Math.abs(s.sw).toFixed(1)} pts</b> swing to ${tw} since 2020${s.flip?` <span class="pn-flip">Flipped from ${s.prev}</span>`:''}</div>`:'';
 return `<div class="pn-bar" style="background:${pc[0]}"></div>
 <div class="pn-hd"><div style="min-width:0"><span class="pn-n">${escH(r.n)}</span><span class="pn-c">${escH(s.short)} · ${s.island.toUpperCase()}</span></div><div class="pn-r"><span class="pn-p" style="background:${pc[0]};color:${pc[1]}">${s.win} won</span>${mor.has(k)&&!target?'<button class="pn-b pn-rv" data-k="'+k+'">Revert</button>':''}<button class="pn-b pn-tgl" aria-expanded="${full}">${full?'Less':'More'}</button>${peek?'':'<button class="pn-b pn-x" aria-label="Close">✕</button>'}</div></div>
 <div class="pn-key">${barHTML('Land',s.aPct,`var(${pv(s.win)})`,!res)}${barHTML('Electors',s.pPct,`var(${pv(s.win)})`,res)}<div class="pn-rel">${rtxt}</div>${swH}</div>
 <div class="pn-more"><div class="pn-st"><span>Electorate <b>${fmt(r.e)}</b></span><span>Turnout <b>${r.t.toFixed(1)}%</b></span><span>Rejected <b>${fmt(r.rj)}</b></span><span>Margin <b>${r.m.toFixed(1)}%</b></span><span>Area <b>${fmt(Math.round(s.area))} km²</b></span><span>Hexes <b>${s.nh}</b></span></div>
 <table class="pn-t"><thead><tr><th>Candidate</th><th>Party</th><th class="num">Votes</th><th class="num">Share</th><th class="num">vs 2020</th></tr></thead><tbody>${rows}</tbody></table></div>`}
""")
rep("<p>It resizes to its share of voters (1 hexagon ≈ 250k) while a dashed line keeps its real shape. Tap again to revert, or tap several to compare.</p><p>On a computer, hover to preview any state.</p>","<p>It resizes to its share of the population while a dashed line keeps its real shape. Tap again to revert, or tap several to compare.</p><p>On a computer, hover to preview any seat.</p>")
rep("<h2>Tap a state</h2>","<h2>Tap a seat</h2>")
# ---- selection/dropdown strings ----
rep("const dotFor=n=>`<i class=\"dot\" style=\"background:var(${cand[ST[n].win].v});margin-right:8px\"></i>`;","const dotFor=n=>`<i class=\"dot\" style=\"background:var(${pv(ST[n].win)});margin-right:8px\"></i>`;")
rep("ddVal.innerHTML=cur?dotFor(cur)+ST[cur].name+","ddVal.innerHTML=cur?dotFor(cur)+escH(ST[cur].name)+")
rep("(mor.size?mor.size+' resized':'All 27 states')","(mor.size?mor.size+' resized':'All 41 seats')")
rep("s.name===null?`<li class=\"dd-opt\" role=\"option\" id=\"o${i}\" data-i=\"${i}\" aria-selected=\"${cur===null&&!mor.size}\"><span class=\"nm\">All 27 states</span></li>`","s.name===null?`<li class=\"dd-opt\" role=\"option\" id=\"o${i}\" data-i=\"${i}\" aria-selected=\"${cur===null&&!mor.size}\"><span class=\"nm\">All 41 seats</span></li>`")
rep("style=\"background:var(${cand[s.win].v})\"></i><span class=\"nm\">${s.name}</span><span class=\"mt\">${metric(s)}</span></li>`","style=\"background:var(${pv(s.win)})\"></i><span class=\"nm\">${escH(s.name)}</span><span class=\"mt\">${metric(s)}</span></li>`")
rep("function metric(s){return sortBy==='p'?'≈'+d3.format('.3~s')(s.el):sortBy==='a'?fmt(s.area)+' km²':s.code}","function metric(s){return sortBy==='p'?fmt(s.el):sortBy==='a'?fmt(Math.round(s.area))+' km²':s.short}")
rep(".normalize('NFD').replace(/[̀-ͯ]/g,'');",".normalize('NFD').replace(/[̀-ͯ’']/g,'');")
rep("norm(s.code).includes(f)","norm(s.short).includes(f)")
rep("(a,b)=>a.name.localeCompare(b.name,'pt')","(a,b)=>a.name.localeCompare(b.name)")
rep("const LS='br-tap-morph-v1';","const LS='tt-tap-morph-v1';")
# ---- note ----
i=t.index("document.getElementById('note').textContent='");j=t.index("';",i)+2
t=t[:i]+"document.getElementById('note').textContent='Land view: the 41 constituency boundaries from the file you supplied, with area computed from those shapes. Population view: the hexagon layout from the population cartogram, whose hex counts came from a 2011-census-based estimate; a resized seat keeps its centre and a dashed line marks its real shape. Shares, density and the seat list use registered electors from the TT Electoral Population by Constituency list. Results: Elections and Boundaries Commission, 2025. “vs 2020” is each candidate’s change in votes; swing is the shift in the UNC–PNM margin toward UNC (positive) or PNM (negative); a seat is flipped when its 2020 winner differs, judged from the UNC and PNM vote changes. Tobago seats have no 2020 comparison.';"+t[j:]
open('template_tt.html','w').write(t)
for w in ['cand[','Lula','Flávio','L22','AB[','27 states','state','Brazil','elTxt','.ls','.fs','ST[k].tot']:
    print(w,t.count(w))

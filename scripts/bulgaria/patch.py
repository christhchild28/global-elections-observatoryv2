t=open('template_tap_src.html').read()
def rep(a,b,cnt=1):
    global t
    assert t.count(a)==cnt,(t.count(a),a[:80]); t=t.replace(a,b)
def splice(s,e,new):
    global t
    i=t.index(s);j=t.index(e,i);t=t[:i]+new+t[j:]
# ---------- head / css ----------
rep("<title>Brazil State Morph</title>","<title>Bulgaria District Morph</title>")
rep("--lula:#c8323c;--flavio:#1f5fbf;","--pb:#c8323c;--gerb:#2f6fb5;--ppdb:#e0a010;--dps:#7b4fa6;--vaz:#8a6a45;--oth:#8a929c;")
rep("--lula:#e0545c;--flavio:#4a8de0;","--pb:#e0545c;--gerb:#4a8de0;--ppdb:#eeb52a;--dps:#9b72c9;--vaz:#b08a5f;--oth:#9aa4ae;",2)
rep(".flip-o{fill:none;stroke:var(--ink);stroke-width:2.4px;stroke-linejoin:round;vector-effect:non-scaling-stroke;pointer-events:none}\n","")
rep(".legbar{flex:0 1 150px;min-width:70px;height:9px;border-radius:5px;background:linear-gradient(90deg,var(--flavio),var(--mid),var(--lula))}\n.legf{flex-basis:100%}\n.legf i{display:inline-block;width:14px;height:9px;border:2px solid var(--ink);border-radius:3px;vertical-align:-1px;margin-right:6px}\n",
 ".legbar{flex:0 1 150px;min-width:70px;height:9px;border-radius:5px;display:inline-block}\n.leg .sw{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:-1px}\n")
rep(".glab{font:600 100px var(--mono);pointer-events:none;text-anchor:middle;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.38);stroke-width:14px;stroke-linejoin:round}\n.slab{font:600 84px var(--mono);pointer-events:none;text-anchor:middle;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.3);stroke-width:12px;stroke-linejoin:round}",
 ".glab,.slab{font:600 11px var(--mono);letter-spacing:.02em;pointer-events:none;text-anchor:middle;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.36);stroke-width:.26em;stroke-linejoin:round}\n.glab.dk,.slab.dk{fill:#14243b;stroke:rgba(255,255,255,.62)}")
rep(".tog[hidden]{display:none}",".tog[hidden]{display:none}\nselect.tog{text-transform:none;letter-spacing:.02em;padding:6px 8px 6px 12px;max-width:100%;font-weight:600}")
rep(".pn-flip{display:inline-block;margin-left:4px;padding:1px 8px;border-radius:99px;background:var(--ink);color:var(--card);font:600 10.5px var(--mono);letter-spacing:.04em;text-transform:uppercase}\n","")
# ---------- html ----------
rep('<h1>Brazil: land vs people</h1><p class="sub">The 2026 presidential runoff by state. Tap a state to resize it from its land area to its share of voters, or flip the whole map.</p>',
 '<h1>Bulgaria: land vs people</h1><p class="sub">The 19 April 2026 parliamentary election by province. Tap one to resize it from its land area to its registered voters, or flip the whole map.</p>')
rep('<span class="lbl">State</span><span class="val" id="ddVal">All 27 states</span>','<span class="lbl">Region</span><span class="val" id="ddVal">All regions</span>')
rep('placeholder="Search states"','placeholder="Search regions"');rep('aria-label="Search states"','aria-label="Search regions"')
rep('aria-label="States"></ul>','aria-label="Regions"></ul>')
rep("aria-label=\"Map of Brazil's 27 states; tap a state to resize it by its electorate\"","aria-label=\"Map of Bulgaria's electoral districts; tap a province to resize it by its registered voters\"")
rep('aria-label="State details"','aria-label="Region details"')
rep('<button class="tog" id="mWin" aria-pressed="true">Winner</button><button class="tog" id="mSw" aria-pressed="false">Swing</button>','<select class="tog" id="colorBy" aria-label="Colour map by"></select>')
rep('<div class="leg" id="leg" hidden><span>◀ Flávio</span><i class="legbar"></i><span>Lula ▶</span><span class="legf"><i></i>Flipped since 2022 · shade shows size of swing (full colour at 5+ pts)</span></div>','<div class="leg" id="leg"></div>')
# ---------- data ----------
splice("const REG={","const cells=GEO.cells;","""const PARTIES=[{k:'PB',n:'Progressive Bulgaria',s:'PB',v:'--pb',t:'#fff'},{k:'GERB',n:'GERB–SDS',s:'GERB',v:'--gerb',t:'#fff'},{k:'PPDB',n:'PP–DB',s:'PP–DB',v:'--ppdb',t:'#14243b'},{k:'DPS',n:'DPS',s:'DPS',v:'--dps',t:'#fff'},{k:'VAZ',n:'Vazrazhdane',s:'Vaz.',v:'--vaz',t:'#fff'},{k:'OTH',n:'Other parties',s:'Other',v:'--oth',t:'#fff'}];
const PK=Object.fromEntries(PARTIES.map(p=>[p.k,p]));
const RACE=['PB','GERB','PPDB','DPS','VAZ'],KEYS=RACE.concat('OTH');
const M0={};D.mirs.forEach(m=>{M0[m.id]=m});
function aggregate(ids){const a={ids,REG:0,VOTED:0,NOTA:0,hasAbroad:false};KEYS.forEach(k=>a[k]=0);
 ids.forEach(id=>{const m=M0[id];KEYS.forEach(k=>a[k]+=m[k]);a.NOTA+=m.NOTA;a.VOTED+=m.VOTED;if(m.REG)a.REG+=m.REG;else a.hasAbroad=true});
 a.sumP=KEYS.reduce((s,k)=>s+a[k],0);const rk=RACE.slice().sort((x,y)=>a[y]-a[x]);a.win=rk[0];a.run=rk[1];a.margin=(a[a.win]-a[a.run])/a.sumP;return a}
D.mirs.forEach(m=>{m.agg=aggregate([m.id])});
const ST={};
D.land.forEach(l=>{const a=aggregate(l.mirs);ST[l.label]={code:l.label,name:l.label2,ids:l.mirs,area:l.area,el:a.REG,a,win:a.win,abroad:false}});
{const a=aggregate(['32']);ST.ABR={code:'ABR',name:'Abroad',ids:['32'],area:0,el:0,a,win:a.win,abroad:true}}
const states=Object.values(ST),codes=Object.keys(ST);
const totArea=d3.sum(states,s=>s.area),totEl=d3.sum(states,s=>s.el);
states.forEach(s=>{s.aPct=s.area/totArea;s.pPct=s.el/totEl;s.nh=0});
const natA=aggregate(D.mirs.map(m=>m.id)),natShare={};KEYS.forEach(k=>natShare[k]=natA[k]/natA.sumP);
const domestic=D.mirs.filter(m=>m.REG),domTurn=d3.sum(domestic,m=>m.VOTED)/d3.sum(domestic,m=>m.REG);
const maxShare={};RACE.forEach(p=>{maxShare[p]=d3.max(states,s=>s.a[p]/s.a.sumP)});
const sgn=(v,u)=>(v>0?'+':v<0?'−':'')+Math.abs(v).toFixed(1)+(u||'');
""")
# ---------- colours ----------
splice("const colors={};\nfunction readColors(){","const sstep=","""const colors={},CT={};let CARD=d3.color('#fff'),mode='win',colFrom={},colTo={};
const MODES=['win'].concat(RACE);
function colorOf(k,m){const a=ST[k].a;let base,op;if(m==='win'){base=colors[a.win];op=.45+.55*Math.min(1,a.margin/.3)}else{base=colors[m];op=.1+.9*Math.min(1,a[m]/a.sumP/maxShare[m])}return d3.color(d3.interpolateRgb(CARD,base)(op))}
function readColors(){const cs=getComputedStyle(document.documentElement);PARTIES.forEach(p=>colors[p.k]=d3.color(cs.getPropertyValue(p.v).trim()||'#888'));CARD=d3.color(cs.getPropertyValue('--card').trim()||'#fff');
 MODES.forEach(m=>{CT[m]={};codes.forEach(k=>{CT[m][k]=colorOf(k,m)})});colFrom=colTo=CT[mode]}
readColors();matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{readColors();CM=1;render()});
""")
# ---------- layers ----------
rep("const flipL=root.append('g'),FLP=states.filter(s=>s.flip).map(s=>({k:s.code,e:flipL.append('path').attr('class','flip-o').attr('d',GEO.outlines[s.code]).attr('opacity',0)}));\n","")
rep("ST[c.st].name+', '+cand[ST[c.st].win].s","ST[c.st].name+', '+PK[ST[c.st].win].s")
# labels
rep("states.forEach(s=>{const p=GEO.labels[s.code];if(p[2]<88)return;GL[s.code]=glabG.append('text').attr('class','glab').attr('x',p[0]).attr('y',p[1]+34).text(s.code)});",
 "states.forEach(s=>{const p=GEO.labels[s.code];if(!p||p[2]<12)return;GL[s.code]=glabG.append('text').attr('class','glab').attr('x',p[0]).attr('y',p[1]).attr('dy','.35em').text(s.code)});")
rep("lab:g.append('text').attr('class','slab').text(k).attr('opacity',0)","lab:g.append('text').attr('class','slab').attr('dy','.35em').text(k).attr('opacity',0)")
# multi-cluster labels
splice("function drawLabels(){","function rebuildClusters()","""function drawLabels(){const seen=new Set(),comps={};
 for(const c of cells){if(seen.has(c))continue;const comp=[c],st=[c];seen.add(c);while(st.length){const u=st.pop();for(const v of nbrK(u))if(v&&v.st===u.st&&!seen.has(v)){seen.add(v);comp.push(v);st.push(v)}}(comps[c.st]=comps[c.st]||[]).push(comp)}
 for(const n in comps){const list=comps[n].sort((a,b)=>b.length-a.length).filter((a,i)=>i===0||a.length>=3).map(a=>{const mx=d3.mean(a,c=>c.x),my=d3.mean(a,c=>c.y);return a.reduce((b,c)=>((c.x-mx)**2+(c.y-my)**2<(b.x-mx)**2+(b.y-my)**2?c:b),a[0])});
  SG[n].lab=SG[n].g.selectAll('text.slab').data(list).join('text').attr('class','slab').attr('dy','.35em').text(n).attr('x',d=>d.x).attr('y',d=>d.y).attr('opacity',0)}
 lastFs=0;if(typeof fitLabels==='function')fitLabels()}
""")
# ---------- state ----------
rep("let CM=0,colorMode=0,T=0,","let CM=1,T=0,")
# ---------- render ----------
rep("const w=1-T,FC={};codes.forEach(k=>{const wc=colors[ST[k].win];FC[k]=CM>.001?d3.color(d3.interpolateRgb(wc,ST[k].swc)(CM)):wc});",
 "const w=1-T,FC={};codes.forEach(k=>{FC[k]=CM>=.999?colTo[k]:CM<=.001?colFrom[k]:d3.color(d3.interpolateRgb(colFrom[k],colTo[k])(CM))});")
rep("this.style.vectorEffect='non-scaling-stroke';this.style.opacity=dimOf(k)});","this.style.vectorEffect='non-scaling-stroke';this.style.opacity=(dimOf(k)*(ST[k].abroad?sstep(.55,1,tk):1)).toFixed(3);this.style.pointerEvents=ST[k].abroad&&tk<.5?'none':''});")
rep(" FLP.forEach(f=>f.e.attr('opacity',CM*(1-sstep(0,.3,te(f.k)))*dimOf(f.k)));\n","")
rep("ol=Math.max(on?sstep(.5,1,t)*(k===cur?1:.6):0,ST[k].flip?CM*sstep(.5,1,t):0);G.hH","ol=on?sstep(.5,1,t)*(k===cur?1:.6):0;G.hH")
rep("  if(GL[k])GL[k].attr('opacity',showLab?(1-sstep(0,.25,t))*dm:0)});","  if(GL[k])GL[k].attr('opacity',showLab?(1-sstep(0,.25,t))*dm:0);\n  const lt=(.299*FC[k].r+.587*FC[k].g+.114*FC[k].b)>158;G.lab.classed('dk',lt);if(GL[k])GL[k].classed('dk',lt)});")
rep(" const fo=cur?1-sstep(0,.5,te(cur)):0;fgH.attr('opacity',fo);fgD.attr('opacity',fo)}"," const fo=cur?1-sstep(0,.5,te(cur)):0;fgH.attr('opacity',fo);fgD.attr('opacity',fo);fitLabels()}\nlet lastFs=0;\nfunction fitLabels(){const sc=svgN.clientWidth/vbC[2];if(!sc)return;const fs=Math.max(8,Math.min(15,8.5/sc));if(Math.abs(fs-lastFs)<.1)return;lastFs=fs;d3.selectAll('.glab,.slab').style('font-size',fs.toFixed(2)+'px')}\naddEventListener('resize',()=>{if(typeof render==='function')render()});")
# ---------- caption ----------
rep("target?'Sized by <b>electorate</b> · 1 hex ≈ 250k voters':mor.size?`<b>${mor.size}</b> resized to voters · 1 hex ≈ 250k · tap to revert`:'Real boundaries · tap a state to resize it'",
 "target?'Sized by <b>registered voters</b> · 1 hex ≈ 100k':mor.size?`<b>${mor.size}</b> resized to voters · 1 hex ≈ 100k · tap to revert`:'Real boundaries · tap a province to resize it'")
# ---------- numbers ----------
rep("const elTxt=s=>'≈'+fmt(Math.round(s.el/1e5)*1e5>=1e6?Math.round(s.el/1e5)*1e5:Math.round(s.el/1e3)*1e3);\n","const p1=v=>(v*100).toFixed(1)+'%';\n")
splice("// national strip","const emptyHTML=","""// national strip
const won={};RACE.forEach(p=>won[p]={n:0,a:0,p:0});
domestic.forEach(m=>{const w=won[m.agg.win];w.n++;w.p+=m.REG/totEl});
states.forEach(s=>{if(!s.abroad)won[s.win].a+=s.aPct});
function drawNat(){const ps=RACE.filter(p=>won[p].n).sort((a,b)=>won[b].n-won[a].n);
 document.getElementById('nat').innerHTML=ps.map((p,i)=>{const w=won[p];return `<div class="nat-r"><span class="nat-n"><i class="dot" style="background:var(${PK[p].v})"></i>${PK[p].s}${PK[p].n!==PK[p].s?`<small>${PK[p].n}</small>`:''}</span><span class="nat-s"><b>${w.n}</b> of 31 districts${i===0?` · <b>${D.nat.PBseats}</b> of 240 seats`:''}</span><span class="nat-m">${pct(w.a)} land · ${pct(w.p)} electors · <b>${p1(natShare[p])}</b> votes</span></div>`}).join('')+
 (ps.length>1?`<div class="nat-g">${PK[ps[1]].s} won <b>${won[ps[1]].n}</b> district${won[ps[1]].n>1?'s':''}, covering <b>${pct(won[ps[1]].a)}</b> of the land and <b>${pct(won[ps[1]].p)}</b> of registered voters, with <b>${p1(natShare[ps[1]])}</b> of all votes. Turnout was ${D.nat.turnout}%.</div>`:'')}
// ---- merged panel ----
const sheet=document.getElementById('sheet'),pnBody=document.getElementById('pnBody');
let full=false;
function chipsHTML(){if(mor.size<2||target)return '';const ss=[...mor].map(n=>ST[n]),la=d3.sum(ss,s=>s.aPct),pa=d3.sum(ss,s=>s.pPct);
 return `<div class="pn-chips"><div class="pn-chl">${ss.map(s=>`<button class="chip${s.code===cur?' on':''}" data-k="${s.code}"><i class="dot" style="background:var(${PK[s.win].v})"></i>${s.code}</button>`).join('')}</div><div class="pn-sum"><b>${ss.length} resized</b> hold ${pct(la)} of the land and ${pct(pa)} of registered voters</div></div>`}
function panelHTML(k){const s=ST[k],a=s.a,c=PK[s.win],ab=s.abroad,res=mor.has(k)||target===1,col=`var(${c.v})`;
 const keys=RACE.slice().sort((x,y)=>a[y]-a[x]).concat('OTH');
 const rows=keys.map(p=>{const sh=a[p]/a.sumP;return `<tr class="${p===s.win?'win':''}"><td><span class="nm"><i style="background:var(${PK[p].v})"></i><span>${PK[p].n}</span></span></td><td class="num">${fmt(a[p])}</td><td class="num">${(sh*100).toFixed(1)}%</td><td class="num">${sgn((sh-natShare[p])*100)}</td></tr>`}).join('');
 const headH=`<div class="pn-sw"><b style="color:${col}">${c.s} ${(a[s.win]/a.sumP*100).toFixed(1)}%</b> · ${PK[a.run].s} ${(a[a.run]/a.sumP*100).toFixed(1)}%${ab?'':` · turnout <b>${(a.VOTED/a.REG*100).toFixed(1)}%</b>`}</div>`;
 let keyH;
 if(ab)keyH=`<div class="pn-rel">No land area. These hexagons exist only in the electorate view, sized by votes cast.</div>${headH}`;
 else{const rel=(s.el/s.area)/(totEl/totArea),rtxt=rel>=1.05?`<b>${rel>=10?Math.round(rel):rel.toFixed(1)}×</b> as many registered voters per km² as the national average`:rel<=.95?`<b>${rel.toFixed(2)}×</b> the national voter density`:'about the national voter density';
  keyH=`${barHTML('Land',s.aPct,col,!res)}${barHTML('Voters',s.pPct,col,res)}<div class="pn-rel">${rtxt}</div>${headH}`}
 const td=ab?0:(a.VOTED/a.REG-domTurn)*100;
 const stats=ab?`<span>Votes cast <b>${fmt(a.VOTED)}</b></span><span>No fixed electorate</span><span>Hexes <b>${s.nh}</b></span><span>Margin <b>${(a.margin*100).toFixed(1)} pp</b> (${fmt(a[a.win]-a[a.run])})</span><span>None of the above <b>${fmt(a.NOTA)}</b></span>`
  :`<span>Registered <b>${fmt(s.el)}</b></span><span>Turnout <b>${(a.VOTED/a.REG*100).toFixed(1)}%</b> (${sgn(td)} pts vs ${(domTurn*100).toFixed(1)}% avg)</span><span>Area <b>${fmt(Math.round(s.area))} km²</b></span><span>Hexes <b>${s.nh}</b></span><span>Margin <b>${(a.margin*100).toFixed(1)} pp</b> (${fmt(a[a.win]-a[a.run])})</span><span>None of the above <b>${fmt(a.NOTA)}</b></span>`;
 const dist=s.ids.length>1&&!ab?`<table class="pn-t"><thead><tr><th>District</th><th class="num">Registered</th><th class="num">Turnout</th><th class="num">Lead</th></tr></thead><tbody>${s.ids.map(id=>{const m=M0[id],g=m.agg;return `<tr><td><span class="nm"><i style="background:var(${PK[g.win].v})"></i><span>${escH(m.name.replace('Sofia city · ',''))}</span></span></td><td class="num">${fmt(m.REG)}</td><td class="num">${(m.VOTED/m.REG*100).toFixed(1)}%</td><td class="num">${PK[g.win].s} +${(g.margin*100).toFixed(1)}</td></tr>`}).join('')}</tbody></table>`:'';
 const cap=ab?'VOTES CAST ABROAD':(s.ids.length>1?'DISTRICTS '+s.ids.join(' + '):'DISTRICT '+s.ids[0]);
 return `<div class="pn-bar" style="background:${col}"></div>
 <div class="pn-hd"><div style="min-width:0;flex:1 1 170px"><span class="pn-n">${escH(s.name)}</span><span class="pn-c">${s.code} · ${cap}</span></div><div class="pn-r"><span class="pn-p" style="background:${col};color:${c.t}">${c.s} won</span>${mor.has(k)&&!target?'<button class="pn-b pn-rv" data-k="'+k+'">Revert</button>':''}<button class="pn-b pn-tgl" aria-expanded="${full}">${full?'Less':'More'}</button>${peek?'':'<button class="pn-b pn-x" aria-label="Close">✕</button>'}</div></div>
 <div class="pn-key">${keyH}</div>
 <div class="pn-more"><div class="pn-st">${stats}</div>
 <table class="pn-t"><thead><tr><th>Party</th><th class="num">Votes</th><th class="num">Share</th><th class="num">vs nat.</th></tr></thead><tbody>${rows}</tbody></table>${dist}</div>`}
""")
rep("<h2>Tap a state</h2><p>It resizes to its share of voters (1 hexagon ≈ 250k) while a dashed line keeps its real shape. Tap again to revert, or tap several to compare.</p><p>On a computer, hover to preview any state.</p>",
 "<h2>Tap a province</h2><p>It resizes to its share of registered voters (1 hexagon ≈ 100k) while a dashed line keeps its real shape. Tap again to revert, or tap several to compare.</p><p>On a computer, hover to preview any province.</p>")
# ---------- selection / dropdown ----------
rep("const dotFor=n=>`<i class=\"dot\" style=\"background:var(${cand[ST[n].win].v});margin-right:8px\"></i>`;","const dotFor=n=>`<i class=\"dot\" style=\"background:var(${PK[ST[n].win].v});margin-right:8px\"></i>`;")
rep("(mor.size?mor.size+' resized':'All 27 states')","(mor.size?mor.size+' resized':'All regions')")
rep("<span class=\"nm\">All 27 states</span></li>`","<span class=\"nm\">All regions</span></li>`")
rep("style=\"background:var(${cand[s.win].v})\"></i><span class=\"nm\">${s.name}</span>","style=\"background:var(${PK[s.win].v})\"></i><span class=\"nm\">${escH(s.name)}</span>")
rep("function metric(s){return sortBy==='p'?'≈'+d3.format('.3~s')(s.el):sortBy==='a'?fmt(s.area)+' km²':s.code}","function metric(s){return s.abroad&&sortBy!=='n'?'—':sortBy==='p'?'≈'+d3.format('.3~s')(s.el):sortBy==='a'?fmt(Math.round(s.area))+' km²':s.code}")
rep("a.name.localeCompare(b.name,'pt')","a.name.localeCompare(b.name)")
# ---------- colour mode ----------
splice("const twC={};","svg.on('click'","""const twC={},sel=document.getElementById('colorBy'),leg=document.getElementById('leg');
[['win','Winner · fainter = narrower margin']].concat(RACE.map(k=>[k,PK[k].n+' share'])).forEach(([v,t])=>{const o=document.createElement('option');o.value=v;o.textContent=t;sel.appendChild(o)});
function drawLegend(){if(mode==='win'){const ps=RACE.filter(p=>states.some(s=>s.win===p));leg.innerHTML=ps.map(p=>`<span><i class="sw" style="background:var(${PK[p].v})"></i>${PK[p].s}</span>`).join('')+'<span>Fainter = narrower margin</span>'}
 else{const p=PK[mode];leg.innerHTML=`<span>Lower</span><i class="legbar" style="background:linear-gradient(90deg,color-mix(in srgb,var(${p.v}) 10%,var(--card)),var(${p.v}))"></i><span>${pct(maxShare[mode])} of party votes (highest region)</span>`}}
function setMode(m){if(m===mode)return;const now={};codes.forEach(k=>{now[k]=CM>=.999?colTo[k]:CM<=.001?colFrom[k]:d3.color(d3.interpolateRgb(colFrom[k],colTo[k])(CM))});
 colFrom=now;mode=m;colTo=CT[m];CM=0;sel.value=m;drawLegend();
 d3.select(twC).interrupt().transition().duration(reduce?100:380).ease(d3.easeCubicOut).tween('c',()=>u=>{CM=u;render()})}
sel.onchange=()=>setMode(sel.value);
""")
# box select: ignore the abroad group while it is invisible
rep("pieces.each(function(c){test(this,c.st)});extras.each","pieces.each(function(c){if(ST[c.st].abroad&&te(c.st)<.5)return;test(this,c.st)});extras.each")
# ---------- storage / note / init ----------
rep("const LS='br-tap-morph-v1';","const LS='bg-tap-morph-v1';")
i=t.index("document.getElementById('note').textContent='");j=t.index("';",i)+2
t=t[:i]+"document.getElementById('note').textContent='Land view: Natural Earth province boundaries (public domain), simplified. Provinces differ slightly from electoral districts, so Plovdiv city and Plovdiv province share one land shape, as do Sofia’s three districts; tapping them resizes the combined area, and their hex positions inside Sofia are approximate. A resized province keeps its centre; one hexagon is about 100,000 registered voters (minimum one per district) at the same scale as the land, and the dashed line marks its real shape. Voting abroad has no land shape or fixed electorate, so its two hexagons are sized by votes cast and appear only in the electorate view or from the menu. Results: Bulgarian Central Election Commission (results.cik.bg), 19 April 2026, 100% of protocols; shares are of party votes, excluding “none of the above”, and can differ from official shares by under 0.1 pp. “vs nat.” compares a party’s share with its national share including abroad; turnout is compared with the average of the 31 domestic districts. A comparison with the October 2024 election is not included because final district-level turnout for 2024 could not be retrieved.';"+t[j:]
rep("drawEdges();drawLabels();rebuildClusters();render();drawCap();drawNat();drawPanel();build();syncBtns();","drawEdges();drawLabels();rebuildClusters();render();drawCap();drawNat();drawPanel();build();syncBtns();drawLegend();")
rep("window.__mode=setMode;","window.__mode=setMode;window.__ST=ST;")
open('template_bg.html','w').write(t)
for w in ['cand[','Lula','Flávio','L22','AB[','27 states','Brazil','elTxt','.ls','.fs','FLP','colorMode','mWin','mSw','swc','.flip','.sw)','tn==null']:
    print(w,t.count(w))

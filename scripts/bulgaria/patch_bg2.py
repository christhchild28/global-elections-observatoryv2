import re
B='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/'
t=open(B+'bg/template_bg_v1.html').read()
def rep(a,b):
    global t
    assert t.count(a)==1,(t.count(a),a[:70])
    t=t.replace(a,b)
p2=open(B+'us/patch2.py').read()
CSS=re.search(r"CSS=r'''(.*?)</style></head><body>'''",p2,re.S).group(1)
CSS+='''.scp{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 8px}
.scp button{display:inline-flex;align-items:center;gap:6px;font:600 11px var(--mono);letter-spacing:.04em;border:1px solid var(--line);background:none;color:var(--mute);border-radius:99px;padding:0 11px;min-height:32px;cursor:pointer}
.scp button[aria-pressed="true"]{background:var(--ink);color:var(--card);border-color:var(--ink)}
.scp button:focus-visible{outline:2px solid var(--hi);outline-offset:1px}
.wv span{white-space:nowrap}
'''
CSS+='</style></head><body>'
rep('</style></head><body>',CSS)
rep('''<div class="grid">
 <div class="mapbox" id="mapbox">''','''<div class="grid">
 <div class="lc">
 <div class="mapbox" id="mapbox">''')
i=t.index(' <aside id="sheet"')
t=t[:i]+''' <section class="charts" id="charts" aria-label="Charts">
  <div class="cc" id="cWho"></div>
  <div class="cc sc" id="cSc"></div>
  <div class="cc" id="cRk"></div>
 </section>
 </div>
'''+t[i:]

JS=r'''
// ---- charts (under the map) ----
const pc1=v=>(v*100).toFixed(1)+'%';
const xRat=v=>{const k=v>=1?v:1/v;return (k>=10?Math.round(k):Math.round(k*10)/10)+'×'};
const rkTxt=q=>(q>.95&&q<1.05)?'≈ 1×':xRat(q)+(q>=1?' bigger':' smaller');
const LAND=states.filter(s=>!s.abroad);
const selStates=()=>{const u=new Set([...mor,...(cur?[cur]:[])]);return states.filter(s=>u.has(s.code))};
function whoCalc(list){const dom=list.filter(s=>!s.abroad),A=d3.sum(dom,s=>s.area),E=d3.sum(dom,s=>s.el);
 const o={land:{},el:{},vt:{},hasLand:A>0};RACE.concat('OTH').forEach(k=>{o.land[k]=0;o.el[k]=0;o.vt[k]=0});
 dom.forEach(s=>{o.land[s.win]+=s.area/A;o.el[s.win]+=s.el/E});
 const V=d3.sum(list,s=>s.a.sumP);list.forEach(s=>KEYS.forEach(k=>o.vt[k]+=s.a[k]/V));return o}
function segRow(lbl,o){const ks=KEYS.filter(k=>o[k]>.0005).sort((a,b)=>o[b]-o[a]);
 return `<div class="wr"><div class="wl">${lbl}</div><div class="wb" role="img" aria-label="${lbl}: ${ks.map(k=>PK[k].s+' '+pc1(o[k])).join(', ')}">${ks.map(k=>`<i style="width:${(o[k]*100).toFixed(2)}%;background:var(${PK[k].v})"></i>`).join('')}</div><div class="wv">${ks.map(k=>`<span><i class="dot" style="background:var(${PK[k].v})"></i>${PK[k].s} <b>${pc1(o[k])}</b></span>`).join('')}</div></div>`}
function whoBlock(list,title){const o=whoCalc(list),w=RACE.slice().sort((a,b)=>o.vt[b]-o.vt[a])[0];
 const head=o.hasLand?`<p class="wh"><b style="color:var(${PK[w].v})">${PK[w].n}</b> carried <b>${pc1(o.land[w])}</b> of the land with <b>${pc1(o.vt[w])}</b> of the vote.</p>`:`<p class="wh"><b style="color:var(${PK[w].v})">${PK[w].n}</b> took <b>${pc1(o.vt[w])}</b> of the votes cast abroad.</p>`;
 return `<div class="wblk">${title?`<div class="wt">${title}</div>`:''}${head}${o.hasLand?segRow('Land carried',o.land)+segRow('Registered voters in districts won',o.el):''}${segRow('Votes cast',o.vt)}</div>`}
function drawWho(){const sl=selStates();
 document.getElementById('cWho').innerHTML=`<h3>Who carried what</h3><p class="cs">Land and registered voters count each district for its winner. Votes include those cast abroad.</p>`+whoBlock(states,sl.length>1?'Whole country':'')+(sl.length>1?whoBlock(sl,'Your selection · '+sl.length+' regions'):'')}
// density vs a party's share
let scP='PB';
const SCW=360,SCH=272,SCl=34,SCr=10,SCt=10,SCb=34;
const lx=s=>Math.log10(s.el/s.area),shr=s=>s.a[scP]/s.a.sumP*100;
const sr=s=>2.2+1.3*Math.sqrt(s.el/1e5)*.62;
let sxs,sys,xD,yD,fit;
function scScales(){const xmin=d3.min(LAND,lx),xmax=d3.max(LAND,lx),ymin=d3.min(LAND,shr),ymax=d3.max(LAND,shr);
 xD=[Math.floor((xmin-.12)*4)/4,Math.ceil((xmax+.12)*4)/4];const stp=(ymax-ymin)<30?5:10;yD=[Math.max(0,Math.floor((ymin-2)/stp)*stp),Math.min(100,Math.ceil((ymax+2)/stp)*stp)];yD.step=stp;
 sxs=d3.scaleLinear().domain(xD).range([SCl,SCW-SCr]);sys=d3.scaleLinear().domain(yD).range([SCH-SCb,SCt]);
 const w=LAND.map(s=>s.a.sumP),x=LAND.map(lx),y=LAND.map(shr),W=d3.sum(w),mx=d3.sum(x.map((v,i)=>v*w[i]))/W,my=d3.sum(y.map((v,i)=>v*w[i]))/W;
 const sxx=d3.sum(x.map((v,i)=>w[i]*(v-mx)**2)),syy=d3.sum(y.map((v,i)=>w[i]*(v-my)**2)),sxy=d3.sum(x.map((v,i)=>w[i]*(v-mx)*(y[i]-my)));fit={b:sxy/sxx,a:my-sxy/sxx*mx,r:sxy/Math.sqrt(sxx*syy)}}
function labelSet(){const forced=new Set([...(cur&&!ST[cur].abroad?[cur]:[]),...[...mor].filter(k=>!ST[k].abroad)]);
 const pri=[...forced,'SOF',...LAND.slice().sort((a,b)=>b.el-a.el).map(s=>s.code)];
 const seen=new Set(),order=pri.filter(k=>!seen.has(k)&&seen.add(k)),placed=[],out=[];
 const dots=LAND.map(s=>({x:sxs(lx(s)),y:sys(shr(s)),r:sr(s)+1,k:s.code}));
 const hit=(a,b)=>!(a.x1<b.x0||a.x0>b.x1||a.y1<b.y0||a.y0>b.y1);
 for(const k of order){if(out.length>=16&&!forced.has(k))break;const s=ST[k],cx=sxs(lx(s)),cy=sys(shr(s)),r=sr(s),w=k.length*6.3+3;
  const opts=[[cx+r+2,cy+3.4,'start'],[cx-r-2,cy+3.4,'end'],[cx,cy-r-3,'middle'],[cx,cy+r+10,'middle']];
  for(const [x,y,an] of opts){const x0=an==='start'?x:an==='end'?x-w:x-w/2,bb={x0,x1:x0+w,y0:y-8.5,y1:y+2};
   if(bb.x0<SCl-4||bb.x1>SCW-1||bb.y0<0||bb.y1>SCH-SCb+2)continue;
   if(placed.some(q=>hit(q,bb)))continue;
   if(!forced.has(k)&&dots.some(d=>d.k!==k&&bb.x0<d.x+d.r&&bb.x1>d.x-d.r&&bb.y0<d.y+d.r&&bb.y1>d.y-d.r))continue;
   placed.push(bb);out.push({k,x,y,an});break}}
 return out}
function drawScSkeleton(){const el=document.getElementById('cSc');scScales();
 const xt=[1,10,100,1000].filter(v=>Math.log10(v)>=xD[0]&&Math.log10(v)<=xD[1]),yt=d3.range(yD[0],yD[1]+.01,yD.step);
 const g=xt.map(v=>`<line class="gl" x1="${sxs(Math.log10(v))}" x2="${sxs(Math.log10(v))}" y1="${SCt}" y2="${SCH-SCb}"/><text class="tk" x="${sxs(Math.log10(v))}" y="${SCH-SCb+13}" text-anchor="middle">${v>=1000?'1k':v}</text>`).join('')+
  yt.map(v=>`<line class="gl" x1="${SCl}" x2="${SCW-SCr}" y1="${sys(v)}" y2="${sys(v)}"/><text class="tk" x="${SCl-5}" y="${sys(v)+3}" text-anchor="end">${v}</text>`).join('');
 const xa=xD[0]+.04,xb=xD[1]-.04,fa=fit.a+fit.b*xa,fb=fit.a+fit.b*xb;
 const ord=LAND.slice().sort((a,b)=>b.el-a.el);
 const dots=ord.map(s=>`<circle class="dt" data-k="${s.code}" cx="${sxs(lx(s)).toFixed(1)}" cy="${sys(shr(s)).toFixed(1)}" r="${sr(s).toFixed(1)}" style="fill:var(${PK[s.win].v})"><title>${escH(s.name)}: ${shr(s).toFixed(1)}% ${PK[scP].s}, ${fmt(Math.round(s.el/s.area))} registered voters per km²</title></circle>`).join('');
 const hits=ord.map(s=>`<circle class="hit" data-k="${s.code}" cx="${sxs(lx(s)).toFixed(1)}" cy="${sys(shr(s)).toFixed(1)}" r="${Math.max(sr(s),7).toFixed(1)}"/>`).join('');
 const rtxt=Math.abs(fit.r)<.2?`Density says little about ${PK[scP].s} support`:fit.r>0?`Denser districts give <b>${PK[scP].s}</b> more of the vote`:`Denser districts give <b>${PK[scP].s}</b> less of the vote`;
 el.innerHTML=`<h3>Density vs the vote</h3><p class="cs">Each dot is a province or city, coloured by its winner. Size is registered voters. Pick a party for the vertical axis.</p>
 <div class="scp" role="group" aria-label="Party on the vertical axis">${RACE.map(k=>`<button data-p="${k}" aria-pressed="${k===scP}"><i class="dot" style="background:var(${PK[k].v})"></i>${PK[k].s}</button>`).join('')}</div>
 <svg viewBox="0 0 ${SCW} ${SCH}" role="img" aria-label="Scatter of registered voters per square kilometre against ${PK[scP].n} share of the vote, by district">${g}
 <line class="fit" x1="${sxs(xa)}" y1="${sys(fa)}" x2="${sxs(xb)}" y2="${sys(fb)}"/>${dots}<g id="scLb"></g>${hits}
 <text class="ax" x="${(SCl+SCW-SCr)/2}" y="${SCH-4}" text-anchor="middle">Voters per km² · log scale</text>
 <text class="ax" transform="translate(9 ${(SCt+SCH-SCb)/2}) rotate(-90)" text-anchor="middle">${PK[scP].s} % of votes</text></svg>
 <p class="nt">${rtxt} (<b>r = ${fit.r>=0?'':'−'}${Math.abs(fit.r).toFixed(2)}</b>, weighted by votes; line shows the fit). This compares districts, not individual voters.</p>`;
 const svgS=el.querySelector('svg');
 svgS.addEventListener('click',e=>{const h=e.target.closest('[data-k]');if(h)setFocus(h.dataset.k)});
 svgS.addEventListener('pointerover',e=>{if(e.pointerType!=='mouse')return;const h=e.target.closest('[data-k]');if(h)peekSet(h.dataset.k)});
 svgS.addEventListener('pointerout',e=>{if(e.pointerType==='mouse'&&e.target.closest('[data-k]'))peekSet(null)});
 el.querySelector('.scp').addEventListener('click',e=>{const b=e.target.closest('button');if(b)scSet(b.dataset.p)})}
function scSet(k){if(!PK[k]||k===scP||!RACE.includes(k))return;scP=k;drawScSkeleton();drawScSel()}
function drawScSel(){const el=document.getElementById('cSc');const sel=selStates();el.classList.toggle('has',sel.length>0);
 el.querySelectorAll('.dt').forEach(c=>{const k=c.dataset.k;c.classList.toggle('on',k===cur);c.classList.toggle('in',mor.has(k)&&k!==cur)});
 const lb=el.querySelector('#scLb');if(lb)lb.innerHTML=labelSet().map(l=>`<text class="lb" x="${l.x.toFixed(1)}" y="${l.y.toFixed(1)}" text-anchor="${l.an}">${l.k}</text>`).join('')}
// ranked: share of registered voters / share of land
const RK=LAND.slice().sort((a,b)=>b.pPct/b.aPct-a.pPct/a.aPct);
const rkLg=RK.map(s=>Math.log2(s.pPct/s.aPct)),rkLO=Math.floor(d3.min(rkLg)-.6),rkHI=Math.ceil(d3.max(rkLg)+.6),rkSP=rkHI-rkLO,rkCP=-rkLO/rkSP*100,rkPos=v=>(Math.log2(v)-rkLO)/rkSP*100;
function drawRkSkeleton(){const el=document.getElementById('cRk');
 const tk=[[.1,'0.1×'],[.25,'¼×'],[.5,'½×'],[1,'1×'],[2,'2×'],[4,'4×'],[10,'10×']].filter((x,i,arr)=>true).filter(([v])=>(rkPos(v)>4&&rkPos(v)<96)||v===1);
 el.innerHTML=`<h3>All 28, ranked</h3><p class="cs">A province's share of registered voters divided by its share of land. Bars right of the line gain size when resized; bars left shrink.</p>
 <div class="rk-h"><span>◀ shrinks</span><span>grows ▶</span></div><div class="rk-ax" id="rkAx">${tk.map(([v,l])=>`<span style="left:${rkPos(v)}%">${l}</span>`).join('')}</div>
 <div class="rk" id="rk" style="--c:${rkCP}%">${RK.map(s=>{const r=s.pPct/s.aPct,lg=Math.log2(r),w=Math.abs(lg)/rkSP*100,l=lg>=0?rkCP:rkCP-w;
  return `<button class="rk-row" data-k="${s.code}" aria-label="${escH(s.name)}, ${rkTxt(r)} when resized to its voters"><span>${s.code}</span><span class="tk" style="--c:${rkCP}%"><i class="br" style="left:${l}%;width:${Math.max(w,.5)}%;background:var(${PK[s.win].v})"></i><span class="vl"></span></span></button>`}).join('')}</div>`;
 const rk=el.querySelector('#rk');
 rk.addEventListener('click',e=>{const b=e.target.closest('.rk-row');if(b)setFocus(b.dataset.k)});
 rk.addEventListener('pointerover',e=>{if(e.pointerType!=='mouse')return;const b=e.target.closest('.rk-row');if(b)peekSet(b.dataset.k)});
 rk.addEventListener('pointerleave',e=>{if(e.pointerType==='mouse')peekSet(null)})}
function drawRkSel(){const rows=document.getElementById('rk').children;
 RK.forEach((s,i)=>{const r=rows[i],on=s.code===cur;r.setAttribute('aria-current',on);r.classList.toggle('in',mor.has(s.code)&&!on);const v=r.querySelector('.vl');
  if(on){const q=s.pPct/s.aPct,lg=Math.log2(q),w=Math.abs(lg)/rkSP*100;v.textContent='#'+(i+1)+' · '+rkTxt(q);v.style.left=v.style.right='';
   if(lg>=0&&rkCP+w>58){v.style.right=(100-(rkCP-1))+'%';v.style.left='auto'}else if(lg>=0){v.style.left=(rkCP+w+1.5)+'%';v.style.right='auto'}else if(rkCP-w>40){v.style.right=(100-(rkCP-w-1.5))+'%';v.style.left='auto'}else{v.style.left=(rkCP+1.5)+'%';v.style.right='auto'}}
  else v.textContent=''})}
function drawCharts(){drawWho();drawScSel();drawRkSel()}
drawScSkeleton();drawRkSkeleton();
'''
rep('// ---- init ----',JS+'// ---- init ----')
rep("build();syncBtns();drawLegend();","build();syncBtns();drawLegend();drawCharts();document.getElementById('note').textContent+=` Charts: density is registered voters per km² of district area (log scale); the line is a fit across the 28 land shapes weighted by votes and compares districts, not individual voters. The ranking divides a province’s share of registered voters by its share of land.`;")
rep("sortPieces();syncDD();drawPanel();drawCap();syncBtns();markSel();render();if(cur)ensureVisible(cur)}","sortPieces();syncDD();drawPanel();drawCap();syncBtns();markSel();render();drawCharts();if(cur)ensureVisible(cur)}")
rep("colFrom=now;mode=m;colTo=CT[m];CM=0;sel.value=m;drawLegend();","colFrom=now;mode=m;colTo=CT[m];CM=0;sel.value=m;drawLegend();if(typeof scSet==='function'&&m!=='win')scSet(m);")
open(B+'bg/template_bg.html','w').write(t);print(len(t))

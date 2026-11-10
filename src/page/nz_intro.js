/* Briefing: lives in a shadow root so its styles cannot touch the map page. Shown above the map on both layers (General and Māori), so the two read as one group. */
(function () {
  /* Switching layers must not carry the old scroll position over (Safari kept the General page's offset and opened the Māori page at its foot). */
  try { history.scrollRestoration = 'manual'; } catch (e) {}
  var toMap = /[?&]map\b/.test(location.search);   /* ?map comes from the layer tabs: land on the map, not the briefing */
  /* Safari can restore the previous page's scroll offset late, after load. Until the reader touches the page (or 2.5 s pass), keep putting the page where this arrival belongs: the top, or the map. */
  var touched = false, until = Date.now() + 2500;
  ['touchstart', 'pointerdown', 'mousedown', 'wheel', 'keydown'].forEach(function (ev) { window.addEventListener(ev, function () { touched = true; }, { passive: true, once: true }); });
  var place = function () {
    if (touched || Date.now() > until) return;
    if (toMap) { var m = document.getElementById('mapstart'); if (m && Math.abs(m.getBoundingClientRect().top - 16) > 2) m.scrollIntoView(); }
    else if (window.scrollY > 0) window.scrollTo(0, 0);
  };
  place(); setTimeout(place, 0); setTimeout(place, 150); setTimeout(place, 500);
  window.addEventListener('load', place); window.addEventListener('scroll', place, { passive: true });
  window.addEventListener('pageshow', function (e) { if (e.persisted) { touched = false; until = Date.now() + 2500; place(); } });
  var host = document.getElementById('intro-host'), tpl = document.getElementById('intro-tpl');
  if (host) { var ln = document.getElementById('layernav'); if (ln) { var bp = document.createElement('p'); bp.style.cssText = 'margin:-4px 0 14px;font:500 14px var(--f-body)'; bp.innerHTML = '<a href="' + '#intro-host' + '" style="color:var(--ink);text-underline-offset:3px;display:inline-block;padding:10px 0">' + 'Read the briefing' + ' \u2191</a>'; bp.firstChild.addEventListener('click', function (e) { e.preventDefault(); host.scrollIntoView({ behavior: 'smooth' }); }); ln.insertAdjacentElement('afterend', bp); } }
  if (!host || !tpl) { if (host) host.remove(); return; }
  var R = host.attachShadow({ mode: 'open' }); R.appendChild(tpl.content.cloneNode(true)); host.style.display = 'block';
  var sk = R.getElementById('skip'); if (sk) sk.addEventListener('click', function (e) { e.preventDefault(); var m = document.getElementById('mapstart'); if (m) m.scrollIntoView({ behavior: 'smooth' }); });

  /* candidate rail, party filter */
(function(){
var rail=R.getElementById('rail'),cards=[].slice.call(rail.children),dots=R.getElementById('dots'),pv=R.getElementById('pv'),nx=R.getElementById('nx'),cur=0;
cards.forEach(function(c,i){var b=document.createElement('button');b.className='dot';b.setAttribute('aria-label','Card '+(i+1));b.onclick=function(){go(i)};dots.appendChild(b)});
function go(i){i=Math.max(0,Math.min(cards.length-1,i));var c=cards[i];rail.scrollTo({left:c.offsetLeft-(rail.clientWidth-c.offsetWidth)/2,behavior:'smooth'})}
function upd(){var m=rail.scrollLeft+rail.clientWidth/2,b=0,d=1e9;cards.forEach(function(c,i){var x=Math.abs(c.offsetLeft+c.offsetWidth/2-m);if(x<d){d=x;b=i}});if(rail.scrollLeft<4)b=0;else if(rail.scrollLeft+rail.clientWidth>=rail.scrollWidth-4)b=cards.length-1;cur=b;[].forEach.call(dots.children,function(e,i){e.setAttribute('aria-current',i===b)});pv.disabled=b===0;nx.disabled=b===cards.length-1}
var ticking=false;rail.addEventListener('scroll',function(){if(ticking)return;ticking=true;requestAnimationFrame(function(){ticking=false;upd()})},{passive:true});
pv.onclick=function(){go(cur-1)};nx.onclick=function(){go(cur+1)};
rail.addEventListener('keydown',function(e){if(e.key==='ArrowRight'){e.preventDefault();go(cur+1)}if(e.key==='ArrowLeft'){e.preventDefault();go(cur-1)}});
upd();
cards.forEach(function(c,i){c.style.setProperty('--i',i)});
if('IntersectionObserver' in window){var cio=new IntersectionObserver(function(es){es.forEach(function(e){e.target.classList.toggle('on',e.intersectionRatio>=.55)})},{root:rail,threshold:[0,.25,.55,.75,1]});cards.forEach(function(c){cio.observe(c)})}else cards[0].classList.add('on');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){rail.classList.add('in');io.disconnect()}})},{threshold:.3});io.observe(rail)}else rail.classList.add('in');
var hw=R.getElementById('hw'),seats=[].slice.call(hw.querySelectorAll('.s')),cn=R.getElementById('cn'),cl=R.getElementById('cl'),lgs=[].slice.call(R.querySelectorAll('.lg')),sel=-1;
lgs.forEach(function(b,i){b.setAttribute('aria-pressed','false');b.onclick=function(){sel=sel===i?-1:i;lgs.forEach(function(x,j){x.setAttribute('aria-pressed',j===sel)});hw.classList.toggle('f',sel>-1);var n=0;seats.forEach(function(s){var on=+s.dataset.p===sel;s.classList.toggle('on',on);if(on)n++});if(sel>-1){cn.textContent=n;cl.textContent=b.textContent.replace(/\s*\d+$/,'')+' seats'}else{cn.textContent=131;cl.textContent='seats'}}});
})();

})();

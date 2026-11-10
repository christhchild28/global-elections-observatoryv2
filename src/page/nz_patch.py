"""Derive nz.template.html (multi-party winner colouring) from warp.template.html. Every edit must match exactly once, so a drifting
base template fails loudly instead of silently producing a two-candidate page."""
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(H, 'warp.template.html'), encoding='utf-8').read()
def sub(old, new, count=1):
    global t
    if t.count(old) != count: sys.exit('nz_patch: expected %d match(es), found %d for: %r' % (count, t.count(old), old[:90]))
    t = t.replace(old, new)
def between(a, b, new):          # replace from the start of a through the end of b (first b after a)
    global t
    i = t.find(a); j = t.find(b, i)
    if i < 0 or j < 0: sys.exit('nz_patch: markers not found: %r .. %r' % (a[:60], b[:60]))
    t = t[:i] + new + t[j + len(b):]

# --- party colour variables (filled by the builder) ---
sub('</style>', '/*PARTYCSS*/\n</style>')

# --- side panel: party key + stacked bars + margin legend ---
between('<h2>Share of {{STATE}} that {{A}} won</h2>', '<div class="keyline"><span><i id="k-b"></i>{{A}}</span><span><i id="k-r"></i>{{B}}</span></div>',
        '<h2>Who won what</h2>\n      <p class="sub">The same election, counted three ways.</p>\n      <div class="keyline" id="keyline"></div>')
between('<h2>County margin</h2>', '<span>{{A}} +60</span></div>',
        '<h2>Margin of victory</h2>\n        <div class="ramp" id="ramp"></div>\n        <div class="ticks"><span>Close</span><span></span><span>Safe seat</span></div>\n        <p class="sw-note">Each electorate takes its winner’s colour. Paler means a closer contest, shown by the winning margin in votes.</p>')
sub('<th>Residents</th><th>{{A}}</th><th>{{B}}</th><th>Margin</th>', '<th>Residents</th><th>Party</th><th>Candidate</th><th>Margin (votes)</th>')

# --- data prep ---
between('var totPop = 0, totLand = 0, tot = {', "if (c.dem) { tot.popD += c.pop; tot.landD += c.landS; tot.cD++; }",
'''var PARTIES = META.parties, NP = PARTIES.length;
  var totPop = 0, totLand = 0, tot = { cnt: PARTIES.map(function () { return 0; }), pop: PARTIES.map(function () { return 0; }), land: PARTIES.map(function () { return 0; }) };
  C.forEach(function (c) { totPop += c.pop; totLand += c.landArea; });
  var mgs = C.map(function (c) { return c.d; }).sort(function (a, b) { return a - b; }), MCAP = Math.max(1, mgs[Math.floor(.9 * (mgs.length - 1))]);   // 90th-percentile margin = full tint
  C.forEach(function (c, i) {
    c.i = i; c.pi = c.r; c.mv = c.d; c.m = Math.min(1, c.mv / MCAP); c.dem = true;
    c.popS = c.pop / totPop; c.landS = c.landArea / totLand; c.f = c.popS / c.landS;
    c.R = dz(c.real); c.H = dz(c.hex); c.H2 = dz(c.hex2); c.W = dz(c.warp); c.K = c.R.length / 2;
    tot.cnt[c.pi]++; tot.pop[c.pi] += c.pop; tot.land[c.pi] += c.landS;''')
sub('var shares = { land: tot.landD, tile: tot.cD / C.length, pop: tot.popD / totPop, votes: tot.d / (tot.d + tot.r) };\n', '')

# --- colour ---
sub("rm: h2r(cv('--r-mid')), rd: h2r(cv('--r-deep')) }; }", "rm: h2r(cv('--r-mid')), rd: h2r(cv('--r-deep')), pc: PARTIES.map(function (p, k) { return h2r(cv('--p' + k)); }) }; }\n  function pcol(c) { return mix(stops.n, stops.pc[c.pi], .42 + .58 * Math.sqrt(c.m)); }")
sub("return (PR && colorMode === 1) ? colorT(c.sw / SWCAP) : colorAt(c.m); }", "return pcol(c); }")
sub("'\"><i style=\"background:' + css(colorAt(c.m)) + '\"></i>'", "'\"><i style=\"background:' + css(pcol(c)) + '\"></i>'")
between("var st = [], k; for (k = -1;", "document.getElementById('k-r').style.background = css(stops.rm);",
'''document.getElementById('ramp').style.background = 'linear-gradient(90deg,' + css(mix(stops.n, stops.pc[0], .42)) + ',' + css(stops.pc[0]) + ')';
    document.getElementById('keyline').innerHTML = PARTIES.map(function (p, k) { return tot.cnt[k] ? '<span><i style="background:' + css(stops.pc[k]) + '"></i>' + esc(p.name) + ' <b>' + tot.cnt[k] + '</b></span>' : ''; }).join('');''')

# --- bars: stacked by party ---
between("var bl = { land:", "    uiMode();\n  }\n\n  /* ---------- county card",
'''var bl = { land: 'Land area won', tile: 'Electorates won', pop: 'People in the electorates won' };
  function drawBars() {
    var box = document.getElementById('bars'); box.textContent = '';
    ['land', 'tile', 'pop'].forEach(function (k) {
      var sh = PARTIES.map(function (p, j) { return k === 'land' ? tot.land[j] : k === 'tile' ? tot.cnt[j] / C.length : tot.pop[j] / totPop; });
      var top = sh.indexOf(Math.max.apply(null, sh)), row = document.createElement('div'); row.className = 'brow'; row.dataset.k = k;
      var l = document.createElement('div'); l.className = 'l'; l.textContent = bl[k];
      var sm = document.createElement('small'); sm.textContent = PARTIES.map(function (p, j) { return sh[j] > 0 ? p.name + ' ' + (sh[j] * 100).toFixed(sh[j] < .1 ? 1 : 0) + '%' : ''; }).filter(Boolean).join(' · ');
      l.appendChild(sm);
      var v = document.createElement('div'); v.className = 'v'; v.textContent = pct(sh[top]) + '%'; v.title = PARTIES[top].name;
      var tr = document.createElement('div'); tr.className = 'track'; tr.setAttribute('role', 'img'); tr.setAttribute('aria-label', bl[k] + ': ' + sm.textContent);
      PARTIES.forEach(function (p, j) { if (!(sh[j] > 0)) return; var s = document.createElement('i'); s.style.flex = sh[j] + ' 1 0'; s.style.background = css(stops.pc[j]); s.title = p.name + ' ' + (sh[j] * 100).toFixed(1) + '%'; tr.appendChild(s); });
      row.appendChild(l); row.appendChild(v); row.appendChild(tr); box.appendChild(row);
    });
    uiMode();
  }

  /* ---------- county card''')

# --- card ---
between("function cardHTML(c) {", "'</tbody></table></div>';\n  }",
'''function cardHTML(c) {
    var P = PARTIES[c.pi], cw = pcol(c), dk = lum(cw) < .3, col = css(cw), mx = Math.max(c.landS, c.popS), lead = P.name + ' +' + fmt(c.mv), cand = (META.cand || {})[c.name] || '';
    return '<div class="pn-bar" style="background:' + col + '"></div>' + chipsHTML(c.i) +
      '<div class="pn-hd"><div style="min-width:0"><span class="pn-n">' + esc(c.name) + '</span><span class="pn-c">' + esc(META.kindLabel) + ' · ' + fmt(c.pop) + ' people</span></div>' +
      '<div class="pn-r"><span class="pn-p" style="background:' + col + ';color:' + (dk ? '#fff' : '#0b0b0b') + '">' + esc(lead) + '</span>' +
      '<button type="button" class="pn-b pn-tgl" aria-expanded="' + full + '">' + (full ? 'Less' : 'More') + '</button>' +
      '<button type="button" class="pn-b pn-x" aria-label="Close">✕</button></div></div>' +
      '<div class="pn-key">' + barRow('Land', c.landS, mx, 'var(--ink-3)') + barRow('People', c.popS, mx, col) + '<div class="pn-rel"><b>' + fx(c).replace(' ', '</b> ') + ' by people</div></div>' +
      '<div class="pn-more"><div class="pn-st"><span>Winner <b>' + esc(cand ? cand + ' (' + P.name + ')' : P.name) + '</b></span><span>Margin <b>' + fmt(c.mv) + ' votes</b></span><span>Electoral population <b>' + fmt(c.pop) + '</b></span><span>Hexagons <b>' + c.n + '</b></span><span>Land <b>' + pct1(c.landS) + '</b></span><span>People <b>' + pct1(c.popS) + '</b></span></div></div>';
  }''')

# --- copy ---
between("var aW = tot.d > tot.r,", "dek.appendChild(document.createTextNode(p[1])); });",
'''var ord = PARTIES.map(function (p, k) { return k; }).sort(function (a, b) { return tot.cnt[b] - tot.cnt[a]; }), w1 = ord[0], w2 = ord[1], ppl = META.people || (META.state + ' residents');
  var dek = document.getElementById('dek'), parts = [
    ['b', PARTIES[w1].name + ' won ' + tot.cnt[w1] + ' of ' + C.length + ' ' + META.unitsLabel], ['t', ', covering ' + pct(tot.land[w1]) + '% of the land. '],
    ['b', PARTIES[w2].name + ' won ' + tot.cnt[w2]], ['t', (tot.land[w2] < tot.pop[w2] / totPop ? ' on ' + pct(tot.land[w2]) + '% of the land, because its seats are packed into cities where the people are. ' : ' on ' + pct(tot.land[w2]) + '% of the land, but its seats hold just ' + pct(tot.pop[w2] / totPop) + '% of the people. ') + (META.dekNote || '')]];
  parts.forEach(function (p) { if (p[0] === 'b') { var b = document.createElement('b'); b.textContent = p[1]; dek.appendChild(b); } else dek.appendChild(document.createTextNode(p[1]));''' + ' });')
between("document.getElementById('method').textContent = '", "cannot touch all of their neighbors. In Lens view", "document.getElementById('method').textContent = 'The cartogram uses hexpack: ' + fmt(D.N) + ' hexagons (one per ' + fmt(D.unit) + ' people, at least one per electorate) are laid out along the population-warped electorate shapes so that every electorate is one connected piece. North and South Islands are drawn as separate landmasses, with Cook Strait left open. ' + D.stats.kept + ' of the ' + D.stats.real + ' borders on the real map are still shared borders here (' + pct(D.stats.kept / D.stats.real) + '%). In Lens view")
sub("[c.name, fmt(c.pop), fmt(c.d), fmt(c.r), (c.dem ? META.a + ' +' : META.b + ' +') + Math.round(Math.abs(c.m) * 100), pct1(c.landS) + ' → ' + pct1(c.popS)]", "[c.name, fmt(c.pop), PARTIES[c.pi].name, (META.cand || {})[c.name] || '', fmt(c.mv), pct1(c.landS) + ' → ' + pct1(c.popS)]")

# --- layer switch between the general and Māori electorate pages ---
sub('<p class="dek" id="dek"></p>', '<p class="dek" id="dek"></p>\n    <div class="layernav" id="layernav" role="group" aria-label="Electorate layer"></div>')
sub('/*PARTYCSS*/', '/*PARTYCSS*/\n.layernav { display: flex; gap: 8px; flex-wrap: wrap; margin: 0 0 14px; }\n.layernav a { font: 500 14px/1 var(--f-body); min-height: 44px; display: inline-flex; align-items: center; padding: 0 16px; border: 1px solid var(--hair); border-radius: 999px; color: var(--ink-2); text-decoration: none; }\n.layernav a[aria-current="page"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }')
sub("showCard(null);\n  recolor();", "(function () { var g = META.layer === 'general'; document.getElementById('layernav').innerHTML = '<a href=\"' + (g ? './' : '../?map') + '\"' + (g ? ' aria-current=\"page\"' : '') + '>General (64)</a><a href=\"' + (g ? 'maori/?map' : './') + '\"' + (g ? '' : ' aria-current=\"page\"') + '>M\u0101ori (7)</a>'; })();\n  showCard(null);\n  recolor();")

# --- charts dropdown above the electorate table ---
sub('  <details>\n    <summary>All {{NCOUNTIES}}', """  <details id="chartsd" class="chartsd">
    <summary>Charts: density vs the vote, and who grows or shrinks</summary>
    <div class="chartbody"><section class="chart" id="cSc" aria-live="polite"></section><section class="chart" id="cRk"></section></div>
  </details>

  <details>
    <summary>All {{NCOUNTIES}}""")
sub('/*PARTYCSS*/\n.layernav', '/*PARTYCSS*/\n/*CHARTCSS*/\n.layernav')
sub("    hlI = i; syncHL();", "    hlI = i; syncHL(); if (window.__chartSel) window.__chartSel(i);")
sub("  showCard(null);\n  recolor();", "/*CHARTJS*/\n  showCard(null);\n  recolor();")
t = t.replace('/*CHARTCSS*/', open(os.path.join(H, 'nz_charts.css'), encoding='utf-8').read()).replace('/*CHARTJS*/', open(os.path.join(H, 'nz_charts.js'), encoding='utf-8').read())
sub('<p>{{SOURCE}}</p>', '<p>{{SOURCE}}</p>\n    <p class="byline">By Christian Theodore &middot; Media Intelligence Architect, Fovea</p>')
sub('<title>{{STATE}} Population Lens</title>', '<title>{{STATE}} 2026: {{OFFICE}}, land vs people</title>')
# --- briefing (intro) above the map: shadow-DOM block on the general layer, plus a link to it on the Māori layer ---
import nz_intro
sub('<!--/next--></nav>\n    <p class="kicker">', '<!--/next--></nav>\n    <div id="intro-host" hidden></div>\n    <p class="kicker" id="mapstart">')
sub('.layernav a[aria-current="page"]', '/*INTROVARS*/\n.layernav a[aria-current="page"]')
sub('<script>\n(function () {\n  var LIVE', '<template id="intro-tpl"><style>/*INTROCSS*/</style>/*INTROHTML*/</template>\n<script>\n(function () {\n  var LIVE')
sub("  showCard(null);\n  recolor();", "/*INTROJS*/\n  showCard(null);\n  recolor();")
_st, _mk = nz_intro.render()
t = t.replace('/*INTROVARS*/', nz_intro.party_vars() + '\n#intro-host { margin: 6px 0 34px; padding-bottom: 26px; border-bottom: 1px solid var(--hair); }\n#mapstart { scroll-margin-top: 16px; }').replace('/*INTROCSS*/', _st).replace('/*INTROHTML*/', _mk).replace('/*INTROJS*/', open(os.path.join(H, 'nz_intro.js'), encoding='utf-8').read())

open(os.path.join(H, 'nz.template.html'), 'w', encoding='utf-8').write(t)
print('wrote nz.template.html', len(t))

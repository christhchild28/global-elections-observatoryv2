"""Election briefing: who is elected, how the system works, what the result means at home and abroad.
Content lives in content/briefings/<id>.json. render(content) -> (css, html). inject() puts it above the map of a built page.
Shadow DOM keeps its styles away from the map page; it reads the host page's colour variables (see briefing.css :host)."""
import html, json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
E = html.escape

def _hemi(parties, total, majority):
    rows = 3 if total <= 60 else 6 if total <= 140 else 8
    r0, r1 = .42, 1.0
    rad = [r0 + (r1 - r0) * i / (rows - 1) for i in range(rows)]
    tot = sum(rad); counts = [round(total * r / tot) for r in rad]; counts[-1] += total - sum(counts)
    seats = []
    for r, c in zip(rad, counts):
        for k in range(c):
            seats.append((math.pi * (1 - k / (c - 1)) if c > 1 else math.pi / 2, r))
    seats.sort(key=lambda s: (-s[0], s[1]))
    W, H = 360, 200; cx, cy = W / 2, H - 14; R = W / 2 - 10
    cum, s = [], 0
    for p in parties: s += p['seats']; cum.append(s)
    assert s == total, 'seats %d != total %d' % (s, total)
    rr = 3.15 if total > 100 else 3.9 if total > 60 else 5.6
    out = []
    for n, (a, r) in enumerate(seats):
        pi = next(j for j, c in enumerate(cum) if n < c)
        out.append('<circle class="s p%d%s" cx="%.1f" cy="%.1f" r="%.2f" data-p="%d"/>' % (pi, ' edge' if parties[pi].get('edge') else '', cx + R * r * math.cos(a), cy - R * r * math.sin(a), rr, pi))
    a = seats[majority - 1][0]
    m = '<line class="maj" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (cx + R * .34 * math.cos(a), cy - R * .34 * math.sin(a), cx + R * 1.08 * math.cos(a), cy - R * 1.08 * math.sin(a))
    return '<svg id="hemi" viewBox="0 0 %d %d" role="img" aria-label="%s">%s%s</svg>' % (W, H, E('Parliament of %d seats by party' % total), ''.join(out), m)

def _paras(items, cls=''):
    out = ''
    for it in items:
        if isinstance(it, str): out += '<p>%s</p>' % it
        else: out += '<h4>%s</h4><p>%s</p>' % (it['h'], it['p'])
    return out

def render(c):
    P = c.get('visual', {}).get('parties', [])
    vars_l = ''.join('--c%d:%s;' % (i, p['light']) for i, p in enumerate(P))
    vars_d = ''.join('--c%d:%s;' % (i, p.get('dark', p['light'])) for i, p in enumerate(P))
    pcss = ''.join('.s.p%d{fill:var(--c%d)}.lg.p%d i,tr.p%d .dot{background:var(--c%d)}.pbar .p%d{background:var(--c%d)}' % ((i,) * 7) for i in range(len(P)))
    css = open(os.path.join(HERE, 'briefing.css'), encoding='utf-8').read()
    css += ':host{%s}\n@media (prefers-color-scheme:dark){:host{%s}}\n%s' % (vars_l, vars_d, pcss)
    v = c.get('visual')
    b = '<p class="kick">%s</p><h1>%s</h1><p class="lede">%s</p><p class="by">%s</p><a class="skip" href="#mapstart" id="skip">Skip to the map &darr;</a>' % (E(c['kicker']), E(c['title']), c['lede'], E(c.get('byline', 'By Christian Theodore · Media Intelligence Architect, Fovea')))
    b += '<h2>At a glance</h2><div class="stats">%s</div>' % ''.join('<div class="stat"><b>%s</b><span>%s</span></div>' % (E(s['n']), E(s['l'])) for s in c['stats'])
    if v and v['type'] == 'hemicycle':
        b += '<div class="hemiwrap" id="hw">%s<div class="center"><b id="cn">%d</b><span id="cl">seats</span></div></div>' % (_hemi(P, v['total'], v['majority']), v['total'])
        b += '<p class="majlab">Dashed line: seat %d, where a majority begins</p>' % v['majority']
        b += '<div class="legend" id="lg" role="group" aria-label="Filter seats by party">%s</div>' % ''.join('<button type="button" class="lg p%d"><i></i>%s <b>%d</b></button>' % (i, E(p['name']), p['seats']) for i, p in enumerate(P))
    if v and v['type'] == 'bar':
        b += '<div class="pbar" role="img" aria-label="%s">%s%s</div>' % (E(v['label']), ''.join('<div class="p%d%s" style="flex:%s">%s</div>' % (i, ' edge' if p.get('edge') else '', p['flex'], E(p['text'])) for i, p in enumerate(P)),
            '<span class="tick" style="position:absolute"></span>' if False else '')
        b += '<div class="pbar-l">%s</div>' % ''.join('<span>%s</span>' % E(x) for x in v['ends'])
    if c.get('visual_note'): b += '<p class="note">%s</p>' % c['visual_note']
    t = c.get('table')
    if t:
        b += '<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
            ''.join('<th class="%s">%s</th>' % (h.get('cls', ''), E(h['t'])) for h in t['head']),
            ''.join('<tr class="%s">%s</tr>' % ('p%d' % r['p'] if 'p' in r else '', ''.join('<td class="%s">%s%s</td>' % (t['head'][k].get('cls', ''), '<span class="dot"></span>' if (k == 0 and 'p' in r) else '', cell) for k, cell in enumerate(r['cells']))) for r in t['rows']))
        if t.get('note'): b += '<p class="note">%s</p>' % t['note']
    b += '<h2 class="c">Who is being elected</h2><div class="ctx">%s</div>' % _paras(c['elects'])
    s = c['system']
    b += '<h2 class="c">How the voting system works</h2><div class="ctx"><p class="oneline">%s</p><ol class="steps2">%s</ol>%s</div>' % (
        s['oneline'], ''.join('<li><b>%s</b>%s</li>' % (x['h'], x['p']) for x in s['steps']), _paras(s.get('more', [])))
    b += '<h2 class="c">What it means at home</h2><div class="ctx">%s</div>' % _paras(c['home'])
    b += '<h2 class="c">What it means for the world</h2><div class="ctx">%s</div>' % _paras(c['world'])
    o = c['otherway']
    b += '<h2 class="c">If it had gone the other way</h2><div class="ctx"><div class="panel other"><h3>%s</h3>%s</div></div>' % (o['h'], _paras(o['p']))
    b += '<div class="ctx"><p class="src"><b>Sources.</b> %s</p></div><p class="foot">%s Last updated %s.</p>' % (
        ' '.join('<a href="%s">%s</a>%s' % (E(x['u']), E(x['t']), x.get('after', '.')) for x in c['sources']), c.get('foot', 'Summaries describe public positions and published projections, not forecasts.'), E(c['asof']))
    return css, b

def block(c, extra_css='', extra_body=''):
    """The <div id=intro-host> + <template> pair that goes above the map. Mounted by briefing.js."""
    css, body = render(c)
    return '<div class="bfwrap"><div id="intro-host" hidden></div><template id="intro-tpl"><style>%s</style>%s</template></div><div id="mapstart"></div>' % (css + extra_css, body + extra_body)

def script():
    return open(os.path.join(HERE, 'briefing.js'), encoding='utf-8').read()

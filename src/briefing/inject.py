"""Upgrade the tap-to-morph country pages (brazil, bulgaria, trinidad-tobago, usa/2024) to the v2 page chrome:
gallery typography, Back / All elections / Next nav, and the election briefing above the map. Idempotent: re-running replaces the previous injection.
usage: python3 src/briefing/inject.py"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import briefing

# page dir -> (briefing id, depth to repo root, next page, next label)
PAGES = [
    ('usa', 'usa-midterms', None),   # hub is built by usa_hub.py
    ('usa/2024', 'usa-2024', 'brazil/'),
    ('brazil', 'brazil', 'trinidad-tobago/'),
    ('trinidad-tobago', 'trinidad-tobago', 'bulgaria/'),
    ('bulgaria', 'bulgaria', 'new-zealand/'),
]
LABEL = {'brazil/': 'Brazil', 'trinidad-tobago/': 'Trinidad and Tobago', 'bulgaria/': 'Bulgaria', 'new-zealand/': 'New Zealand', 'usa/': 'USA midterms', 'usa/2024/': 'USA 2024'}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400..800&family=IBM+Plex+Mono:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400..700&display=swap" rel="stylesheet">')
CSS = """/*v2-chrome*/
:root{--display:"Source Serif 4","Source Serif 4 Fallback",Georgia,serif;--body:"Archivo","Archivo Fallback","Helvetica Neue",Arial,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;--f-head:var(--display);--f-body:var(--body);--f-mono:var(--mono)}
@font-face{font-family:"Archivo Fallback";src:local("Arial"),local("Helvetica Neue");size-adjust:103.5%;ascent-override:84.8%;descent-override:20.3%;line-gap-override:0%}
@font-face{font-family:"Source Serif 4 Fallback";src:local("Times New Roman"),local("Times");size-adjust:109.2%;ascent-override:94.8%;descent-override:30.7%;line-gap-override:0%}
h1,h2{font-family:var(--display);letter-spacing:-.015em}
.pgnav{max-width:1000px;margin:0 auto;padding:12px 16px 0;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;column-gap:12px}
.back{display:inline-flex;align-items:center;gap:6px;min-height:44px;margin:0 0 2px -8px;padding:0 8px;color:var(--mute);text-decoration:none;font:500 12px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;border-radius:8px;white-space:nowrap}
.pgl{display:contents}.pgnav .pgl+.back{margin-left:0;text-align:right}.pgnav .pgl .back+.back{margin-left:auto;margin-right:auto;text-align:center}
button.back{background:none;border:0;cursor:pointer;-webkit-appearance:none;appearance:none}
.pgb[hidden]{display:none}.pgb[hidden]+a::before{content:"\\2190"}
.back:hover{color:var(--ink)}.back:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
@media(max-width:430px){.pgnav{column-gap:4px}.pgnav .back{font-size:10.5px;letter-spacing:.04em;padding-left:6px;padding-right:6px}}
@media(max-width:370px){.pgnav .back{font-size:9.5px;letter-spacing:.02em;padding-left:4px;padding-right:4px}}
.bfwrap{max-width:1000px;margin:0 auto;padding:18px 16px 0}
#intro-host{display:block}
.bfmap{max-width:1000px;margin:36px auto 0;padding:0 16px;font:500 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}
/*/v2-chrome*/"""
NAVJS = ('<script>(function(){try{history.scrollRestoration="manual"}catch(e){}if(!location.hash){var u=0,z=function(){if(!u)scrollTo(0,0)};["touchstart","wheel","keydown","mousedown"].forEach(function(t){addEventListener(t,function(){u=1},{once:true,passive:true})});z();addEventListener("DOMContentLoaded",z);addEventListener("load",z);addEventListener("pageshow",function(e){if(!e.persisted)z()});[60,200,500,1000,2000].forEach(function(t){setTimeout(z,t)});var g=function(){if(!u&&scrollY>0)scrollTo(0,0)};addEventListener("scroll",g,{passive:true});setTimeout(function(){removeEventListener("scroll",g)},6000)}'
         'var b=document.querySelector(".pgb");if(!b)return;b.addEventListener("click",function(){var r=document.referrer,ok=false;try{ok=!!r&&new URL(r).origin===location.origin}catch(e){}if(ok&&history.length>1)history.back();else location.href="%s"})})()</script>')

def nav(up, home_label, home_href, nxt):
    link = '<a class="back" href="%s%s" aria-label="Next election: %s">Next: %s &rarr;</a>' % (up, nxt, LABEL[nxt], LABEL[nxt]) if nxt else ''
    return '<nav class="pgnav" aria-label="Elections"><span class="pgl"><button type="button" class="back pgb">&larr; Back</button><a class="back" href="%s">%s</a></span>%s</nav>' % (home_href, home_label, link) + NAVJS % home_href

def strip(h):
    h = re.sub(r'/\*v2-chrome\*/.*?/\*/v2-chrome\*/', '', h, flags=re.S)
    h = re.sub(r'<!--v2-nav-->.*?<!--/v2-nav-->', '', h, flags=re.S)
    h = re.sub(r'<!--v2-briefing-js-->.*?<!--/v2-briefing-js-->', '', h, flags=re.S)
    return h

for d, bid, nxt in PAGES:
    if nxt is None: continue
    p = os.path.join(ROOT, d, 'index.html'); h = strip(open(p, encoding='utf-8').read())
    up = '../' * (d.count('/') + 1)
    c = json.load(open(os.path.join(ROOT, 'content', 'briefings', bid + '.json'), encoding='utf-8'))
    h = re.sub(r'<link[^>]*fonts\.googleapis\.com[^>]*>', '', h)
    h = h.replace('</head>', FONTS + '<style>' + CSS + '</style></head>', 1)
    home = ('../', 'USA midterms') if d == 'usa/2024' else (up, 'All elections')
    h = h.replace('<body>', '<body><!--v2-nav-->' + nav(up, home[1], home[0], up and nxt) + '<!--/v2-nav-->' + '<!--v2-nav-->' + briefing.block(c) + '<!--/v2-nav-->', 1)
    h = h.replace('</body>', '<!--v2-briefing-js--><script>' + briefing.script() + '</script><!--/v2-briefing-js--></body>', 1)
    open(p, 'w', encoding='utf-8').write(h); print('injected', d, len(h))

# USA midterms hub: briefing only (the hub generator owns its own nav and typography)
hp = os.path.join(ROOT, 'usa', 'index.html'); h = strip(open(hp, encoding='utf-8').read())
c = json.load(open(os.path.join(ROOT, 'content', 'briefings', 'usa-midterms.json'), encoding='utf-8'))
hcss = '<style>/*v2-chrome*/.bfwrap{max-width:960px;margin:0 auto;padding:18px 16px 0}#intro-host{display:block}#mapstart{scroll-margin-top:16px}/*/v2-chrome*/</style>'
h = h.replace('</head>', hcss + '</head>', 1)
h = h.replace('<a class="skip" href="#elections">Jump to the elections &darr;</a>', '<!--v2-nav-->' + briefing.block(c) + '<!--/v2-nav-->' + '<a class="skip" href="#elections">Jump to the elections &darr;</a>', 1)
h = h.replace('</body>', '<!--v2-briefing-js--><script>' + briefing.script() + '</script><!--/v2-briefing-js--></body>', 1)
open(hp, 'w', encoding='utf-8').write(h); print('injected hub', len(h))

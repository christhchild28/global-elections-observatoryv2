from playwright.sync_api import sync_playwright
D='/tmp/claude-0/-home-claude/23baac29-0d12-53fd-89ee-6f0a4956ec6e/scratchpad/br/'
d3=open(D+'npm/node_modules/d3/dist/d3.min.js').read()
def route(r):
    u=r.request.url
    if 'd3.min.js' in u: r.fulfill(body=d3,content_type='application/javascript')
    elif 'fonts.g' in u: r.fulfill(body='',content_type='text/css')
    else: r.continue_()
def st(pg): return pg.evaluate('__st()')
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':1100,'height':900});pg=ctx.new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
    pg.route('**/*',route);pg.goto('file://'+D+'tt_tap_morph.html');pg.wait_for_timeout(400)
    ok=lambda n,c:print('PASS' if c else 'FAIL',n)
    # 1 tap during global transition to pop (mid) must only focus, not morph
    pg.evaluate("__go(1)");pg.wait_for_timeout(150);pg.evaluate("__tap('PFT')");s=st(pg);ok('tap mid-toggle focuses only',s['cur']=='PFT' and not s['mor'])
    pg.wait_for_timeout(700);pg.evaluate("__go(0)");pg.wait_for_timeout(700)
    s=st(pg);ok('back to land, no morphed',s['T']==0 and not s['mor'] and max(s['M'].values())==0)
    # 2 rapid double tap = revert
    pg.evaluate("__tap('MYO')");pg.wait_for_timeout(100);pg.evaluate("__tap('MYO')");pg.wait_for_timeout(800)
    s=st(pg);ok('rapid tap-tap reverts',not s['mor'] and s['M']['MYO']==0)
    # 3 morph then global then back keeps morph set
    pg.evaluate("__tap('MGT');__tap('TSG')");pg.wait_for_timeout(700);pg.evaluate("__go(1)");pg.wait_for_timeout(700);pg.evaluate("__go(0)");pg.wait_for_timeout(700)
    s=st(pg);ok('morph set survives toggle',set(s['mor'])=={'MGT','TSG'} and s['M']['MGT']==1 and s['M']['PFT']==0)
    # 4 revert all button + Escape
    pg.click('#tRevert');pg.wait_for_timeout(700);s=st(pg);ok('revert all',not s['mor'] and s['cur'] is None and max(s['M'].values())==0)
    # 5 hover peek: panel shows hovered state, restores
    pg.evaluate("__tap('CMZ')");pg.wait_for_timeout(700)
    box=pg.evaluate("(()=>{const r=[...document.querySelectorAll('.pc')].find(e=>e.__data__&&e.__data__.st==='ARI').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
    pg.mouse.move(box[0],box[1]);pg.wait_for_timeout(120);ok('hover previews RS',pg.inner_text('.pn-n')=='Arima')
    pg.mouse.move(5,5);pg.wait_for_timeout(150);ok('hover restores BA',pg.inner_text('.pn-n')=='Cumuto/Manzanilla')
    # 6 escape
    pg.keyboard.press('Escape');pg.wait_for_timeout(100);ok('escape clears focus',st(pg)['cur'] is None)
    # 7 dropdown pick + All
    pg.click('#ddBtn');pg.click('.dd-opt:nth-child(3)');pg.wait_for_timeout(600);ok('dropdown morphs',len(st(pg)['mor'])==2)
    pg.click('#ddBtn');pg.click('.dd-opt:nth-child(1)');pg.wait_for_timeout(700);ok('dropdown All clears',not st(pg)['mor'])
    # 8 rearrange: drag in pop, reset
    pg.evaluate("__go(1)");pg.wait_for_timeout(700);pg.click('#tEdit')
    c=pg.evaluate("(()=>{const e=[...document.querySelectorAll('.pc')].find(e=>e.__data__&&e.__data__.st==='PFT'),r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
    pg.mouse.move(c[0],c[1]);pg.mouse.down();pg.mouse.move(c[0]+60,c[1]+10,steps=6);pg.mouse.up();pg.wait_for_timeout(400)
    ok('reset appears after drag',pg.is_visible('#tReset'))
    pg.click('#tReset');pg.wait_for_timeout(500);ok('reset hides',not pg.is_visible('#tReset'))
    pg.click('#tEdit');pg.evaluate("__go(0)");pg.wait_for_timeout(700)
    # 9 box select adds states in land mode
    m=pg.evaluate("(()=>{const r=document.querySelector('#map').getBoundingClientRect();return [r.left,r.top,r.width,r.height]})()")
    pg.mouse.move(m[0]+m[2]*.55,m[1]+m[3]*.35);pg.mouse.down();pg.mouse.move(m[0]+m[2]*.9,m[1]+m[3]*.6,steps=8);pg.mouse.up();pg.wait_for_timeout(800)
    ok('box select morphs >=2',len(st(pg)['mor'])>=2)
    # 10 resize across breakpoint with sheet open: body padding cleared on desktop
    pg.set_viewport_size({'width':390,'height':844});pg.wait_for_timeout(300)
    pad_m=pg.evaluate("document.body.style.paddingBottom");pg.set_viewport_size({'width':1100,'height':900});pg.wait_for_timeout(300)
    pad_d=pg.evaluate("document.body.style.paddingBottom");ok('phone pads for sheet / desktop clears',pad_m!='' and pad_d=='')
    # 11 no horizontal overflow at phone
    pg.set_viewport_size({'width':360,'height':740});pg.wait_for_timeout(300)
    ok('no h-scroll at 360',pg.evaluate("document.documentElement.scrollWidth<=innerWidth"))
    print('errors',errs);b.close()

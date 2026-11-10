"""Generates the New Zealand briefing (intro) markup: hemicycle, table, candidate cards. Imported by nz_patch.py."""
import math
# parties in chamber order (left->right), colours light/dark
P=[('Te Pāti Māori','tpm',5,'#8e3a8a','#a4519a','Māori self-determination / social justice','0.57%'),
('Greens','gr',16,'#098137','#2fb060','Environmental / progressive left','13.30%'),
('Labour','lab',36,'#DE2C34','#f2635c','Centre-left / social democratic','29.36%'),
('Opportunity','opp',7,'#00A3A1','#2cc4c0','Centrist / reform-oriented','5.96%'),
('National','nat',42,'#00529F','#3b8fe0','Centre-right','29.21%'),
('NZ First','nzf',12,'#5b6770','#9aa5ae','Nationalist / populist','9.78%'),
('ACT','act',13,'#FDE401','#FDE401','Libertarian / market-oriented right','10.92%')]
assert sum(p[2] for p in P)==131
assert sum(p[2] for p in P if p[1] in ('nat','act','nzf'))==67   # governing bloc shown in the bar
# hemicycle seat positions
N=131; rows=6; r0,r1=0.42,1.0
rad=[r0+(r1-r0)*i/(rows-1) for i in range(rows)]
tot=sum(rad); counts=[round(N*r/tot) for r in rad]; counts[-1]+=N-sum(counts)
seats=[]
for r,c in zip(rad,counts):
    for k in range(c):
        a=math.pi*(1-k/(c-1)) if c>1 else math.pi/2
        seats.append((a,r))
seats.sort(key=lambda s:(-s[0],s[1]))
W,H=360,200; cx,cy=W/2,H-14; R=W/2-10
dots=[]
cum=[];s=0
for p in P: s+=p[2]; cum.append(s)
for n,(a,r) in enumerate(seats):
    pi=next(j for j,c in enumerate(cum) if n<c)
    x=cx+R*r*math.cos(a); y=cy-R*r*math.sin(a)
    dots.append(f'<circle class="s {P[pi][1]}" cx="{x:.1f}" cy="{y:.1f}" r="3.15" data-p="{pi}"/>')
# majority marker: seat 66 position (angle of seat index 65)
a66=seats[65][0]
mx1=cx+R*0.34*math.cos(a66); my1=cy-R*0.34*math.sin(a66)
mx2=cx+R*1.08*math.cos(a66); my2=cy-R*1.08*math.sin(a66)
hemi=f'<svg id="hemi" viewBox="0 0 {W} {H}" role="img" aria-label="Parliament of 131 seats by party">'+''.join(dots)+f'<line class="maj" x1="{mx1:.1f}" y1="{my1:.1f}" x2="{mx2:.1f}" y2="{my2:.1f}"/></svg>'
SL=['luxon','hipkins','swarbrick','seymour','peters','waititi','wong']
def img(i): return 'img/%s.jpg'%SL[i]
CARDS=[
(0,'Christopher Luxon','National','nat','Botany, Auckland','42 seats · 29.21% party vote','Business investment, economic growth, fiscal restraint, crime policy, school performance and government delivery.','First won Botany in 2020, became National leader in 2021 and prime minister after the 2023 election. Provisionally retains Botany.','Leads the largest party in the outgoing National–ACT–NZ First coalition. This is his first election defending a government he leads.'),
(1,'Chris Hipkins','Labour','lab','Remutaka, Wellington region','36 seats · 29.36% party vote','Public healthcare, cost of living, workers’ rights, education and public services; proposes targeted capital gains taxation.','First elected in Remutaka in 2008. Prime minister in 2023 after Jacinda Ardern resigned; Labour lost that year’s election. Provisionally retains Remutaka.','A former prime minister seeking a return to government after one term in opposition.'),
(2,'Chlöe Swarbrick','Greens','gr','Auckland Central','16 seats · 13.30% party vote','Climate policy, housing affordability, more progressive taxation, public transport, social equality and stronger public services.','Ran for Auckland mayor in 2016 and entered Parliament as a list MP in 2017. Won Auckland Central in 2020 and 2023 and provisionally holds it again.','A Green with a durable local electorate base, one of the party’s two provisional electorate MPs.'),
(3,'David Seymour','ACT','act','Epsom, Auckland','13 seats · 10.92% party vote','Tax cuts, smaller government, deregulation, individual liberties and revisions to policies concerning the Treaty of Waitangi.','First won Epsom in 2014 and retained it in 2017, 2020 and 2023. Provisionally retains it. ACT joined the National-led government in 2023.','ACT wins most of its representation through the nationwide party vote rather than local electorates.'),
(4,'Winston Peters','NZ First','nzf','Party list (no electorate)','12 seats · 9.78% party vote','Economic nationalism, limits on immigration, support for regional industry, older voters and selective state intervention.','First elected to Parliament for National in 1978 and founded NZ First in 1993. Has served in coalitions with both major parties. NZ First returned in 2023 after missing out in 2020.','A veteran coalition negotiator whose party may work with different major parties depending on the terms.'),
(5,'Rawiri Waititi','Te Pāti Māori','tpm','Waiariki (Māori electorate)','5 seats · 0.57% party vote','Māori sovereignty, Treaty-based rights, housing, healthcare, Indigenous institutions, language and economic redistribution.','Won Waiariki from Labour in 2020 and retained it in 2023. Provisionally retains it in 2026.','The party’s five seats come from Māori electorates, despite its very small nationwide party vote.'),
(6,'Qiulae Wong','Opportunity','opp','Party list (no electorate)','7 seats · 5.96% party vote','Land-value taxation, a citizen’s income, housing affordability and changes to how taxation, land and public services are structured.','Became leader in 2025 with no prior parliamentary experience. The party’s predecessor won no seats in 2023; its preliminary tally crosses the 5% threshold.','A first-time entrant who could matter for government formation if final results shift the coalition arithmetic.'),
]
cards=''.join(f'''<article class="card {c[3]}" id="c{n}" aria-label="{c[1]}"><div class="ph"><img src="{img(c[0])}" alt="Illustration of {c[1]}" loading="lazy"></div><div class="cb"><span class="pty"><i></i>{c[2]}</span>{"<span class=\"pm\">Incumbent prime minister</span>" if c[1]=="Christopher Luxon" else ""}<h3>{c[1]}</h3><p class="seat">{c[4]}</p><p class="num">{c[5]}</p><dl><dt>Platform</dt><dd>{c[6]}</dd><dt>History</dt><dd>{c[7]}</dd><dt>Why they matter</dt><dd>{c[8]}</dd></dl></div></article>''' for n,c in enumerate(CARDS))
tbl=''.join(f'<tr class="{p[1]}"><td><i></i>{p[0]}</td><td class="pol">{p[5]}</td><td class="n">{p[6]}</td><td class="n">{p[2]}</td></tr>' for p in sorted(P,key=lambda p:-p[2]))
leg=''.join(f'<button type="button" class="lg {p[1]}"><i></i>{p[0]} <b>{p[2]}</b></button>' for p in P)

def render():
    """Return (style, markup) for the shadow root; the page CSS defines --ip-* party colours."""
    here = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
    body = open(here + '/nz_intro_body.html', encoding='utf-8').read()
    for k, v in {'{{HEMI}}': hemi, '{{TBL}}': tbl, '{{CARDS}}': cards, '{{LEG}}': leg}.items(): body = body.replace(k, v)
    return open(here + '/nz_intro.css', encoding='utf-8').read(), body
def party_vars():
    L = ''.join('--ip-%s:%s;' % (p[1], p[3]) for p in P); D = ''.join('--ip-%s:%s;' % (p[1], p[4]) for p in P)
    return ':root{%s}\n@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){%s}}\n:root[data-theme="dark"]{%s}' % (L, D, D)

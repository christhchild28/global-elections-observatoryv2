import re,sys
VOTE='''<h3>How the voting system works</h3>
<ol class="steps2"><li><b>Two votes.</b> Each voter casts an electorate vote for a local MP and a party vote for a party.</li><li><b>The party vote sets the shares.</b> Seats in Parliament are shared out in proportion to party votes, so 29% of the party vote means roughly 29% of the seats.</li><li><b>The 5% rule.</b> A party needs 5% of the party vote or one electorate seat to take list seats. That is how Te Pāti Māori is in Parliament on 0.57%.</li><li><b>Overhang.</b> A party that wins more electorate seats than its share allows keeps them all, so Parliament grows past 120. That is why it is projected at 131.</li><li><b>Māori electorates.</b> There are seven, and voters on the Māori roll choose these instead of general electorates.</li><li><b>Forming a government.</b> A government needs the confidence of a majority of Parliament, and in a 131-seat house that is 66. No single party is near it, so coalition talks decide who governs.</li></ol>
'''
OTHER='''<h3>If it had gone the other way</h3>
<p class="other">On the preliminary count the governing bloc (National, ACT and NZ First) holds 67 seats against 64 for Labour, the Greens, Te Pāti Māori and Opportunity. Had a few seats moved, a Labour-led government would have been the likely outcome.</p>
<ul class="oth"><li><b>At home.</b> Labour dropped farm emissions pricing from its campaign, the Greens still want it, and the Treaty of Waitangi would have been handled very differently from the coalition’s approach. A left bloc would have needed to bargain over all of it.</li><li><b>Abroad.</b> Labour opposes AUKUS and the Greens want out of Five Eyes. A left-led government would have had to settle those splits in coalition talks, with Australia, the US and the UK watching.</li></ul>
'''
CSS='''
/* v2 sections */
.steps2{list-style:none;counter-reset:s;margin:10px 0 18px;padding:0;display:grid;gap:8px;text-align:left;hyphens:none}
.steps2 li{counter-increment:s;position:relative;border:1px solid var(--hair);border-radius:12px;padding:12px 14px 12px 48px;background:var(--card);font-size:15px;line-height:1.5}
.steps2 li::before{content:counter(s);position:absolute;left:14px;top:10px;font:800 20px var(--f-body);color:var(--ink-3)}
.oth{list-style:none;margin:10px 0 18px;padding:0;display:grid;gap:8px;text-align:left;hyphens:none}
.oth li{border:1px solid var(--hair);border-left:4px solid var(--ink-3);border-radius:12px;padding:12px 14px;background:var(--card);font-size:15px;line-height:1.5}
'''
def add(s,css=False):
    if 'steps2' in s and not css: return s
    if css: return s if '/* v2 sections */' in s else s+CSS
    s=s.replace('<h3>Beyond New Zealand</h3>',VOTE+'<h3>Beyond New Zealand</h3>',1)
    s=s.replace('<ul class="three">',OTHER+'<ul class="three">',1)
    return s
for f in sys.argv[1:]:
    t=open(f,encoding='utf-8').read(); n=add(t, f.endswith('.css'))
    if f.endswith('.html') and 'intro-tpl' in n and '/* v2 sections */' not in n:
        n=n.replace('</style>',CSS+'</style>',1)  # first style = intro-tpl style
    open(f,'w',encoding='utf-8').write(n); print(f,len(t),'->',len(n))

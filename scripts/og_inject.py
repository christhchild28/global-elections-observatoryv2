"""Insert social-preview (Open Graph / Twitter) tags after the <title>. Idempotent.
usage: python3 og_inject.py <html file> <key>   (key: landing|usa|brazil|bulgaria|new-zealand|new-zealand-maori|trinidad-tobago)"""
import re,sys
BASE='https://christhchild28.github.io/election-land-vs-people/'
M={'landing':('Land vs people','Election cartograms that morph from real land area to share of voters: US, Brazil, Bulgaria, New Zealand, Trinidad and Tobago.',''),
 'usa':('United States: land vs people','2024 presidential election. Tap a state to resize it from land area to electoral votes.','usa/'),
 'brazil':('Brazil: land vs people','2026 presidential runoff. Tap a state to resize it from land area to registered voters.','brazil/'),
 'bulgaria':('Bulgaria: land vs people','April 2026 parliamentary election. Tap a province to resize it from land area to registered voters.','bulgaria/'),
 'new-zealand':('New Zealand: land vs people','2026 general election (preliminary). Tap an electorate to resize it from land area to population.','new-zealand/'),
 'new-zealand-maori':('New Zealand Māori electorates: land vs people','2026 election (preliminary). Tap one of the 7 Māori electorates to resize it from land area to population.','new-zealand/maori/'),
 'trinidad-tobago':('Trinidad and Tobago: land vs people','2025 general election. Tap a seat to resize it from land area to population.','trinidad-tobago/')}
f,k=sys.argv[1],sys.argv[2];t,d,p=M[k]
h=open(f,encoding='utf-8').read()
h=re.sub(r'<!--og-->.*?<!--/og-->\s*','',h,flags=re.S)
img=BASE+'assets/og/'+k+'.png'
blk=f'''<!--og-->
<meta name="description" content="{d}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Land vs people">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:url" content="{BASE+p}"><meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{t}: real map beside the same map resized by voters">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{img}">
<!--/og-->
'''
h=re.sub(r'<meta name="description"[^>]*>\s*','',h)
m=re.search(r'</title>\s*',h);assert m
h=h[:m.end()]+blk+h[m.end():]
open(f,'w',encoding='utf-8').write(h)

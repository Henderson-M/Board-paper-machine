import re,os
S='summaries/'; T='tmp_scan/modeltest/'
PACKS={
 'RHQ 8 Sep (Sheffield, 23 papers)':{
   'sonnet':T+'RHQ_2026-09-08__sonnet_ORIGINAL.md','opus':T+'RHQ_2026-09-08__opus.md','fable':T+'RHQ_2026-09-08__fable.md',
   'checks':[
     ('NOF 26th->86th, segment 3', r'26(th)?\s*(to|-)\s*86|86th'),
     ('NHSE "not sufficiently assured"', r'not sufficiently assured'),
     ('external well-led review commissioned', r'well[- ]led (review|reviewer)'),
     ('GBP15.1m/15.2m efficiency adverse', r'15\.1[0-9]?m|15\.2m|15\.17'),
     ('Intergrowth chart non-compliance', r'intergrowth'),
     ('coroner narrative verdict / triage', r'narrative (verdict|conclusion)'),
     ('PFD WRONGLY attributed to trust', r'trust has issued a Prevention|trust issued a Prevention'),
     ('notes Paper K unavailable', r'paper k|MOSS'),
   ]},
 'RWX 8 Sep (Berkshire, 328pp)':{
   'sonnet':S+'RWX_2026-09-08.md','opus':T+'RWX_2026-09-08__opus.md','fable':T+'RWX_2026-09-08__fable.md',
   'checks':[
     ('CQC well-led inspection live', r'well[- ]led'),
     ('bribery charges item', r'briber'),
     ('hearing SCHEDULED (correct)', r'scheduled for early August'),
     ('hearing HELD (WRONG)', r'hearing held|held in early August'),
     ('names TIAA contractor', r'TIAA'),
     ('acute bed risk -> severe', r'severe'),
     ('flags contempt risk', r'contempt|active proceedings'),
     ('new chair Frances West', r'Frances West'),
   ]},
 'RX1 10 Sep (Nottingham, 451pp)':{
   'sonnet':S+'RX1_2026-09-10.md','opus':T+'RX1_2026-09-10__opus.md','fable':T+'RX1_2026-09-10__fable.md',
   'checks':[
     ('section 30 referral (MAJOR)', r'section 30'),
     ('corporate manslaughter suspect', r'corporate manslaughter'),
     ('Ockenden review', r'Ockenden'),
     ('Ockenden 2,500 cases figure', r'2,500'),
     ('GBP80.6m 25/26 deficit', r'80\.6'),
     ('GBP16m ask / supplier delays', r'suppli'),
     ('hip fracture mortality outlier', r'hip[- ]fracture|hip fracture'),
     ('1,176 WTE reduction', r'1,176'),
     ('ICO enforcement notice', r'\bICO\b'),
   ]},
}
MODELS=['sonnet','opus','fable']
tot={m:[0,0] for m in MODELS}   # [hits, misses] on GOOD checks
bad={m:0 for m in MODELS}       # errors
for pack,cfg in PACKS.items():
    print('\n'+'='*78); print(pack); print('='*78)
    texts={m:(open(cfg[m],encoding='utf-8').read() if os.path.exists(cfg[m]) else '') for m in MODELS}
    print('%-38s %-8s %-8s %-8s'%('','SONNET','OPUS','FABLE'))
    for label,pat in cfg['checks']:
        is_err='WRONG' in label
        row=[]
        for m in MODELS:
            hit=bool(re.search(pat,texts[m],re.I))
            row.append(('ERROR' if hit else 'ok') if is_err else ('yes' if hit else 'MISS'))
            if is_err:
                if hit: bad[m]+=1
            else:
                tot[m][0 if hit else 1]+=1
        print('%-38s %-8s %-8s %-8s'%(label,row[0],row[1],row[2]))
    print('%-38s %-8s %-8s %-8s'%('--- leads/watch/foi ---',*[
        '%d/%d/%d'%(len(re.findall(r'^\[LEAD\]',texts[m],re.M)),
                    len(re.findall(r'^\[WORTH WATCHING\]',texts[m],re.M)),
                    len(re.findall(r'^\[FOI\]',texts[m],re.M))) for m in MODELS]))
    print('%-38s %-8s %-8s %-8s'%('--- words ---',*['%d'%len(texts[m].split()) for m in MODELS]))
    print('%-38s %-8s %-8s %-8s'%('--- em dashes (house style) ---',*['%d'%texts[m].count(chr(8212)) for m in MODELS]))
print('\n'+'='*78); print('TOTALS across all three packs'); print('='*78)
print('%-24s %-10s %-10s %-10s'%('','SONNET','OPUS','FABLE'))
print('%-24s %-10s %-10s %-10s'%('substantive items hit',*['%d/%d'%(tot[m][0],tot[m][0]+tot[m][1]) for m in MODELS]))
print('%-24s %-10s %-10s %-10s'%('factual errors',*[str(bad[m]) for m in MODELS]))

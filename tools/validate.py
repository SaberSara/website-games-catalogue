#!/usr/bin/env python3
"""Validate source JSON without any third-party Python packages."""
from pathlib import Path
import json
import re
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]

def https_url(value):
    if not isinstance(value,str) or len(value)>2048 or any(ord(c)<32 for c in value):return False
    try:
        u=urlsplit(value)
        return u.scheme=='https' and bool(u.hostname) and not u.username and not u.password
    except ValueError:return False

def validate():
    c=json.loads((ROOT/'data/curriculum.json').read_text(encoding='utf-8'))
    d=json.loads((ROOT/'data/games.json').read_text(encoding='utf-8'))
    assert c['schemaVersion']==1 and d['schemaVersion']==1,'Unknown schema version'
    subjects={s['id'] for s in c['subjects']};topics={t['id']:t for t in c['topics']}
    assert len(topics)==len(c['topics']),'Duplicate curriculum topic IDs'
    assert set(subjects)=={'ela','math','science','hss','arts','health','pe','cs'},'Unexpected subjects'
    for sid,source in c['sourceRegister'].items():assert https_url(source['url']),f'Invalid source URL: {sid}'
    grade_ids={g['id'] for g in c['grades']}
    assert grade_ids=={'K',*[str(i) for i in range(1,13)]},'Incomplete K–12 grade set'
    for t in c['topics']:
        assert t['grade'] in grade_ids and t['subject'] in subjects,'Invalid topic grade or subject'
        assert set(t['sourceIds'])<=set(c['sourceRegister']),'Invalid topic sources'
    ids=set()
    assert len(d['games'])<=2000,'Resource count exceeds limit'
    for g in d['games']:
        gid=g['id'];assert isinstance(gid,str) and len(gid)<=150 and re.fullmatch(r'[a-z0-9-]+',gid) and gid not in ids,f'Invalid or duplicate resource ID: {gid}'
        ids.add(gid)
        for key,max_len in [('title',150),('publisher',150),('kind',100),('priceLabel',180)]:assert isinstance(g.get(key),str) and g[key].strip() and len(g[key])<=max_len,f'{gid}: invalid {key}'
        for key,max_len in [('description',500),('access',500)]:assert isinstance(g.get(key),str) and len(g[key])<=max_len,f'{gid}: invalid {key}'
        assert https_url(g['url']),f'{gid}: invalid activity URL'
        assert g['platform'] in ['browser','app'],f'{gid}: invalid platform'
        assert g['grades'] and set(g['grades'])<={x['id'] for x in c['grades']},f'{gid}: unsupported grade'
        assert g['subjects'] and set(g['subjects'])<=subjects,f'{gid}: unsupported subject'
        for tid in g['topicIds']:
            assert tid in topics,f'{gid}: unknown topic {tid}'
            assert topics[tid]['grade'] in g['grades'] and topics[tid]['subject'] in g['subjects'],f'{gid}: topic mismatch {tid}'
        assert set(g['sourceIds'])<=set(c['sourceRegister']),f'{gid}: unknown source reference'
        assert set(g.get('devices',[]))<={'browser','ios','android','amazon','chromeos','desktop','mobile','unknown'},f'{gid}: unsupported device'
        review=g['review'];assert review['status'] in ['publisher_claim_reviewed','teacher_verified','needs_review'],f'{gid}: unknown review status'
        assert isinstance(review['runtimeTested'],bool),f'{gid}: missing playtest status'
        if review.get('adEvidenceUrl'):assert https_url(review['adEvidenceUrl']),f'{gid}: invalid evidence URL'
        if review['status']=='publisher_claim_reviewed':assert review.get('adEvidenceSourceId') in c['sourceRegister'] or https_url(review.get('adEvidenceUrl')),f'{gid}: no source for published claim'
        if review['status']=='teacher_verified':assert g.get('teacherVerified') is True and review.get('advertisingStatus')=='not_independently_checked',f'{gid}: teacher verification must not imply ad clearance'
        if g.get('thumbnailAsset'):
            assert re.fullmatch(r'[a-z0-9-]+\.webp',g['thumbnailAsset']),f'{gid}: invalid thumbnail path'
            assert (ROOT/'assets'/g['thumbnailAsset']).is_file(),f'{gid}: missing thumbnail'
        assert 'ahmadischool' not in g['url'].lower(),f'{gid}: excluded link'
        assert 'ahmadi academy' not in g['title'].lower(),f'{gid}: excluded academy'
    return {'topics':len(topics),'games':len(ids),'publisherClaimRecords':sum(g['review']['status']=='publisher_claim_reviewed' for g in d['games']),'teacherVerifiedRecords':sum(g['review']['status']=='teacher_verified' for g in d['games'])}

if __name__=='__main__':print(json.dumps(validate(),indent=2))

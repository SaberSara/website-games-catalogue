#!/usr/bin/env python3
"""Data coverage smoke test: no external requests, no runtime/gameplay certification."""
from pathlib import Path
import json,collections
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/'data/curriculum.json').read_text())
d=json.loads((ROOT/'data/games.json').read_text())
assert d['seedRevision']==2
approved=[x for x in d['games'] if x['review']['status']=='publisher_claim_reviewed']
pending=[x for x in d['games'] if x['review']['status']=='needs_review']
grades=[g['id'] for g in c['grades']]
assert len(d['games'])==152 and len(approved)==118 and len(pending)==34
assert all(any(gr in x['grades'] for x in approved) for gr in grades)
assert all(x['topicIds'] for x in approved),'Every published record must have a real curricular link'
assert all(x['review']['runtimeTested'] is False for x in d['games']), 'No fabricated hands-on test claims'
assert all((x['review'].get('adEvidenceUrl') or x['review'].get('adEvidenceSourceId')) for x in approved)
assert all(x['platform']=='browser' or x['devices'] for x in d['games'])
assert not any(x['id'].startswith('icivics') and x in approved for x in d['games'])
assert all(x.get('thumbnailAsset','').startswith('subject-') and x['thumbnailAsset'].endswith('.webp') for x in d['games'][28:]),'Use available themed thumbnails'
subject_names={s['id']:s['name'] for s in c['subjects']}
coverage=collections.defaultdict(lambda:collections.Counter())
for x in approved:
 for grade in x['grades']:
  for subject in x['subjects']:coverage[grade][subject]+=1
matched={t for x in approved for t in x['topicIds']}
metrics={'records':len(d['games']),'approved':len(approved),'pending':len(pending),'grades':len(grades),'topicsWithVisibleResource':len(matched),'topicCount':len(c['topics']),
  'perGrade':{gr:{'visible':len([x for x in approved if gr in x['grades']]),'subjectActivityCounts':dict(coverage[gr])} for gr in grades}}
(ROOT/'docs/coverage-test-report.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2))

#!/usr/bin/env python3
"""Data coverage smoke test: no external requests, no runtime/gameplay certification."""
from pathlib import Path
import json,collections
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/'data/curriculum.json').read_text())
d=json.loads((ROOT/'data/games.json').read_text())
assert d['seedRevision']==4
approved=[x for x in d['games'] if x['review']['status']=='publisher_claim_reviewed']
pending=[x for x in d['games'] if x['review']['status']=='needs_review']
teacher=[x for x in d['games'] if x['review']['status']=='teacher_verified']
visible=approved+teacher
grades=[g['id'] for g in c['grades']]
assert len(d['games'])==220 and len(approved)==118 and len(pending)==34 and len(teacher)==68
assert not any(g['id'] in {'hub-41-the-sun','hub-10-nasa-kids-science'} for g in d['games'])
restricted={'phet-waves-intro':{'8','9'},'phet-color-vision':set(map(str,range(8,13))),
'phet-density':set(map(str,range(8,13))),'hub-51-properties-density-phet':set(map(str,range(8,13))),
'phet-states-of-matter-basics':set(map(str,range(8,13))),'phet-natural-selection':set(map(str,range(8,13)))}
for game in d['games']:
 if game['id'] in restricted:
  assert set(game['grades'])<=restricted[game['id']],game['id']
  if game['id']=='phet-waves-intro':assert game['grades']==['8','9']
assert all(any(gr in x['grades'] for x in approved) for gr in grades)
assert all(x['topicIds'] for x in approved),'Every published record must have a real curricular link'
assert all(x['review']['runtimeTested'] is False for x in d['games']), 'No fabricated hands-on test claims'
assert all((x['review'].get('adEvidenceUrl') or x['review'].get('adEvidenceSourceId')) for x in approved)
assert all(x['platform']=='browser' or x['devices'] for x in d['games'])
assert not any(x['id'].startswith('icivics') and x in approved for x in d['games'])
assert all((ROOT/'assets'/x['thumbnailAsset']).is_file() for x in d['games'] if x.get('thumbnailAsset')),'Thumbnail files present'
subject_names={s['id']:s['name'] for s in c['subjects']}
coverage=collections.defaultdict(lambda:collections.Counter())
for x in visible:
 for grade in x['grades']:
  for subject in x['subjects']:coverage[grade][subject]+=1
matched={t for x in visible for t in x['topicIds']}
metrics={'records':len(d['games']),'approved':len(approved),'pending':len(pending),'teacherVerified':len(teacher),'visible':len(visible),'grades':len(grades),'topicsWithVisibleResource':len(matched),'topicCount':len(c['topics']),
  'perGrade':{gr:{'visible':len([x for x in visible if gr in x['grades']]),'subjectActivityCounts':dict(coverage[gr])} for gr in grades}}
(ROOT/'docs/coverage-test-report.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2))

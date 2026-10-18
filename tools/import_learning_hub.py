#!/usr/bin/env python3
"""Recreate curated Wonderwood imports from the user-supplied Learning Hub ZIP.

Run with the original ZIP path and a separate working source checkout:
  python tools/import_learning_hub.py --hub-zip /path/to/aropl-kids-learning-hub-main.zip

No videos or executable game folders are copied. Those destinations point to
existing hosted links. Thumbnails are resized source images from the ZIP.
The explicit classification table is EDITORIAL; source-specified grade tags are
preserved separately. This is not a California standards certification.
"""
import argparse
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit
from bs4 import BeautifulSoup
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
HUB_URL='https://aropl-kids-learning-hub.vercel.app/'
DATE='2026-10-18'
# Grades/subjects are editorial suggestions where the source does not name a grade.
# Fields: subjects separated by +, grades inclusive in expanded range form, topic keywords.
CLASSIFICATIONS={
 0:('ela','9','informational,writing'),
 1:('ela','9','informational,writing'),
 2:('ela+health','9','informational,wellbeing'),
 3:('ela+cs','9','informational,computing'),
 4:('ela+science','9','informational,earth and space'),
 5:('ela+hss','9','informational,economic'),
 6:('math','2-6','multiply,place value,equal groups,operations'),
 7:('ela+science+health','3-6','informational,human impacts,health'),
 8:('ela+hss','4-8','informational,geography,history'),
 9:('science','2-6','space,earth systems,sky'),
 10:('ela+hss','5-9','informational,geography'),
 11:('science+ela','2-6','ecosystems,habitats,informational'),
 12:('ela+hss','6-10','informational,rights,civic'),
 13:('science+ela','4-7','earth systems,land and water,informational'),
 14:('health','7-10','wellbeing,health skills'),
 15:('science+health','7-10','body systems,wellbeing'),
 16:('science+ela','5-8','ecosystems,informational,life cycles'),
 17:('science','3-7','life cycles,ecosystems,plants and habitats'),
 18:('science+ela','5-10','earth systems,earth and space,informational'),
 19:('ela','10-12','informational,writing'),
 20:('health+ela','7-12','health skills,speaking,informational'),
 21:('health+ela','7-12','health skills,speaking,informational'),
 22:('ela+cs','9-12','informational,computing'),
 23:('health+ela','10-12','health skills,informational'),
 24:('cs','7-12','computing'),
 25:('ela+cs','6-12','informational,computing'),
 26:('science','2-5','plants and habitats,life cycles,ecosystems'),
 27:('science','3-7','weather,climate,hazards'),
 28:('science','2-5','weather,climate,earth changes'),
 29:('science','2-5','weather,climate,earth changes'),
 30:('science','3-7','ecosystems,climate,plants and habitats'),
 31:('science','3-7','ecosystems,climate,plants and habitats'),
 32:('science+hss','4-8','earth changes,earth systems,geography'),
 33:('science','2-5','plants and habitats,ecosystems,climate'),
 34:('hss','1-5','traditions,cultures,community histories'),
 35:('science','5-10','energy,human impacts,resources'),
 36:('science','4-8','earth changes,earth processes,hazards'),
 37:('science+hss','7-10','earth processes,hazards,earth and space,geography'),
 38:('science','4-8','space,gravity,earth and space'),
 39:('science','5-9','space,gravity,earth and space'),
 40:('science','1-6','sky,space,gravity,earth systems'),
 41:('science','3-6','traits,life cycles,ecosystems'),
 42:('science','3-7','ecosystems,energy,plants and habitats'),
 43:('science','3-8','ecosystems,energy,plants and habitats'),
 44:('science','7-12','evolution,traits,reproduction,organisms'),
 45:('science','2-8','plants and habitats,life cycles,traits,reproduction'),
 46:('science','5-10','reproduction,life cycles,traits,organisms'),
 47:('science','6-12','cells,organisms'),
 48:('science','6-12','cells,organisms'),
 49:('science','6-12','human impacts,ecosystems,earth systems'),
 50:('science','5-10','matter,materials,atoms'),
 51:('science','5-9','matter,mixtures,atoms,reactions'),
 52:('science','3-9','ecosystems,human impacts,engineering solutions'),
 53:('science','5-10','ecosystems,organisms,evolution'),
 54:('science','3-8','ecosystems,life cycles,organisms'),
 55:('science','4-8','space,gravity,earth and space'), # repeated original link; deduplicated
 56:('science','1-5','sound,waves,information'),
 57:('science','4-9','waves,information'),
 58:('science','6-10','matter,atoms,reactions'),
 59:('science','6-10','matter,atoms,reactions'),
 60:('science','3-9','magnets,forces,energy,engineering'),
 61:('science','5','engineering solutions'), # explicitly Science 5
 62:('science','3-8','weather,climate,hazards'),
 63:('science+health','2-5','weather,climate,health skills'),
 64:('science','5-10','engineering solutions,forces,energy,technology'),
 65:('science','9','cells,organisms'), # explicitly Grade 9
 66:('science','6-10','body systems,cells and organisms'),
 67:('science','8-12','cells,organisms,ecosystems'),
 68:('science','6-9','cells,organisms'),
 69:('science','6-10','cells,organisms'),
 70:('science','8-12','matter,atoms,reactions'),
}
assert set(CLASSIFICATIONS)==set(range(71))

def grade_expand(s):
    if '-' in s:
        a,b=map(int,s.split('-'))
        return [str(i) for i in range(a,b+1)]
    return [s]

def slug(s):
    s=s.lower().replace('’','').replace('–','-')
    s=re.sub('[^a-z0-9]+','-',s).strip('-')
    return s[:60].strip('-')

def relevant(grades,subjects,key,topics):
    patterns=[x.strip().lower() for x in key.split(',') if x.strip()]
    out=[]
    for g in grades:
      relevant_for_grade=[t for t in topics if t['grade']==g and t['subject'] in subjects and any(p in t['title'].lower() for p in patterns)]
      for t in relevant_for_grade[:3]:
       if t['id'] not in out:out.append(t['id'])
    return out

def main(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
      prefix=next(p for p in archive.namelist() if p.endswith('/index.html') and p.count('/')==1).removesuffix('index.html')
      soup=BeautifulSoup(archive.read(prefix+'index.html').decode('utf-8'),'html.parser')
      cards=soup.select('a.card')
      if len(cards)!=71:raise ValueError(f'Source changed unexpectedly: {len(cards)} cards instead of 71')
      games_path=ROOT/'data/games.json'
      source=json.loads(games_path.read_text(encoding='utf-8'))
      curriculum=json.loads((ROOT/'data/curriculum.json').read_text(encoding='utf-8'))
      source['games']=[g for g in source['games'] if not g['id'].startswith('hub-')]
      original_urls={g['url'] for g in source['games']}
      seen={}
      manifest=[]; imported=[]; duplicate=0; existing_overlap=0; thumbnails=[]
      for order,el in enumerate(cards):
        title=el.select_one('h3').get_text(' ',strip=True)
        sect=el.find_parent('section')
        section={'tests-section':'Assessments','math-section':'Math','english-section':'English','science-section':'Science'}[sect['id']]
        raw=el['href']
        # Local project games on the source host, not copied to Wonderwood.
        if raw.startswith('video.html?'):
            params=parse_qs(urlsplit(raw).query)
            url=params.get('creditLink',[''])[0]
            if not url.startswith('https://www.youtube.com/watch?'):
                raise ValueError('Missing external original-video source for '+title)
            media='Video'
        else:
            url=urljoin(HUB_URL,raw)
            media='Interactive simulation' if '/solar-system-explorer' in raw or 'phet.colorado.edu' in url else 'Mini-game' if '/math-smash' in raw else 'Reading resource'
            if any(x in url for x in ['pdf','ssph-journal','pewresearch','ipcc','oecd','scholar','oup','pmc','hbs.edu','leadx','eric.ed.gov']):media='Research resource'
        # Curatorial removals: keep source positions for archival provenance,
        # but never reimport links withdrawn by the catalogue owner.
        if title.strip().casefold() in {'the sun','nasa kids science'} or url in {
            'https://science.nasa.gov/kids/',
            'https://education.nationalgeographic.org/resource/sun-101/'
        }:
            manifest.append({'order':order+1,'sourceSection':section,'title':title,'url':url,
                             'omittedFromCatalogue':'Withdrawn by site owner 2026-10-18'})
            continue
        # These are original source cards, not authoritative publisher reviews.
        if 'ahmadi' in (title+' '+url).lower():
            raise ValueError('Excluded academy link appeared in import cards')
        subjects_s,gr_s,pattern=CLASSIFICATIONS[order]
        subjects=subjects_s.split('+');grades=grade_expand(gr_s)
        tag=el.select_one('.tag');lesson=tag.get_text(' ',strip=True) if tag else ''
        desc=el.select_one('p').get_text(' ',strip=True) if el.select_one('p') else ''
        thumbnail=el.select_one('img')['src']
        if url in seen:
            seen[url]['sourcePositions'].append(order+1)
            duplicate+=1
            continue
        if url in original_urls:
            existing_overlap+=1
            # Allow a teacher-verification annotation on the already-present matching link, no duplicate card.
            original=next(g for g in source['games'] if g['url']==url)
            original.setdefault('hubSourcePositions',[]).append(order+1)
            original['teacherVerified']=True
            original['teacherVerifiedSource']='User-provided teacher-verified Learning Hub, 2026-10-18'
            manifest.append({'order':order+1,'sourceSection':section,'title':title,'url':url,'thumbnail':thumbnail,'matchingExistingGame':original['id']})
            continue
        rid='hub-'+str(order+1).zfill(2)+'-'+slug(title)
        # Include attached source thumbnails; do not trust the live hub's availability.
        key=prefix+thumbnail
        content=archive.read(key)
        try:
          with Image.open(io.BytesIO(content)) as frame:
            frame=ImageOps.exif_transpose(frame).convert('RGB')
            frame=ImageOps.pad(frame,(400,220),method=Image.Resampling.LANCZOS,color='#f4f7fa',centering=(0.5,0.5))
            filename=rid+'.webp'
            path=ROOT/'assets'/filename
            frame.save(path,format='WEBP',quality=74,method=6)
        except Exception as e:raise ValueError(f'Could not decode source thumbnail {thumbnail}: {e}')
        thumbnails.append(str(path.relative_to(ROOT)))
        explicit_grade= (['9'] if re.search(r'Grade\s*9\b',lesson) else ['5'] if title.startswith('Science 5 |') else [])
        grade_basis='Source explicitly names '+('Grade 9' if explicit_grade==['9'] else 'Science 5') if explicit_grade else 'Editorial age/topic suggestion; exact grade not stated on source card'
        notes=f'Teacher verification reported by the person supplying the Learning Hub. Source section: {section}; source card #{order+1}.'
        if lesson:notes+=f' Original lesson label: {lesson}.'
        if 'book code' in desc.lower():
          desc='Biology learning resources (classroom access may be required).'
          notes+=' Access code present in supplied source; not republished in this child-facing catalogue.'
        notes+=' Ad inventory, paywalls, and live destination were not independently checked.'
        publisher=urlsplit(url).hostname.removeprefix('www.') or 'Learning Hub'
        platform='browser'
        g={
            'id':rid,'title':title,'publisher':publisher,'url':url,'subjects':subjects,'grades':grades,
            'topicIds':relevant(grades,subjects,pattern,curriculum['topics']),
            'kind':media,'platform':platform,'access': 'Browser · external video' if media=='Video' else 'Browser · external source',
            'priceLabel':'Check access', 'description':desc[:180],
            'art': {'math':'math','ela':'reading','hss':'world','science':'science','health':'health','cs':'coding'}[subjects[0]],
            'thumbnailAsset':filename,'sourceIds':[],
            'learningSuggestion':'Explore together, then discuss what you learned.',
            'alignmentStatus':'Editorial placement based on source card; California standards mastery is not independently verified',
            'review':{
                'status':'teacher_verified','reviewedOn':DATE,'method':'User attestation that source links were verified by teachers; no independent external visit',
                'runtimeTested':False,'advertisingStatus':'not_independently_checked','evidenceScope':'Teacher verification of supplied selection; no publisher no-ad claim implied',
                'notes':notes,
            },
            'teacherVerified':True, 'teacherVerifiedSource':'Teacher-verified Learning Hub, supplied by project owner',
            'hubSource':HUB_URL,'hubSection':section,'hubOrder':order+1,'hubLesson':lesson,
            'gradeEvidence':grade_basis,
            'sourcePositions':[order+1],
            'featured':False,'devices':['browser']
        }
        # Preserve the exact source credit, rather than republishing local video files.
        if media=='Video':g['videoCreditURL']=url
        seen[url]=g;imported.append(g)
        manifest.append({'order':order+1,'sourceSection':section,'title':title,'originalUrl':raw,'url':url,
                         'sourceThumbnail':thumbnail,'savedThumbnail':filename,'originalLesson':lesson,
                         'suggestedGrades':grades,'suggestedSubjects':subjects,'gradeEvidence':grade_basis})
      # Explicit provenance/order for the duplicate source card.
      for m in manifest:
        if m['title']=='Solar System Explorer':m['sourcePositions']=[39,56]
      source['games']+=imported
      source['seedRevision']=4
      source['reviewedOn']=DATE
      games_path.write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
      (ROOT/'docs/HUB-IMPORT-MANIFEST.json').write_text(json.dumps({
          'importedOn':DATE,'source':'User-supplied ZIP of AROPL Kids Learning Hub',
          'hubURL':HUB_URL, 'sourceCardCount':len(cards),'uniqueImported':len(imported),
          'duplicateSourceCards':duplicate,'alreadyInWonderwood':existing_overlap,
          'omitted':'The Ahmadi Academy link, logo, page branding, two stored MP4 files, original game code. Videos use creator YouTube links; two hosted games use their hub routes.',
          'records':manifest},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
      print(json.dumps({'originalCards':len(cards),'imported':len(imported),'repeatedSourceCards':duplicate,
                        'existingCatalogLinks':existing_overlap,'thumbnailCount':len(thumbnails),
                        'newCatalogueTotal':len(source['games']),
                        'teacherVisibleCountsBySubject':dict(Counter(s for g in imported for s in g['subjects'])),
                        'newSourceSizeKB':round(games_path.stat().st_size/1024)},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--hub-zip',required=True,type=Path)
    args=parser.parse_args()
    main(args.hub_zip)

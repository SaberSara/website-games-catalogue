#!/usr/bin/env python3
"""Offline checks for the ZIP-derived teacher selection import and thumbnails."""
from pathlib import Path
from collections import Counter
import json, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
G=json.loads((ROOT/'data/games.json').read_text())
H=json.loads((ROOT/'docs/HUB-IMPORT-MANIFEST.json').read_text())
items=[x for x in G['games'] if x['id'].startswith('hub-')]
checks=[]
def ck(condition,label):
    if not condition:raise AssertionError(label)
    checks.append(label)
ck(len(G['games'])==222,'Original catalogue retained with 70 additions')
ck(len(items)==70,'70 unique Learning Hub activity records')
ck(H['sourceCardCount']==71 and H['duplicateSourceCards']==1,'71 source cards; one repeated entry collapsed')
ck([g['hubOrder'] for g in items]==sorted(g['hubOrder'] for g in items),'Import preserves source ordering')
ck(all(g['review']['status']=='teacher_verified' and g['teacherVerified'] for g in items),'Teacher verified label is recorded')
ck(all(g['review']['advertisingStatus']=='not_independently_checked' for g in items),'No false advertising claims')
ck(all(g['review']['runtimeTested'] is False for g in items),'No false live testing claims')
ck(all((ROOT/'assets'/g['thumbnailAsset']).is_file() for g in items),'Local ZIP thumbnails present')
ck(len({g['thumbnailAsset'] for g in items})==70,'One distinct thumbnail per imported record')
ck(all(g['url'].startswith('https://') for g in items),'All imported destinations HTTPS')
ck(not any('ahmadischool' in x['url'].lower() or 'ahmadi academy' in x['title'].lower() for x in G['games']), 'Academy link excluded')
ck(len([g for g in items if g['kind']=='Video'])==2,'Two video links imported')
ck(all('youtube.com/watch' in g['url'] for g in items if g['kind']=='Video'),'Videos use original credited YouTube links')
ck(not any('/videos/' in g['url'] for g in items),'No uploaded MP4 dependencies')
ck(sum(g['id'].endswith('solar-system-explorer') for g in items)==1,'Repeated solar system item deduplicated')
ck(items[0]['title']=='School Uniforms & Research','Source begins with assessments')
ck(items[-1]['title']=='Molecular Geometry (PhET)','Source final card maintained')
ck(all(g['topicIds'] for g in items),'Every imported activity has a matching editorial topic')
ck(all(g['priceLabel']=='Check access' for g in items),'No unverified free-price claims')
ck(all(g['gradeEvidence'] for g in items),'Grade provenance recorded')
ck(not list(ROOT.rglob('DNA-replication-3D.mp4')) and not list(ROOT.rglob('electromagnets.mp4')),'No source MP4 files copied')
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    for width in [390,1280]:
        page=browser.new_page(viewport={'width':width,'height':900})
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        # Standalone HTML embeds thumbnails. File URLs are blocked by this test environment.
        page.set_content((ROOT/'wonderwood-play.html').read_text(encoding='utf-8'),wait_until='load',timeout=30000)
        ck(page.evaluate('validData(original)'),f'{width}px browser validates updated schema')
        ck(page.evaluate('approved().length')==188,f'{width}px includes teacher reviewed items')
        page.evaluate("state.grade='9'; state.subject='ela'; state.showAll=true; renderGames()")
        ids=page.eval_on_selector_all('#games [data-game]','els=>els.map(e=>e.dataset.game)')
        ck('hub-01-school-uniforms-research' in ids,f'{width}px teacher Grade 9 ELA appears')
        img=page.locator('[data-game="hub-01-school-uniforms-research"] .source-thumbnail').first
        ck(img.evaluate('(e)=>e.complete && e.naturalWidth>0'),f'{width}px imported original thumbnail loads')
        page.locator('[data-open="hub-01-school-uniforms-research"]').click()
        ck('Teacher verified' in page.locator('.popup-review').inner_text(),f'{width}px teacher label appears')
        ck('Ads not independently checked' in page.locator('.popup-review').inner_text(),f'{width}px ad disclosure appears')
        ck(page.locator('.popup-art .source-thumbnail').count()==1,f'{width}px thumbnail repeats in popup')
        page.screenshot(path=str(ROOT/f'previews/hub-import-{width}.png'),full_page=width==1280)
        ck(not errors,f'{width}px no script errors')
        page.close()
    browser.close()
report={'date':'2026-10-18','passed':len(checks),'scope':'ZIP/source data, local browser HTML and local thumbnails. No external game links or YouTube were fetched.', 'checks':checks}
(ROOT/'docs/HUB-IMPORT-TEST-REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'failed':0,'screenshots':['previews/hub-import-390.png','previews/hub-import-1280.png']},indent=2))

#!/usr/bin/env python3
"""V3 interface tests. Requires optional Playwright + Chromium.
Uses set_content: real navigation is blocked by browser policy in the build environment.
Does not test external gameplay, downloads, hosted/file-origin persistence or a deployment.
"""
from pathlib import Path
import json,os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];HTML=(R/'wonderwood-play.html').read_text();O=R/'previews'
checks=[];errors=[];requests=[]
def ck(ok,name):
 if not ok:raise AssertionError(name)
 checks.append({'check':name,'result':'passed'})
def click(p,s):p.locator(s).first.click();p.wait_for_timeout(60)
def home(p):p.evaluate("state.grade='K';resetFilters();state.showAll=false;switchView('explore',false)")
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 p=b.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1);p.set_default_timeout(4000)
 p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url));p.on('dialog',lambda d:d.accept())
 p.set_content(HTML,wait_until='load');p.wait_for_timeout(300)
 ck(p.evaluate('validData(original)'),'Expanded K–12 catalogue passes browser validation')
 ck(p.evaluate('curriculum.grades.length')==13,'13 grade records, K–12')
 ck(p.evaluate('curriculum.topics.length')==433,'433 topic shelves loaded')
 ck(p.locator('#subjects button').count()==8,'Eight subject buttons preserved')
 ck(p.locator('.navlinks .nav-art').count()==4,'Four illustrated navigation icons replace top emojis')
 ck(p.locator('.game-card').count()==5,'Five initial desktop featured cards')
 ck(p.locator('#grade-bands button').count()==4,'Four grade-group controls')
 ck(p.locator('#view-all').inner_text().strip()=='All games','Shortened All games label')
 ck('Browser' not in p.locator('[data-game="khan-kids"] .platform-badge').inner_text(),'Mobile app is not mislabeled browser')
 ck('Trial' in p.locator('[data-game="tym-numbers-ios"] .card-tags').inner_text(),'Trial is not labeled free')
 ck(p.locator('button button, a button, button a').count()==0,'No nested interactive controls')
 p.screenshot(path=str(O/'desktop.png'),full_page=True)
 # Browser + app popups, including complete-card hit area and focus.
 for gid in ['khan-kids','starfall-abc','tym-numbers-ios']:
  card=p.locator(f'[data-open="{gid}"]');card.click(position={'x':8,'y':8});p.wait_for_timeout(150)
  ck(p.locator('#details').evaluate('(e)=>e.open'),f'{gid}: full-card corner opens dialog')
  ck(p.locator('.popup-art > img,.popup-art > svg').count()==1,f'{gid}: thumbnail repeated at top')
  ck(p.locator('.popup-meta .meta-item').count()==3,f'{gid}: three compact metadata tiles')
  ck(not p.locator('.popup-notes').evaluate('(e)=>e.open'),f'{gid}: grown-up notes collapsed by default')
  ck('Not play-tested' in p.locator('.popup-review').inner_text(),f'{gid}: no false playtest claim')
  ck(p.locator('.popup-launch').get_attribute('rel')=='noopener noreferrer',f'{gid}: external-link isolation')
  ck(p.locator('.popup-launch').get_attribute('target')=='_blank',f'{gid}: new-tab destination')
  ck(p.locator('.popup-launch').get_attribute('href')==p.evaluate('(id)=>dataset.games.find(g=>g.id===id).url',gid),f'{gid}: exact official URL retained')
  visible_words=p.evaluate("document.querySelector('#details').innerText.split(/\\s+/).length")
  ck(visible_words<90,f'{gid}: collapsed popup has fewer than 90 visible words')
  if gid=='khan-kids':
   p.locator('#details').screenshot(path=str(O/'popup-detail.png'));p.screenshot(path=str(O/'popup-desktop.png'))
  click(p,'.popup-notes summary');ck(p.locator('.popup-notes').evaluate('(e)=>e.open'),f'{gid}: notes open on demand')
  ck('Evidence scope.' in p.locator('.popup-notes-body').inner_text(),f'{gid}: evidence retained in notes')
  # The external action remains reachable with notes expanded.
  ck(p.locator('.popup-launch').is_visible(),f'{gid}: action visible with notes expanded')
  p.keyboard.press('Escape');ck(not p.locator('#details').evaluate('(e)=>e.open'),f'{gid}: Escape closes dialog')
  ck(card.evaluate('(e)=>e===document.activeElement'),f'{gid}: focus returns to source card')
 p.locator('[data-open="starfall-abc"]').focus();p.keyboard.press('Enter');ck(p.locator('#details').evaluate('(e)=>e.open'),'Enter opens a keyboard-focused card');p.keyboard.press('Escape')
 click(p,'[data-save="starfall-abc"]');ck(not p.locator('#details').evaluate('(e)=>e.open'),'Favorite button does not launch details')
 ck(p.locator('[data-save="starfall-abc"]').get_attribute('aria-pressed')=='true','Favorite pressed state updates')
 click(p,'.navlinks [data-nav="favorites"]');ck(p.locator('.game-card').count()==1,'Favorites filter works');home(p)
 # Every grade + every subject is a real filter, not decorative chrome.
 bands=[['K','1','2'],['3','4','5'],['6','7','8'],['9','10','11','12']]
 for i,gs in enumerate(bands):
  click(p,f'[data-band="{i}"]')
  ck(p.locator('#grade-buttons button').count()==len(gs),f'Band {i}: correct grade controls')
  for g in gs:
   click(p,f'[data-grade="{g}"]')
   ck(p.evaluate('state.grade')==g,f'Grade {g}: selection works')
   ck(p.locator(f'[data-grade="{g}"]').get_attribute('aria-pressed')=='true',f'Grade {g}: accessible selected state')
   ck(p.evaluate('[...document.querySelectorAll("[data-game]")].every(n=>dataset.games.find(g=>g.id===n.dataset.game).grades.includes(state.grade))'),f'Grade {g}: only mapped resources')
   ck(p.locator('.game-card').count()>0,f'Grade {g}: at least one starter activity')
   ck(p.evaluate('[...document.querySelectorAll("[data-quick]")].every(n=>curriculum.topics.some(t=>t.id===n.dataset.quick))'),f'Grade {g}: quick topics have real IDs')
   for sub in ['ela','math','science','hss','arts','health','pe','cs']:
    p.evaluate('(sub)=>{state.subject=sub;state.topic="all";renderChild()}',sub)
    ck(p.evaluate('[...document.querySelectorAll("[data-game]")].every(n=>dataset.games.find(g=>g.id===n.dataset.game).subjects.includes(state.subject))'),f'Grade {g}/{sub}: subject filter')
   p.evaluate('state.subject="all";renderChild()')
 p.evaluate("state.grade='9';state.subject='all';state.type='all';renderChild();window.scrollTo(0,0)");p.wait_for_timeout(150);p.screenshot(path=str(O/'grade9.png'),full_page=True)
 ck('History' in p.locator('#subjects').inner_text(),'Older grades use age-appropriate subject labels')
 ck(p.evaluate("approved().some(g=>g.review.status==='teacher_verified')"),'Teacher-verified Hub resources appear in child catalogue')
 ck(p.evaluate("dataset.games.filter(g=>g.review.status==='teacher_verified').length")==68,'68 retained teacher selections')
 ck(p.evaluate("!dataset.games.some(g=>/ahmadischool|ahmadi academy/i.test(g.url+' '+g.title))"),'Excluded academy is not imported')
 click(p,'#view-all') if p.locator('#view-all').is_visible() else None
 ck(p.evaluate("approved().some(g=>g.id==='hub-01-school-uniforms-research'&&g.grades.includes('9'))"),'Grade 9 assessment imported')
 p.evaluate("state.grade='9';state.subject='ela';state.showAll=true;renderGames()")
 ck(p.locator('[data-game="hub-01-school-uniforms-research"] .source-thumbnail').count()==1,'Original Learning Hub source thumbnail shown')
 click(p,'[data-open="hub-01-school-uniforms-research"]')
 ck('Teacher verified' in p.locator('.popup-review').inner_text(),'Teacher verification label remains separate from advertising evidence')
 ck('Ads not independently checked' in p.locator('.popup-review').inner_text(),'Unverified advertising is disclosed')
 ck(p.locator('.popup-art .source-thumbnail').count()==1,'Hub source thumbnail repeats in popup')
 p.keyboard.press('Escape')
 p.evaluate("state.grade='9';state.subject='all';state.showAll=false;renderGames()")
 click(p,'[data-type="explore"]');ck(p.locator('.game-card').count()>=2,'Explore filter includes interactive simulations')
 p.locator('#device-filter').select_option('app');ck(p.locator('.game-card').count()==0,'Device filter excludes browser sims from apps');ck(p.locator('.empty').count()==1,'Unfilled filter has an honest empty state')
 home(p);click(p,'#view-all');ck(p.locator('.game-card').count()==p.evaluate("approved().filter(g=>g.grades.includes('K')).length"),'All games expands current-grade catalogue')
 p.locator('#search').fill('Starfall');p.wait_for_timeout(100);ck(p.locator('.game-card').count()==5,'Search filters current grade by publisher/title')
 click(p,'#clear-search');ck(p.locator('#search').input_value()=='','Clear search works')
 click(p,'[data-subject="math"]');ck(p.locator('#topics button').count()>1,'Subject shows grade-specific topics');home(p)
 # Schema safety.
 rejects={
 'unsupported grade':"{...original.games[0],grades:['13']}",
 'unknown topic':"{...original.games[0],topicIds:['made-up']}",
 'mismatched topic':"{...original.games[0],topicIds:[curriculum.topics.find(t=>t.grade==='12').id]}",
 'non-HTTPS URL':"{...original.games[0],url:'javascript:alert(1)'}",
 'credentials in URL':"{...original.games[0],url:'https://name:pass@example.com'}",
 'invalid artwork path':"{...original.games[0],thumbnailAsset:'../image.webp'}",
 'unsupported platform':"{...original.games[0],platform:'console'}",
 'missing ad evidence':"{...original.games[0],review:{...original.games[0].review,adEvidenceSourceId:'missing'}}"}
 for label,record in rejects.items():ck(p.evaluate('!validData({...original,games:['+record+']})'),'Import rejects '+label)
 ck(p.evaluate('!validData({...original,games:[original.games[0],original.games[0]]})'),'Import rejects duplicate IDs')
 # Grown-up map/editor supports all grades.
 click(p,'.parent-nav');ck(p.locator('#parent-grade option').count()==13,'Adult map exposes all 13 grades')
 p.locator('#parent-grade').select_option('12');ck(p.locator('.topic-row').count()>20,'Grade 12 map populated')
 ck('American democracy' in p.locator('#parent-content').inner_text(),'Grade 12 contains democracy/economics shelves')
 ck('starter topic shelves' in p.locator('.notice').inner_text(),'New mapping scope disclosed')
 p.screenshot(path=str(O/'parent-k12.png'),full_page=True)
 click(p,'[data-tab="manage"]');ck(p.locator('input[name="grades"]').count()==13,'Link editor exposes 13 grade checkboxes')
 f=p.locator('#game-form');f.locator('[name="title"]').fill('Grade Twelve Test');f.locator('[name="publisher"]').fill('Local test')
 f.locator('[name="url"]').fill('https://example.org/grade-12');f.locator('[name="grades"][value="K"]').uncheck();f.locator('[name="grades"][value="12"]').check()
 f.locator('[name="subjects"][value="ela"]').uncheck();f.locator('[name="subjects"][value="math"]').check()
 opts=f.locator('#editor-topics option').count();ck(opts==6,'Editor topics respect selected Grade 12 and math')
 first=f.locator('#editor-topics option').first.get_attribute('value');f.locator('#editor-topics').select_option(first)
 f.locator('[name="priceLabel"]').fill('Free');f.locator('[name="access"]').fill('Browser');f.locator('[name="description"]').fill('Practice equations.');f.locator('[type="submit"]').click();p.wait_for_timeout(100)
 ck(p.evaluate("dataset.games.some(g=>g.title==='Grade Twelve Test'&&g.grades[0]==='12'&&g.review.status==='needs_review')"),'Grade 12 game saves into review queue')
 ck(p.evaluate("!approved().some(g=>g.title==='Grade Twelve Test')"),'Unreviewed new record is hidden from child catalogue')
 gid=p.evaluate("dataset.games.find(g=>g.title==='Grade Twelve Test').id")
 click(p,f'[data-review="{gid}"]');ck(not p.locator('#details').evaluate('(e)=>e.classList.contains("game-dialog")'),'Review form does not inherit compact-game layout')
 ck(p.locator('#review-form input[required][type="checkbox"]').count()==2,'Approval still requires both evidence and play-check attestations')
 p.keyboard.press('Escape')
 # Actual JSON import input, without persisting it outside this session.
 payload=json.dumps(p.evaluate('original')).encode()
 p.locator('#import-file').set_input_files({'name':'games.json','mimeType':'application/json','buffer':payload});p.wait_for_timeout(150)
 ck(p.evaluate('dataset.games.length')==220,'Import restores 220-resource supplied dataset')
 # Export payload handling; do not claim an actual user download was tested.
 export_ok=p.evaluate("""async()=>{let result;const create=URL.createObjectURL,revoke=URL.revokeObjectURL,clk=HTMLAnchorElement.prototype.click;URL.createObjectURL=b=>{result=b;return 'blob:test'};URL.revokeObjectURL=()=>{};HTMLAnchorElement.prototype.click=function(){};try{downloadJSON(dataset,'games.json');return JSON.parse(await result.text()).games.length===220}finally{URL.createObjectURL=create;URL.revokeObjectURL=revoke;HTMLAnchorElement.prototype.click=clk}}""")
 ck(export_ok,'Export produces valid 220-record JSON payload')
 # Imported text is rendered as text, not executed markup.
 p.evaluate("dataset.games[0].title='<img src=x onerror=alert(1)>';state.grade='K';switchView('explore',false)")
 ck(p.locator('.card-title img').count()==0,'Imported title is HTML-escaped');p.evaluate('dataset=structuredClone(original)');home(p)
 # Responsive widths and popup fit, with primary action in viewport.
 for w,h in [(320,568),(390,844),(600,900),(768,1024),(1024,1000),(1440,1100),(1920,1080)]:
  p.set_viewport_size({'width':w,'height':h});home(p);p.wait_for_timeout(220)
  ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'{w}px: no page horizontal overflow')
  ck(p.evaluate('[...document.querySelectorAll("img")].filter(i=>i.offsetParent!==null).every(i=>i.complete&&i.naturalWidth>0)'),f'{w}px: visible raster assets load')
  if w==390:p.screenshot(path=str(O/'mobile.png'),full_page=True)
  if w==768:p.screenshot(path=str(O/'tablet.png'),full_page=True)
  click(p,'[data-open="tym-numbers-ios"]');p.wait_for_timeout(150)
  ck(p.locator('#details').evaluate('(e)=>e.scrollWidth<=e.clientWidth'),f'{w}px: popup no horizontal overflow')
  ck(p.locator('.popup-launch').evaluate('(e)=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}'),f'{w}px: primary popup action visible')
  if w==390:p.screenshot(path=str(O/'popup-mobile.png'))
  p.keyboard.press('Escape')
 p.emulate_media(reduced_motion='reduce');home(p);click(p,'[data-grade="1"]')
 ck(p.locator('[data-grade="1"]').evaluate('(e)=>getComputedStyle(e).animationName')=='none','Reduced-motion disables press animation')
 ck(p.locator('.grade-button').first.evaluate('(e)=>getComputedStyle(e).transitionDuration')=='0s','Reduced-motion disables control transitions')
 p.emulate_media(reduced_motion='no-preference');p.set_viewport_size({'width':1440,'height':1100});home(p)
 p.locator('[data-grade="1"]').hover();ck(p.locator('[data-grade="1"]').evaluate('(e)=>getComputedStyle(e).transform')!='none','Grade button has hover feedback')
 ck(not errors,'No uncaught JavaScript errors during tests')
 ck(not requests,'No network requests from standalone catalogue interactions')
 b.close()
report={'version':'3','date':'2026-10-15','passed':len(checks),'failed':0,'checks':checks,'browser':'Headless Chromium / Playwright, set_content','consoleErrors':errors,'networkRequests':requests,'limitations':['Real navigation blocked by browser policy; hosted/file-origin persistence not tested.','No external games, app installs, external link handoffs or actual user downloads were tested.','No real touchscreen, assistive-technology, Safari or Firefox testing.','Curriculum expansion is a starter editorial map, not a standards-completeness audit.']}
(R/'docs/ui-test-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':len(checks),'failed':0}))

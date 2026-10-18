#!/usr/bin/env python3
"""Logic-only draft migration checks using an in-memory localStorage stub.
This does not verify real browser origin storage, disk persistence or cross-file access.
"""
from pathlib import Path
import copy,json,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'wonderwood-play.html').read_text(encoding='utf-8')
original=json.loads((ROOT/'data/games.json').read_text(encoding='utf-8'))
legacy=copy.deepcopy(original)
legacy['games']=[g for g in legacy['games'][:23] if g['id']!='starfall-abc']
legacy.pop('seedRevision',None)
legacy['games'][0]['title']='My saved V2 title'
checks=[]
def check(ok,name):
    if not ok: raise AssertionError(name)
    checks.append({'check':name,'result':'passed'})
def load(browser,values):
    page=browser.new_page()
    encoded=json.dumps({k:json.dumps(v) for k,v in values.items()}).replace('<','\\u003c')
    stub='''<script>window.__storage='''+encoded+''';Object.defineProperty(window,'localStorage',{value:{getItem:k=>window.__storage[k]??null,setItem:(k,v)=>{window.__storage[k]=String(v)},removeItem:k=>{delete window.__storage[k]}}});</script>'''
    page.set_content(html.replace('<head>','<head>'+stub),wait_until='load')
    return page
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    p=load(browser,{'wonderwood-catalogue-v2':legacy,'wonderwood-favorites-v2':['khan-kids']})
    check(p.evaluate('dataset.games[0].title')=='My saved V2 title','Legacy V2 edited title preserved')
    check(not p.evaluate("dataset.games.some(g=>g.id==='starfall-abc')"),'Legacy intentional deletion preserved')
    check(p.evaluate("dataset.games.filter(g=>g.id.startsWith('phet-')).length")>=5,'All PhET seed additions available in migrated draft')
    check(p.evaluate("dataset.games.some(g=>g.id==='codeorg-coursec')"),'K–12 seeds appended to legacy draft')
    check(p.evaluate("dataset.seedRevision===3"),'Migrated draft stamped with current seed revision')
    check(p.evaluate('new Set(dataset.games.map(g=>g.id)).size===dataset.games.length'),'No duplicate IDs in merged draft')
    check(p.evaluate("favorites.includes('khan-kids')"),'Favorites key remains compatible')
    p.evaluate('saveDraft()')
    check(p.evaluate("JSON.parse(window.__storage['wonderwood-catalogue-v3']).games[0].title")== 'My saved V2 title','Save writes merged data to the V3 key')
    p.close()
    v3=copy.deepcopy(original);v3['games']=v3['games'][:2];v3.pop('seedRevision',None);v3['games'][0]['title']='My V3 title'
    p=load(browser,{'wonderwood-catalogue-v2':legacy,'wonderwood-catalogue-v3':v3})
    check(p.evaluate('dataset.games[0].title')=='My V3 title','Valid V3 draft takes precedence over legacy')
    check(p.evaluate('dataset.games.length')==len(original['games'])-28+2,'V3 baseline removals preserved, new seeds appended')
    check(not p.evaluate("dataset.games.some(g=>g.id==='starfall-an')"),'V3 intentional deletion is respected')
    check(p.evaluate("dataset.games.some(g=>g.id==='phet-function-builder')"),'New simulations present in migrated V3 draft')
    p.evaluate('dataset.games=dataset.games.filter(g=>g.id!=="phet-function-builder");saveDraft()')
    saved=json.loads(p.evaluate("window.__storage['wonderwood-catalogue-v3']"))
    p.close()
    p=load(browser,{'wonderwood-catalogue-v3':saved})
    check(not p.evaluate("dataset.games.some(g=>g.id==='phet-function-builder')"),'Deleting new seed after migration remains intentional')
    p.close()
    p=load(browser,{'wonderwood-catalogue-v3':{'schemaVersion':99},'wonderwood-catalogue-v2':legacy})
    check(p.evaluate('dataset.games[0].title')=='My saved V2 title','Invalid V3 draft falls back to valid legacy')
    p.close()
    p=load(browser,{'wonderwood-catalogue-v3':{'schemaVersion':99},'wonderwood-catalogue-v2':{'schemaVersion':99}})
    check(p.evaluate('dataset.games.length')==222,'Invalid saved drafts fall back to current seed data')
    p.close()
    rev2=copy.deepcopy(original)
    rev2['seedRevision']=2
    rev2['games']=[g for g in rev2['games'] if not g['id'].startswith('hub-') and g['id']!='phet-function-builder']
    rev2['games'][0]['title']='Saved teacher title'
    p=load(browser,{'wonderwood-catalogue-v3':rev2})
    check(p.evaluate('dataset.seedRevision')==3,'Revision 2 drafts migrate to revision 3')
    check(p.evaluate("dataset.games.filter(g=>g.id.startsWith('hub-')).length")==70,'Hub additions appear in existing valid drafts')
    check(not p.evaluate("dataset.games.some(g=>g.id==='phet-function-builder')"),'Revision 2 intentional deletion is not resurrected')
    check(p.evaluate('dataset.games[0].title')=='Saved teacher title','Revision 2 saved title remains unchanged')
    p.evaluate('dataset.games=dataset.games.filter(g=>g.id!=="hub-01-school-uniforms-research");saveDraft()')
    saved_v3=json.loads(p.evaluate("window.__storage['wonderwood-catalogue-v3']"))
    p.close()
    p=load(browser,{'wonderwood-catalogue-v3':saved_v3})
    check(not p.evaluate("dataset.games.some(g=>g.id==='hub-01-school-uniforms-research')"),'Intentional deletion of a Hub seed remains deleted')
    p.close();browser.close()
report={'version':'3','passed':len(checks),'failed':0,'scope':'In-memory mocked storage logic only; not real persistence','checks':checks}
(ROOT/'docs/migration-test-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'failed':0,'scope':report['scope']}))

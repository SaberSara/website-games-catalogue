#!/usr/bin/env python3
"""Regression tests: optional, privacy-focused Cloudflare traffic tracking."""
from pathlib import Path
from subprocess import run
from os import environ
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
TOKEN='0123456789abcdef0123456789abcdef'
BUILD=[sys.executable,str(ROOT/'tools/build.py')]
checks=[]
def ck(ok,detail):
    assert ok,detail
    checks.append(detail)
def build(token):
    env=dict(environ)
    env.pop('CF_WEB_ANALYTICS_TOKEN',None)
    if token is not None:env['CF_WEB_ANALYTICS_TOKEN']=token
    return run(BUILD,cwd=ROOT,capture_output=True,text=True,env=env)
try:
    b=build(None);ck(b.returncode==0,'Site builds without analytics token')
    html=(ROOT/'index.html').read_text(encoding='utf-8');portable=(ROOT/'wonderwood-play.html').read_text(encoding='utf-8')
    ck('name="wonderwood-analytics" content="off"' in html,'Tracking is off by default')
    ck('static.cloudflareinsights.com/beacon.min.js' not in html,'No beacon without token')
    ck('📊 Analytics' in html and 'Privacy & stats' in html,'Analytics tab and footer link are present')
    ck('name="wonderwood-analytics" content="off"' in portable,'Standalone preview reports tracking off')
    ck('static.cloudflareinsights.com/beacon.min.js' not in portable,'Standalone preview makes no Cloudflare request')

    b=build(TOKEN);ck(b.returncode==0,'Site builds with a site token')
    html=(ROOT/'index.html').read_text(encoding='utf-8');portable=(ROOT/'wonderwood-play.html').read_text(encoding='utf-8')
    ck('name="wonderwood-analytics" content="configured"' in html,'Configured status is included')
    ck(html.count('https://static.cloudflareinsights.com/beacon.min.js')==1,'Exactly one Cloudflare beacon')
    ck(html.count(TOKEN)==1,'Site token is inserted exactly once')
    ck('sabersara.github.io' in html and "location.protocol !== 'https:'" in html,'Beacon limited to HTTPS on intended hostname')
    ck("location.pathname.startsWith('/website-games-catalogue/')" in html,'Other GitHub Pages projects are excluded')
    ck('\\"spa\\":false' in html,'No simulated pageviews for grade/button changes')
    ck(TOKEN not in portable and 'static.cloudflareinsights.com/beacon.min.js' not in portable,'Portable preview never has tracker even when configured')
    ck('grade=' not in html.split('https://static.cloudflareinsights.com/beacon.min.js')[-1][:350],'Beacon carries no grade or child actions')

    b=build('not-a-token');ck(b.returncode!=0 and 'CF_WEB_ANALYTICS_TOKEN' in b.stderr,'Bad token fails securely')
    b=build('YOUR_CLOUDFLARE_TOKEN_PLACEHOLDER');ck(b.returncode!=0,'Placeholder token rejected')
    # Return downloadable artifact to normal untracked local mode.
    b=build(None);ck(b.returncode==0,'Local artifact restored to untracked mode')

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for width in (390,768,1280):
                page=browser.new_page(viewport={'width':width,'height':860})
                page.set_content((ROOT/'wonderwood-play.html').read_text(encoding='utf-8'),wait_until='load',timeout=25000)
                page.locator('.parent-nav').click()
                page.locator('[data-tab="analytics"]').click()
                ck(page.locator('#analytics-title').is_visible(),f'Adult analytics visible at {width}px')
                ck(page.locator('.analytics-card').count()==6,f'Six aggregate metric groups at {width}px')
                ck(page.locator('.analytics-status').inner_text()=='Setup needed',f'No invented connected state at {width}px')
                ck(page.locator('.analytics-actions a').first.get_attribute('href')=='https://dash.cloudflare.com/',f'Dashboard button links correctly at {width}px')
                ck(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),f'No horizontal overflow at {width}px')
                if width==1280:
                    p=ROOT/'previews';p.mkdir(exist_ok=True)
                    page.screenshot(path=str(p/'analytics-parent.png'),full_page=True)
                page.close()
            browser.close()
    except ImportError:
        print('Playwright unavailable; source/build checks still completed')
finally:
    # Never leave mock analytics token in local distributable output.
    assert build(None).returncode==0
p=ROOT/'docs/ANALYTICS-TEST-REPORT.json'
p.write_text(json.dumps({'passed':len(checks),'checks':checks,'limitations':'Cloudflare account not connected; live traffic collection and provider dashboard require the site owner to add their beacon token.'},indent=2)+'\n')
print(json.dumps({'passed':len(checks),'report':str(p)},indent=2))

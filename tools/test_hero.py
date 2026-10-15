#!/usr/bin/env python3
"""Regression tests for the bright, uncropped Wonderwood hero artwork.

Requires Python Playwright and local Chromium. Exercises the built portable page;
never follows external activity links or claims to validate those sites.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'src/styles.css').read_text(encoding='utf-8')
HTML = (ROOT / 'wonderwood-play.html').read_text(encoding='utf-8')
checks = []

def check(condition, label):
    assert condition, label
    checks.append(label)

check("background-image:url('../assets/hero-left.webp')" in CSS,
      'Complete original left illustration is restored')
check("background-image:url('../assets/hero-right.webp')" in CSS,
      'Complete original right illustration is restored')
check("background-image:url('../assets/hero-left-v4.webp')" not in CSS,
      'Cropped screenshot-derived left banner is no longer used')
check("background-image:url('../assets/hero-right-v4.webp')" not in CSS,
      'Cropped screenshot-derived right banner is no longer used')
check('background:#fff;min-height:377px' not in CSS,
      'Opaque white hero stage from V4 is removed')

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                 args=['--no-sandbox'])
    for width in [320, 350, 390, 600, 601, 640, 700, 768, 960, 961, 1024,
                  1190, 1191, 1270, 1440, 1600, 1920]:
        page = browser.new_page(viewport={'width': width, 'height': 900})
        page.set_content(HTML, wait_until='load')
        state = page.evaluate('''() => {
          const rect = sel => {
            const r = document.querySelector(sel).getBoundingClientRect();
            return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height};
          };
          return {
            scrollWidth: document.documentElement.scrollWidth,
            stageBackground: getComputedStyle(document.querySelector('.hero')).backgroundImage,
            leftOpacity: getComputedStyle(document.querySelector('.hero-left')).opacity,
            rightOpacity: getComputedStyle(document.querySelector('.hero-right')).opacity,
            leftArt: getComputedStyle(document.querySelector('.hero-left')).backgroundImage,
            rightArt: getComputedStyle(document.querySelector('.hero-right')).backgroundImage,
            left:rect('.hero-left'), right:rect('.hero-right'),
            grade:rect('.grade-picker'), hero:rect('.hero')
          };
        }''')
        check(state['scrollWidth'] <= width, f'{width}px: no horizontal overflow')
        check(state['leftOpacity'] == '1' and state['rightOpacity'] == '1',
              f'{width}px: art not faded or washed out')
        check('data:image/webp' in state['leftArt'] and 'data:image/webp' in state['rightArt'],
              f'{width}px: both complete image assets are loaded')
        check('gradient' in state['stageBackground'],
              f'{width}px: blue sky illustration backdrop, not solid white')
        if width <= 960:
            check(state['left']['top'] >= state['grade']['bottom'] - 1,
                  f'{width}px: fox is below the last grade button')
            check(state['right']['top'] >= state['grade']['bottom'] - 1,
                  f'{width}px: owl is below the last grade button')
        elif width <= 1190:
            check(state['left']['bottom'] <= state['grade']['top'] + 1,
                  f'{width}px: fox finishes before the grade buttons')
            check(state['right']['bottom'] <= state['grade']['top'] + 1,
                  f'{width}px: owl finishes before the grade buttons')
        # A school band is still a real control, not printed over a raster picture.
        page.locator('[data-band="3"]').click()
        check(page.locator('#grade-buttons [data-grade="12"]').count() == 1,
              f'{width}px: Year 12 selector still works')
        page.close()
    browser.close()

out = {'passed': len(checks), 'failed': 0, 'scope': 'Local Chromium responsive hero and real grade interaction tests',
       'checks': checks}
(ROOT / 'docs' / 'hero-test-report.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps({'passed':len(checks),'failed':0}))
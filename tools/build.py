#!/usr/bin/env python3
"""Build static site + portable HTML using only Python's standard library.
Run from any directory: python tools/build.py
The served site makes no third-party requests until a user follows an external link.
"""
from pathlib import Path
import base64
import json
import mimetypes
import re

ROOT = Path(__file__).resolve().parents[1]

def json_for_html(value):
    # Prevent JSON strings from terminating their application/json script element.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')

def main():
    from validate import validate
    validate()
    html=(ROOT/'src/template.html').read_text(encoding='utf-8')
    for key,name in [('__CURRICULUM__','curriculum'),('__GAMES__','games')]:
        html=html.replace(key,json_for_html(json.loads((ROOT/f'data/{name}.json').read_text(encoding='utf-8'))))
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    css=(ROOT/'src/styles.css').read_text(encoding='utf-8')
    js=(ROOT/'src/app.js').read_text(encoding='utf-8')
    # Assets named dynamically in JS need a lookup, not replacement of source code fragments.
    asset_map={}
    for path in sorted((ROOT/'assets').iterdir()):
        if not path.is_file():continue
        mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        asset_map['assets/'+path.name]='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
    for source,uri in asset_map.items():
        html=html.replace('"'+source+'"','"'+uri+'"')
        css=css.replace('../'+source,uri)
    # Translate only attributes written by the app. DOM/CSS/UI remain live HTML.
    portable_js='const PORTABLE_ASSETS = '+json.dumps(asset_map,separators=(',',':'))+';\n'+js
    # Patch known image string generation points, including template literals.
    portable_js=portable_js.replace('src="assets/subject-${asset}.webp"','src="${PORTABLE_ASSETS[`assets/subject-${asset}.webp`]}"')
    portable_js=portable_js.replace('src="assets/${asset}"','src="${PORTABLE_ASSETS[`assets/${asset}`]}"')
    portable_js=portable_js.replace('src="assets/${grade === \'K\' ? \'fox\' : \'bunny\'}.webp"','src="${PORTABLE_ASSETS[`assets/${grade === \'K\' ? \'fox\' : \'bunny\'}.webp`]}"')
    html=html.replace('<link rel="stylesheet" href="src/styles.css">','<style>\n'+css+'\n</style>')
    html=html.replace('<script src="src/app.js" defer></script>','<script>\n'+portable_js+'\n</script>')
    (ROOT/'wonderwood-play.html').write_text(html,encoding='utf-8')
    print('Built index.html and wonderwood-play.html')

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Generate static index.html from src/template.html + data, no dependencies."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def safe_json(x):
    return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
def main():
    html=(ROOT/'src/template.html').read_text(encoding='utf-8')
    for token,stem in [('__CURRICULUM__','curriculum'),('__GAMES__','games')]:
        doc=json.loads((ROOT/'data'/f'{stem}.json').read_text(encoding='utf-8'))
        html=html.replace(token,safe_json(doc))
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    print('Built index.html. Serve from the repository root.')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Offline checks for the editable Wonderwood data."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def main():
    c=json.loads((R/'data/curriculum.json').read_text(encoding='utf-8'))
    g=json.loads((R/'data/games.json').read_text(encoding='utf-8'))
    assert len(c['grades'])==13
    assert isinstance(c['topics'],list) and c['topics']
    assert isinstance(g['games'],list)
    used=set()
    for game in g['games']:
        assert game['id'] not in used, 'Duplicate game id'
        used.add(game['id'])
        assert game['url'].startswith('https://'), 'Requires HTTPS URL'
    print(f"Validated {len(c['grades'])} grades, {len(c['topics'])} topics, {len(g['games'])} games")
if __name__=='__main__': main()

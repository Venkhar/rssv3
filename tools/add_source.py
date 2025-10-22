from __future__ import annotations
import os, sys, json, yaml
from pathlib import Path

SOURCES = Path('sources.yaml')

def main():
    # Inputs can come from GitHub Actions (repository_dispatch or workflow_dispatch)
    payload = {}
    # 1) repo_dispatch: payload in GITHUB_EVENT_PATH under client_payload
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if event_path and Path(event_path).exists():
        try:
            with open(event_path, 'r', encoding='utf-8') as f:
                evt = json.load(f)
            payload = (evt.get('client_payload') or {})
        except Exception:
            # si le fichier n'est pas un repo_dispatch, on ignore
            pass

    # 2) workflow_dispatch: read env/inputs (mapés par le job)
    # Les workflows mettent ces valeurs dans des variables d'env INPUT_*
    payload.setdefault('url', os.getenv('INPUT_URL'))
    payload.setdefault('out', os.getenv('INPUT_OUT'))
    payload.setdefault('feed_title', os.getenv('INPUT_FEED_TITLE'))
    payload.setdefault('site_name', os.getenv('INPUT_SITE_NAME'))

    # selectors arrive en JSON (string), on le parse
    selectors = os.getenv('INPUT_SELECTORS')
    if selectors:
        try:
            payload['selectors'] = json.loads(selectors)
        except Exception:
            print('WARN: selectors JSON invalide, ignoré', file=sys.stderr)

    # booléens en chaînes "true"/"false"
    if os.getenv('INPUT_FETCH_DETAIL'):
        payload['fetch_detail'] = os.getenv('INPUT_FETCH_DETAIL').lower() == 'true'
    if os.getenv('INPUT_FORCE_RELATIVE'):
        payload['force_relative'] = os.getenv('INPUT_FORCE_RELATIVE').lower() == 'true'

    # Validation minimale
    if not payload.get('url'):
        print('Missing url', file=sys.stderr)
        return 2

    # Charge sources.yaml (ou crée une base vide)
    data = {'sources': []}
    if SOURCES.exists():
        with open(SOURCES, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {'sources': []}

    # index pour éviter les doublons (url, out)
    seen = {(s.get('url'), s.get('out')) for s in data.get('sources', [])}
    entry = {k: v for k, v in payload.items() if v is not None}

    # Valeur par défaut pour "out" si absent : dérivée de l'URL
    if 'out' not in entry or not entry['out']:
        from urllib.parse import urlparse
        u = urlparse(entry['url'])
        base = (u.netloc + u.path.rstrip('/')).replace('/', '-').replace(':', '-')
        entry['out'] = f"{base or 'feed'}.xml"

    key = (entry.get('url'), entry.get('out'))

    # Upsert : ajoute si nouveau, sinon met à jour l'existant
    if key not in seen:
        data['sources'].append(entry)
        print(f"Added: {entry['url']} → {entry['out']}")
    else:
        new_sources = []
        for s in data['sources']:
            if (s.get('url'), s.get('out')) == key:
                s.update(entry)
                print(f"Updated: {entry['url']} → {entry['out']}")
            new_sources.append(s)
        data['sources'] = new_sources

    # Sauvegarde
    with open(SOURCES, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    print(f"sources.yaml updated with {entry['url']} → {entry['out']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

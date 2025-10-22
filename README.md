# rssgen — Générateur de flux RSS à partir d'URL


**But** : à partir d'une URL d'une page qui liste des articles/mises à jour mais qui ne propose pas de flux, générer automatiquement un `feed.xml` (RSS 2.0) et l'exporter.


## Caractéristiques
- Entrée : une URL (ou plusieurs) via CLI.
- Détection automatique des items : `<article>`, classes courantes (`post`, `entry`, `article`, `news`), microdonnées (`itemprop="datePublished"`), balises `<time>`.
- Récupération optionnelle des pages de détail pour enrichir titre/date/résumé (via Readability).
- Normalisation des dates (via `dateparser`).
- Génération RSS 2.0 (via `feedgen`).
- Fichier de configuration optionnel (YAML) pour des sélecteurs CSS spécifiques à un site.
- Caching simple (sur disque) et limitation de taux pour être "courtois".
- Mode batch + sortie dans un dossier `dist/`.


## Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```


## Utilisation
```bash
python -m rssgen.cli https://exemple.com/blog/ \
--site-name "Exemple Blog" \
--feed-title "Mises à jour — Exemple" \
--max-items 30 \
--output dist/feed.xml
```


Avec un fichier de config personnalisé :
```bash
python -m rssgen.cli https://exemple.com/updates/ \
--config config.yaml \
--output dist/exemple-updates.xml
```


`config.yaml` (exemple) :
```yaml
selectors:
item: "article, .post, .entry, .news-item"
link: "h2 a, .post-title a, a.title"
title: "h2, .post-title, .title"
date: "time[datetime], time, .date, [itemprop=\"datePublished\"]"
content: ".content, .summary, .excerpt"
force_relative: true # n'inclure que les liens du même domaine
fetch_detail: true # ouvrir la page de détail pour enrichir
```


## Publication GitHub
- Ajoutez ce repo sur GitHub.
- (Optionnel) Activez un workflow planifié pour régénérer le flux chaque jour et pousser `dist/feed.xml` (voir `.github/workflows/cron.yml`).

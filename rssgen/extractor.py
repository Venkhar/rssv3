from __future__ import annotations
items: list[Item] = []


# 1) pré-sélection : blocs d'article
blocks = soup.select(sel_item)
if not blocks:
# fallback : chercher des listes de liens dans le contenu principal
blocks = soup.select("main a, .content a, article a") or soup.select("a")


seen = set()
for blk in blocks:
a = blk.select_one(sel_link) if blk else None
if not a:
a = blk if blk.name == "a" else None
if not a or not a.get("href"):
continue
href = a.get("href").strip()
abs_href = absolutize(base_url, href)
if force_relative and not same_domain(base_url, abs_href):
continue
if abs_href in seen:
continue
seen.add(abs_href)


title_el = blk.select_one(sel_title)
title = (title_el.get_text(strip=True) if title_el else a.get_text(strip=True)) or abs_href


# date
dt_el = blk.select_one(sel_date)
dt_text = None
if dt_el:
dt_text = dt_el.get("datetime") or dt_el.get("content") or dt_el.get_text(strip=True)
else:
# heuristique : si le bloc contient une chaîne ressemblant à une date
text = blk.get_text(" ", strip=True)
if looks_like_datetime(text):
dt_text = text
dt_iso = None
if dt_text:
d = parse_date(dt_text, settings={"RELATIVE_BASE": None})
if d:
dt_iso = d.isoformat()


# summary
content_el = blk.select_one(sel_content)
summary = content_el.get_text(" ", strip=True)[:400] if content_el else None


items.append(Item(url=abs_href, title=title, date=dt_iso, summary=summary))


return items




def enrich_from_detail(html: str, item: Item) -> Item:
# Utiliser Readability pour extraire un titre/summary/date éventuelle
try:
doc = Document(html)
if not item.title or len(item.title) < 5:
item.title = doc.short_title() or item.title
summary_html = doc.summary()
# retirer les balises grossièrement
text = BeautifulSoup(summary_html, "lxml").get_text(" ", strip=True)
item.summary = (item.summary or text[:500])
except Exception:
pass


# dates via meta
soup = BeautifulSoup(html, "lxml")
meta = soup.select_one("meta[property='article:published_time'], meta[name='date'], meta[itemprop='datePublished']")
if meta:
dt = meta.get("content")
if dt and not item.date:
d = parse_date(dt)
if d:
item.date = d.isoformat()
return item

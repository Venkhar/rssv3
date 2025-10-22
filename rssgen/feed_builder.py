from __future__ import annotations
from typing import Iterable
from feedgen.feed import FeedGenerator




def build_rss(*, site_url: str, site_name: str, feed_title: str, items: Iterable[dict]) -> bytes:
fg = FeedGenerator()
fg.load_extension('podcast') # no-op si inutilisé
fg.title(feed_title or site_name)
fg.link(href=site_url, rel='alternate')
fg.link(href=site_url.rstrip('/') + '/feed.xml', rel='self')
fg.description(f"Flux généré automatiquement pour {site_name}")
for it in items:
fe = fg.add_entry()
fe.id(it['url'])
fe.link(href=it['url'])
fe.title(it['title'])
if it.get('summary'):
fe.description(it['summary'])
if it.get('date'):
fe.published(it['date'])
return fg.rss_str(pretty=True)

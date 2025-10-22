from __future__ import annotations
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import asyncio
import httpx
from .utils import USER_AGENT, SimpleCache
from .extractor import extract_items, enrich_from_detail
from .feed_builder import build_rss


app = FastAPI(title="rssgen API")


class FeedRequest(BaseModel):
url: str
feed_title: str | None = None
site_name: str | None = None
selectors: dict | None = None
fetch_detail: bool = True
force_relative: bool = False
max_items: int = 25


@app.post('/feeds')
async def create_feed(req: FeedRequest):
cache = SimpleCache(ttl_seconds=1800)
limits = httpx.Limits(max_connections=10)
async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, limits=limits, http2=True, follow_redirects=True) as client:
r = await client.get(req.url, timeout=20)
if r.status_code >= 400:
raise HTTPException(status_code=400, detail=f"Fetch failed: {r.status_code}")
html = r.text
items = extract_items(html, req.url, req.selectors or {}, force_relative=req.force_relative)
if req.fetch_detail:
enriched = []
for it in items[: req.max_items]:
try:
d = await client.get(it.url, timeout=20)
it = enrich_from_detail(d.text, it)
await asyncio.sleep(0.02)
except Exception:
pass
enriched.append(it)
items = enriched
else:
items = items[: req.max_items]
site_name = req.site_name or req.url
feed_title = req.feed_title or f"Mises à jour — {site_name}"
feed_bytes = build_rss(site_url=req.url, site_name=site_name, feed_title=feed_title,
items=[it.__dict__ for it in items])
return Response(content=feed_bytes, media_type='application/rss+xml')

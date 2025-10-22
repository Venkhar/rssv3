from __future__ import annotations
await asyncio.sleep(0.05)
except Exception:
pass
enriched.append(it)
items = enriched
else:
items = items[: max_items]


if not site_name:
try:
soup = BeautifulSoup(html, 'lxml')
site_name = soup.title.get_text(strip=True) if soup.title else url
except Exception:
site_name = url
feed_title = feed_title or f"Mises à jour — {site_name}"


feed_bytes = build_rss(site_url=url, site_name=site_name, feed_title=feed_title,
items=[it.__dict__ for it in items])
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, out_name)
with open(path, 'wb') as f:
f.write(feed_bytes)
return path, len(items)


async def run_batch(sources: list[dict], *, concurrency: int, cache_ttl: int, out_dir: str, max_items: int) -> int:
cache = SimpleCache(ttl_seconds=cache_ttl)
limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
async with httpx.AsyncClient(headers=HEADERS, limits=limits, http2=True, follow_redirects=True) as client:
sem = asyncio.Semaphore(concurrency)
async def worker(src: dict):
async with sem:
path, n = await process_one(client, src, cache, out_dir, max_items)
print(f"✅ {src['url']} → {path} ({n} entrées)")
await asyncio.gather(*(worker(s) for s in sources))
return 0


async def run_single(url: str, **kwargs) -> int:
cfg = {"sources": [{"url": url, **({k:v for k,v in kwargs.items() if v is not None})}]}
return await run_batch(cfg["sources"], concurrency=kwargs.get("concurrency",5), cache_ttl=kwargs.get("cache_ttl",1800), out_dir=kwargs.get("out_dir","dist"), max_items=kwargs.get("max_items",25))




def main(argv: Optional[list[str]] = None) -> int:
p = argparse.ArgumentParser(description="Génère un ou plusieurs flux RSS à partir d'URL")
p.add_argument('url', nargs='?', help='URL unique (sinon utiliser --list)')
p.add_argument('--list', help='Fichier YAML listant des sources (voir README)')
p.add_argument('--out-dir', default='dist')
p.add_argument('--site-name', default=None)
p.add_argument('--feed-title', default=None)
p.add_argument('--max-items', type=int, default=25)
p.add_argument('--concurrency', type=int, default=10)
p.add_argument('--cache-ttl', type=int, default=1800)
args = p.parse_args(argv)


if not args.url and not args.list:
print("Fournir une URL ou --list sources.yaml", file=sys.stderr)
return 2


if args.list:
with open(args.list, 'r', encoding='utf-8') as f:
cfg = yaml.safe_load(f) or {}
sources = cfg.get('sources') or []
return asyncio.run(run_batch(sources, concurrency=args.concurrency, cache_ttl=args.cache_ttl, out_dir=args.out_dir, max_items=args.max_items))
else:
return asyncio.run(run_single(args.url, site_name=args.site_name, feed_title=args.feed_title, out_dir=args.out_dir, max_items=args.max_items, concurrency=args.concurrency, cache_ttl=args.cache_ttl))


if __name__ == '__main__':
raise SystemExit(main())

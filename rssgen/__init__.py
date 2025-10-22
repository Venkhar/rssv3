__version__ = "0.1.0"


---


# rssgen/utils.py
from __future__ import annotations
import hashlib
import os
import re
import time
from urllib.parse import urljoin, urlparse


USER_AGENT = (
"rssgen/0.2 (+https://github.com/yourname/rssgen; polite crawler)"
)


class SimpleCache:
def __init__(self, base_dir: str = ".cache", ttl_seconds: int = 3600):
self.base_dir = base_dir
self.ttl = ttl_seconds
os.makedirs(base_dir, exist_ok=True)


def _path(self, key: str) -> str:
key_b = hashlib.sha256(key.encode("utf-8")).hexdigest()
return os.path.join(self.base_dir, key_b + ".bin")


def get(self, key: str) -> bytes | None:
p = self._path(key)
if not os.path.exists(p):
return None
if time.time() - os.path.getmtime(p) > self.ttl:
return None
with open(p, "rb") as f:
return f.read()


def set(self, key: str, data: bytes) -> None:
p = self._path(key)
with open(p, "wb") as f:
f.write(data)




def same_domain(url: str, href: str) -> bool:
u = urlparse(url)
h = urlparse(href)
return (h.netloc == "" or h.netloc == u.netloc)




def absolutize(base: str, href: str) -> str:
return urljoin(base, href)




def looks_like_datetime(text: str) -> bool:
return bool(re.search(r"\d{4}[-/].+|\d{1,2}\s\w+\s\d{4}", text))

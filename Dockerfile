FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY rssgen ./rssgen
COPY sources.yaml ./sources.yaml
CMD ["python", "-m", "rssgen.cli", "--list", "sources.yaml", "--out-dir", "dist", "--concurrency", "20"]

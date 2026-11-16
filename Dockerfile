FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code plus the prebuilt data (orders.db and the Chroma index).
COPY fieldkit/ fieldkit/
COPY mcp_server/ mcp_server/
COPY data/ data/

# Cloud Run sets $PORT. The API key comes from Secret Manager, never from a file.
ENV GOOGLE_GENAI_USE_VERTEXAI=FALSE
CMD ["sh", "-c", "adk web --host 0.0.0.0 --port ${PORT:-8080} /app"]

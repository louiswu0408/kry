# Build React, then serve it alongside FastAPI from a single Render service.
FROM node:24-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn requests python-dotenv google-genai
COPY . ./
COPY --from=frontend-build /frontend/dist /app/frontend/dist
EXPOSE 10000
CMD ["sh", "-c", "uvicorn kry_web:app --host 0.0.0.0 --port ${PORT:-10000}"]

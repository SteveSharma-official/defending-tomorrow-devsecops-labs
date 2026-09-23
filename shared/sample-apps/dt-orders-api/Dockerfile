# syntax=docker/dockerfile:1
# Hardened reference image for dt-orders-api (LAB-09 solution baseline).
# EXECUTION VALIDATION REQUIRED: pin the base image by digest before use:
#   docker buildx imagetools inspect python:3.13-slim  -> copy the index digest below


FROM python:3.13-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ORDERS_DB=/tmp/orders.db \
    PORT=8080
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=build /install /usr/local
COPY --chown=root:root --chmod=0444 app.py config.yaml ./
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health').status==200 else 1)"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]

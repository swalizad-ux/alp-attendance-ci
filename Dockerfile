# ---- build stage: install dependencies into a virtualenv ----
FROM python:3.12-slim AS build
WORKDIR /app
RUN python -m venv /venv
COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- runtime stage: small image, non-root user ----
FROM python:3.12-slim
RUN useradd --create-home alp
COPY --from=build /venv /venv
WORKDIR /app
COPY app ./app
COPY wsgi.py .
USER alp
ENV PATH="/venv/bin:$PATH" PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "wsgi:app"]

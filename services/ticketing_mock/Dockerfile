# Ticketing mock: a stand-in for the company ticketing system.
# Build context is this folder: docker build -t ticketing-mock services/ticketing_mock
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mockapi ./mockapi

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 mock
USER mock

EXPOSE 8081

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/health', timeout=2)"

CMD ["uvicorn", "mockapi.main:app", "--host", "0.0.0.0", "--port", "8081"]

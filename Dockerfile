FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system copilot && useradd --system --gid copilot copilot
COPY pyproject.toml README.md ./
COPY src ./src
COPY services ./services
RUN pip install --no-cache-dir ".[course,ticketing,protocols,agents,postgres,telemetry]"
COPY data ./data
COPY policies ./policies
COPY release ./release
RUN mkdir -p /app/.work && chown -R copilot:copilot /app/.work
USER copilot
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=3)"
CMD ["copilot", "serve", "--host", "0.0.0.0", "--port", "8080"]

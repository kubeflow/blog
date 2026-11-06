FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY retry_safe_llm_eval /app/retry_safe_llm_eval
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "-m", "retry_safe_llm_eval.server", "--host", "0.0.0.0", "--port", "8080", "--db-path", "/data/state.sqlite3"]

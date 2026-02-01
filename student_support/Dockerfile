FROM python:3.11-slim

# Verhindert .pyc Dateien und sorgt für sofortige Logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installiere Abhängigkeiten BEVOR der Code kopiert wird (Caching-Vorteil)
RUN pip install --no-cache-dir \
    crewai \
    crewai-tools \
    fastapi \
    uvicorn \
    requests \
    pydantic \
    litellm \
     \
    apscheduler

# Kopiere den Inhalt des student_support Ordners in das Arbeitsverzeichnis
COPY ./student_support .

EXPOSE 8001

# Starte die App (app.py muss direkt in /app liegen)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
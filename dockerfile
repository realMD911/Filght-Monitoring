FROM python:3.9-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere alles
COPY . /app

# Installiere das Projekt
RUN pip install /app/opensky-api-master/python

# Kopiere die requirements.txt und installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r /app/requirements.txt

# Führe das Skript aus
CMD ["python", "getAPIData.py"]

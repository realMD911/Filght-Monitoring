import time
import os
from dotenv import load_dotenv
from opensky_api import OpenSkyApi
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway

# Laden der Umgebungsvariablen
load_dotenv()

# Prometheus Metriken definieren
registry = CollectorRegistry()
flight_count = Gauge('opensky_flight_count', 'Anzahl der aktuellen Flüge', registry=registry)
avg_altitude = Gauge('opensky_avg_altitude', 'Durchschnittliche Flughöhe aller Flugzeuge', registry=registry)
avg_speed = Gauge('opensky_avg_speed', 'Durchschnittliche Geschwindigkeit aller Flugzeuge', registry=registry)

# Dynamische Metriken für GPS-Koordinaten der Flugzeuge
latitude_metric = Gauge('opensky_flight_latitude', 'Breitengrad der Flugzeuge', ['icao24'], registry=registry)
longitude_metric = Gauge('opensky_flight_longitude', 'Längengrad der Flugzeuge', ['icao24'], registry=registry)

# OpenSky API Zugangsdaten
USERNAME = os.getenv("OPEN_SKY_USERNAME")
PASSWORD = os.getenv("OPEN_SKY_PASSWORD")
api = OpenSkyApi(USERNAME, PASSWORD)

# Pushgateway URL aus Umgebungsvariable
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")

def fetch_flight_data():
    states = api.get_states()
    if states:
        num_flights = len(states.states)
        altitudes = [s.geo_altitude for s in states.states if s.geo_altitude is not None]
        speeds = [s.velocity for s in states.states if s.velocity is not None]
        
        flight_count.set(num_flights)
        avg_altitude.set(sum(altitudes) / len(altitudes) if altitudes else 0)
        avg_speed.set(sum(speeds) / len(speeds) if speeds else 0)

        # GPS-Koordinaten für jedes Flugzeug speichern
        for s in states.states:
            if s.latitude is not None and s.longitude is not None:
                latitude_metric.labels(icao24=s.icao24).set(s.latitude)
                longitude_metric.labels(icao24=s.icao24).set(s.longitude)
        
        push_to_gateway(PUSHGATEWAY_URL, job='opensky', registry=registry)
    else:
        print("Fehler beim Abrufen der Flugdaten")

def main():
    while True:
        fetch_flight_data()
        time.sleep(900)  # Alle 15 Minuten aktualisieren

if __name__ == "__main__":
    main()

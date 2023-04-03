import requests
import gzip
import json
import io
from datetime import datetime
import os

import streamlit as st
from dotenv import load_dotenv
import pandas as pd

import folium
from streamlit_folium import folium_static


# Récupérer la liste des villes en France depuis l'API OpenWeatherMap
url = "http://bulk.openweathermap.org/sample/city.list.json.gz"
response = requests.get(url, stream=True)

if response.status_code == 200:
    # Lire les données compressées en mémoire
    content = gzip.GzipFile(fileobj=io.BytesIO(response.content)).read()

    # Décoder les données JSON
    cities = json.loads(content)

    # Extraire les noms des villes en France avec leur code pays
    fr_cities = [city['name'] for city in cities if city['country'] == 'FR']
else:
    print("Error downloading cities list")


# Récupérer les données météorologiques pour chaque ville en France depuis l'API OpenWeatherMap

load_dotenv() # Charge les variables d'environnement à partir du fichier .env
api_key = os.getenv("WEATHER_API_KEY")

# Créer une liste déroulante pour permettre à l'utilisateur de sélectionner une ville
selected_city = st.selectbox("Choisir une ville", options=fr_cities, index=0)

# Requête pour la ville sélectionnée
url = f"http://api.openweathermap.org/data/2.5/forecast?q={selected_city}&appid={api_key}"
response = requests.get(url)

# Vérifier que la requête s'est bien passée
if response.status_code == 200:
    data = json.loads(response.text)

    # Récupérer les prévisions pour les 5 prochains jours
    forecasts = data['list']

    # Créer une liste pour stocker les données de chaque prévision
    forecast_data = []

    # Boucler sur chaque prévision et ajouter les informations pertinentes à la liste
    for forecast in forecasts:
        dt_txt = forecast['dt_txt']
        temperature = forecast['main']['temp'] - 273.15
        humidity = forecast['main']['humidity']
        wind_speed = forecast['wind']['speed']
        weather_description = forecast['weather'][0]['description']

        # Ajouter les données de la prévision à la liste
        forecast_data.append((dt_txt, temperature, humidity, wind_speed, weather_description))

    # Afficher les données sous forme de tableau
    st.write("<h3>Prévisions pour les 5 prochains jours à {} :</h3>".format(selected_city), unsafe_allow_html=True)
    table = "<table><thead><tr><th style='text-align:left;'>Date et heure</th><th style='text-align:center;'>Température (°C)</th><th style='text-align:center;'>Humidité (%)</th><th style='text-align:center;'>Vitesse du vent (m/s)</th><th style='text-align:left;'>Description du temps</th></tr></thead><tbody>"
    for forecast in forecast_data:
        table += "<tr><td style='text-align:left;'>{}</td><td style='text-align:center;'>{:.2f}</td><td style='text-align:center;'>{}</td><td style='text-align:center;'>{}</td><td style='text-align:left;'>{}</td></tr>".format(forecast[0], forecast[1], forecast[2], forecast[3], forecast[4])
    table += "</tbody></table>"
    st.write(table, unsafe_allow_html=True)
else:
    st.write(f"Erreur : la requête a échoué avec le code d'état {response.status_code}")

    
# Créer une carte centrée sur la France
m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)


url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
cities = ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre", "Saint-Etienne", "Toulon", "Grenoble", "Dijon", "Nîmes", "Angers", "Villeurbanne"]

for city in cities:
    response = requests.get(url.format(city, api_key)).json()
    lat = response['coord']['lat']
    lon = response['coord']['lon']
    temp = round(response['main']['temp'] - 273.15, 1)
    name = response['name']
    desc = response['weather'][0]['description'].capitalize()
    popup_text = f"{name}<br>{desc}<br>Temperature: {temp} °C"
    folium.Marker(location=[lat, lon], tooltip=name, popup=popup_text).add_to(m)

# Afficher la carte
folium_static(m)


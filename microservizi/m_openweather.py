"""
Questo microservizio serve per gestire l'api di openweather,
interrogando il server sulle previsioni meteo
"""
import requests
api_url = "https://api.openweathermap.org/data/3.0/onecall"
params = {
    'appid': '241cf7e334517a031d31287144b10f1a',
    'exclude':'minutely',
    'lat': 0,
    'lon': 0,
    'units': 'metric'
}
#https://api.openweathermap.org/data/3.0/onecall?lat=33.44&lon=-94.04&exclude=hourly,daily&appid=241cf7e334517a031d31287144b10f1a

campi_da_rimuovere = ["feels_like", "dew_point","visibility","wind_deg","icon","id"]

def coords(city):
    #coordinate di siracusa
    lat = 37.075474
    lon = 15.286586
    value=[lat,lon]
    return value

def f(city):
    city_coords = coords(city)
    params['lat'] = city_coords[0]
    params['lon'] = city_coords[1]

    response = requests.get(api_url,params)
    
    return response.json()

# funzione per filtrare i messaggi raw ottenuti da openweather
def rimuovi_campi(json_data, campi_da_rimuovere):
    if isinstance(json_data, dict):
        for campo in campi_da_rimuovere:
            json_data.pop(campo, None)

        for chiave, valore in json_data.items():
            if isinstance(valore, (dict, list)):
                rimuovi_campi(valore, campi_da_rimuovere)
    elif isinstance(json_data, list):
        for elemento in json_data:
            if isinstance(elemento, (dict, list)):
                rimuovi_campi(elemento, campi_da_rimuovere)
    return json_data


# -----------------------------------------------------------
# I codici sottostanti sono test per verificare il corretto
# funzionamento delle funzioni sviluppate 
# -----------------------------------------------------------

if __init__ == '__main__':    
    debug_procedures() # solo per debug. Non sarà presente nella versione definitiva

def debug_procedures():
    json_response = f("Siracusa")
    print(json_response)
    rimuovi_campi(json_response,campi_da_rimuovere)
    print(json_response)

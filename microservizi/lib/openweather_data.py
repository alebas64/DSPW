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
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import config

def get_coordinates(city:str, state:str, country:str):
    api_url = f'https://api.api-ninjas.com/v1/geocoding?city={city}&country={country}'
    response = requests.get(api_url, headers={'X-Api-Key': config.api_key})

    if response.status_code == requests.codes.ok:
        coord_all = json.loads(response.text)
        coord_filtered = []

        for item in coord_all:
            if item['state'] == state:
                coord_filtered.append(item)

        num_elements = len(coord_filtered)

        if num_elements == 1:
            return coord_filtered[0]
        elif num_elements == 0:
            raise Exception(f'No city found for the given input ({city}, {state}, {country})')
        else:
            raise Exception(f'For the given input ({city}, {state}, {country}) there are {num_elements} different locations. Please give more precise values.')
    else:
        raise Exception('Error:', response.status_code, response.text)

def get_grid(latitude:float, longitude:float):
    api_url = f'https://api.weather.gov/points/{latitude},{longitude}'
    response = requests.get(api_url, headers={'User-Agent': config.user_agent})

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)['properties']
    else:
        raise Exception('Error:', response.status_code, response.text)

def get_current(api_url:str):
    response = requests.get(api_url, headers={'User-Agent': config.user_agent})

    if response.status_code == requests.codes.ok:
        stations = json.loads(response.text)['features']
    else:
        raise Exception('Error:', response.status_code, response.text)

    name = []
    temperature = []
    relativeHumidity = []
    windSpeed = []
    windChill = []

    for item in stations:
        station_url = item['id'] + '/observations/latest'
        reponse_station = requests.get(station_url, headers={'User-Agent': config.user_agent})

        if reponse_station.status_code == requests.codes.ok:
            station_data = json.loads(reponse_station.text)['properties']
        else:
            continue

        name.append(item['properties']['name'])
        temperature.append(station_data['temperature']['value'])
        relativeHumidity.append(station_data['relativeHumidity']['value'])
        windSpeed.append(station_data['windSpeed']['value'])
        windChill.append(station_data['windChill']['value'])

    df_current = pd.DataFrame()
    df_current['name'] = name
    df_current['temperature'] = temperature
    df_current['relativeHumidity'] = relativeHumidity
    df_current['windSpeed'] = windSpeed
    df_current['windChill'] = windChill

    return df_current

def get_forecast(api_url:str):
    response = requests.get(api_url, headers={'User-Agent': config.user_agent})

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)['properties']['periods']
    else:
        raise Exception('Error:', response.status_code, response.text)

if __name__ == "__main__":
    city = 'Boston'
    state = 'Massachusetts'
    country = 'US'

    coordinates = get_coordinates(city, state, country)

    grid = get_grid(round(coordinates.get('latitude'),4), round(coordinates.get('longitude'),4))

    #Current weather
    current = get_current(grid['observationStations'])

    pd.set_option('display.max_columns', None)
    print(current)

    #Forecast following 7 days
    forecast = get_forecast(grid['forecast'])

    name = []
    temp_daytime = []
    temp_night = []

    for item in forecast:
        if item['isDaytime']:
            name.append(item['name'])
            temp_daytime.append((item['temperature'] - 32) * 1.8)
        else:
            temp_night.append((item['temperature'] - 32) * 1.8)

    plt.plot(name, temp_daytime, label='Daytime', color='orange')
    plt.plot(name, temp_night, label='Night', color='blue')
    plt.title('Forecast next 7 days')
    plt.xlabel('Day')
    plt.ylabel('Temperature in C')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

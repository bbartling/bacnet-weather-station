import aiohttp
import asyncio
import math
from datetime import datetime

API_KEY = "6f1efece8acf334b0af1ec3538846065"
LAT = 38.6246
LON = -76.9391
API_URL = "https://api.openweathermap.org/data/2.5/weather"

def calculate_dew_point(temp_f, humidity):
    """Calculate dew point using Magnus formula."""
    temp_c = (temp_f - 32) * 5 / 9
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dew_point_c = (b * alpha) / (a - alpha)
    dew_point_f = (dew_point_c * 9 / 5) + 32
    return round(dew_point_f, 2)

async def fetch_weather(session):
    try:
        params = {
            'lat': LAT,
            'lon': LON,
            'appid': API_KEY,
            'units': 'imperial',
            'lang': 'en'
        }

        async with session.get(API_URL, params=params) as response:
            response.raise_for_status()  # Raise error for bad status
            data = await response.json()

            # Debug the full JSON response
            print("Full API Response:", data)

            # Extract data
            temperature = data['main'].get('temp', 'N/A')
            humidity = data['main'].get('humidity', 'N/A')

            # Calculate dew point
            dew_point = calculate_dew_point(temperature, humidity) if temperature != 'N/A' and humidity != 'N/A' else 'N/A'

            # Print results
            print(f"Time: {datetime.now()}")
            print(f"Temperature (°F): {temperature}")
            print(f"Humidity (%): {humidity}")
            print(f"Dew Point (°F): {dew_point}")
            print("-" * 40)

    except aiohttp.ClientResponseError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except aiohttp.ClientError as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e:
        print(f"General error: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            await fetch_weather(session)
            await asyncio.sleep(1200)  # 20 minutes interval

if __name__ == "__main__":
    asyncio.run(main())

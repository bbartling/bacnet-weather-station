import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject
from bacpypes3.local.binary import BinaryValueObject
from bacpypes3.debugging import bacpypes_debugging, ModuleLogger
import math
from microdot.asgi import Microdot
import json

from config import LAT, LON, API_URL, INTERVAL, UNITS, LANG

# Debugging
_debug = 0
_log = ModuleLogger(globals())

try:
    load_dotenv()
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        raise ValueError("Missing OPENWEATHER_API_KEY in .env or environment variables.")

except Exception as e:
    _log.error(f"Failed to load API key: {e}")
    sys.exit(1)

# Microdot app for REST endpoint
api_app = Microdot()
bacnet_app = None


def calculate_wet_bulb(temp_f, humidity):
    temp_c = (temp_f - 32) * 5 / 9
    rh = humidity
    wet_bulb_c = (
        temp_c * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(temp_c + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * rh**1.5 * math.atan(0.023101 * rh)
        - 4.686035
    )
    wet_bulb_f = (wet_bulb_c * 9 / 5) + 32
    return round(wet_bulb_f, 2)


def calculate_dew_point(temp_f, humidity):
    temp_c = (temp_f - 32) * 5 / 9
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dew_point_c = (b * alpha) / (a - alpha)
    dew_point_f = (dew_point_c * 9 / 5) + 32
    return round(dew_point_f, 2)


@bacpypes_debugging
class SampleApplication:
    def __init__(self, args):
        if _debug:
            _log.debug("Initializing SampleApplication")

        self.app = Application.from_args(args)

        self.current_data = {
            "temperature": 0.0,
            "humidity": 0.0,
            "dew_point": 0.0,
            "wet_bulb": 0.0,
            "error": "inactive",
            "timestamp": None,
            "lat": LAT,
            "lon": LON,
        }

        self.temp_av = AnalogValueObject(
            objectIdentifier=("analogValue", 1),
            objectName="oa-dry-bulb",
            presentValue=0.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            units="degreesFahrenheit",
            description="Web Weather Outside Air Dry Bulb Temp",
        )

        self.humidity_av = AnalogValueObject(
            objectIdentifier=("analogValue", 2),
            objectName="oa-humidity",
            presentValue=0.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            units="percent",
            description="Web Weather Outside Air Humidity",
        )

        self.dew_point_av = AnalogValueObject(
            objectIdentifier=("analogValue", 3),
            objectName="oa-dew-point",
            presentValue=0.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            units="degreesFahrenheit",
            description="Web Weather Outside Air Dew Point Temp",
        )

        self.wet_bulb_av = AnalogValueObject(
            objectIdentifier=("analogValue", 4),
            objectName="oa-wet-bulb",
            presentValue=0.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            units="degreesFahrenheit",
            description="Web Weather Outside Air Wet Bulb Temp",
        )

        self.error_bv = BinaryValueObject(
            objectIdentifier=("binaryValue", 1),
            objectName="web-api-error",
            description="Web Weather Data Request Error",
            presentValue="inactive",
            statusFlags=[0, 0, 0, 0],
        )

        for obj in [
            self.temp_av,
            self.humidity_av,
            self.dew_point_av,
            self.wet_bulb_av,
            self.error_bv,
        ]:
            self.app.add_object(obj)

        _log.info("BACnet Weather Objects initialized.")
        asyncio.create_task(self.update_values())

    async def fetch_weather(self, session):
        params = {
            "lat": LAT,
            "lon": LON,
            "appid": API_KEY,
            "units": UNITS,
            "lang": LANG,
        }

        async with session.get(API_URL, params=params) as response:
            if response.status == 401:
                raise ValueError("Unauthorized: Invalid API key for OpenWeatherMap.")
            response.raise_for_status()
            return await response.json()

    async def update_values(self):
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    data = await self.fetch_weather(session)

                    temperature = data["main"].get("temp", 0.0)
                    humidity = data["main"].get("humidity", 0.0)
                    dew_point = calculate_dew_point(temperature, humidity)
                    wet_bulb = calculate_wet_bulb(temperature, humidity)

                    self.temp_av.presentValue = temperature
                    self.humidity_av.presentValue = humidity
                    self.dew_point_av.presentValue = dew_point
                    self.wet_bulb_av.presentValue = wet_bulb
                    self.error_bv.presentValue = "inactive"

                    self.current_data.update(
                        {
                            "temperature": temperature,
                            "humidity": humidity,
                            "dew_point": dew_point,
                            "wet_bulb": wet_bulb,
                            "error": "inactive",
                            "timestamp": datetime.now().isoformat(),
                            "lat": LAT,
                            "lon": LON,
                        }
                    )

                    if _debug:
                        _log.debug(f"Updated Data: {self.current_data}")

                except Exception as e:
                    _log.error(f"Error fetching or updating weather data: {e}")
                    self.error_bv.presentValue = "active"
                    self.current_data["error"] = str(e)

                await asyncio.sleep(INTERVAL)


@api_app.get("/status")
async def status(request):
    if bacnet_app is None:
        return {
            "error": "BACnet app not initialized. Check API key or startup error."
        }, 500
    return bacnet_app.current_data


@api_app.get("/")
async def hello(request):
    if bacnet_app is None:
        return {
            "error": "BACnet app not initialized. Check API key or startup error."
        }, 500
    return {"message": "Hello from Microdot! See the /status route for weather data!"}


async def main():
    global _debug, bacnet_app

    parser = SimpleArgumentParser()
    args = parser.parse_args()

    if args.debug:
        _debug = 1
        _log.set_level("DEBUG")
        _log.debug("Debug mode enabled")

    try:
        bacnet_app = SampleApplication(args)
    except Exception as e:
        _log.error(f"BACnet app failed to initialize: {e}")
        return

    asyncio.create_task(api_app.start_server(host="0.0.0.0", port=8080))
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _log.info("Keyboard interrupt received, shutting down.")
        sys.exit(0)
    except RuntimeError as e:
        _log.error(f"Runtime error: {e}")
        sys.exit(1)

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject
from bacpypes3.local.binary import BinaryValueObject
from bacpypes3.debugging import bacpypes_debugging, ModuleLogger
import math
from config import LAT, LON, API_URL, INTERVAL

# Debugging (Follow BACpypes3 standard)
_debug = 0
_log = ModuleLogger(globals())

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


def calculate_dew_point(temp_f, humidity):
    """Calculate dew point using Magnus formula."""
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
        """Initialize the BACnet application and objects."""

        if _debug:
            _log.debug("Initializing SampleApplication")

        # Initialize the BACnet Application
        self.app = Application.from_args(args)

        # Define BACnet objects
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

        self.error_bv = BinaryValueObject(
            objectIdentifier=("binaryValue", 1),
            objectName="web-api-error",
            description="Web Weather Data Request Error",
            presentValue="inactive",
            statusFlags=[0, 0, 0, 0],
        )

        # Add objects to BACnet app
        for obj in [self.temp_av, self.humidity_av, self.dew_point_av, self.error_bv]:
            self.app.add_object(obj)

        _log.info("BACnet Weather Objects initialized.")

        # Start periodic value updates
        asyncio.create_task(self.update_values())

    async def fetch_weather(self, session):
        params = {
            "lat": LAT,
            "lon": LON,
            "appid": API_KEY,
            "units": "imperial",
            "lang": "en",
        }

        async with session.get(API_URL, params=params) as response:
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

                    # Update BACnet objects
                    self.temp_av.presentValue = temperature
                    self.humidity_av.presentValue = humidity
                    self.dew_point_av.presentValue = dew_point
                    self.error_bv.presentValue = "inactive"

                    if _debug:
                        _log.debug(f"Updated Dry-Bulb Temp: {temperature}")
                        _log.debug(f"Updated Humidity: {humidity}")
                        _log.debug(f"Updated Dew Point: {dew_point}")

                except Exception as e:
                    _log.error(f"Error fetching or updating weather data: {e}")
                    self.error_bv.presentValue = "active"

                await asyncio.sleep(INTERVAL)


async def main():
    global _debug

    parser = SimpleArgumentParser()
    args = parser.parse_args()

    if args.debug:
        _debug = 1
        _log.set_level("DEBUG")
        _log.debug("Debug mode enabled")

    if _debug:
        _log.debug(f"Parsed arguments: {args}")

    app = SampleApplication(args)

    await asyncio.Future()  # Keep running


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _log.info("Keyboard interrupt received, shutting down.")
        sys.exit(0)

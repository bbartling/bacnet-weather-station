# 🚀 **BACnet Weather Station Setup Guide**

This is a Python-based BACnet app optimized for embedded systems to provide BAS web weather data using OpenWeatherMap API.

---

## 🛠️ **Prerequisites**
- Raspberry Pi with Armbian Minimal / IoT image
- Python 3, `pip`, and virtual environment support
- SSH access

---

📖 **Skip right to the Docker Documentation:**  
[🐳 Docker README](https://github.com/bbartling/bacnet-web-weather-linux/blob/develop/docker_readme.md)

---


### 🛠️ **Clone the Repository & Set Up Python Environment**  

```bash
git clone https://github.com/your-repo/bacnet-weather-station.git
cd bacnet-weather-station
```

#### 🐍 **Create & Activate a Virtual Environment**
```bash
python3 -m venv env
source env/bin/activate
```

#### 📦 **Install Required Dependencies**
```bash
pip install -r requirements.txt
```

🔹 *This ensures the BACnet weather app runs in an isolated environment with all necessary dependencies installed.*

#### 🐳 **Prefer Docker?**  
If you'd rather run this in a container, check out the **[Docker Setup Guide](https://github.com/bbartling/bacnet-web-weather-linux/blob/develop/docker_readme.md)**. 🚀

---

### ⚙️ **Step 7: Create `.env` File for API Key**

```bash
nano .env
```

Add the following:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

### ⚙️ **Step 7.1: Configure `config.py` for API Settings**  

After setting up your `.env` file, you need to configure the **weather API settings** inside `config.py`.  

#### ✏️ **Edit the Configuration File**
```bash
nano config.py
```

#### 🛠 **Update the Following Variables**
Make sure the following settings are set inside `config.py`:

```python
LAT = 38.6246
LON = -76.9391
API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Weather Data Update interval in seconds (20 minutes)
INTERVAL = 1200  

# OpenWeather API Configurations
UNITS = "imperial"  # Options: 'standard', 'metric', 'imperial'
LANG = "en"         # Language code for API responses
```

#### 🔍 **What Each Setting Does**
- `LAT` / `LON` → Set the **latitude** and **longitude** for your weather data.  
- `API_URL` → The **endpoint** for fetching weather data from OpenWeather.  
- `INTERVAL` → How often (in **seconds**) the app fetches weather data (default: **20 minutes**).  
- `UNITS` → Choose between `'standard'`, `'metric'`, or `'imperial'` for temperature units.  
- `LANG` → Set the **language** for API responses (e.g., `"en"` for English).  

After updating, **save and exit**:  
- **For Nano**: Press `CTRL + X`, then `Y`, then `Enter`.  

---


### ⚙️ **Step 8: Running the BACnet Weather App**

```bash
python main.py --name BacnetWeatherStation --instance 3456789 --debug
```

* If you need to assign a static IP or unique port number, **bacpypes3** also supports assigning hard-coded [addresses](https://bacpypes3.readthedocs.io/en/stable/gettingstarted/addresses.html) which would be useful if your BACnet network is running on a unique port number.

```bash
python main.py --name BacnetWeatherStation --address 192.168.0.21/24:47809 --instance 3456789 --debug
```

---

### 🖼️ **Step 9: BACnet Weather Station Screenshot**

Here's a sample screenshot of the BACnet Weather Station in action:

[![BACnet Weather Station Screenshot](https://github.com/bbartling/bacnet-weather-station/blob/develop/images/snip.png)](https://github.com/bbartling/bacnet-weather-station/blob/develop/images/snip.png)

---


### ⚡ **Step 10: Accessing the Microdot REST API**
The BACnet Weather Station also provides a **REST API endpoint** using **Microdot**.  
This allows external applications to retrieve **real-time weather data** in JSON format.

#### 🔌 **API Endpoint**
```http
GET http://<your-device-ip>:8080/status
```

#### 📡 **Example Request**
Change `localhost` to the IP address of your Pi...
```bash
curl http://localhost:8080/status
```

#### 🔍 **Example JSON Response**
```json
{
  "temperature": 40.78,
  "humidity": 32,
  "dew_point": 13.23,
  "error": "inactive",
  "wet_bulb": 31.13,
  "timestamp": "2025-03-22T18:49:14.725541",
  "lat": 43.555,
  "lon": -89.927
}
```

#### 🛠️ **How It Works**
- The API continuously updates weather data from OpenWeather.
- You can **fetch current temperature, humidity, and dew point**.
- The `error` field indicates if there were **issues fetching the data**.
- The `timestamp` is updated every **INTERVAL** (default: 20 minutes).

---

### ✅ **You're All Set!**
The BACnet Weather Station now **broadcasts data** over BACnet **and** provides an easy-to-use REST API! 🚀🔥



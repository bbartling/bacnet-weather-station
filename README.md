# 🚀 **BACnet Weather Station Setup Guide**

This is a Python-based BACnet app optimized for embedded systems to provide BAS web weather data using OpenWeatherMap API.

---

## 🛠️ **Prerequisites**
- Raspberry Pi with Armbian Minimal / IoT image
- Python 3, `pip`, and virtual environment support
- SSH access

---

## 🔄 **Step 1: Download and Install Armbian**

1. Download the latest Armbian Minimal / IoT image:
   - [Armbian Raspberry Pi 4B](https://www.armbian.com/rpi4b/)

2. Burn the image to an SD card using Raspberry Pi Imager.

---

## ⚙️ **Step 2: Initial Setup**

1. Insert the SD card into the Raspberry Pi and power it up.
2. Connect to the Pi via SSH:

```bash
ssh root@192.168.1.224
```

- Default username: `root`
- Default password: `1234`

3. Complete the Armbian setup and create a new user (e.g., `ben`).

---

### 📦 **Step 3: Install Required Packages**

```bash
sudo apt update
sudo apt install vim git python3 python3-venv python3-pip -y
```

---

### 🔐 **Step 4: Setup Secure SSH Access**

1. On your Windows machine, generate an SSH key:

```powershell
ssh-keygen -t rsa -b 4096 -C "ben.bartling@gmail.com"
```

2. Retrieve and copy the public key:

```powershell
Get-Content ~\.ssh\id_rsa.pub
```

3. On the Raspberry Pi, set up the SSH keys:

```bash
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
```

4. Paste the public key, save, and set permissions:

```bash
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

5. Disable root SSH login:

```bash
sudo nano /etc/ssh/sshd_config
```
- Set `PermitRootLogin no`.
- Restart SSH:

```bash
sudo systemctl restart sshd
```

---

### 🧪 **Step 5: Test SSH Login**

```bash
ssh ben@192.168.1.224
```

Ensure root login is disabled by attempting:

```bash
ssh root@192.168.1.224
```

You should receive a "permission denied" message.

---

### 🧰 **Step 6: Clone the Repo and Setup Python Environment**

```bash
git clone https://github.com/your-repo/bacnet-weather-station.git
cd bacnet-weather-station
python3 -m venv env
source env/bin/activate
pip install bacpypes3 ifaddr aiohttp python-dotenv
```

---

### ⚙️ **Step 7: Create `.env` File for API Key**

```bash
nano .env
```

Add the following:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

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

### 🔄 **Step 9: Log Rotation (Optional)**

1. Install `logrotate`:

```bash
sudo apt install logrotate
```

2. Create a logrotate configuration for the app logs if needed.

---

## ✅ **You're All Set!**

The BACnet Weather Station app should now be running and providing BACnet objects with real-time weather data!


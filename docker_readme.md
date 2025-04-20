# 🐳 **Docker Cheat Sheet for BACnet Weather Station**

This guide covers the essential Docker commands to manage the **BACnet Weather Station** container on your Raspberry Pi. Modify Docker run command as needed with a text editor if there is a requirement to run BACnet app on a different port number.

---

## 🚀 **Build the Docker Image**

Install Docker if need be

```bash
# Install Docker
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

Build container

```bash
docker build -t bacnet-weather-station .
```

---

## ⚙️ **Run the Docker Container**

```bash
docker run -d \
  --name bacnet-weather-station \
  --env-file .env \
  --network host \
  --restart unless-stopped \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  bacnet-weather-station
```

### **Key Flags Explained:**
- `-d`: Run in detached mode.
- `--env-file .env`: Load environment variables.
- `--network host`: Required for BACnet UDP communication.
- `--restart unless-stopped`: Automatically restart after reboot or power loss.
- `--log-driver json-file`: Enables basic logging.
- `--log-opt max-size=10m`: Rotate log files after reaching 10MB.
- `--log-opt max-file=3`: Keep only the last 3 log files.

---

## 🔄 **Check if the Container Restarts Automatically**

After reboot:

```bash
docker ps
```

---

## 🛠️ **Basic Docker Commands**

| **Action**             | **Command**                                        |
|------------------------|----------------------------------------------------|
| Start container        | `docker start bacnet-weather-station`              |
| Stop container         | `docker stop bacnet-weather-station`               |
| Restart container      | `docker restart bacnet-weather-station`            |
| View logs              | `docker logs -f bacnet-weather-station`            |
| Remove container       | `docker rm bacnet-weather-station`                 |
| Remove image           | `docker rmi bacnet-weather-station`                |
| List running containers| `docker ps`                                        |
| List all containers    | `docker ps -a`                                     |
| Inspect container      | `docker inspect bacnet-weather-station`            |

---

## 📦 **Check Docker Restart Policy**

```bash
docker inspect -f "{{ .HostConfig.RestartPolicy.Name }}" bacnet-weather-station
```

**Expected Output:**
```
unless-stopped
```

---

## 🛡️ **Enable Docker Service on Boot**

```bash
sudo systemctl enable docker
```

---

## 🗑️ **Clean Up Unused Resources**

Remove stopped containers, dangling images, and unused volumes:

```bash
docker system prune -f
```

---

## 🔄 **Rebuild the Docker Image**

If you make changes to the code or dependencies:

```bash
docker build --no-cache -t bacnet-weather-station .
```

---

## 🛠 ** Modifying the Py file **
Stopping, removing, rebuilding, and running the app again...

```bash
docker build -t bacnet-weather-station .
docker stop bacnet-weather-station
docker rm bacnet-weather-station
docker run -d \
  --name bacnet-weather-station \
  --env-file .env \
  --network host \
  --restart unless-stopped \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  bacnet-weather-station
```

Then track logs
```bash
docker logs -f bacnet-weather-station
```


### ✅ **All Set!**

This cheat sheet will help you manage Docker efficiently for your BACnet Weather Station on the Raspberry Pi. 🚀

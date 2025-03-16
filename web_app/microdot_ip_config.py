from microdot.asgi import Microdot, Response
from microdot import Request
import subprocess
import logging
import os
import re
from pathlib import Path
from datetime import datetime

from network_form import HTML_FORM

app = Microdot()

# Setup Logging
LOG_FILE = '/var/log/web_app/app.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Netplan configuration file path
NETPLAN_CONFIG = Path("/etc/netplan/01-netcfg.yaml")


def log_and_print(message, level="info"):
    print(message)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        log_and_print(f"Error executing command '{command}': {e.stderr.decode().strip()}", level="error")
        return None

def get_active_interface():
    output = run_command("ip -o -4 addr show up")
    log_and_print(f"Raw command output: {output}", level="debug")

    if output:
        for line in output.splitlines():
            line = line.replace("\\", "").strip()
            log_and_print(f"Processing cleaned line: {line}", level="debug")
            match = re.search(r'^\d+: (\w[\w\d:.-]+).* inet (\d+\.\d+\.\d+\.\d+)', line)
            if match and match.group(1) != "lo":
                interface = match.group(1)
                log_and_print(f"Detected interface: {interface}", level="info")
                return interface
    
    log_and_print("No active interface detected.", level="error")
    return None

def write_netplan_config(content):
    NETPLAN_CONFIG.write_text(content)
    log_and_print(f"Configuration written to {NETPLAN_CONFIG}")

def apply_netplan():
    """Apply Netplan configuration."""
    result = run_command("sudo /usr/sbin/netplan apply")
    if result is not None:
        log_and_print("Netplan configuration applied successfully.")
    else:
        log_and_print("Failed to apply Netplan configuration.", level="error")


def set_static_ip(interface, ip_address, netmask, gateway):
    static_config = f"""
network:
  version: 2
  ethernets:
    {interface}:
      dhcp4: no
      addresses:
        - {ip_address}/{netmask}
      gateway4: {gateway}
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
    """
    write_netplan_config(static_config)
    apply_netplan()
    log_and_print(f"Static IP {ip_address} applied to {interface}.")

def set_dhcp(interface):
    dhcp_config = f"""
network:
  version: 2
  ethernets:
    {interface}:
      dhcp4: true
    """
    write_netplan_config(dhcp_config)
    apply_netplan()
    log_and_print(f"DHCP applied to {interface}.")

@app.get('/')
async def index(request):
    logging.info("Accessed Network Config Form")
    return Response(body=HTML_FORM, headers={'Content-Type': 'text/html'})

@app.post('/network/config')
async def configure_network(request: Request):
    try:
        form = request.form
        mode = form.get('mode')

        interface = get_active_interface()
        if not interface:
            return {'error': 'No active network interface detected.'}, 400

        if mode == 'dhcp':
            logging.info("Configuring network to DHCP mode")
            set_dhcp(interface)
            return {'status': 'DHCP configured successfully'}

        elif mode == 'static':
            ip_address = form.get('ip_address')
            netmask = form.get('netmask')
            gateway = form.get('gateway')

            if not all([ip_address, netmask, gateway]):
                logging.error("Missing static IP configuration fields.")
                return {'error': 'Missing static IP configuration fields.'}, 400

            logging.info(f"Configuring network to static IP: {ip_address}")
            set_static_ip(interface, ip_address, netmask, gateway)
            return {'status': f'Static IP {ip_address} configured successfully'}

        else:
            logging.error("Invalid mode selected.")
            return {'error': 'Invalid mode selected.'}, 400

    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        return {'error': 'Internal Server Error'}, 500

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("microdot_ip_config:app", host="0.0.0.0", port=8000, reload=True)
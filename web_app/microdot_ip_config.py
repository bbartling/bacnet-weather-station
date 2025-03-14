from microdot.asgi import Microdot, Response
from microdot import Request
import subprocess
import logging
import re
import os

from network_form import HTML_FORM

app = Microdot()

# Setup Logging
logging.basicConfig(
    filename='/var/log/web_app/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def get_ethernet_interface() -> str:
    """Automatically detect the active Ethernet interface."""
    try:
        result = subprocess.run(['ip', '-o', 'link'], stdout=subprocess.PIPE, text=True)
        interfaces = re.findall(r'^\d+: (\w+):.*state UP', result.stdout, re.MULTILINE)
        for interface in interfaces:
            if not interface.startswith('lo'):  # Exclude loopback
                logging.info(f"Detected Ethernet interface: {interface}")
                return interface
    except Exception as e:
        logging.error(f"Failed to detect network interface: {e}")
    return "eth0"  # Fallback if detection fails

INTERFACE_NAME = get_ethernet_interface()
NETWORK_CONFIG_FILE = f"/etc/systemd/network/10-static-{INTERFACE_NAME}.network"

def generate_static_ip_config(ip_address: str, netmask: str, gateway: str) -> str:
    return f"""
[Match]
Name={INTERFACE_NAME}

[Network]
Address={ip_address}/{netmask}
Gateway={gateway}
DNS=8.8.8.8 8.8.4.4
"""

def generate_dhcp_config() -> str:
    return f"""
[Match]
Name={INTERFACE_NAME}

[Network]
DHCP=yes
"""

def is_valid_ip(address: str) -> bool:
    """Validate IPv4 address."""
    pattern = r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'
    if re.match(pattern, address):
        return all(0 <= int(octet) <= 255 for octet in address.split('.'))
    return False

def is_currently_dhcp() -> bool:
    """Check if the current config is set to DHCP."""
    if os.path.exists(NETWORK_CONFIG_FILE):
        with open(NETWORK_CONFIG_FILE) as f:
            return 'DHCP=yes' in f.read()
    return True  # Assume DHCP if no config file

@app.get('/')
async def index(request):
    logging.info("Accessed Network Config Form")
    return Response(body=HTML_FORM, headers={'Content-Type': 'text/html'})

@app.post('/network/config')
async def configure_network(request: Request):
    try:
        form = await request.form()
        mode = form.get('mode')

        # Check current configuration
        current_dhcp = is_currently_dhcp()

        # Avoid redundant configuration changes
        if mode == 'dhcp' and current_dhcp:
            logging.info("Already in DHCP mode. No changes made.")
            return {'status': 'already configured'}

        if mode == 'static':
            ip_address = form.get('ip_address')
            netmask = form.get('netmask')
            gateway = form.get('gateway')

            if not all([ip_address, netmask, gateway]):
                logging.error("Missing static IP configuration fields.")
                return {'error': 'Missing static IP configuration fields.'}, 400

            if not all([is_valid_ip(ip_address), is_valid_ip(netmask), is_valid_ip(gateway)]):
                logging.error("Invalid IP address format detected.")
                return {'error': 'Invalid IP address format. Please enter valid IPv4 addresses.'}, 400

            config_content = generate_static_ip_config(ip_address, netmask, gateway)
            logging.info(f"Configuring network to static IP: {ip_address}")

        elif mode == 'dhcp':
            config_content = generate_dhcp_config()
            logging.info("Configuring network to DHCP mode")

        else:
            logging.error("Invalid mode selected.")
            return {'error': 'Invalid mode selected.'}, 400

        # Write the configuration
        with open(NETWORK_CONFIG_FILE, 'w') as f:
            f.write(config_content)

        subprocess.run(["sudo", "systemctl", "daemon-reexec"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "systemd-networkd"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "bacnet_app.service"], check=True)

        logging.info("Network and BACnet service restarted successfully.")
        return {'status': 'success'}

    except subprocess.CalledProcessError as e:
        logging.error(f"System command failed: {e}")
        return {'error': 'System command failed.'}, 500

    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        return {'error': 'Internal Server Error'}, 500

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("microdot_ip_config:app", host="0.0.0.0", port=8000, reload=True)

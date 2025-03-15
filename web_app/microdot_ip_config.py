from microdot.asgi import Microdot, Response
from microdot import Request
import subprocess
import logging
import os

from network_form import HTML_FORM

app = Microdot()

# Setup Logging
logging.basicConfig(
    filename='/var/log/web_app/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Paths to Bash Scripts
SET_DHCP_SCRIPT = '/opt/web_app/set_dhcp.sh'
SET_STATIC_SCRIPT = '/opt/web_app/set_static.sh'

def is_currently_dhcp(config_file: str) -> bool:
    """Check if the current network configuration is set to DHCP."""
    if os.path.exists(config_file):
        with open(config_file) as f:
            return 'DHCP=yes' in f.read()
    return True  # Assume DHCP if no config file exists


@app.get('/')
async def index(request):
    logging.info("Accessed Network Config Form")
    return Response(body=HTML_FORM, headers={'Content-Type': 'text/html'})

@app.post('/network/config')
async def configure_network(request: Request):
    try:
        form = request.form
        mode = form.get('mode')

        # Path to current network config file for DHCP check
        INTERFACE_NAME = 'enxb827ebef5eec'  # Or dynamically detect if needed
        DHCP_CONFIG_FILE = f"/etc/systemd/network/10-dhcp-{INTERFACE_NAME}.network"

        if mode == 'dhcp':
            if is_currently_dhcp(DHCP_CONFIG_FILE):
                logging.info("Already in DHCP mode. No changes made.")
                return {'status': 'DHCP is already configured'}

            logging.info("Configuring network to DHCP mode")
            subprocess.run(['sudo', SET_DHCP_SCRIPT], check=True)
            return {'status': 'DHCP configured successfully'}

        elif mode == 'static':
            ip_address = form.get('ip_address')
            netmask = form.get('netmask')
            gateway = form.get('gateway')

            if not all([ip_address, netmask, gateway]):
                logging.error("Missing static IP configuration fields.")
                return {'error': 'Missing static IP configuration fields.'}, 400

            logging.info(f"Configuring network to static IP: {ip_address}")
            subprocess.run(['sudo', SET_STATIC_SCRIPT, ip_address, netmask, gateway], check=True)
            return {'status': f'Static IP {ip_address} configured successfully'}

        else:
            logging.error("Invalid mode selected.")
            return {'error': 'Invalid mode selected.'}, 400

    except subprocess.CalledProcessError as e:
        logging.error(f"System command failed: {e}")
        return {'error': 'System command failed.'}, 500

    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        return {'error': 'Internal Server Error'}, 500



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("microdot_ip_config:app", host="0.0.0.0", port=8000, reload=True)

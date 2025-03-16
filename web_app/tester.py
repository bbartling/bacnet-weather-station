import subprocess
import time
from pathlib import Path
import re
import logging
from datetime import datetime

# Configure Logging
LOG_FILE = '/var/log/netplan/netplan_ip_change.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Static IP configuration
STATIC_IP = "192.168.0.190"
NETMASK = "24"
GATEWAY = "192.168.0.1"

# Path to the Netplan configuration file
NETPLAN_CONFIG = Path("/etc/netplan/01-netcfg.yaml")

# Retry settings
RETRY_COUNT = 5
RETRY_DELAY = 3  # seconds

def log_and_print(message, level="info"):
    """Helper function to log and print messages."""
    print(message)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)

def run_command(command):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        log_and_print(f"Error executing command '{command}': {e.stderr.decode().strip()}", level="error")
        return None

def get_active_interface():
    """Auto-detect the active network interface (ignoring loopback)."""
    for attempt in range(RETRY_COUNT):
        output = run_command("ip -o -4 addr show up")
        log_and_print(f"Attempt {attempt+1}: Raw command output: {output}", level="debug")

        if output:
            for line in output.splitlines():
                line = line.replace("\\", "").strip()
                log_and_print(f"Processing cleaned line: {line}", level="debug")
                
                match = re.search(r'^\d+: (\w[\w\d:.-]+).* inet (\d+\.\d+\.\d+\.\d+)', line)
                if match and match.group(1) != "lo":
                    interface = match.group(1)
                    ip_address = match.group(2)
                    log_and_print(f"Detected interface: {interface} with IP: {ip_address}", level="info")
                    return interface

        log_and_print(f"No active interface detected. Retrying in {RETRY_DELAY} seconds...", level="warning")
        time.sleep(RETRY_DELAY)

    log_and_print("Failed to detect an active network interface after retries.", level="error")
    return None

def write_netplan_config(content):
    """Write configuration content to the Netplan file."""
    NETPLAN_CONFIG.write_text(content)
    log_and_print(f"Configuration written to {NETPLAN_CONFIG}")

def apply_netplan():
    """Apply Netplan configuration."""
    result = run_command("netplan apply")
    if result is not None:
        log_and_print("Netplan configuration applied successfully.")
    else:
        log_and_print("Failed to apply Netplan configuration.", level="error")

def set_static_ip(interface):
    """Set static IP configuration."""
    static_config = f"""
network:
  version: 2
  ethernets:
    {interface}:
      dhcp4: no
      addresses:
        - {STATIC_IP}/{NETMASK}
      gateway4: {GATEWAY}
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
    """
    write_netplan_config(static_config)
    apply_netplan()
    log_and_print(f"Static IP {STATIC_IP} applied to {interface}.")

def set_dhcp(interface):
    """Set DHCP configuration."""
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

def main():
    start_time = datetime.now()
    log_and_print(f"Script starting at time {start_time} !!!", level="info")

    interface = get_active_interface()
    if not interface:
        log_and_print("No network interface found. Exiting.", level="error")
        return

    log_and_print("Switching to static IP...")
    set_static_ip(interface)

    # Wait for 60 seconds
    time.sleep(60)

    log_and_print("Switching back to DHCP...")
    set_dhcp(interface)

    # Wait for DHCP to establish and detect again
    time.sleep(60)

    # Re-check if the interface is up
    if not get_active_interface():
        log_and_print("No interface detected after switching to DHCP. Manual intervention may be required.", level="error")

    end_time = datetime.now()
    log_and_print(f"Script ending at time {end_time} !!!", level="info")

if __name__ == "__main__":
    main()

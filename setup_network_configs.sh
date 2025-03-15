#!/bin/bash

# Detect the active Ethernet interface (not lo or wlan0)
INTERFACE=$(ip link show | awk -F: '/^[0-9]+: e/{print $2}' | head -n 1 | tr -d ' ')

if [ -z "$INTERFACE" ]; then
    echo "❌ No active Ethernet interface detected."
    exit 1
fi

echo "✅ Detected interface: $INTERFACE"

# Define directories and file paths
NETWORK_DIR="/etc/systemd/network"
NETPLAN_DIR="/etc/netplan"
NETPLAN_BACKUP_DIR="/etc/netplan/backup"
DHCP_FILE="$NETWORK_DIR/10-dhcp-$INTERFACE.network"
STATIC_FILE="$NETWORK_DIR/10-static-$INTERFACE.network"

# Create necessary directories
sudo mkdir -p "$NETWORK_DIR"
sudo mkdir -p "$NETPLAN_BACKUP_DIR"

# Backup existing Netplan configs
if ls "$NETPLAN_DIR"/*.yaml 1> /dev/null 2>&1; then
    sudo mv "$NETPLAN_DIR"/*.yaml "$NETPLAN_BACKUP_DIR"/
    echo "✅ Netplan configuration files moved to backup: $NETPLAN_BACKUP_DIR"
else
    echo "ℹ️ No Netplan configuration files found to backup."
fi

# Create DHCP configuration file
sudo tee "$DHCP_FILE" > /dev/null <<EOL
[Match]
Name=$INTERFACE

[Network]
DHCP=yes
EOL

# Create Static configuration file with placeholders
sudo tee "$STATIC_FILE" > /dev/null <<EOL
[Match]
Name=$INTERFACE

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8 8.8.4.4
EOL

# Disable Static config by default
sudo mv "$STATIC_FILE" "$STATIC_FILE.disabled"

# Apply Netplan changes if still present (safe check)
if command -v netplan &> /dev/null; then
    sudo netplan apply || echo "ℹ️ Netplan apply failed, but it's likely because it's now disabled."
fi

# Restart systemd-networkd to apply DHCP config
sudo systemctl daemon-reexec
sudo systemctl restart systemd-networkd

# Wait for DHCP to assign an IP and check
sleep 5
CURRENT_IP=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
if [ -n "$CURRENT_IP" ]; then
    echo "✅ Interface $INTERFACE is now using DHCP with IP: $CURRENT_IP"
else
    echo "⚠️ Warning: DHCP may not have assigned an IP yet."
fi

echo "✅ Network configuration files created for interface: $INTERFACE"
echo "   - DHCP Config: $DHCP_FILE"
echo "   - Static Config (Disabled): $STATIC_FILE.disabled"

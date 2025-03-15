#!/bin/bash

# Detect the active Ethernet interface
INTERFACE=$(ip link show | awk -F: '/^[0-9]+: e/{print $2}' | head -n 1 | tr -d ' ')

if [ -z "$INTERFACE" ]; then
    echo "No active Ethernet interface detected."
    exit 1
fi

# Create the DHCP configuration file
sudo tee "/etc/systemd/network/10-dhcp-$INTERFACE.network" > /dev/null <<EOL
[Match]
Name=$INTERFACE

[Network]
DHCP=yes
EOL

# Remove any static configuration
sudo rm -f "/etc/systemd/network/10-static-$INTERFACE.network"

# Reload and restart systemd-networkd
sudo systemctl daemon-reexec
sudo systemctl restart systemd-networkd
sudo systemctl restart bacnet_app.service

echo "✅ DHCP configured for $INTERFACE"

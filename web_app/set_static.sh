#!/bin/bash

# Input Variables
IP_ADDRESS=$1
NETMASK=$2
GATEWAY=$3

# sudo ./set_static.sh <IP_ADDRESS> <NETMASK> <GATEWAY>
# sudo ./set_static.sh 192.168.1.253 24 192.168.1.1


# Detect the active Ethernet interface
INTERFACE=$(ip link show | awk -F: '/^[0-9]+: e/{print $2}' | head -n 1 | tr -d ' ')

if [ -z "$INTERFACE" ]; then
    echo "No active Ethernet interface detected."
    exit 1
fi

if [ -z "$IP_ADDRESS" ] || [ -z "$NETMASK" ] || [ -z "$GATEWAY" ]; then
    echo "Usage: ./set_static.sh <IP_ADDRESS> <NETMASK> <GATEWAY>"
    exit 1
fi

# Create the static configuration file
sudo tee "/etc/systemd/network/10-static-$INTERFACE.network" > /dev/null <<EOL
[Match]
Name=$INTERFACE

[Network]
Address=$IP_ADDRESS/$NETMASK
Gateway=$GATEWAY
DNS=8.8.8.8 8.8.4.4
EOL

# Remove any DHCP configuration
sudo rm -f "/etc/systemd/network/10-dhcp-$INTERFACE.network"

# Reload and restart systemd-networkd
sudo systemctl daemon-reexec
sudo systemctl restart systemd-networkd
sudo systemctl restart bacnet_app.service

echo "✅ Static IP $IP_ADDRESS configured for $INTERFACE"

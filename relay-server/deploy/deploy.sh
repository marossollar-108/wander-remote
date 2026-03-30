#!/usr/bin/env bash
# Deploy script pre relay server na VPS
# Pouzitie: bash deploy.sh user@server
set -e

SERVER="${1:-forge@167.99.255.47}"
REMOTE_DIR="/home/forge/wander-relay"

echo "=== Deploying Wander Remote Relay ==="
echo "Server: $SERVER"
echo "Remote: $REMOTE_DIR"
echo ""

# Sync relay-server suborov
echo "Syncing files..."
rsync -avz --exclude='node_modules' --exclude='.env' \
    ../../relay-server/ "$SERVER:$REMOTE_DIR/"

# Remote setup
echo "Running remote setup..."
ssh "$SERVER" << 'REMOTE'
cd /home/forge/wander-relay

# Install dependencies
npm ci --production

# Vytvor .env ak neexistuje
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Vytvoreny .env — uprav podla potreby!"
fi

# PM2 setup
if command -v pm2 &> /dev/null; then
    pm2 delete wander-relay 2>/dev/null || true
    pm2 start ecosystem.config.cjs
    pm2 save
    echo "PM2 started"
else
    echo "PM2 nie je nainstalovane — npm install -g pm2"
fi

echo ""
echo "Relay server deployed!"
REMOTE

echo ""
echo "=== Deploy hotovy ==="
echo "Relay: wss://relay.wanderremote.com (po nginx + certbot)"
echo "Alebo priamo: ws://$SERVER:8765"

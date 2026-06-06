#!/bin/bash
# Deploy ai-oral-practice to VPS (speak.projfit.top)
# Run from local machine: bash deploy/deploy.sh
set -e

VPS="tcloud"
REMOTE_DIR="/opt/ai-oral-practice"

echo "=== Deploying ai-oral-practice to $VPS ==="

# 1. Sync code to VPS
echo "[1/5] Syncing code..."
ssh $VPS "mkdir -p $REMOTE_DIR"
rsync -az --delete \
  --exclude node_modules --exclude __pycache__ --exclude .env \
  --exclude dist --exclude audio_cache --exclude '*.pyc' \
  ./ $VPS:$REMOTE_DIR/

# 2. Copy nginx config
echo "[2/5] Setting up nginx site..."
ssh $VPS "sudo cp $REMOTE_DIR/deploy/nginx-speak-projfit.conf /etc/nginx/sites-available/speak-projfit"
ssh $VPS "sudo ln -sf /etc/nginx/sites-available/speak-projfit /etc/nginx/sites-enabled/speak-projfit"

# 3. Get SSL cert (skip if already exists)
echo "[3/5] Checking SSL certificate..."
ssh $VPS "sudo certbot certificates -d speak.projfit.top 2>/dev/null | grep -q 'Certificate Name' \
  || sudo certbot --nginx -d speak.projfit.top --non-interactive --agree-tos"

# 4. Reload nginx
echo "[4/5] Reloading nginx..."
ssh $VPS "sudo nginx -t && sudo systemctl reload nginx"

# 5. Build and start Docker containers
echo "[5/5] Building and starting containers..."
ssh $VPS "cd $REMOTE_DIR && docker compose -f docker-compose.prod.yml up -d --build"

echo ""
echo "=== Done! ==="
echo "Site: https://speak.projfit.top"
echo "Logs: ssh $VPS 'cd $REMOTE_DIR && docker compose -f docker-compose.prod.yml logs -f'"

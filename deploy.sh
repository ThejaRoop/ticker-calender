#!/bin/bash

set -e

echo "========================================="
echo "Pulling latest code..."
echo "========================================="
git pull

echo ""
echo "========================================="
echo "Stopping old containers..."
echo "========================================="
docker compose down

echo ""
echo "========================================="
echo "Building latest image..."
echo "========================================="
docker compose build --no-cache

echo ""
echo "========================================="
echo "Starting application..."
echo "========================================="
docker compose up -d

echo ""
echo "========================================="
echo "Cleaning unused Docker images..."
echo "========================================="
docker image prune -f

echo ""
echo "========================================="
echo "Done!"
echo "========================================="
docker ps

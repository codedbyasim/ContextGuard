#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Build frontend React static files
echo "📦 Building React Frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Install backend Python dependencies
echo "🐍 Installing Python Backend dependencies..."
pip install -r backend/requirements.txt

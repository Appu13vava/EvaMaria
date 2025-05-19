#!/bin/bash

# Clone the correct repo
if [ -z "$UPSTREAM_REPO" ]; then
  echo "Cloning main Repository"
  git clone https://github.com/AM-ROBOTS/EvaMaria.git /EvaMaria
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO"
  git clone "$UPSTREAM_REPO" /EvaMaria
fi

cd /EvaMaria || exit

# Install any updated requirements
pip3 install -U -r requirements.txt

# Start dummy Flask app for Koyeb health check
python3 healthcheck.py &

# Start the actual bot
echo "Starting Bot..."
python3 bot.py

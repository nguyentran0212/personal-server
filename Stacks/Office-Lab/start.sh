#!/bin/bash

# Define the default environment file
DEFAULT_ENV="./default.env"
DOTENV="./.env"

# Determine the environment file to use, prioritizing user input, then .env, then default
if [ -n "$1" ]; then
  ENV_FILE="$1"
  echo "Using environment file specified as argument: '$ENV_FILE'"
elif [ -f "$DOTENV" ]; then
  ENV_FILE="$DOTENV"
  echo "Using environment file: '$ENV_FILE'"
else
  ENV_FILE="$DEFAULT_ENV"
  echo "Using default environment file: '$ENV_FILE'"
fi

# Check if the determined environment file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Environment file '$ENV_FILE' does not exist."
  exit 1
fi

# Start Docker Compose in detached mode with the specified env file
docker compose --env-file "$ENV_FILE" up -d --remove-orphans

# Optional: Confirm the services are started
if [ $? -eq 0 ]; then
  echo "Docker Compose started successfully in detached mode using '$ENV_FILE'."
else
  echo "Error starting Docker Compose."
fi

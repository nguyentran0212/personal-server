#!/bin/bash

# Check if an argument is provided; if not, set the default env file
ENV_FILE="${1:-./default.env}"

# Check if the specified environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file '$ENV_FILE' does not exist."
    exit 1
fi

# Start Docker Compose in detached mode with the specified env file
docker-compose --env-file "$ENV_FILE" up -d

# Optional: Confirm the services are started
if [ $? -eq 0 ]; then
    echo "Docker Compose started successfully in detached mode using '$ENV_FILE'."
else
    echo "Error starting Docker Compose."
fi

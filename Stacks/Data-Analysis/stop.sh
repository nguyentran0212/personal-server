#!/bin/bash

# Start Docker Compose in detached mode with the specified env file
docker compose stop

# Optional: Confirm the services are started
if [ $? -eq 0 ]; then
    echo "Docker Compose stops successfully."
else
    echo "Error stopping Docker Compose."
fi

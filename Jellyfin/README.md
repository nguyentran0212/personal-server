# Jellyfin

This directory contains docker compose for running a Jellyfin server in my network

## Instructions

1. Create `.env` by making a copy of `default.env`
2. Update the setttings
3. Run `docker compose up -d` in the `../Homestack`
4. When the stack starts correctly, pihole admin console would be available at `${METUBE_DOMAIN}.${HOME_SERVER_DOMAIN}`
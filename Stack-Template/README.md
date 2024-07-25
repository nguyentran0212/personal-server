# Start template for defining a stack

This directory contains a template for defining and running a container stack. 

## Instructions

1. Create environment file: `cp .env.default .env`
2. Modify the `compose.yml` to include the necessary apps
3. Use the `.env` to override any application-specific environment variable to adapt it to the stack
4. Deploy the stack `docker compose up -d`
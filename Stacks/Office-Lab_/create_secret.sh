#!/usr/bin/env bash

sed -i 's|AP_API_KEY=.*|AP_API_KEY='"$(openssl rand -hex 64)"'|g' .env
sed -i 's|AP_POSTGRES_PASSWORD=.*|AP_POSTGRES_PASSWORD='"$(openssl rand -hex 32)"'|g' .env
sed -i 's|AP_JWT_SECRET=.*|AP_JWT_SECRET='"$(openssl rand -hex 32)"'|g' .env
sed -i 's|ENCRYPTION_KEY=.*|ENCRYPTION_KEY='"$(openssl rand -hex 16)"'|g' .env

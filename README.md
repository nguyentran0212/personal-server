# Dev Box setup process

Content of the Dev Box:
- Docker
- ngrok
- DroneCI

# Procedure

## Ngrok

```sh
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok
```

```sh
ngrok config add-authtoken 1mVBKhzcTMlRbXz40B41uZMkYKD_21VzwtQXX8RuLgUZ6Vrip
```

## DroneCI

```sh
# Create shared secret between Drone server and Drone worker
openssl rand -hex 16

# Download server container
docker pull drone/drone:2

# Configure and launch server
docker run \
  --volume=/var/lib/drone:/data \
  --env=DRONE_GITHUB_CLIENT_ID=your-id \
  --env=DRONE_GITHUB_CLIENT_SECRET=super-duper-secret \
  --env=DRONE_RPC_SECRET=super-duper-secret \
  --env=DRONE_SERVER_HOST=drone.company.com \
  --env=DRONE_SERVER_PROTO=https \
  --publish=80:80 \
  --publish=443:443 \
  --restart=always \
  --detach=true \
  --name=drone \
  drone/drone:2
```
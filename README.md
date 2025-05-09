# My Server Stack

This repository contains the configuration and environment files to start my homelab and work stack. Each service runs as a Docker container. A Traefik reverse proxy is used as the entry point to the stack.

## Environment Variables

### Stack-level Variables

These variables would be common across all applications deployed within one stack, and different between different stacks. 

- HOME_SERVER_DOMAIN: top level domain of the whole stack
- HOME_SERVER_TZ: timezone code to be applied to all apps in the stack



## How to add new service

You need to ensure that the following conditions are met:

Add labels to docker compose file of the new service so that it would be recognized by Traefik

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.<servicename>.rule=Host(`${SERVICE_DOMAIN}.${HOME_SERVER_DOMAIN}`)"
  - "traefik.http.services.<servicename>.loadbalancer.server.port=8443"
```

Connect the new service to the traefik network by adding this network to the docker compose of the new service

```yaml
networks:
  - traefik-net
```

Add the full domain name to the extra hosts field in the `docker-compose.yml` of PiHole so that the domain name would be routed to the right IP

```yaml
extra_hosts:
  - 'service service.domain:ip_address'
```

Include the Docker compose of the new service to the docker compose of the stack

```yaml
version: '3'

include:
  - ../Traefik/docker-compose.yml ## Traefik: reverse proxy
  - ../PiHole/docker-compose.yml ## Pihole: DNS server and ad blocker
  - ../Metube/docker-compose.yml ## Metube: YouTube downloader
  - ../Jellyfin/docker-compose.yml ## Jellyfin: Media server
  - ../Mealie/compose.yaml ## Mealie: Menu planner server
  - ../CodeServer/compose.yaml ## Codeserver
```


# Known errors / quirks

If a container is connected to two networks (e.g., `traefik-net` and `app-specific-net`), traefik would not be able to reach the container with my current configuration. It seems traefik detects the IP address on the `app-specific-net`, but it tries to direct the traffic via `traefik-net` (or vice versa, neee more investigation). The result is always gateway timeout.

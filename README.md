# Server Craft

<img src="Assets/logo.jpg" alt="My Image" width="300" />

A collection of composable recipes to deploy software stacks for your server.

## Why

Good software elevates us to be more insightful, knowledgeable, and productive. Thanks to the passion of the open source community, there is no shortage of good software. The real challenge is configuration, and integration. 

Say, you are tasked with analysing some experiment data to generate a detailed report and you don't think the plain old Excel spreadsheet can cope with the scale of your data and the complexity of your analysis. Naturally, you would turn to Python or a powerful business intelligence tool. Thanks to open source and software container technologies like Docker, it's so easy to spin up an instance of Jupyter notebook or Metabase in 5 minutes, including the download time.  

But why stop there? To supply your new tools with data, you would need one (or a few) databases. Now that you have databases, it's no harm to setup some sorts of workflow management tools to fetch, clean, and push data into your databases. How about adding a reverse proxy so that you can reach your tools using memorable domain names rather than IP addresses and ports? What if you want to access your tools from another machine? What if you want to access your tools from another country? If you expose your tools to Internet, how would you secure them? 

And just like that, before you know it, dozens of hours have passed and you find yourself knee-deep in the documentation of some arcane software and trouding through forums, finding a way to build just the right software stack and get them talk to eachother. Finally, at the wee hour of the morning, the whole stack works. It's glorious. 

And now you want to do that all over again for a media server at home.

Why don't we just pay for a SaaS instead? Well, small subscriptions here and there stack up quickly. Moreover, sometimes, you work with sensitive data that simply cannot leave your home or organisation. And let's face it, if you are here, you are a certified geek who wants to do it yourself. 

*So, wouldn't that be nice if our hard-earned knowledge about how to build stacks can be reused and combined to build other stacks? Wouldn't it be nice if we can improve upon the knowledge that we gain rather than searching and starting over all the time?*

Welcome to Server Craft.

## How




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

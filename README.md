# Server Craft

<img src="Assets/logo.jpg" alt="My Image" width="300" />

A collection of composable recipes to deploy software stacks for your server.

## Why

Good software elevates us. 

Thanks to the open source community, there is no shortage of good software. The real challenge is configuring these software and integrate them into a stack that is functional, convenient, and secure.

Say, imagine you need to work with some mates to analyse some experiment data and plain old spreadsheet does not cut it anymore. Naturally, you would think about Jupyter Lab or some sorts of business intelligence tool. Thanks to open source and container technology, you can spin up an instance of Jupyter Lab or Metabase in 5 minutes, including the download time. And everyone is happy.

But why stop there? How about a nice set of databases to store the experiment data so all your mates can access? Let's throw in a data pipeline as well to move data directly from the bench to the database. How about adding a reverse proxy so your mates can use domain name rather than IP addresses? What if you want to access your server from Internet so you can work from home? Suddenly, you find yourself pulling an alnighter trouding through obscure documentation trying to configure your reverse proxy to talk to your apps.

Finally, at the wee hour of the morning, the whole stack works. It's glorious. And now you want to do that all over again for a media server at home.

*Wouldn't that be nice if our hard-earned knowledge can be reused and combined to build other stacks?*

**Welcome to Server Craft.**


## User Manual

Server Craft is an *opinionated* collection of "recipes" that can be combined to create a software stack for your server. Some recipes describe how a particular *application* (e.g., Jupyter Lab, Metabase, Jellyfin, Langflow, etc.) is configured and deployed. Other recipes describe how applications are combined to form a *substack*, such as data analysis or GenAI applications. Substacks come together to create *stacks* that you can deploy on your server. 

As a **user**, you either **deploy** or **create** a Server Craft stack recipe on your server.


### Deploy a Stack

Prerequisite: 
- [Docker Engine](https://docs.docker.com/engine/install/) or similar container runtime. This project was tested with Docker.
- [Docker Compose](https://docs.docker.com/compose/install/). This project was not tested with Podman compose.

Process:

``` bash
# clone repository
git clone https://github.com/nguyentran0212/personal-server

# go to stack recipe such as Office-Lab
cd personal-server/Stacks/Office-Lab

# create environment file to configure your stack
cp default.env my-stack.env

# Modify my-stack.env 

# Start the stack with your environment file
./start.sh my-stack.env

# After the stack starts, your apps would be available at <app_domain>.<your_domain> and <app_domain>.localhost
```


### Configure a Stack

Applications in your stack are preconfigured with sensible defaults so that their data is kept between container restarts and they are detected by the reverse proxy out of the box. You can check the recipes in `Apps/`, particularly their `default.env` to see the available environment variables to configure.

**Do not change the configurations directly in the app recipes. Override them within the environment of your stack instead.** This way, you can ensure that all configurations of your stack are packed together in one place, and no unexpected side effects are introduced.

You can configure your stack in two ways:

- Create new `my-stack.env` file and use it to start the stack (`./start.sh my-stack.env`). Any environment variable in my stack would override the corresponding one in substacks and apps.
- Modify `compose.override.yml` to override a part of the recipe of an app that cannot be overriden by environment variable.

Common Environment Variables:

``` bash
# Top level configs
HOME_SERVER_DOMAIN="localhost" # Domain name to access the stack. App would be available as subdomain (e.g., app.localhost)
HOME_SERVER_TZ="Australia/Adelaide" # Timezone code
STACK_NAME="my_stack" # Name of the stack
TRAEFIK_NETWORK="traefik-net" # Name of the network docker compose would create for reverse proxy
```

### Create a stack

So far, you have used the prebuilt `Office-Lab` stack for demonstration. You can make your own stack based on the existing Apps and Substacks.

**Because your stack is private to your use case and server, it is highly recommended that you fork Server Craft to your GitHub and modify that copy.**

``` bash
# Create a new stack based on the template
cd Stacks/
cp Template My-Stack
cd My-Stack

# Edit compose.yml to include substacks and apps
# You need to keep the foundation substack to keep reverse proxy and monitoring!

# Modify your compose.override.yml if needed

# Create your my-stack.env based on default.env

# Enjoy your new stack!
```

## Developer Manual

We welcome contributions that introduce new apps and new substacks. Please see the roadmap for our "wishlist" of new apps and substacks.

### General Guideline

Prerequisite: 
- [Docker Engine](https://docs.docker.com/engine/install/) or similar container runtime. This project was tested with Docker.
- [Docker Compose](https://docs.docker.com/compose/install/). This project was not tested with Podman compose.
- Familiarity with Docker and Docker Compose
- Familiarity with reverse proxy and Traefik

Process: 
- Fork Server Craft to your GitHub account.
- Write your new App or Substack recipe. The `Apps/Template/` and `Substacks/Template/` provide a starting point to define your new apps and substacks. 
- Please avoid modifying `network`, `extra-hosts`, and `labels` related to Traefik to ensure that the reverse proxy works with your new apps. Other than that, you can define services as you would like, and multiple services can exist within an app. For example, see `Apps/Langflow/compose.yml`. 
- Set the default configuration of your apps using `default.env`
- Integrate into a substack or stack and have a try to ensure everything works on your server.
- Open a pull request to merge your new recipes to Server Craft.

### Known errors / quirks

If a container is connected to two networks (e.g., `traefik-net` and `app-specific-net`), traefik would not be able to reach the container with my current configuration. It seems traefik detects the IP address on the `app-specific-net`, but it tries to direct the traffic via `traefik-net` (or vice versa, neee more investigation). The result is always gateway timeout.

## Product Roadmap

MVP
- [x] Design a mechanism to support recipe composition
- [x] Design reverse proxy mechanism
- [x] Build initial substacks and corresponding apps (Data analysis, media servers, data store, GenAI apps, GenAI tools)
- [x] Build and tested two stacks for demonstration
- [x] User guide
- [x] Developer general guideline
- [ ] Document the general architecture of a stack built on Server Craft
- [ ] Create architecture diagram to explain the design of the recipe composition mechanism

Key enhancement
- [ ] VPN support 
- [ ] Secure tunnel support for accessing from Internet
- [ ] Setup LDAP and SSO so that users can login with only one credential
- [ ] Security hardening of the stack
- [ ] Introduce proper secret management in the recipes
- [ ] Introduce backup and restore mechanism to the stack

Wishlist
- [ ] Kubernetes support for multi-host stacks
- [ ] Langfuse integration for GenAI observability
- [ ] Apache airflow integration for data pipeline
- [ ] MinIO integration for persistence
- [ ] LLM inference substack (Ollama or vLLM + an LLM router)
- [ ] Image generation substack (ComfyUI on Nvidia)
- [ ] LLM finetuning substack
- [ ] Stable diffusion finetuning substack

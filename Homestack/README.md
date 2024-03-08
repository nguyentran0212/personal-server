# Software stack for home

Open problems:

- I ended up attaching Jellyfin into a virtual Docker network, breaking its ability to do DLNA. I don't have the skillset to sand other configurationsetup reverse proxy properly and dealing with SSL to use the network mode host. I will need to explore later
- Jellyfin needs some start up preparations, including creating empty folders. I need to make a bash script for this preparations before running Docker
- I still need to extract all the parameters of this stack into a `.env` file

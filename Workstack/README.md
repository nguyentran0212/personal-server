# Work Stack (WIP)

Stack of services for work. Right now, there is only OpenProject running on port 8080. It is exposed to the Internet via an ngrok tunnel that connects to their edge server. The edge server has been assigned the following domain name: https://needlessly-optimal-labrador.ngrok-free.app/

Limitation: There is no reverse proxy setup before the OpenProject, so I cannot run another service on this machine and expose it via the same domain name, at least not that I know how to do it. 

Use the following command to start ngrok and point to the edge that I have setup: `ngrok tunnel --label edge=edghts_2dFlBy5qfL5ALzVshKOKG1tGOMS http://localhost:9000`

Todo:

- Extract configurations from the docker-compose into external .env file (particularly the domain name and static IP)
- Setup Docker compose for NGROK
- Integrate reverse proxy into this stack
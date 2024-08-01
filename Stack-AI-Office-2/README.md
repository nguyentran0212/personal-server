# AI stack powered by a local Ollama instance

This stack contains AI apps that interacts with an Ollama instance running on the same machine (but not inside Docker). All apps would interact with Ollama via `http://host.docker.internal:11434`

Services:
- `openwebui.localhost`: Open WebUI
- `sillytavern.localhost`: Silly Tavern AI
- `searxng.localhost`: Searxng (for both independent use and OpenWebUI)

Additional instructions: 
- Add the following line `127.0.0.1 *.localhost` to the `/etc/hosts` file so that all the subdomains above would be routed correctly
- Need to open port 11434 (ollama), otherwise containers will not be able to reach `host.docker.internal:11434`.
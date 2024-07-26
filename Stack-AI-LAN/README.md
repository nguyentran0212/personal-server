# AI stack powered by a LAN Ollama instance

NOTE: NOT WORKING WITH MY NUC BOX AT THE MOMENT

This stack contains AI apps that interacts with an Ollama instance running on a different machine via LAN. All apps would interact with Ollama via `OLLAMA_BASE_URL`

Services:
- `openwebui.ai.local`: Open WebUI
- `sillytavern.ai.local`: Silly Tavern AI
- `searxng.ai.local`: Searxng (for both independent use and OpenWebUI)

Additional instructions: 
- Add the following line `ip-of-server-stack *.ai.local` to the `/etc/hosts` file of all client machines who want to use the stack so that all the subdomains above would be routed correctly
- Add the following line `127.0.0.1 *.localhost` to the `/etc/hosts` file of all client machines who want to use the stack so that all the subdomains above would be routed correctly
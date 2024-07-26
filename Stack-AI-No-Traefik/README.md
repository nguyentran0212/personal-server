# AI stack powered by a LAN Ollama instance


This stack contains AI apps that interacts with an Ollama instance running on a different machine via LAN. All apps would interact with Ollama via `OLLAMA_BASE_URL`

Services:
- `<host-ip>:3000`: Open WebUI
- `<host-ip>:9000`: Silly Tavern AI
- `<host-ip>:8080`: Searxng (for both independent use and OpenWebUI)
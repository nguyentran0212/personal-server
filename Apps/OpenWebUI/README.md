# OpenWebUI

A GUI for using local LLM with built in ability to doing RAG, websearch and tool calling. 

There are two versions of docker compose here:

- `compose.yml`: Can only access Ollama server via `host.docker.internal` (if the Ollama server is running locally) or a proper domain name that can be resolved. Cannot access an Ollama server on LAN via IP address.
- `compose.lan.yml`: Can access Ollama server on LAN via IP address. The container has one additional macvlan interface


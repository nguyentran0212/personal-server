# GPT Researcher

An app that implements an agentic workflow to retrieve and generate report on a topic.

There are two versions of docker compose here:

- `compose.yml`: Can only access servers via `host.docker.internal` (if the server is running locally) or a proper domain name that can be resolved. Cannot access a server on LAN via IP address.
- `compose.lan.yml`: Can access servers on LAN via IP address. The container has one additional macvlan interface

## Environment variables

``` bash
APP_NAME=gptresearcher
APP_DOMAIN=gptresearcher
GPT_RESEARCHER_OLLAMA_URL=http://host.docker.internal:11434
GPT_RESEARCHER_OLLAMA_FAST_MODEL=Meta-Llama-3.1-8B-Instruct:latest
GPT_RESEARCHER_OLLAMA_SMART_MODEL=Meta-Llama-3.1-8B-Instruct:latest
GPT_RESEARCHER_OLLAMA_EMBEDDING_MODEL=mxbai-embed-large:latest
SEARXNG_URL=http://searxng:8080
```
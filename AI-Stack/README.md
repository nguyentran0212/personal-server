# Local AI Stack

This stack is developed for both local development and utilisation. 

Known limitations:
- OLLAMA running inside Docker CANNOT use GPU on Macbook. 
- Some configuration on Open WebUI needs to be done manually: connecting to SearNGX
- If OLLAMA runs on a different machine, any service that requires connection to OLLAMA must use `network_mode: host`, meaning all port mapping and reverse proxy does not work.
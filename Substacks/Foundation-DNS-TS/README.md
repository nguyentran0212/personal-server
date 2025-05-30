# Traefik-DNS-TS foundation stack.

We want to achieve the following:

- Reach every dockerised app via domain name `appdomain.domain.tld`
- Being able to do it from anywhere on Internet rather than being stuck in LAN.

Here is how we solve this:

1. Use traefik to enable directing `appdomain.domain.tld` to correct docker container.
2. Use local DNS records in PiHole to resolve all `appdomain.domain.tld` to the LAN IP address of the server. On LAN, as long as a client use the PiHole as the DNS server, it would be able to resolve `appdomain.domain.tld` to LAN IP to reach the server easily. 
3. Use tailscale to create a private mesh VPN so that clients on mesh VPN can reach the server. 
4. Tailscale is configured so that all DNS queries for `domain.tld` would be resolved by the server running PiHole. This ensure that every client would be able to resolve `appdomain.domain.tld` to LAN IP address of the server anywhere on Internet.
5. Tailscale on the server is configured to advertise the LAN IP of the server on tailscale net. With this configuration, every tailscale client would know to direct the traffic for LAN IP of the server to its tailscale interface. 
6. Tailscale runs within Docker to maintain the coding convention. However, this container use `network-mode:host` to simplify the configuration. There might be problems down the line with this configuration, but I haven't found any problem so far. 

# Tailscale Docker Compose

This is a Docker Compose definition for Tailscale in host mode. It sets up the Tailscale daemon to:
- Use `network_mode: host` for kernel TUN and UDP connectivity.
- Advertise this host as DNS server to Tailnet clients.
- Advertise your LAN subnet for routing to internal devices.

Configure `default.env` with your TS_AUTHKEY, TS_HOSTNAME, and LAN_CIDR.

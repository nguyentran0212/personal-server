# Office Lab Stack

This is example of a server stack for data analysis and experimentation workflows. It relies on `Foundation-DNS-TS` substack, meaning it has built-in reverse proxy (via traefik), DNS server (via PiHole) and VPN support (via tailscale). It also has built-in support for OIDC (via Authentik). It means it's a complex stack that requires more patience to get it up and running.

To use this step, you need to do the following:
- Create `.env` file by copying and renaming the `default.env`
- Modify top-level configs as needed
- Modify the path to media storage folders as needed
- Note down the LAN IP address of your server that you plan to use to run this stack.
- Fill in the `LAN_CIDR` field with your LAN IP. Tailscale would advertise and route this IP so that any tailscale client in your network would be able to reach your server.
- Populate the `PIHOLE_EXTRA_HOSTS` field with the `subdomain:LAN_IP` records. These records would be used by PiHole to resolve `subdomain.domain.tld` name of your app to the IP address of the server.
- Create a tailscale account if you don't have and get yourself an Authkey
- Add the tailscale Authkey to `TS_AUTHKEY`

By now, you can start the stack.

If you want to setup SSO, you need to create apps and provider in `Authentik` after the stack is online, and then use use the client secret and client ID provided by Authentik to fill in the corresponding fields in `.env`. 

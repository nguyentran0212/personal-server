# Pi Hole

Pi Hole is an adblocker that also doubles as DHCP server and DNS server. I use this service to provide domain name on my local network. 

Some important notes:

- In order to add domain names to the DNS server, change the `extra_hosts` field in the docker-compose.yml.
- Remember to set the FTLCONF_LOCAL_IPV4 to the right local IP
- The admin interface at `pi.hole/admin` does not work. I have to use `IP:8053/admin`
- In order to make this configuration works, I have modified the router so that any IP assignment via DHCP would be provided with a DNS server that points to my local server where Pi Hole runs. If this Pi Hole instance does not work, the whole network would not have DNS resolving ability
- Huawei LTE router hides the DNS configuration by default. To show these configurations, go to the DHCP page, open developer console, and type the following `$('#dhcp_dns').show()`. It will make the DNS configuration part appear.
- Need to add dns 127.0.0.1 and 1.1.1.1 to the Pi Hole container, otherwise it would not be able to resolve any DNS
- Disable the stub listener on Ubuntu, otherwise the container would not be able to bind to port 53

> Modern releases of Ubuntu (17.10+) and Fedora (33+) include systemd-resolved which is configured by default to implement a caching DNS stub resolver. This will prevent pi-hole from listening on port 53. The stub resolver should be disabled with: sudo sed -r -i.orig 's/#?DNSStubListener=yes/DNSStubListener=no/g' /etc/systemd/resolved.conf. This will not change the nameserver settings, which point to the stub resolver thus preventing DNS resolution. Change the /etc/resolv.conf symlink to point to /run/systemd/resolve/resolv.conf, which is automatically updated to follow the system's netplan: sudo sh -c 'rm /etc/resolv.conf && ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf' After making these changes, you should restart systemd-resolved using systemctl restart systemd-resolved

## Instructions

1. Create `.env` by making a copy of `default.env`
2. Change the `PIHOLE_DOMAIN` and `PIHOLE_WEB_PASSWORD` in the newly created `.env`
3. Run `docker compose up -d` in the `../Homestack`
4. When the stack starts correctly, pihole admin console would be available at `${PIHOLE_DOMAIN}.${HOME_SERVER_DOMAIN}`

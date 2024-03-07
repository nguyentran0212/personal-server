# Pi Hole

Pi Hole is an adblocker that also doubles as DHCP server and DNS server. I use this service to provide domain name on my local network. 

Some important notes:

- In order to add domain names to the DNS server, change the `extra_hosts` field in the docker-compose.yml.
- Remember to set the FTLCONF_LOCAL_IPV4 to the right local IP
- The admin interface at `pi.hole/admin` does not work. I have to use `IP:8053/admin`
- In order to make this configuration works, I have modified the router so that any IP assignment via DHCP would be provided with a DNS server that points to my local server where Pi Hole runs. If this Pi Hole instance does not work, the whole network would not have DNS resolving ability
- Huawei LTE router hides the DNS configuration by default. To show these configurations, go to the DHCP page, open developer console, and type the following `$('#dhcp_dns').show()`. It will make the DNS configuration part appear.
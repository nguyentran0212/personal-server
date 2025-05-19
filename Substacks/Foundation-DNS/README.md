# Foundation Substack with DNSStubListener

This foundation substack provides the core services (e.g., reverse proxy, dashboard, IdP, container monitoring). When you include this substack in your Docker Compose stack (and configure orther services correctly), applications in your stack would be reachable from browser under two domain names: `appdomain.domain.tld` and `appdomain.localhost`. If you open a browser on the server and type in `appdomain.localhost`, you will reach the application. 

## Make appdomain.domain.tld work

There are two challenges you need to solve: 

1. How to make the browser of yourself and your users know how to resolve appdomain.domain.tld into the IP address of the server that host your stack?
2. How to make services inside your stack know how to resolve appdomain.domain.tld into IP address of the server? This is particularly important for setting up SSO inside your stack.

The substack in this directory relies on PiHole. It turns your server into a DNS server, which knows how to resolve all the `appdomain.domain.tld` into correct IP (which is its IP address). After pointing the DNS server setting of all of you computers to your server, all of them would be able to resolve `appdomain.domain.tld`. 

There are a few steps you need to do for this scheme to work:

1. Turn off DNSStubListener on your server to unbind the port 53. Otherwise, PiHole container would fail to start.
2. Add localhost (127.0.0.1) into the list of name servers on your server. Without this setting, your containers would not be able to use PiHole to resolve DNS query.
3. Add DNS records (e.g., `Server-IP appdomain.domain.tld`) to PiHole.

If the IP address of your server changes, you will need to update DNS records in PiHole.

### Finding your IP Address

Use `ip addr` to find the external IP address attached to the network interface that is attached to your Docker network. If you use wifi, it's usually the `wlp6s0` interface. 

### Adding DNS records

After deploying your stack, access it at `pihole.localhost/admin` from the server. Use the `Local DNS records` settings to set the DNS records.

### Convenient script

Use the script `prepare_dns_server.sh` to disable DNSStubListener and add 127.0.0.1 to your DNS list. This script also add `8.8.8.8` as back up DNS server for the server in case there is a problem with PiHole.

## Pros and Cons

Pros: simple to start. If you are running a modern Linux distribution, all the necessary DNS configurations are usually pre-configured. You only need to modify `/etc/hosts`

Cons: 
- If IP address of your computer changes, you need to update all the `/etc/hosts` files.
- If you add new services, you need to update all the `/etc/hosts` files.

If you want a more elegant but complex solution, see `Foundation-DNS` substack.

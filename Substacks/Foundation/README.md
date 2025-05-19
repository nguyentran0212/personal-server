# Foundation Substack with DNSStubListener

This foundation substack provides the core services (e.g., reverse proxy, dashboard, IdP, container monitoring). When you include this substack in your Docker Compose stack (and configure orther services correctly), applications in your stack would be reachable from browser under two domain names: `appdomain.domain.tld` and `appdomain.localhost`. If you open a browser on the server and type in `appdomain.localhost`, you will reach the application. 

## Make appdomain.domain.tld work

There are two challenges you need to solve: 

1. How to make the browser of yourself and your users know how to resolve appdomain.domain.tld into the IP address of the server that host your stack?
2. How to make services inside your stack know how to resolve appdomain.domain.tld into IP address of the server? This is particularly important for setting up SSO inside your stack.

The substack in this directory relies on [DNSStubListener](https://wiki.archlinux.org/title/Systemd-resolved) and manual configuration of `/etc/hosts` file. To help services in your stack talk to each other using `appdomain.domain.tld`, you need to manually modify the `/etc/hosts` file and add the records for **every app** in your stack. 

For example, imagine you have 3 apps available at `appdomain1.domain.tld`, `appdomain2.domain.tld`, and `appdomain3.domain.tld` and the external IP of your server on the local network is `192.186.8.10`. You will need to add the following lines to the `/etc/hosts` file **of your server** and any computers that want to interact with your apps:

``` ini
192.168.8.10 domain.tld
192.168.8.10 appdomain1.domain.tld
192.168.8.10 appdomain2.domain.tld
192.168.8.10 appdomain3.domain.tld
```

Remember to modify `/etc/hosts` correctly on your server. Otherwise, your containers will not be able to resolve `appdomain.domain.tld` that you set.

### Finding your IP Address

Use `ip addr` to find the external IP address attached to the network interface that is attached to your Docker network. If you use wifi, it's usually the `wlp6s0` interface. 

## Pros and Cons

Pros: simple to start. If you are running a modern Linux distribution, all the necessary DNS configurations are usually pre-configured. You only need to modify `/etc/hosts`

Cons: 
- If IP address of your computer changes, you need to update all the `/etc/hosts` files.
- If you add new services, you need to update all the `/etc/hosts` files.

If you want a more elegant but complex solution, see `Foundation-DNS` substack.

# Audiobookshelf

> Self-hosted audiobook and podcast server

## Configurations

Set the `AUDIOBOOKSHELF_MEDIA_DIR` variable to point to the directory where audiobooks and podcasts would be stored.

## SSO

Audiobookshelf supports SSO, but it has to be configured via web UI (Or at least I haven't figured out the way to set this up via environment variables). To enable SSO, do the following:

1. In `authentik` (at `authentik.domain.tld`), create a new app for Audiobookshelf with OIDC provider.
2. Copy the OpenID Configuration URL in the OIDC provider of the Audiobookshelf app
3. Copy the client ID and client secret of Audiobookshelf app in authentik.
4. Log in to Audiobookshelf as admin
5. Go to authentication and enable OIDC
6. Paste the OpenID configuration URL to auto populate other URL, and then paste client ID and client secret
7. Remember to turn on auto register user

Gotcha: if the admin user ID is the same as the user ID from authentik, you will lose access to the admin account because that admin account would be overwritten by the account in Authentik, and the account in Authentik is a normal user, not admin. 

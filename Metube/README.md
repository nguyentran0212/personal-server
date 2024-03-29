# Metube

Metube is a GUI utility for downloading Youtube videos

Mount the file cookies-youtube-com.txt into the /cookies/cookies-youtube-com.txt using the cookies extracted from YouTube in order to download videos from private playlists

## Instructions

1. Create `.env` by making a copy of `default.env`
2. Update the setttings
3. Run `docker compose up -d` in the `../Homestack`
4. When the stack starts correctly, pihole admin console would be available at `${METUBE_DOMAIN}.${HOME_SERVER_DOMAIN}`

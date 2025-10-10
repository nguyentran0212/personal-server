# Creating New Apps for Server Craft

This guide explains how to create a new app for the Server Craft stack. Following these steps will ensure your app integrates properly with the reverse proxy, homepage, and backup systems.

## Overview

Server Craft apps are Docker Compose configurations that automatically integrate with the stack's core capabilities. Each app consists of three main files:
- `compose.yml` - Docker Compose configuration for the service(s)
- `default.env` - Default environment variables for the app
- `metadata.yaml` - App metadata and configuration for CLI integration

## Step 1: Copy the Template

Start by copying the template app:

```bash
cp -r Apps/Template Apps/YourAppName
```

Replace `YourAppName` with the name of your app.

## Step 2: Configure compose.yml

Modify `Apps/YourAppName/compose.yml` to define your services:

### Example Structure

```yaml
services:
  your-app-service: # Main service of this app. Accessible from proxy and homepage.
    image: your-image:tag
    environment: 
      # Use stack-level environment variables where appropriate
      APP_TZ: ${HOME_SERVER_TZ}
      # Define app-specific variables that can be overridden by the stack
      APP_PORT: ${APP_PORT}
      CUSTOM_VAR: ${SOME_CUSTOM_VAR}
    volumes:
      - your-app-data:/app/data
    restart: unless-stopped
    networks:
      - ${TRAEFIK_NETWORK}
      - your-app-net
    extra_hosts:
      - "host.docker.internal:host-gateway"
    labels:
      # Traefik reverse proxy integration
      - "traefik.enable=true" # Enable reverse proxy
      - "traefik.http.routers.${APP_NAME}.rule=Host(`${APP_DOMAIN}.${HOME_SERVER_DOMAIN}`) || Host(`${APP_DOMAIN}.localhost`)" # Domain names to reach the app
      - "traefik.http.services.${APP_NAME}.loadbalancer.server.port=${APP_PORT}" # Tell reverse proxy which port to use
      - "traefik.docker.network=${STACK_NAME}_${TRAEFIK_NETWORK}"
      
      # Homepage integration
      - "homepage.group=Your_Group_Name" # Group for this service on the homepage
      - "homepage.name=Your App Display Name" # Name of this service on the homepage
      - "homepage.icon=icon-name.png" # Icon from https://github.com/homarr-labs/dashboard-icons
      - "homepage.href=https://${APP_DOMAIN}.${HOME_SERVER_DOMAIN}/" # Link to access this service on the homepage
      - "homepage.description=Short description of your app" # Description of this service on the homepage
      
      # Nautical backup integration
      - "nautical-backup.override-source-dir=${STACK_NAME}_your-app-service"
      - "nautical-backup.additional-folders=${STACK_NAME}_your-app-service"

  # Optional: Dependent services that should be hidden from proxy and homepage
  your-app-db:
    image: database-image:tag
    volumes:
      - your-app-db:/var/lib/mysql
    restart: unless-stopped
    networks:
      - your-app-net
    environment:
      DB_TZ: ${HOME_SERVER_TZ}

volumes:
  your-app-data:
  your-app-db:

networks:
  your-app-net:
```

### Key Points for compose.yml

1. **Use Environment Variables**: Leverage stack-level environment variables like `${HOME_SERVER_DOMAIN}`, `${HOME_SERVER_TZ}`, `${STACK_NAME}`, etc.

2. **Traefik Labels**: For services that should be accessible via the reverse proxy, include the required Traefik labels using these patterns:
   - `traefik.enable=true`
   - `traefik.http.routers.${APP_NAME}.rule=Host(`${APP_DOMAIN}.${HOME_SERVER_DOMAIN}`) || Host(`${APP_DOMAIN}.localhost`)`
   - `traefik.http.services.${APP_NAME}.loadbalancer.server.port=${APP_PORT}`
   - `traefik.docker.network=${STACK_NAME}_${TRAEFIK_NETWORK}`

3. **Homepage Labels**: Include homepage integration labels to make your app appear on the dashboard.

4. **Backup Labels**: Include nautical-backup labels for automated backup integration.

5. **Networks**: Use `${TRAEFIK_NETWORK}` for services that need reverse proxy access, and create app-specific networks for internal communication.

## Step 3: Configure default.env

Update `Apps/YourAppName/default.env` with default environment variables:

```
# App identification (required)
APP_NAME=your_app_name
APP_DOMAIN=your_app_domain
APP_PORT=8080

# App-specific configuration with default values
SOME_CUSTOM_VAR=default_value
ANOTHER_VAR=another_default

# Secrets that will be auto-generated during stack creation
SECRET_API_KEY=
ENCRYPTION_KEY=
```

### Key Points for default.env

1. **Required Variables**: Every app must define `APP_NAME`, `APP_DOMAIN`, and `APP_PORT`
2. **Default Values**: Provide sensible defaults for all configurable parameters
3. **Empty Secrets**: Leave secrets empty (`SECRET_VAR=`) so they are auto-generated during stack creation

## Step 4: Configure metadata.yaml

Update `Apps/YourAppName/metadata.yaml` with app information and user configuration:

```yaml
metadata:
  name: Your App Display Name
  type: app
  description: One sentence description of what your app does
  projectUrl: https://github.com/username/repository

# User-configurable settings that will be prompted during stack creation
userConfig:
  - name: YOUR_APP_USERNAME
    prompt: "Admin username for your app"
    type: string
    default: "admin"
  - name: YOUR_APP_EMAIL
    prompt: "Admin email for your app"
    type: string
    default: "admin@example.com"

# Volumes that need host path configuration during stack creation
volumes:
  - hostPathKey: YOUR_APP_MEDIA_DIR
    prompt: "Directory for media files"
    default: "./your-app-media"
    containerMount: "/media"
  - hostPathKey: YOUR_APP_CONFIG_DIR
    prompt: "Directory for configuration files"
    default: "./your-app-config"
    containerMount: "/config"

# Post-installation instructions that will be shown to users
postInstall:
  - "After starting the stack, access your app at https://your_app_domain.your_domain.com"
  - "Default login credentials are admin/admin"
  - "Remember to change the default password after first login"
```

### Key Points for metadata.yaml

1. **metadata section**: Define the app name, type (must be "app"), description, and project URL
2. **userConfig section**: Define variables that require user input during stack creation
   - `name`: The environment variable name
   - `prompt`: The text shown to the user
   - `type`: Variable type (string, enum for dropdowns)
   - `default`: Default value to suggest
3. **volumes section**: Define host path mounts that users need to configure
   - `hostPathKey`: The environment variable that will hold the host path
   - `prompt`: The text shown to the user
   - `default`: Default path suggestion
   - `containerMount`: Where the volume should be mounted inside the container
4. **postInstall section**: Provide important setup instructions for users after deployment

## Step 5: Test Your App

1. Add your app to a stack by including it in the stack's `compose.yml`:
   ```yaml
   include:
     - path: ../../Apps/YourAppName/compose.yml
       env_file:
         - ../../Apps/YourAppName/default.env
   ```

2. Create a test stack using the CLI:
   ```bash
   servercraft create test-stack
   ```

3. Verify that:
   - The app appears in the homepage dashboard
   - The reverse proxy correctly routes to your app
   - All user-configurable variables are prompted during creation
   - Volumes are properly mounted
   - Backup integration works

## Environment Variables Reference

Your app can use these common stack-level environment variables:

- `HOME_SERVER_DOMAIN` - Domain name to access the stack (e.g., `aurora.lab`)
- `HOME_SERVER_TZ` - Timezone code (e.g., `Australia/Adelaide`)
- `STACK_NAME` - Name of the stack
- `TRAEFIK_NETWORK` - Name of Docker bridge network used by Traefik (default: `traefik-net`)
- `LAN_CIDR` - Local area network CIDR (e.g., `192.168.1.0/24`)
- `MEDIA_DIR` - Path to media directory
- `WORK_DIR` - Path to work directory
- `BACKUP_SOURCE_DIR` - Directory where Docker volumes are stored
- `BACKUP_DESTINATION_DIR` - Destination directory for backups
- `BACKUP_SCHEDULE` - Cron schedule for automated backups

## Integration Labels Reference

### Traefik Reverse Proxy Integration:
- `traefik.enable=true` - Enable reverse proxy for the service
- `traefik.http.routers.${APP_NAME}.rule=Host(`${APP_DOMAIN}.${HOME_SERVER_DOMAIN}`) || Host(`${APP_DOMAIN}.localhost`)'` - Define routing rules using environment variables
- `traefik.http.services.${APP_NAME}.loadbalancer.server.port=${APP_PORT}` - Specify port to use for load balancing
- `traefik.docker.network=${STACK_NAME}_${TRAEFIK_NETWORK}` - Specify the network Traefik uses

### Homepage Integration:
- `homepage.group=Group_Name` - Group name for service on homepage
- `homepage.name=Display_Name` - Display name for service on homepage
- `homepage.icon=icon-name.png` - Icon file (select from homarr-labs/dashboard-icons)
- `homepage.href=https://${APP_DOMAIN}.${HOME_SERVER_DOMAIN}/` - Access URL for service
- `homepage.description=Description` - Description of the service

### Nautical Backup Integration:
- `nautical-backup.override-source-dir=${STACK_NAME}_container_name` - Backup source directory
- `nautical-backup.additional-folders=${STACK_NAME}_container_name` - Additional folders to back up

## Best Practices

1. **Security**: Don't put secrets in `default.env` - leave them empty so they're auto-generated
2. **Flexibility**: Use environment variables for configurable parameters so stack creators can override them
3. **User Experience**: Provide clear prompts and helpful defaults in metadata.yaml
4. **Consistency**: Follow the naming conventions used in other apps
5. **Testing**: Test your app integration with different stack configurations
6. **Documentation**: Include helpful post-install instructions for users

## Example: Life Engineer App

For reference, see the Life Engineer app which demonstrates all these concepts:

```yaml
# Apps/LifeEngineer/metadata.yaml
metadata:
  name: Life Engineer
  type: app
  description: AI Engineer for your life
  projectUrl: https://github.com/nguyentran0212/life-engineer

userConfig:
  - name: LIFE_ENGINEER_ASSISTANT_PERSONA
    prompt: "Choose your assistant persona"
    type: string
    default: "max"
  - name: LIFE_ENGINEER_USER_PERSONA
    prompt: "Choose your user persona"
    type: string
    default: "gen"
  - name: LIFE_ENGINEER_INITIAL_ADMIN_EMAIL
    prompt: "Email for the default admin account of life engineer"
    type: string
    default: "admin@example.com"
  - name: LIFE_ENGINEER_INITIAL_ADMIN_PASSWORD
    prompt: "Password for the default admin account of life engineer"
    type: string
    default: "admin1234"

volumes:
  - hostPathKey: LIFE_ENGINEER_BOOTSTRAP_DIR
    prompt: "Path to your bootstrap folder where you provide your seed taskwarrior database to be used"
    default: "./life-engineer-bootstrap"
    containerMount: "/tmp/life_engineer"
  - hostPathKey: LIFE_ENGINEER_PERSONA_DIR
    prompt: "Path to your directory where you provide personas for yourself and AI that you want to use"
    default: "./life-engineer-personas"
    containerMount: "/tmp/life_engineer"

postInstall:
  - "Remember to copy your .taskwarrior directory into the LIFE_ENGINEER_BOOTSTRAP_DIR folder if you want to use existing task database with your life engineer instance."
  - "Remember to add to LIFE_ENGINEER_PERSONA_DIR folder with the persona.txt files for the user and assistant persona that you want to use with your life engineer instance."
  - "Ensure OPENAI_API_KEY is set in your .env or in your terminal before starting the stack."
```
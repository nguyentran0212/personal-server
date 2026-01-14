# Server Craft - Project Context for Qwen Code

## Project Overview

Server Craft is a comprehensive toolkit for creating and managing Docker-based server stacks. It provides preconfigured, composable recipes and utilities to craft Dockerized server environments with core capabilities like reverse proxy, authentication, monitoring, and more working automatically. The project uses Docker Compose's `include` functionality to allow users to compose complex server stacks from modular components.

### Key Components:
- **Apps**: Individual applications like Jellyfin, OpenWebUI, Jupyter, etc.
- **Substacks**: Collections of related apps (e.g., Data-Analysis, GenAI-Tools, Foundation stacks)
- **Stacks**: Complete server setups composed from apps and substacks
- **servercraft CLI**: Command-line tool for managing stacks

### Architecture:
The project enables composable server stacks using Docker and Docker Compose with the `include` directive. This allows for:
- Foundation stacks providing core capabilities (reverse proxy, SSO, monitoring)
- App templates that integrate with the core capabilities
- Composable design rules for apps to work together

## Technology Stack

- **Python 3.10+**: Core CLI tool implementation
- **uv**: Dependency management
- **Docker & Docker Compose**: Container orchestration
- **Typer**: CLI framework
- **PyYAML**: YAML processing
- **Questionary**: Interactive prompts in CLI

## Building and Running

### Setup:
```bash
# Clone repository
git clone https://github.com/nguyentran0212/personal-server

# Install CLI dependencies
uv sync

# Run servercraft CLI
uv run servercraft --help
```

### Key Commands:
- `servercraft list-apps` - List all available applications
- `servercraft list-stacks` - List all existing stacks
- `servercraft create <NAME>` - Scaffold a new stack
- `servercraft start <NAME>` - Start a Docker stack
- `servercraft stop <NAME>` - Stop a Docker stack
- `servercraft inspect <NAME>` - Show configuration and next steps

### Deploy a Stack:
```bash
# Navigate to a stack
cd Stacks/Office-Lab

# Create environment file
cp default.env my-stack.env

# Start the stack
docker compose --env-file my-stack.env up -d
```

## Project Structure

```
personal-server/
├── Apps/                   # Individual application templates
│   ├── Activepieces/       # Example: App with compose.yml, default.env
│   ├── Jellyfin/
│   ├── OpenWebUI/
│   └── ...
├── Substacks/              # Collections of related apps
│   ├── Foundation-DNS-TS/  # Example: Foundation with compose.yml
│   ├── Data-Analysis/
│   ├── GenAI-Tools/
│   └── ...
├── Stacks/                 # Complete deployable stacks
│   ├── office-lab/         # Example: Final stack with compose.yml
│   ├── Home-Server/
│   └── Template/
├── servercraft/            # Python CLI tool
│   └── main.py
├── Assets/
├── Docs/
├── README.md
├── pyproject.toml          # Standard Python project configuration (compatible with uv)
└── uv.lock                 # uv lock file for dependency management
```

Each app contains:
- `compose.yml` - Docker Compose configuration
- `default.env` - Default environment variables
- `metadata.yaml` - App metadata and configuration prompts

## Development Conventions

### Environment Variables
The stack uses a set of common environment variables that are automatically available to all apps:

#### Stack-level Configuration:
- `HOME_SERVER_DOMAIN` - Domain name to access the stack (e.g., `aurora.lab`)
- `HOME_SERVER_TZ` - Timezone code (e.g., `Australia/Adelaide`)
- `STACK_NAME` - Name of the stack
- `LAN_CIDR` - Local area network CIDR (e.g., `192.168.1.0/24`)
- `MEDIA_DIR` - Path to media directory
- `WORK_DIR` - Path to work directory
- `BACKUP_SOURCE_DIR` - Directory where Docker volumes are stored
- `BACKUP_DESTINATION_DIR` - Destination directory for backups
- `BACKUP_SCHEDULE` - Cron schedule for automated backups

#### Foundation-specific Configuration:
- `TRAEFIK_NETWORK` - Name of Docker bridge network used by Traefik (default: `traefik-net`)
- `TS_AUTHKEY` - Tailscale authentication key
- `PIHOLE_LOCAL_DNS_RECORDS` - Auto-generated DNS records for services

### Creating New Apps:
- Follow the template in `Apps/Template/`
- Use consistent environment variables (APP_NAME, APP_DOMAIN, APP_PORT)
- Leverage common stack-level environment variables where appropriate
- Configure Traefik labels for reverse proxy integration using environment variables
- Add homepage integration labels
- Define volumes for data persistence
- Include metadata.yaml for CLI integration and user configuration prompts
- Use the `nautical-backup` labels for backup integration

### Label Integration System
Apps automatically integrate with core stack capabilities through Docker labels:

#### Traefik Reverse Proxy Integration:
- `traefik.enable=true` - Enable reverse proxy for the service
- `traefik.http.routers.${APP_NAME}.rule=Host(`${APP_DOMAIN}.${HOME_SERVER_DOMAIN}`) || Host(`${APP_DOMAIN}.localhost`)'` - Define routing rules using environment variables
- `traefik.http.services.${APP_NAME}.loadbalancer.server.port=${APP_PORT}` - Specify port to use for load balancing
- `traefik.docker.network=${STACK_NAME}_${TRAEFIK_NETWORK}` - Specify the network Traefik uses

#### Homepage Integration:
- `homepage.group=Homepage_Group` - Group name for service on homepage
- `homepage.name=Homepage_Name` - Display name for service on homepage
- `homepage.icon=jellyfin.png` - Icon file (select from homarr-labs/dashboard-icons)
- `homepage.href=http://${APP_DOMAIN}.${HOME_SERVER_DOMAIN}/` - Access URL for service
- `homepage.description=Media server` - Description of the service

#### Nautical Backup Integration:
- `nautical-backup.override-source-dir=${STACK_NAME}_container_name` - Backup source directory
- `nautical-backup.additional-folders=${STACK_NAME}_container_name` - Additional folders to back up

### Environment Configuration:
- Apps should use sensible defaults in `default.env`
- Stack-specific configurations override app defaults via environment substitution
- Leverage common stack environment variables when possible
- Use `.env` files for sensitive data
- Do not modify configurations directly in app recipes; override in stack instead

### Networking:
- Use `traefik-net` for services accessible via reverse proxy
- Create app-specific networks for internal communication
- Note: Avoid connecting containers to multiple networks simultaneously due to potential routing issues

### CLI Integration:
- Apps can define `userConfig` in metadata.yaml for interactive prompts during stack creation
- Volume mounts can be prompted for during stack creation
- Post-installation instructions can be defined in metadata.yaml
- The CLI tool will automatically generate appropriate environment variable values based on user input

## Core Capabilities

### Foundation Stacks:
- **Traefik**: Reverse proxy for routing requests
- **Authentik**: Single sign-on and LDAP authentication
- **Homepage**: Dashboard for accessing server apps
- **Portainer**: Docker container management
- **Nautical**: Backup automation
- **Tailscale**: Secure VPN connectivity
- **PiHole**: Network-wide ad blocking

### Composability Features:
- Docker Compose `include` directive for modular composition
- Environment variable override system
- Automatic DNS record generation
- Consistent labeling for service discovery

## Common Development Tasks

### Adding a New App:
For detailed instructions on creating a new app, see `Docs/Creating-New-Apps.md`.
1. Copy template from `Apps/Template/`
2. Configure `compose.yml` with appropriate labels and networking
3. Set up `default.env` with appropriate defaults
4. Add `metadata.yaml` with app information and prompts
5. Test integration with existing stacks

### Creating a New Stack:
1. Use `servercraft create <stack-name>` CLI command
2. Or manually create in `Stacks/<stack-name>/`
3. Configure `compose.yml` with desired includes
4. Set up `.env` file with overrides
5. Test deployment with `docker compose up -d`

### Modifying Existing Stacks:
1. Edit `compose.yml` in the stack directory
2. Add/remove apps or substacks as needed
3. Update environment variables in `.env` file if necessary
4. Test changes with `servercraft start <stack-name>`
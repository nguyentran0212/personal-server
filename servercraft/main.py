import os
import shutil
import ipaddress
import secrets
from pathlib import Path

import yaml
import typer
import questionary
from dotenv import dotenv_values

app = typer.Typer(help="Servercraft CLI: scaffold Docker stacks with apps & foundations")

ROOT_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT_DIR / "Apps"
SUBSTACKS_DIR = ROOT_DIR / "Substacks"
STACKS_DIR = ROOT_DIR / "Stacks"
TEMPLATE_STACK = STACKS_DIR / "Template"

def scan_foundations():
    foundations = []
    for p in SUBSTACKS_DIR.iterdir():
        if p.is_dir() and p.name.startswith("Foundation-"):
            if (p / "compose.yml").exists():
                foundations.append((p.name, p))
    return foundations

def scan_apps():
    apps = []
    for p in APPS_DIR.iterdir():
        if p.is_dir() and (p / "compose.yml").exists() and (p / "default.env").exists():
            apps.append((p.name, p))
    return apps

@app.command()
def init(stack_name: str):
    """
    Initialize a new Docker stack named STACK_NAME.
    """
    dest = STACKS_DIR / stack_name
    if dest.exists():
        typer.secho(f"Error: stack {stack_name} already exists.", fg=typer.colors.RED)
        raise typer.Exit(1)
    shutil.copytree(TEMPLATE_STACK, dest)

    # Top-level prompts
    top = {}
    top["STACK_NAME"] = stack_name
    top["HOME_SERVER_DOMAIN"] = questionary.text("Home server domain:").ask()
    top["HOME_SERVER_TZ"] = questionary.text("Home server timezone:").ask()
    top["LAN_CIDR"] = questionary.text("LAN CIDR (e.g. 192.168.1.0/24):").ask()
    top["MEDIA_DIR"] = questionary.text("Media directory:").ask()
    top["WORK_DIR"] = questionary.text("Work directory:").ask()

    # Foundation choice
    foundations = scan_foundations()
    names = [name for name, _ in foundations]
    choice = questionary.select("Choose foundation:", choices=names).ask()
    foundation_path = dict(foundations)[choice]

    # App selection
    apps = scan_apps()
    app_names = [name for name, _ in apps]
    selected = questionary.checkbox("Select apps:", choices=app_names).ask()
    app_paths = [dict(apps)[name] for name in selected]

    # Update compose.yml includes
    compose_file = dest / "compose.yml"
    compose_data = yaml.safe_load(compose_file.read_text())
    include = []
    include.append({"path": os.path.relpath(foundation_path / "compose.yml", dest)})
    for app_path in app_paths:
        include.append({
            "path": os.path.relpath(app_path / "compose.yml", dest),
            "env_file": [os.path.relpath(app_path / "default.env", dest)]
        })
    compose_data["include"] = include
    compose_file.write_text(yaml.safe_dump(compose_data, sort_keys=False))

    # Build .env
    template_env = (dest / "default.env").read_text().splitlines()
    out_lines = []
    # Group 1: Top-Level
    for line in template_env:
        if line.strip().startswith("#"):
            out_lines.append(line)
            continue
        key = line.split("=", 1)[0]
        if key in top:
            out_lines.append(f'{key}="{top[key]}"')
        else:
            out_lines.append(line)
    out_lines.append("")

    # Group 2: Foundation
    fe = foundation_path / "default.env"
    if fe.exists():
        out_lines.append(f"# {choice} settings")
        for line in fe.read_text().splitlines():
            if line.strip().startswith("#"):
                out_lines.append(line)
                continue
            key, _, val = line.partition("=")
            if val.strip() == "":
                user_val = questionary.text(f"{key} (foundation):").ask() or ""
                out_lines.append(f'{key}="{user_val}"')
            else:
                out_lines.append(line)
    out_lines.append("")

    # PiHole DNS auto-generation
    network = ipaddress.ip_network(top["LAN_CIDR"], strict=False)
    hosts = list(network.hosts())
    server_ip = hosts[0] if hosts else network.network_address
    records = []
    for app_path in app_paths:
        env_map = dotenv_values(app_path / "default.env")
        for k, v in env_map.items():
            if k.endswith("_DOMAIN") and v:
                fqdn = f"{v}.{top['HOME_SERVER_DOMAIN']}"
                records.append(f"{fqdn}:{server_ip}")
    out_lines.append("# PiHole local DNS")
    out_lines.append(f'PIHOLE_LOCAL_DNS_RECORDS="{";".join(records)}"')
    out_lines.append("")

    # Group 3: App-Specific
    for app_path in app_paths:
        name = app_path.name
        out_lines.append(f"# {name} settings")
        env_map = dotenv_values(app_path / "default.env")
        for k in env_map:
            if k.startswith("SECRET_") or k.endswith("_KEY"):
                val = secrets.token_urlsafe()
                out_lines.append(f'{k}="{val}"')
            elif k.startswith("OIDC_"):
                out_lines.append(f'{k}="CHANGE_ME"')
        out_lines.append("")

    (dest / ".env").write_text("\n".join(out_lines))

    # Make scripts executable
    for script in ["start.sh", "stop.sh"]:
        p = dest / script
        p.chmod(p.stat().st_mode | 0o111)

    typer.secho(f"Stack '{stack_name}' created successfully!", fg=typer.colors.GREEN)
    typer.echo(f"Next steps:\n  cd {dest}\n  docker compose up -d")

def main():
    app()

if __name__ == "__main__":
    main()

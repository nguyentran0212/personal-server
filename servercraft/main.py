import os
import shutil
import ipaddress
import secrets
import socket
from pathlib import Path

import yaml
import typer
import questionary
from dotenv import dotenv_values
import subprocess

try:
    from zoneinfo import available_timezones
except ImportError:
    available_timezones = None

app = typer.Typer(help="Servercraft CLI: scaffold Docker stacks with apps & foundations")

ROOT_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT_DIR / "Apps"
SUBSTACKS_DIR = ROOT_DIR / "Substacks"
STACKS_DIR = ROOT_DIR / "Stacks"
TEMPLATE_STACK = STACKS_DIR / "Template"

def get_default_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = None
    finally:
        s.close()
    return ip

def prompt_dir(prompt: str, default: str = "") -> str:
    dangerous_dirs = {
        Path("/"), Path("/root"), Path("/etc"),
        Path("/usr"), Path("/bin"), Path("/dev"), Path("/sys")
    }
    while True:
        user_input = questionary.text(prompt, default=default).ask() or ""
        expanded = Path(user_input).expanduser()
        try:
            abs_path = expanded.resolve()
        except Exception:
            abs_path = expanded.absolute()
        # Confirm expansion
        if not questionary.confirm(f"Use directory '{abs_path}'?").ask():
            continue
        # Warn on dangerous directories
        if abs_path in dangerous_dirs:
            if not questionary.confirm(
                f"'{abs_path}' is a system directory. Are you sure you want to use it?"
            ).ask():
                continue
        # Check existence
        if abs_path.exists():
            return str(abs_path)
        # Offer retry if missing
        if questionary.confirm(f"Directory '{abs_path}' does not exist. Try again?").ask():
            continue
        return str(abs_path)

def prompt_cron_schedule() -> str:
    """
    Prompt the user to define backup frequency and construct a cron string.
    """
    freq = questionary.select(
        "How often should backups run?",
        choices=["Hourly", "Daily", "Weekly", "Custom"]
    ).ask()
    if freq == "Hourly":
        return "0 * * * *"
    elif freq == "Daily":
        time_str = questionary.text("Daily backup time (HH:MM):", default="04:00").ask()
        hour, minute = time_str.split(":")
        return f"{minute} {hour} * * *"
    elif freq == "Weekly":
        day = questionary.select(
            "Day of week for weekly backups:",
            choices=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        ).ask()
        time_str = questionary.text("Time of day (HH:MM):", default="04:00").ask()
        hour, minute = time_str.split(":")
        dow_map = {
            "Monday":"1","Tuesday":"2","Wednesday":"3","Thursday":"4",
            "Friday":"5","Saturday":"6","Sunday":"0"
        }
        return f"{minute} {hour} * * {dow_map[day]}"
    else:
        minute = questionary.text("Cron minute [0-59]:", default="0").ask()
        hour = questionary.text("Cron hour [0-23]:", default="4").ask()
        dom = questionary.text("Cron day of month [1-31]:", default="*").ask()
        month = questionary.text("Cron month [1-12]:", default="*").ask()
        dow = questionary.text("Cron day of week [0-6]:", default="*").ask()
        return f"{minute} {hour} {dom} {month} {dow}"

def scan_foundations():
    foundations = []
    for p in SUBSTACKS_DIR.iterdir():
        if p.is_dir() and p.name.startswith("Foundation-") and (p / "compose.yml").exists():
            meta_file = p / "metadata.yaml"
            if meta_file.exists():
                meta = yaml.safe_load(meta_file.read_text())["metadata"]
                display = f"{meta['name']} - {meta.get('description','')}"
            else:
                display = p.name
            foundations.append((display, p))
    return foundations

def scan_apps():
    apps = []
    for p in APPS_DIR.iterdir():
        if p.is_dir() and (p / "compose.yml").exists() and (p / "default.env").exists():
            meta_file = p / "metadata.yaml"
            if not meta_file.exists():
                continue
            meta = yaml.safe_load(meta_file.read_text())["metadata"]
            if meta.get("type") != "app":
                continue
            display = f"{meta['name']} - {meta.get('description','')}"
            apps.append((display, p))
    return apps

@app.command("create")
def create(stack_name: str):
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
    top["HOME_SERVER_DOMAIN"] = questionary.text("Home server domain (leave it to localhost if you are not accessing it from LAN or Internet):", default="localhost").ask()
    # Timezone selection
    if available_timezones:
        tz_choices = sorted(available_timezones())
        top["HOME_SERVER_TZ"] = questionary.autocomplete(
            "Home server timezone:", choices=tz_choices, validate=lambda val: val in tz_choices
        ).ask()
    else:
        top["HOME_SERVER_TZ"] = questionary.text("Home server timezone:").ask()
    # LAN CIDR with detected default IP
    default_ip = get_default_ip()
    default_cidr = f"{default_ip}/24" if default_ip else ""
    while True:
        cidr_ans = questionary.text("LAN CIDR (e.g. 192.168.1.0/24):", default=default_cidr).ask()
        try:
            ipaddress.ip_network(cidr_ans, strict=False)
            top["LAN_CIDR"] = cidr_ans
            break
        except ValueError:
            typer.secho(f"Invalid CIDR '{cidr_ans}'. Please enter a valid CIDR.", fg=typer.colors.RED)
    # Directories with existence check
    top["MEDIA_DIR"] = prompt_dir("Media directory:", default="")
    top["WORK_DIR"] = prompt_dir("Work directory:", default="")
    # Nautical backup settings
    # Infer backup source directory
    try:
        output = subprocess.run(
            ["docker", "info", "--format", "{{ .DockerRootDir }}"],
            capture_output=True, text=True
        ).stdout.strip()
        backup_source = f"{output}/volumes" if output else "/var/lib/docker/volumes"
    except Exception:
        backup_source = "/var/lib/docker/volumes"
    top["BACKUP_SOURCE_DIR"] = backup_source
    top["BACKUP_DESTINATION_DIR"] = prompt_dir("Backup destination directory:", default="~/backups")
    top["BACKUP_SCHEDULE"] = prompt_cron_schedule()

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
            if key == "PIHOLE_LOCAL_DNS_RECORDS":
                continue
            if val.strip() == "":
                user_val = questionary.text(f"{key} (foundation):").ask() or "CHANGE_ME"
                out_lines.append(f'{key}="{user_val}"')
            else:
                out_lines.append(line)
    out_lines.append("")

    # PiHole DNS auto-generation
    network = ipaddress.ip_network(top["LAN_CIDR"], strict=False)
    hosts = list(network.hosts())
    server_ip = hosts[0] if hosts else network.network_address
    records = []
    # include apps inside foundation substack
    f_compose = foundation_path / "compose.yml"
    if f_compose.exists():
        f_data = yaml.safe_load(f_compose.read_text())
        for inc in f_data.get("include", []):
            path_str = inc.get("path", "")
            if "/Apps/" in path_str:
                app_dir = (foundation_path / path_str).resolve().parent
                env_map = dotenv_values(app_dir / "default.env")
                for k, v in env_map.items():
                    if k.endswith("_DOMAIN") and v:
                        fqdn = f"{v}.{top['HOME_SERVER_DOMAIN']}"
                        records.append(f"{server_ip} {fqdn}")
    # selected app-specific records
    for app_path in app_paths:
        env_map = dotenv_values(app_path / "default.env")
        for k, v in env_map.items():
            if k.endswith("_DOMAIN") and v:
                fqdn = f"{v}.{top['HOME_SERVER_DOMAIN']}"
                records.append(f"{server_ip} {fqdn}")
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

    typer.secho(f"Stack '{stack_name}' created successfully!", fg=typer.colors.GREEN)
    # Post‐install inspection
    inspect_stack(stack_name)

@app.command("inspect")
def inspect_stack(stack_name: str):
    """
    Inspect and summarize stack configuration and highlight variables needing attention.
    """
    dest = STACKS_DIR / stack_name
    env_file = dest / ".env"
    if not env_file.exists():
        typer.secho(f"No .env file found for stack {stack_name}", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Load environment variables
    env_map = dotenv_values(env_file)

    # General configuration
    typer.secho("General Configuration:", fg=typer.colors.CYAN)
    for key in ["STACK_NAME", "HOME_SERVER_DOMAIN", "HOME_SERVER_TZ", "LAN_CIDR", "MEDIA_DIR", "WORK_DIR"]:
        typer.echo(f"  {key}: {env_map.get(key)}")

    # Load compose includes to determine foundation and apps
    compose_file = dest / "compose.yml"
    compose_data = yaml.safe_load(compose_file.read_text())
    includes = compose_data.get("include", [])

    # Foundation
    if includes:
        foundation_path = Path(dest, includes[0]["path"]).resolve()
        foundation_name = foundation_path.parent.name
        typer.secho(f"Foundation: {foundation_name}", fg=typer.colors.CYAN)

    # Apps
    app_list = []
    for inc in includes:
        p = inc.get("path", "")
        if "/Apps/" in p:
            app_name = Path(dest, p).resolve().parent.name
            app_list.append(app_name)
    typer.secho("Apps:", fg=typer.colors.CYAN)
    if app_list:
        for a in app_list:
            typer.echo(f"  - {a}")
    else:
        typer.echo("  (none)")

    # Identify missing or placeholder environment variables
    missing = [(k, v) for k, v in env_map.items() if v in ("", None) or v == "CHANGE_ME"]
    if missing:
        typer.secho("Variables needing attention:", fg=typer.colors.YELLOW)
        for k, v in missing:
            status = "missing" if v in ("", None) else "placeholder"
            typer.echo(f"  {k}: {status}")
        # Tailor guidance
        if any(k == "TS_AUTHKEY" for k, _ in missing):
            typer.secho("- Tailscale: generate an auth key at https://login.tailscale.com/admin/settings/keys and set TS_AUTHKEY.", fg=typer.colors.GREEN)
            dom = env_map.get("HOME_SERVER_DOMAIN")
            typer.secho(f"- Verify DNS records in Tailscale dashboard point {dom} to your server's Tailscale IP.", fg=typer.colors.GREEN)
        if any(k.startswith("OIDC_") for k, _ in missing):
            typer.secho("- OIDC: after initial deploy, in Authentik admin create OAuth clients for each service and set OIDC_CLIENT_ID/SECRET vars in .env.", fg=typer.colors.GREEN)
    else:
        typer.secho("All environment variables are set.", fg=typer.colors.GREEN)

    typer.echo("Inspection complete.")

@app.command("start")
def start_stack(stack_name: str):
    """
    Start an existing Docker stack named STACK_NAME.
    """
    dest = STACKS_DIR / stack_name
    env_file = dest / ".env"
    if not env_file.exists():
        typer.secho(f"Error: .env file not found for stack {stack_name}.", fg=typer.colors.RED)
        typer.echo("Please configure your environment file or create a new stack with 'servercraft create'.")
        raise typer.Exit(1)
    result = subprocess.run(["docker", "compose", "up", "-d"], cwd=str(dest))
    if result.returncode != 0:
        typer.secho("Failed to start stack services.", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"Stack '{stack_name}' started.", fg=typer.colors.GREEN)

@app.command("stop")
def stop_stack(stack_name: str):
    """
    Stop a running Docker stack named STACK_NAME.
    """
    dest = STACKS_DIR / stack_name
    # Check if any services are running
    result_ps = subprocess.run(["docker", "compose", "ps"], cwd=str(dest), capture_output=True, text=True)
    lines = result_ps.stdout.strip().splitlines()
    if len(lines) <= 1:
        typer.secho(f"Stack '{stack_name}' is not running.", fg=typer.colors.YELLOW)
        raise typer.Exit(0)
    env_file = dest / ".env"
    if not env_file.exists():
        typer.secho(f"Error: .env file not found for stack {stack_name}. Cannot stop automatically.", fg=typer.colors.RED)
        raise typer.Exit(1)
    result_down = subprocess.run(["docker", "compose", "down"], cwd=str(dest))
    if result_down.returncode != 0:
        typer.secho("Failed to stop stack services.", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"Stack '{stack_name}' stopped.", fg=typer.colors.GREEN)

# List available apps and stacks
@app.command("list-apps")
def list_apps():
    """
    List all available applications.
    """
    apps = scan_apps()
    if not apps:
        typer.echo("No available apps found.")
        return
    for display, _ in apps:
        typer.echo(f"- {display}")

@app.command("list-stacks")
def list_stacks():
    """
    List all available stacks (excluding Template).
    """
    stacks = [p.name for p in STACKS_DIR.iterdir() if p.is_dir() and p.name != "Template"]
    if not stacks:
        typer.echo("No stacks found.")
        return
    for s in sorted(stacks):
        typer.echo(f"- {s}")

def main():
    app()

if __name__ == "__main__":
    main()

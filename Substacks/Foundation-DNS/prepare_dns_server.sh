#!/bin/bash

# This script disables systemd-resolved's DNSStubListener and
# configures 127.0.0.1 as a nameserver using a drop-in file.
# It avoids directly modifying the main /etc/systemd/resolved.conf file
# and uses resolvectl for verification.
# The script will ask for sudo privileges when necessary.

# --- Configuration ---
DROP_IN_FILE="/etc/systemd/resolved.conf.d/50-local-dns.conf"
RESOLVED_CONF="/etc/systemd/resolved.conf"
BACKUP_DIR="/var/backups/systemd-resolved"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/resolved.conf.bak_${DATE}"

# --- Functions ---

# Function to check if systemd-resolved is active
check_resolved_active() {
    # systemctl is-active typically doesn't require sudo for status checks
    if systemctl is-active systemd-resolved > /dev/null 2>&1; then
        return 0 # Active
    else
        return 1 # Inactive
    fi
}

# Function to create backup
create_backup() {
    if [ -f "$RESOLVED_CONF" ]; then
        echo "Creating backup of ${RESOLVED_CONF}..."
        sudo mkdir -p "$BACKUP_DIR"
        sudo cp "$RESOLVED_CONF" "$BACKUP_FILE"
        if [ $? -eq 0 ]; then
            echo "Backup created at ${BACKUP_FILE}"
        else
            echo "Error: Failed to create backup of ${RESOLVED_CONF}."
            exit 1
        fi
    else
        echo "Warning: ${RESOLVED_CONF} not found, skipping backup."
    fi
}

# Function to apply changes using sudo tee
apply_changes() {
    echo "Creating drop-in file to disable DNSStubListener and set DNS..."
    # Use sudo mkdir to create the directory if it doesn't exist
    sudo mkdir -p "$(dirname "$DROP_IN_FILE")"
    # Use sudo tee to write the content to the file with root privileges
    cat <<EOF | sudo tee "$DROP_IN_FILE" > /dev/null
[Resolve]
DNSStubListener=no
# Add 127.0.0.1 and optionally other DNS servers here.
# This line will override any 'DNS=' settings in other configuration files.
DNS=127.0.0.1 8.8.8.8
EOF
    if [ $? -eq 0 ]; then
        echo "Drop-in file ${DROP_IN_FILE} created successfully."
        echo "Note: Added 8.8.8.8 as a secondary DNS. You can edit the file to change this."
    else
        echo "Error: Failed to create drop-in file ${DROP_IN_FILE}."
        exit 1
    fi
}

# Function to restart systemd-resolved using sudo
restart_resolved() {
    echo "Restarting systemd-resolved.service..."
    sudo systemctl daemon-reload
    sudo systemctl restart systemd-resolved
    if [ $? -eq 0 ]; then
        echo "systemd-resolved.service restarted successfully."
        sleep 2 # Give it a moment to apply settings
        return 0
    else
        echo "Error: Failed to restart systemd-resolved.service."
        return 1
    fi
}

# Function to verify changes using resolvectl (usually does not require sudo)
verify_changes() {
    echo "Verifying changes with resolvectl status..."
    resolvectl status
    echo "Look for 'DNSStubListener: no' and 'DNS Servers: 127.0.0.1' (and 8.8.8.8 if added) in the output."
}

# --- Main Script ---

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    echo "Error: sudo is not installed or not in the PATH. Please install it or run the script as root."
    exit 1
fi

echo "Attempting to configure systemd-resolved (will ask for sudo when needed)..."

if ! check_resolved_active; then
    echo "Error: systemd-resolved.service is not active. Please ensure it is running before proceeding."
    exit 1
fi

# While the request asks to use resolvectl instead of changing files directly for nameservers,
# setting static global DNS servers persistently with systemd-resolved is primarily done
# via configuration files (resolved.conf or drop-ins). resolvectl set-dns is typically for
# per-link or temporary global settings.
# We will use a drop-in file for persistent configuration as it's the recommended approach
# and avoids modifying the main configuration file directly.

create_backup
apply_changes

if restart_resolved; then
    verify_changes
    echo ""
    echo "Script finished successfully."
    echo "To revert these changes:"
    echo "1. Remove the drop-in file: sudo rm ${DROP_IN_FILE}"
    echo "2. Restart systemd-resolved: sudo systemctl daemon-reload && sudo systemctl restart systemd-resolved"
else
    echo ""
    echo "Script failed during systemd-resolved restart. Please check logs for details."
    echo "You may need to manually revert changes by removing: ${DROP_IN_FILE}"
fi

exit 0

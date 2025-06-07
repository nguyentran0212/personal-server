# Backup Mechanism

## 1. Introduction

### 1.1. Purpose of backups in Servercraft stacks
Backups ensure that critical data stored in Docker volumes can be recovered in case of accidental deletion, corruption, or host failure. In Servercraft stacks, we integrate Nautical to provide scheduled, application-consistent volume backups.

### 1.2. Why we chose Nautical for volume-level backups
Nautical is a lightweight, containerized backup solution that:
- Operates as a Docker service with a built-in scheduler.
- Uses Docker labels to identify and group volumes.
- Creates compressed archives (`.tar.gz`) of specified volumes.
- Resumes application containers after snapshotting to maintain consistency.

## 2. How Nautical Is Wired into Your Stack

### 2.1. Nautical service definition in `Foundation-Local/compose.yml`
The foundation stack includes the Nautical service via:
```yaml
include:
  - path: "../../Apps/Nautical/compose.yml"
```
This brings in the Nautical container and its default configuration.

### 2.2. Docker Compose “include” of `Apps/Nautical/compose.yml`
By using our Compose “include” mechanism, Nautical is injected alongside core services (Traefik, Authentik, Homepage, etc.) without modifying their individual Compose files.

### 2.3. Overview of the Nautical container and its built-in scheduler
- Nautical reads three environment variables (`BACKUP_SOURCE_DIR`, `BACKUP_DESTINATION_DIR`, `BACKUP_SCHEDULE`) to locate volumes, choose a destination, and schedule tasks.
- It scans containers by Docker labels, groups them, pauses them, archives volumes, then resumes them.

## 3. Grouping Services & Volumes via Nautical Labels

### 3.1. nautical-backup.group
Assign the **same group name** (e.g. `authentik`) to all related services so Nautical will:
1. Pause every container in the group.
2. Snapshot each specified volume.
3. Resume the containers together.
This ensures a consistent state across multi-container applications.

### 3.2. nautical-backup.override-source-dir
Explicitly points Nautical at the host’s Docker volume directory for a given service. For example:
- `${STACK_NAME}_database`
- `${STACK_NAME}_redis`  
This overrides the default scan of `BACKUP_SOURCE_DIR` and targets exactly the named volume.

### 3.3. nautical-backup.source-dir-required
When set to `false` on stateless services (application servers or workers), Nautical:
- Still includes those containers in the **pause/resume** sequence.
- Skips volume backup for them, avoiding errors when no volume is present.

### 3.4. Authentik Example
```yaml
services:
  authentik-postgresql:
    labels:
      - "nautical-backup.group=authentik"
      - "nautical-backup.override-source-dir=${STACK_NAME}_database"
  authentik-redis:
    labels:
      - "nautical-backup.group=authentik"
      - "nautical-backup.override-source-dir=${STACK_NAME}_redis"
  authentik-server:
    labels:
      - "nautical-backup.group=authentik"
      - "nautical-backup.source-dir-required=false"
  authentik-worker:
    labels:
      - "nautical-backup.group=authentik"
      - "nautical-backup.source-dir-required=false"
```

## 4. Controlling Backup Behavior with Environment Variables

### 4.1. BACKUP_SOURCE_DIR
- **Definition**: Host path where Docker stores its `volumes/` directory.
- **Default**: Inferred automatically via:
  ```
  docker info --format '{{ .DockerRootDir }}'
  ```
  with `/volumes` appended (or `/var/lib/docker/volumes` fallback).

### 4.2. BACKUP_DESTINATION_DIR
- **Definition**: Directory where Nautical writes compressed archives.
- **Default**: `~/backups` (configurable via CLI prompt).

### 4.3. BACKUP_SCHEDULE
- **Definition**: Cron-style string driving Nautical’s scheduler.
- **Format**:
  - Hourly: `0 * * * *`
  - Daily at HH:MM: `MM HH * * *`
  - Weekly: `MM HH * * DOW`
  - Custom: any valid `m h dom month dow` expression.

## 5. Using the Servercraft CLI to Set Up & Inspect Backups

### 5.1. servercraft create <stack>
- **Auto-detects** `BACKUP_SOURCE_DIR`.
- **Prompts** for `BACKUP_DESTINATION_DIR` using the directory picker.
- **Builds** `BACKUP_SCHEDULE` via a friendly wizard (no raw cron entry).

### 5.2. servercraft inspect <stack>
- Displays current values for `BACKUP_SOURCE_DIR`, `BACKUP_DESTINATION_DIR`, and `BACKUP_SCHEDULE`.
- Highlights any missing or invalid entries.

### 5.3. Updating backup settings on an existing stack
- **Edit** the stack’s `.env` file directly.
- Or **re-run** the prompts via a future `servercraft update` command (TBD).

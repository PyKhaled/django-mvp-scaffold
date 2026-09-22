# Backup and restore

## Preconditions

Identify the database, bucket, release revision, recovery-point objective,
recovery-time objective, retention period, and incident owner. Use PostgreSQL
client tools compatible with the server and a protected backup destination outside
the checkout. Provision backup credentials through a restricted password file or
secret store, not a password embedded in command history.

Database backups contain personal data and ticket capabilities. Encrypt and
restrict access to them. A database dump alone does not back up GCS objects,
service credentials, deployment configuration, or PostgreSQL roles.

## Create a coordinated backup

1. Record UTC time, revision, migration state, and database identity.
2. For a database/media-consistent recovery point, drain all writers, including
   admin users. Application maintenance alone does not block superusers.
3. Set `BACKUP_DIR` to an existing protected directory; `POSTGRES_*` identify the
   source database. Configure PostgreSQL client authentication separately.

   ```sh
   umask 077
   : "${BACKUP_DIR:?Set a protected backup directory}"
   : "${POSTGRES_HOST:?Set the source host}"
   : "${POSTGRES_PORT:?Set the source port}"
   : "${POSTGRES_USER:?Set the source user}"
   : "${POSTGRES_DB:?Set the source database}"
   BACKUP_FILE="$BACKUP_DIR/product-$(date -u +%Y%m%dT%H%M%SZ).dump"
   pg_dump --host="$POSTGRES_HOST" --port="$POSTGRES_PORT"      --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"      --format=custom --file="$BACKUP_FILE"
   pg_restore --list "$BACKUP_FILE" > "$BACKUP_FILE.contents"
   shasum -a 256 "$BACKUP_FILE" > "$BACKUP_FILE.sha256"
   ```

   Stop on any failed command. An archive listing and checksum are integrity aids,
   not proof that the backup can be restored.
4. Use the storage platform's snapshot/version-preservation or copy process to
   preserve `mediafiles/`. Record bucket, object generations, recovery time, and
   retention. Merely enabling versioning now cannot recover previously deleted
   objects. Preserve the release's `staticfiles/` or verify reproducible rebuilds.
5. Store configuration references and database-role/grant recovery instructions
   separately. Resume writers only after recording the complete recovery point.

## Restore rehearsal or incident recovery

1. Start with a new empty, isolated PostgreSQL database and a separate media
   bucket. Confirm the destination identity before any write. Do not restore over
   the live database as a rehearsal. Disable outbound production email and public
   traffic in the isolated environment.
2. Verify the archive checksum from its backup directory:

   ```sh
   shasum -a 256 -c "$BACKUP_FILE.sha256"
   ```

3. Have the database operator create the empty destination and its application
   role. Set `RESTORE_HOST`, `RESTORE_PORT`, `RESTORE_USER`, and `RESTORE_DB` to that
   destination and configure its client authentication:

   ```sh
   : "${RESTORE_HOST:?Set an isolated restore host}"
   : "${RESTORE_PORT:?Set the restore port}"
   : "${RESTORE_USER:?Set the restore user}"
   : "${RESTORE_DB:?Set a new empty restore database}"
   pg_restore --host="$RESTORE_HOST" --port="$RESTORE_PORT"      --username="$RESTORE_USER" --dbname="$RESTORE_DB"      --no-owner --no-acl --exit-on-error --single-transaction "$BACKUP_FILE"
   ```

   Reapply reviewed application grants; ownership/ACLs are intentionally omitted.
4. Restore media from the matching recovery point. Configure an isolated copy of
   the application with the backed-up revision, restored database, separate Redis,
   restored bucket, and controlled email. Check migrations with `showmigrations`
   and `migrate --check` before deciding whether a newer release is appropriate.
5. Verify representative users, ticket/follow-up counts, login permissions,
   controlled secure-ticket access, and media retrieval. Record restore duration,
   row/object comparisons, and the latest recovered data timestamp.
6. For an actual incident, obtain the incident owner's acceptance of data loss,
   drain writers, switch the deployment to recovered services, then run the
   [deployment smoke checks](deployment.md). Keep the previous services isolated
   until acceptance; do not delete them during diagnosis.

If a rehearsal fails, preserve error output and leave live services unchanged.
A successful drill requires usable application data and media, not just a zero
exit code from `pg_restore`. Local SQLite recovery is separate: stop local writers
and use SQLite's backup facility, preserving `mediafiles/` alongside the database.

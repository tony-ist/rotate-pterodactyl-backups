# Rotate Pterodactyl Backups

This script uses Pterodactyl API to make backups of servers with specific tag in description, downloads backups to two
different physical drives and calls external rotation script. There is also restore backup script in this repo.

[RFC](https://docs.google.com/document/d/1gSQEY1mXGZBYNuF5cqelp8d80icmTJVJvaKWTPbTWg0/edit?usp=sharing)

## Usage

### Warning

Backup and restore procedures require you to set 2 or more backup slots for your pterodactyl server. Backup and restore always **delete** oldest backup in your server and then create new one so that you do not hit the backup limit. Restore deletes oldest backup because it needs to create one dummy backup. Currently `/api/client/servers/<id>/backups/<id>/restore` API endpoint is not intended for use other than via browser client. So instead it creates dummy backup, copies selected backup in its place, and then you manually press restore button in pterodactyl.

### Backup

```bash
copy .env.example .env
pipenv shell
pipenv install
```

* Edit the `.env` file.
* Set up a cron job to run `main.py` daily as a root. Rotations happen daily, and it's not configurable for now.

Example root cron job:

```bash
0 6 * * * PYTHONPATH=/opt/rotate-pterodactyl-backups /root/.local/share/virtualenvs/rotate-pterodactyl-backups-PWOIOIqs/bin/python /opt/rotate-pterodactyl-backups/src/main.py
```

### Restore

* Run `restore.py` script. You can then choose the server to restore backups for and backup which you want to restore.
* After script is done, head to the pterodactyl panel and restore backup with the provided name.

## TODO

* Read `rotate-backups.ini` configuration file via rotate-backups API

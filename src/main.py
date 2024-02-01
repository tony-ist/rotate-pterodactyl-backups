import os
import pathlib
import time

from dotenv import load_dotenv

from src.client import PterodactylClient
from src.util import iso_to_timestamp, copy, rotate_backups


def main():
    load_dotenv()

    api_key = os.environ['API_KEY']
    pterodactyl_url = os.environ['PTERODACTYL_URL']
    pterodactyl_backups_dir = os.environ['PTERODACTYL_BACKUPS_DIR']
    main_backups_dir = os.environ['MAIN_BACKUPS_DIR']
    reserve_backups_dir = os.environ['RESERVE_BACKUPS_DIR']
    # rotate_backups_config_path = os.environ['ROTATE_BACKUPS_CONFIG_PATH']
    client = PterodactylClient(api_key, pterodactyl_url)

    servers_to_backup = client.get_servers_to_backup()

    print('Servers to backup:', list(map(lambda server: server['attributes']['name'], servers_to_backup)))

    for server in servers_to_backup:
        # server_sid is abbreviation of server string id. Pterodactyl has three server ids:
        # internal integer id `internal_id`, string id `identifier` which is used here
        # and also `uuid`. First part of `uuid` is `identifier`.
        server_sid = server['attributes']['identifier']
        server_name = server['attributes']['name']
        oldest_backup = client.get_oldest_backup(server_sid)
        if oldest_backup:
            oldest_backup_uuid = oldest_backup['attributes']['uuid']
            client.delete_backup(server_sid, oldest_backup_uuid)
            print(f'Deleted old backup "{oldest_backup_uuid}" for server "{server_sid}" with name "{server_name}"')
        backup_response = client.make_backup(server_sid)
        backup_json = backup_response.json()
        backup_uuid = backup_json['attributes']['uuid']

        print(f'Started backup "{backup_uuid}" creation for server "{server_sid}" with name "{server_name}"')

        while True:
            print(f'Waiting for backup {backup_uuid} completion...')
            backup_details = client.backup_details(server_sid, backup_uuid).json()
            if backup_details['attributes']['completed_at']:
                break
            time.sleep(3)

        pterodactyl_backup_path = f'{pterodactyl_backups_dir}/{backup_uuid}.tar.gz'
        timestamp_iso = backup_json['attributes']['created_at']
        timestamp = iso_to_timestamp(timestamp_iso)
        backup_name_with_timestamp = f"{timestamp}_{backup_uuid}.tar.gz"

        server_uuid = server['attributes']['uuid']
        main_backup_path = f"{main_backups_dir}/{server_uuid}/{backup_name_with_timestamp}"
        reserve_backup_path = f"{reserve_backups_dir}/{server_uuid}/{backup_name_with_timestamp}"

        pathlib.Path(f"{main_backups_dir}/{server_uuid}").mkdir(parents=True, exist_ok=True)
        pathlib.Path(f"{reserve_backups_dir}/{server_uuid}").mkdir(parents=True, exist_ok=True)

        # Copy the backup to first and second drives
        # In case one of the drives fails we will still have a copy of the backup
        copy(pterodactyl_backup_path, main_backup_path)
        copy(pterodactyl_backup_path, reserve_backup_path)

        # Delete old backups on both drives so that we do not run out of space
        rotate_backups(f"{main_backups_dir}/{server_uuid}")
        rotate_backups(f"{reserve_backups_dir}/{server_uuid}")


if __name__ == '__main__':
    main()

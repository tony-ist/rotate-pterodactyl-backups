import os
import shutil
from datetime import datetime

from dotenv import load_dotenv

from src.client import PterodactylClient


def copy(file_path: str, destination_file_path: str):
    shutil.copy(file_path, destination_file_path)
    print(f"Copied '{file_path}' to '{destination_file_path}'")


def rotate_backups(folder_path: str):
    pass


def iso_to_timestamp(timestamp_utc):
    dt = datetime.fromisoformat(timestamp_utc)
    return "{:%Y_%m_%d_%H_%M_%S}".format(dt)


def main():
    load_dotenv()

    api_key = os.environ['API_KEY']
    pterodactyl_url = os.environ['PTERODACTYL_URL']
    pterodactyl_backups_dir = os.environ['PTERODACTYL_BACKUPS_DIR']
    main_backups_dir = os.environ['MAIN_BACKUPS_DIR']
    reserve_backups_dir = os.environ['RESERVE_BACKUPS_DIR']
    client = PterodactylClient(api_key, pterodactyl_url, pterodactyl_backups_dir)

    servers_to_backup = client.get_servers_to_backup()
    print(servers_to_backup)

    for server in servers_to_backup:
        # server_sid is abbreviation of server string id. Pterodactyl has two ids:
        # internal integer id and also string id which is used here and in urls
        server_sid = server['attributes']['identifier']
        server_name = server['attributes']['name']
        oldest_backup = client.get_oldest_backup(server_sid)
        print(oldest_backup)
        if oldest_backup:
            oldest_backup_uuid = oldest_backup['attributes']['uuid']
            client.delete_backup(server_sid, oldest_backup_uuid)
            print(f"Deleted old backup '{oldest_backup_uuid}' for server '{server_sid}' with name '{server_name}'")
        backup_response = client.make_backup(server_sid)
        backup_json = backup_response.json()
        backup_uuid = backup_json['attributes']['uuid']
        print('backup_response.json():', backup_json)

        pterodactyl_backup_path = f"/var/lib/pterodactyl/backups/{backup_uuid}.tar.gz"
        timestamp_iso = backup_json['attributes']['created_at']
        timestamp = iso_to_timestamp(timestamp_iso)
        backup_name_with_timestamp = f"{backup_uuid}_{timestamp}.tar.gz"

        print("backup_name_with_timestamp:", backup_name_with_timestamp)

        # Copy the backup to first and second drives
        # In case one of the drives fails we will still have a copy of the backup
        copy(pterodactyl_backup_path, f"{main_backups_dir}/{backup_name_with_timestamp}")
        copy(pterodactyl_backup_path, f"{reserve_backups_dir}/{backup_name_with_timestamp}")

    # Delete old backups on both drives so that we do not run out of space
    rotate_backups(main_backups_dir)
    rotate_backups(reserve_backups_dir)


if __name__ == '__main__':
    main()

import os
import urllib.parse

import requests
from dotenv import load_dotenv

from src.client import PterodactylClient

ENABLE_BACKUPS_TAG = 'ENABLE_AUTO_BACKUPS'


def main():
    load_dotenv()

    api_key = os.environ['API_KEY']
    pterodactyl_key = os.environ['PTERODACTYL_URL']
    pterodactyl_backups_dir = os.environ['PTERODACTYL_BACKUPS_DIR']
    client = PterodactylClient(api_key, pterodactyl_key, pterodactyl_backups_dir)

    servers_to_backup = client.get_servers_to_backup()

    for server in servers_to_backup:
        # server_sid is abbreviation of server string id: pterodactyl has internal integer id
        # and also external string id which is used here
        oldest_backup = client.get_oldest_backup(server_sid)
        if oldest_backup:
            client.delete_backup(oldest_backup_uuid)
        backup_uuid = client.make_backup(server_sid)

        # Copy the backup to first and second drives
        # In case one of the drives fails we will still have a copy of the backup
        copy(pterodactyl_backup_path, main_backups_dir)
        copy(pterodactyl_backup_path, reserve_backups_dir)

    # Delete old backups on both drives so that we do not run out of space # TODO: Move comment to function docstring
    rotate_backups(main_backups_dir)
    rotate_backups(reserve_backups_dir)

    backup_id = initiate_backup(options)

    servers_url = urllib.parse.urljoin(pterodactyl_url, '/api/client')

    servers_response = requests.get(servers_url, headers=headers)
    print(servers_response.text)
    servers = servers_response.json()['data']
    print(len(servers))

    servers_to_backup = list(filter(lambda s: ENABLE_BACKUPS_TAG in s['attributes']['description'], servers))
    print(len(servers_to_backup))

    for server in servers:
        print(server['attributes']['identifier'])

    server_id = '1d9fa352'
    backups_url = urllib.parse.urljoin(pterodactyl_url, f'/api/client/servers/{server_id}/backups')
    backups_response = requests.get(backups_url, headers=headers)
    print(backups_response.text)

    backup_id = '7f053d09-19e2-4e82-b1f6-432975a81a3b'
    backup_download_url = urllib.parse.urljoin(pterodactyl_url,
                                               f'/api/client/servers/{server_id}/backups/{backup_id}/download')
    backup_download_link_response = requests.get(backup_download_url, headers=headers)
    backup_download_link = backup_download_link_response.json()['attributes']['url']
    print(backup_download_link)

    backup_response = requests.get(backup_download_link)

    # with open('files/backup.tar.gz', 'wb') as file:
    #     file.write(backup_response.content)


if __name__ == '__main__':
    main()

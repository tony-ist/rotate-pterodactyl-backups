import os

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()

    headers = {
        'Authorization': 'Bearer ' + os.environ['API_KEY'],
        'Accept': 'Application/vnd.pterodactyl.v1+json',
        'Content-Type': 'application/json',
    }

    servers_response = requests.get("http://localhost/api/client", headers=headers)
    print(servers_response.text)
    servers = servers_response.json()['data']

    for server in servers:
        print(server['attributes']['identifier'])

    server_id = "1d9fa352"
    backups_response = requests.get(f"http://localhost/api/client/servers/{server_id}/backups", headers=headers)
    print(backups_response.text)

    backup_id = "7f053d09-19e2-4e82-b1f6-432975a81a3b"
    backup_download_link_response = requests.get(f"http://localhost/api/client/servers/{server_id}/backups/{backup_id}/download", headers=headers)
    backup_download_link = backup_download_link_response.json()['attributes']['url']
    print(backup_download_link)

    backup_response = requests.get(backup_download_link)

    with open("files/backup.tar.gz", "wb") as file:
        file.write(backup_response.content)


if __name__ == '__main__':
    main()

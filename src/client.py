import urllib.parse

import requests

ENABLE_BACKUPS_TAG = 'ENABLE_AUTO_BACKUPS'


class PterodactylClient:
    api_key: str
    pterodactyl_url: str
    backups_dir: str

    def __init__(self, api_key: str, pterodactyl_url: str, backups_dir: str):
        self.api_key = api_key
        self.pterodactyl_url = pterodactyl_url
        self.headers = {
            'Authorization': 'Bearer ' + api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.backups_dir = backups_dir

    def request(self, method: str, url: str, payload: dict = None) -> requests.Response:
        full_url = urllib.parse.urljoin(self.pterodactyl_url, url)
        response = requests.request(method, full_url, headers=self.headers, data=payload)
        if not response.ok:
            raise Exception(f'Got response with status code {response.status_code}. Response: {response.text}')
        return response

    def get(self, url: str):
        return self.request('GET', url)

    def post(self, url: str):
        return self.request('POST', url)

    def delete(self, url: str):
        return self.request('DELETE', url)

    def get_servers_to_backup(self) -> list[dict]:
        servers_response = self.get('/api/client')
        servers = servers_response.json()['data']

        def has_backups_tag(server: dict) -> bool:
            return ENABLE_BACKUPS_TAG in server['attributes']['description']

        return list(filter(has_backups_tag, servers))

    def make_backup(self, server_sid: str):
        return self.post(f'/api/client/servers/{server_sid}/backups')

    def download_backup(self, backup_uuid: str, save_path: str):
        pass

    def delete_backup(self, server_sid: str, backup_uuid: str):
        return self.delete(f'/api/client/servers/{server_sid}/backups/{backup_uuid}')

    def get_oldest_backup(self, server_sid: str):
        response = self.get(f'/api/client/servers/{server_sid}/backups')
        backup_list = response.json()['data']

        if len(backup_list) == 0:
            return None

        return min(backup_list, key=lambda backup: backup['attributes']['created_at'])

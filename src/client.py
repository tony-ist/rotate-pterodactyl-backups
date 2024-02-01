import urllib.parse

import requests

ENABLE_BACKUPS_TAG = 'ENABLE_AUTO_BACKUPS'


class PterodactylClient:
    api_key: str
    pterodactyl_url: str

    def __init__(self, api_key: str, pterodactyl_url: str):
        self.api_key = api_key
        self.pterodactyl_url = pterodactyl_url
        self.headers = {
            'Authorization': 'Bearer ' + api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def request(self, method: str, url: str, payload: dict = None) -> requests.Response:
        full_url = urllib.parse.urljoin(self.pterodactyl_url, url)
        response = requests.request(method, full_url, headers=self.headers, json=payload)
        if not response.ok:
            raise Exception(f'Got response with status code {response.status_code}. Response: {response.text}')
        return response

    def get(self, url: str):
        return self.request('GET', url)

    def post(self, url: str, payload: dict = None):
        return self.request('POST', url, payload)

    def delete(self, url: str):
        return self.request('DELETE', url)

    def get_servers(self) -> list[dict]:
        servers_response = self.get('/api/client')
        return servers_response.json()['data']

    def get_servers_to_backup(self) -> list[dict]:
        servers = self.get_servers()

        def has_backups_tag(server: dict) -> bool:
            return ENABLE_BACKUPS_TAG in server['attributes']['description']

        return list(filter(has_backups_tag, servers))

    def make_backup(self, server_sid: str, name: str = None):
        payload = {'name': name} if name else None
        return self.post(f'/api/client/servers/{server_sid}/backups', payload)

    def backup_details(self, server_sid: str, backup_uuid: str):
        return self.get(f'/api/client/servers/{server_sid}/backups/{backup_uuid}')

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

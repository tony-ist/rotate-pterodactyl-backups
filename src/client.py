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

    def get_servers_to_backup(self) -> list[dict]:
        pass

    def make_backup(self, server_uuid: str) -> str:
        pass

    def download_backup(self, backup_uuid: str, save_path: str):
        pass

    def delete_backup(self, backup_uuid: str):
        pass

    def get_oldest_backup(self, server_uuid: str):
        pass

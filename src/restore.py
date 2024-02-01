import os
import time

import questionary
from dotenv import load_dotenv
from questionary import Choice
from yaspin import yaspin

from src.client import PterodactylClient
from src.util import copy


def server_to_choice(server: dict) -> Choice:
    server_name = server['attributes']['name']
    server_sid = server['attributes']['identifier']
    return Choice(f"{server_name} ({server_sid})", value=server)


def delete_oldest_backup_if_exists(client: PterodactylClient, server: dict):
    server_sid = server['attributes']['identifier']
    server_name = server['attributes']['name']
    oldest_backup = client.get_oldest_backup(server_sid)

    if oldest_backup:
        oldest_backup_uuid = oldest_backup['attributes']['uuid']
        oldest_backup_name = oldest_backup['attributes']['name']

        delete_confirmation_result = questionary.confirm(
            f'Deleting oldest backup "{oldest_backup_name}" ({oldest_backup_uuid}) '
            f'for server "{server_name}" ({server_sid})'
        ).ask()

        if not delete_confirmation_result:
            return

        client.delete_backup(server_sid, oldest_backup_uuid)
        print(f'Deleted backup "{oldest_backup_name}" ({oldest_backup_uuid}')


def get_backup_uuids(backups_dir: str, server_uuid: str) -> list[str]:
    try:
        files = os.listdir(f'{backups_dir}/{server_uuid}')
        return list(filter(lambda f: f.endswith('.tar.gz'), files))
    except FileNotFoundError:
        return []


def parse_backup_filename(backup_filename: str) -> tuple[str, str]:
    last_underscore_index = backup_filename.rfind('_')
    timestamp = backup_filename[:last_underscore_index]
    uuid = backup_filename[last_underscore_index+1:]
    return timestamp, uuid


def restore():
    load_dotenv()

    api_key = os.environ['API_KEY']
    pterodactyl_url = os.environ['PTERODACTYL_URL']
    main_backups_dir = os.environ['MAIN_BACKUPS_DIR']
    pterodactyl_backups_dir = os.environ['PTERODACTYL_BACKUPS_DIR']
    client = PterodactylClient(api_key, pterodactyl_url)

    servers = client.get_servers()

    server_choices = list(map(server_to_choice, servers))

    server_question = questionary.select(
        "Select server to restore backup for:",
        choices=server_choices
    )
    selected_server = server_question.ask()
    selected_server_uuid = selected_server['attributes']['uuid']
    selected_server_sid = selected_server['attributes']['identifier']
    selected_server_name = selected_server['attributes']['name']

    delete_oldest_backup_if_exists(client, selected_server)

    backup_uuids = get_backup_uuids(main_backups_dir, selected_server_uuid)

    if not backup_uuids:
        print(f'No backups for server "{selected_server_name}" in directory "{main_backups_dir}"')
        return

    backup_question = questionary.select(
        "Select backup to restore:",
        backup_uuids
    )

    selected_backup_filename = backup_question.ask()

    [selected_backup_timestamp, _] = parse_backup_filename(selected_backup_filename)
    dummy_backup_name = f'Restore backup at {selected_backup_timestamp}'
    dummy_backup_response = client.make_backup(selected_server_sid, dummy_backup_name)
    dummy_backup_json = dummy_backup_response.json()
    dummy_backup_uuid = dummy_backup_json['attributes']['uuid']

    print(dummy_backup_json)

    with yaspin(text='Making dummy backup...'):
        while True:
            backup_details = client.backup_details(selected_server_sid, dummy_backup_uuid).json()
            if backup_details['attributes']['completed_at']:
                break
            time.sleep(3)

    print(f'Created dummy backup with name "{dummy_backup_name}"')
    print('Replacing dummy backup file with selected backup file...')

    selected_backup_path = f'{main_backups_dir}/{selected_server_uuid}/{selected_backup_filename}'
    dummy_backup_path = f'{pterodactyl_backups_dir}/{dummy_backup_uuid}.tar.gz'
    copy(selected_backup_path, dummy_backup_path)

    print(f'Done. Now head to pterodactyl panel and restore backup with name "{dummy_backup_name}"')


if __name__ == '__main__':
    restore()
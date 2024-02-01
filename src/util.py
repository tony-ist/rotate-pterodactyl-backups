import shutil

import rotate_backups as rb
from datetime import datetime


def copy(source_file_path: str, destination_file_path: str):
    shutil.copy(source_file_path, destination_file_path)
    print(f"Copied '{source_file_path}' to '{destination_file_path}'")


def rotate_backups(folder_path: str, rotate_backups_config_path: str = "/etc/rotate-backups.ini"):
    rotator = rb.RotateBackups(rotation_scheme={'daily': 10, 'monthly': 3}, prefer_recent=True)
    # rotator.load_config_file(rotate_backups_config_path)
    rotation_commands = rotator.rotate_backups(folder_path)
    commands_args = list(map(lambda c: c.command, rotation_commands))
    print(f"Deleted old backups. Rotation commands ({len(rotation_commands)}):", commands_args)


def iso_to_timestamp(timestamp_utc):
    dt = datetime.fromisoformat(timestamp_utc)
    return "{:%Y_%m_%d_%H_%M_%S}".format(dt)
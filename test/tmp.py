from pathlib import Path
from typing import *

from googleapiutils.drive.drive import Drive, GoogleMimeTypes
from googleapiutils.utils import get_oauth2_creds

dir = Path("auth")

config_path = dir.joinpath("friday-institute-reports.credentials.json")

creds = get_oauth2_creds(client_config=config_path)

drive = Drive(creds=creds)

filepath = "googleapiutils/hey/what"

folder = "https://drive.google.com/drive/u/0/folders/1lWgLNquLCwKjW4lenekduwDZ3J7aqCZJ"
t_file = drive.create_drive_file_object(
    filepath=filepath,
    create_folders=True,
    parents=[folder],
    mime_type=GoogleMimeTypes.csv,
)


drive.permissions_create(folder, "mike7400@gmail.com", sendNotificationEmail=False)
perms = drive.permissions_list(folder)

for p in perms:
    print(p)

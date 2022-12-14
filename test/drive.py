from pathlib import Path
from typing import *

from googleapiutils2.drive.drive import Drive
from googleapiutils2.utils import get_oauth2_creds

dir = Path("auth")
config_path = dir.joinpath("friday-institute-reports.credentials.json")

creds = get_oauth2_creds(client_config=config_path)

drive = Drive(creds=creds)

test_folder = (
    "https://drive.google.com/drive/u/0/folders/1lWgLNquLCwKjW4lenekduwDZ3J7aqCZJ"
)

files = drive.list_children(parent_id=test_folder)
for file in files:
    print(file)


perms = drive.permissions_list(test_folder)

for p in perms:
    print(p)

ECF_FOLDER = (
    "https://drive.google.com/drive/u/0/folders/1fB2mj-hl7KIduiNidbWLlMAFXZ76GmN8"
)
filepath = "/Users/mkbabb/Programming/ecf-dedup/data/ECF Deduped.csv"

t_file = drive.upload_file(filepath=filepath, parents=[ECF_FOLDER], update=True)

a = drive.get()

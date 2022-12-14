from pathlib import Path
from typing import *

from googleapiutils2.sheets import Sheets, SheetSlice, SheetsValueRange
from googleapiutils2.utils import get_oauth2_creds

SHEET_URL = "https://docs.google.com/spreadsheets/d/1d07HFq7wSbYPsuwBoJcd1E1R4F14RkeN-3GUyzvWepw/edit#gid=0"

dir = Path("auth")
config_path = dir.joinpath("friday-institute-reports.credentials.json")

creds = get_oauth2_creds(client_config=config_path)
sheets = Sheets(creds=creds)

Sheet = SheetsValueRange(sheets, SHEET_URL)
Sheet1 = Sheet["Sheet1"]
slc = SheetSlice[2, ...]
Sheet1[slc].update([[1, 2]], auto_batch_size=2)
Sheet1[3, ...].update([[1, 2]], auto_batch_size=2)

sheets.batch_update(
    SHEET_URL,
    {
        slc: [["Gay vibes", "wow"]],
        "3:3": [["Gayer vibes", "wower"]],
    },
)

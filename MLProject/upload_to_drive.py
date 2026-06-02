import os
import json

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = json.loads(
    os.environ["GDRIVE_CREDENTIALS"]
)

credentials = Credentials.from_service_account_info(
    creds,
    scopes=[
        "https://www.googleapis.com/auth/drive"
    ]
)

service = build(
    "drive",
    "v3",
    credentials=credentials
)

ROOT_FOLDER_ID = os.environ[
    "GDRIVE_FOLDER_ID"
]

def create_folder(folder_name, parent_id):

    metadata = {

        "name": folder_name,

        "mimeType":
        "application/vnd.google-apps.folder",

        "parents": [parent_id]
    }

    folder = service.files().create(
        body=metadata,
        fields="id",
        supportsAllDrives=True
    ).execute()

    return folder["id"]


def upload_directory(
    local_dir,
    parent_drive_id
):

    for item_name in os.listdir(local_dir):

        item_path = os.path.join(
            local_dir,
            item_name
        )

        if os.path.isdir(item_path):

            folder_id = create_folder(
                item_name,
                parent_drive_id
            )

            print(
                f"Created Folder: {item_name}"
            )

            upload_directory(
                item_path,
                folder_id
            )

        else:

            print(
                f"Uploading: {item_name}"
            )

            metadata = {

                "name": item_name,

                "parents": [
                    parent_drive_id
                ]
            }

            media = MediaFileUpload(
                item_path,
                resumable=True
            )

            service.files().create(

                body=metadata,

                media_body=media,

                fields="id",

                supportsAllDrives=True

            ).execute()

def main():

    mlruns_dir = "./mlruns"

    artifacts_dir = "./artifacts"

    from datetime import datetime

    run_folder_name = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    root_run_folder = create_folder(
        run_folder_name,
        ROOT_FOLDER_ID
    )

    print(
        f"Created Root Folder: "
        f"{run_folder_name}"
    )

    if os.path.exists(
        mlruns_dir
    ):

        mlruns_folder = create_folder(
            "mlruns",
            root_run_folder
        )

        upload_directory(
            mlruns_dir,
            mlruns_folder
        )

    if os.path.exists(
        artifacts_dir
    ):

        artifacts_folder = create_folder(
            "artifacts",
            root_run_folder
        )

        upload_directory(
            artifacts_dir,
            artifacts_folder
        )

    print(
        "Upload Finished"
    )


if __name__ == "__main__":
    main()
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
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }

    folder = service.files().create(
        body=metadata,
        fields="id",
        supportsAllDrives=True
    ).execute()

    return folder["id"]

def upload_file(file_path, parent_id):

    filename = os.path.basename(file_path)

    print(f"Uploading: {filename}")

    metadata = {
        "name": filename,
        "parents": [parent_id]
    }

    media = MediaFileUpload(
        file_path,
        resumable=True
    )

    service.files().create(
        body=metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()

def main():

    artifacts_dir = "./artifacts"

    if not os.path.exists(artifacts_dir):
        raise FileNotFoundError(
            "Folder artifacts tidak ditemukan"
        )

    from datetime import datetime

    upload_folder_name = (
        "artifacts_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    drive_folder_id = create_folder(
        upload_folder_name,
        ROOT_FOLDER_ID
    )

    print(
        f"Created Drive Folder: {upload_folder_name}"
    )

    for file_name in os.listdir(
        artifacts_dir
    ):

        file_path = os.path.join(
            artifacts_dir,
            file_name
        )

        if os.path.isfile(
            file_path
        ):

            upload_file(
                file_path,
                drive_folder_id
            )

    print(
        "All artifacts uploaded successfully."
    )

if __name__ == "__main__":
    main()
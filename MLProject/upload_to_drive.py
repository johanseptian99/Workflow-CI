import os
import json
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds_env = os.environ.get("GDRIVE_CREDENTIALS")
if not creds_env:
    raise ValueError("Environment variable 'GDRIVE_CREDENTIALS' tidak ditemukan.")

creds = json.loads(creds_env)

credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)

service = build("drive", "v3", credentials=credentials)

ROOT_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")
if not ROOT_FOLDER_ID:
    raise ValueError("Environment variable 'GDRIVE_FOLDER_ID' tidak ditemukan.")


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
        raise FileNotFoundError("Folder ./artifacts tidak ditemukan di workspace GitHub Action.")

    upload_folder_name = "artifacts_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        drive_folder_id = create_folder(upload_folder_name, ROOT_FOLDER_ID)
        print(f"Created Drive Folder: {upload_folder_name} (ID: {drive_folder_id})")
    except Exception as e:
        print(f"Gagal membuat folder di Google Drive. Error: {e}")
        return

    uploaded_count = 0
    for file_name in os.listdir(artifacts_dir):
        file_path = os.path.join(artifacts_dir, file_name)

        if os.path.isfile(file_path):
            try:
                upload_file(file_path, drive_folder_id)
                uploaded_count += 1
            except Exception as e:
                print(f"Gagal mengupload {file_name}. Error: {e}")

    print(f"Selesai! Berhasil mengunggah {uploaded_count} artifact ke Google Drive.")


if __name__ == "__main__":
    main()
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

from logger.logging_config import logger


class GoogleManager():


    SCOPES = [
        'https://www.googleapis.com/auth/drive.file', 
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.appdata'
        ]


    def __init__(self):
        with open(".//google//token.json") as f:
            self.token_info = json.load(f) 
        with open(".//google//files.json") as f:
            self.files = json.load(f)
        self.credentials = Credentials.from_authorized_user_info(
            info=self.token_info, scopes=self.SCOPES)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = "1S2ldK5YLDyzxGKHM0VN267FtirpZPUc4"
    

    def upload_files_to_drive(self, files_include: list) -> None:
        for file_name in self.files:
            if file_name in files_include:
                print(file_name)
                self.upload_file_to_drive(file_name=file_name)
        self._save_files_file()


    def upload_file_to_drive(self, file_name: str):
        logger.info("Uploading file %s to drive...", file_name)
        file_path = self._get_file_path(file_name=file_name)
        file_body = MediaFileUpload(
            file_path, mimetype=self.files[file_name]["mime_type"],
            resumable=True
            )
        upload = self.drive_service.files()
        if self.files[file_name]["file_id"] is None:
            file_metadata = {
                "name": file_name, 
                "parents": [self.files[file_name]["folder_id"]]
                }   
            upload_file = (
                upload
                .create(
                    body=file_metadata, media_body=file_body, fields="id"
                    )
            )
        else:
            upload_file = upload.update(
                fileId=self.files[file_name]["file_id"],
                media_body=file_body, fields="id",
            )

        resp = upload_file.execute()
        logger.info(
            "File %s uploaded to drive to folder: %s.", 
            file_name, file_path
            )
        self._set_field_value(file_name=file_name, field_id=resp["id"])


    def _get_file_path(self, file_name: str):

        return self.files[file_name]["path"] + file_name
    

    def _set_field_value(self, file_name: str, field_id: int) -> None:
        self.files[file_name]["file_id"] = field_id


    def _save_files_file(self):
        with open(".//google//files.json", "w") as f:
            json.dump(self.files, f)






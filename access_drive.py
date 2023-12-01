from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
FOLDER_ID = '1VeT4QnsFMk-ni5_pTVubKrr6JGos6Irk'


credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=credentials)


def get_images(file_name):
    result = service.files().list(
        q=f"mimeType contains 'image/' and name contains '{file_name}' and '{FOLDER_ID}' in parents",
        spaces='drive',
        fields='files(id, name, parents)',
    ).execute()
    return result.get('files', [])

def save_files(files):
    for file in files:
        request = service.files().get_media(fileId=file['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

        with open(file['name'], 'wb') as f:
            fh.seek(0)
            f.write(fh.read())

if __name__ == '__main__':
    save_files(get_images('test-1'))

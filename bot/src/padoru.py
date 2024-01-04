import datetime
import io
import asyncio

import discord
from discord.ext import tasks

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from bot_config import client
import config

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = '../service_account.json'
FOLDER_ID = '1VeT4QnsFMk-ni5_pTVubKrr6JGos6Irk'

WHEN = datetime.time(6, 9, 0, tzinfo=config.TZINFO)
WHERE = 908128228701536270

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=credentials)


def get_images(file_name, exact=False):
    result = service.files().list(
        q=f"mimeType contains 'image/' and name {'=' if exact else 'contains'} '{file_name}' and '{FOLDER_ID}' in parents",
        spaces='drive',
        fields='files(id, name, mimeType)',
    ).execute()
    return result.get('files', [])


def download_file(file):
    request = service.files().get_media(fileId=file['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}.")

    fh.seek(0)
    return fh

@tasks.loop(time=WHEN)
async def send_padoru():  # Fired every day
    now = datetime.datetime.now(tz=config.TZINFO)
    if now.date().month != 12:
        return

    print("Sending padoru")

    day = now.date().day
    padoru_name = f"Padoru_{day}"

    channel = client.get_channel(WHERE)

    image = get_images(padoru_name, exact=True)
    if not image:
        await channel.send("Was about to send a padoru but I didn't find padoru image for today.")
        return

    image = image[0]

    filename = image['name']

    match image['mimeType'].split('/')[1]:
        case 'png':
            filename += '.png'
        case 'jpeg':
            filename += '.jpg'
        case 'webp':
            filename += '.webp'
        case _:
            await channel.send("Padoru is not a valid image")
            return
    img_blob = download_file(image)

    f = discord.File(img_blob, filename=filename)
    await channel.send(file=f)

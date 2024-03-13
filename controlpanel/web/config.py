import os

TZ = os.environ.get("TZ", 'Europe/Madrid')

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", 'bad_secret_key')

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", None)
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", None)
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", None)
CONTROL_PANEL_ADMIN_ID = os.environ.get("CONTROL_PANEL_ADMIN_ID", None)

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", 'localhost')
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", '5432')
POSTGRES_DB = os.environ.get("POSTGRES_DB", 'postgres')
POSTGRES_USER = os.environ.get("POSTGRES_USER", 'postgres')
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", '12345')

SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", 'https')

from bot_config import client
import config

# Bot command modules. They need to be included to process the @client.command decorator
import anime
import punishment
import music
import misc


@client.event
def on_ready():
    dev_channel = client.get_channel(config.DEV_CHANNEL_ID)
    await dev_channel.send("DIABLO Strike restarted and ready!")

def main():
    client.run(config.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()

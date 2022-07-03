from bot_config import client
import config

# Bot command modules. They need to be included to process the @client.command decorator
import bot.anime
import bot.punishment
import bot.music
import bot.misc


def main():
    client.run(config.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()

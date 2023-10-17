import argparse

from bot_config import client
import config

# Bot command modules. They need to be included to process the @client.command decorator
import anime # noqa F401
import punishment # noqa F401
from music import music
import misc  # noqa F401
import amplitugraphy # noqa F401


def main():
    parser = argparse.ArgumentParser('bot', description='Main program that runs the discrod bot')
    parser.add_argument(
        '-s',
        '--sync',
        action='store_true',
        help='Synchronizes the command tree with servers for slash commands'
    )
    args = parser.parse_args()

    client.sync = args.sync
    client.cog_classes = [music.Music]
    # client.groups = [test_hybrid.slash_group]

    client.run(config.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()

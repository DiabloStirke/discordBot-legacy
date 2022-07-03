import json
from typing import Union
from discord.ext.commands import has_permissions
from discord.ext.commands.context import Context
from discord import Member, Role
from bot_config import client
from utils import find_vc
from structlog import get_logger

logger = get_logger(__name__)


@has_permissions(administrator=True)
@client.command(aliases=['pconf'])
async def punishconf(ctx: Context, config: str, arg: Union[Role, str]):
    with open('data/punishment_roles.json', 'r') as conf:
        current_conf = json.load(conf)

    match config.lower():
        case 'role' | 'r':
            if not isinstance(arg, Role):
                await ctx.channel.send('You should mention the role with "@"')
                return
            guild_conf = current_conf.get(str(ctx.guild.id), {})
            guild_conf['role'] = arg.id
            current_conf[str(ctx.guild.id)] = guild_conf

        case 'channel' | 'ch' | 'c':
            arg = str(arg)
            vc = find_vc(ctx.guild, arg)
            if vc is None:
                await ctx.channel.send(f'Voice channel "{arg}" not found.')
                return
            guild_conf = current_conf.get(str(ctx.guild.id), {})
            guild_conf['channel'] = vc.id
            current_conf[str(ctx.guild.id)] = guild_conf

        case _:
            await ctx.channel.send('Not a valid config.')
            return

    with open('data/punishment_roles.json', 'w') as conf:
        json.dump(current_conf, conf)

    await ctx.channel.send('OK')


@client.command(aliases=['gulag', 'g', 'p'])
async def punish(ctx: Context, user: Member):
    # get punishment role
    with open('data/punishment_roles.json', 'r') as f_punishment_roles:
        punishment_roles_dict = json.load(f_punishment_roles)

    guild_conf = punishment_roles_dict.get(str(ctx.guild.id), None)

    if not guild_conf or not guild_conf.get('role', None):
        await ctx.channel.send('It seems that this feature is not configured yet on this server\n'
                               'To do so create a role with preferred permissions and add it '
                               'to my database sending ?punishconf role @role')

    if ctx.guild.get_role(guild_conf.get('role')) in user.roles and \
            ctx.guild.owner != ctx.author:
        await ctx.channel.send('You do not have permission')
        return

    initial_roles = user.roles[1:]
    logger.info(initial_roles)
    vc_stat = user.voice
    await user.remove_roles(*initial_roles, reason='punishment')

    # save punished user initial data
    with open('data/punished_users.json', 'r') as f_pu:
        pu_dict = json.load(f_pu)

    pu_dict[str(user.id)] = {
        'initial_roles': [role.id for role in initial_roles],
        'initial_vc': vc_stat.channel.id if vc_stat and vc_stat.channel else None
    }

    with open('data/punished_users.json', 'w') as f_pu:
        json.dump(pu_dict, f_pu)

    await user.add_roles(ctx.guild.get_role(guild_conf['role']))

    if user.voice and guild_conf.get('channel', None):
        await user.move_to(ctx.guild.get_channel(guild_conf['channel']))

    await ctx.channel.send(f'User {user.mention} was punished')


# @has_permissions(move_members=True, manage_roles=True)
@client.command(aliases=['pa', 'forgive', 'f'])
async def pardon(ctx: Context, user: Member):
    with open('data/punishment_roles.json', 'r') as f_punishment_roles:
        punishment_roles_dict = json.load(f_punishment_roles)
        guild_conf = punishment_roles_dict.get(str(ctx.guild.id))
        punishment_role = guild_conf['role']

    if ctx.guild.get_role(punishment_role) in user.roles and \
            ctx.guild.owner != ctx.author:
        await ctx.channel.send('You do not have permission')
        return

    with open('data/punished_users.json', 'r') as f_pu:
        pu_dict = json.load(f_pu)

    logger.info(pu_dict)

    user_recovery_data = pu_dict.pop(str(user.id), None)
    logger.info(pu_dict)

    if not user_recovery_data:
        await ctx.channel.send('This user is not punished')
        return

    with open('data/punished_users.json', 'w') as f_pu:
        logger.info(pu_dict)
        json.dump(pu_dict, f_pu)

    await user.remove_roles(ctx.guild.get_role(punishment_role), reason='pardon')
    await user.add_roles(
        *[ctx.guild.get_role(role_id) for role_id in user_recovery_data['initial_roles']],
        reason='pardon'
    )
    if user.voice and user_recovery_data.get('initial_vc', None):
        await user.move_to(ctx.guild.get_channel(user_recovery_data['initial_vc']))

    await ctx.channel.send('OK')

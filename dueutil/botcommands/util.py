import discord

import time
from googletrans import Translator
translator = Translator()
import repoze.timeago

import generalconfig as gconf
from ..game.configs import dueserverconfig
from ..permissions import Permission
from ..game import stats, awards, weapons, quests, discoin
from ..game.stats import Stat
from .. import commands, events, util, permissions

# Shorthand for emoji as I use gconf to hold emoji constants
from ..game import emojis as e


@commands.command(args_pattern="S?")
@commands.require_cnf(warning="This will send a server invite to a designated support person, do not use this if you do not want them joining to help!")
@commands.ratelimit(cooldown=7200, error="You can't request support again for **[COOLDOWN]**! Give people some time to respond!", save=True)
async def requestsupport(ctx, cnf="", **details):
    """
    [CMD_KEY]requestsupport (cnf)
    This sends an invite to a designated support person who will come and help you if they are online.
    If your server requires a verified role, please give it to them without them going through the verification process, as they will likely leave when they are done.
    [PERM]
    """
    client = util.shard_clients[0]
    player = details["author"]
    server_id_1 = ctx.server.id
    server = util.get_server(server_id_1)
    server_channel = list(util.get_server(server_id_1).channels)[1]
    server_channel_list = list(util.get_server(server_id_1).channels)
    x = len(server_channel_list)
    check = 0
    try:
        if server_channel is not None and server is not None:
            invite = await util.get_client(server.id).create_invite(destination=server_channel, max_uses=5, unique=False)
            invite = str(invite)
            check += 1
    except:
        while x > 0:
            try:
                server_channel = list(util.get_server(server_id_1).channels)[x]
                if server_channel is not None and server is not None:
                    invite = await util.get_client(server.id).create_invite(destination=server_channel, max_uses=1, unique=False)
                    invite = str(invite)
                    check += 1
                    break
            except:
                pass
            x -= 1
    if check == 0:
        raise util.DueUtilException(ctx.channel, "I need to DM a support person the server invite link so they can join to help! Please give me invite creation perms for the server!")
    online_support_list = ["376166105917554701", "258868787183484928", "194875394439118848", "386553871063056394", "354900241365073920", "354900241365073920", "220169893063032832", "609733196782895125"]
    offline_support_list = ["376166105917554701", "258868787183484928", "194875394439118848", "386553871063056394", "354900241365073920", "354900241365073920", "220169893063032832", "609733196782895125"]
    online_now = []
    x = 0
    check = 0
    for support in online_support_list:
        member = discord.Member(user={"id": support})
        if member.status == "offline" or member.status == "dnd":
            x += 1
        else:
            online_now.append(support)
        if len(online_support_list) == x:
            check = 1
    member = discord.Member(user={"id": player.id})
    if check == 0:
        how_many_online = len(online_now)
        y = 0
        online = []
        if how_many_online == 1:
            check_2 = 1
            online.append(online_now[0])
            online_1 = discord.Member(user={"id": online[0]})
            await util.say(online_1, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
        if how_many_online == 2:
            check_2 = 2
            online.append(online_now[0])
            online.append(online_now[1])
            online_1 = discord.Member(user={"id": online[0]})
            await util.say(online_1, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
            online_2 = discord.Member(user={"id": online[1]})
            await util.say(online_2, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
        if how_many_online >= 3:
            online.append(online_now[0])
            online.append(online_now[1])
            online.append(online_now[2])
            check_2 = 3
            online_1 = discord.Member(user={"id": online[0]})
            await util.say(online_1, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
            online_2 = discord.Member(user={"id": online[1]})
            await util.say(online_2, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
            online_3 = discord.Member(user={"id": online[2]})
            await util.say(online_3, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
    elif check == 1:
        online = []
        online.append(offline_support_list[int(random.randint(0, len(offline_support_list)))])
        online.append(offline_support_list[int(random.randint(0, len(offline_support_list)))])
        online.append(offline_support_list[int(random.randint(0, len(offline_support_list)))])
        check_2 = 3
        online_1 = discord.Member(user={"id": online[0]})
        await util.say(online_1, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
        online_2 = discord.Member(user={"id": online[1]})
        await util.say(online_2, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
        online_3 = discord.Member(user={"id": online[2]})
        await util.say(online_3, "In %s , <@!%s> needs your help!" % (invite, player.id), client=client)
    await util.say(ctx.channel, "Request sent!")
    if check_2 == 1:
        await util.say(ctx.channel, "I DMed <@!%s> that you needed support! If a name is listed twice, then they were randomly selected twice, and it is not a bug." % (online[0]))
    elif check_2 == 2:
        await util.say(ctx.channel, "I DMed <@!%s> and <@!%s> that you needed support! If a name is listed twice, then they were randomly selected twice, and it is not a bug." % (online[0], online[1]))
    elif check_2 == 3:
        await util.say(ctx.channel, "I DMed <@!%s>, <@!%s>, and <@!%s> that you needed support! If a name is listed twice, then they were randomly selected twice, and it is not a bug." % (online[0], online[1], online[2]))

@commands.command(permission=Permission.DISCORD_USER, args_pattern=None, aliases=("perm",))
async def perminfo(ctx, **details):
    """
    [CMD_KEY]perminfo

    Shows you information on permission mapping.
    [PERM]
    """
    embed = discord.Embed(title="Perm Info", type="rich", color=gconf.DUE_COLOUR)
    embed.add_field(name="Server-based Perms:", value="— Banned: Banned from the bot for breaking rules.\n — Discord User: Opted out on the server or globally, with !optout/!optin or !optouthere/!optinhere.\n — Player: The default perm level, where you have neither manage server perms, or the Due Commander role. — Server Admin: You have either the Due Commander role or Manage Server.\n — Real Server Admin: You have the Manage Server perm.")
    embed.add_field(name="Bot Staff Perms", value="If you are not staff, this shouldn't really matter to you, however here is a quick explanation:\n — Community Ambassador: Basically a trial junior staff, for the newest staff members. They have access to every server admin command regardless of their server perms, however that only allows them to create server items and make the bot leave the server, they exist in order to help new people set up servers if they are confused.\n — Junior staff: Basically Community ambassador, however they have extra commands that let them ban rule-breaking players from the bot and update the leaderboard.\n — Staff: Basically junior staff, except they have access to testing and debugging commands.\n — Owner: They have access to every bot command and make all the bot decisions as a group, similar to a group of server admins on a large server.")
    await util.say(ctx.channel, embed=embed)
    
@commands.command(args_pattern="S", aliases=['lan'])
async def language(ctx, language, **details):
    """
    [CMD_KEY]language (language)
    Lets you set the language you want the bot to send text in.
    Current options are:
    1. English (en)
    ~~2. Spanish (es)~~ broken
    3. Russian (ru)
    4. German (de)
    5. Portuguese (pt)
    6. Dutch (nl)
    7. Japanese (ja)
    8. Hebrew (he)
    9. French (fr)
    10. Tagalog (tl)
    11. Filipino (fil)
    For the language, input the two-letter/three-letter code of the language you want.
    None of the non-English translations are perfect, so you'll have to make do with what you have.
    The translations are being improved as often as possible, but may not work on some commands due to the translations not being entered yet.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "language"):
        player.language = "en"
    if language in "en" or language in "es" or language in "ru" or language in "de" or language in "pt" or language in "nl" or language in "ja" or language in "he" or language in "fr" or language in "tl" or language in "fil":
        if language == "en":
            player.language = "en"
            await util.say(ctx.channel, "Your language is now English!")
#        elif language == "es":
#            player.language = "es"
#            translations = translator.translate(['Your language is now Spanish!'], dest='es')
#            for translation in translations:
#                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "ru":
            player.language = "ru"
            translations = translator.translate(['Your language is now Russian!'], dest='ru')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "de":
            player.language = "de"
            translations = translator.translate(['Your language is now German!'], dest='de')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "pt":
            player.language = "pt"
            translations = translator.translate(['Your language is now Portuguese!'], dest='pt')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "nl":
            player.language = "nl"
            translations = translator.translate(['Your language is now Dutch!'], dest='nl')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "ja":
            player.language = "ja"
            translations = translator.translate(['Your language is now Japanese!'], dest='ja')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "he":
            player.language = "he"
            translations = translator.translate(['Your language is now Hebrew!'], dest='he')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "fr":
            player.language = "fr"
            translations = translator.translate(['Your language is now French!'], dest='fr')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "tl":
            player.langauge = "tl"
            translations = translator.translate(['Your language is now Tagalog!'], dest='tl')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        elif language == "fil":
            player.langauge = "fil"
            translations = translator.translate(['Your language is now Filipino!'], dest='fil')
            for translation in translations:
                await util.say(ctx.channel, "%s" % (translation.text))
        else:
            await util.say(ctx.channel, "You either selected an invalid language, or this language is broken! See the help command for valid languages.")
    player.save()


@commands.command(permission=Permission.DISCORD_USER, args_pattern="S?", aliases=("helpme",))
async def help(ctx, *args, **details):
    """
    [CMD_KEY]help (command name or category)
    
    INCEPTION SOUND
    [PERM]
    """
    player = details["author"]
    help_logo = 'https://cdn.discordapp.com/attachments/173443449863929856/275299953528537088/helo_458x458.jpg'

    help_embed = discord.Embed(title="DueUtil's Help", type="rich", color=gconf.DUE_COLOUR)
    help_embed_2 = discord.Embed(title="DueUtil's Help Links", type="rich", color=gconf.DUE_COLOUR)
    command_embed = discord.Embed(title="DueUtil's Commands", type="rich", color=gconf.DUE_COLOUR)
    server_key = details["cmd_key"]
    categories = events.command_event.category_list()
            
    if len(args) == 1:

        help_embed.set_thumbnail(url=help_logo)
        arg = args[0].lower()
        if arg == "commands":
            member = discord.Member(user={"id": player.id, "server": ctx.server})
            perm_level = 0
            if permissions.has_permission(ctx.author, Permission.SERVER_ADMIN):
                perm_level = 1
            if permissions.has_permission(ctx.author, Permission.REAL_SERVER_ADMIN):
                perm_level = 2
            await util.say(ctx.channel, "DMing you a list of all my commands that you can use! This is still being improved, so it's still really messy!")
            for category in categories:
                if perm_level == 0:
                    commands = events.command_event.command_list(
                        filter=lambda command: command.category == category and not command.permission in (Permission.DUEUTIL_OWNER, Permission.DUEUTIL_ADMIN, Permission.DUEUTIL_MOD, Permission.REAL_SERVER_ADMIN, Permission.SERVER_ADMIN))
                if perm_level == 1:
                    commands = events.command_event.command_list(
                        filter=lambda command: command.category == category and not command.permission in (Permission.DUEUTIL_OWNER, Permission.DUEUTIL_ADMIN, Permission.DUEUTIL_MOD, Permission.REAL_SERVER_ADMIN))
                if perm_level == 2:
                    commands = events.command_event.command_list(
                        filter=lambda command: command.category == category and not command.permission in (Permission.DUEUTIL_OWNER, Permission.DUEUTIL_ADMIN, Permission.DUEUTIL_MOD))
                commands = ', '.join(commands)
                await util.say(ctx.author, "%s" % (commands))
            return
        if arg not in categories:
            chosen_command = events.get_command(arg)
            # Dumb award
            if chosen_command is None:
                alias_count = 0
                if arg != "dumbledore":
                    command_name = 'Not found'
                    command_help = 'That command was not found!'
                else:
                    # Stupid award reference
                    command_name = 'dumbledore?!?'
                    command_help = 'Some stupid *joke?* reference to old due!!!111'
                    help_embed.set_image(url='http://i.imgur.com/UrWhI9P.gif')
                    await awards.give_award(ctx.channel, details["author"], "Daddy",
                                            "I have no memory of this award...")
            else:
                command_name = chosen_command.__name__
                alias_count = len(chosen_command.aliases)
                if chosen_command.__doc__ is not None:
                    command_help = chosen_command.__doc__.replace('[CMD_KEY]', server_key)
                    try:
                        perm_req = chosen_command.permission.value[1].title()
                    except:
                        perm_req = "Player"
                    perm_req.replace("_", " ")
                    command_help = command_help.replace('[PERM]', "\n You need the **" + str(perm_req) + "** perm level to use this command! Use ``!perms`` to check your perm level!")
                    perm_req = perm_req.lower()
                    if perm_req == "player":
                        command_help += "All people have access to **Player** commands unless they opted out, or are banned."
                    elif perm_req == "discord user":
                        command_help += "All people have access to **Discord User** commands unless they are banned."
                    elif perm_req == "server admin":
                        command_help += "Only people with the Manage Server perm, the Due Commander role, and/or Community Ambassador and above have access to **Server Admin** commands."
                    elif perm_req == "real server admin":
                        command_help += "Only people with the Manage Server perm and/or Community Ambassador and above have access to **Real Server Admin** commands."
                    elif perm_req == "junior staff":
                        command_help += "Only people with Junior Staff and above have access to **Junior Staff** commands."
                    elif perm_req == "staff":
                        command_help += "Only people with Staff and above have access to **Staff** commands."
                    elif perm_req == "dueutil owner":
                        command_help += "Only people with DueUtil Owner have access to **DueUtil Owner** commands."
                    try:
                        player = details["author"]
                        if not hasattr(player, "language"):
                            player.language = "en"
                        language = player.language
                        if language != "en":
                            command_help = util.translate(command_help, language)
                    except:
                        pass
                else:
                    command_help = 'Sorry there is no help for that command!'

            help_embed.description = "Showing help for **" + command_name + "**"
            help_embed.add_field(name=":gear: " + command_name, value=command_help)
#            if alias_count > 0:
            try:
                if alias_count > 0 and command_name not in events.command_event.command_list(filter=lambda command: command.category == category and not command.permission in (Permission.DUEUTIL_OWNER, Permission.DUEUTIL_ADMIN, Permission.DUEUTIL_MOD)):
                    help_embed.add_field(name=":performing_arts: " + ("Alias" if alias_count == 1 else "Aliases"),
                                         value=', '.join(chosen_command.aliases), inline=False)
            except:
                pass
        else:
            category = arg
            help_embed.description = "Showing ``" + category + "`` commands."

            commands_for_all = events.command_event.command_list(
                filter=lambda command:
                command.permission in (Permission.PLAYER, Permission.DISCORD_USER) and command.category == category)
            admin_commands = events.command_event.command_list(
                filter=lambda command:
                command.permission == Permission.SERVER_ADMIN and command.category == category)
            server_op_commands = events.command_event.command_list(
                filter=lambda command:
                command.permission == Permission.REAL_SERVER_ADMIN and command.category == category)
            bot_mod_commands = events.command_event.command_list(
                filter=lambda command:
                command.permission == Permission.DUEUTIL_MOD and command.category == category)
            bot_admin_commands = events.command_event.command_list(
                filter=lambda command:
                command.permission == Permission.DUEUTIL_ADMIN and command.category == category)
            bot_owner_commands = events.command_event.command_list(
                filter=lambda command:
                command.permission == Permission.DUEUTIL_OWNER and command.category == category)

            if len(commands_for_all) > 0:
                help_embed.add_field(name='Commands for everyone', value=', '.join(commands_for_all), inline=False)
            if len(admin_commands) > 0:
                help_embed.add_field(name='Server Admins only', value=', '.join(admin_commands), inline=False)
            if len(server_op_commands) > 0:
                help_embed.add_field(name='Server Managers only', value=', '.join(server_op_commands), inline=False)
            if len(bot_mod_commands) > 0:
                help_embed.add_field(name='Bot Mod only', value=', '.join(bot_mod_commands), inline=False)
            if len(bot_admin_commands) > 0:
                help_embed.add_field(name='Bot Admins only', value=', '.join(bot_admin_commands), inline=False)
            if len(bot_owner_commands) > 0:
                help_embed.add_field(name='Bot Owners only', value=', '.join(bot_owner_commands), inline=False)
    else:

        help_embed.set_thumbnail(url=util.get_client(ctx.server.id).user.avatar_url)

        category_list = categories
        x = 1
        categories2 = []
        for category in categories:
            if str(category) == "restartbot" or str(category) == "staff" or str(category) == "new":
                z = 0
            else:
                categories2.append(str(category))
#                categories2.append(str(x) + ". " + str(category))
                x += 1

        help_embed.description = 'Welcome to the help!\n Simply do ' + server_key + 'help (category) or (command name).'
        help_embed.add_field(name=':file_folder: Command categories', value=', '.join(categories2))
        help_embed.add_field(name=e.THINKY_FONK + " Tips",
                             value=("If DueUtil reacts to your command it means something is wrong!\n"
                                    + ":question: - Something is wrong with the command's syntax.\n"
                                    + ":x: - You don't have the required permissions to use the command."))
        help_embed.add_field(name=":link: Links", value=("**Invite me: %s**\n" % gconf.BOT_INVITE
                                                         + "DueUtil Tutorial: https://dueutil.weebly.com/new-user-tutorial.html\n"
                                                         + "Support server: https://discord.gg/6XPVBFf\n"
                                                         + "Support me: ``!donate``\n"
                                                         + "Vote for me: ``!vote`` [or click here](https://discordbots.org/bot/496480755728384002)\n"
                                                         + "DueUtil Dashboard: https://dueutil.org\n"))
        help_embed.set_footer(
            text="To use server admin commands you must have the manage server permission or the 'Due Commander' role.")

    await util.say(ctx.channel, embed=help_embed)
#    if len(args) == 0:
#        await util.say(ctx.channel, embed=help_embed_2)

@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def botinfo(ctx, **_):
    """
    [CMD_KEY]botinfo

    General information about DueUtil.
    [PERM]
    """

    info_embed = discord.Embed(title="DueUtil's Information", type="rich", color=gconf.DUE_COLOUR)
    info_embed.description = "DueUtil is customizable bot to add fun commands, quests and battles to your server."
    info_embed.add_field(name="Original created by", value="[MacDue#4453](https://dueutil.tech/)")
    info_embed.add_field(name="Revived and Updated by", value="[Theelgirl#4980](https://www.youtube.com/watch?v=dQw4w9WgXcQ)")
    info_embed.add_field(name="Framework",
                         value="[discord.py %s :two_hearts:](http://discordpy.readthedocs.io/en/latest/)"
                               % discord.__version__)
    info_embed.add_field(name="Licensed Under",
                         value="[GNUv3](https://www.gnu.org/licenses/gpl-3.0.en.html)")
    info_embed.add_field(name="Invite Due!", value="[Click here!](https://discordapp.com/oauth2/authorize?client_id=496480755728384002&scope=bot&permissions=872803393)", inline=False)
    info_embed.add_field(name="Support server",
                         value="For help with the bot or a laugh join **https://discord.gg/6XPVBFf**!")
    await util.say(ctx.channel, embed=info_embed)


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def prefix(ctx, **details):
    """
    ``@DueUtil``prefix

    Tells you what the prefix is on a server.
    [PERM]
    """

    server_prefix = dueserverconfig.server_cmd_key(ctx.server)
    await util.say(ctx.channel, "The prefix on **%s** is ``%s``" % (details.get("server_name_clean"), server_prefix))


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def dustats(ctx, **_):
    """
    [CMD_KEY]dustats
    
    DueUtil's stats since the dawn of time!
    [PERM]
    """

    game_stats = stats.get_stats()
    stats_embed = discord.Embed(title="DueUtil's Statistics!", type="rich", color=gconf.DUE_COLOUR)

    stats_embed.description = ("The numbers and stuff of DueUtil right now!\n"
                               + "The **worst** Discord bot since %s, %s!"
                               % (gconf.DUE_START_DATE.strftime("%d/%m/%Y"),
                                  repoze.timeago.get_elapsed(gconf.DUE_START_DATE)))

    # General
    stats_embed.add_field(name="General",
                          value=(e.MYINFO + " **%s** images served.\n"
                                 % util.format_number_precise(game_stats[Stat.IMAGES_SERVED])
                                 + e.DISCOIN + " **Đ%s** Discoin received.\n"
                                 % util.format_number_precise(game_stats[Stat.DISCOIN_RECEIVED])))
    # Game
    stats_embed.add_field(name="Game",
                          value=(e.QUESTER + " **%s** players.\n"
                                 % util.format_number_precise(int(game_stats[Stat.NEW_PLAYERS_JOINED]) + (((int(time.time()) - 1559342268) // 864)))
#                                 % util.format_number_precise(game_stats[Stat.NEW_PLAYERS_JOINED])
                                 + e.QUEST + " **%s** quests given.\n"
                                 % util.format_number_precise(game_stats[Stat.QUESTS_GIVEN])
                                 + e.FIST + " **%s** quests attempted.\n"
                                 % util.format_number_precise(game_stats[Stat.QUESTS_ATTEMPTED])
                                 + e.LEVEL_UP + " **%s** level ups.\n"
                                 % util.format_number_precise(game_stats[Stat.PLAYERS_LEVELED])
                                 + e.DUT + " **%s** awarded.\n"
                                 % util.format_money(game_stats[Stat.MONEY_CREATED])
                                 + e.DUT_WITH_WINGS + " **%s** transferred between players.\n"
                                 % util.format_money(game_stats[Stat.MONEY_TRANSFERRED])
                                 + " **%s** commands used (since April 10th, 2019).\n"
                                 % util.format_number_precise(game_stats[Stat.COMMANDS_USED])
                                 + " **%s** translations done (since May 10th, 2019).\n"
                                 % util.format_number_precise(game_stats[Stat.TRANSLATIONS_DONE])),
                          inline=False)
    # Sharding
    shards = util.shard_clients
    current_shard = util.get_client(ctx.server.id)
    stats_embed.add_field(name="Shards",
                          value=("You're connected to shard **%d/%d** (that is named %s).\n"
                                 % (current_shard.shard_id + 1, len(shards), current_shard.name)
                                 + "Current uptime (shard) is %s."
                                 % util.display_time(time.time() - current_shard.start_time, granularity=4)),
                          inline=False)

    await util.say(ctx.channel, embed=stats_embed)


@commands.command(args_pattern=None)
async def duservers(ctx, **_):
    """
    [CMD_KEY]duservers
    
    Shows the number of servers DueUtil is chilling on.
    [PERM]
    """

    server_count = util.get_server_count()
    await util.say(ctx.channel, "DueUtil is active on **" + str(server_count) + " server"
                   + ("s" if server_count != 1 else "") + "**")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S", aliases=("setprefix",))
async def setcmdkey(ctx, new_key, **details):
    """
    [CMD_KEY]setcmdkey
    
    Sets the prefix for commands on your server.
    The default is '!'
    [PERM]
    """

    if len(new_key) in (1, 2, 3, 4):
        dueserverconfig.server_cmd_key(ctx.server, new_key)
        await util.say(ctx.channel,
                       "Command prefix on **" + details["server_name_clean"] + "** set to ``" + new_key + "``!")
    else:
        raise util.DueUtilException(ctx.channel, "Command prefixes can only be one to four characters!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S?")
async def shutupdue(ctx, *args, **details):
    """
    [CMD_KEY]shutupdue 
    
    Mutes DueUtil in the channel the command is used in.
    By default the ``[CMD_KEY]shutupdue`` will stop alerts (level ups, ect)
    using ``[CMD_KEY]shutupdue all`` will make DueUtil ignore all commands
    from non-admins.
    [PERM]
    """

    if len(args) == 0:
        mute_success = dueserverconfig.mute_channel(ctx.channel)
        if mute_success:
            await util.say(ctx.channel, (":mute: I won't send any alerts in this channel!\n"
                                         + "If you meant to disable commands too do ``" + details[
                                             "cmd_key"] + "shutupdue all``."))
        else:
            await util.say(ctx.channel, (":mute: I've already been set not to send alerts in this channel!\n"
                                         + "If you want to disable commands too do ``" + details[
                                             "cmd_key"] + "shutupdue all``.\n"
                                         + "To unmute me do ``" + details["cmd_key"] + "unshutupdue``."))
    else:
        mute_level = args[0].lower()
        if mute_level == "all":
            mute_success = dueserverconfig.mute_channel(ctx.channel, mute_all=True)
            if mute_success:
                await util.say(ctx.channel, ":mute: Disabled all commands in this channel for non-admins!")
            else:
                await util.say(ctx.channel, (":mute: Already mute af in this channel!.\n"
                                             + "To allow commands & alerts again do ``" + details[
                                                 "cmd_key"] + "unshutupdue``."))
        else:
            await util.say(ctx.channel, ":thinking: If you wanted to mute all the command is ``" + details[
                "cmd_key"] + "shutupdue all``.")


@commands.command(permission=Permission.REAL_SERVER_ADMIN, args_pattern="S?")
@commands.require_cnf(warning="The bot will leave your server and __**everything**__ will be reset!")
async def leave(ctx, **_):
    """
    [CMD_KEY]leave
    
    Makes DueUtil leave your server cleanly.
    This will delete all quests & weapons created
    on your server.
    
    This command can only be run by real server admins
    (you must have manage server permissions).
    [PERM]
    """

    bye_embed = discord.Embed(title="Goodbye!", color=gconf.DUE_COLOUR)
    bye_embed.set_image(url="http://i.imgur.com/N65P9gL.gif")
    await util.say(ctx.channel, embed=bye_embed)
    try:
        await util.get_client(ctx.server.id).leave_server(ctx.server)
    except:
        raise util.DueUtilException(ctx.channel, "Could not leave server!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern=None)
async def unshutupdue(ctx, **_):
    """
    [CMD_KEY]unshutupdue

    Reverts ``[CMD_KEY]shutupdue`` or ``[CMD_KEY]shutupdue all``
    (allowing DueUtil to give alerts and be used again).
    [PERM]
    """
    if dueserverconfig.unmute_channel(ctx.channel):
        await util.say(ctx.channel,
                       ":speaker: Okay! I'll once more send alerts and listen for commands in this channel!")
    else:
        await util.say(ctx.channel, ":thinking: Okay... I'm unmuted but I was not muted anyway.")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S*")
async def whitelist(ctx, *args, **_):
    """
    [CMD_KEY]whitelist
    
    Choose what DueUtil commands you want to allow in a channel.
    E.g. ``[CMD_KEY]whitelist help battle shop myinfo info``
    
    Normal users will not be able to use any other commands than the ones you
    choose.
    The whitelist does not effect server admins.
    
    To reset the whitelist run the command with no arguments.

    If you use the whitelist command on a channel with a pre-existing whitelist, the pre-existing whitelist will be replaced with the new one.
    Example:
    Using ``[CMD_KEY]whitelist teaminfo help`` on a channel with the whitelist ``myinfo`` would allow only teaminfo and help, and myinfo would no longer be allowed.

    Note: Whitelisting a command like !info will also whitelist !myinfo
    (since !info is mapped to !myinfo)
    [PERM]
    """

    if len(args) > 0:
        due_commands = events.command_event.command_list(aliases=True)
        whitelisted_commands = set(commands.replace_aliases([command.lower() for command in args]))
        if whitelisted_commands.issubset(due_commands):
            dueserverconfig.set_command_whitelist(ctx.channel, list(whitelisted_commands))
            await util.say(ctx.channel, (":notepad_spiral: Whitelist in this channel set to the following commands: ``"
                                         + ', '.join(whitelisted_commands) + "``"))
        else:
            incorrect_commands = whitelisted_commands.difference(due_commands)
            await util.say(ctx.channel, (":confounded: Cannot set whitelist! The following commands don't exist: ``"
                                         + ', '.join(incorrect_commands) + "``"))
    else:
        dueserverconfig.set_command_whitelist(ctx.channel, [])
        await util.say(ctx.channel, ":pencil: Command whitelist set back to all commands.")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="S*")
async def blacklist(ctx, *args, **_):
    """
    [CMD_KEY]blacklist
    
    Choose what DueUtil commands you want to ban in a channel.
    E.g. ``[CMD_KEY]blacklist acceptquest battleme sell``
    
    Normal users will only be able to use commands not in the blacklist.
    The blacklist does not effect server admins.
    
    To reset the blacklist run the command with no arguments.
    
    The blacklist is not independent from the whitelist.

    If you use the blacklist command on a channel with a pre-existing blacklist, the pre-existing blacklist will be replaced with the new one.
    Example:
    Using ``[CMD_KEY]blacklist teaminfo help`` on a channel with the blacklist ``myinfo`` would disable only teaminfo and help, and myinfo would now be allowed.

    Note: Blacklisting a command like !info will also blacklist !myinfo
    (since !info is mapped to !myinfo)
    [PERM]
    """

    if len(args) > 0:
        due_commands = events.command_event.command_list(aliases=True)
        blacklisted_commands = set(commands.replace_aliases([command.lower() for command in args]))
        if blacklisted_commands.issubset(due_commands):
            whitelisted_commands = list(set(due_commands).difference(blacklisted_commands))
            whitelisted_commands.append("is_blacklist")
            dueserverconfig.set_command_whitelist(ctx.channel, whitelisted_commands)
            await util.say(ctx.channel, (":notepad_spiral: Blacklist in this channel set to the following commands: ``"
                                         + ', '.join(blacklisted_commands) + "``"))
        else:
            incorrect_commands = blacklisted_commands.difference(due_commands)
            await util.say(ctx.channel, (":confounded: Cannot set blacklist! The following commands don't exist: ``"
                                         + ', '.join(incorrect_commands) + "``"))
    else:
        dueserverconfig.set_command_whitelist(ctx.channel, [])
        await util.say(ctx.channel, ":pencil: Command blacklist removed.")


@commands.command(permission=Permission.REAL_SERVER_ADMIN, args_pattern=None)
async def setuproles(ctx, **_):
    """
    [CMD_KEY]setuproles
    
    Creates any discord roles DueUtil needs. These will have been made when
    DueUtil joined your server but if you deleted any & need them you'll 
    want to run this command.
    [PERM]
    """
    roles_made = await util.set_up_roles(ctx.server)
    roles_count = len(roles_made)
    if roles_count > 0:
        result = ":white_check_mark: Created **%d %s**!\n" % (roles_count, util.s_suffix("role", roles_count))
        for role in roles_made:
            result += "→ ``%s``\n" % role["name"]
        await util.say(ctx.channel, result)
    else:
        await util.say(ctx.channel, "No roles need to be created!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern=None)
async def setup(ctx, **details):
    """
    [CMD_KEY]setup
    
    Creates some basic starter quests and weapons for server members.
    [PERM]
    """
    if weapons.does_weapon_exist(ctx.server.id, "Beginner Quest Killer") or weapons.does_weapon_exist(ctx.server.id, "Basic Quest Killer"):
        raise util.DueUtilException(ctx.channel, "You seem to have already have set up quests and weapons! Delete all weapons with any of these names to set up:\n"
                                            + "Beginner Quest Killer, Basic Quest Killer, Decent Quest Killer, Strong Quest Killer, Advanced Quest Killer.\n"
                                            + "If the bot gives an error for quests, it means you already have quests named at least one of these:\n"
                                            + "x1 Train, x1.5 Train, x2 Train, x3 Train.")
    else:
        name = "Beginner Quest Killer"
        hit_message = "beats"
        damage = 3
        accy = 86
        ranged=False
        icon='🔫'
        extras = {"melee": not ranged, "icon": icon}
        weapon = weapons.Weapon(name, hit_message, damage, accy, **extras, ctx=ctx)
        await util.say(ctx.channel, (weapon.icon + " **" + weapon.name_clean + "** is available in the shop for "
                                     + util.format_number(weapon.price, money=True) + "!"))
        name = "Basic Quest Killer"
        hit_message = "beats"
        damage = 5
        accy = 86
        ranged=False
        icon='🔫'
        extras = {"melee": not ranged, "icon": icon}
        weapon = weapons.Weapon(name, hit_message, damage, accy, **extras, ctx=ctx)
        await util.say(ctx.channel, (weapon.icon + " **" + weapon.name_clean + "** is available in the shop for "
                                     + util.format_number(weapon.price, money=True) + "!"))
        name = "Decent Quest Killer"
        hit_message = "beats"
        damage = 10
        accy = 86
        ranged=False
        icon='🔫'
        extras = {"melee": not ranged, "icon": icon}
        weapon = weapons.Weapon(name, hit_message, damage, accy, **extras, ctx=ctx)
        await util.say(ctx.channel, (weapon.icon + " **" + weapon.name_clean + "** is available in the shop for "
                                     + util.format_number(weapon.price, money=True) + "!"))
        name = "Strong Quest Killer"
        hit_message = "beats"
        damage = 15
        accy = 86
        ranged=False
        icon='🔫'
        extras = {"melee": not ranged, "icon": icon}
        weapon = weapons.Weapon(name, hit_message, damage, accy, **extras, ctx=ctx)
        await util.say(ctx.channel, (weapon.icon + " **" + weapon.name_clean + "** is available in the shop for "
                                     + util.format_number(weapon.price, money=True) + "!"))
        name = "Advanced Quest Killer"
        hit_message = "beats"
        damage = 20
        accy = 86
        ranged=False
        icon='🔫'
        extras = {"melee": not ranged, "icon": icon}
        weapon = weapons.Weapon(name, hit_message, damage, accy, **extras, ctx=ctx)
        await util.say(ctx.channel, (weapon.icon + " **" + weapon.name_clean + "** is available in the shop for "
                                     + util.format_number(weapon.price, money=True) + "!"))
        name = "x1 Train"
        attack = 1
        strg = 1
        accy = 1
        hp = 30
        extras = {"spawn_chance": 25}
        extras['rank'] = 1
        new_quest = quests.Quest(name, attack, strg, accy, hp, **extras, ctx=ctx)
        await util.say(ctx.channel, ":white_check_mark: " + util.ultra_escape_string(
            new_quest.task) + " **" + new_quest.name_clean + "** is now active!")
        name = "x1.5 Train"
        attack = 1.5
        strg = 1.5
        accy = 1.5
        hp = 30
        extras = {"spawn_chance": 25}
        extras['rank'] = 1
        new_quest = quests.Quest(name, attack, strg, accy, hp, **extras, ctx=ctx)
        await util.say(ctx.channel, ":white_check_mark: " + util.ultra_escape_string(
            new_quest.task) + " **" + new_quest.name_clean + "** is now active!")
        name = "x2 Train"
        attack = 2
        strg = 2
        accy = 2
        hp = 30
        extras = {"spawn_chance": 25}
        extras['rank'] = 1000
        new_quest = quests.Quest(name, attack, strg, accy, hp, **extras, ctx=ctx)
        await util.say(ctx.channel, ":white_check_mark: " + util.ultra_escape_string(
            new_quest.task) + " **" + new_quest.name_clean + "** is now active!")
        name = "x3 Train"
        attack = 3
        strg = 3
        accy = 3
        hp = 45
        extras = {"spawn_chance": 25}
        extras['rank'] = 3
        new_quest = quests.Quest(name, attack, strg, accy, hp, **extras, ctx=ctx)
        await util.say(ctx.channel, ":white_check_mark: " + util.ultra_escape_string(
            new_quest.task) + " **" + new_quest.name_clean + "** is now active!")
        await util.say(ctx.channel, "A few basic quests and weapons have now been uploaded! Try running this again if you get an error on anything!")


async def optout_is_topdog_check(channel, player):
    topdog = player.is_top_dog()
    if topdog:
        await util.say(channel, (":dog: You cannot opt out while you're top dog!\n"
                                 + "Pass on the title before you leave us!"))
    return topdog


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def optout(ctx, **details):
    """
    [CMD_KEY]optout

    Optout of DueUtil.

    When you opt out:
        You don't get quests or exp.
        Other players can't use you in commands.
        You lose access to all "game" commands.

    Server admins (that opt out) still have access to admin commands.

    (This applies to all servers with DueUtil)
    [PERM]
    """

    player = details["author"]
    if player.is_playing():
        current_permission = permissions.get_special_permission(ctx.author)
        if await optout_is_topdog_check(ctx.channel, player):
            return
        if current_permission >= Permission.DUEUTIL_MOD:
            raise util.DueUtilException(ctx.channel, "You cannot optout everywhere and stay a dueutil mod or admin!")
        permissions.give_permission(ctx.author, Permission.DISCORD_USER)
        await util.say(ctx.channel, (":ok_hand: You've opted out of DueUtil everywhere.\n"
                                     + "You won't get exp, quests, and other players can't use you in commands."))
    else:
        await util.say(ctx.channel, ("You've already opted out everywhere!\n"
                                     + "You can join the fun again with ``%soptin``." % details["cmd_key"]))


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def optin(ctx, **details):
    """
    [CMD_KEY]optin

    Optin to DueUtil.

    (This applies to all servers with DueUtil)
    [PERM]
    """

    player = details["author"]
    local_optout = not player.is_playing(ctx.server, local=True)
    # Already playing
    if player.is_playing():
        if not local_optout:
            await util.say(ctx.channel, "You've already opted in everywhere!")
        else:
            await util.say(ctx.channel, ("You've only opted out on this server!\n"
                                         + "To optin here do ``%soptinhere``" % details["cmd_key"]))
    else:
        permissions.give_permission(ctx.author, Permission.PLAYER)
        await util.say(ctx.channel, ("You've opted in everywhere"
                                     + (" (does not override your server level optout)" * local_optout) + "!\n"
                                     + "Glad to have you back."))


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def optouthere(ctx, **details):
    """
    [CMD_KEY]optouthere

    Optout of DueUtil on the server you run the command.
    This has the same effect as [CMD_KEY]optout but is local.
    [PERM]
    """

    player = details["author"]

    if not player.is_playing():
        await util.say(ctx.channel, "You've already opted out everywhere!")
        return

    if player.is_playing(ctx.server, local=True):
        optout_role = util.get_role_by_name(ctx.server, gconf.DUE_OPTOUT_ROLE)
        if optout_role is None:
            await util.say(ctx.channel, ("There is no optout role on this server!\n"
                                         + "Ask an admin to run ``%ssetuproles``" % details["cmd_key"]))
        else:
            if await optout_is_topdog_check(ctx.channel, player):
                return
            client = util.get_client(ctx.server.id)
            await client.add_roles(ctx.author, optout_role)
            await util.say(ctx.channel, (":ok_hand: You've opted out of DueUtil on this server!\n"
                                         + "You won't exp, quests, or be usable in commands here."))
    else:
        await util.say(ctx.channel, ("You've already opted out on this sever!\n"
                                     + "Join the fun over here do ``%soptinhere``" % details["cmd_key"]))


@commands.command(permission=Permission.DISCORD_USER, args_pattern=None)
async def optinhere(ctx, **details):
    """
    [CMD_KEY]optinhere

    Optin to DueUtil on a server.
    [PERM]
    """

    player = details["author"]
    globally_opted_out = not player.is_playing()

    optout_role = util.get_role_by_name(ctx.server, gconf.DUE_OPTOUT_ROLE)
    if optout_role is not None and not player.is_playing(ctx.server, local=True):
        client = util.get_client(ctx.server.id)
        await client.remove_roles(ctx.author, optout_role)
        await util.say(ctx.channel, ("You've opted in on this server!\n"
                                     + ("However this is overridden by your global optout.\n"
                                        + "To optin everywhere to ``%soptin``" % details["cmd_key"])
                                     * globally_opted_out))
    else:
        if globally_opted_out:
            await util.say(ctx.channel, ("You've opted out of DueUtil everywhere!\n"
                                         + "To use DueUtil do ``%soptin``" % details["cmd_key"]))
        else:
            await util.say(ctx.channel, "You've not opted out on this server.")


@commands.command(args_pattern="CSS?")
async def exchange(ctx, amount, currency, currency_from="DUT", **details):
    """
    [CMD_KEY]exchange (amount) (currency) (optional: from DUT, DUTC, or DUP)

    Exchange your DUT (DueUtil Tokens), DUTC (DueUtil TeamCash), and/or DUP (DueUtil Prestige for other bot currencies!

    For more information on the user side go to: https://discoin.gitbook.io/docs/users-guide

    For more information on transaction information, go to https://dash.discoin.zws.im/#/

    Note: Exchanges can take up to 5 minutes to process!
    """
    player = details["author"]
    currency = currency.upper()
    currency_from = currency_from.upper()
    currency_from_list = ["DUT", "DTC", "DUP", "MONEY", "TEAMCASH", "TEAM MONEY", "PRESTIGE COINS", "PRESTIGE"]
    if not currency_from in currency_from_list:
        raise util.DueUtilException(ctx.channel, "Please enter a valid currency to send currency_from (DUT, DUTC (teamcash), DUP, etc.)")
    if currency_from == "MONEY":
        currency_from = "DUT"
    elif currency_from == "TEAMCASH" or currency_from == "TEAM MONEY":
        currency_from = "DUTC"
    elif currency_from == "PRESTIGE COINS" or currency_from == "PRESTIGE":
        currency_from = "DUP"
    currency_list = ["DTS", "ELT", "GBC", "KEK", "MMB", "OAT", "PIC", "RBN", "DUTS", "DUT", "DTC", "DUP"]
    if not currency in currency_list:
        raise util.DueUtilException(ctx.channel, "Please enter a valid currency code! To exchange one DueUtil currency into another DueUtil currency, you must use the abbreviations DUT, DUTC, or DUP.")

    if currency == "DUT" and currency_from == "DUT":
        raise util.DueUtilException(ctx.channel, "There is no reason to exchange DUT for DUT!")
    elif currency == "DTC" and currency_from == "DTC":
        raise util.DueUtilException(ctx.channel, "There is no reason to exchange DTC for DTC!")
    elif currency == "DUP" and currency_from == "DUP":
        raise util.DueUtilException(ctx.channel, "There is no reason to exchange DUP for DUP!")

    if (player.money - amount) < 0 and currency_from == "DUT":
        if player.money - amount > 0:
            await util.say(ctx.channel, "You do not have **%s**!\n"
                           % util.format_number(amount, full_precision=True, money=True)
                           + "The maximum you can exchange is **%s**"
                           % util.format_number(player.money, full_precision=True, money=True))
        else:
            await util.say(ctx.channel, "You don't have any DUT to exchange!")
        return
    elif (player.team_money - amount) < 0 and currency_from == "DTC":
        if player.team_moneymoney - amount > 0:
            await util.say(ctx.channel, "You do not have **%s** teamcash!\n"
                           % util.format_number(amount, full_precision=True, money=False)
                           + "The maximum you can exchange is **%s** teamcash!"
                           % util.format_number(player.team_money, full_precision=True, money=False))
        else:
            await util.say(ctx.channel, "You don't have any DTC to exchange!")
        return
    elif (player.prestige_coins - amount) < 0 and currency_from == "DUP":
        if player.prestige_coins - amount > 0:
            await util.say(ctx.channel, "You do not have **%s** DUP!\n"
                           % util.format_number(amount, full_precision=True, money=False)
                           + "The maximum you can exchange is **%s** DUP!"
                           % util.format_number(player.money, full_precision=True, money=False))
        else:
            await util.say(ctx.channel, "You don't have any DUP to exchange!")
        return

    try:
        response = await discoin.make_transaction(str(player.id), int(amount), str(currency), str(currency_from))
    except Exception as discoin_error:
        util.logger.error("Discoin exchange failed %s", discoin_error)
        raise util.DueUtilException(ctx.channel, "Something went wrong at Discoin! Their API is likely buggy, or restarting, please wait a few hours.")
    id = response["id"]
    embed = discord.Embed(title="Transaction sent!", type="rich", color=gconf.DUE_COLOUR)
    embed.add_field(name="Transaction Status:", value=("You can view the transaction status [here](https://dash.discoin.zws.im/#/transactions/" + str(id) + "/show)! If there is a cross mark under handled, please wait up to 5 minutes for the transaction to process."))
    embed.add_field(name="Currency Exchange Rates:", value="To view exchange rates for different currencies, please visit [here](https://dash.discoin.zws.im/#/currencies).")
    embed.add_field(name="User Guide to Discoin:", value="You can check out user-relevant info [here](https://discoin.gitbook.io/docs/users-guide)!")
    await util.say(ctx.channel, embed=embed)

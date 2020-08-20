from datetime import datetime

import discord
import repoze.timeago
import asyncio
import time
import math
import random

import generalconfig as gconf
from .. import commands, util, dbconn
from ..game import awards, players, leaderboards, game, teams
from ..game.helpers import misc, imagehelper
from ..game import emojis


async def glitter_text(channel, text):
    try:
        gif_text = await misc.get_glitter_text(text)
        await util.get_client(channel).send_file(channel, fp=gif_text,
                                                 filename="glittertext.gif",
                                                 content=":sparkles: Your glitter text!")
    except (ValueError, asyncio.TimeoutError):
        await util.say(channel, ":cry: Could not fetch glitter text!")

@commands.command(args_pattern=None)
async def kek(ctx, **details):
    """
    [CMD_KEY]kek
    
    A cool command to display one of two kek emotes.
    [PERM]
    """
    x = random.randint(1,2)
    if x == 1:
        await util.say(ctx.channel, "%s" % emojis.DUE_KEK)
    if x == 2:
        await util.say(ctx.channel, "%s" % emojis.DUE_KEK2)


@commands.command(args_pattern=None)
async def blob(ctx, **details):
    """
    [CMD_KEY]blob

    A cool command to display one of 10 blob emotes.
    [PERM]
    """
    x = random.randint(1,10)
    if x == 1:
        await util.say(ctx.channel, "%s" % emojis.BLOB1)
    if x == 2:
        await util.say(ctx.channel, "%s" % emojis.BLOB2)
    if x == 3:
        await util.say(ctx.channel, "%s" % emojis.BLOB3)
    if x == 4:
        await util.say(ctx.channel, "%s" % emojis.BLOB4)
    if x == 5:
        await util.say(ctx.channel, "%s" % emojis.BLOB5)
    if x == 6:
        await util.say(ctx.channel, "%s" % emojis.BLOB6)
    if x == 7:
        await util.say(ctx.channel, "%s" % emojis.BLOB7)
    if x == 8:
        await util.say(ctx.channel, "%s" % emojis.BLOB8)
    if x == 9:
        await util.say(ctx.channel, "%s" % emojis.BLOB9)
    if x == 10:
        await util.say(ctx.channel, "%s" % emojis.BLOB10)

@commands.command(args_pattern="I?S?", aliases=['c'])
async def count(ctx, number=0, send="", **details):
    """
    [CMD_KEY]count (optional: number) (optional: message for owner)
    Lets you add to the DueUtil count! You can only do so 25 times per day.
    Each time you successfully count, you will gain a bonus for atk, strg, and accy based on how many times you've counted correctly.
    You can view the number that you should count with the basic ``!count``.
    If you want, you can have the bot DM the owner with a message, such as "Great job updating Due!", or "We love your new updates!"
    [PERM]
    """
    player = details["author"]
    theel = players.find_player("376166105917554701")
    if not hasattr(player, "counts"):
        player.counts = 0
    if not hasattr(player, "count"):
        player.count = 0
    if not hasattr(theel, "count"):
        theel.count = 0
    x = int(theel.count + 1)
    if number == 0:
        await util.say(ctx.channel, "The current number that count is at is %s." % (x))
        return
    elif number == x:
        if player.count <= 25:
            theel.count += 1
            if player.id != "376166105917554701":
                player.count += 1
            player.counts += 1
            try:
                y = (player.counts / math.log(player.counts, 1.05))
            except ZeroDivisionError:
                y = .1
            except ValueError:
                y = .1
            a = y * 1.2
            try:
                z = random.uniform(y, a) * math.log(player.level, 1.5)
            except ValueError:
                z = random.uniform(y, a)
            player.attack += z
            player.strg += z
            player.accy += z
            player.exp += (z * 300)
            await game.check_for_level_up(ctx, player)
            theel.save()
            player.save()
            b = round(z, 2)
            message = "You gained " + str(b) + " of each of Attack, Strength, and Accuracy!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
            if send != "":
                theelid = 376166105917554701
                ctx.author = discord.Member(user={"id": theelid})
                ctx.author.server = ctx.server
                await util.say(ctx.author, "%s - from %s" % (send, player.id))
        else:
            message = "You have counted 25 times today!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
    else:
        message = "Your count was incorrect! You should have written" 
        message2 = "(Sometimes people from other servers may steal your count)"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
            message2 = util.translate(message2, language)
        await util.say(ctx.channel, "%s %s %s" % (message, x, message2))


@commands.command(args_pattern="P?", aliases=['tds'])
async def topdogstats(ctx, *args, **details):
    """
    [CMD_KEY]topdogstats (optional: player)
    Shows you various topdog data on someone in an embed.
    [PERM]
    """
    if len(args) == 0:
        player = details["author"]
    else:
        player = args[0]
    if not hasattr(player, "topdog_time_elapsed"):
        player.topdog_time_elapsed = 0
    if not hasattr(player, "topdog_time"):
        player.topdog_time = 0
    if not hasattr(player, "topdog_attempts"):
        player.topdog_attempts = 0
    top_dog_stats = awards.get_award_stat("TopDog")
    top_dog = players.find_player(top_dog_stats["top_dog"])
    if player.id == top_dog.id:
        a = int(time.time()) - int(player.topdog_time_elapsed)
        b = a + player.topdog_time
        c = util.display_time(a)
        d = util.display_time(b)
        e = player.topdog_attempts
        message = "Topdog Data!"
        message2 = "Current Topdog Time (since March 16th):"
        message3 = "Total TopDog Time (since March 16th):"
        message4 = "Attempts to Take Their TopDog:"
        language = player.language
        if language != "en":
            x = util.translate_4(message, message2, message3, message4, language)
            message = x[0]
            message2 = x[1]
            message3 = x[2]
            message4 = x[3]
        stats = discord.Embed(title=message, type="rich",
                                        color=gconf.DUE_COLOUR)
        stats.add_field(name=message2, value=c)
        stats.add_field(name=message3, value=d)
        stats.add_field(name=message4, value=e)
        await util.say(ctx.channel, embed=stats)
    else:
        a = util.display_time(player.topdog_time)
        if player.topdog_time >= 1 and player.topdog_time <= 100000000:
            message = "Topdog Data!"
            message2 = "Total TopDog Time (since March 16th):"
            language = player.language
            if language != "en":
                message = util.translate(message, language)            
                message2 = util.translate(message2, language)
            stats = discord.Embed(title=message, type="rich",
                                            color=gconf.DUE_COLOUR)
            stats.add_field(name=message2, value=a)
            await util.say(ctx.channel, embed=stats)
        else:
            message = "They haven't had topdog since March 16th, 2019!"
            language = player.language
            if language != "en":
                message = util.translate(message, language) 
            await util.say(ctx.channel, "%s" % (message))

@commands.command(args_pattern=None, aliases=['tdn'])
async def topdognotify(ctx, **details):
    """
    [CMD_KEY]topdognotify
    Toggles whether you want to be notified if your topdog award is stolen.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "opt_topdog"):
        player.opt_topdog = 0
    a = player.opt_topdog
    if int(a) == 0:
        message = "You will now recieve a direct message if top dog is stolen from you!"
        language = player.language
        if language != "en":
            message = util.translate(message, language) 
        player.opt_topdog = 1
        await util.say(ctx.channel, "%s" % (message))
    else:
        message = "You will no longer recieve a direct message if top dog is stolen from you."
        language = player.language
        if language != "en":
            message = util.translate(message, language) 
        player.opt_topdog = 0
        await util.say(ctx.channel, "%s" % (message))
    player.save()


@commands.command(args_pattern="P?", aliases=['mtdt'])
async def topdogtime(ctx, *args, **details):
    """
    [CMD_KEY]topdogtime (optional: player)
    Tells you how long you/they have had topdog if you currently have it.
    It also says how long you/they have had it since when this feature was implemented (March 16th, 2019).
    [PERM]
    """
    if len(args) == 0:
        player = details["author"]
    else:
        player = args[0]
    if not hasattr(player, "topdog_time_elapsed"):
        player.topdog_time_elapsed = 0
    if not hasattr(player, "topdog_time"):
        player.topdog_time = 0
    if not hasattr(player, "topdog_attempts"):
        player.topdog_attempts = 0
    top_dog_stats = awards.get_award_stat("TopDog")
    top_dog = players.find_player(top_dog_stats["top_dog"])
    if player.id == top_dog.id:
        a = time.time() - player.topdog_time_elapsed
        b = a + player.topdog_time
        c = util.display_time(a)
        d = util.display_time(b)
        e = player.topdog_attempts
        message = "You have had this top dog for **" + str(c) + "**!"
        message2 = "You have had top dog for **" + str(d) + "** since March 16th, 2019!"
        message3 = "People have tried to take this top dog **" + str(e) + "** times!"
        language = player.language
        if language != "en":
            x = util.translate_3(message, message2, message3, language)
            message = x[0]
            message2 = x[1]
            message3 = x[2]
        await util.say(ctx.channel, "%s %s %s" % (message, message2, message3))
    else:
        a = util.display_time(player.topdog_time)
        if player.topdog_time >= 1:
            message = "You have had top dog for **" + str(a) + "** since March 16th, 2019!"
            language = player.language
            if language != "en":
                message = util.translate(message, language) 
            await util.say(ctx.channel, "%s" % (message))
        else:
            message = "You haven't had topdog since March 16th, 2019"
            language = player.language
            if language != "en":
                message = util.translate(message, language) 
            await util.say(ctx.channel, "%s!" % (message))


@commands.command(args_pattern='S', aliases=("gt", "glittertext",))
@commands.imagecommand()
async def glitter(ctx, text, **details):
    """
    [CMD_KEY]glitter(text)
    
    Creates a glitter text gif!
    
    (Glitter text from http://www.gigaglitters.com/)

    **This is broken at the moment.**
    [PERM]
    """
    details["author"].misc_stats["art_created"] += 1
    await util.say(ctx.channel, "The website that was used to create these has gone down, but you can use other websites on your own.")
    return
    await glitter_text(ctx.channel, text)


@commands.command(args_pattern="S?")
@commands.imagecommand()
async def eyes(ctx, eye_description="", **details):
    """
    [CMD_KEY]eyes modifiers
    
    __Modifiers:__
        snek - Snek eyes (slits)
        ogre - Ogre colours
        evil - Red eyes
        gay  - Pink stuff
        high - Large pupils + red eyes
        emoji - emoji size + no border
        small - Small size (larger than emoji)
        left - Eyes look left
        right - Eyes look right
        top - Eyes look to the top
        bottom - Eyes look to the bottom
        derp - Random pupil positions
        bottom left - Eyes look bottom left
        bottom right - Eyes look bottom right
        top right - Eyes look top right
        top left - Eyes look top left
        no modifiers - Procedurally generated eyes!!!111

    **This is broken at the moment.**
    [PERM]
    """
    details["author"].misc_stats["art_created"] += 1
    await util.say(ctx.channel, "The website that was used to create these has gone down, but you can use other websites on your own.")
    return
    await imagehelper.googly_eyes(ctx.channel, eye_description)


@commands.command(args_pattern="C?", aliases=("globalrankings", "globalleaderboard", "gleaderboard"))
async def globalranks(ctx, page=1, **details):
    """
    [CMD_KEY]globalranks (page)

    Global DueUtil leaderboard
    [PERM]
    """

    await leaderboard.__wrapped__(ctx, mixed="global", page_alt=page, **details)


@commands.command(args_pattern="M?C?", aliases=("ranks", "rankings"))
async def leaderboard(ctx, mixed=1, page_alt=1, **details):
    """
    [CMD_KEY]leaderboard (page)
    or for global ranks
    [CMD_KEY]leaderboard global (page)
    [CMD_KEY]globalranks (page)
    
    The global leaderboard of DueUtil!
    
    The leaderboard updated every hour, but it may be longer.
    
    **Now with local**.
    [PERM]
    """

    page_size = 10

    # Handle weird page args
    if type(mixed) is int:
        page = mixed - 1
        local = True
        ranks = "local"
    else:
        local = mixed.lower() != "global"
        ranks = "local" if local else "global"
        page = page_alt - 1

    # Local/Global
    if local:
        title = "DueUtil Leaderboard on %s" % details["server_name_clean"]
        # Cached.
        local_leaderboard = leaderboards.get_local_leaderboard(ctx.server, "levels")
        leaderboard_data = local_leaderboard.data
        last_updated = local_leaderboard.updated
    else:
        title = "DueUtil Global Leaderboard"
        leaderboard_data = leaderboards.get_leaderboard("levels")
        last_updated = leaderboards.last_leaderboard_update

    if leaderboard_data is None or len(leaderboard_data) == 0:
        await util.say(ctx.channel, "The %s leaderboard has yet to be calculated!\n" % ranks
                       + "Check again soon!")
        return

    leaderboard_embed = discord.Embed(title="%s %s" % (emojis.QUESTER, title),
                                      type="rich", color=gconf.DUE_COLOUR)

    if page > 0:
        leaderboard_embed.title += ": Page %d" % (page + 1)
    if page * page_size >= len(leaderboard_data):
        raise util.DueUtilException(ctx.channel, "Page not found")

    index = 0
    for index in range(page_size * page, page_size * page + page_size):
        if index >= len(leaderboard_data):
            break
        bonus = ""
        if index == 0:
            bonus = "     :first_place:"
        elif index == 1:
            bonus = "     :second_place:"
        elif index == 2:
            bonus = "     :third_place:"
        player = players.find_player(leaderboard_data[index])
        user_info = ctx.server.get_member(player.id)
        if user_info is None:
            user_info = player.id
        leaderboard_embed \
            .add_field(name="#%s" % (index + 1) + bonus,
                       value="[%s **``Level %s``**](https://dueutil.org/player/id/%s) (%s) | **Total EXP** %d"
                             % (player.name_clean, player.level, player.id,
                                util.ultra_escape_string(str(user_info)), player.total_exp), inline=False)

    if index < len(leaderboard_data) - 1:
        remaining_players = len(leaderboard_data) - page_size * (page + 1)
        leaderboard_embed.add_field(name="+%d more!" % remaining_players,
                                    value="Do ``%sleaderboard%s %d`` for the next page!"
                                          % (details["cmd_key"], "" if local else " global", page + 2), inline=False)
    leaderboard_embed.set_footer(text="Leaderboard calculated "
                                      + repoze.timeago.get_elapsed(datetime.utcfromtimestamp(last_updated)))
    await util.say(ctx.channel, embed=leaderboard_embed)


async def rank_command(ctx, player, ranks="", **details):
    ranks = ranks.lower()
    local = ranks != "global"

    if local:
        position = leaderboards.get_rank(player, "levels", ctx.server)
        ranks = padding = ""
    else:
        position = leaderboards.get_rank(player, "levels")
        padding = " "

    player_is_author = ctx.author.id == player.id
    player_name = "**%s**" % player.name_clean

    if position != -1:
        page = position // 10 + (1 * position % 10 != 0)
        await util.say(ctx.channel, (":sparkles: " + ("You're" if player_is_author else player_name + " is")
                                     + (" **{0}** on the{4}{3} leaderboard!\n"
                                        + "That's on page {1} (``{2}leaderboard{4}{3} {5}``)!")
                                     .format(util.int_to_ordinal(position), page,
                                             details["cmd_key"], ranks, padding, page if page > 1 else "")))
    else:
        await util.say(ctx.channel, (":confounded: I can't find "
                                     + ("you" if player_is_author else player_name)
                                     + " on the {}{}leaderboard!?\n".format(ranks, padding)
                                     + "You'll need to wait till it next updates!\n" * player_is_author
                                     + "Also, if you didn't use a command within 5 minutes of the leaderboard update, you won't be on the leaderboard!"))


@commands.command(args_pattern="S?")
async def myrank(ctx, ranks="", **details):
    """
    [CMD_KEY]myrank
    or for your global rank
    [CMD_KEY]myrank global

    Tells you where you are on the [CMD_KEY]leaderboard.
    [PERM]
    """

    await rank_command(ctx, details["author"], ranks, **details)


@commands.command(args_pattern="PS?")
async def rank(ctx, player, ranks="", **details):
    """
    [CMD_KEY]rank @player
    or for the global rank
    [CMD_KEY]rank @player global

    Tells you where a player is on the [CMD_KEY]leaderboard.
    [PERM]
    """

    await rank_command(ctx, player, ranks, **details)


@commands.command(args_pattern="P?", aliases=("grank",))
async def globalrank(ctx, player=None, **details):
    """
    [CMD_KEY]globalrank
    or [CMD_KEY]globalrank @player

    Find your or another player's global rank.
    [PERM]
    """

    if player is None:
        player = details["author"]
    await rank_command(ctx, player, "global", **details)


async def give_emoji(channel, sender, receiver, emoji):
    if not util.char_is_emoji(emoji) and not util.is_server_emoji(channel.server, emoji):
        raise util.DueUtilException(channel, "You can only send emoji!")
    if sender == receiver:
        raise util.DueUtilException(channel, "You can't send a " + emoji + " to yourself!")
    await util.say(channel, "**" + receiver.name_clean + "** " + emoji + " :heart: **" + sender.name_clean + "**")


@commands.command(args_pattern='PS', aliases=("emoji",))
async def giveemoji(ctx, receiver, emoji, **details):
    """
    [CMD_KEY]giveemoji player emoji
    
    Give a friend an emoji.
    Why? Who knows.
    I'm sure you can have loads of game with the :cancer: emoji though!
    Also see ``[CMD_KEY]givepotato``
    [PERM]
    """
    sender = details["author"]

    try:
        await give_emoji(ctx.channel, sender, receiver, emoji)
        sender.misc_stats["emojis_given"] += 1
        receiver.misc_stats["emojis"] += 1
    except util.DueUtilException as command_error:
        raise command_error
    await awards.give_award(ctx.channel, sender, "Emoji", ":fire: __Breakdown Of Society__ :city_dusk:")
    if emoji == "🍆":
        await awards.give_award(ctx.channel, sender, "Sauce", "*Saucy*")
    if sender.misc_stats["emojis_given"] == 100:
        await awards.give_award(ctx.channel, sender, "EmojiKing", ":biohazard: **__WIPEOUT HUMANITY__** :radioactive:")


@commands.command(args_pattern='P', aliases=("potato",))
async def givepotato(ctx, receiver, **details):
    """
    [CMD_KEY]givepotato player
    
    Who doesn't like potatoes?
    [PERM]
    """
    sender = details["author"]

    try:
        await give_emoji(ctx.channel, sender, receiver, '🥔')
        sender.misc_stats["potatoes_given"] += 1
        receiver.misc_stats["potatoes"] += 1
    except util.DueUtilException as command_error:
        raise command_error
    await awards.give_award(ctx.channel, sender, "Potato", ":potato: Bringer Of Potatoes :potato:")
    if sender.misc_stats["potatoes_given"] == 100:
        await awards.give_award(ctx.channel, sender, "KingTat", ":crown: :potato: **Potato King!** :potato: :crown:")


@commands.command(args_pattern=None)
async def topdog(ctx, **details):
    """
    [CMD_KEY]topdog

    View the "top dog" and their team stats.
    [PERM]
    """
    player_1 = details["author"]
    top_dog_stats = awards.get_award_stat("TopDog")
    if top_dog_stats is not None and "top_dog" in top_dog_stats:
        top_dog = players.find_player(top_dog_stats["top_dog"])
        player = top_dog
        if not hasattr(player, "team"):
            player.team = None
        if player.team >= 0:
            player.team = None

        team = teams.get_team_no_id(player.team)
        if team is not None:
            if not hasattr(team, "topdog_count"):
                team.topdog_count = 0
            team_stats = team.topdog_count
        else:
            team_stats = 0
        x = 1
        if x == 1:
            if player.team != None:
                message = "The current top dog is " + str(top_dog) + " **(" + str(top_dog.id) + ")**!" 
                message2 = "They are the **" + str(util.int_to_ordinal(top_dog_stats["times_given"])) + "** to earn the rank of top dog, " + "and are in team **" + str(player.team) + "**!"
                message3 = "This is time number **" + str(team_stats) + "** that their team has gotten top dog since the last topdog event!"
                language = player_1.language
                if language != "en":
                    x = util.translate_3(message, message2, message3, language)
                    message = x[0]
                    message2 = x[1]
                    message3 = x[2]
                await util.say(ctx.channel, (":dog: %s\n"
                                             + "%s\n"
                                             + "%s")
                               % (message, message2, message3))
            else:
                message = "The current top dog is " + str(top_dog) + " **(" + str(top_dog.id) + ")**!" 
                message2 = "They are the **" + str(util.int_to_ordinal(top_dog_stats["times_given"])) + "** to earn the rank of top dog!"
                language = player_1.language
                if language != "en":
                    x = util.translate_2(message, message2, language)
                    message = x[0]
                    message2 = x[1]
                await util.say(ctx.channel, (":dog: %s\n"
                                             + "%s")
                               % (message, message2))
    else:
        message = "There is not a top dog yet!"
        language = player_1.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))


@commands.command(args_pattern=None)
async def pandemic(ctx, **_):
    """
    [CMD_KEY]pandemic

    Tracks the ongoing DueUtil pandemic.
    [PERM]
    """
    virus_stats = awards.get_award_stat("Duerus")

    if virus_stats is None or virus_stats["times_given"] == 0:
        await util.say(ctx.channel, "All looks good now though a pandemic could break out any day.00000000000")
        return

    warning_symbols = {0: ":heart: - Healthy", 1: ":yellow_heart: - Worrisome", 2: ":black_heart: - Doomed"}
    thumbnails = {0: "http://i.imgur.com/NENJMOP.jpg",
                  1: "http://i.imgur.com/we6XgpG.gif",
                  2: "http://i.imgur.com/EJVYJ9C.gif"}

    total_players = dbconn.get_collection_for_object(players.Player).count() + (((int(time.time()) - 1559342268) // 864))
    total_infected = virus_stats["times_given"]
    total_uninfected = total_players - total_infected
    percent_infected = (total_infected / total_players) * 100
    pandemic_level = percent_infected // 33
    pandemic_embed = discord.Embed(title=":biohazard: DueUtil Pandemic :biohazard:", type="rich",
                                   color=gconf.DUE_COLOUR)
    pandemic_embed.description = ("The pandemic is still going!\n"
                                  + "Infect more people by beating them in a battle when you're infected!")
    pandemic_embed.set_thumbnail(url=thumbnails.get(pandemic_level, thumbnails[2]))
    # pandemic_embed.description = "Monitoring the spread of the __loser__ pandemic."
    pandemic_embed.add_field(name="Pandemic stats", value=("Out of a total of **%s** players:\n"
                                                           + ":biohazard: **%s** "
                                                           + ("is" if total_infected == 1 else "are") + " infected.\n"
                                                           + ":pill: **%s** "
                                                           + ("is" if total_uninfected == 1 else "are")
                                                           + " uninfected.\n\n"
                                                           + "This means **%.2g**%% of all players are infected!")
                                                          % (total_players, total_infected,
                                                             total_uninfected, percent_infected))
    pandemic_embed.add_field(name="Health level",
                             value=warning_symbols.get(pandemic_level, warning_symbols[2]))

    await util.say(ctx.channel, embed=pandemic_embed)

import json
import os
import re
import subprocess
import random
import math
from io import StringIO

import discord
import objgraph
import asyncio
import time

import generalconfig as gconf
import dueutil.permissions
from ..game.helpers import imagehelper
from ..permissions import Permission
from .. import commands, util, events
from ..game import customizations, awards, leaderboards, game, weapons, players, teams
from ..game import emojis as e

# Import all game things. This is (bad) but is needed to fully use the eval command

@commands.command(args_pattern=None)
async def teamtrees(ctx, **details):
    """
    [CMD_KEY]teamtrees

    Outputs a link to the teamtrees home page, where you can donate to help plant trees.
    This is a custom command from the Christmas Giveaway, and it will be removed on January 31st.
    """
    await util.say(ctx.channel, "Donate to help trees here: https://teamtrees.org/")

@commands.command(args_pattern=None)
async def update(ctx, **details):
    """
    [CMD_KEY]update

    Shows info about the most recent updates.
    [PERM]
    """
    a = str("1. Added a page to dueutil.org for update logs.")
    b = str("2. Adding 3 new tips.")
    c = str("3. Fixing a lot of bugs.")
    d = str("https://discord.gg/6XPVBFf")
    update = discord.Embed(title="Most recent update!", type="rich",
                                    color=gconf.DUE_COLOUR)
    update.add_field(name="Command Updates:", value=a)
    update.add_field(name="Bug Fixes:", value=b)
    update.add_field(name="Other:", value=c)
    update.add_field(name="Support Server (with full update log):", value=d)
    update.set_footer(text="Join the support server with the above link for a full update log, or visit dueutil.org/update-log/!")
    await util.say(ctx.author, embed=update)
    await util.say(ctx.channel, "The update message has been DMed to you! Check back every week or so for new updates!")

@commands.command(args_pattern="IIS")
async def settimer(ctx, timer, interval, reminder_message, **details):
    """
    [CMD_KEY]settimer (length) (interval) (reminder)

    Length and reminder interval in seconds, and use reminder in quotes unless it's one word.

    The interval has to be a factor of the timer, otherwise the bot will overrun the timer.
    [PERM]
    """
    player = details["author"]
    a = int(timer)
    b = int(interval)
    c = int(timer) - int(interval)
    d = a / b
    e = "%s seconds" % a
    f = "%s seconds" % b
    message = "Timer complete!"
    message2 = "Person who is being reminded:"
    message3 = "Reminder:"
    message4 = "Timer length:"
    message5 = "Reminder interval:"
    message6 = "Thanks for trying Due Remind!"
    language = player.language
    if language != "en":
        x = util.translate_6(message, message2, message3, message4, message5, message6, language)
        message = x[0]
        message2 = x[1]
        message3 = x[2]
        message4 = x[3]
        message5 = x[4]
        message6 = x[5]
    reminder = discord.Embed(title=message, type="rich",
                                    color=gconf.DUE_COLOUR)
    reminder.add_field(name=message2, value=player.name_clean)
    reminder.add_field(name=message3, value=reminder_message)
    reminder.add_field(name=message4, value=e)
    reminder.add_field(name=message5, value=f, inline=False)
    reminder.set_footer(text=message6)
    if b < a:
        if a < 604800:
            if d <= 30:
                message = "Your timer has been started."
                language = player.language
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
                for i in range(c,0,-b):
                    await asyncio.sleep(b)
                    await util.say(ctx.author, "%s seconds left" % i)
                await asyncio.sleep(b)
                await util.say(ctx.author, embed=reminder)
            else:
                message = "The interval cannot be less than 1/30th of the total time!"
                language = player.language
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))
        else:
            message = "Timer cannot be longer than one week!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
    else:
        message = "The interval has to be smaller than the timer length!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))

@commands.command(args_pattern="S")
async def afk(ctx, afk, **details):
    """
    [CMD_KEY]afk (message)

    Sets your afk to display a message when you're pinged.

    Adding AFK to your name has to be done manually for now.

    **This is temporairily disabled.**
    [PERM]
    """
    raise util.DueUtilException(ctx.channel, "This feature has been disabled because of lack of use, because it used a lot of the bot's CPU.")
    player = details["author"]

    if not hasattr(player, "afk"):
        player.afk = 0
    if not hasattr(player, "afk_message"):
        player.afk_message = 0
    if player.afk == 0:
        player.afk = 1
        player.afk_message = afk
        game.awayfromkeyboard.append(player.id)
        game.awayfromkeyboardmessage.append(player.afk_message)
        message = "I set your away from keyboard message"
        message2 = "to"
        language = player.language
        if language != "en":
            x = util.translate_2(message, message2, language)
            message = x[0]
            message2 = x[1]
        await util.say(ctx.channel, "%s **%s** %s **%s**!" % (message, player.id, message2, player.afk_message))
    else:
        message = "You already have an away from keyboard message active!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))

@commands.command(args_pattern=None)
async def donate(ctx, **details):
    """
    [CMD_KEY]donate

    Gives you a link to donate to the bot and help keep it alive!
    [PERM]
    """
    donate_link = discord.Embed(title="Donate for a special role in support and to keep bot alive!", type="rich",
                                    color=gconf.DUE_COLOUR)
    donate_link.add_field(name="Link:", value="https://www.paypal.me/theelgirlsdueutil")
    donate_link.set_footer(text="Thanks for considering donating! Lets keep Due strong!")
    await util.say(ctx.channel, embed=donate_link)

@commands.command(args_pattern=None)
@commands.ratelimit(cooldown=43200, error="You can't collect your voting reward again for **[COOLDOWN]**!", save=True)
async def vote(ctx, **details):
    """
    [CMD_KEY]vote

    This gives you the same reward as daily!

    You can use this command once every 12 hours, instead of 24 hours.
    [PERM]
    """
    DAILY_AMOUNT = 50
    player = details["author"]
    if not hasattr(player, "streak"):
        player.streak = 0
    if not hasattr(player, "streak_check"):
        player.streak_check = 0
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "team_money"):
        player.team_money = 0
    a = float(time.time()) - player.streak_check
    if a >= 129600:
        player.streak = 1
        message = "Your streak was reset for not collecting daily after 36 hours! (12 hour grace period)"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    message3 = "Your streak has gone up by one!"
    if a >= 86400:
        player.streak += 1
        player.streak_check = time.time()
    else:
        message3 = "It has not been 24 hours since you last used ``!daily`` or ``!vote``, so your streak stayed the same!"     
    try:
        if player.team >= 0:
            player.team = None
    except:
        pass
    b = int(.1 * player.level * player.streak) + 1
    if player.team != None:
        player.team_money += b
    BALANCED_AMOUNT = DAILY_AMOUNT * player.level * player.streak
    player.money += BALANCED_AMOUNT
    player.save()
    c = player.streak - 1
    if player.team is None:
        message = str(player) + " collected " + str(BALANCED_AMOUNT) + " DUT!"
        message2 = "You have a " + str(c) + " day streak!"
        language = player.language
        if language != "en":
            x = util.translate_3(message, message2, message3, language)
            message = x[0]
            message2 = x[1]
            message3 = x[2]
        await util.say(ctx.channel, e.DUT + " %s %s %s" % (message, message2, message3))
    if player.team != None:
        message = str(player) + " collected " + str(BALANCED_AMOUNT) + " DUT, and " + str(b) + " teamcash!"
        message2 = "You have a " + str(c) + " day streak!"
        language = player.language
        if language != "en":
            x = util.translate_3(message, message2, message3, language)
            message = x[0]
            message2 = x[1]
            message3 = x[2]
        await util.say(ctx.channel, e.DUT + " %s %s %s" % (message, message2, message3))

    player.save()
    message = "You collected your rewards anyway, but right now voting is on an honor system. Eventually, voting will be tied to whether you voted or not, but for now, please vote on either or both of these links:"
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "%s (https://top.gg/bot/496480755728384002) (https://bots.ondiscord.xyz/bots/496480755728384002). The first link takes you to top, where you can sign in and vote, and the second links takes you to the BoD page, where you will be able to vote when the bot gets approved!" % (message))


@commands.command(args_pattern=None)
async def invite(ctx, **details):
    """
    [CMD_KEY]invite

    Provides the invite link to the bot, the support server, and some voting sites!
    [PERM]
    """
    embed = discord.Embed(title="Invites", type="rich", color=gconf.DUE_COLOUR)
    embed.add_field(name="Bot Invite:", value="[Click here to invite Due!](https://dueutil.org/invite/)")
    embed.add_field(name="Support Server Invite:", value="[Click here to join the support server!](https://discord.gg/6XPVBFf)")
    embed.add_field(name="Voting Links:", value="[DBL Voting Link](https://top.gg/bot/496480755728384002)  [BoD Voting Link](https://bots.ondiscord.xyz/bots/496480755728384002) You can vote at the DBL link to help the bot reach new users, and the BoD link when the bot gets approved!")
    await util.say(ctx.channel, embed=embed)

@commands.command(permission=Permission.DISCORD_USER, args_pattern=None, aliases=["perms"])
async def permissions(ctx, **_):
    """
    [CMD_KEY]permissions
    
    A check command for the permissions system.
    [PERM]
    """

    permissions_report = ""
    for permission in dueutil.permissions.permissions:
        permissions_report += ("``" + permission.value[1] + "`` → "
                               + (":white_check_mark:" if dueutil.permissions.has_permission(ctx.author,
                                                                                             permission)
                                  else ":no_entry:") + "\n")
    await util.say(ctx.channel, permissions_report)


@commands.command(args_pattern="S*", hidden=True)
async def test(ctx, *args, **_):
    """A test command"""

    # print(args[0].__dict__)
    # args[0].save()
    # await imagehelper.test(ctx.channel)
    await util.say(ctx.channel, ("Yo!!! What up dis be my test command fo show.\n"
                                 "I got deedz args ```" + str(args) + "```!"))


@commands.command(args_pattern="RR", hidden=True)
async def add(ctx, first_number, second_number, **_):
    """
    [CMD_KEY]add (number) (number)
    
    One of the first test commands for Due2
    I keep it for sentimental reasons
    [PERM]
    """

    result = first_number + second_number
    await util.say(ctx.channel, "Is " + str(result))


@commands.command()
async def wish(*_, **details):
    """
    [CMD_KEY]wish
    
    Does this increase the chance of a quest spawn?!
    
    Who knows?
    
    Me.
    [PERM]
    """

    player = details["author"]
    player.quest_spawn_build_up += 0.01


@commands.command(args_pattern="S", hidden=True)
async def disableddueeval(ctx, statement, **details):
    player = details["author"]
    # print(player.last_message_hashes)
    #try:
        #if statement.startswith("await"):
            #result = await eval(statement.replace("await", '', 1))
        #else:
            #result = eval(statement)
        #if result is not None:
            #await util.say(ctx.channel, ":ferris_wheel: Eval...\n"
                                        #"**Result** ```" + str(result) + "```")
    #except Exception as eval_exception:
        #await util.say(ctx.channel, (":cry: Could not evaluate!\n"
                                     #+ "``%s``" % eval_exception))
    util.logger.info("%s has tried dueeval to do %s", player.id, statement)


"""
@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="PS")
async def say(ctx, **details):
    pass
"""
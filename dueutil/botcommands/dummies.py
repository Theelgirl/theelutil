import discord
import random
import math
import time
import os
import asyncio

import dueutil.game.awards as game_awards
import generalconfig as gconf
from ..game import players, customizations
from ..game import stats, game
from ..game.helpers import misc, playersabstract, imagehelper
from .. import commands, util, dbconn
from ..game import emojis as e
from ..game import (
    quests,
    game,
    battles,
    weapons,
    stats,
    awards,
    players)

DUMMY_MODIFIER = .0025


@commands.command(args_pattern='PIS?', aliases=["sd"])
async def senddummy(ctx, receiver, dummies_sent, message="", **details):
    """
    [CMD_KEY]senddummy (player) (dummy amount) (optional message)

    Sends some dummies to someone else.
    The maximum amount someone can recieve is their distance up (in levels) from level 5 divided by 10.
    Example:
    If I'm level 4, I can't recieve dummies because I'm not at least level 5.
    At levels 5-14, I can recieve 1 dummy.
    At levels 15-24, I can recieve 2.
    At levels 25-34, I can get 3... (and so on)

    This can get confusing for some people, the developer is working on a better way now!
    [PERM]
    """
    sender = details["author"]
    if not hasattr(sender, "dummies"):
        sender.dummies = 0
    if not hasattr(receiver, "dummies"):
        receiver.dummies = 0
    if receiver.id == sender.id:
        language = sender.language
        message = "There is no reason to send training dummies to yourself!"
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if sender.dummies - dummies_sent < 0:
        if sender.dummies > 0:
            language = sender.language
            message = "You do not have"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s %s" % (message, dummies_sent))
        else:
            language = sender.language
            message = "You do not have any training dummies to transfer!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
        return
    max_receive = int(receiver.level / 10)
    if dummies_sent > max_receive:
        language = sender.language
        message = str(receiver.name_clean) + " cannot recieve this many training dummies!"
        message2 = "The maximum they can receive is " + str(max_receive) + "!"
        if language != "en":
            x = util.translate_2(message, message2, language)
            message = x[0]
            message2 = x[1]
        await util.say(ctx.channel, ("%s %s") % (message, message2))
        return
    sender.dummies -= dummies_sent
    receiver.dummies += dummies_sent
    sender.save()
    receiver.save()
    language = sender.language
    message = "Transaction complete!"
    message2 = "Sender:"
    message3 = "Recipient:"
    message4 = "Training Dummies Sent:"
    message5 = "Attached note:"
    message6 = "Please keep this receipt for your records."
    if language != "en":
        x = util.translate_6(message, message2, message3, message4, message5, message6, language)
        message = x[0]
        message2 = x[1]
        message3 = x[2]
        message4 = x[3]
        message5 = x[4]
        message6 = x[5]
    transaction_log = discord.Embed(title=message, type="rich",
                                    color=gconf.DUE_COLOUR)
    transaction_log.add_field(name=message2, value=sender.name_clean)
    transaction_log.add_field(name=message3, value=receiver.name_clean)
    transaction_log.add_field(name=message4, value=dummies_sent, inline=False)
    if message != "":
        transaction_log.add_field(name=message5, value=message, inline=False)
    transaction_log.set_footer(text=message6)
    await util.say(ctx.channel, embed=transaction_log)


@commands.command(args_pattern="S", aliases=["ud"])
@commands.ratelimit(cooldown=900, error="You can't use dummies again for **[COOLDOWN]**!", save=True)
async def usedummy(ctx, stat, **details):
    """
    [CMD_KEY]usedummy (stat to train)

    Choose to train either your attack (atk), strength (strg), accuracy (accy), defense (def), HP, limit, or prestige bonus (prestige) stat.

    Dummies can be used as training dummies every 15 minutes in order to increase stats, and can be earned through quests or bought with !buydummy.

    Atk, strg, and accy dummies increase your stats by a percentage of your current stats.

    HP, limit, and defense increase relatively linearly.

    Prestige bonus increases entirely linearly.
    [PERM]
    """

    player = details["author"]

    if not hasattr(player, "dummy_limit"):
        player.dummy_limit = 1
    if not hasattr(player, "hp_modifier"):
        player.hp_modifier = 1
    if not hasattr(player, "defense"):
        player.defense = 1
    if not hasattr(player, "dummies"):
        player.dummies = 0
    if not hasattr(player, "dummy_max"):
        player.dummy_max = 10
    if not hasattr(player, "dummy_prestige"):
        player.dummy_prestige = 1


    if player.dummies >= player.dummy_max:
        player.dummies = player.dummy_max
        message = "Your dummy count was reset because it was above your dummy max! Buy a higher max with !teambuy."
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    if player.dummy_limit >= 10:
        player.dummy_limit = 10
        message = "Your dummy limit was reset to normal because it there was a big bug in the code that made some people's limit 10x higher than it should have been!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    z = str(stat)
    z = z.lower()
    if "atk" in z:
        if player.dummies >= 1:
            a = round(player.attack * DUMMY_MODIFIER * random.uniform(.8, 1.2), 1)
            player.attack = round(player.attack + a, 2)
            player.dummies -= 1
            message = "Your attack is now " + str(player.attack) + ", and it improved by " + str(a) + "!"
            message2 = "You have " + str(player.dummies) + " dummies left!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            await util.say(ctx.channel, "%s %s" % (message, message2))
        else:
            message = "You don't have any dummies!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
    elif "strg" in z and player.dummies >= 1:
        if player.dummies >= 1:
            b = round(player.strg * DUMMY_MODIFIER * random.uniform(.8, 1.2), 1)
            player.strg = round(player.strg + b, 2)
            player.dummies -= 1
            message = "Your strength is now " + str(player.strg) + ", and it improved by " + str(b) + "!"
            message2 = "You have " + str(player.dummies) + " dummies left!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            await util.say(ctx.channel, "%s %s" % (message, message2))
        else:
            message = "You don't have any dummies!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
    elif "accy" in z and player.dummies >= 1:
        if player.dummies >= 1:
            c = round(player.accy * DUMMY_MODIFIER * random.uniform(.8, 1.2), 1)
            player.accy = round(player.accy + c, 2)
            player.dummies -= 1
            message = "Your accuracy is now " + str(player.accy) + ", and it improved by " + str(c) + "!"
            message2 = "You have " + str(player.dummies) + " dummies left!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            await util.say(ctx.channel, "%s %s" % (message, message2))
        else:
            message = "You don't have any dummies!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
    elif "hp" in z or "HP" in z:
        if player.hp_modifier <= 10 and player.dummies >= 1:
            d = round(player.hp_modifier * .005 * random.uniform(.75, 1), 4)
            player.hp_modifier += d
            player.hp_modifier = round(player.hp_modifier, 4)
            player.dummies -= 1
            message = "Your HP modifier is now " + str(player.hp_modifier) + ", and it improved by " + str(d) + "!"
            message2 = "You have " + str(player.dummies) + " dummies left!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            await util.say(ctx.channel, "%s %s" % (message, message2))
        else:
            message = "You don't have any dummies or you reached the max HP modifier (10x)!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
    elif "limit" in z:
        if player.dummy_limit <= 10 and player.dummies >= 1:
            e = round(player.dummy_limit * .005 * random.uniform(.75, 1), 4)
            player.dummy_limit += e
            player.dummy_limit = round(player.dummy_limit, 4)
            player.dummies -= 1
            message = "Your dummy limit modifier is now " + str(player.dummy_limit) + ", and it improved by " + str(e) + "!"
            message2 = "You have " + str(player.dummies) + " dummies left!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            await util.say(ctx.channel, "%s %s" % (message, message2))
        else:
            message = "You don't have any dummies or you reached the max dummy limit modifier (10x)!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
    elif "def" in z or "defense" in z:
        if player.defense <= 10 and player.dummies >= 1:
            f = round(player.defense * .005 * random.uniform(.75, 1), 4)
            player.defense += f
            player.defense = round(player.defense, 4)
            player.dummies -= 1
            message = "Your defense is now " + str(player.defense) + ", and it improved by " + str(f) + "!"
            message2 = "You have " + str(player.dummies) + " dummies left!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            await util.say(ctx.channel, "%s %s" % (message, message2))
        else:
            message = "You don't have any dummies or you reached the max defense modifier (10x)!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
    elif "prestige" in z or "prestige bonus" in z:
        if player.dummy_prestige <= 3 and player.dummies >= 1:
            f = round(.02 * random.uniform(.75, 1), 4)
            player.dummy_prestige += f
            player.dummy_prestige = round(player.dummy_prestige, 4)
            player.dummies -= 1
            message = "Your prestige bonus is now " + str(player.dummy_prestige) + ", and it improved by " + str(f) + "!"
            message2 = "You have " + str(player.dummies) + " dummies left!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            await util.say(ctx.channel, "%s %s" % (message, message2))
            player.save()
        else:
            message = "You don't have any dummies or you reached the max prestige bonus modifier (3x)!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
    else:
        message = "Use a valid dummy (find valid ones in help usedummy)!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    player.save()


@commands.command(args_pattern=None)
async def mydummies(ctx, **details):
    """
    [CMD_KEY]dummies

    Shows you how many dummies you have.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "dummies"):
        player.dummies = 0
    await util.say(ctx.channel, "You have **%s** dummies!" % (player.dummies))


@commands.command(args_pattern="I", aliases=["bd"])
async def buydummy(ctx, dummies_bought, **details):
    """
    [CMD_KEY]buydummy (number of dummies to buy)

    Lets you buy dummies for 50k DUT each for use with [CMD_KEY]usedummy.

    View details on the type of dummies you can use in [CMD_KEY]help usedummy.
    [PERM]
    """

    player = details["author"]

    if not hasattr(player, "dummies"):
        player.dummies = 0

    if not hasattr(player, "dummy_max"):
        player.dummy_max = 10

    a = int(player.dummy_max)
    b = int(50000 * dummies_bought)
    c = int(player.dummy_max - dummies_bought)
    d = int(player.dummy_max - player.dummies)

    if player.money >= b and dummies_bought >= 1:
        if int(dummies_bought) <= d:
            d = int(dummies_bought)
            player.money -= b
            player.dummies += d
            message = "You bought " + str(dummies_bought) + " dummies! You now have " + str(player.dummies) + " dummies!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
        else:
            message = "You can only have " + str(player.dummy_max) + " dummies at a time!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
    else:
        message = "You need " + str(b) + " DUT to buy " + str(dummies_bought) + " dummies, and you can't buy negative dummies!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    player.save()

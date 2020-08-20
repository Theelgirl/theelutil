import math
import time
import random
import asyncio

import discord

import generalconfig as gconf
from ..game.helpers import imagehelper
from ..permissions import Permission
from ..game import (
    quests,
    game,
    battles,
    weapons,
    stats,
    awards,
    players,
    teams)
from .. import commands, util, permissions
from ..game.helpers import misc

from ..game import emojis as e

@commands.command(args_pattern="I")
async def autotimer(ctx, number, **details):
    """
    [CMD_KEY]autotimer (# of quest reminders)

    Lets you know every 5 minutes when to send a message for quests.

    You cannot start more autoreminders when some are already ongoing.

    Resetting your profile resets your timer count, and max # is 30.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "reminders"):
        player.reminders = 0
    if player.reminders != 0:
        player.reminders= 0
        await util.say(ctx.channel, "Your remaining reminders were deleted!")
    if int(player.reminders) == 0:
        if number <= 30:
            message = "I set autoreminder to remind you **" + str(number) + "** times!"
            language = player.language
            if language != "en":
                x = util.translate(message, language)
                message = x
            await util.say(ctx.channel, "%s" % (message))
            message = "Go send a message for a chance to get a quest!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            for i in range(number, 0, -1):
                await asyncio.sleep(300)
                await util.say(ctx.author, "%s" % (message))
                player.reminders = 1
            player.reminders = 0
        else:
            message = "No more than 30 autoreminders can be set at one time!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
    else:
        message = "You need to wait for all your autotimers to finish first!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))


@commands.command(args_pattern="I", aliases=['tqc'])
async def testquestchance(ctx, quest_index, **details):
    """
    [CMD_KEY]testquestchance (quest number)
    Shows you the approximate chance you have to beat a quest, and the approximate stats it'll give.
    It'll add in randomness to the chances/approximate stats by default.
    You can decrease the randomness (and therefore improve accuracy) by spending teamcash to buy improved accuracy.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "defense"):
        player.defense = 1
    if not hasattr(player, "dummy_chance"):
        player.dummy_chance = 1
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    if not hasattr(player, "prestiges"):
        player.prestiges = 0
    if not hasattr(player, "prediction_accy"):
        player.prediction_accy = 0.75
    quest_index -= 1
    if quest_index >= len(player.quests):
        raise util.DueUtilException(ctx.channel, "Quest not found!")
    repeats = 5
    wins= 0
    while repeats > 0:
        quest = player.quests[quest_index]
        battle_log = battles.get_battle_log(player_one=player, player_two=quest, p2_prefix="the ")
        winner = battle_log.winner
        quest_scale = quest.get_quest_scale()
        avg_player_stat = player.get_avg_stat()
        turns = battle_log.turn_count
        average_quest_battle_turns = player.misc_stats["average_quest_battle_turns"] = (player.misc_stats[
                                                                                        "average_quest_battle_turns"] + turns) / 2
        a = player.prestige_bonus()
        b = 100 * a
        c = 10000 * a
        d = math.log(a, 2)
        def attr_gain(stat):
            return (max(0.01, (stat / avg_player_stat)
                    * quest.level * (turns / average_quest_battle_turns) / 2 * (quest_scale + 0.5) * 3 * d))

        add_strg = min(attr_gain(quest.strg), b)
        add_attack = min(attr_gain(quest.attack), min(add_strg * 3 * random.uniform(0.6, 1.5) * d, b))
        add_accy = min(attr_gain(quest.accy), min(add_strg * 3 * random.uniform(0.6, 1.5) * d, b))
        if winner == player:
            wins += 1
    losses = 5 - wins
    x = (1 - player.prediction_accy)
    y = (1 + player.prediction_accy)
    z = 100 - (player.prediction_accy * 100)
    add_strg_1 = add_strg * x
    add_strg_2 = add_strg * y
    add_attack_1 = add_attack * x
    add_attack_2 = add_attack * y
    add_accy_1 = add_accy * x
    add_accy_2 = add_accy * y
    add_strg = round(random.uniform(add_strg_1, add_strg_2), 1)
    add_attack = round(random.uniform(add_attack_1, add_attack_2), 2)
    add_accy = round(random.uniform(add_accy_1, add_accy_2), 2)
    w1 = (wins / 5) * player.prediction_accy * random.uniform(x, y)
    idk = int(quest.money * a)

    language = player.language
    message = "Quest Data!"
    message2 = "Estimated Win Chance:"
    message3 = "Estimated Strength Gained:"
    message4 = "Estimated Attack Gained:"
    message5 = "Estimated Accuracy Gained:"
    message6 = "Quest Money:"
    message7 = "Prediction Accuracy:"
    message8 = "Increase your prediction accuracy in the teamshop!"
    if language != "en":
        x = util.translate_8(message, message2, message3, message4, message5, message6, message7, message8, language)
        message = x[0]
        message2 = x[1]
        message3 = x[2]
        message4 = x[3]
        message5 = x[4]
        message6 = x[5]
        message7 = x[6]
        message8 = x[7]
    win_stats = discord.Embed(title=message, type="rich",
                                    color=gconf.DUE_COLOUR)
    win_stats.add_field(name=message2, value=w1)
    win_stats.add_field(name=message3, value=add_strg)
    win_stats.add_field(name=message4, value=add_attack)
    win_stats.add_field(name=message5, value=add_accy)
    win_stats.add_field(name=message6, value=idk)
    win_stats.add_field(name=message7, value=z)
    win_stats.set_footer(text=message8)
    await util.say(ctx.channel, embed=win_stats)
    player.save()


@commands.command(args_pattern=None, aliases=['aqa'])
@commands.imagecommand()
async def acceptquestall(ctx, **details):
    """
    [CMD_KEY]acceptquestall

    Accepts all the quests you have. You must have at least 5 quests to use this.

    This will show battle logs every 5 quests that it beats for you.
    [PERM]
    """

    player = details["author"]
    if not hasattr(player, "defense"):
        player.defense = 1
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "dummy_max"):
        player.dummy_max = 10
    if not hasattr(player, "dummies"):
        player.dummies = 0
    if not hasattr(player, "dummy_chance"):
        player.dummy_chance = 1
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    if not hasattr(player, "prestiges"):
        player.prestiges = 0
    language = player.language
    if len(player.quests) < 5:
        message = "You need at least 5 quests to use this!"
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    a = player.prestige_bonus()
    b = 100 * a
    c = 10000 * a
    if a >= 2.5:
        d = math.log(a, 2.5)
    else:
        d = a 
    aa = 0
    y = 0
    n = 0
    i = len(player.quests)
    while len(player.quests) > 0:
        if player.money - player.quests[0].money // 2 < 0:
            message = "You can't afford the risk anymore! Quest accepting stopped! You need to get more money!"
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))
            break
        if not hasattr(player, "double_quests"):
            player.double_quests = False
        if player.donor or player.double_quests:
            if player.quests_completed_today >= quests.TEAM_MAX_DAILY_QUESTS:
                message = "You can't do more than"
                message2 = "quests a day"
                if language != "en":
                    x = util.translate_2(message, message2, language)
                    message = x[0]
                    message = x[1]
                raise util.DueUtilException(ctx.channel, "%s %s %s" % (message, str(quests.TEAM_MAX_DAILY_QUESTS), message2))
                break
        else:
            if player.quests_completed_today >= quests.MAX_DAILY_QUESTS:
                message = "You can't do more than"
                message2 = "quests a day"
                if language != "en":
                    x = util.translate_2(message, message2, language)
                    message = x[0]
                    message = x[1]
                raise util.DueUtilException(ctx.channel, "%s %s %s" % (message, str(quests.MAX_DAILY_QUESTS), message2))
                break

        quest = player.quests.pop(0)
        battle_log = battles.get_battle_log(player_one=player, player_two=quest, p2_prefix="the ")
        battle_embed = battle_log.embed
        turns = battle_log.turn_count
        winner = battle_log.winner
        stats.increment_stat(stats.Stat.QUESTS_ATTEMPTED)
        # Not really an average (but w/e)
        average_quest_battle_turns = player.misc_stats["average_quest_battle_turns"] = (player.misc_stats[
                                                                                            "average_quest_battle_turns"] + turns) / 2
        if winner == quest:
            quest_results = (":skull: **" + player.name_clean + "** lost to the **" + quest.name_clean + "** and dropped ``"
                             + util.format_number(quest.money // 2, full_precision=True, money=True) + "``")
            player.money -= quest.money // 2
            player.quest_spawn_build_up += 0.1
            player.misc_stats["quest_losing_streak"] += 1
            if player.misc_stats["quest_losing_streak"] == 10:
                await awards.give_award(ctx.channel, player, "QuestLoser")
            n += 1
        elif winner == player:
            try:
                if player.team >= 0:
                    player.team = None
            except:
                pass
            if player.quest_day_start == 0:
                player.quest_day_start = time.time()
            skip = 0
            team = None
            if player.team is not None:
                team = teams.get_team_no_id(player.team.lower())
                skip = 0
                if team is None:
                    skip += 1
                    await util.say(ctx.channel, "I couldn't find your team to add exp to!")
            player.quests_completed_today += 1
            player.quests_won += 1

            reward = (
                ":sparkles: **" + player.name_clean + "** defeated the **" + quest.name + "** and was rewarded with ``"
                + util.format_number(quest.money, full_precision=True, money=True) + "``\n")
            quest_scale = quest.get_quest_scale()
            avg_player_stat = player.get_avg_stat()

            def attr_gain(stat):
                return (max(0.01, (stat / avg_player_stat)
                            * quest.level * (turns / average_quest_battle_turns) / 2 * (quest_scale + 0.5) * 3 * d))

            add_strg = min(attr_gain(quest.strg), b)
            # Limit these with add_strg. Since if the quest is super strong. It would not be beatable.
            # Add a little random so the limit is not super visible
            add_attack = min(attr_gain(quest.attack), min(add_strg * 3 * random.uniform(0.6, 1.4), b))
            add_accy = min(attr_gain(quest.accy), min(add_strg * 3 * random.uniform(0.6, 1.4), b))

            stats_reward = players.STAT_GAIN_FORMAT % (add_attack, add_strg, add_accy)
            quest_results = reward + stats_reward
            aa = int(aa) + int(int(add_strg + add_attack + add_accy) / 3)
            team_exp = player.progress(add_attack, add_strg, add_accy, max_attr=b, max_exp=c, return_exp=True)
            player.money += int(quest.money * (a / 3))
            stats.increment_stat(stats.Stat.MONEY_CREATED, int(quest.money))
            if not hasattr(player, "team_money"):
                player.team_money = 0
            if player.team != None:
                if player.prestige_coins >= 7.5:
                    player.team_money += int(math.log(player.prestige_coins, 7.5))
                else:
                    player.team_money += 1
            if skip == 0 and team != None:
                team.exp += team_exp
                team.total_exp += team_exp
                await game.team_check_for_level_up(ctx, team)
                team.save()
            z = float(random.random() / player.dummy_chance)
            if z <= .1 and player.dummies < player.dummy_max:
                player.dummies += 1
                message = "You recieved a training dummy! You now have " + str(player.dummies) + " training dummies!"
                if language != "en":
                    message = util.translate(message, language)
                await util.say(ctx.channel, "%s" % (message))

            quest_info = quest.info
            if quest_info is not None:
                quest_info.times_beaten += 1
                quest_info.save()
            await game.check_for_level_up(ctx, player)
            player.misc_stats["quest_losing_streak"] = 0
        else:
            quest_results = ":question: Against all you drew with the quest!"
        # Put this here to avoid 'spoiling' results before battle log
        if winner == player:
            await awards.give_award(ctx.channel, player, "QuestDone", "*Saved* the server!")
        elif winner == quest:
            await awards.give_award(ctx.channel, player, "RedMist", "Red mist...")
        else:
            await awards.give_award(ctx.channel, player, "InconceivableQuest")
        n += 1
        if (n % 5) == 0:
            battle_embed.add_field(name="Quest results", value=quest_results, inline=False)
            await imagehelper.battle_screen(ctx.channel, player, quest)
            await util.say(ctx.channel, embed=battle_embed)
            e = i - n
            if e < 0:
                e = 0
            await util.say(ctx.channel, "This is quest **#%s**. **%s** left!" % (n, e))
        await asyncio.sleep(.05)
        player.save()
    aa = float(aa / n)
    aa = round(aa, 2)
    y = aa * 100
    message = "Wow that was a lot! You gained an average of"
    message2 = "of each stat per quest, and got"
    message3 = "experience per quest while doing"
    message4 = "quests"
    if language != "en":
        x = util.translate_4(message, message2, message3, message4, language)
        message = x[0]
        message2 = x[1]
        message3 = x[2]
        message4 = x[3]
    await util.say(ctx.channel, "%s **%s** %s **%s** %s **%s** %s" % (message, aa, message2, y, message3, n, message4))


@commands.command(args_pattern="CS?P?C?")
@commands.ratelimit(cooldown=1800,
                    error="You have to wait 30 minutes per send! You have **[COOLDOWN]** left!",
                    save=True)
async def sendquest(ctx, quest_index, *args, **details):
    """
    [CMD_KEY]sendquest (quest # to sacrifice) (name) (@user) (level)  

    You will lose the quest number that you sacrifice, but in exchange, the bot will spawn the player specified a quest with the specified name and level.  
    [PERM]
    """

    player = details["author"]
    
    if len(args) == 0:
        if quests.has_quests(ctx.channel):
            quest = quests.get_random_quest_in_channel(ctx.channel)
        else:
            raise util.DueUtilException(ctx.channel, "Could not find a quest in this channel to send!")
    else:
        if len(args) >= 2:
            player = args[1]
        quest_name = args[0].lower()
        quest = quests.get_quest_from_id(ctx.server.id + "/" + quest_name)

    try:
        quest_index -= 1
        if quest_index < len(player.quests):
            quest = player.quests[quest_index]
            del player.quests[quest_index]
            player.save()
            active_quest = await quests.ActiveQuest.create(quest.q_id, player)
        else:
            raise util.DueUtilException(ctx.channel, "You don't have any quests to send")
        if len(args) == 3:
            active_quest.level = args[2]
            await active_quest._calculate_stats()
            player.save()
            await util.say(ctx.channel, "Sent Level " + str(active_quest.level) + " " + quest.name_clean + "")
        else:
            raise util.DueUtilException(ctx.channel, "Use the correct format in the help page!")
    except:
        raise util.DueUtilException(ctx.channel, "Failed to send quest!")

@commands.command(args_pattern=None, aliases=['qc'])
async def questcheck(ctx, **details):
    """
    [CMD_KEY]questcheck

    Tells you how much time you have left until your daily quest limit resets, and how long until you can get a quest again.
    [PERM]
    """

    player = details["author"]
    reset_wait = 86400 - (time.time() - player.quest_day_start)
    reset_wait_2 = util.display_time(reset_wait)
    chance_wait = 300 - (time.time() - player.last_quest)
    if chance_wait >= 0:
        if not player.learning:
            chance_wait_2 = util.display_time(chance_wait)
            await util.say(ctx.channel, ("You have **%s** until your quest day restarts, and **%s** until you have a chance for a quest again!\n"
                                         + "You have beaten **%s** quests since the last reset! If times seem weird, beating a quest should fix them up!")
                           % (reset_wait_2, chance_wait_2, player.quests_completed_today))
        else:
            chance_wait_2 = util.display_time(chance_wait)
            await util.say(ctx.channel, ("You have **%s** until your quest day restarts, and you have half the chance to get a quest (because you're learning).\n"
                                         + "You have to wait **%s** until you can get a quest again.\n"
                                         + "You have beaten **%s** quests since the last reset! If times seem weird, beating a quest should fix them up!")
                           % (reset_wait_2, chance_wait_2, player.quests_completed_today))
    else:
        await util.say(ctx.channel, ("You have **%s** until your quest day restarts, and you currently cannot get a quest (you either have max quests waiting or you've beaten the max quests).\n"
                                     + "You have beaten **%s** quests since the last reset! If times seem weird, beating a quest should fix them up!")
                       % (reset_wait_2, player.quests_completed_today))


@commands.command(args_pattern='C', aliases=['qi'])
@commands.imagecommand()
async def questinfo(ctx, quest_index, **details):
    """
    [CMD_KEY]questinfo index
    
    Shows a simple stats page for the quest.
    [PERM]
    """

    player = details["author"]
    quest_index -= 1
    if 0 <= quest_index < len(player.quests):
        await imagehelper.quest_screen(ctx.channel, player.quests[quest_index])
    else:
        raise util.DueUtilException(ctx.channel, "Quest not found!")


@commands.command(args_pattern='C?', aliases=['mq'])
@commands.imagecommand()
async def myquests(ctx, page=1, **details):
    """
    [CMD_KEY]myquests
    
    Shows the list of active quests you have pending.
    [PERM]
    """

    player = details["author"]
    page -= 1
    # Always show page 1 (0)
    if page != 0 and page * 5 >= len(player.quests):
        raise util.DueUtilException(ctx.channel, "Page not found")
    await imagehelper.quests_screen(ctx.channel, player, page)


@commands.command(args_pattern='C?', aliases=['aq'])
@commands.imagecommand()
async def acceptquest(ctx, quest_index=1, **details):
    """
    [CMD_KEY]acceptquest (quest number)

    You know what to do. Spam ``[CMD_KEY]acceptquest 1``!

    If you just do ``!aq``, it'll default to accepting your oldest quest.
    [PERM]
    """

    player = details["author"]
    quest_index -= 1
    language = player.language
    if quest_index >= len(player.quests):
        message = "Quest not found, you likely do not have this many quests!"
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if player.money - player.quests[quest_index].money // 2 < 0:
        message = "You can't afford the risk!"
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if not hasattr(player, "double_quests"):
        player.double_quests = False
    if player.donor or player.double_quests:
        if player.quests_completed_today >= quests.TEAM_MAX_DAILY_QUESTS:
            message = "You can't do more than"
            message2 = "quests a day"
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message = x[1]
            raise util.DueUtilException(ctx.channel, "%s %s %s" % (message, str(quests.TEAM_MAX_DAILY_QUESTS), message2))
    else:
        if player.quests_completed_today >= quests.MAX_DAILY_QUESTS:
            message = "You can't do more than"
            message2 = "quests a day"
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message = x[1]
            raise util.DueUtilException(ctx.channel, "%s %s %s" % (message, str(quests.MAX_DAILY_QUESTS), message2))

    if not hasattr(player, "defense"):
        player.defense = 1
    if not hasattr(player, "team"):
        player.team = None
    if not hasattr(player, "dummy_max"):
        player.dummy_max = 10
    if not hasattr(player, "dummies"):
        player.dummies = 0
    if not hasattr(player, "dummy_chance"):
        player.dummy_chance = 1
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    if not hasattr(player, "prestiges"):
        player.prestiges = 0

    quest = player.quests.pop(quest_index)
    battle_log = battles.get_battle_log(player_one=player, player_two=quest, p2_prefix="the ")
    battle_embed = battle_log.embed
    turns = battle_log.turn_count
    winner = battle_log.winner
    stats.increment_stat(stats.Stat.QUESTS_ATTEMPTED)
    # Not really an average (but w/e)
    average_quest_battle_turns = player.misc_stats["average_quest_battle_turns"] = (player.misc_stats[
                                                                                        "average_quest_battle_turns"] + turns) / 2
    if winner == quest:
        quest_results = (":skull: **" + player.name_clean + "** lost to the **" + quest.name_clean + "** and dropped ``"
                         + util.format_number(quest.money // 2, full_precision=True, money=True) + "``")
        player.money -= quest.money // 2
        player.quest_spawn_build_up += 0.1
        player.misc_stats["quest_losing_streak"] += 1
        if player.misc_stats["quest_losing_streak"] == 10:
            await awards.give_award(ctx.channel, player, "QuestLoser")
    elif winner == player:
        if player.quest_day_start == 0:
            player.quest_day_start = time.time()
        skip = 0
        team = None
        try:
            if player.team >= 0:
                player.team = None
        except:
            pass
        if player.team is not None and player.team != 0:
            team = teams.get_team_no_id(player.team.lower())
            skip = 0
            if team is None:
                skip += 1
                await util.say(ctx.channel, "I couldn't find your team to add exp to!")
        player.quests_completed_today += 1
        player.quests_won += 1

        reward = (
            ":sparkles: **" + player.name_clean + "** defeated the **" + quest.name + "** and was rewarded with ``"
            + util.format_number(quest.money, full_precision=True, money=True) + "``\n")
        quest_scale = quest.get_quest_scale()
        avg_player_stat = player.get_avg_stat()
        a = player.prestige_bonus()
        b = 100 * a
        c = 10000 * a
        if a >= 2.5:
            d = math.log(a, 2.5)
        else:
            d = a 
        def attr_gain(stat):
            return (max(0.01, (stat / avg_player_stat)
                        * quest.level * (turns / average_quest_battle_turns) / 2 * (quest_scale + 0.5) * 3 * d))

        add_strg = min(attr_gain(quest.strg), b)
        # Limit these with add_strg. Since if the quest is super strong. It would not be beatable.
        # Add a little random so the limit is not super visible
        add_attack = min(attr_gain(quest.attack), min(add_strg * 3 * random.uniform(0.6, 1.4), b))
        add_accy = min(attr_gain(quest.accy), min(add_strg * 3 * random.uniform(0.6, 1.4), b))

        if attr_gain(quest.strg) <= .1:
            await util.say(ctx.channel, "Do you keep getting super low stats from quests? That's likely because you're using too strong of a weapon for quests, try to use ones with 86% accuracy, and less than 30 damage. Feel free to use strong weapons in PvP though!")

        stats_reward = players.STAT_GAIN_FORMAT % (add_attack, add_strg, add_accy)
        quest_results = reward + stats_reward

        team_exp = player.progress(add_attack, add_strg, add_accy, max_attr=b, max_exp=c, return_exp=True)
        player.money += int(quest.money * (a / 3))
        stats.increment_stat(stats.Stat.MONEY_CREATED, int(quest.money))
        if not hasattr(player, "team_money"):
            player.team_money = 0
        if player.team != None:
            if player.prestige_coins >= 6:
                player.team_money += int(math.log(player.prestige_coins, 6))
            else:
                player.team_money += 1

        if skip == 0 and team != None:
            team.exp += team_exp
            team.total_exp += team_exp
            await game.team_check_for_level_up(ctx, team)
            team.save()
        z = float(random.random() / player.dummy_chance)
        if z <= .1 and player.dummies < player.dummy_max:
            player.dummies += 1
            message = "You recieved a training dummy! You now have " + str(player.dummies) + " training dummies!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))
        elif player.dummies > player.dummy_max:
            player.dummies = player.dummy_max
            message = "Your dummy count was reset because it was above your dummy max! Buy a higher max with teambuy!"
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.channel, "%s" % (message))

        quest_info = quest.info
        if quest_info is not None:
            quest_info.times_beaten += 1
            quest_info.save()
        await game.check_for_level_up(ctx, player)
        player.misc_stats["quest_losing_streak"] = 0
    else:
        quest_results = ":question: Against all you drew with the quest!"
    battle_embed.add_field(name="Quest results", value=quest_results, inline=False)
    await imagehelper.battle_screen(ctx.channel, player, quest)
    await util.say(ctx.channel, embed=battle_embed)
    # Put this here to avoid 'spoiling' results before battle log
    if winner == player:
        await awards.give_award(ctx.channel, player, "QuestDone", "*Saved* the server!")
    elif winner == quest:
        await awards.give_award(ctx.channel, player, "RedMist", "Red mist...")
    else:
        await awards.give_award(ctx.channel, player, "InconceivableQuest")
    player.save()


@commands.command(args_pattern='C', aliases=["dq"])
async def declinequest(ctx, quest_index, **details):
    """
    [CMD_KEY]declinequest index

    Declines a quest because you're too wimpy to accept it.
    [PERM]
    """

    player = details["author"]
    if not hasattr(player, "prestige_coins"):
        player.prestige_coins = 0
    quest_index -= 1
    if quest_index < len(player.quests):
        quest = player.quests[quest_index]
        if player.prestige_coins > 0:
            add_attack = round(math.log(player.prestige_coins, 1.5), 2)
            add_strg = round(math.log(player.prestige_coins, 1.5), 2)
            add_accy = round(math.log(player.prestige_coins, 1.5), 2)
            a = add_attack * 3
            b = a * 100
            player.progress(add_attack, add_strg, add_accy, max_attr=a, max_exp=b)
            await util.say(ctx.channel, ("**" + player.name_clean + "** got a stat refund of %s from their prestige coins!" % (add_attack)))
            await game.check_for_level_up(ctx, player)
        del player.quests[quest_index]
        player.save()
        quest_info = quest.info
        if quest_info is not None:
            quest_task = quest_info.task
        else:
            quest_task = "do a long forgotten quest:"
        await util.say(ctx.channel, ("**" + player.name_clean + "** declined to "
                                     + quest_task + " **" + quest.name_clean
                                     + " [Level " + str(math.trunc(quest.level)) + "]**!"))
    else:
        raise util.DueUtilException(ctx.channel, "Quest not found!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='SRRRRS?S?S?%?I?', aliases=["cq"])
async def createquest(ctx, name, attack, strg, accy, hp,
                      task=None, weapon=None, image_url=None, spawn_chane=25, rank=1000, **_):
    """
    [CMD_KEY]createquest name (base attack) (base strg) (base accy) (base hp)
    
    You can also add (task string) (weapon) (image url) (spawn chance) (rank)
    after the first four args.
    
    Note a base value is how strong the quest would be at level 1
    
    __Example__:
    Basic Quest:
        ``[CMD_KEY]createquest "Mega Mouse" 1.3 2 1.1 32``
        This creates a quest named "Mega Mouse".
        With base values:
            Attack = 1.3
            Strg = 2
            Accy = 1.1
            HP = 32
    Advanced Quest:
        ``[CMD_KEY]createquest "Snek Man" 1.3 2 1.1 32 "Kill the" "Dagger" http://i.imgur.com/sP8Rnhc.png 21 3``
        This creates a quest with the same base values as before but with the message "Kill the"
        when the quest pops up, a dagger, a quest icon image, a spawn chance of 21%, and players have to be rank 3, or levels 21-30 to recieve it.
    [PERM]
    """
    if len(quests.get_server_quest_list(ctx.server)) >= gconf.THING_AMOUNT_CAP:
        raise util.DueUtilException(ctx.server, "Whoa, you've reached the limit of %d quests!"
                                    % gconf.THING_AMOUNT_CAP)

    extras = {"spawn_chance": spawn_chane}
    if task is not None:
        extras['task'] = task
    if weapon is not None:
        weapon_name_or_id = weapon
        weapon = weapons.find_weapon(ctx.server, weapon_name_or_id)
        if weapon is None:
            raise util.DueUtilException(ctx.channel, "Weapon for the quest not found!")
        extras['weapon_id'] = weapon.w_id
    if image_url is not None:
        extras['image_url'] = image_url
    if 1 <= rank <= 10:
        extras['rank'] = rank
    else:
        extras['rank'] = 1000

    new_quest = quests.Quest(name, attack, strg, accy, hp, **extras, ctx=ctx)
    await util.say(ctx.channel, ":white_check_mark: " + util.ultra_escape_string(
        new_quest.task) + " **" + new_quest.name_clean + "** is now active!")
    if "image_url" in extras:
        await imagehelper.warn_on_invalid_image(ctx.channel, url=extras["image_url"])


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='SS*')
@commands.extras.dict_command(optional={"attack/atk": "R", "strg/strength": "R", "hp": "R",
                                        "accy/accuracy": "R", "spawn": "%", "weapon/weap": "S",
                                        "image": "S", "task": "S", "channel": "S", "rank":"I"})
async def editquest(ctx, quest_name, updates, **_):
    """
    [CMD_KEY]editquest name (property value)+

    Any number of properties can be set at once.
    This is also how you set quest channels!

    Properties:
        __attack__, __hp__, __accy__, __spawn__, __weapon__,
        __image__, __task__, __strg__, __rank__, and __channel__

    Example usage:

        [CMD_KEY]editquest "snek man" hp 43 attack 4.2 task "Kill the monster"

        [CMD_KEY]editquest slime channel ``#slime_fields``
    [PERM]
    """

    quest = quests.get_quest_on_server(ctx.server, quest_name)
    if quest is None:
        raise util.DueUtilException(ctx.channel, "Quest not found!")
    if not hasattr(quest, "rank"):
        quest.rank = 1000
    new_image_url = None
    for quest_property, value in updates.items():
        # Validate and set updates.
        if quest_property in ("attack", "atk", "accy", "accuracy", "strg", "strength"):
            if value >= 1:
                if quest_property in ("attack", "atk"):
                    quest.base_attack = value
                elif quest_property in ("accy", "accuracy"):
                    quest.base_accy = value
                else:
                    quest.base_strg = value
            else:
                updates[quest_property] = "Must be at least 1!"
            continue
        elif quest_property == "spawn":
            if 25 >= value >= 1:
                quest.spawn_chance = value / 100
            else:
                updates[quest_property] = "Must be 1-25%!"
        elif quest_property == "hp":
            if value >= 30:
                quest.base_hp = value
            else:
                updates[quest_property] = "Must be at least 30!"
        elif quest_property in ("weap", "weapon"):
            weapon = weapons.get_weapon_for_server(ctx.server.id, value)
            if weapon is not None:
                quest.w_id = weapon.w_id
                updates[quest_property] = weapon
            else:
                updates[quest_property] = "Weapon not found!"
        elif quest_property == "channel":
            if value.upper() in ("ALL", "NONE"):
                quest.channel = value.upper()
                updates[quest_property] = value.title()
            else:
                channel_id = value.replace("<#", "").replace(">", "")
                channel = util.get_client(ctx.server.id).get_channel(channel_id)
                if channel is not None:
                    quest.channel = channel.id
                else:
                    updates[quest_property] = "Channel not found!"
        elif quest_property == "rank":
            if 1 <= value <= 10 or value == 1000:
                quest.rank = value
            else:
               await util.say(ctx.channel, "Rank has to be between 1 and 10, or use 1000 for every rank.")
        else:
            updates[quest_property] = util.ultra_escape_string(value)
            if quest_property == "image":
                new_image_url = quest.image_url = value
            else:
                # Task
                quest.task = value
                updates[quest_property] = '"%s"' % updates[quest_property]

    # Format result.
    if len(updates) == 0:
        await util.say(ctx.channel, "You need to provide a valid list of changes for the quest!")
    else:
        quest.save()
        result = e.QUEST + " **%s** updates!\n" % quest.name_clean
        for quest_property, update_result in updates.items():
            result += ("``%s`` → %s\n" % (quest_property, update_result))
        await util.say(ctx.channel, result)
        if new_image_url is not None:
            await imagehelper.warn_on_invalid_image(ctx.channel, new_image_url)


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='S', aliases=["rq"])
async def removequest(ctx, quest_name, **_):
    """
    [CMD_KEY]removequest (quest name)
    
    Systematically exterminates all instances of the quest...
    ...Even those yet to be born
    [PERM]
    """

    quest_name = quest_name.lower()
    quest = quests.get_quest_on_server(ctx.server, quest_name)
    if quest is None:
        raise util.DueUtilException(ctx.channel, "Quest not found!")

    quests.remove_quest_from_server(ctx.server, quest_name)
    await util.say(ctx.channel, ":white_check_mark: **" + quest.name_clean + "** is no more!")


@commands.command(permission=Permission.REAL_SERVER_ADMIN, args_pattern="S?")
@commands.require_cnf(warning="This will **__permanently__** delete all your quests!")
async def resetquests(ctx, **_):
    """
    [CMD_KEY]resetquests

    Genocide in a command!
    This command will **delete all quests** on your server.
    [PERM]
    """

    quests_deleted = quests.remove_all_quests(ctx.server)
    if quests_deleted > 0:
        await util.say(ctx.channel, ":wastebasket: Your quests have been reset—**%d %s** deleted."
                                    % (quests_deleted, util.s_suffix("quest", quests_deleted)))
    else:
        await util.say(ctx.channel, "There's no quests to delete!")


@commands.command(args_pattern='M?', aliases=["sq"])
async def serverquests(ctx, page=1, **details):
    """
    [CMD_KEY]serverquests (page or quest name)

    Lists the quests active on your server.

    If you would like to see the base stats of a quest do [CMD_KEY]serverquests (quest name)

    Remember you can edit any of the quests on your server with [CMD_KEY]editquest
    [PERM]
    """

    @misc.paginator
    def quest_list(quests_embed, current_quest, **_):
        quests_embed.add_field(name=current_quest.name_clean,
                               value="Completed %s time" % current_quest.times_beaten
                                     + ("s" if current_quest.times_beaten != 1 else "") + "\n"
                                     + "Active channel: %s"
                                       % current_quest.get_channel_mention(ctx.server))

    if type(page) is int:
        page -= 1

        quests_list = list(quests.get_server_quest_list(ctx.server).values())
        quests_list.sort(key=lambda server_quest: server_quest.times_beaten, reverse=True)

        # misc.paginator handles all the messy checks.
        quest_list_embed = quest_list(quests_list, page, e.QUEST+" Quests on " + details["server_name_clean"],
                                      footer_more="But wait there more! Do %sserverquests %d" % (details["cmd_key"], page+2),
                                      empty_list="There are no quests on this server!\nHow sad.")

        await util.say(ctx.channel, embed=quest_list_embed)
    else:
        # TODO: Improve
        quest_info_embed = discord.Embed(type="rich", color=gconf.DUE_COLOUR)
        quest_name = page
        quest = quests.get_quest_on_server(ctx.server, quest_name)
        if quest is None:
            raise util.DueUtilException(ctx.channel, "Quest not found!")
        quest_info_embed.title = "Quest information for the %s " % quest.name_clean
        quest_info_embed.description = "You can edit these values with %seditquest %s (values)" \
                                       % (details["cmd_key"], quest.name_command_clean.lower())

        attributes_formatted = tuple(util.format_number(base_value, full_precision=True)
                                     for base_value in quest.base_values() + (quest.spawn_chance * 100,))
        quest_info_embed.add_field(name="Base stats", value=((e.ATK + " **ATK** - %s \n"
                                                              + e.STRG + " **STRG** - %s\n"
                                                              + e.ACCY + " **ACCY** - %s\n"
                                                              + e.HP + " **HP** - %s\n"
                                                              + e.QUEST + " **Spawn %%** - %s\n")
                                                             % attributes_formatted))
        quest_weapon = weapons.get_weapon_from_id(quest.w_id)
        if not hasattr(quest, "rank"):
            quest.rank = "All"
        quest_rank = quest.rank
        if quest_rank == 1000:
            quest_rank = "All"
        quest_info_embed.add_field(name="Other attributes", value=(e.QUESTINFO + " **Image** - [Click to view](%s)\n"
                                                                   % util.ultra_escape_string(quest.image_url)
                                                                   + ':speech_left: **Task message** - "%s"\n'
                                                                   % util.ultra_escape_string(quest.task)
                                                                   + e.WPN + " **Weapon** - %s\n" % quest_weapon
                                                                   + e.CHANNEL + " **Channel** - %s\n"
                                                                   % quest.get_channel_mention(ctx.server)
                                                                   + "**Rank** - %s" % (quest_rank)),
                                   inline=False)
        quest_info_embed.set_thumbnail(url=quest.image_url)
        await util.say(ctx.channel, embed=quest_info_embed)

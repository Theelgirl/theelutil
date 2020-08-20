import math
import random
import re
import time
import numpy
from numpy.random import choice
import discord

# import enchant
#import ssdeep
# from guess_language import guess_language

import generalconfig as gconf
from .. import events
from .. import util, dbconn
from ..game import players, raids
from ..game import stats, weapons, quests, awards, shields
from ..game.configs import dueserverconfig
from ..game.helpers import imagehelper
from . import gamerules
from ..game.helpers.misc import Ring

# from threading import Lock

SPAM_TOLERANCE = 80
# For awards in the first week. Not permanent.
old_players = open('oldplayers.txt').read()  # For comeback award
testers = open('testers.txt').read()  # For testers award
# spelling_lock = Lock()
awayfromkeyboard = []
awayfromkeyboardmessage = []
criminals = []


def get_spam_level(player, message_content):
    #"""
    #Get's a spam level for a message using a 
    #fuzzy hash > 50% means it's probably spam
    #"""
    #message_hash = ssdeep.hash(message_content)
    spam_level = 0
    #spam_levels = [ssdeep.compare(message_hash, prior_hash) for prior_hash in player.last_message_hashes if
                   #prior_hash is not None]
    #if len(spam_levels) > 0:
        #spam_level = max(spam_levels)
    #player.last_message_hashes.append(message_hash)
    #if spam_level > SPAM_TOLERANCE:
        #player.spam_detections += 1
    return spam_level

def original_get_spam_level(player, message_content):
    """
    Get's a spam level for a message using a 
    fuzzy hash > 50% means it's probably spam
    """
    if not hasattr(player, "last_message_hashes"):
        player.last_message_hashes = Ring(10)
    message_hash = ssdeep.hash(message_content)
    spam_level = 0
    spam_levels = [ssdeep.compare(message_hash, prior_hash) for prior_hash in player.last_message_hashes if
                   prior_hash is not None]
    if len(spam_levels) > 0:
        spam_level = max(spam_levels)
    player.last_message_hashes.append(message_hash)
    if spam_level > SPAM_TOLERANCE:
        player.spam_detections += 1
    return spam_level

def progress_time(player):
    return time.time() - player.last_progress >= 60


def quest_time(player):
    return time.time() - player.last_quest >= quests.QUEST_COOLDOWN


async def player_message(message, player, spam_level):
    """
    W.I.P. Function to allow a small amount of exp
    to be gained from messaging.
    
    """

    def get_words():
        return re.compile('\w+').findall(message.content)

    if player is not None:

        # Mention the old bot award
        if gconf.DEAD_BOT_ID in message.raw_mentions:
            await awards.give_award(message.channel, player, "SoCold", "They're not coming back.")
        # Art award
        if player.misc_stats["art_created"] >= 100:
            await awards.give_award(message.channel, player, "ItsART")
        if not hasattr(player, "job"):
            player.job = []
        if not hasattr(player, "learning"):
            player.learning = False
        if not hasattr(player, "learning_end"):
            player.learning_end = time.time()
        if not hasattr(player, "tax_status"):
            player.tax_status = False
        if not hasattr(player, "tax_filing"):
            player.tax_filing = time.time()
        if player.learning:
            if int(player.learning_end) <= int(time.time()):
                await util.say(message.author, "Your learning time is finished!")
                player.learning = False
                x = 0
                y = 1
                z = 2
                if "head teacher" in player.job:
                    x += z
                if "teacher" in player.job:
                    x += y
                player.education += (x / z) + 1
        if player.tax_status:
            if (int(time.time() - int(player.tax_filing))) > 172800:
                a = (player.level * ((int(time.time()) - int(player.tax_filing)) / 2) / 10)
                if (player.money - a) < 10000:
                    a = player.money - 10000
                    player.money = 10000
                else:
                    player.money -= a
                player.tax_filing = int(time.time())
                if player.id in criminals:
                    criminals.remove(player.id)
                await util.say(message.author, "You lost %s DUT for failing to file your taxes for your job!" % (a))
            if (int(time.time()) - int(player.tax_filing)) > 86400:
                if not player.id in criminals:
                    criminals.append(player.id)
                    await util.say(message.author, "You have been put on the toil raid list because you haven't filed taxes in a day!")
        if progress_time(player) and spam_level < SPAM_TOLERANCE:

            if len(message.content) > 0:
                player.last_progress = time.time()
            else:
                return
            if not hasattr(player, "language"):
                player.language = "en"

            # Special Awards
            # Comeback award
            if player.id in old_players:
                await awards.give_award(message.channel, player, "CameBack", "Return to DueUtil")
            # Tester award
            if player.id in testers:
                await awards.give_award(message.channel, player, "Tester", ":bangbang: **Something went wrong...**")
            # Donor award
            if player.donor:
                await awards.give_award(message.channel, player, "Donor",
                                        "Donate to DueUtil!!! :money_with_wings: :money_with_wings: :money_with_wings:")
            # DueUtil tech award
            if dbconn.conn()["dueutiltechusers"].find({"_id": player.id}).count() > 0:
                if "DueUtilTech" not in player.awards:
                    player.inventory["themes"].append("dueutil.tech")
                await awards.give_award(message.channel, player, "DueUtilTech", "<https://dueutil.org/>")

            ### DueUtil - the hidden spelling game!
            # The non-thread safe Apsell calls
            # spelling_lock.acquire()
            # DISABLED: Spell checking due to random seg faults (even with locks).
            """lang = guess_language(message.content)
            if lang in enchant.list_languages():
                spelling_dict = enchant.Dict(lang)
            else:
                spelling_dict = enchant.Dict("en_GB")

            spelling_score = 0
            big_word_count = 1
            big_word_spelling_score = 0
            message_words = get_words()
            for word in message_words:
                if len(word) > 4:
                    big_word_count += 1
                if random.getrandbits(1):  # spelling_dict.check(word):
                    spelling_score += 3
                    if len(word) > 4:
                        big_word_spelling_score += 1
                else:
                    spelling_score -= 1
            # spelling_lock.release()
            # We survived?!

            spelling_score = max(1, spelling_score / ((len(message_words) * 3) + 1))
            spelling_avg = player.misc_stats["average_spelling_correctness"]
            1 - abs(spelling_score - spelling_avg)
            spelling_strg = big_word_spelling_score / big_word_count
            # Not really an average (like quest turn avg) (but w/e)
            player.misc_stats["average_spelling_correctness"] = (spelling_avg + spelling_score) / 2

            len_limit = max(1, 120 - len(message.content))
            player.progress(spelling_score / len_limit, spelling_strg / len_limit, spelling_avg / len_limit)
            """

            player.hp = 10 * player.level
#            await check_for_level_up(message, player)
            player.save()

    else:
        players.Player(message.author)
        stats.increment_stat(stats.Stat.NEW_PLAYERS_JOINED)


async def check_for_level_up(ctx, player):
    """
    Handles player level ups.
    """

    exp_for_next_level = gamerules.get_exp_for_next_level(player.level)
    level_up_reward = 0
    while player.exp >= exp_for_next_level:
        player.exp -= exp_for_next_level
        player.level += 1
        level_up_reward += (player.level * 10)
        player.money += level_up_reward

        stats.increment_stat(stats.Stat.PLAYERS_LEVELED)

        exp_for_next_level = gamerules.get_exp_for_next_level(player.level)
    stats.increment_stat(stats.Stat.MONEY_CREATED, level_up_reward)
    if level_up_reward > 0:
        if dueserverconfig.mute_level(ctx.channel) < 0:
            await imagehelper.level_up_screen(ctx.channel, player, level_up_reward)
        else:
            util.logger.info("Won't send level up image - channel blocked.")
        rank = player.rank
        if 1 <= rank <= 10:
            await awards.give_award(ctx.channel, player, "Rank%d" % rank, "Attain rank %d." % rank)

async def team_check_for_level_up(ctx, team):
    """
    Handles team level ups.
    """

    exp_for_next_level = gamerules.team_get_exp_for_next_level(team.level)
    level_up_reward = 0
    while team.exp >= exp_for_next_level:
        team.exp -= exp_for_next_level
        team.level += 1

        exp_for_next_level = gamerules.team_get_exp_for_next_level(team.level)

async def manage_quests(message, player, spam_level):
    """
    Gives out quests!
    """
    if player.learning == True:
        return
    channel = message.channel
    server = message.server
    if time.time() - player.quest_day_start > quests.QUEST_DAY and player.quest_day_start != 0:
        if not hasattr(player, "quests_spawned"):
            player.quests_spawned = 0
        if not hasattr(player, "count"):
            player.count = 0
        if not hasattr(player, "discoin_transactions"):
            player.discoin_transactions = 0
        player.discoin_transactions = 0
        player.quests_completed_today = 0
        player.quest_day_start = 0
        player.quests_spawned = 0
        if player.id != "376166105917554701":
            player.count = 0
        util.logger.info("%s (%s) daily completed quests reset", player.name_assii, player.id)
    if not hasattr(player, "language"):
        player.language = "en"

    # Testing   
    if len(quests.get_server_quest_list(channel.server)) == 0:
        quests.add_default_quest_to_server(message.server)
    if quest_time(player):
        if not hasattr(player, "double_quests"):
            player.double_quests = False
        if player.double_quests:
            x = quests.TEAM_MAX_DAILY_QUESTS
        else:
            x = quests.MAX_DAILY_QUESTS
        player.last_quest = time.time()
        if quests.has_quests(channel) and len(
                player.quests) < quests.MAX_ACTIVE_QUESTS and player.quests_completed_today < x and spam_level < SPAM_TOLERANCE:
            server_quests_2 = quests.get_channel_quests(channel)
            r = random.randint(2, 7)
            while r > 0:
                try:
                    if len(server_quests_2) > 0:
                        random.shuffle(server_quests_2)
                except:
                    pass
                r -= 1
            quest_list_2 = []
            quest_chances = []
            for Quest in server_quests_2:
                c = Quest.spawn_chance
                quest_chances.append(int(c * 100))
            quest_chance_sum = sum(quest_chances)
            if not hasattr(player, "quest_spawn_boost"):
                player.quest_spawn_boost = 1
            quest_number_2 = 0
            quest_chances_2 = []
            chosen_quests = []
            check = 0
            while len(server_quests_2) > 0 and check < 20:
                quest = server_quests_2.pop()
                if not hasattr(quest, "rank"):
                    quest.rank = 1000
                #TODO: Take out the loop breaks, as they keep stopping multiple quests from being picked down at TODO 2
                if (quest.rank - 1) == (player.level // 10) or quest.rank == 1000:
                    if quest.channel == message.channel or quest.channel in ("All", "all", message.channel):
                        chosen_quests.append(quest)
                        quest_chances_2.append(((quest.spawn_chance * 100) / quest_chance_sum))
                if len(chosen_quests) == 0:
                    channel_quests = quests.get_channel_quests(channel)
                    while len(channel_quests) > 0:
                        quest = channel_quests.pop()
                        if not hasattr(quest, "rank"):
                            quest.rank = 1000
                        if (quest.rank - 1) == (player.level //10) or quest.rank == 1000:
                            chosen_quests.append(quest)
                            quest_chances_2.append(((quest.spawn_chance * 100) / quest_chance_sum))
                if len(chosen_quests) == 0:
                    channel_quests = quests.get_channel_quests(channel)
                    while len(channel_quests) > 0:
                        quest = channel_quests.pop()
                        if not hasattr(quest, "rank"):
                            quest.rank = 1000
                        chosen_quests.append(quest)
                        quest_chances_2.append(((quest.spawn_chance * 100) / quest_chance_sum))
                check += 1
                quest.save()
            quest_list_3 = []
            q = 0
            check_2 = 0
            for i in chosen_quests:
                if check_2 >= 20:
                    break
                quest_list_3.append(q)
                q += 1
                check_2 += 1
            #TODO 2: Form a loop for quest_2 and insert the quest breaks there
            if len(quest_list_3) and len(quest_chances_2) != 0:
                quest_2 = choice(quest_list_3, 1, quest_chances_2).tolist()
                quest_2 = quest_2[0]
            else:
                try:
                    quest_2 = random.randint(0, int(len(chosen_quests) - 1))
                except:
                    quest_2 = 0
            quest = chosen_quests[quest_2]
            if not hasattr(player, "prestige_coins"):
                player.prestige_coins = 0
            if not hasattr(player, "topdog_attempts"):
                player.topdog_attempts = 0
            if not hasattr(player, "quest_spawn_boost"):
                player.quest_spawn_boost = 1
            a = (player.prestige_coins / 3000 + 1) * (player.topdog_attempts / 250 + 1)
            if not player.learning:
                b = player.quest_spawn_boost
            else:
                b = (player.quest_spawn_boost / 2)
            if random.random() <= .08:
                raid = raids.get_random_raid()
                raids.ActiveRaid(raid.name, (player.level))
            elif random.random() <= (.5 * player.quest_spawn_build_up * b): # add * a if kurono isnt super OP
                new_quest = await quests.ActiveQuest.create(quest.q_id, player)
                stats.increment_stat(stats.Stat.QUESTS_GIVEN)
                player.quest_spawn_build_up = 1
                try:
                    if dueserverconfig.mute_level(message.channel) < 0:
                        await imagehelper.new_quest_screen(channel, new_quest, player)
#                    else:
#                        util.logger.info("Won't send new quest image - channel blocked.")
                except:
                    await util.say(channel, "You recieved a quest but something went wrong with sending the image!")
                util.logger.info("%s has received a quest [%s][s-id: %s]", player.name_assii, new_quest.q_id, message.server.id)
            else:
                player.quest_spawn_build_up += 0.5


async def check_for_recalls(ctx, player):
    """
    Checks for weapons that have been recalled
    """

    current_weapon_id = player.equipped["weapon"]

    weapons_to_recall = [weapon_id for weapon_id in player.inventory["weapons"] + [current_weapon_id]
                         if (weapons.get_weapon_from_id(weapon_id).id == weapons.NO_WEAPON_ID
                             and weapon_id != weapons.NO_WEAPON_ID)]

    if len(weapons_to_recall) == 0:
        return
    if current_weapon_id in weapons_to_recall:
        player.weapon = weapons.NO_WEAPON_ID
    player.inventory["weapons"] = [weapon_id for weapon_id in player.inventory["weapons"] if
                                   weapon_id not in weapons_to_recall]
    recall_amount = sum([weapons.get_weapon_summary_from_id(weapon_id).price for weapon_id in weapons_to_recall])
    player.money += recall_amount
    player.save()
#    await util.say(ctx.channel, (
#        ":bangbang: " + ("One" if len(weapons_to_recall) == 1 else "Some") + " of your weapons has been recalled!\n"
#        + "You get a refund of ``" + util.format_number(recall_amount, money=True, full_precision=True) + "``"))

async def check_afk(ctx, player):
    if not hasattr(player, "afk_message"):
        player.afk_message = 0
    if not hasattr(player, "afk"):
        player.afk = 0
    player.afk = 0
    a = player.id
    b = player.afk_message
    awayfromkeyboard.remove(a)
    awayfromkeyboardmessage.remove(b)
    await util.say(ctx.channel, "Removed your afk!")
    player.afk_message = 0

async def check_afk_ping(ctx, message):
    try:
        player_id = "".join(str(x) for x in message.raw_mentions)
        player = players.find_player(player_id)
        if not hasattr(player, "afk"):
            player.afk = 0
        if not hasattr(player, "afk_message"):
            player.afk_message = 0
        if player.id in awayfromkeyboard and player.afk == 1:
            afk_embed = discord.Embed(title="This player is AFK!", type="rich",
                                    color=gconf.DUE_COLOUR)
            afk_embed.add_field(name="AFK Message:", value=player.afk_message)
            await util.say(ctx.channel, embed=afk_embed)
    except AttributeError:
        pass
    except ValueError:
        pass

async def give_attributes(ctx, player):
    if not hasattr(player, "shield"):
        player.shield = shields.NO_SHIELD_ID
    if not hasattr(player, "shields"):
        player.shields = []
#    if not hasattr(player, "afk"):
#        player.afk = 0
#    if not hasattr(player, "afk_message"):
#        player.afk_message = 0
    if not hasattr(player, "learning"):
        player.learning = False
#    if not hasattr(player, "attribute_holder"):
#        player.attribute_holder = []
#    if not hasattr(player, "broken_status"):
#        player.broken_status = False
#    if hasattr(player, "shield"):
#        if getattr(player, "shield") == shields.NO_SHIELD_ID:
#            player.shield = shields.NO_SHIELD
#    if hasattr(player, "shield"):
#        player.shield = shields.NO_SHIELD
#    if hasattr(player, "shields"):
#        if getattr(player, "shields") == [shields.NO_SHIELD]:
#            player.shields = [shields.NO_SHIELD_2]
#    if hasattr(player, "shields"):
#        if getattr(player, "shields") == []:
#            player.shields = [shields.NO_SHIELD_2]
#    if hasattr(player, "shields"):
#        player.shields = []
#    player.shields = []
#    player.shields.clear()
#    player.inventory["shields"] = []
#    player.inventory["shields"].clear()

async def on_message(message):
    player = players.find_player(message.author.id)
    spam_level = 0
    if player is not None:
        if not player.is_playing(message.server):
            return
        if quest_time(player) or progress_time(player):
            spam_level = get_spam_level(player, message.content)
        await give_attributes(message, player)
    await player_message(message, player, spam_level)
    if player is not None:
        await manage_quests(message, player, spam_level)
        await check_for_recalls(message, player)
#        await check_afk_ping(message, message)
#        if player.afk == 1:
#            await check_afk(message, player)
#            player.afk = 0



events.register_message_listener(on_message)

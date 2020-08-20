import random
import asyncio
from collections import OrderedDict
from collections import namedtuple

import discord
import time
import math

import generalconfig as gconf
from .. import util
from ..game import weapons, awards, teams, shields
from ..game.players import Player
from ..game.shields import Shield
from ..game.quests import Quest

# Some tuples for use within this module.
_BattleResults = namedtuple("BattleResults", ["moves", "turn_count", "winner",
                                              "loser", "opponents", "p1_hits", "p2_hits"])
_BattleLog = namedtuple("BattleLog", ["embed", "turn_count", "winner", "loser"])
_Move = namedtuple("Move", ["message", "repetitions"])
_OpponentInfo = namedtuple("OpponentInfo", ["prefix", "player"])
_Opponents = namedtuple("Opponents", ["p1", "p2"])

"""
        ===################===============                                           
        ===###   ####   ###   |   |   O  =====================================================
        ===################   |===|   |  I was meant to fill up white space but python sucks ===    
        ===###          ###   |   |   |  =====================================================
        ===################===============
"""

# Some default attack messages (if the player does not have a weapon)
BABY_MOVES = ("slapped", "scratched", "hit", "punched", "licked", "bit", "kicked", "tickled")
MAX_BATTLE_LOG_LEN = 1024


class BattleRequest:
    """A class to hold a wager"""

    __slots__ = ["sender_id", "receiver_id", "wager_amount"]

    def __init__(self, sender, receiver, wager_amount):
        self.sender_id = sender.id
        self.receiver_id = receiver.id
        self.wager_amount = wager_amount
        self._add(receiver)

    def _add(self, receiver):
        receiver.received_wagers.append(self)
        receiver.save()


async def give_awards_for_battle(channel, battle_log: _BattleLog):
    """
    Award triggers that can be called after a battle.
    This can be called after a battle. Passing the battle log.
    """

    # NOTE: do not use !duereload outside of tests. It will break stuff!
    if not (isinstance(battle_log.winner, Player) or isinstance(battle_log.loser, Player)):
        return
    if battle_log.winner is not None:
        winner = battle_log.winner
        loser = battle_log.loser
        if "Duerus" in winner.awards:
            await awards.give_award(channel, loser, "Duerus")
        if "TopDog" in winner.awards:
            if not hasattr(winner, "topdog_attempts"):
                winner.topdog_attempts = 0
            if not hasattr(loser, "topdog_attempts"):
                loser.topdog_attempts = 0
            winner.topdog_attempts = winner.topdog_attempts + 1
        if not hasattr(winner, "team"):
            winner.team = 0
        if not hasattr(loser, "team"):
            loser.team = 0
        if "TopDog" in loser.awards:
            if winner.id == "354900241365073920":
                return
            if not hasattr(winner, "topdog_time_elapsed"):
                winner.topdog_time_elapsed = 0
            if not hasattr(loser, "topdog_time_elapsed"):
                loser.topdog_time_elapsed = 0
            if not hasattr(winner, "topdog_time"):
                winner.topdog_time = 0
            if not hasattr(loser, "topdog_time"):
                loser.topdog_time = 0
            if not hasattr(winner, "topdog_attempts"):
                winner.topdog_attempts = 0
            if not hasattr(loser, "topdog_attempts"):
                loser.topdog_attempts = 0
            await asyncio.sleep(1 / 1000)
            await awards.take_award(channel, loser, "TopDog")
            await asyncio.sleep(1 / 1000)
            await awards.give_award(channel, winner, "TopDog")
            awards.update_award_stat("TopDog", "top_dog", winner.id)
            awards.update_award_stat("TopDog", "times_given", 1)
            a = time.time() - loser.topdog_time_elapsed
            if a <= 10000000:
                loser.topdog_time = loser.topdog_time + a
            winner.topdog_time_elapsed = time.time()
            loser.topdog_attempts = 0
            if not hasattr(winner, "team"):
                winner.team = None
            try:
                if player.team >= 0:
                    player.team = None
            except:
                pass
            if winner.team != None:
                team = teams.get_team_no_id(winner.team)
                if team != None:
                    if not hasattr(team, "topdog_count"):
                        team.topdog_count = 0
                    team.topdog_count += 1
                    team.save()
            winner.save()
        if battle_log.turn_count == 1 and winner.level - loser.level <= 2.5:
            await  awards.give_award(channel, winner, "CritHit")
        # If it's me
        if loser.id == "132315148487622656":
            await awards.give_award(channel, winner, "KillMe")

    if not hasattr(winner, "team"):
        winner.team = 0

    if not hasattr(loser, "team"):
        loser.team = 0

    if "TopDog" in loser.awards:
        awards.update_award_stat("TopDog", "team", winner.team)


def get_battle_log(**battleargs):
    """
    Creates a formatted embed of a battle
    """

    battle_result = battle(**battleargs)
    battle_moves = list(battle_result.moves.values())
    battle_embed = discord.Embed(title=(battleargs.get('player_one').name_clean
                                        + " :vs: " + battleargs.get('player_two').name_clean), type="rich",
                                 color=gconf.DUE_COLOUR)
    battle_log = ""
    for move in battle_moves:
        move_repetition = move.repetitions
        if move_repetition <= 1:
            battle_log += move.message + '\n'
        else:
            battle_log += "(%s) × %d\n" % (move.message, move.repetitions)
    if len(battle_log) > MAX_BATTLE_LOG_LEN:
        # Too long battle.
        # Mini summary.
        player_one = battle_result.opponents.p1
        player_two = battle_result.opponents.p2
        battle_embed.description = ("Oh no! The battle was too long!\n"
                                    + "Here's a mini summary!")
        battle_embed.add_field(name="Mini summary",
                               value="%s**%s** hit **%d** %s and %s**%s** hit **%d** %s!\n"
                                     % (player_one.prefix.title(), player_one.player.name_clean, battle_result.p1_hits,
                                        util.s_suffix("time", battle_result.p1_hits),
                                        player_two.prefix, player_two.player.name_clean, battle_result.p2_hits,
                                        util.s_suffix("time", battle_result.p2_hits))
                                     + battle_moves[-1].message)
    else:
        battle_embed.add_field(name='Battle log', value=battle_log)
    battle_info = battle_result._asdict()
    # Deleted unneeded keys
    del battle_info["moves"], battle_info["opponents"], \
        battle_info["p1_hits"], battle_info["p2_hits"]
    return _BattleLog(embed=battle_embed, **battle_info)


# quest, wager normal
def battle(**battleargs):
    """
    Battles two player like things.
    Will return a log of the battle
    """

    current_move = 1
    damage_modifier = 1

    opponents = _Opponents(p1=_OpponentInfo(prefix=battleargs.get('p1_prefix', ""),
                                            player=battleargs.get('player_one')),
                           p2=_OpponentInfo(prefix=battleargs.get('p2_prefix', ""),
                                            player=battleargs.get('player_two')))

    hp = [opponents.p1.player.hp * util.clamp(5 - opponents.p1.player.level, 1, 5),
          opponents.p2.player.hp * util.clamp(5 - opponents.p2.player.level, 1, 5)]
    hit_count = [0, 0]  # p1 and p2 hit counter

    moves = OrderedDict()

    def add_move(attacker, other, message=None):
        nonlocal opponents, moves, current_move, damage_modifier
        if message is None:
            weapon = attacker.player.weapon
            if weapon.id == weapons.NO_WEAPON_ID:
                message = random.choice(BABY_MOVES)
            else:
                message = weapon.hit_message

        player_num = opponents.index(attacker)
        moves['%d/%d' % (player_num,
                         current_move)] = _Move(message=("%s**%s** %s %s**%s**"
                                                         % (attacker.prefix.title(),
                                                            attacker.player.name_clean,
                                                            message,
                                                            other.prefix,
                                                            other.player.name_clean)
                                                         ), repetitions=1)
        hit_count[player_num] += 1
        current_move += 1
        damage_modifier += 0.25

    def add_heal_move(attacker, other, heal_amount, message=None):
        nonlocal opponents, moves, current_move, damage_modifier
        player_num = opponents.index(attacker)
        moves['%d/%d' % (player_num,
                         current_move)] = _Move(message=("%s**%s** healed for **%s** HP! %s **%s** couldn't do anything!"
                                                         % (attacker.prefix.title(),
                                                            attacker.player.name_clean,
                                                            heal_amount,
                                                            other.prefix,
                                                            other.player.name_clean)
                                                         ), repetitions=1)
        hit_count[player_num] += 1
        current_move += 1
        damage_modifier -= 0.1

    def shrink_repeats(moves_to_shrink):

        """
        Replaces consecutive repeated moves with 
        moves with a single move with "repetitions"
        """

        last_move_id = None
        moves_shrink_repeat = OrderedDict()
        for move_id, move in moves_to_shrink.items():
            if last_move_id is not None:
                # If last move and this move are from the same player
                if last_move_id[0] == move_id[0]:
                    last_move = moves_shrink_repeat[last_move_id]
                    move = move._replace(repetitions=move.repetitions + last_move.repetitions)
                    move_id = last_move_id
            moves_shrink_repeat[move_id] = move
            last_move_id = move_id
        return moves_shrink_repeat

    def shrink_duos(moves_to_shrink):

        """
        Replaces moves that swich between players. With a single duo move.
        
        E.g.
        
        P1 hits P2
        P2  hits P1
        
        to P1 hits P2 <-> P2 Hits P1
        """

        moves_shrink_duos = OrderedDict()
        last_move_id = None
        count = 0
        for move_id, move in moves_to_shrink.items():
            count += 1
            if last_move_id is not None and count % 2 == 0:
                last_move = moves_to_shrink[last_move_id]
                moves_shrink_duos[last_move_id] = last_move._replace(repetitions=last_move.repetitions - 1)

                moves_shrink_duos["Duo%d" % count] = _Move(message=last_move.message + " ⇆ " + move.message,
                                                           repetitions=1)
                moves_shrink_duos[move_id] = move._replace(repetitions=move.repetitions - 1)
            last_move_id = move_id
        if len(moves_to_shrink) % 2 == 1:
            # Add missed move
            odd_move = moves_to_shrink.popitem()
            moves_shrink_duos[odd_move[0]] = odd_move[1]
        for move_id, move in list(moves_shrink_duos.items()):
            if move.repetitions <= 0:
                del moves_shrink_duos[move_id]
        return moves_shrink_duos

    def compress_moves():

        """
        Shortcut for the full process to shrink the log
        """
        nonlocal moves
        moves = shrink_repeats(shrink_duos(shrink_repeats(moves)))

    def apply_buffs():
        nonlocal opponents
        attacker = opponents.p1
        other = opponents.p2
        if not hasattr(attacker.player, "job"):
            attacker.player.job = []
        if not hasattr(attacker.player, "job_level"):
            attacker.player.job_level = 1
        if not hasattr(other.player, "job"):
            other.player.job = []
        if not hasattr(other.player, "job_level"):
            other.player.job_level = 1  
        if len(attacker.player.job) > 0:
            jobs = gconf.JOBS
            job_buffs = gconf.JOB_BUFFS
            for i in attacker.player.job:
                try:
                    job_number_for_buffs = int(gconf.JOBS.index(i))
                    attacker_player_job_number = int(job_number_for_buffs + 1)
                except:
                    attacker_player_job_number = 0
                    break
                job_level = attacker.player.job_level
                attacker_player_job_level = attacker.player.job_level
                job_buff = job_buffs[job_number_for_buffs]
                if "all" in job_buff:
                    attacker_player_strg = attacker.player.strg * (1 + (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_attack = attacker.player.attack * (1 + (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_accy = attacker.player.accy * (1 + (attacker_player_job_number * 0.1) + (job_level * 0.002))
                elif "strg" in job_buff:
                    attacker_player_strg = attacker.player.strg * (1 + (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_attack = attacker.player.attack * (1 - (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_accy = attacker.player.accy
                elif "atk" in job_buff:
                    attacker_player_attack = attacker.player.attack * (1 + (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_accy = attacker.player.accy * (1 - (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_strg = attacker.player.strg
                elif "accy" in job_buff:
                    attacker_player_accy = attacker.player.accy * (1 + (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_strg = attacker.player.strg * (1 - (attacker_player_job_number * 0.1) + (job_level * 0.002))
                    attacker_player_attack = attacker.player.attack
                else:
                    attacker_player_attack = attacker.player.attack
                    attacker_player_accy = attacker.player.accy
                    attacker_player_strg = attacker.player.strg
                    try:
                        attacker_player_job_level = attacker.player.job_level
                    except:
                        attacker_player_job_level = 1
        else:
            attacker_player_attack = attacker.player.attack
            attacker_player_accy = attacker.player.accy
            attacker_player_strg = attacker.player.strg
            attacker_player_job_number = 0
            try:
                attacker_player_job_level = attacker.player.job_level
            except:
                attacker_player_job_level = 1
        if len(other.player.job) > 0:
            jobs = gconf.JOBS
            job_buffs = gconf.JOB_BUFFS
            for i in other.player.job:
                try:
                    job_number_for_buffs = int(gconf.JOBS.index(i))
                    other_player_job_number = int(job_number_for_buffs + 1)
                except:
                    other_player_job_number = 0
                    break
                job_level = other.player.job_level
                other_player_job_level = other.player.job_level
                job_buff = job_buffs[job_number_for_buffs]
                if "all" in job_buff:
                    other_player_strg = other.player.strg * (1 + (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_attack = other.player.attack * (1 + (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_accy = other.player.accy * (1 + (other_player_job_number * 0.1) + (job_level * 0.002))
                elif "strg" in job_buff:
                    other_player_strg = other.player.strg * (1 + (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_attack = other.player.attack * (1 - (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_accy = other.player.accy
                elif "atk" in job_buff:
                    other_player_attack = other.player.attack * (1 + (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_accy = other.player.accy * (1 - (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_strg = other.player.strg
                elif "accy" in job_buff:
                    other_player_accy = other.player.accy * (1 + (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_strg = other.player.strg * (1 - (other_player_job_number * 0.1) + (job_level * 0.002))
                    other_player_attack = other.player.attack
                else:
                    other_player_attack = other.player.attack
                    other_player_accy = other.player.accy
                    other_player_strg = other.player.strg
                    try:
                        other_player_job_level = other.player.job_level
                    except:
                        other_player_job_level = 1
        else:
            other_player_attack = other.player.attack
            other_player_accy = other.player.accy
            other_player_strg = other.player.strg
            other_player_job_number = 0
            try:
                other_player_job_level = other.player.job_level
            except:
                other_player_job_level = 1
        return [attacker_player_job_number, other_player_job_number, attacker_player_job_level, other_player_job_level, attacker_player_attack, attacker_player_accy, attacker_player_strg, other_player_attack, other_player_accy, other_player_strg]

    list1 = apply_buffs()


    def apply_heal():
        nonlocal opponents
        attacker = opponents.p1
        other = opponents.p2
        if not hasattr(attacker.player, "job"):
            attacker.player.job = []
        if not hasattr(other.player, "job"):
            other.player.job = []
        if random.random() <= .25:
            if len(attacker.player.job) > 0:
                jobs = gconf.JOBS
                job_buffs = gconf.JOB_BUFFS
                for i in attacker.player.job:
                    try:
                        job_number_for_buffs = int(gconf.JOBS.index(i))
                        job_number = int(job_number_for_buffs + 1)
                    except:
                        break
                    job_buff = job_buffs[job_number_for_buffs]
                    if "/heal" in job_buff or "/all buffs" in job_buff:
                        heal_status = 1
                    else:
                        heal_status = 0
            elif len(other.player.job) > 0:
                jobs = gconf.JOBS
                job_buffs = gconf.JOB_BUFFS
                for i in other.player.job:
                    try:
                        job_number_for_buffs = int(gconf.JOBS.index(i))
                        job_number = int(job_number_for_buffs + 1)
                    except:
                        break
                    job_buff = job_buffs[job_number_for_buffs]
                    if "/heal" in job_buff or "/all buffs" in job_buff:
                        heal_status = 2
                    else:
                        heal_status = 0
            else:
                heal_status = 0
        else:
            heal_status = 0
        return heal_status

    heal_status = apply_heal()

    def fight():
        nonlocal opponents, damage_modifier
        nonlocal heal_status, list1

        hits = [opponents.p1.player.weapon_hit(),
                opponents.p2.player.weapon_hit()]
        for hitter, hit in enumerate(hits):
            if hit:
                attacker = opponents.p1 if hitter == 0 else opponents.p2
                other = opponents[1 - opponents.index(attacker)]
                if attacker == opponents.p1:
                    weapon_damage_modifier = list1[4]
                elif attacker == opponents.p2:
                    weapon_damage_modifier = list1[7]
                if not attacker.player.weapon.melee:
                    if attacker == opponents.p1:
                        weapon_damage_modifier = list1[5]
                    elif attacker == opponents.p2:
                        weapon_damage_modifier = list1[8]
                try:
                    shield_damage_modifier = other.player.shield.defense
                except:
                    shield_damage_modifier = 1
                if not hasattr(attacker.player, "defense"):
                    attacker.player.defense = 1
                if not hasattr(other.player, "defense"):
                    other.player.defense = 1
                if attacker.player.defense < 1:
                    attacker.player.defense = 1
                # Deal damage
#                if heal_status == 1:
#                    a = hp[hitter] * ((list1[0] * 0.05) + (list1[2] * 0.002)) if attacker == opponents.p1 else 0
#                    hp[hitter] += a
#                    add_heal_move(attacker, other, a)
#                if heal_status == 2:
#                    a = hp[1 - hitter] * ((list1[1] * 0.05) + (list1[3] * 0.002)) if attacker == opponents.p2 else 0
#                    hp[1 - hitter] += a
#                    add_heal_move(attacker, other, a)
                if shield_damage_modifier < 3:
                    shield_damage_modifier_2 = 3
                else:
                    shield_damage_modifier_2 = shield_damage_modifier
                try:
                    x = (((((attacker.player.weapon.damage / 10) * (weapon_damage_modifier / 10) * (math.sqrt(other.player.level) / 10)) / (list1[9] * damage_modifier / 10)) / (shield_damage_modifier / 10)) * 100000)
                except:
                    x = 2
                if x < (hp[1 - hitter] / 300):
                    x = (hp[1 - hitter] / 300)
                hp[1 - hitter] -= x
                add_move(attacker, other)

    def fight_starter():
        y = 0
        while hp[0] > 0 and hp[1] > 0 and y < 300:
            y += 1
            fight()

    fight_starter()

    compress_moves()
    if hp[0] > hp[1]:
        winner = opponents.p1
        loser = opponents.p2
    elif hp[0] < hp[1]:
        winner = opponents.p2
        loser = opponents.p1
    else:
        # Inconceivable
        winner = loser = None
    turns = current_move - 1
    moves["winner"] = _Move(message=(":trophy: %s**%s** wins in **%d** %s!"
                                     % (winner.prefix.title(),
                                        winner.player.name_clean,
                                        turns,
                                        util.s_suffix("turn", turns))
                                     ), repetitions=1)
    # Results as a simple namedturple
    return _BattleResults(moves=moves, turn_count=turns, winner=winner.player,
                          loser=loser.player, opponents=opponents, p1_hits=hit_count[0], p2_hits=hit_count[1])

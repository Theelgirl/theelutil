import discord
import time
import random
import asyncio
import time
import math

import generalconfig as gconf
from ..game import players
from ..permissions import Permission
from ..game import battles, weapons, stats, awards
from ..game.helpers import imagehelper, misc
from .. import commands, util

@commands.command(args_pattern="II", aliases=["pt"])
async def pricetest(ctx, damage, accy, **details):
    """
    [CMD_KEY]pricetest (damage) (accuracy)

    Enter the damage and accuracy of the weapon you want and it'll tell you what the price would be without creating it.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "language"):
        player.language = "en"
    price = (((damage * (accy / 100)) / .5) + 1)
    price_2 = int(price)
    message = "The weapon would cost " + str(price_2) + " DUT."
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "%s" % (message))


@commands.command(args_pattern="II", aliases=["dt"])
async def damagetest(ctx, price, accy, **details):
    """
    [CMD_KEY]damagetest (price) (accuracy)

    Enter the price and accuracy of the weapon you want and it'll tell you what the damage would be without creating it.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "language"):
        player.language = "en"
    damage = ((((price - 1) * .5) * 100) / accy)
    damage_2 = int(damage)
    message = "The weapon would need about " + str(damage_2) + " damage."
    language = player.language
    if language != "en":
        x = util.translate(message, language)
        message = x
    await util.say(ctx.channel, "%s" % (message))


@commands.command(args_pattern="II", aliases=["at"])
async def accuracytest(ctx, price, damage, **details):
    """
    [CMD_KEY]accuracytest (price) (damage)

    Enter the price and damage of the weapon you want and it'll tell you what the accuracy would be without creating it.
    [PERM]
    """
    player = details["author"]
    if not hasattr(player, "language"):
        player.language = "en"
    accy = ((((price - 1) * .5) * 100) / damage)
    accy_2 = int(accy)
    message = "The weapon would need about " + str(accy_2) + " accuracy."
    language = player.language
    if language != "en":
        x = util.translate(message, language)
        message = x
    await util.say(ctx.channel, "%s" % (message))

@commands.command(args_pattern="SSSRRS", aliases=["fw"])
async def fuseweapons(ctx, weapon_1, weapon_2, new_name, sacrifice, accy, hit_message, **details):
    """
    [CMD_KEY]fuseweapons (weapon 1) (weapon 2) (new name) (sacrifice) (accuracy desired) (hit_message)

    You will lose the two weapons you fuse, and come out with a new weapon with between 75% and 125% of the total damage of the weapons fused.

    You also get a higher multiplier by sacrificing more teamcash, so between 80% and 130%, 85% and 135%, and up to a max of 90% and 140%.

    The icon of the new weapon will be the default icon.
    [PERM]
    """

    player = details["author"]

    if not hasattr(player, "team_money"):
        player.team_money = 0

    weapon_1 = player.get_weapon(weapon_1)
    weapon_2 = player.get_weapon(weapon_2)

    if weapon_1 is None or weapon_2 is None:
        message = "One of your weapons was not found, and both need to be unequipped!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if len(player.inventory["weapons"]) > weapons.MAX_STORED_WEAPONS:
        message = "You need more than 1 and less than 7 weapons in your inventory to use this!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if weapon_1.is_stock() or weapon_2.is_stock():
        message = "You cannot include stock weapons in fusions!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if sacrifice < 100 or sacrifice > 1000 or sacrifice > player.team_money:
        message = "You cannot sacrifice less than 100 team cash, more than 1000, or more than you have!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if int(accy) > 86:
        message = "You can't make accuracy above 86!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    x = float(.9 * math.log(sacrifice, 100))
    y = float(1.1 * math.log(sacrifice, 100))
    icon='🔫'
    ranged=False
    image_url=None

    extras = {"melee": not ranged, "icon": icon}
    if image_url is not None:
        extras["image_url"] = image_url

    damage = (weapon_1.damage + weapon_2.damage) * ((random.uniform(.9, 1.1) + random.uniform(x, y)) / 2)
    limit_value = int(2 * (((damage * (accy / 100)) / .04375) + 1))
    z = 2 * player.item_value_limit
    if limit_value > z:
        message = "The total price of the final weapon would be **" + str(limit_value) + "**, which is more than 2x your limit."
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    else:
        player.team_money -= int(sacrifice)

    weapon = weapons.Weapon(new_name, hit_message, damage, accy, **extras, ctx=ctx)
    player.discard_stored_weapon(weapon_1)
    player.discard_stored_weapon(weapon_2)
    player.store_weapon(weapon)

    message = "The new weapon should show in your inventory now."
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "%s" % (message))


@commands.command(args_pattern="SR", aliases=["uw"])
async def upgradeweapon(ctx, weapon_name, multiplier, **details):
    """
    [CMD_KEY]upgradeweapon (weapon name) (multiplier)

    Allows you to attempt to upgrade your weapon!

    Select the weapon name, and a multiplier you want to upgrade it by.

    The weapon cannot be equipped if you want to upgrade it, you have to unequip it first.

    The higher the multiplier, the lower the chance it's successful (multiplier maxes at 1.5x)!
    [PERM]
    """

    player = details["author"]

    weapon = player.get_weapon(weapon_name)

    if weapon is None:
        message = "Weapon not found!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if weapon.is_stock():
        message = "You cannot upgrade stock weapons!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if not hasattr(weapon, "upgrades"):
        weapon.upgrades = 0
    if multiplier < 1 or multiplier > 1.5 or weapon.upgrades >= 6 or player.money < 5000000:
        message = "You need at least 5m DUT, and you need to use a multiplier between 1 and 1.5. Also, you can't upgrade a weapon more than 6 times."
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    else:
        percent_fail_chance = multiplier * 40
        x = random.randint(0, 100)
        if player.money < 10000000:
            if x < percent_fail_chance:
                y = float(player.money * random.uniform(.02, .04))
                z = round(y, 1)
                player.money -= z
                weapon.upgrades += 1
                message = "The attempt failed, and your money is now **" + str(player.money) + "**!"
                message2 = "Your money decreased by **" + str(z) + "**!"
                language = player.language
                if language != "en":
                    x = util.translate_2(message, message2, language)
                    message = x[0]
                    message2 = x[1]
                await util.say(ctx.channel, "%s %s" % (message, message2))
            else:
                if x >= percent_fail_chance:
                    weapon.upgrades += 1
                    player.money -= 2500000
                    weapon.price = weapon._price()
                    weapon_damage = weapon.damage * multiplier * random.uniform(1, 1.1)
                    weapon.damage = weapon_damage
                    message = "The attempt worked, and your damage has increased by the multiplier with some random! Your new weapon damage is"
                    language = player.language
                    if language != "en":
                        message = util.translate(message, language)
                    await util.say(ctx.channel, "%s **%s**!" % (message, weapon_damage))
        else:
            if x < percent_fail_chance:
                y = float(player.money * random.uniform(.02, .04))
                z = round(y, 1)
                player.money -= z
                weapon.upgrades += 1
                message = "The attempt failed, and your money is now **" + str(player.money) + "**!"
                message2 = "Your money decreased by **" + str(z) + "**!"
                language = player.language
                if language != "en":
                    x = util.translate_2(message, message2, language)
                    message = x[0]
                    message2 = x[1]
                await util.say(ctx.channel, "%s %s" % (message, message2))
            else:
                if x >= percent_fail_chance:
                    weapon.upgrades += 1
                    player.money -= 2500000
                    weapon.price = weapon._price()
                    weapon_damage = weapon.damage * multiplier * random.uniform(1, 1.1)
                    weapon.damage = weapon_damage
                    message = "The attempt worked, and your damage has increased by the multiplier with some random! Your new weapon damage is"
                    language = player.language
                    if language != "en":
                        message = util.translate(message, language)
                    await util.say(ctx.channel, "%s **%s**!" % (message, weapon_damage))

    weapon.save()
    player.save()

@commands.command(args_pattern="M?S?", aliases=["mw"])
async def myweapons(ctx, page=1, name="TheelKey", **details):
    """
    [CMD_KEY]myweapons (page)/(weapon name) (optional: type)
    
    Shows the contents of your weapon inventory.
    If you have a weapon with a name like 1, or 15, and you want to view the specific weapon stats, write ``name`` after the weapon name.
    [PERM]
    """

    player = details["author"]
    player_weapons = player.get_owned_weapons()

    if type(page) is int and name == "TheelKey":
        weapon_store = weapons_page(player_weapons, page-1,
                                    title=player.get_name_possession_clean() + " Weapons", price_divisor=4/3,
                                    empty_list="")
        if len(player_weapons) == 0:
            message = "No weapons stored!"
            message2 = "You can buy up to 6 more weapons from the shop and store them here!"
            language = player.language
            if language != "en":
                x = util.translate_2(message, message2, language)
                message = x[0]
                message2 = x[1]
            weapon_store.add_field(name=message,
                                   value=message2)
        message = "Currently equipped:"
        message2 = "Do " + details["cmd_key"] + "equip (weapon name) to equip a weapon"
        language = player.language
        if language != "en":
            x = util.translate_2(message, message2, language)
            message = x[0]
            message2 = x[1]
        weapon_store.description = message + str(player.weapon)
        weapon_store.set_footer(text=message2)
        await util.say(ctx.channel, embed=weapon_store)
    else:
        weapon_name = page
        if player.equipped["weapon"] != weapons.NO_WEAPON_ID:
            player_weapons.append(player.weapon)
        weapon = next((weapon for weapon in player_weapons if weapon.name.lower() == weapon_name.lower()), None)
        if weapon is not None:
            if not hasattr(weapon, "alias"):
                weapon.alias = weapon_name
            embed = discord.Embed(type="rich", color=gconf.DUE_COLOUR)
            info = weapon_info(**details, weapon=weapon, price_divisor=4 / 3, embed=embed)
            weapon.price = weapon._price()
            await util.say(ctx.channel, embed=info)
        else:
            message = "You don't have a weapon with that name! Make sure not to use an alias!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))


@commands.command(args_pattern="S?", aliases=["rmw"])
@commands.require_cnf(warning="This will reset your weapons without a refund, so make sure to try to sell your weapons first!")
async def resetmyweapons(ctx, cnf="", **details):
    """
    [CMD_KEY]resetmyweapons (cnf)
    This resets your weapon inventory if a weapon bug pops up.
    This is meant as a temporary command until the problem can be fixed.
    [PERM]
    """
    try:
        player.weapons.clear()
    except:
        raise util.DueUtilException(ctx.channel, "A problem clearing your weapons has occured, please file a ``!bugreport``.")
    await util.say(ctx.channel, "Cleared!")


@commands.command(args_pattern="S?", aliases=["uq"])
async def unequip(ctx, *args, **details):
    """
    [CMD_KEY]unequip
    
    Unequips your current weapon
    [PERM]
    """

    player = details["author"]
    weapon = player.weapon
    if len(args) == 1:
        if not hasattr(weapon, "alias"):
            weapon.alias = args[0]
    if not hasattr(player, "slot_increase"):
        player.slot_increase = 0
    if weapon.w_id == weapons.NO_WEAPON_ID:
        message = "You don't have anything equipped anyway!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
#    if len(player.inventory["weapons"]) >= (weapons.MAX_STORED_WEAPONS + player.slot_increase):
#        raise util.DueUtilException(ctx.channel, "No room in your weapon storage! If this pops up repeatedly and you have less than 6 weapons, sell your weapons for a refund and do ``!resetmyweapons cnf``.")
    if player.owns_weapon(weapon.name):
        message = "You already have a weapon with that name or alias stored!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if hasattr(weapon, "alias"):
        if player.owns_weapon_alias(weapon.alias):
            message = "You already have a weapon with that alias stored!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))

    player.store_weapon(weapon)
    player.weapon = weapons.NO_WEAPON_ID
    player.save()
    message = "unequipped!"
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, ":white_check_mark: **" + weapon.name_clean + "** %s" % (message))


@commands.command(args_pattern='S', aliases=["eq"])
async def equip(ctx, weapon_name, **details):
    """
    [CMD_KEY]equip (weapon name)
    
    Equips a weapon from your weapon inventory.
    [PERM]
    """

    player = details["author"]
    current_weapon = player.weapon
    x = 0
    if not hasattr(current_weapon, "alias"):
        current_weapon.alias = weapon_name
    if current_weapon.w_id != weapons.NO_WEAPON_ID:
        current_weapon_alias = str(current_weapon.alias)
        current_weapon_alias_lower = current_weapon_alias.lower()
    else:
        current_weapon_alias_lower = None
    weapon_name = weapon_name.lower()
    weapon_alias = weapon_name.lower()

    weapon = player.get_weapon(weapon_name)
    weapon_1 = player.get_weapon_alias(weapon_alias)
    if weapon is not None:
        if not hasattr(weapon, "alias"):
            weapon.alias = weapon_name
    if weapon_1 is not None:
        if not hasattr(weapon_1, "alias"):
            weapon_1.alias = weapon_name
    if weapon is None and weapon_1 is None:
        if weapon_name != current_weapon.name.lower() and weapon_alias != current_weapon_alias_lower:
            if not player.owns_weapon_alias(current_weapon.alias) and not player.owns_weapon(current_weapon.name):
                message = "You do not have that weapon stored!"
                language = player.language
                if language != "en":
                    message = util.translate(message, language)
                raise util.DueUtilException(ctx.channel, "%s" % (message))
        message = "You already have that weapon equipped!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
        return
    if weapon is not None and weapon_1 is None:
        player.discard_stored_weapon(weapon)
        player.store_weapon(player.weapon)
        x = 2
    elif weapon is None and weapon_1 is not None:
        player.discard_stored_weapon(weapon_1)
        player.store_weapon(player.weapon)
        x = 2
    elif current_weapon.w_id != weapons.NO_WEAPON_ID:
        if player.owns_weapon_alias(current_weapon.alias) and player.owns_weapon(current_weapon.name):
            if weapon is not None and weapon_1 is None:
                player.discard_stored_weapon(weapon)
                player.store_weapon(weapon)
                x = x + 1
            elif weapon is None and weapon_1 is not None:
                player.discard_stored_weapon(weapon_1)
                player.store_weapon(weapon_1)
                x = x + 1
            elif weapon is not None and weapon_1 is not None:
                player.discard_stored_weapon(weapon)
                player.store_weapon(weapon)
                x = x + 1
            message = "I can't put your weapon into storage! There is already a weapon with the same name stored!"
            language = player.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(ctx.channel, "%s" % (message))

    if current_weapon.w_id != weapons.NO_WEAPON_ID and x == 0:
        player.discard_stored_weapon(weapon)
        player.store_weapon(player.weapon)
        x = 2

    message = "equipped!"
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    if weapon is not None:
        if x == 0:
            try:
                player.discard_stored_weapon(weapon)
                player.store_weapon(player.weapon)
                x = 2
            except:
                try:
                    player.discard_stored_weapon(weapon)
                    player.store_weapon(player.weapon)
                    x = 2
                except:
                    pass
        player.weapon = weapon
        await util.say(ctx.channel, ":white_check_mark: **" + weapon.name_clean + "** %s" % (message))
    elif weapon_1 is not None and weapon is None:
        if x == 0:
            try:
                player.discard_stored_weapon(weapon)
                player.store_weapon(player.weapon)
                x = 2
            except:
                try:
                    player.discard_stored_weapon(weapon)
                    player.store_weapon(player.weapon)
                    x = 2
                except:
                    pass
        player.weapon = weapon_1
        weapon_1.price = weapon_1._price()
        await util.say(ctx.channel, ":white_check_mark: **" + weapon_1.name_clean + "** %s" % (message))
    else:
        raise util.DueUtilException(ctx.channel, "Something went wrong, please file a ``!bugreport``.")
    player.save()


@misc.paginator
def weapons_page(weapons_embed, weapon, **extras):
    price_divisor = extras.get('price_divisor', 1)
    weapons_embed.add_field(name=str(weapon),
                            value='``' + util.format_number(weapon.price // price_divisor, full_precision=True,
                                                            money=True) + '``')


@commands.command(args_pattern='PP?', aliases=["bt"])
@commands.imagecommand()
async def battle(ctx, *args, **details):
    """
    [CMD_KEY]battle player (optional other player)
    
    Battle someone!
    
    Note! You don't gain any exp or reward from these battles!
    Please do not spam anyone with unwanted battles.
    [PERM]
    """
    # TODO: Handle draws
    player = details["author"]
    if len(args) == 2 and args[0] == args[1] or len(args) == 1 and player == args[0]:
        # TODO Check if args are the author or random player
        message = "You can't battle yourself!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if len(args) == 2:
        player_one = args[0]
        player_two = args[1]
    else:
        player_one = player
        player_two = args[0]

    if not hasattr(player, "defense"):
        player.defense = 1
    if not hasattr(player_one, "opt_topdog"):
        player_one.opt_topdog = 0
    if not hasattr(player_one, "topdog_time_elapsed"):
        player_one.topdog_time_elapsed = 0
    if not hasattr(player_one, "topdog_time"):
        player_one.topdog_time = 0
    if not hasattr(player_two, "opt_topdog"):
        player_two.opt_topdog = 0
    if not hasattr(player_two, "topdog_time_elapsed"):
        player_two.topdog_time_elapsed = 0
    if not hasattr(player_two, "topdog_time"):
        player_two.topdog_time = 0
    if not hasattr(player_two, "topdog_attempts"):
        player_two.topdog_attempts = 0
    if not hasattr(player_one, "topdog_attempts"):
        player_one.topdog_attempts = 0

#    message = "You can't battle Kurono!"
#    language = player.language
#    if language != "en":
#        message = util.translate(message, language)

#    if str(player_one.id) == "354900241365073920":
#        raise util.DueUtilException(ctx.channel, "%s" % (message))
#    if str(player_two.id) == "354900241365073920":
#        raise util.DueUtilException(ctx.channel, "%s" % (message))

    a = time.time() - player_two.topdog_time_elapsed
    battle_log = battles.get_battle_log(player_one=player_one, player_two=player_two)

    await imagehelper.battle_screen(ctx.channel, player_one, player_two)
    await util.say(ctx.channel, embed=battle_log.embed)
    if battle_log.winner is None:
        # Both players get the draw battle award
        awards.give_award(ctx.channel, player_one, "InconceivableBattle")
        awards.give_award(ctx.channel, player_two, "InconceivableBattle")
    await battles.give_awards_for_battle(ctx.channel, battle_log)
    if len(args) == 1:
        if player_two.opt_topdog == 1 and player_one.is_top_dog():
            b = util.display_time(a)
            player_two.topdog_time_elapsed = 0
            player_one.topdog_time_elapsed = time.time()
            ctx.author = ctx.server.get_member(player_two.id)
            if ctx.author is None:
                ctx.author = player_two.to_member()
                ctx.author.server = ctx.server
            author2 = players.find_player(ctx.author.id)
            message = "Your TopDog award was stolen. You had the award for " + str(b) + ". <@!" + str(player_one.id) + "> took it."
            language = author2.language
            if language != "en":
                message = util.translate(message, language)
            await util.say(ctx.author, "%s" % (message))



@commands.command(args_pattern=None, aliases=["bttd"])
@commands.imagecommand()
async def battletopdog(ctx, **details):
    """
    [CMD_KEY]battletopdog

    Makes you battle the current topdog.
    [PERM]
    """

    player_one = details["author"]
    player = details["author"]
    if not hasattr(player_one, "opt_topdog"):
        player_one.opt_topdog = 0
    if not hasattr(player_one, "topdog_time_elapsed"):
        player_one.topdog_time_elapsed = 0
    if not hasattr(player_one, "topdog_time"):
        player_one.topdog_time = 0
    if not hasattr(player_one, "topdog_attempts"):
        player_one.topdog_attempts = 0
    top_dog_stats = awards.get_award_stat("TopDog")
    if top_dog_stats is not None and "top_dog" in top_dog_stats:
        top_dog = players.find_player(top_dog_stats["top_dog"])
        if player_one.is_top_dog() is False:
            player_two = top_dog
            ctx.author = ctx.server.get_member(player_two.id)
            if ctx.author is None:
                ctx.author = player_two.to_member()
                ctx.author.server = ctx.server
        else:
            if top_dog.id == player_one.id:
                message = "You are the TopDog!"
                language = player.language
                if language != "en":
                    message = util.translate(message, language)
                raise util.DueUtilException(ctx.channel, "%s" % (message))
            else:
                if player_one.is_top_dog():
                    player_one.awards.remove("TopDog")
                    raise util.DueUtilException(ctx.channel, "Try once more, it should work now!")
                else:
                    pass
    else:
        message = "There is no TopDog!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if not hasattr(player_two, "opt_topdog"):
        player_two.opt_topdog = 0
    if not hasattr(player_two, "topdog_time_elapsed"):
        player_two.topdog_time_elapsed = 0
    if not hasattr(player_two, "topdog_time"):
        player_two.topdog_time = 0
    if not hasattr(player_two, "topdog_attempts"):
        player_two.topdog_attempts = 0

#    message = "You can't battle Kurono!"
#    language = player.language
#    if language != "en":
#        message = util.translate(message, language)

#    if str(player_one.id) == "354900241365073920":
#        raise util.DueUtilException(ctx.channel, "%s" % (message))
#    if str(player_two.id) == "354900241365073920":
#        raise util.DueUtilException(ctx.channel, "%s" % (message))

    battle_log = battles.get_battle_log(player_one=player_one, player_two=player_two)

    await imagehelper.battle_screen(ctx.channel, player_one, player_two)
    await util.say(ctx.channel, embed=battle_log.embed)
    if battle_log.winner is None:
        # Both players get the draw battle award
        awards.give_award(ctx.channel, player_one, "InconceivableBattle")
        awards.give_award(ctx.channel, player_two, "InconceivableBattle")
    await battles.give_awards_for_battle(ctx.channel, battle_log)
    if player_two.opt_topdog == 1 and player_one.is_top_dog():
        a = time.time() - player_two.topdog_time_elapsed
        b = util.display_time(a)
        player_one.topdog_time_elapsed = time.time()
        player_two.topdog_time_elapsed = 0
        author2 = players.find_player(ctx.author.id)
        message = "Your TopDog award was stolen. You had the award for " + str(b) + ". <@!" + str(player_one.id) + "> took it."
        language = author2.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.author, "%s" % (message))


@commands.command(args_pattern='PC', aliases=("wager", "wb"))
async def wagerbattle(ctx, receiver, money, **details):
    """
    [CMD_KEY]wagerbattle player amount
    
    Money will not be taken from your account after you use this command.
    If you cannot afford to pay when the wager is accepted you will be forced
    to sell your weapons.
    [PERM]
    """
    sender = details["author"]
    player = details["author"]
    if sender == receiver:
        message = "You can't send a wager to yourself!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if sender.money - money < 0:
        message = "You can't afford this wager!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if len(receiver.received_wagers) >= gconf.THING_AMOUNT_CAP:
        message = "**" + str(receiver.get_name_possession_clean()) + "** wager inbox is full!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    battles.BattleRequest(sender, receiver, money)

    message = "**" + str(sender.name_clean) + "** wagers **" + str(receiver.name_clean) + "** ``" + str(util.format_number(money, full_precision=True, money=True)) + "`` that they will win in a battle!"
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "%s" % (message))


@commands.command(args_pattern='C?', aliases=["vw"])
async def mywagers(ctx, page=1, **details):
    """
    [CMD_KEY]mywagers (page)
    
    Lists your received wagers.
    [PERM]
    """

    @misc.paginator
    def wager_page(wagers_embed, current_wager, **extras):
        sender = players.find_player(current_wager.sender_id)
        message = str(extras["index"]+1) + ". Request from " + str(sender.name_clean)
        message2 = "<!@" + str(sender.id) + "> ``" + str(util.format_money(current_wager.wager_amount)) + "``"
        language = sender.language
        if language != "en":
            x = util.translate_2(message, message2, language)
            message = x[0]
            message2 = x[1]
        wagers_embed.add_field(name=message, value=message2)

    player = details["author"]

    message = str(player.get_name_possession_clean()) + " Received Wagers"
    message2 = "But wait there's more! Do ``" + str(details["cmd_key"]) + "mywagers " + str(page+1) + "``."
    message3 = "Actions:"
    message4 = "Do ``" + str(details["cmd_key"]) + "acceptwager (number)`` to accept a wager, or ``" + str(details["cmd_key"]) + "`` to decline a wager."
    message5 = "No wagers received!"
    message6 = "Wager requests you get from other players will appear here."
    language = player.language
    if language != "en":
        x = util.translate_6(message, message2, message3, message4, message5, message6, language)
        message = x[0]
        message2 = x[1]
        message3 = x[2]
        message4 = x[3]
        message5 = x[4]
        message6 = x[5]

    wager_list_embed = wager_page(player.received_wagers, page-1,
                                  title=message,
                                  footer_more=message2,
                                  empty_list="")

    if len(player.received_wagers) != 0:
        wager_list_embed.add_field(name=message3,
                                   value=message4,
                                   inline=False)
    else:
        wager_list_embed.add_field(name=message5,
                                   value=message6)

    await util.say(ctx.channel, embed=wager_list_embed)


@commands.command(args_pattern='C', aliases=["aw"])
@commands.imagecommand()
async def acceptwager(ctx, wager_index, **details):
    """
    [CMD_KEY]acceptwager (wager number)
    
    Accepts a wager!
    [PERM]
    """
    # TODO: Handle draws
    player = details["author"]
    wager_index -= 1
    if wager_index >= len(player.received_wagers):
        message = "This wager was not found!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if player.money - player.received_wagers[wager_index].wager_amount < 0:
        message = "You can't afford the risk!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if not hasattr(player, "defense"):
        player.defense = 1

    wager = player.received_wagers.pop(wager_index)
    sender = players.find_player(wager.sender_id)
    battle_log = battles.get_battle_log(player_one=player, player_two=sender)
    battle_embed = battle_log.embed
    winner = battle_log.winner
    loser = battle_log.loser
    wager_amount_str = util.format_number(wager.wager_amount, full_precision=True, money=True)
    total_transferred = wager.wager_amount
    if winner == sender:
        wager_results = "**" + str(player.name_clean) + "** lost to **" + str(sender.name_clean) + "** and paid ``" + wager_amount_str + "``"
        language = player.language
        if language != "en":
            wager_results = util.translate(wager_results, language)
        player.money -= wager.wager_amount
        sender.money += wager.wager_amount
        sender.wagers_won += 1
    elif winner == player:
        player.wagers_won += 1
        if sender.money - wager.wager_amount >= 0:
            payback = "**" + str(sender.name_clean) + "** lost to **" + str(player.name_clean) + "** and paid ``" + wager_amount_str + "``"
            language = player.language
            if language != "en":
                payback = util.translate(payback, language)
            player.money += wager.wager_amount
            sender.money -= wager.wager_amount
        else:
            weapons_sold = 0
            if sender.equipped["weapon"] != weapons.NO_WEAPON_ID:
                weapons_sold += 1
                sender.money += sender.weapon.get_summary().price // (4 / 3)
                sender.weapon = weapons.NO_WEAPON_ID
            if sender.money - wager.wager_amount < 0:
                for weapon in sender.get_owned_weapons():
                    weapon_price = weapon.get_summary().price
                    sender.discard_stored_weapon(weapon)
                    sender.money += weapon_price // (4 / 3)
                    weapons_sold += 1
                    if sender.money - wager.wager_amount >= 0:
                        break
            amount_not_paid = max(0, wager.wager_amount - sender.money)
            amount_paid = wager.wager_amount - amount_not_paid
            amount_paid_str = util.format_number(amount_paid, full_precision=True, money=True)

            if weapons_sold == 0:
                payback = "**" + str(sender.name_clean) + "** could not afford to pay and had no weapon to sell. ``" + amount_paid_str + "`` is all they could pay."
                language = player.language
                if language != "en":
                    payback = util.translate(payback, language)
            else:
                payback = ("**" + sender.name_clean + "** could not afford to pay and had to sell "
                           + str(weapons_sold) + " weapon" + ("s" if weapons_sold != 1 else "") + " \n")
                if amount_paid != wager.wager_amount:
                    payback2 = "They were still only able to pay ``" + amount_paid_str + "``. Pathetic."
                    language = player.language
                    if language != "en":
                        payback += util.translate(payback2, language)
                else:
                    payback2 = "They were able to muster up the full ``" + amount_paid_str + "``."
                    language = player.language
                    if language != "en":
                        payback += util.translate(payback2, language)
            sender.money -= amount_paid
            player.money += amount_paid
            total_transferred = amount_paid
        wager_results = (":sparkles: **"
                         + player.name_clean
                         + "** won against **"
                         + sender.name_clean + "**!\n" + payback)
    else:
        wager_results = "Against all the odds the wager ended in a draw!"
    try:
        stats.increment_stat(stats.Stat.MONEY_TRANSFERRED, total_transferred)
    except:
        pass
    battle_embed.add_field(name="Wager results", value=wager_results, inline=False)
    await imagehelper.battle_screen(ctx.channel, player, sender)
    await util.say(ctx.channel, embed=battle_embed)
    if winner is not None:
        await awards.give_award(ctx.channel, winner, "YouWin", "Win a wager")
        await awards.give_award(ctx.channel, loser, "YouLose", "Lose a wager!")
        if winner.wagers_won == 2500:
            await awards.give_award(ctx.channel, winner, "2500Wagers")
    else:
        await  awards.give_award(ctx.channel, player, "InconceivableWager")
        await  awards.give_award(ctx.channel, sender, "InconceivableWager")
    await battles.give_awards_for_battle(ctx.channel, battle_log)
    sender.save()
    player.save()


@commands.command(args_pattern='C', aliases=["dw"])
async def declinewager(ctx, wager_index, **details):
    """
    [CMD_KEY]declinewager (wager number)
    
    Declines a wager.
    [PERM]
    """

    player = details["author"]
    wager_index -= 1
    if wager_index < len(player.received_wagers):
        wager = player.received_wagers[wager_index]
        del player.received_wagers[wager_index]
        player.save()
        sender = players.find_player(wager.sender_id)
        message = "**" + player.name_clean + "** declined a wager from **" + sender.name_clean + "**"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    else:
        message = "Request not found!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='SSC%B?S?S?S?')
async def createweapon(ctx, name, hit_message, damage, accy, ranged=False, icon='🔫', image_url=None, alias=None, **details):
    """
    [CMD_KEY]createweapon "weapon name" "hit message" damage accy
    
    Creates a weapon for the server shop!
    
    For extra customization you add the following:
    
    (ranged) (icon) (image url) (alias)
    
    __Example__: 
    Basic Weapon:
        ``[CMD_KEY]createweapon "Laser" "FIRES THEIR LAZOR AT" 100 50``
        This creates a weapon named "Laser" with the hit message
        "FIRES THEIR LAZOR AT", 100 damage and 50% accy
    Advanced Weapon:
        ``[CMD_KEY]createweapon "Banana Gun" "splats" 12 10 True :banana: http://i.imgur.com/6etFBta.png Bnana``
        The first four properties work like before. This weapon also has ranged set to ``true``
        as it fires projectiles, a icon (for the shop) ':banana:', an image of the weapon from the url, and an alias of "Bnana".
    [PERM]
    """
    player = details["author"]
    if len(weapons.get_weapons_for_server(ctx.server)) >= gconf.THING_AMOUNT_CAP:
        message = "Sorry, you've used all " + str(gconf.THING_AMOUNT_CAP) + " slots in your shop!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    extras = {"melee": not ranged, "icon": icon}
    if image_url is not None:
        extras["image_url"] = image_url
    if alias is not None:
        extras["alias"] = alias
    if alias is None:
        extras["alias"] = name

    weapon = weapons.Weapon(name, hit_message, damage, accy, **extras, ctx=ctx)
    message = "**" + str(weapon.name_clean) + "** is available in the shop for " + str(util.format_number(weapon.price, money=True)) + "!"
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "%s" % (message))

    if "image_url" in extras:
        await imagehelper.warn_on_invalid_image(ctx.channel, url=extras["image_url"])


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="SS*")
@commands.extras.dict_command(optional={"message/hit/hit_message": "S", "ranged": "B",
                                        "icon": "S", "image": "S", "alias": "S"})
async def editweapon(ctx, weapon_name, updates, **details):
    """
    [CMD_KEY]editweapon name (property value)+

    Any number of properties can be set at once.

    Properties:
        __message__, __icon__, __ranged__, and __image__

    Example usage:

        [CMD_KEY]editweapon laser message "pews at" icon :gun:

        [CMD_KEY]editweapon "a gun" image http://i.imgur.com/QuZQm4D.png
    [PERM]
    """
    player = details["author"]
    weapon = weapons.get_weapon_for_server(ctx.server.id, weapon_name)
    if weapon is None:
        message = "Weapon not found!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if weapon.is_stock():
        message = "You cannot edit stock weapons!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    if not hasattr(weapon, "alias"):
        weapon.alias = weapon_name
    if weapon_name == weapon.alias and weapon_name != weapon.name:
        message = "You need to use the actual name of the weapon you want to edit with, you can't use the alias!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))

    new_image_url = None
    for weapon_property, value in updates.items():
        if weapon_property == "icon":
            if util.is_discord_emoji(ctx.server, value):
                weapon.icon = value
            else:
                message = "The weapon icon must be an emoji! Custom emojis must be on this server."
                language = player.language
                if language != "en":
                    message = util.translate(message, language)
                updates[weapon_property] = message
        elif weapon_property == "ranged":
            weapon.melee = not value
            updates[weapon_property] = str(value).lower()
        elif weapon_property == "alias":
            if weapon.acceptable_string(value, 30):
                weapon.alias = value
                updates[weapon_property] = '"%s"' % updates[weapon_property]
            else:
                message = "Aliases cannot be over 30 characters!"
                language = player.language
                if language != "en":
                    message = util.translate(message, language)
                updates[weapon_property] = message
        else:
            updates[weapon_property] = util.ultra_escape_string(value)
            if weapon_property == "image":
                new_image_url = weapon.image_url = value
            else:
                if weapon.acceptable_string(value, 32):
                    weapon.hit_message = value
                    updates[weapon_property] = '"%s"' % updates[weapon_property]
                else:
                    message = "The image URL cannot be over 32 characters!"
                    language = player.language
                    if language != "en":
                        message = util.translate(message, language)
                    updates[weapon_property] = message

    if len(updates) == 0:
        message = "You need to provide a valid list of changes for the weapon!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(ctx.channel, "%s" % (message))
    else:
        weapon.save()
        result = weapon.icon+" **%s** updates!\n" % weapon.name_clean
        for weapon_property, update_result in updates.items():
            result += "``%s`` → %s\n" % (weapon_property, update_result)
        await util.say(ctx.channel, result)
        if new_image_url is not None:
            await imagehelper.warn_on_invalid_image(ctx.channel, new_image_url)


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='S')
async def removeweapon(ctx, weapon_name, **details):
    """
    [CMD_KEY]removeweapon (weapon name)
    
    Screw all the people that bought it :D
    [PERM]
    """
    player = details["author"]
    weapon_name = weapon_name.lower()
    weapon = weapons.get_weapon_for_server(ctx.server.id, weapon_name)
    if weapon is None or weapon.id == weapons.NO_WEAPON_ID:
        message = "Weapon not found! You have to use the normal weapon name, and not the alias!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    if weapon.id != weapons.NO_WEAPON_ID and weapons.stock_weapon(weapon_name) != weapons.NO_WEAPON_ID:
        message = "You can't remove stock weapons!"
        language = player.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(ctx.channel, "%s" % (message))
    weapons.remove_weapon_from_shop(ctx.server, weapon_name)
    message = "**" + str(weapon.name_clean) + "** has been removed from the shop!"
    language = player.language
    if language != "en":
        message = util.translate(message, language)
    await util.say(ctx.channel, "%s" % (message))

@commands.command(permission=Permission.REAL_SERVER_ADMIN, args_pattern="S?")
@commands.require_cnf(warning="This will **__permanently__** delete all weapons from your shop!")
async def resetweapons(ctx, **_):
    """
    [CMD_KEY]resetweapons

    Screw over everyone on your server!
    This command **deletes all weapons** on your server.
    [PERM]
    """

    weapons_deleted = weapons.remove_all_weapons(ctx.server)
    if weapons_deleted > 0:
        await util.say(ctx.channel, ":wastebasket: Your weapon shop has been reset—**%d %s** deleted."
                                    % (weapons_deleted, util.s_suffix("weapon", weapons_deleted)))
    else:
        await util.say(ctx.channel, "There's no weapons to delete!")


# Part of the shop buy command
async def buy_weapon(weapon_name, **details):
    customer = details["author"]
    weapon = weapons.get_weapon_for_server(details["server_id"], weapon_name)
    channel = details["channel"]
    if weapon is not None:
        if not hasattr(weapon, "alias"):
            weapon.alias = weapon_name

    if not hasattr(customer, "item_limit_x2"):
        customer.item_limit_x2 = 1

    if customer.item_limit_x2 < 1:
        customer.item_limit_x2 = 1
    if not hasattr(customer, "dummy_limit"):
        customer.dummy_limit = 1
    if not hasattr(customer, "slot_increase"):
        customer.slot_increase = 0

    if weapon is None or weapon_name == "none":
        message = "The weapon was not found."
        language = customer.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(channel, "%s" % (message))
    if weapon.price > customer.item_value_limit:
        message = "Awww. I can't sell you that. You can use weapons with a value up to **" + str(util.format_number(customer.item_value_limit, money=True, full_precision=True)) + "**."
        language = customer.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(channel, "%s" % (message))
    elif customer.money - weapon.price < 0:
        message = "You can't afford that weapon."
        language = customer.language
        if language != "en":
            message = util.translate(message, language)
        raise util.DueUtilException(channel, "%s" % (message))
    elif customer.equipped["weapon"] != weapons.NO_WEAPON_ID:
        if len(customer.inventory["weapons"]) < (weapons.MAX_STORED_WEAPONS + customer.slot_increase):
            if weapon.w_id not in customer.inventory["weapons"]:
                customer.store_weapon(weapon)
                customer.money -= weapon.price
                message = "**" + str(customer.name_clean) + "** bought a **" + str(weapon.name_clean) + "** for " + str(util.format_number(weapon.price, money=True, full_precision=True)) + ". You hve not equipped this weapon, equip it with ``" + details["cmd_key"] + "equip " + str(weapon.name_clean.lower()) + "`` to equip this weapon!"
                language = customer.language
                if language != "en":
                    message = util.translate(message, language)
                await util.say(channel, "%s" % (message))
            else:
                message = "I cannot store your new weapon because you already have a weapon with the same name!"
                language = customer.language
                if language != "en":
                    message = util.translate(message, language)
                raise util.DueUtilException(channel,
                                            "%s" % (message))
        else:
            message = "You have no free weapon slots!"
            language = customer.language
            if language != "en":
                message = util.translate(message, language)
            raise util.DueUtilException(channel, "%s" % (message))
    else:
        customer.weapon = weapon
        customer.money -= weapon.price
        message = "**" + str(customer.name_clean) + "** bought a **" + str(weapon.name_clean) + "** for " + str(util.format_number(weapon.price, money=True, full_precision=True)) + "!"
        language = customer.language
        if language != "en":
            message = util.translate(message, language)
        await util.say(channel, "%s" % (message))
        await awards.give_award(channel, customer, "Spender", "Licence to kill!")
    customer.save()


async def sell_weapon(weapon_name, **details):
    player = details["author"]
    channel = details["channel"]

    price_divisor = 4 / 3
    player_weapon = player.weapon
    if player_weapon != weapons.NO_WEAPON and player_weapon.name.lower() == weapon_name:
        weapon_to_sell = player.weapon
        player.weapon = weapons.NO_WEAPON_ID
    else:
        weapon_to_sell = next((weapon for weapon in player.get_owned_weapons() if weapon.name.lower() == weapon_name),
                              None)
        if weapon_to_sell is None:
            raise util.DueUtilException(channel, "Weapon not found. You can't buy/sell weapons with alias names, only their normal names!")
        player.discard_stored_weapon(weapon_to_sell)

    sell_price = weapon_to_sell.price // price_divisor
    player.money += sell_price
    await util.say(channel, ("**" + player.name_clean + "** sold their trusty **" + weapon_to_sell.name_clean
                             + "** for ``" + util.format_number(sell_price, money=True, full_precision=True) + "``"))
    player.save()


def weapon_info(weapon_name=None, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    weapon = details.get('weapon')
    if weapon is not None:
        if not hasattr(weapon, "alias"):
            weapon.alias = weapon_name
    if weapon is None:
        weapon = weapons.get_weapon_for_server(details["server_id"], weapon_name)
        if not hasattr(weapon, "alias"):
            weapon.alias = weapon_name
        if weapon is None:
            raise util.DueUtilException(details["channel"], "Weapon not found")
    embed.title = weapon.icon + ' | ' + weapon.name_clean
    embed.set_thumbnail(url=weapon.image_url)
    embed.add_field(name='Damage', value=util.format_number(weapon.damage))
    embed.add_field(name='Accuracy', value=util.format_number(weapon.accy * 100) + '%')
    embed.add_field(name='Price',
                    value=util.format_number(weapon.price // price_divisor, money=True, full_precision=True))
    embed.add_field(name="Hit Message", value=weapon.hit_message)
    embed.add_field(name="Alias", value=weapon.alias)
    if weapon.melee:
        embed.add_field(name="Hit Type", value="Melee")
    else:
        embed.add_field(name="Hit Type", value="Ranged")
    embed.set_footer(text='Image supplied by weapon creator.')
    return embed

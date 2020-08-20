import discord
import time
import math

import generalconfig as gconf
from ..game import players
from ..permissions import Permission
from ..game import battles, weapons, stats, awards, shields
from ..game.helpers import imagehelper, misc
from .. import commands, util


@commands.command(args_pattern='II', aliases=["spt"])
async def shieldpricetest(ctx, defense, defend_chance, **details):
    """
    [CMD_KEY]shieldpricetest (defense) (defend chance)
    
    Tells you what the price would be for a shield with a certain defense and defend chance.
    [PERM]
    """
    price = int(defense ** 2.5) + 1
    await util.say(ctx.channel, "The shield would have a price of %s DUT." % (str(price)))

@commands.command(args_pattern="S?", aliases=["uqs"])
async def unequipshield(ctx, _=None, **details):
    """
    [CMD_KEY]unequipshield
    
    Unequips your current shield.
    [PERM]
    """

    player = details["author"]
    shield = player.shield2
    if shield.s_id == shields.NO_SHIELD_ID:
        raise util.DueUtilException(ctx.channel, "You don't have anything equipped anyway!")
    if len(player.inventory["shields"]) >= 6:
        raise util.DueUtilException(ctx.channel, "No room in your shield storage!")
    if player.owns_shield(shield.name):
        raise util.DueUtilException(ctx.channel, "You already have a shield with that name stored!")

    player.store_shield(shield)
    player.shield2 = shields.NO_SHIELD_ID
    player.save()
    await util.say(ctx.channel, ":white_check_mark: **" + shield.name_clean + "** unequipped!")


@commands.command(args_pattern='S', aliases=["seq"])
async def shieldequip(ctx, shield_name, **details):
    """
    [CMD_KEY]shieldequip (shield name)
    
    Equips a shield from your shield inventory.
    [PERM]
    """

    player = details["author"]
    current_shield = player.shield2
    shield_name = shield_name.lower()

    shield = player.get_shield(shield_name)
    if shield is None:
        try:
            if shield_name != current_shield.name.lower():
                raise util.DueUtilException(ctx.channel, "You do not have that shield stored!")
        except:
            raise util.DueUtilException(ctx.channel, "You do not have that shield stored!")
        await util.say(ctx.channel, "You already have that shield equipped!")
        return   

    player.discard_stored_shield(shield)
    try:
        try:
            skip = 0
            if not hasattr(current_shield, "name"):
                player.discard_stored_shield(current_shield)
                skip = 1
        except:
            raise util.DueUtilException(ctx.channel, "Something went wrong with your current shield, please make a ``!bugreport`` so the owner knows.")
        if player.owns_shield(current_shield.name):
            player.store_shield(shield)
            raise util.DueUtilException(ctx.channel, ("Can't put your current shield into storage!\n"
                                                      + "There is already a shield with the same name stored!"))
    except:
        player.shield2s = []
        player.inventory["shields"] = []
        player.shield2 = shields.NO_SHIELD
        player.equipped["shield"] = shields.NO_SHIELD
        raise util.DueUtilException(ctx.channel, "Something was bugged with your shields, I had to clear your shields. Contact Theelgirl#4980 in the support server for a refund.")

    try:
        if current_shield.s_id != shields.NO_SHIELD_ID:
            player.store_shield(current_shield)
    except:
        raise util.DueUtilException(ctx.channel, "Something is still bugged with your shields, please send a ``!bugreport``.")

    player.shield2 = shield
    player.save()

    await util.say(ctx.channel, ":white_check_mark: **" + shield.name_clean + "** equipped!")


@misc.paginator
def shields_page(shields_embed, shield, **extras):
    price_divisor = extras.get('price_divisor', 1)
    shields_embed.add_field(name=str(shield),
                            value='``' + util.format_number(shield.price // price_divisor, full_precision=True,
                                                            money=True) + '``')

@commands.command(args_pattern="M?", aliases=["ms"])
async def myshields(ctx, *args, **details):
    """
    [CMD_KEY]myshields (page)/(shield name)
    
    Shows the contents of your shield inventory.
    [PERM]
    """

    player = details["author"]
    if not hasattr(player, "shield"):
        player.shield2 = shields.NO_SHIELD
    player_shields = player.get_owned_shields()
    page = 1
    if len(args) == 1:
        page = args[0]

    if type(page) is int:
        shield_store = shields_page(player_shields, page-1,
                                    title=player.get_name_possession_clean() + " Shields", price_divisor=4/3,
                                    empty_list="")
        if len(player_shields) == 0:
            shield_store.add_field(name="No shields stored!",
                                   value="You can buy up to 6 more shields from the shop and store them here!")
        shield_store.description = "Currently equipped: " + str(player.shield2)
        shield_store.set_footer(text="Do " + details["cmd_key"] + "shieldequip (shield name) to equip a shield.")
        await util.say(ctx.channel, embed=shield_store)
    else:
        shield_name = page
        if player.equipped["shield"] != shields.NO_SHIELD_ID:
            player_shields.append(player.shield2)
        shield = next((shield for shield in player_shields if shield.name.lower() == shield_name.lower()), None)
        if shield is not None:
            embed = discord.Embed(type="rich", color=gconf.DUE_COLOUR)
            info = shield_info(**details, shield=shield, price_divisor=3, embed=embed)
            await util.say(ctx.channel, embed=info)
        else:
            raise util.DueUtilException(ctx.channel, "You don't have a shield with that name!")
#    await util.say(ctx.channel, "Due to the ongoing bugs with shields, all shields have been reset to try and fix the problems.")

@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='SR%S?S?')
async def createshield(ctx, name, defense, defend_chance, icon='🔫', image_url=None, **details):
    """
    [CMD_KEY]createshield "shield name" defense (defend chance)
    
    Creates a shield for the server shop!
    
    For extra customization you add the following:
    
    (icon) (image url)
    
    __Example__: 
    Basic Shield:
        ``[CMD_KEY]createshield "Steel Shield" 2 50``
        This creates a shield named "Steel Shield" with 2x damage reduction and 50% defend chance
    Advanced Shield:
        ``[CMD_KEY]createshield "Laser Wall" 5 25 :banana: http://i.imgur.com/6etFBta.png``
        The first three properties work like before,
        but it has a icon (for the shop) ':banana:', and an image of the shield from the url.
    [PERM]
    """
    if len(shields.get_shields_for_server(ctx.server)) >= gconf.THING_AMOUNT_CAP:
        raise util.DueUtilException(ctx.channel, "Sorry you've used all %s slots in your shop!"
                                                 % gconf.THING_AMOUNT_CAP)
    if name == "Test" or name == "test" or name == "Placeholder Shield" or name == "placeholder shield" or name == "Wooden Shield" or name == "wooden shield":
        raise util.DueUtilException(ctx.channel, "You can't name your shield that!")
    extras = {"icon": icon}
    if image_url is not None:
        extras["image_url"] = image_url
        
    defense = round(defense, 2)
    
    shield = shields.Shield(name, defense, defend_chance, **extras, ctx=ctx)
    await util.say(ctx.channel, (shield.icon + " **" + shield.name_clean + "** is available in the shop for "
                                 + util.format_number(shield.price, money=True) + "!"))
    if "image_url" in extras:
        await imagehelper.warn_on_invalid_image(ctx.channel, url=extras["image_url"])


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern='S')
async def removeshield(ctx, shield_name, **_):
    """
    [CMD_KEY]removeshield (shield name)
    
    Screw all the people that bought it :D
    [PERM]
    """

    shield_name = shield_name.lower()
    shield = shields.get_shield_for_server(ctx.server.id, shield_name)
    if shield is None or shield.id == shields.NO_SHIELD_ID:
        raise util.DueUtilException(ctx.channel, "Shield not found!")
    if shield.id != shields.NO_SHIELD_ID and shields.stock_shield(shield_name) != shields.NO_SHIELD_ID:
        raise util.DueUtilException(ctx.channel, "You can't remove stock shields!")
    shields.remove_shield_from_shop(ctx.server, shield_name)
    await util.say(ctx.channel, "**" + shield.name_clean + "** has been removed from the shop!")


@commands.command(permission=Permission.SERVER_ADMIN, args_pattern="SS*")
@commands.extras.dict_command(optional={"icon": "S", "image": "S"})
async def editshield(ctx, shield_name, updates, **_):

    """
    [CMD_KEY]editshield name (property value)+

    Any number of properties can be set at once.

    Properties:
        __icon__, and __image__

    Example usage:

        [CMD_KEY]editshield laser icon :gun:

        [CMD_KEY]editshield "a gun" image http://i.imgur.com/QuZQm4D.png icon :bomb:
    [PERM]
    """

    shield = shields.get_shield_for_server(ctx.server.id, shield_name)
    if shield is None:
        raise util.DueUtilException(ctx.channel, "Shield not found!")
    if shield.is_stock():
        raise util.DueUtilException(ctx.channel, "You cannot edit stock shields!")

    new_image_url = None
    for shield_property, value in updates.items():
        if shield_property == "icon":
            if util.is_discord_emoji(ctx.server, value):
                shield.icon = value
            else:
                updates[shield_property] = "Must be an emoji! (custom emojis must be on this server)"
        else:
            updates[shield_property] = util.ultra_escape_string(value)
            if shield_property == "image":
                new_image_url = shield.image_url = value
            else:
                if shield.acceptable_string(value, 32):
                    shield.hit_message = value
                    updates[shield_property] = '"%s"' % updates[shield_property]
                else:
                    updates[shield_property] = "Cannot be over 32 characters!"

    if len(updates) == 0:
        await util.say(ctx.channel, "You need to provide a list of valid changes for the shield!")
    else:
        shield.save()
        result = shield.icon+" **%s** updates!\n" % shield.name_clean
        for shield_property, update_result in updates.items():
            result += "``%s`` → %s\n" % (shield_property, update_result)
        await util.say(ctx.channel, result)
        if new_image_url is not None:
            await imagehelper.warn_on_invalid_image(ctx.channel, new_image_url)


@commands.command(permission=Permission.REAL_SERVER_ADMIN, args_pattern="S?")
@commands.require_cnf(warning="This will **__permanently__** delete all shields from your shop!")
async def resetshields(ctx, **_):
    """
    [CMD_KEY]resetshields

    Screw over everyone on your server!
    This command **deletes all shields** on your server.
    [PERM]
    """

    shields_deleted = shields.remove_all_shields(ctx.server)
    if shields_deleted > 0:
        await util.say(ctx.channel, ":wastebasket: Your shield shop has been reset—**%d %s** deleted."
                                    % (shields_deleted, util.s_suffix("shield", shields_deleted)))
    else:
        await util.say(ctx.channel, "There's no shields to delete!")

# Part of the shop buy command
async def buy_shield(shield_name, **details):
    customer = details["author"]
    shield = shields.get_shield_for_server(details["server_id"], shield_name)
    channel = details["channel"]


    if not hasattr(customer, "item_limit_x2"):
        customer.item_limit_x2 = 1
    if not hasattr(customer, "slot_increase"):
        customer.slot_increase = 0
    if customer.item_limit_x2 < 1:
        customer.item_limit_x2 = 1

    if shield is None or shield_name == "none":
        raise util.DueUtilException(channel, "Shield not found!")
    if shield.price > customer.item_value_limit:
        raise util.DueUtilException(channel, (":baby: Awwww. I can't sell you that.\n"
                                              + "You can use shields with a value up to **"
                                              + util.format_number(customer.item_value_limit, money=True,
                                                                   full_precision=True) + "**"))
    elif customer.money - shield.price < 0:
        await util.say(channel, ":anger: You can't afford that shield.")
    elif customer.equipped["shield"] != shields.NO_SHIELD_ID or customer.equipped["shield"] == shields.NO_SHIELD_ID:
        if len(customer.inventory["shields"]) < (shields.MAX_STORED_SHIELDS + customer.slot_increase):
            if shield.s_id not in customer.inventory["shields"]:
                customer.store_shield(shield)
                customer.money -= shield.price
                await util.say(channel, ("**" + customer.name_clean + "** bought a **" + shield.name_clean + "** for "
                                         + util.format_number(shield.price, money=True, full_precision=True)
                                         + "\n:warning: You have not equipped this shield! Do **"
                                         + details["cmd_key"] + "shieldequip "
                                         + shield.name_clean.lower() + "** to equip this shield."))
            else:
                raise util.DueUtilException(channel,
                                            "Cannot store new shield as you already have a shield with the same name!")
        else:
            raise util.DueUtilException(channel, "No free shield slots!")
    else:
        customer.shield = shield
        customer.money -= shield.price
        await util.say(channel, ("**" + customer.name_clean + "** bought a **"
                                 + shield.name_clean + "** for " + util.format_number(shield.price, money=True,
                                                                                      full_precision=True)))
    customer.save()

async def sell_shield(shield_name, **details):
    player = details["author"]
    channel = details["channel"]

    price_divisor = 3
    player_shield = player.shield2
    shield = player_shield
    if player_shield != shields.NO_SHIELD and player_shield.name.lower() == shield_name:
        shield_to_sell = player.shield2
        player.shield2 = shields.NO_SHIELD
    else:
        shield_to_sell = next((shield for shield in player.get_owned_shields() if shield.name.lower() == shield_name),
                              None)
        if shield_to_sell is None:
            raise util.DueUtilException(channel, "Shield not found!")
        player.discard_stored_shield(shield_to_sell)

    sell_price = shield_to_sell.price // (4 / 3)
#    sell_price = shield_to_sell.price
    if shield_name == "None" or shield_name == "Broken Shield" or shield_name == "Other Broken Shield":
        sell_price = 0
    player.money += int(sell_price)
    await util.say(channel, ("**" + player.name_clean + "** sold their trusty **" + shield_to_sell.name_clean
                             + "** for ``" + util.format_number(int(sell_price), money=True, full_precision=True) + "``"))
    player.save()

def shield_info(shield_name=None, **details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor', 1)
    shield = details.get('shield')
    if shield is None:
        shield = shields.get_shield_for_server(details["server_id"], shield_name)
        if shield is None:
            raise util.DueUtilException(details["channel"], "Shield not found!")
    embed.title = shield.icon + ' | ' + shield.name_clean
    embed.set_thumbnail(url=shield.image_url)
    embed.add_field(name='Defense', value=util.format_number(shield.defense))
    embed.add_field(name='Defend Chance', value=util.format_number(shield.defend_chance * 100) + '%')
    embed.add_field(name='Price',
                    value=util.format_number(int(shield.price), money=True, full_precision=True))
    embed.set_footer(text='Image supplied by shield creator.')
    return embed

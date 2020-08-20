import json
from collections import namedtuple
from typing import Union, Dict

import discord
import jsonpickle

from ..util import SlotPickleMixin
from .. import dbconn
from .. import util
from ..game.helpers.misc import DueUtilObject, DueMap
from . import weapons
from . import emojis


stock_shields = ["none"]
shields = DueMap()

MAX_STORED_SHIELDS = 6

# Simple namedtuple for shield sums
Summary = namedtuple("Summary", ["price", "defense", "defend_chance"])


class Shield(DueUtilObject, SlotPickleMixin):
    """A simple shield that can be used by a monster or player in DueUtil"""

    PRICE_CONSTANT = 2.5
    DEFAULT_IMAGE = "http://i.imgur.com/QFyiU6O.png"

    __slots__ = ["name", "defense", "defend_chance", "price",
                 "_icon", "image_url",
                 "shield_sum", "server_id"]

    def __init__(self, name, defense, defend_chance, **extras):
        message = extras.get('ctx', None)

        if message is not None:
            if does_shield_exist(message.server.id, name):
                raise util.DueUtilException(message.channel, "A shield with that name already exists on this server!")

            if not Shield.acceptable_string(name, 30):
                raise util.DueUtilException(message.channel, "Shield names must be between 1 and 30 characters!")

            if defense == 0 or defend_chance == 0:
                raise util.DueUtilException(message.channel, "No shield stats can be zero!")

            if defend_chance < 1 or defend_chance > 86:
                raise util.DueUtilException(message.channel, "Defend chance must be between 1% and 86%!")

            if defense < 1:
                raise util.DueUtilException(message.channel, "Defense must be above 1!")

            icon = extras.get('icon', emojis.DAGGER)
            if not (util.char_is_emoji(icon) or util.is_server_emoji(message.server, icon)):
                raise util.DueUtilException(message.channel, (":eyes: Shield icons must be emojis! :ok_hand:**"
                                                              + "(custom emojis must be on this server)**​"))

            self.server_id = message.server.id

        else:
            self.server_id = "STOCK"

        self.name = name
        self.defense = defense
        self.defend_chance = defend_chance / 100
        self.price = self._price()

        super().__init__(self._shield_id(), **extras)

        self._icon = extras.get('icon', emojis.DAGGER)
        self.image_url = extras.get('image_url', Shield.DEFAULT_IMAGE)

        self.shield_sum = self._shield_sum()
        self._add()

    @property
    def s_id(self):
        return self.id

    def _shield_id(self):
        return "%s+%s/%s" % (self.server_id, self._shield_sum(), self.name.lower())

    def _shield_sum(self):
        return "%d|%d|%.2f" % (self.price, self.defense, self.defend_chance)

    def _price(self):
        return int(self.defense ** self.PRICE_CONSTANT) + 1

    def _add(self):
        shields[self.s_id] = self
        self.save()

    def get_summary(self) -> Summary:
        return get_shield_summary_from_id(self.id)

    def is_stock(self):
        return self.server_id == "STOCK"

    @property
    def icon(self):
        # Handles custom emojis for shields being removed.
        # Not the best place for it but it has to go somewhere.
        if self.server_id != "STOCK" and not util.char_is_emoji(self._icon):
            server = util.get_server(self.server_id)
            if not util.is_server_emoji(server, self._icon):
                self.icon = emojis.MISSING_ICON
                self.save()
        return self._icon

    @icon.setter
    def icon(self, icon):
        self._icon = icon

    def __setstate__(self, object_state):
        updated = False
        if "icon" in object_state:
            # Update shields icon -> _icon
            object_state["_icon"] = object_state["icon"]
            del object_state["icon"]
            updated = True

        SlotPickleMixin.__setstate__(self, object_state)

        if not hasattr(self, "server_id"):
            # Fix an old bug. Shields missing server_id.
            # Get the proper server_id from the first part of the id.
            self.server_id = self.id.split('+')[0]
            updated = True

        if updated:
            self.save()

# The 'None'/No weapon weapon
NO_SHIELD = Shield("Placeholder Shield", 1, 86, no_save=True, image_url="http://i.imgur.com/gNn7DyW.png", icon="👊")
# NO_SHIELD_2 = Shield("Other Broken Shield", 1, 86, no_save=False, image_url="http://i.imgur.com/gNn7DyW.png", icon="👊")
NO_SHIELD_ID = NO_SHIELD.id

def get_shield_from_id(shield_id: str) -> Shield:
    if shield_id in shields:
        shield = shields[shield_id]
        # Getting from the store WILL not ensure an exact match.
        # It will only use the name and server id.
        # We must compare here to ensure the meta data is the same.
        if shield.id == shield_id:
            return shield
    return shields[NO_SHIELD_ID]


def does_shield_exist(server_id: str, shield_name: str) -> bool:
    return get_shield_for_server(server_id, shield_name) is not None

def get_shield_for_server(server_id: str, shield_name: str) -> Shield:
    if shield_name.lower() in stock_shields:
        return shields["STOCK/" + shield_name.lower()]
    shield_id = server_id + "/" + shield_name.lower()
    if shield_id in shields:
        return shields[shield_id]


def get_shield_summary_from_id(shield_id: str) -> Summary:
    summary = shield_id.split('/', 1)[0].split('+')[1].split('|')
    return Summary(price=int(summary[0]),
                   defense=int(summary[1]),
                   defend_chance=float(summary[2]))


def remove_shield_from_shop(server: discord.Server, shield_name: str) -> bool:
    shield = get_shield_for_server(server.id, shield_name)
    if shield is not None:
        del shields[shield.id]
        dbconn.get_collection_for_object(Shield).remove({'_id': shield.id})
        return True
    return False


def get_shields_for_server(server: discord.Server) -> Dict[str, Shield]:
    return dict(shields[server], **shields["STOCK"])


def find_shield(server: discord.Server, shield_name_or_id: str) -> Union[Shield, None]:
    shield = get_shield_for_server(server.id, shield_name_or_id)
    if shield is None:
        shield_id = shield_name_or_id.lower()
        shield = get_shield_from_id(shield_id)
        if shield.s_id == NO_SHIELD_ID and shield_id != NO_SHIELD_ID:
            return None
    return shield


def stock_shield(shield_name: str) -> str:
    if shield_name in stock_shields:
        return "STOCK/" + shield_name
    return NO_SHIELD_ID


def remove_all_shields(server):
    if server in shields:
        result = dbconn.delete_objects(Shield, '%s\+.*' % server.id)
        del shields[server]
        return result.deleted_count
    return 0


def _load():
    def load_stock_shields():
        with open('dueutil/game/configs/defaultshields.json') as defaults_file:
            defaults = json.load(defaults_file)
            for shield_name, shield_data in defaults.items():
                stock_shields.append(shield_name)
                Shield(shield_data["name"],
                       shield_data["defense"],
                       shield_data["defend_chance"],
                       icon=shield_data["icon"],
                       image_url=shield_data["image"],
                       no_save=True)
    load_stock_shields()

    # Load from db
    for shield in dbconn.get_collection_for_object(Shield).find():
        loaded_shield = jsonpickle.decode(shield['data'])
        shields[loaded_shield.id] = util.load_and_update(NO_SHIELD, loaded_shield)
#    shields[NO_SHIELD_2.id] = util.load_and_update(NO_SHIELD_2, NO_SHIELD_2)
    util.logger.info("Loaded %s shields", len(shields))


_load()

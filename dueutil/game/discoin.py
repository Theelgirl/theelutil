import aiohttp
import generalconfig as gconf
import json
import asyncio

import requests
import time

from . import players, stats
from .stats import Stat
from dueutil import util, tasks

import traceback

# A quick discoin implementation.

DISCOIN = "https://discoin.zws.im"
VERIFY = DISCOIN+"/verify"
HANDLED = "https://discoin.zws.im/transactions/"
# Endpoints
TRANSACTIONS = "/transactions"
headers = {"Authorization": gconf.other_configs["discoinKey"], "Content-Type": "application/json"}
headersDTC = {"Authorization": gconf.other_configs["discoinKeyDTC"], "Content-Type": "application/json"}
headersDUP = {"Authorization": gconf.other_configs["discoinKeyDUP"], "Content-Type": "application/json"}

async def test_http(sender_id, amount, to, currency_from):
    transaction_data = {
        "amount": amount,
        "toId": to,
        "user": sender_id
    }
    r = requests.post('http://requestbin.net/r/wxolhgwx', data=json.dumps(transaction_data))

async def make_transaction(sender_id, amount, to, currency_from):

    transaction_data = {
        "amount": amount,
        "toId": to,
        "user": sender_id
    }

    player = players.find_player(sender_id)

    if currency_from == "DTC":
        try:
            player.team_money -= amount
        except:
            pass
        with aiohttp.Timeout(3):
            async with aiohttp.ClientSession() as session:
                async with session.post(url=(DISCOIN + TRANSACTIONS),
                                        data=json.dumps(transaction_data), headers=headersDTC) as response:
                    return await response.json()
    elif currency_from == "DUP":
        try:
            player.prestige_coins -= amount
        except:
            pass
        with aiohttp.Timeout(3):
            async with aiohttp.ClientSession() as session:
                async with session.post(url=(DISCOIN + TRANSACTIONS),
                                        data=json.dumps(transaction_data), headers=headersDUP) as response:
                    return await response.json()
    else:
        try:
            player.money -= amount
        except:
            pass
        with aiohttp.Timeout(3):
            async with aiohttp.ClientSession() as session:
                async with session.post(url=(DISCOIN + TRANSACTIONS),
                                        data=json.dumps(transaction_data), headers=headers) as response:
                    return await response.json()

async def unprocessed_transactions():
    async with aiohttp.ClientSession() as session:
        discoins = []
        async with session.get("https://discoin.zws.im/transactions?s={%22to.id%22%3A%20%22DUT%22%2C%20%22handled%22%3A%20false}", headers=headers) as response:
             x = await response.json()
             discoins.append(x)
        async with session.get("https://discoin.zws.im/transactions?s={%22to.id%22%3A%20%22DTC%22%2C%20%22handled%22%3A%20false}", headers=headersDTC) as response:
             x = await response.json()
             discoins.append(x)
        async with session.get("https://discoin.zws.im/transactions?s={%22to.id%22%3A%20%22DUP%22%2C%20%22handled%22%3A%20false}", headers=headersDUP) as response:
             x = await response.json()
             discoins.append(x)
        return discoins


@tasks.task(timeout=120)
async def process_transactions():
    util.logger.info("Processing Discoin transactions.")
    try:
        unprocessed = await unprocessed_transactions()
    except Exception as exception:
        util.logger.error("Failed to fetch Discoin transactions: %s", exception)
        return
    try:
        if unprocessed is None:
            return
    except:
        try:
            if len(unprocessed) == 0:
                return
        except:
            pass

    client = util.shard_clients[0]

    for currency in unprocessed:
        if currency is None:
            continue
        for transaction in currency:
            if transaction.get('handled'):
                continue
            id = transaction.get('id')
            user_id = transaction.get('user')
            receipt = transaction.get('id')
            source_bot = transaction.get('source')
            amount = transaction.get('amount')
            payout = transaction.get('payout')
            if payout is None:
                continue
            if amount is None:
                continue
            amount = int(float(amount))
            payout = int(float(payout))
            player = players.find_player(user_id)
            if player is None:
                continue

            if not hasattr(player, "discoin_transactions"):
                player.discoin_transactions = 0
            player.discoin_transactions += 1

            from_currency = transaction.get('from').get('id')
            from_currency_2 = from_currency.upper()
            to_currency = transaction.get('to').get('id')
            to_currency_2 = to_currency.upper()

            if player.discoin_transactions >= 8:
                client.run_task(notify_failed, user_id)
                handle = {'handled': True}
                if to_currency_2 == "DUT":
                    async with aiohttp.ClientSession() as session:
                        async with session.patch(url=(HANDLED + id), data=json.dumps(handle), headers=headers) as response:
                            continue
                elif to_currency_2 == "DTC":
                    async with aiohttp.ClientSession() as session:
                        async with session.patch(url=(HANDLED + id), data=json.dumps(handle), headers=headersDTC) as response:
                            continue
                elif to_currency_2 == "DUP":
                    async with aiohttp.ClientSession() as session:
                        async with session.patch(url=(HANDLED + id), data=json.dumps(handle), headers=headersDUP) as response:
                            continue
                else:
                    continue

            if to_currency_2 == "DUT":
                if (player.money + payout) > 100000000 and str(player.id) != "376166105917554701":
                    overage = (player.money + payout) - 100000000
                    client.run_task(notify_complete, user_id, transaction, overage=overage)
                    try:
                        stats.increment_stat(Stat.DISCOIN_RECEIVED, int(100000000 - player.money))
                    except:
                        pass
                    if player.money >= 100000000:
                        x = 1
                    else:
                        player.money = 100000000
                    player.save()
                    client.run_task(make_transaction, user_id, overage, from_currency)            
                else:
                    client.run_task(notify_complete, user_id, transaction)
                    player.money = player.money + payout
                    try:
                        stats.increment_stat(Stat.DISCOIN_RECEIVED, payout)
                    except:
                        pass
                    player.save()
            elif to_currency_2 == "DTC":
                if not hasattr(player, "team_money"):
                    player.team_money = 0
                if (player.team_money + payout) > 10000:
                    overage = (player.team_money + payout) - 10000
                    client.run_task(notify_complete, user_id, transaction, overage=overage)
                    stats.increment_stat(Stat.DISCOIN_RECEIVED, int(10000 - player.team_money))
                    if player.team_money >= 10000:
                        x = 1
                    else:
                        player.team_money = 10000
                    player.save()
                    client.run_task(make_transaction, user_id, overage, from_currency)            
                else:
                    client.run_task(notify_complete, user_id, transaction)
                    player.team_money = player.team_money + payout
                    stats.increment_stat(Stat.DISCOIN_RECEIVED, payout)
                    player.save()
            elif to_currency_2 == "DUP":
                if not hasattr(player, "prestige_coins"):
                    player.prestige_coins = 0
                if (player.prestige_coins + payout) > 2000:
                    overage = (player.prestige_coins + payout) - 2000
                    client.run_task(notify_complete, user_id, transaction, overage=overage)
                    stats.increment_stat(Stat.DISCOIN_RECEIVED, int(2000 - player.prestige_coins))
                    if player.prestige_coins >= 2000:
                        x = 1
                    else:
                        player.prestige_coins = 2000
                    player.save()
                    client.run_task(make_transaction, user_id, overage, from_currency)            
                else:
                    client.run_task(notify_complete, user_id, transaction)
                    player.prestige_coins = player.prestige_coins + payout
                    stats.increment_stat(Stat.DISCOIN_RECEIVED, payout)
                    player.save()
            player.save()
            handle = {'handled': True}
            if to_currency_2 == "DUT":
                async with aiohttp.ClientSession() as session:
                    async with session.patch(url=(HANDLED + id), data=json.dumps(handle), headers=headers) as response:
                        x = 1
            elif to_currency_2 == "DUTC":
                async with aiohttp.ClientSession() as session:
                    async with session.patch(url=(HANDLED + id), data=json.dumps(handle), headers=headersDTC) as response:
                        x = 1
            elif to_currency_2 == "DUP":
                async with aiohttp.ClientSession() as session:
                    async with session.patch(url=(HANDLED + id), data=json.dumps(handle), headers=headersDUP) as response:
                        x = 1
            util.logger.info("Processed discoin transaction")

#        await util.duelogger.info("Discoin transaction with receipt ``%s`` processed.\n" % receipt
#                                  + "User: %s | Amount: %.2f | Source: %s" % (user_id, amount, source_bot))


async def notify_complete(user_id, transaction, overage=0, failed=False, test='abc'):
    client = util.shard_clients[0]
    user = await client.get_user_info(user_id)
    try:
        await client.start_private_message(user)
        if not failed:
            if overage == 0:
                amount = int(transaction["payout"])
                try:
                    await util.say(user, ":white_check_mark: You've received ``%s`` from Discoin!\n" % (util.format_number(amount, full_precision=True, money=True)), client=client)
                except:
                    pass
            else:
                amount = int(overage)
                try:
                    await util.say(user, ":white_check_mark: Your transaction would leave you with over 100 million DUT, 10000 DUTC, or 2000 DUP. Your money has been set to its max with the Discoin sent, and the remainder has been refunded.!\n", client=client)
                except:
                    pass
        else:
            try:
                await util.say(user, ":warning: Your Discoin exchange has been cancelled!\n"
                               + "To exchange to DueUtil you must be a player "
                               + "and the amount has to be worth at least 1 DUT.", client=client)
            except:
                pass
    except Exception as error:
        util.logger.error("Could not notify discoin complete %s", error)
        traceback.print_exc()

async def notify_failed(user_id):
    client = util.shard_clients[0]
    user = await client.get_user_info(user_id)
    try:
        await client.start_private_message(user)
        try:
            await util.say(user, "You have exceeded the limit of recieving 8 transactions per 24 hours.", client=client)
        except:
            pass
    except Exception as error:
        util.logger.error("Could not notify discoin failed %s", error)
        traceback.print_exc()
import asyncio
from datetime import datetime
import json
import ssl
import websockets
from db.facade import DB
from utils.functions import format_percentage_change, format_value, scan_links
from utils.get_data_cg import get_cg
from utils.get_data_go_plus import get_data_go_plus_by_address
from utils.get_data_honeypot import get_data_honeypot_is
from utils.get_token_data import get_token_data_by_address
from bot.main import bot

db = DB()
main_chat_id = -1002187981684


def unique_dicts(dicts_list):
    unique_set = set()
    unique_list = []

    for d in dicts_list:
        # Convert dictionary to a sorted tuple of items
        dict_tuple = tuple(sorted(d.items()))
        if dict_tuple not in unique_set:
            unique_set.add(dict_tuple)
            unique_list.append(d)

    return unique_list


def format_large_number(number):
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}m"
    elif number >= 1_000:
        return f"{number / 1_000:.0f}k"
    else:
        return str(number)


async def send_message_to_user(user_id, msg):
    await bot.send_message(chat_id=user_id, text=msg, disable_web_page_preview=True)


async def send_message_to_group(msg):
    try:
        await bot.send_message(chat_id=main_chat_id, text=msg, disable_web_page_preview=True)
    except Exception as e:
        print(f'{e}')


async def token_matches_default_settings(token_data):
    default_settings = await db.default_settings_crud.read(1)
    default_settings = default_settings.as_dict()

    checks = {
        "market_cap": (default_settings["market_cap_min"] <= token_data.get("market_cap", 0) <= default_settings[
            "market_cap_max"]),
        "volume_5m": (default_settings["volume_5_minute_min"] <= token_data.get("volume_5m", 0)),
        "volume_1h": (default_settings["volume_1_hour_min"] <= token_data.get("volume_1h", 0)),
        "liquidity": (default_settings["liquidity_min"] <= token_data.get("liquidity_usd", 0) <= default_settings[
            "liquidity_max"]),
        "price_change_5m": (default_settings["price_change_5_minute_min"] <= token_data.get("price_change_5m", 0)),
        "price_change_1h": (default_settings["price_change_1_hour_min"] <= token_data.get("price_change_1h", 0)),
        "transaction_count_5m": (default_settings["transaction_count_5_minute_min"] <= token_data.get(
            "transaction_count_5_minute_min", 0)),
        "transaction_count_1h": (
                default_settings["transaction_count_1_hour_min"] <= token_data.get("transaction_count_1_hour_min",
                                                                                   0)),
        "holders": (token_data.get("holders", 0) >= default_settings["holders_min"]),
        "renounced": (token_data.get("renounced") == default_settings["renounced"]),
        "pair_age": ((datetime.now().timestamp() - token_data.get("pair_created_at", 0)) <= default_settings[
            "pair_age_max"])
    }
    # Print all checks and their results
    for key, value in checks.items():
        print(key, value)
    return all(checks.values())


async def form_message(new_data, links):
    risk_level_link = "https://example.com/risk-level"  # Replace with actual link

    link_str = " | ".join([f'<a href="{link.get("url")}">{link.get("type").capitalize()}</a>' for link in links])
    address = new_data.get('contract_address')
    owner_address = new_data.get('owner_address')
    if owner_address != 0:
        owner_str = f'{owner_address[0:4]}...{owner_address[-5:-1]}'
    else:
        owner_str = 'N/A'
    try:
        owner_link = scan_links[f"{new_data.get('chain_name')}"].format(address) if owner_address != 'N/A' else 'N/A'
    except KeyError:
        owner_link = scan_links['ethereum'].format(address) if owner_address != 'N/A' else 'N/A'
    message = f"""
📌 <b>{new_data.get('name', "N/A")}</b> | <b>Risk Level:</b> {new_data.get('risk_level', "N/A")}\n\n

👨‍💻 <b>Deployer: </b><a href='{owner_link}'>{owner_str}</a>
👤 <b>Owner:</b> RENOUNCED: {'Yes' if new_data.get('renounced', False) else 'No'}
🔶 <b>Chain:</b> {new_data.get('chain_name')} | ⚖️️ Age: {int((datetime.now().timestamp() -
                                                   new_data.get('pair_created_at')) / 3600)} hours

💰 <b>MC:</b> ${format_large_number(new_data.get('market_cap'))} | <b>Liq:</b> ${format_large_number(new_data.get('liquidity_usd'))}
🔒 <b>LP Lock: </b> N/A <b>Burned:</b> {new_data.get('percentage', "N/A")}%
💳 <b>Tax:</b> B: {format_percentage_change(new_data.get('tax_buy', 'N/A'))}% | S: {format_percentage_change(new_data.get(
        'tax_sell', 'N/A'))}% | T: {format_percentage_change(new_data.get('tax_transfer', 'N/A'))}%
📈 <b>24h:</b> {format_percentage_change(new_data.get('price_change_24h'))}% | V:  {format_large_number(
        new_data.get('volume_24h'))} | B: {format_large_number(new_data.get('transaction_count_24_hour_min_buys', 'N/A'))} S: {
    format_large_number(new_data.get('transaction_count_24_hour_min_sells', 'N/A'))}

💲 <b>Price:</b> ${format_value(new_data.get('price'))}
💵 <b>Launch MC:</b> N/A
👆 <b>ATH:</b> $7.58M (1552x)
🔗 {link_str}

📊 <b>TS:</b> {format_large_number(new_data.get('transaction_count_24_hour_min_buys', 0) +
                                  new_data.get('transaction_count_24_hour_min_sells', 0))}
👩‍👧‍👦 <b>Holders:</b> {format_large_number(new_data.get('holders', 0))} | <b>Top 10:</b> {new_data.get('top10_percentage')}
💸 <b>Airdrops:</b> CLEAN No Airdrops!

<code>{new_data.get('contract_address')}</code> (click to copy)

    """

    return message


async def on_message(message):
    data = json.loads(message)
    try:
        pairs = data.get('pairs', [])
    except Exception as e:
        print(f'{e}')
        return
    for i in pairs:
        address = i.get('baseToken', {}).get('address', None)
        name = i.get('baseToken', {}).get('name', None)
        symbol = i.get('baseToken', {}).get('symbol', None)
        price_usd = i.get('price', 0)
        liquidity_usd = i.get('liquidity', {}).get('usd', 0)
        chain_name = i.get('chainId', None)
        dex_id = i.get('dexId', None)
        price_change_5m = i.get('priceChange', {}).get('m5', 0)
        price_change_1h = i.get('priceChange', {}).get('h1', 0)
        price_change_24h = i.get('priceChange', {}).get('h24', 0)
        volume_1h = i.get('volume', {}).get('h1', 0)
        volume_5m = i.get('volume', {}).get('m5', 0)
        volume_24h = i.get('volume', {}).get('h24', 0)
        pair_created_at = i.get('pairCreatedAt', 0) / 1000
        market_cap = i.get('marketCap', 0)
        transaction_count_5_minute_min_buys = i.get('txns', {}).get('m5', {}).get('buys', 0)
        transaction_count_5_minute_min_sells = i.get('txns', {}).get('m5', {}).get('sells', 0)
        transaction_count_1_hour_min_buys = i.get('txns', {}).get('h1', {}).get('buys', 0)
        transaction_count_1_hour_min_sells = i.get('txns', {}).get('h1', {}).get('sells', 0)
        transaction_count_24_hour_min_buys = i.get('txns', {}).get('h24', {}).get('buys', 0)
        transaction_count_24_hour_min_sells = i.get('txns', {}).get('h24', {}).get('sells', 0)

        current_time = datetime.now().timestamp()
        # current_time - pair_created_at > 86400 or
        if (current_time - pair_created_at > 86400 or
                await db.tokenPair_crud.check_contract(contract_address=address)):
            print('SKIPPED ___________________________________')
            continue
        token_data = await get_token_data_by_address(chain_name, address)
        if isinstance(token_data, str):
            try:
                token_data = json.loads(token_data)
            except json.JSONDecodeError:
                token_data = {"error": "Failed to decode token data"}

        risk_level_data = await get_data_honeypot_is(address=address)
        go_plus = await get_data_go_plus_by_address(chain=chain_name, address=address)
        extracted_data = {}
        links = []
        if token_data.get('cg') is not None:
            cg_id = token_data['cg']['id']
            cg_data = get_cg(cg_id)
            ath_usd = cg_data['market_data']['ath']['usd']
        else:
            ath_usd = 0

        if token_data.get('ll') is not None:
            tag = token_data['ll']['locks'][0]['tag']
            if tag == 'Burned':
                percentage = sum([i['percentage'] for i in token_data['ll']['locks']])
            else:
                percentage = 0
        else:
            percentage = 0

        for k, v in token_data.items():
            if isinstance(v, dict):
                if 'socials' in v and v['socials'] != []:
                    for link in v['socials']:
                        links.append(link)
                if 'contractRenounced' in v:
                    extracted_data['renounced'] = v['contractRenounced']
                if 'holders' == k and v['count'] != 0:
                    extracted_data['holders'] = v['count']
        links = unique_dicts(links)
        new_data = {
            "contract_address": address,
            "name": name,
            "symbol": symbol,
            "price": price_usd,
            "liquidity_usd": liquidity_usd,
            "chain_name": chain_name,
            "dex_id": dex_id,
            "price_change_5m": price_change_5m,
            "price_change_1h": price_change_1h,
            "price_change_24h": price_change_24h,
            "volume_5m": volume_5m,
            "volume_1h": volume_1h,
            "volume_24h": volume_24h,
            "pair_created_at": pair_created_at,
            "market_cap": market_cap,
            "transaction_count_5_minute_min": transaction_count_5_minute_min_buys + transaction_count_5_minute_min_sells,
            "transaction_count_1_hour_min": transaction_count_1_hour_min_sells + transaction_count_1_hour_min_buys,
            "tax_buy": risk_level_data.get('buy_tax', 0),
            "tax_sell": risk_level_data.get('sell_tax', 0),
            "tax_transfer": risk_level_data.get('transfer_tax', 0),
            'owner_supply': go_plus.get('owner_balance', 0),
            'owner_address': go_plus.get('creator_address', 0),
            'total_supply': go_plus.get('total_supply', 0),
            'top10_percentage': round(sum([float(i['percent']) for i in go_plus.get('holders', [{'percent': 0}])]), 2),
            'risk_level': risk_level_data.get('risk', "N/A"),
            'transaction_count_24_hour_min_buys': transaction_count_24_hour_min_buys,
            'transaction_count_24_hour_min_sells': transaction_count_24_hour_min_sells,
            'ath_usd': ath_usd,
            'liquidity_burned': percentage,
            **extracted_data
        }

        message = await form_message(new_data, links)

        if await token_matches_default_settings(new_data):
            await send_message_to_group(message)
            token = await db.tokenPair_crud.create(**new_data)
            if token is not None:
                for v in links:
                    link_data = {
                        "type": v['type'],
                        "url": v['url'],
                        "token_pair_id": token.id,
                    }
                    await db.tokenLink_crud.create(**link_data)
        matching_users = await db.user_settings_crud.get_matching_users(new_data)
        for user_id in matching_users:
            await send_message_to_user(user_id, message)


async def on_connect():
    uri = "wss://io.dexscreener.com/dex/screener/pairs/h24/1"
    headers = {
        "Host": "io.dexscreener.com",
        "x-client-name": "dex-screener-app",
        "Cookie": "__cf_bm=XD_d..rcFEqIntyzwA6xgB3F3I54tIp1IxPse0Bl2Eo-1713211807-1.0.1.1-8DukO0ZUdbeTXbHxP0dkTYSQ.ttQ7z3dIuG8icHb5x5jgmV6uFQ5eo7I211xx0IwBlKeETnQWw_gvSPAh1OYvtLyDUl6kyUKHZ2C13iECnY",
        "Sec-WebSocket-Key": "dVSX78Ahq4VVu2IU1UUk/g==",
        "Sec-WebSocket-Version": "13",
        "Upgrade": "websocket",
        "Origin": "https://io.dexscreener.com",
        "User-Agent": "DEX Screener/1.8.74.13 Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Connection": "Upgrade"
    }

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, extra_headers=headers, ssl=ssl_context) as websocket:
        print("WebSocket connection opened")
        while True:
            try:
                message = await websocket.recv()
                await on_message(message)
            except websockets.ConnectionClosed:
                print("WebSocket connection closed")
                break
            # except Exception as e:
            #     print(f"Error: {e}")
            #     await asyncio.sleep(5)  # Retry after a delay


async def main():
    while True:
        # try:
        await on_connect()
        # except Exception as e:
        #     print(f"Connection failed: {e}")
        #     await asyncio.sleep(5)  # Retry after a delay


if __name__ == "__main__":
    asyncio.run(main())

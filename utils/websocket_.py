import asyncio
import random
from datetime import datetime
import json
import ssl
import websockets
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from websockets_proxy import proxy_connect
from websockets_proxy import Proxy
from db.facade import DB
from utils.functions import format_percentage_change, format_value, scan_links
from utils.get_data_go_plus import get_data_go_plus_by_address
from utils.get_data_honeypot import get_data_honeypot_is
from utils.get_solana_data import get_solana_data_response
from utils.get_token_data import get_token_data_by_address
from bot.main import bot
from loguru import logger


user_file = 'user_tokens_should_be_sent.txt'
main_file = 'main_tokens_should_be_sent.txt'
db = DB()
main_chat_id = -1002185408863  # PROD
# main_chat_id = -1002187981684


def unique_dicts(dicts_list):
    unique_set = set()
    unique_list = []

    for d in dicts_list:
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


async def send_message_to_user(user_id, msg, kb, token_address):
    try:
        logger.info(f'send_message_to_user: {user_id}')
        await bot.send_message(chat_id=user_id,
                               text=msg,
                               reply_markup=kb,
                               disable_web_page_preview=True)
        record_data = {"user_id": user_id, "token_address": token_address}
        await db.user_token_notifications.create(**record_data)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        with open(user_file, 'a') as f:
            f.write(f"{timestamp} | Should be sent to {user_id}: {token_address}\n")
    except Exception as e:
        logger.error(f'{e}')


async def send_message_to_group(msg, kb):
    try:
        logger.info(f'send_message_to_group:')
        await bot.send_message(chat_id=main_chat_id,
                               text=msg,
                               reply_markup=kb,
                               disable_web_page_preview=True)
    except Exception as e:
        logger.error(f'{e}')


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
        "transaction_count_5m": (default_settings["transaction_count_5_minute_min"] <= token_data.get(
            "transaction_count_5_minute_min", 0)),
        "transaction_count_1h": (
                default_settings["transaction_count_1_hour_min"] <= token_data.get("transaction_count_1_hour_min",
                                                                                   0)),
        "renounced": (token_data.get("renounced", False) == default_settings["renounced"]),
        "pair_age": ((datetime.now().timestamp() - token_data.get("pair_created_at", 0)) <= default_settings[
            "pair_age_max"])
    }
    # for k, v in checks.items():
    #     logger.info(f'{k}: {v}')
    return all(checks.values())


async def second_check(token_data):
    default_settings = await db.default_settings_crud.read(1)
    default_settings = default_settings.as_dict()
    checks = {
        'holders': (default_settings.get('holders_min', 1) <= token_data.get('holders', 1)),
        'lp_burned': (default_settings.get('lp_burned', False) <= token_data.get('lp_burned', False)),
        'lp_locked': (default_settings.get('lp_locked', False) <= token_data.get('lp_locked', False))
    }
    return all(checks.values())


async def form_message(new_data, links):
    risk_level_link = "https://example.com/risk-level"  # Replace with actual link

    link_str = " | ".join([f'<a href="{link.get("url")}">' + \
                            f'{link.get("type").capitalize()}</a>' for link in links])
    address = new_data.get('contract_address')
    owner_address = new_data.get('owner_address')
    if owner_address != 0:
        owner_str = f'{owner_address[0:4]}...{owner_address[-5:-1]}'
    else:
        owner_str = 'N/A'
    try:
        owner_link = scan_links[f"{new_data.get('chain_name')}"].format(owner_address) if owner_address != 'N/A' else 'N/A'
        contract_link = scan_links[f"{new_data.get('chain_name')}"].format(address)
    except KeyError:
        owner_link = scan_links['ethereum'].format(owner_address) if owner_address != 'N/A' else 'N/A'
        contract_link = scan_links['ethereum'].format(address)
    message = f"""
📌 <b><a href="{contract_link}">{new_data.get('name', "N/A")}</a></b> | <b>Risk Level:</b> {new_data.get('risk_level', "N/A")}


👨‍💻 <b>Deployer: </b><a href='{owner_link}'>{owner_str}</a>
👤 <b>RENOUNCED:</b> <b>{"Yes" if new_data.get('renounced', False) else 'No'}</b>
🔶 <b>Chain:</b> {new_data.get('chain_name')} | ⚖️️ Age: {int((datetime.now().timestamp() -
                                                   new_data.get('pair_created_at')) / 3600)} hours

💰 <b>MC:</b> ${format_large_number(new_data.get('market_cap'))} | <b>Liq:</b> ${format_large_number(new_data.get('liquidity_usd'))}
🔒 <b>LP Lock: </b> {new_data.get('liquidity_lock', "N/A")}% | <b>Burned:</b> {new_data.get('liquidity_burned', "N/A")}%
💳 <b>Tax:</b> B: {round(new_data.get('tax_buy', 0), 3)}% | S: {round(new_data.get('tax_sell', 0), 3)}% | T: {
    round(new_data.get('tax_transfer', 0), 3)}%
📈<b>V:</b> {format_large_number(
        new_data.get('volume_24h'))} | <b>B:</b> {format_large_number(new_data.get('transaction_count_24_hour_min_buys',
        'N/A'))}| <b>S:</b> {format_large_number(new_data.get('transaction_count_24_hour_min_sells', 'N/A'))}
📉<b>5m:</b>{format_percentage_change(new_data.get('price_change_5m'))}% | <b>1h: </b>{format_percentage_change
    (new_data.get('price_change_1h'))}% | <b>24h:</b> {format_percentage_change(new_data.get('price_change_24h'))}%      

💲 <b>Price:</b> ${format_value(new_data.get('price'))}
💵 <b>Launch MC:</b> ${format_large_number(new_data.get('launch_market_cap', 'N/A'))}
🔗 {link_str}

📊 <b>TS:</b> {format_large_number(new_data.get('transaction_count_24_hour_min_buys', 0) +
                                  new_data.get('transaction_count_24_hour_min_sells', 0))}
👩‍👧‍👦 <b>Holders:</b> {format_large_number(new_data.get('holders', 0))} | <b>Top 10:</b> {round(new_data.get('top10_percentage'), 2)}%

<code>{new_data.get('contract_address')}</code> (click to copy)

    """
    if new_data.get('chain_name') == 'ethereum':
        chain_name = 'ether'
    else:
        chain_name = new_data.get('chain_name')
    kb = [
        [
            InlineKeyboardButton(text='BananaBot', url=f'https://t.me/BananaGunSniper_bot?start=snp_falcon_{address}'),
            InlineKeyboardButton(text='MaestroBot', url=f'https://t.me/maestro?start={address}-spaceman_vats')
        ],
        [
            InlineKeyboardButton(text='DexTools', url=f"https://www.dextools.io/app/en/"
                                                      f"{chain_name}/pair-explorer/{address}"),
            InlineKeyboardButton(text='DexScreener', url=f"https://dexscreener.com/{new_data.get('chain_name')}/{address}")
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=kb)

    return message, markup


async def on_message(message):
    data = json.loads(message)
    try:
        pairs = data.get('pairs', [])
    except Exception as e:
        logger.error(f'Error in fetching pairs: {e}')
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
        try:
            start_price = float(price_usd) / (1 + (float(price_change_24h) / 100))
            launch_market_cap = (start_price / float(price_usd)) * float(market_cap)
        except ZeroDivisionError:
            continue
        current_time = datetime.now().timestamp()
        if (current_time - pair_created_at > 86400 or
                await db.tokenPair_crud.check_contract(contract_address=address)):
            # logger.info(f'Skipped ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {name} on {chain_name}')
            continue
        token_data = await get_token_data_by_address(chain_name, address)
        if isinstance(token_data, str):
            try:
                token_data = json.loads(token_data)
            except json.JSONDecodeError:
                token_data = {"error": "Failed to decode token data"}
        if chain_name != 'solana':
            risk_level_data = await get_data_honeypot_is(address=address)
            risk_level_data = {
                "tax_buy": risk_level_data.get('buy_tax', 0),
                "tax_sell": risk_level_data.get('sell_tax', 0),
                "tax_transfer": risk_level_data.get('transfer_tax', 0),
                'risk_level': risk_level_data.get('risk', "N/A"),
            }
        extracted_data = {}
        links = []

        if token_data.get('ll') is not None:
            liquidity_burned = sum([i['percentage'] for i in token_data['ll']['locks'] if i['tag'] == 'Burned'])
        else:
            liquidity_burned = 0

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
            'transaction_count_24_hour_min_buys': transaction_count_24_hour_min_buys,
            'transaction_count_24_hour_min_sells': transaction_count_24_hour_min_sells,
            'ath_usd': 0,
            'liquidity_burned': liquidity_burned,
            'launch_market_cap': launch_market_cap,
            **extracted_data,
        }
        logger.info(f"Got {name}, {address}, {chain_name}")
        if await token_matches_default_settings(new_data):
            if chain_name == 'solana':
                soll = await get_solana_data_response(chain=chain_name, address=address)

            go_plus = await get_data_go_plus_by_address(chain=chain_name, address=address)
            lp_holders = go_plus.get('lp_holders')
            if lp_holders:
                liquidity_lock = int(sum([float(i['percent']) for i in lp_holders if i['is_locked'] == 1]) * 100)
            else:
                liquidity_lock = 0
            if chain_name != 'solana':
                gp = {
                    'owner_supply': go_plus.get('owner_balance', 0),
                    'owner_address': go_plus.get('creator_address', 0),
                    'total_supply': go_plus.get('total_supply', 0),
                    'liquidity_lock': liquidity_lock,
                    'lp_burned': True if liquidity_burned > 90 else False,
                    'lp_locked': True if liquidity_lock > 90 else False,
                    'top10_percentage': round(sum([float(i['percent']) for i in go_plus.get('holders', [{'percent': 0}])]),
                                              2) * 100,
                    **risk_level_data,
                    'holders': int(go_plus.get('holder_count', 0)),
                }
                new_data.update(gp)
            else:
                soll = {
                    'liquidity_lock': liquidity_lock,
                    'owner_supply': 0,
                    'owner_address': soll['quickiAudit']["contract_Creator"],
                    'tax_buy': soll['tokenDynamicDetails']['buy_Tax'],
                    'tax_sell': soll['tokenDynamicDetails']['sell_Tax'],
                    'tax_transfer': soll['tokenDynamicDetails']['transfer_Tax'],
                    'total_supply': soll['tokenDetails']['tokenSupply'],
                    'lp_burned': True if liquidity_burned > 90 else False,
                    'lp_locked': True if liquidity_lock > 90 else False,
                    'top10_percentage': 0
                }
                new_data.update(soll)
            if await second_check(new_data):
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                with open(main_file, 'a') as f:
                    f.write(f"{timestamp} | Should be sent to main chat: {address}\n")

                message, kb = await form_message(new_data, links)
                logger.info('Send message to main chat')
                await send_message_to_group(message, kb)
                token = await db.tokenPair_crud.create(**new_data)
                if token is not None:
                    for v in links:
                        link_data = {
                            "type": v['type'],
                            "url": v['url'],
                            "token_pair_id": token.id,
                        }
                        await db.tokenLink_crud.create(**link_data)
            else:
                logger.warning(f'{name}, didn‘t match second check')
        else:
            logger.warning(f'{name}, didn‘t match default settings')

        already_sent_users = await db.user_token_notifications.get_users_by_token_address(address)
        matching_users = await db.user_settings_crud.get_matching_users(new_data)

        # Filter out users who already received the token
        users_to_notify = [user_id for user_id in matching_users if user_id not in already_sent_users]

        if users_to_notify:

            if chain_name == 'solana':
                soll = await get_solana_data_response(chain=chain_name, address=address)

            go_plus = await get_data_go_plus_by_address(chain=chain_name, address=address)
            lp_holders = go_plus.get('lp_holders')
            if lp_holders:
                liquidity_lock = int(sum([float(i['percent']) for i in lp_holders if i['is_locked'] == 1]) * 100)
            else:
                liquidity_lock = 0
            if chain_name != 'solana':
                gp = {
                    'owner_supply': go_plus.get('owner_balance', 0),
                    'owner_address': go_plus.get('creator_address', 0),
                    'total_supply': go_plus.get('total_supply', 0),
                    'liquidity_lock': liquidity_lock,
                    'lp_burned': True if liquidity_burned > 90 else False,
                    'lp_locked': True if liquidity_lock > 90 else False,
                    'top10_percentage': round(sum([float(i['percent']) for i in go_plus.get('holders', [{'percent': 0}])]),
                                              2) * 100,
                    **risk_level_data,
                    'holders': int(go_plus.get('holder_count', 0)),
                }
                new_data.update(gp)
            else:
                soll_data = {
                    'liquidity_lock': liquidity_lock,
                    'owner_supply': 0,
                    'owner_address': soll['quickiAudit'].get("contract_Creator", ''),
                    'tax_buy': soll['tokenDynamicDetails'].get('buy_Tax', 0) or 0,
                    'tax_sell': soll['tokenDynamicDetails'].get('sell_Tax', 0) or 0,
                    'tax_transfer': soll['tokenDynamicDetails'].get('transfer_Tax', 0) or 0,
                    'total_supply': soll['tokenDetails'].get('tokenSupply', 0) or 0,
                    'lp_burned': True if liquidity_burned > 90 else False,
                    'lp_locked': True if liquidity_lock > 90 else False,
                    'top10_percentage': 0,
                    'renounced': new_data.get('renounced', False)
                }
                # print(soll_data)
                new_data.update(soll_data)
            message, kb = await form_message(new_data, links)
            for user_id in matching_users:
                if await db.user_settings_crud.second_check(new_data, user_id):
                    await send_message_to_user(user_id, message, kb, address)


async def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file]
    return proxies


async def get_random_proxy(proxies):
    return random.choice(proxies)


async def on_connect(uri):
    headers = {
        "Host": "io.dexscreener.com",
        "x-client-name": "dex-screener-app",
        "Sec-WebSocket-Version": "13",
        "Upgrade": "websocket",
        "Origin": "https://io.dexscreener.com",
        "User-Agent": "DEX Screener/1.8.74.13 Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Connection": "Upgrade"
    }

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            proxies = await load_proxies("proxies.txt")
            proxy_url = await get_random_proxy(proxies)
            proxy_auth = f"http://{proxy_url.split(':')[2]}:{proxy_url.split(':')[3]}@{proxy_url.split(':')[0]}:{proxy_url.split(':')[1]}"
            proxy = Proxy.from_url(proxy_auth)

            async with proxy_connect(uri, proxy=proxy, extra_headers=headers, ssl=ssl_context) as websocket:
                logger.info(f"WebSocket connection opened to {uri} via proxy {proxy_url}")
                while True:
                    try:
                        message = await websocket.recv()
                        await on_message(message)
                    except websockets.ConnectionClosed:
                        logger.warning("WebSocket connection closed, reconnecting...")
                        break
        except Exception as e:
            logger.error(f"Connection failed: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)


async def main():
    uri_links = [
        'wss://io.dexscreener.com/dex/screener/pairs/h24/1?filters%5BchainIds%5D%5B0%5D=bsc',
        'wss://io.dexscreener.com/dex/screener/pairs/h24/1?filters%5BchainIds%5D%5B0%5D=ethereum',
        'wss://io.dexscreener.com/dex/screener/pairs/h24/1?filters%5BchainIds%5D%5B0%5D=base',
        # 'wss://io.dexscreener.com/dex/screener/pairs/h24/1?filters%5BchainIds%5D%5B0%5D=solana',
    ]

    tasks = [on_connect(uri) for worker_id, uri in enumerate(uri_links, start=1)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())


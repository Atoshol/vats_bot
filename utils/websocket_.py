import asyncio
from datetime import datetime
import json
import csv
import os
import ssl
from pprint import pprint
import websockets
from db.facade import DB
from utils.get_data_go_plus import get_data_go_plus_by_address
from utils.get_token_data import get_token_data_by_address
from bot.main import bot


db = DB()


async def send_message_to_user(user_id, msg):
    await bot.send_message(chat_id=user_id, text=msg)


async def send_message_to_group(msg):
    pass


def token_matches_default_settings(token_data):
    default_settings = {
        "market_cap_min": 50000,
        "market_cap_max": 500000,
        "volume_5_minute_min": 15000,
        "volume_1_hour_min": 15000,
        "liquidity_min": 20000,
        "liquidity_max": 200000,
        "price_change_5_minute_min": 100,
        "price_change_1_hour_min": 100,
        "transaction_count_5_minute_min": 10,
        "transaction_count_1_hour_min": 10,
        "holders_min": 25,
        "renounced": False,
        "pair_age_max": 86400
    }

    checks = {
        "market_cap": (default_settings["market_cap_min"] <= token_data.get("market_cap", 0) <= default_settings["market_cap_max"]),
        "volume_5m": (default_settings["volume_5_minute_min"] <= token_data.get("volume_5m", 0)),
        "volume_1h": (default_settings["volume_1_hour_min"] <= token_data.get("volume_1h", 0)),
        "liquidity": (default_settings["liquidity_min"] <= token_data.get("liquidity_usd", 0) <= default_settings["liquidity_max"]),
        "price_change_5m": (default_settings["price_change_5_minute_min"] <= token_data.get("price_change_5m", 0)),
        "price_change_1h": (default_settings["price_change_1_hour_min"] <= token_data.get("price_change_1h", 0)),
        "transaction_count_5m": (default_settings["transaction_count_5_minute_min"] <= token_data.get("transaction_count_5_minute_min", 0)),
        "transaction_count_1h": (default_settings["transaction_count_1_hour_min"] <= token_data.get("transaction_count_1_hour_min", 0)),
        "holders": (token_data.get("holders", 0) >= default_settings["holders_min"]),
        "renounced": (token_data.get("renounced") == default_settings["renounced"]),
        "pair_age": ((datetime.now().timestamp() - token_data.get("pair_created_at", 0)) <= default_settings["pair_age_max"])
    }
    pprint(token_data)
    # Print all checks and their results
    for key, value in checks.items():
        print(key, value)
    return all(checks.values())


async def form_message(new_data, links):
    risk_level_link = "https://example.com/risk-level"  # Replace with actual link

    link_str = " | ".join([f'<a href="{link.get("url")}">{link.get("type").capitalize()}</a>' for link in links])

    message = f"""
    <b>Vats Bot</b><br>
    <br>
    - <b>{new_data.get('name')} - ({new_data.get('symbol')})</b><br>
    - Network: {new_data.get('chain_name')}<br>
    - Price: ${new_data.get('price')}<br>
    - 5M Change %: {new_data.get('price_change_5m')}%<br>
    - 1H Change %: {new_data.get('price_change_1h')}%<br>
    - 24Hr Volume: ${new_data.get('volume_24h')}<br>
    - Liquidity: ${new_data.get('liquidity_usd')}<br>
    - Market Cap: ${new_data.get('market_cap')}<br>
    - Risk level: <a href='{risk_level_link}'>Click here</a><br>
    - Tax (S/B): {new_data.get('tax_sell', 'N/A')}/{new_data.get('tax_buy', 'N/A')}<br>
    - Liquidity Lock/Burn: N/A<br>
    - Holders: {new_data.get('holders')}<br>
    - Clog: N/A<br>
    - Owner Supply: N/A<br>
    - Pair Age: {int((datetime.now().timestamp() - new_data.get('pair_created_at')) / 3600)} hours<br>
    - Renounced: {'Yes' if new_data.get('renounced', False) else 'No'}<br><br>
    <b>Maestro buy link</b><br>
    <b>Banana bot buy link</b><br><br>
    <code>{new_data.get('contract_address')}</code><br><br>
    {link_str}<br><br>
    <i>Ad section (using same mechanism as Aladdin)</i><br>
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
        transaction_count_5_minute_min = i.get('txns', {}).get('m5', {}).get('buys', 0) + i.get('txns', {}).get('m5',
                                                                                                                {}).get(
            'sells', 0)
        transaction_count_1_hour_min = i.get('txns', {}).get('h1', {}).get('buys', 0) + i.get('txns', {}).get('h1',
                                                                                                              {}).get(
            'sells', 0)
        print(address, chain_name)
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

        risk_level_data = await get_data_go_plus_by_address(chain=chain_name, address=address)

        extracted_data = {}
        links = []
        for k, v in token_data.items():
            if isinstance(v, dict):
                if 'socials' in v and v['socials'] != []:
                    for link in v['socials']:
                        links.append(link)
                if 'contractRenounced' in v:
                    extracted_data['renounced'] = v['contractRenounced']
                if 'holders' == k and v['count'] != 0:
                    extracted_data['holders'] = v['count']

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
            "transaction_count_5_minute_min": transaction_count_5_minute_min,
            "transaction_count_1_hour_min": transaction_count_1_hour_min,
            "tax_buy": risk_level_data.get('buy_tax', 0),
            "tax_sell": risk_level_data.get('sell_tax', 0),
            'owner_supply': risk_level_data.get('owner_balance', 0),
            # 'risk_level_data': risk_level_data
            **extracted_data
        }

        message = await form_message(new_data, links)

        if token_matches_default_settings(new_data):
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

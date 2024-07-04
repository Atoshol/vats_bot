import random
import httpx


async def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file]
    return proxies


async def get_random_proxy(proxies):
    proxy = random.choice(proxies)
    ip, port, username, password = proxy.split(":")
    return f"http://{username}:{password}@{ip}:{port}"


async def get_token_data_by_address(chain, address):
    proxies = await load_proxies('proxies.txt')
    proxy = await get_random_proxy(proxies)
    async with httpx.AsyncClient(proxies=proxy) as client:
        headers = {
            # 'cookie': "__cf_bm=8cmzohK8wZvDe6.snFW8.1i4hrgMbrFBgZQhJoNoLRs-1716464133-1.0.1.1-9CzOCWTIZvB3RH_2SZDwh.j23gBH5CurOlkPg2Y7SDWpClRuBKGsQVfFnmzbopX5wIZiTF0JWB5074PZnZhuLY4VCHkLaWhQbUDkbsBm4xE; __cflb=0H28vzQ7jjUXq92cxrkZaaXVukQv5gNwbep3mRby6iq",
            'user-agent': "DEX Screener/1.8.89.4 Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        }
        response = await client.get(f"https://io.dexscreener.com/dex/pair-details/v3/{chain}/{address}", headers=headers)
        return response.text

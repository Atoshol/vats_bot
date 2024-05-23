import asyncio
import http.client
from pprint import pprint


async def get_token_data_by_address(chain, address):
    conn = http.client.HTTPSConnection("io.dexscreener.com")

    payload = ""

    headers = {
        'cookie': "__cf_bm=8cmzohK8wZvDe6.snFW8.1i4hrgMbrFBgZQhJoNoLRs-1716464133-1.0.1.1-9CzOCWTIZvB3RH_2SZDwh.j23gBH5CurOlkPg2Y7SDWpClRuBKGsQVfFnmzbopX5wIZiTF0JWB5074PZnZhuLY4VCHkLaWhQbUDkbsBm4xE; __cflb=0H28vzQ7jjUXq92cxrkZaaXVukQv5gNwbep3mRby6iq",
        'user-agent': "DEX Screener/1.8.89.4 Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        }

    conn.request("GET", f"/dex/pair-details/v3/{chain}/{address}", payload, headers)

    res = conn.getresponse()
    data = res.read()

    return data

if __name__ == '__main__':
    data = asyncio.run(get_token_data_by_address('base', '0x772aa2e596f739ed7292fc990196416e84db3c81'))
    pprint(data)

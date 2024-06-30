import asyncio

import requests


url = 'https://api.quickintel.io/v1/getquickiauditfull'


async def get_solana_data_response(chain, address):
    payload = {
        'chain': chain,
        'address': address,
    }
    res = requests.post(url, data=payload)
    print(res.json())


if __name__ == '__main__':
    asyncio.run(get_solana_data_response(chain='solana', address='2u7FBpY3r93aMu2F1e87xMJNwpTP8uL166HVvsbnpump'))




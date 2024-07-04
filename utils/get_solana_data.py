import asyncio
from pprint import pprint

import requests


url = 'https://api.quickintel.io/v1/getquickiauditfull'


async def get_solana_data_response(chain, address):
    payload = {
        'chain': chain,
        'tokenAddress': address,
    }
    headers = {'X-QKNTL-KEY': f'650a4bb5b40a479a8533edbc42274697'}
    res = requests.post(url, json=payload, headers=headers)
    return res.json()


import asyncio
import sys

import requests


url = 'https://api.honeypot.is/v2/IsHoneypot'


async def get_data_honeypot_is(address):
    response = requests.get(url, params={'address': address})
    js = response.json()
    if response.status_code == 200:
        print(js)
        clear_data = {
            "risk": js['summary']['risk'],
            'buy_tax': js['simulationResult']['buyTax'] / 100,
            'sell_tax': js['simulationResult']['sellTax'] / 100,
            'transfer_tax': js['simulationResult']['sellTax'] / 100,
        }

        return clear_data
    else:
        return {}


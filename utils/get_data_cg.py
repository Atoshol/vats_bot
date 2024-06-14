import requests


def get_cg(cg_id):

    res = requests.get(f'https://api.coingecko.com/api/v3/coins/{cg_id}')
    json_data = res.json()
    if 'error' not in json_data.keys():
        return res.json()
    return None

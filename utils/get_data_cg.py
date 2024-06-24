import requests


def get_cg(cg_id):

    res = requests.get(f'https://api.coingecko.com/api/v3/coins/{cg_id}')
    json_data = res.json()
    print(json_data)
    if 'error' not in json_data.keys():
        return res.json()
    return None


print(get_cg('AujTJJ7aMS8LDo3bFzoyXDwT3jBALUbu4VZhzZdTZLmG'))

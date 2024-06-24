import requests


chains = {
    "ethereum": "1",
    "bsc": "56",
    "arbitrum": "42161",
    "polygon": "137",
    "solana": "solana",
    "opBNB": "204",
    "zkSync Era": "324",
    "Linea Mainnet": "59144",
    "base": "8453",
    "mantle": "5000",
    "scroll": "534352",
    "optimism": "10",
    "avalanche": "43114",
    "fantom": "250",
    "cronos": "25",
    "heco": "128",
    "gnosis": "100",
    "tron": "tron",
    "kcc": "321",
    "fon": "201022",
    "ZKFair": "42766",
    "blast": "81457",
    "manta pacific": "169",
    "berachain artio testnet": "80085",
    "merlin": "4200",
    "bitlayer mainnet": "200901",
    "zkLink Nova": "810180"
}

url = "https://api.gopluslabs.io/api/v1/token_security/{chain}?contract_addresses={address}"
headers = {
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }


async def get_data_go_plus_by_address(chain, address):
    try:
        r = requests.get(url.format(chain=chains[chain], address=address))
        if r.json()['result']:
            return r.json()['result'][address.lower()]
        return {}
    except Exception as e:
        return {}

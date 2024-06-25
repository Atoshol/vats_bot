import http.client
import csv
import json
import gzip
import io

address = '0xC298d75509943156f1B43F8ba9F484827a22c2C2,'
chain = 'bsc'
url = f"/shared/pair?address={address}&chain={chain}&sudit=true&locks=true"

headers = {
    'content-type': 'application/json',
    'accept': 'application/json',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoiVTJGc2RHVmtYMSs4dVFFbXhoRldXeU4yL0pWbXJqVCtiOU5kWFprdlQ3aDA4MGswdVFaTFMyOUxaVDRLNVNsLzFmQTBKa1lqbXgrS0pNMlJlRFk4NnU0Sm42Y1pvTFlENmtXNzhRNE0xbHl6WUI3ZlJpRFdpVWNlOVROT1ZvTFJybTFTeTlGWWpBRkxuNW5rSFNET0Qzd1dvQS9XTXlLa1FuOFpneTBiYkQzenVienMzelN2dFlCeHkwQmZJM0xZT2poQlgxbmN5Ym1HQVIwNGlhem9EUT09IiwiaWF0IjoxNzEzMzg1NzUzLCJleHAiOjE3MTMzODYxNTN9.A1HnwzJEpOshnRCShig2I7n0gK6BgSQlrHPr4QamVjY',
    'sec-fetch-site': 'same-origin',
    'accept-language': 'uk-UA,uk;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'sec-fetch-mode': 'cors',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'referer': 'https://www.dextools.io/app/en/solana/pair-explorer/Hd8oipr385kQSxvnqnebdQR5HCoJngcBujvQSTEWcdho',
    'cookie': '_pk_id.1.b299=b61a44f9e96221d8.1719223591; _pk_id.5.b299=a59e02e9f26d551cb.1719223591; _pk_ses.1.b299=1; _pk_ses.5.b299=1; cf_clearance=Dpz8dQ6u4cwNWIp5Jo1Pyy8nZu_LB5kQTW4xNh8uV3Q-1719224092-1.0.1.1-RN1B7j91b7FC5x85Vg0xBd5G; __cf_bm=FCDvaPZqh6V3EKaQZAw.3nbD5afoAEk_gInkaM0-1719223649-1.0.1.1-eR12obeUuswoMzewQVR6CpwVgM9Z36EApsMmp7uMiqFSCg',
    'sec-fetch-dest': 'empty'
}

# Create a connection
conn = http.client.HTTPSConnection("www.dextools.io")

# Make the GET request
conn.request("GET", url, headers=headers)

res = conn.getresponse()
data = res.read()

# Check for content encoding and decompress if necessary
if res.getheader('Content-Encoding') == 'gzip':
    buf = io.BytesIO(data)
    f = gzip.GzipFile(fileobj=buf)
    data = f.read().decode('utf-8')
elif res.getheader('Content-Encoding') == 'br':
    import brotli
    data = brotli.decompress(data).decode('utf-8')
else:
    data = data.decode('utf-8')

data = json.loads(data)

print(data)

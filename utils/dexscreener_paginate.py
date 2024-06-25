import http
import requests
import json
import json
import csv

# Load the JSON data from the file
with open("response_pretty.json", "r") as file:
    data = json.load(file)

# Assuming the data is stored in a list under the 'pairs' key
first_100_pairs = data['pairs'][:1000000000]

# Base URL template for making additional requests
conn = http.client.HTTPSConnection("io.dexscreener.com")

payload = ""

headers = {
# 'cookie': "__cf_bm=8cmzohK8wZvDe6.snFW8.1i4hrgMbrFBgZQhJoNoLRs-1716464133-1.0.1.1-9CzOCWTIZvB3RH_2SZDwh.j23gBH5CurOlkPg2Y7SDWpClRuBKGsQVfFnmzbopX5wIZiTF0JWB5074PZnZhuLY4VCHkLaWhQbUDkbsBm4xE; __cflb=0H28vzQ7jjUXq92cxrkZaaXVukQv5gNwbep3mRby6iq",
'user-agent': "DEX Screener/1.8.89.4 Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
}
all_results = []  # List to store all responses

# # Iterate through the first 100 pairs and make requests based on chainId and pairAddress
# for pair in first_100_pairs:
#     chain_id = pair['chainId']
#     pair_address = pair['pairAddress']
#
#     conn.request("GET", f'/dex/pair-details/v3/{chain_id}/{pair_address}', payload, headers)
#     res = conn.getresponse()
#     data = res.read().decode('utf-8')
#     if res.code == 200:
#
#         print(f"Data retrieved successfully for pair address: {pair_address} on chain {chain_id}")
#         all_results.append(data)  # Append the JSON response to the list
#     else:
#         print(f"Failed to retrieve data for pair address: {pair_address} on chain {chain_id}, Status Code: {res.status_code}")
#         all_results.append({'error': f"Failed to retrieve data for pair address: {pair_address} on chain {chain_id}, Status Code: {res.status_code}"})
#
# # Save the combined results to a JSON file
# with open("all_results.json", "w") as outfile:
#     json.dump(all_results, outfile, indent=4)

with open('all_results.json', 'r') as file:
    content = file.read()

json_strings = content.split('\n')

# Clean and parse each JSON string
json_list = []
for json_str in json_strings:
    if json_str.strip():  # Skip empty lines
        try:
            # Remove leading and trailing double quotes and unescape characters
            clean_json_str = json_str.strip()[1:-1].replace('\\"', '"')
            json_list.append(json.loads(clean_json_str))
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
# Extract the Telegram links
telegram_links = []
for i in json_list:
    for k, v in i.items():
        if isinstance(v, dict):
            if 'socials' in v and v['socials'] != []:
                for link in v['socials']:
                    print(link)
                    if link['type'] == 'telegram':
                        telegram_links.append([link['url']])

# Write the links to a CSV file
with open('dexscreener_links.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Telegram Link'])  # Header
    writer.writerows(telegram_links)

print("CSV file with Telegram links has been created.")

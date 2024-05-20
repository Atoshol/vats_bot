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
base_url = 'https://io.dexscreener.com/dex/pair-details/v2/{}/{}'  # Includes placeholders for chain and pair address

# Headers as specified earlier
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
}

all_results = []  # List to store all responses

# Iterate through the first 100 pairs and make requests based on chainId and pairAddress
for pair in first_100_pairs:
    chain_id = pair['chainId']
    pair_address = pair['pairAddress']
    request_url = base_url.format(chain_id, pair_address)
    response = requests.get(request_url, headers=headers)
    print(request_url)
    if response.status_code == 200:

        print(f"Data retrieved successfully for pair address: {pair_address} on chain {chain_id}")
        all_results.append(response.json())  # Append the JSON response to the list
    else:
        print(f"Failed to retrieve data for pair address: {pair_address} on chain {chain_id}, Status Code: {response.status_code}")
        all_results.append({'error': f"Failed to retrieve data for pair address: {pair_address} on chain {chain_id}, Status Code: {response.status_code}"})

# Save the combined results to a JSON file
with open("all_results.json", "w") as outfile:
    json.dump(all_results, outfile, indent=4)

with open('all_results.json', 'r') as file:
    data = json.load(file)

# Extract the Telegram links
telegram_links = []
for entry in data:
    # Check if 'ti' is not None and 'socials' key exists
    if entry.get('ti') and 'socials' in entry['ti']:
        for social in entry['ti']['socials']:
            if social['type'] == 'telegram':
                telegram_links.append([social['url']])

# Write the links to a CSV file
with open('dexscreener_links.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Telegram Link'])  # Header
    writer.writerows(telegram_links)

print("CSV file with Telegram links has been created.")
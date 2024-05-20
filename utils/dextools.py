import requests
import csv

url = "https://www.dextools.io/shared/analytics/tokens/social-network-updates"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoiVTJGc2RHVmtYMSs4dVFFbXhoRldXeU4yL0pWbXJqVCtiOU5kWFprdlQ3aDA4MGswdVFaTFMyOUxaVDRLNVNsLzFmQTBKa1lqbXgrS0pNMlJlRFk4NnU0Sm42Y1pvTFlENmtXNzhRNE0xbHl6WUI3ZlJpRFdpVWNlOVROT1ZvTFJybTFTeTlGWWpBRkxuNW5rSFNET0Qzd1dvQS9XTXlLa1FuOFpneTBiYkQzenVienMzelN2dFlCeHkwQmZJM0xZT2poQlgxbmN5Ym1HQVIwNGlhem9EUT09IiwiaWF0IjoxNzEzMzg1NzUzLCJleHAiOjE3MTMzODYxNTN9.A1HnwzJEpOshnRCShig2I7n0gK6BgSQlrHPr4QamVjY',
    'Sec-Fetch-Site': 'same-origin',
    'Accept-Language': 'uk-UA,uk;q=0.9',
    'If-None-Match': 'W/"4e8ce-WI7XD54TyJPI3ZaL+6nV5A8CF7A"',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Referer': 'https://www.dextools.io/app/en/socials-recently-updated',
    'Sec-Fetch-Dest': 'empty',
    'Cookie': '_pk_id.1.b299=0ec203bdc95d9a52.1711895227.; _pk_ses.1.b299=1; __cf_bm=1dDxJbLmt_1jNO0qV8.rPE8zVjXUr6mhUsmpHov6bZw-1713385751-1.0.1.1-r3cFDopdLkUvqDZU99fcLNTISKRelkF3I7onqcB7N2UHj5LE4ZIxyNgVWW3ZNi3MMyPnSoeoSvZ5v_YzRGpjmA; cf_clearance=xdx0fkXwouGqst_nPwot4rBELQeYdkqtlyzR71ZZkqo-1713385751-1.0.1.1-2MIa1n80c1DWxJPjLmgFd61UphF5K.wvBzUEXAZ0S3aWnBXqiXhHladGpPtGgleleS2foHcb7K5teyhMspBp6A'
}

# Make the GET request
response = requests.get(url, headers=headers)
data = response.json()


# List to store telegram links
telegram_links = []

# Extracting telegram links from each item
for item in data['data']:
    if 'telegram' in item:
        telegram_links.append([item['telegram']])

# Writing to CSV
with open('dextools_Links.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Telegram Link'])
    writer.writerows(telegram_links)

print("CSV file has been created with all Telegram links.")

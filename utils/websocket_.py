import websocket
import json
import ssl
import time
import csv
import os


# Function to read existing addresses from CSV file
def read_existing_addresses(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        return {row[0] for row in reader}


# Function to append a new address to the CSV file
def append_address_to_csv(filename, address):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([address])


def on_message(ws, message):
    print("Received new message:")
    # Prettify the JSON output
    data = json.loads(message)
    pairs = data['pairs']
    for i in pairs:
        address = i['baseToken']['address']
        if address not in existing_addresses:
            print(f"New data saved: {address}")
            # Save the prettified JSON to a file
            with open("response_pretty.json", "a") as json_file:
                json_file.write(json.dumps(data, indent=4, sort_keys=True) + '\n')
            # Append the new address to CSV and add it to the existing addresses set
            append_address_to_csv(csv_filename, address)
            existing_addresses.add(address)
        else:
            print(f"Duplicate address found: {address}, not saving.")


def on_error(ws, error):
    print("Error occurred")
    ws.close()
    time.sleep(5)
    connect()


def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")
    time.sleep(5)
    connect()


def on_open(ws):
    print("WebSocket connection opened")


def connect():
    websocket.enableTrace(True)

    headers = {
        "Host": "io.dexscreener.com",
        "x-client-name": "dex-screener-app",
        "Cookie": "__cf_bm=XD_d..rcFEqIntyzwA6xgB3F3I54tIp1IxPse0Bl2Eo-1713211807-1.0.1.1-8DukO0ZUdbeTXbHxP0dkTYSQ.ttQ7z3dIuG8icHb5x5jgmV6uFQ5eo7I211xx0IwBlKeETnQWw_gvSPAh1OYvtLyDUl6kyUKHZ2C13iECnY",
        "Sec-WebSocket-Key": "dVSX78Ahq4VVu2IU1UUk/g==",
        "Sec-WebSocket-Version": "13",
        "Upgrade": "websocket",
        "Origin": "https://io.dexscreener.com",
        "User-Agent": "DEX Screener/1.8.74.13 Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Connection": "Upgrade"
    }

    ws_url = "wss://io.dexscreener.com/dex/screener/pairs/h24/3"

    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header=headers)

    # Connect and keep the connection open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # Only for testing, remove sslopt in production


if __name__ == "__main__":
    csv_filename = 'addresses.csv'
    existing_addresses = read_existing_addresses(csv_filename)
    connect()

import websocket
import json
import ssl
import time


def on_message(ws, message):
    print("Received new message:")
    # Prettify the JSON output
    pretty_json = json.dumps(json.loads(message), indent=4, sort_keys=True)
    print(pretty_json)
    # Save the prettified JSON to a file
    with open("response_pretty.json", "a") as json_file:
        json_file.write(pretty_json + '\n')


def on_error(ws, error):
    print("Error occurred:")
    print(error)
    time.sleep(5)
    connect()


def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")
    time.sleep(5)
    connect()


def on_open(ws):
    print("WebSocket connection opened")


def connect():
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

    ws_url = "wss://io.dexscreener.com/dex/screener/pairs/h1/1?rankBy%5Bkey%5D=pairAge&rankBy%5Border%5D=asc"

    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header=headers)

    # Connect and keep the connection open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # Only for testing, remove sslopt in production


if __name__ == "__main__":
    connect()

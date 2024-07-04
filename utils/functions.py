import os
import random
import time
from io import BytesIO
import requests
# from PIL import Image, ImageDraw, ImageFont
from bot.main import db_last_message, db_messages


scan_links = {
    "ethereum": "https://etherscan.io/address/{}",
    "base": "https://basescan.org/address/{}",
    "bsc": "https://bscscan.com/address/{}",
    "polygon": "https://polygonscan.com/address/{}",
    "avalanche": "https://snowtrace.io/address/{}",
    "fantom": "https://ftmscan.com/address/{}",
    "arbitrum": "https://arbiscan.io/address/{}",
    "optimism": "https://optimistic.etherscan.io/address/{}",
    "solana": "https://explorer.solana.com/address/{}",
    "cardano": "https://explorer.cardano.org/en/address/{}",
    "tezos": "https://tzkt.io/{}",
    "cosmos": "https://www.mintscan.io/cosmos/account/{}",
    "polkadot": "https://polkadot.subscan.io/account/{}",
    "near": "https://explorer.near.org/accounts/{}",
    "harmony": "https://explorer.harmony.one/address/{}",
    "terra": "https://finder.terra.money/mainnet/address/{}"
}


def get_price(symbol, period):
    key = f"price_change_{period}_percent"
    response = requests.get(f'https://coincodex.com/api/coincodex/get_coin/{symbol}')
    data = response.json()
    current_price = data['last_price_usd']
    try:
        percentage_change = data[key]
    except KeyError:
        percentage_change = data['price_change_1D_percent']
    # Calculate the future price based on the current price and the percentage change
    try:
        future_price = current_price * (1 + percentage_change / 100)
    except TypeError as e:
        future_price = 'No data available'

    return {
        "current_price": current_price,
        "percentage_change": percentage_change,
        "future_price": round(future_price, 2) if isinstance(future_price, float) else future_price,
        "percentage_change_absolute": abs(percentage_change) if isinstance(future_price, float) else future_price,
        'all_data': data
    }


def get_history(symbol):
    response = requests.get(f'https://coincodex.com/api/coincodex/get_coin_history/{symbol}/2022-01-01/2024-01-05/')
    try:
        data = response.json()[f'{symbol}']
    except KeyError:
        data = response.json()
    return data


def get_fng():
    response = requests.get('https://api.alternative.me/fng/?limit=10')
    if response.ok:
        data = response.json()['data']
        current_timestamp = int(time.time())

        # Initialize variables to keep track of the closest value and its minimum distance to current time
        closest_value = None
        min_distance = float('inf')

        # Iterate through each data entry
        for entry in data:
            timestamp = int(entry["timestamp"])
            distance = abs(current_timestamp - timestamp)

            # Update the closest value if a closer timestamp is found
            if distance < min_distance:
                min_distance = distance
                closest_value = entry["value"]
        value_int = int(closest_value)
        if value_int <= 25:
            emoji = '🔴'  # Red
        elif value_int <= 50:
            emoji = '🟠'  # Orange
        elif value_int <= 75:
            emoji = '🟡'  # Yellow
        else:
            emoji = '🟢'  # Green

        return f"{closest_value} {emoji}"
    return {"error": "Could not retrieve Fear and Greed Index data."}


def get_volatility_indx():
    url = f"https://crypto-volatility-index.p.rapidapi.com/tick/BTC/2021-10-01-10-31-00"

    headers = {
        "X-RapidAPI-Key": "b0fc0b1435msha7ca302c33feeffp13aefbjsn7fef10377493",
        "X-RapidAPI-Host": "crypto-volatility-index.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    closest_value = response.json()['value']
    value_int = int(closest_value)
    if value_int <= 25:
        emoji = '🔴'  # Red
    elif value_int <= 50:
        emoji = '🟠'  # Orange
    elif value_int <= 75:
        emoji = '🟡'  # Yellow
    else:
        emoji = '🟢'  # Green

    return f'{closest_value} {emoji}'


def get_data(symbol, period='1D'):
    all_responses = {
        "price_prediction": get_price(symbol, period),
        "fng_data": get_fng(),
        "volatility_index": get_volatility_indx()
    }
    return all_responses


# def create_image_with_text(text, background_folder='backgrounds/'):
#     # Configure the size of the image and load a random background
#     files = [os.path.join(background_folder, f) for f in os.listdir(background_folder) if
#              f.endswith(('.jpg', '.jpeg', '.png'))]
#     if not files:
#         raise ValueError("No background images found in the specified folder.")
#     background_path = random.choice(files)
#     img = Image.open(background_path)
#
#     draw = ImageDraw.Draw(img)
#     font = ImageFont.truetype(font='arial.ttf', size=175)
#
#     # Format text based on the input number
#     try:
#         number = float(text)
#         text = f"+{number:.2f}%" if number >= 0 else f"{number:.2f}%"
#         color = '#34eb46' if number >= 0 else '#eb3434'
#     except ValueError:
#         raise ValueError("Text must be a number.")
#
#     # Calculate text size and position
#     text_width, text_height = draw.textsize(text, font=font)
#     x = (img.width - text_width) / 2
#     y = (img.height - text_height) / 2
#
#     # Place text in the center with the determined color
#     draw.text((x, y), text, font=font, fill=color)
#
#     # Save the image to a BytesIO object
#     img_bytes = BytesIO()
#     img.save(img_bytes, format='JPEG')
#     img_bytes.seek(0)  # Move the reading cursor to the start of the buffer
#     return img_bytes.getvalue()


def find_closest_time_frame(user_input):
    # Convert user input to hours for more granularity
    input_hours = 0
    if 'H' in user_input:
        input_hours = int(user_input[:-1])
    elif 'D' in user_input:
        input_hours = int(user_input[:-1]) * 24
    elif 'M' in user_input:
        input_hours = int(user_input[:-1]) * 30 * 24
    elif 'Y' in user_input:
        input_hours = int(user_input[:-1]) * 365 * 24

    # Create a dictionary to map the keys to hours
    key_to_hours = {
        '1H': 1, '1D': 24, '7D': 7 * 24, '30D': 30 * 24, '90D': 90 * 24,
        '180D': 180 * 24, '365D': 365 * 24, '3Y': 3 * 365 * 24, '5Y': 5 * 365 * 24
    }

    # Find the key with the minimum difference to the input hours
    closest_key = min(key_to_hours, key=lambda k: abs(key_to_hours[k] - input_hours))

    # Return the corresponding value from the data
    return closest_key


async def escape_markdown_v2(text: str):
    """
    Escapes characters for MarkdownV2 in Telegram.
    """
    escape_chars = '[]()~>#+-=|{}.!'

    return ''.join(['\\' + char if char in escape_chars else char for char in text])


async def get_display_message():
    all_messages = [message.as_dict() for message in await db_messages.get_all_active()]
    all_id_s = [message['id'] for message in all_messages]

    message_to_display_id = None

    if len(all_messages) == 0:
        return None

    elif len(all_messages) == 1:
        message_to_display_id = all_id_s[0]

    else:
        last = await db_last_message.get_all()
        last_shown_message_id = last[0].message_id

        if last_shown_message_id == all_id_s[-1]:
            message_to_display_id = all_id_s[0]

        else:
            for message_id in all_id_s:
                if message_id > last_shown_message_id:
                    message_to_display_id = message_id
                    break

    last_message = {'message_id': message_to_display_id}
    await db_last_message.update(id_=1, **last_message)

    message_to_show = next(filter(lambda message: message['id'] == message_to_display_id, all_messages), None)

    return message_to_show


def format_value(value):
    if value == 0:
        return "0.00"
    value = float(value)
    abs_value_str = f"{abs(value):.50f}".rstrip('0')
    integer_part, decimal_part = abs_value_str.split('.')

    # Find the first non-zero digit in the decimal part and add three digits after it
    significant_digits = ''
    count = 0
    started = False
    for digit in decimal_part:
        significant_digits += digit
        if digit != '0':
            started = True
        if started:
            count += 1
        if count == 4:
            break

    formatted_value = f"{integer_part}.{significant_digits}"
    return formatted_value.rstrip('.')


def format_percentage_change(value):
    if value == 0:
        return "0.00"
    value = float(value)
    abs_value_str = f"{abs(value):.10f}".rstrip('0')
    integer_part, decimal_part = abs_value_str.split('.')

    # Find the first non-zero digit in the decimal part and add three digits after it
    significant_digits = ''
    count = 0
    started = False
    for digit in decimal_part:
        significant_digits += digit
        if digit != '0':
            started = True
        if started:
            count += 1
        if count == 4:
            break

    formatted_value = f"{integer_part}.{significant_digits}"
    return f"+{formatted_value}" if value > 0 else f"-{formatted_value}"

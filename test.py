import asyncio

from db.facade import DB

db = DB()


default_settings = {
        "market_cap_min": 10000,
        "market_cap_max": 4000000,
        "volume_5_minute_min": 10,
        "volume_1_hour_min": 10,
        "liquidity_min": 15000,
        "liquidity_max": 400000,
        "price_change_5_minute_min": 10,
        "price_change_1_hour_min": 10,
        "transaction_count_5_minute_min": 10,
        "transaction_count_1_hour_min": 10,
        "holders_min": 25,
        "renounced": False,
        "pair_age_max": 86400
    }
test = asyncio.run(db.settings_crud.create(id=1))


print(test.holders_min)

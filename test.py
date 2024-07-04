import asyncio

from db.facade import DB

db = DB()

record_data = {"user_id": 835960470, "token_address": '0xb53319e16eBBEF7d85a9C7f1Ced21969dDC47C3d'}

test = asyncio.run(db.user_token_notifications.create(**record_data))
print(test)
from datetime import datetime
from hashlib import md5

from requests import post


def get_current_source_time():
    return datetime.now().strftime('%Y%m%d%H%M%S')

print(get_current_source_time())


secret = "3E8EA3F2-4776-4E1C-9A97-E4C13C5AEF1C"







phone_number = "998908175047"
address = "Russia"
customer = 10
comment = "salom"


query = f"phone={phone_number}&address={address}&source_time={get_current_source_time}&customer={customer}&comment={comment}"

signature = md5((query + secret).encode()).hexdigest()

print(signature)


url = f"https://millennium.tm.taxi:8089/common_api/1.0/create_order?{query}"

req = post(url, headers={
    "Signature": signature,
    "Content-Type": "application/x-www-form-urlencoded",
    "X-User-id": "10"
})


print(req.status_code)
print(req.content)
print(req.text)

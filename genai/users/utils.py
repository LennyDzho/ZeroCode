import hashlib
import hmac
import time
from django.conf import settings

def verify_telegram_auth(data: dict, secret: str):
    hash_to_check = data.pop('hash')
    data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(data.items())])
    secret_key = hashlib.sha256(secret.encode()).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return h == hash_to_check

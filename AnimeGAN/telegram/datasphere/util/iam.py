import os
import time
import jwt
import json
import requests
import dotenv

def generate_jwt() -> str:
    with open('keys/datasphere-key.json', 'r') as f:
        obj = f.read()
        obj = json.loads(obj)
        private_key = obj['private_key']
        key_id = obj['id']
        service_account_id = obj['service_account_id']

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 3600
    }

    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    return encoded_token


def get_iam_token_jwt(encoded_jwt: str) -> str:
    req = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json = {"jwt": encoded_jwt})
    token_obj = json.loads(req.text)
    return token_obj['iamToken']

def get_iam_token() -> str:
    OAUTH_TOKEN = os.environ['YANDEX_OAUTH']
    req = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json={"yandexPassportOauthToken": OAUTH_TOKEN})
    token_obj = json.loads(req.text)
    return token_obj['iamToken']
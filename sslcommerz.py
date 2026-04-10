import requests
from config import STORE_ID, STORE_PASSWORD

def validate_payment(val_id):
    url = "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"

    params = {
        "val_id": val_id,
        "store_id": STORE_ID,
        "store_passwd": STORE_PASSWORD,
        "format": "json"
    }

    res = requests.get(url, params=params)

    if res.status_code != 200:
        return None

    return res.json()
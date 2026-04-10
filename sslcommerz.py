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

    try:
        res = requests.get(url, params=params, timeout=10)

        print("RAW VALIDATION:", res.text)

        try:
            return res.json()
        except:
            return None

    except Exception as e:
        print("VALIDATION ERROR:", e)
        return None
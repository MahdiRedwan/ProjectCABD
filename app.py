from flask import Flask, render_template, request, redirect
import requests
import time

app = Flask(__name__)

# 🔐 YOUR SANDBOX CREDENTIALS (provided by you)
STORE_ID = "healt69d2ddc0e9804"
STORE_PASSWORD = "healt69d2ddc0e9804@ssl"

# 🌍 Replace this after deployment (Render / Railway / VPS)
BASE_URL = "https://your-app.onrender.com"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pay', methods=['POST'])
def pay():
    amount = request.form.get("amount")
    tran_id = f"TXN_{int(time.time())}"

    payload = {
        "store_id": STORE_ID,
        "store_passwd": STORE_PASSWORD,
        "total_amount": amount,
        "currency": "BDT",
        "tran_id": tran_id,

        "success_url": f"{BASE_URL}/success",
        "fail_url": f"{BASE_URL}/fail",
        "cancel_url": f"{BASE_URL}/cancel",

        "cus_name": "Test User",
        "cus_email": "test@mail.com",
        "cus_add1": "Dhaka",
        "cus_phone": "01700000000",

        "product_name": "Demo Product",
        "product_category": "General",
        "product_profile": "general"
    }

    response = requests.post(
        "https://sandbox.sslcommerz.com/gwprocess/v4/api.php",
        data=payload
    )

    data = response.json()

    if "GatewayPageURL" in data:
        return redirect(data["GatewayPageURL"])
    else:
        return data


@app.route('/success', methods=['POST'])
def success():
    return render_template("success.html")


@app.route('/fail', methods=['POST'])
def fail():
    return render_template("fail.html")


@app.route('/cancel', methods=['POST'])
def cancel():
    return render_template("cancel.html")


if __name__ == "__main__":
    app.run(debug=True)
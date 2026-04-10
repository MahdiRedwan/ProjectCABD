from flask import Flask, render_template, request, redirect
import time
import requests

from config import STORE_ID, STORE_PASSWORD, BASE_URL
from db import db
from models import Transaction
from sslcommerz import validate_payment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pay", methods=["POST"])
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
        "cus_phone": "01700000000",
        "product_name": "Demo",
        "product_category": "General",
        "product_profile": "general"
    }

    res = requests.post(
        "https://sandbox.sslcommerz.com/gwprocess/v4/api.php",
        data=payload
    )

    data = res.json()

    if "GatewayPageURL" in data:
        return redirect(data["GatewayPageURL"])

    return data


@app.route("/success", methods=["GET", "POST"])
def success():
    val_id = request.values.get("val_id")
    tran_id = request.values.get("tran_id")

    print("VAL_ID:", val_id)

    payment = validate_payment(val_id) if val_id else None

    if payment:
        status_raw = payment.get("status", "FAILED")
        card_type = payment.get("card_type", "UNKNOWN")
        amount = payment.get("amount", 0)
        bank_tran_id = payment.get("bank_tran_id", "")
    else:
        # fallback (never crash)
        status_raw = "FAILED"
        card_type = "UNKNOWN"
        amount = 0
        bank_tran_id = ""

    # map status
    if status_raw == "VALIDATED":
        status = "SUCCESS"
    elif status_raw == "VALIDATED_RISK":
        status = "SUCCESS WITH RISK"
    else:
        status = "FAILED"

    txn = Transaction(
        tran_id=tran_id,
        amount=amount,
        status=status,
        payment_method=card_type,
        bank_tran_id=bank_tran_id
    )

    db.session.add(txn)
    db.session.commit()

    return render_template("success.html", txn=txn)


@app.route("/fail", methods=["GET", "POST"])
def fail():
    return render_template("fail.html")


@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    return render_template("cancel.html")


@app.route("/dashboard")
def dashboard():
    txns = Transaction.query.all()
    return render_template("dashboard.html", txns=txns)


if __name__ == "__main__":
    app.run(debug=True)
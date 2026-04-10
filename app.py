from flask import Flask, render_template, request, redirect
import time
import requests
import json

from db import db
from models import Transaction
from sslcommerz import validate_payment
from config import STORE_ID, STORE_PASSWORD, BASE_URL

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


# ======================
# PAYMENT INIT
# ======================
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


# ======================
# SUCCESS CALLBACK (FIXED)
# ======================
@app.route("/success", methods=["GET", "POST"])
def success():
    callback = request.values.to_dict()

    val_id = callback.get("val_id")
    tran_id = callback.get("tran_id")

    payment = validate_payment(val_id) if val_id else None

    # ---------- STATUS FIX ----------
    if payment and isinstance(payment, dict):
        raw_status = str(payment.get("status", "")).upper()

        if raw_status == "VALIDATED":
            status = "SUCCESS"

        elif raw_status == "VALIDATED_RISK":
            status = "SUCCESS WITH RISK"

        else:
            status = "FAILED"

        card_type = payment.get("card_type", "UNKNOWN")
        amount = payment.get("amount", 0)
        bank_tran_id = payment.get("bank_tran_id", "")

    else:
        status = "PENDING VERIFICATION"
        card_type = "UNKNOWN"
        amount = 0
        bank_tran_id = ""

    txn = Transaction(
        tran_id=tran_id,
        amount=amount,
        status=status,
        payment_method=card_type,
        bank_tran_id=bank_tran_id,
        raw_callback=json.dumps(callback),
        raw_validation=json.dumps(payment) if payment else None
    )

    db.session.add(txn)
    db.session.commit()

    return render_template("success.html", txn=txn)


# ======================
# FAIL CALLBACK (FIXED)
# ======================
@app.route("/fail", methods=["GET", "POST"])
def fail():
    callback = request.values.to_dict()

    tran_id = callback.get("tran_id", f"FAIL_{int(time.time())}")

    txn = Transaction(
        tran_id=tran_id,
        amount=0,
        status="FAILED",
        payment_method="UNKNOWN",
        raw_callback=json.dumps(callback)
    )

    db.session.add(txn)
    db.session.commit()

    return render_template("fail.html", txn=txn)


# ======================
# CANCEL
# ======================
@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    return render_template("cancel.html")


# ======================
# DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    txns = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template("dashboard.html", txns=txns)


if __name__ == "__main__":
    app.run(debug=True)
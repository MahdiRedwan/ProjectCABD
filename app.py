from flask import Flask, render_template, request, redirect
import time
import json
import requests

from config import STORE_ID, STORE_PASSWORD, BASE_URL, DEMO_MODE
from db import db
from models import Transaction
from sslcommerz import validate_payment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------------------
# HOME
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------
# INIT PAYMENT
# ---------------------------
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

        "product_name": "Demo Product",
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


# ---------------------------
# SUCCESS CALLBACK
# ---------------------------
@app.route("/success", methods=["GET", "POST"])
def success():
    callback_data = request.values.to_dict()

    print("CALLBACK:", callback_data)

    val_id = callback_data.get("val_id")
    tran_id = callback_data.get("tran_id")

    validation_data = None

    # -----------------------
    # REAL VALIDATION STEP
    # -----------------------
    if val_id:
        validation_data = validate_payment(val_id)

    # -----------------------
    # DETERMINE STATUS
    # -----------------------
    if validation_data and validation_data.get("status") == "VALIDATED":
        status = "SUCCESS"

    elif validation_data and validation_data.get("status") == "VALIDATED_RISK":
        status = "SUCCESS WITH RISK"

    else:
        status = "FAILED"

    # -----------------------
    # EXTRACT SAFE DATA
    # -----------------------
    card_type = validation_data.get("card_type", "UNKNOWN") if validation_data else "UNKNOWN"
    bank_tran_id = validation_data.get("bank_tran_id", "") if validation_data else ""
    amount = validation_data.get("amount", 0) if validation_data else 0

    # -----------------------
    # SAVE AUDIT LOG
    # -----------------------
    txn = Transaction(
        tran_id=tran_id,
        amount=amount,
        status=status,
        payment_method=card_type,
        bank_tran_id=bank_tran_id,
        raw_callback=json.dumps(callback_data),
        raw_validation=json.dumps(validation_data) if validation_data else None
    )

    db.session.add(txn)
    db.session.commit()

    return render_template("success.html", txn=txn)


# ---------------------------
# FAIL
# ---------------------------
@app.route("/fail")
def fail():
    return render_template("fail.html")


# ---------------------------
# CANCEL
# ---------------------------
@app.route("/cancel")
def cancel():
    return render_template("cancel.html")


# ---------------------------
# DASHBOARD
# ---------------------------
@app.route("/dashboard")
def dashboard():
    txns = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template("dashboard.html", txns=txns)


if __name__ == "__main__":
    app.run(debug=True)
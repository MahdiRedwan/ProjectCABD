from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import time

app = Flask(__name__)

# ======================
# CONFIG
# ======================
STORE_ID = "healt69d2ddc0e9804"
STORE_PASSWORD = "healt69d2ddc0e9804@ssl"

BASE_URL = "https://projectcabd-production.up.railway.app"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ======================
# DATABASE MODEL
# ======================
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tran_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Float)
    status = db.Column(db.String(20))


with app.app_context():
    db.create_all()

# ======================
# ROUTES
# ======================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pay', methods=['POST'])
def pay():
    amount = request.form.get("amount")
    tran_id = f"TXN_{int(time.time())}"

    # Save INITIATED
    txn = Transaction(tran_id=tran_id, amount=amount, status="INITIATED")
    db.session.add(txn)
    db.session.commit()

    payload = {
        "store_id": STORE_ID,
        "store_passwd": STORE_PASSWORD,
        "total_amount": amount,
        "currency": "BDT",
        "tran_id": tran_id,

        "success_url": f"{BASE_URL}/success?tran_id={tran_id}",
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


@app.route('/success', methods=['GET', 'POST'])
def success():
    tran_id = request.args.get("tran_id")

    txn = Transaction.query.filter_by(tran_id=tran_id).first()
    if txn:
        txn.status = "SUCCESS"
        db.session.commit()

    return render_template("success.html")


@app.route('/fail', methods=['GET', 'POST'])
def fail():
    return render_template("fail.html")


@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    return render_template("cancel.html")


@app.route('/admin')
def admin():
    transactions = Transaction.query.all()
    return render_template("admin.html", transactions=transactions)


if __name__ == "__main__":
    app.run(debug=True)
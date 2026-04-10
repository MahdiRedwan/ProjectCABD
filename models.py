from db import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tran_id = db.Column(db.String(100))
    amount = db.Column(db.Float)

    status = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))

    bank_tran_id = db.Column(db.String(100))

    # 🔥 audit fields (VERY IMPORTANT)
    raw_callback = db.Column(db.Text)
    raw_validation = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
from db import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tran_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Float)

    status = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))

    bank_tran_id = db.Column(db.String(100))
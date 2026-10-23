from app.extensions import db
from datetime import datetime

class FeeCategory(db.Model):
    __tablename__ = 'fee_categories'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    default_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
class FeeInvoice(db.Model):
    __tablename__ = 'fee_invoices'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('fee_categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), default=0.00)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Unpaid') # Unpaid, Partial, Paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('invoices', lazy=True))
    category = db.relationship('FeeCategory')

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('fee_invoices.id'), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    reference_number = db.Column(db.String(100))
    # Razorpay Transaction Fields
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    razorpay_signature = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoice = db.relationship('FeeInvoice', backref=db.backref('payments', lazy=True))
from app.extensions import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(50))
    category = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=1)
    available_qty = db.Column(db.Integer, default=1)
    rack_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BookIssue(db.Model):
    __tablename__ = 'book_issues'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    fine_amount = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.String(20), default='Issued') # Issued, Returned, Overdue

    book = db.relationship('Book', backref=db.backref('issues', lazy=True))
    student = db.relationship('Student', backref=db.backref('book_issues', lazy=True))
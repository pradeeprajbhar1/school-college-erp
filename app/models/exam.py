from app.extensions import db
from datetime import datetime

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False) # e.g., Mid-Term 2026, Final Exam
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExamMark(db.Model):
    __tablename__ = 'exam_marks'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False) # e.g., Mathematics, Science
    max_marks = db.Column(db.Float, default=100.0)
    marks_obtained = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exam = db.relationship('Exam', backref=db.backref('marks', lazy=True))
    student = db.relationship('Student', backref=db.backref('exam_marks', lazy=True))
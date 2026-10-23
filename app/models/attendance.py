from app.extensions import db
from datetime import datetime

class StudentAttendance(db.Model):
    __tablename__ = 'student_attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False) # Present, Absent, Late
    remarks = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship jisse hum attendance record se student ki details nikal sakein
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))
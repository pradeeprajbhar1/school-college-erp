from app.extensions import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False) # e.g., Science, Commerce, IT

    employees = db.relationship('Employee', backref='department', lazy=True)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Optional link to User login
    employee_code = db.Column(db.String(50), unique=True, nullable=False) # e.g., EMP-101
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    contact_number = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    designation = db.Column(db.String(100), nullable=False) # e.g., Assistant Professor, Senior Teacher
    qualification = db.Column(db.String(150))
    joining_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TimetableSlot(db.Model):
    __tablename__ = 'timetable_slots'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    subject_name = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False) # Monday, Tuesday...
    start_time = db.Column(db.String(10), nullable=False) # e.g., 09:00 AM
    end_time = db.Column(db.String(10), nullable=False)   # e.g., 09:45 AM
    room_number = db.Column(db.String(50))

    course_class = db.relationship('CourseClass', backref=db.backref('timetable_slots', lazy=True))
    teacher = db.relationship('Employee', backref=db.backref('timetable_slots', lazy=True))
from app.extensions import db
from datetime import datetime

class CourseClass(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    sections = db.relationship('Section', backref='course_class', lazy=True)
    students = db.relationship('Student', backref='course_class', lazy=True)

class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    students = db.relationship('Student', backref='section', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Student Login ID
    guardian_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Parent Login ID
    admission_number = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
    guardian_name = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # User Relationships
    student_user = db.relationship('User', foreign_keys=[user_id], backref='student_profile', uselist=False)
    guardian_user = db.relationship('User', foreign_keys=[guardian_user_id], backref='guardian_students')
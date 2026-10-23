from app.extensions import db
from datetime import datetime

class Hostel(db.Model):
    __tablename__ = 'hostels'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hostel_type = db.Column(db.String(20), nullable=False) # Boys, Girls, Co-ed
    address = db.Column(db.String(255))

    rooms = db.relationship('HostelRoom', backref='hostel', lazy=True)

class HostelRoom(db.Model):
    __tablename__ = 'hostel_rooms'
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'), nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, default=2)
    cost_per_bed = db.Column(db.Numeric(10, 2), nullable=False)

    allocations = db.relationship('RoomAllocation', backref='room', lazy=True)

class RoomAllocation(db.Model):
    __tablename__ = 'room_allocations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('hostel_rooms.id'), nullable=False)
    allocated_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active') # Active, Vacated

    student = db.relationship('Student', backref=db.backref('hostel_allocation', uselist=False))

class AdmissionInquiry(db.Model):
    __tablename__ = 'admission_inquiries'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    course_applied = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default='New Inquiry') # New Inquiry, Contacted, Admitted, Rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
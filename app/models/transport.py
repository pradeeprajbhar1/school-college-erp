from app.extensions import db
from datetime import datetime

class TransportVehicle(db.Model):
    __tablename__ = 'transport_vehicles'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    vehicle_number = db.Column(db.String(50), nullable=False) # e.g., UP32-AB-1234
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phone = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, default=40)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TransportRoute(db.Model):
    __tablename__ = 'transport_routes'
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('transport_vehicles.id'), nullable=True)
    route_title = db.Column(db.String(150), nullable=False) # e.g., Route 1: Charbagh to Aliganj
    start_point = db.Column(db.String(100))
    end_point = db.Column(db.String(100))
    monthly_fare = db.Column(db.Numeric(10, 2), nullable=False) # e.g., 1200.00
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicle = db.relationship('TransportVehicle', backref=db.backref('routes', lazy=True))

class StudentTransport(db.Model):
    __tablename__ = 'student_transports'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'), nullable=False)
    assigned_date = db.Column(db.Date, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('transport_allocation', uselist=False, lazy=True))
    route = db.relationship('TransportRoute', backref=db.backref('assigned_students', lazy=True))
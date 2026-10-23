from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.transport import TransportVehicle, TransportRoute, StudentTransport
from app.models.student import Student
from app.extensions import db

transport_bp = Blueprint('transport', __name__, url_prefix='/transport')

@transport_bp.route('/routes', methods=['GET', 'POST'])
@login_required
def manage_routes():
    vehicles = TransportVehicle.query.filter_by(institution_id=current_user.institution_id).all()
    
    if request.method == 'POST':
        action_type = request.form.get('action_type')

        # 1. Add Vehicle
        if action_type == 'add_vehicle':
            v_num = request.form.get('vehicle_number')
            d_name = request.form.get('driver_name')
            d_phone = request.form.get('driver_phone')
            capacity = int(request.form.get('capacity', 40))

            new_v = TransportVehicle(
                institution_id=current_user.institution_id,
                vehicle_number=v_num,
                driver_name=d_name,
                driver_phone=d_phone,
                capacity=capacity
            )
            db.session.add(new_v)
            db.session.commit()
            flash('Vehicle added successfully!', 'success')

        # 2. Add Route
        elif action_type == 'add_route':
            title = request.form.get('route_title')
            vehicle_id = request.form.get('vehicle_id')
            start_p = request.form.get('start_point')
            end_p = request.form.get('end_point')
            fare = float(request.form.get('monthly_fare', 0))

            new_r = TransportRoute(
                institution_id=current_user.institution_id,
                vehicle_id=vehicle_id if vehicle_id else None,
                route_title=title,
                start_point=start_p,
                end_point=end_p,
                monthly_fare=fare
            )
            db.session.add(new_r)
            db.session.commit()
            flash('Transport Route created successfully!', 'success')

        return redirect(url_for('transport.manage_routes'))

    routes = TransportRoute.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('transport/routes.html', title='Manage Routes & Vehicles', vehicles=vehicles, routes=routes)

@transport_bp.route('/assign', methods=['GET', 'POST'])
@login_required
def assign_transport():
    routes = TransportRoute.query.filter_by(institution_id=current_user.institution_id).all()

    if request.method == 'POST':
        admission_no = request.form.get('admission_number')
        route_id = request.form.get('route_id')

        student = Student.query.filter_by(admission_number=admission_no, institution_id=current_user.institution_id).first()
        route = TransportRoute.query.get(route_id)

        if not student:
            flash('Student not found with this Admission Number!', 'danger')
        elif not route:
            flash('Selected route does not exist.', 'danger')
        else:
            # Check if student already has a route
            existing = StudentTransport.query.filter_by(student_id=student.id).first()
            if existing:
                existing.route_id = route.id
                flash(f'Transport route updated for {student.first_name}.', 'info')
            else:
                new_alloc = StudentTransport(student_id=student.id, route_id=route.id)
                db.session.add(new_alloc)
                flash(f'Transport route "{route.route_title}" assigned to {student.first_name}.', 'success')
            
            db.session.commit()
            return redirect(url_for('transport.assign_transport'))

    allocations = StudentTransport.query.join(Student).filter(Student.institution_id == current_user.institution_id).all()
    return render_template('transport/assign.html', title='Assign Transport Route', routes=routes, allocations=allocations)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.hostel_lms import Hostel, HostelRoom, RoomAllocation, AdmissionInquiry
from app.models.student import Student
from app.extensions import db
from app.academic.routes import admin_required
from datetime import datetime

hostel_lms_bp = Blueprint('hostel_lms', __name__)

# --- 1. HOSTEL MANAGEMENT ROUTES ---

@hostel_lms_bp.route('/hostel/manage', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_hostels():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        # Add Hostel Building
        if form_type == 'add_hostel':
            name = request.form.get('name')
            hostel_type = request.form.get('hostel_type')
            address = request.form.get('address')
            
            new_hostel = Hostel(
                institution_id=current_user.institution_id,
                name=name,
                hostel_type=hostel_type,
                address=address
            )
            db.session.add(new_hostel)
            db.session.commit()
            flash('Hostel added successfully!', 'success')

        # Add Room to Hostel
        elif form_type == 'add_room':
            hostel_id = request.form.get('hostel_id')
            room_number = request.form.get('room_number')
            capacity = int(request.form.get('capacity', 2))
            cost = float(request.form.get('cost_per_bed', 0))

            new_room = HostelRoom(
                hostel_id=hostel_id,
                room_number=room_number,
                capacity=capacity,
                cost_per_bed=cost
            )
            db.session.add(new_room)
            db.session.commit()
            flash('Hostel room added successfully!', 'success')

        return redirect(url_for('hostel_lms.manage_hostels'))

    hostels = Hostel.query.filter_by(institution_id=current_user.institution_id).all()
    rooms = HostelRoom.query.join(Hostel).filter(Hostel.institution_id == current_user.institution_id).all()
    
    return render_template('hostel_lms/hostel.html', title='Hostel Management', hostels=hostels, rooms=rooms)

@hostel_lms_bp.route('/hostel/allocate', methods=['GET', 'POST'])
@login_required
@admin_required
def allocate_room():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        room_id = request.form.get('room_id')
        
        existing = RoomAllocation.query.filter_by(student_id=student_id, status='Active').first()
        if existing:
            flash('Student already has an active room allocation!', 'warning')
            return redirect(url_for('hostel_lms.allocate_room'))

        allocation = RoomAllocation(
            student_id=student_id,
            room_id=room_id,
            allocated_date=datetime.today().date(),
            status='Active'
        )
        db.session.add(allocation)
        db.session.commit()
        flash('Room allocated to student successfully!', 'success')
        return redirect(url_for('hostel_lms.allocate_room'))

    students = Student.query.filter_by(institution_id=current_user.institution_id, status='Active').all()
    rooms = HostelRoom.query.join(Hostel).filter(Hostel.institution_id == current_user.institution_id).all()
    allocations = RoomAllocation.query.join(Student).filter(Student.institution_id == current_user.institution_id, RoomAllocation.status == 'Active').all()

    return render_template('hostel_lms/allocate.html', title='Hostel Allocation', students=students, rooms=rooms, allocations=allocations)


# --- 2. ONLINE ADMISSION LMS ROUTES ---

@hostel_lms_bp.route('/apply-online', methods=['GET', 'POST'])
def public_apply():
    """PUBLIC FORM: Anyone can fill this without logging in."""
    if request.method == 'POST':
        institution_id = request.form.get('institution_id', 1)
        name = request.form.get('applicant_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        course = request.form.get('course_applied')
        notes = request.form.get('notes')

        inquiry = AdmissionInquiry(
            institution_id=institution_id,
            applicant_name=name,
            email=email,
            phone=phone,
            course_applied=course,
            notes=notes,
            status='New Inquiry'
        )
        db.session.add(inquiry)
        db.session.commit()
        flash('Application submitted successfully! Our admission counselor will contact you soon.', 'success')
        return redirect(url_for('hostel_lms.public_apply'))

    return render_template('hostel_lms/public_apply.html', title='Online Admission Application')

@hostel_lms_bp.route('/admission/leads', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_leads():
    if request.method == 'POST':
        lead_id = request.form.get('lead_id')
        new_status = request.form.get('status')
        notes = request.form.get('notes')

        lead = AdmissionInquiry.query.get_or_404(lead_id)
        lead.status = new_status
        if notes:
            lead.notes = notes
        db.session.commit()
        flash('Lead status updated successfully!', 'success')
        return redirect(url_for('hostel_lms.manage_leads'))

    leads = AdmissionInquiry.query.filter_by(institution_id=current_user.institution_id).order_by(AdmissionInquiry.applied_on.desc()).all()
    return render_template('hostel_lms/leads.html', title='Admission LMS Leads', leads=leads)
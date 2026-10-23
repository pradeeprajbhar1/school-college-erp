from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.student import Student, CourseClass
from app.extensions import db
from app.academic.routes import admin_required

from app.models.attendance import StudentAttendance
from app.models.fee import FeeInvoice, FeePayment
from app.models.exam import ExamMark
from app.models.library import BookIssue
from app.models.transport import StudentTransport
from app.models.hostel_lms import RoomAllocation
from app.models.core import User

students_bp = Blueprint('students', __name__, url_prefix='/students')

@students_bp.route('/')
@login_required
def index():
    selected_class_id = request.args.get('class_id', type=int)
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()
    
    query = Student.query.filter_by(institution_id=current_user.institution_id)
    if selected_class_id:
        students = query.filter_by(class_id=selected_class_id).all()
    else:
        students = query.all()
        
    return render_template('students/index.html', 
                           title='Students Directory', 
                           students=students, 
                           classes=classes, 
                           selected_class_id=selected_class_id)

@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        admission_number = request.form.get('admission_number')
        class_id = request.form.get('class_id')
        gender = request.form.get('gender')
        guardian_name = request.form.get('guardian_name')
        contact_number = request.form.get('contact_number')

        target_class_id = int(class_id) if class_id else None

        # Class-wise Admission Number Duplicate Check
        existing = Student.query.filter_by(
            admission_number=admission_number,
            class_id=target_class_id,
            institution_id=current_user.institution_id
        ).first()

        if existing:
            flash(f'Is class mein Admission Number "{admission_number}" pehle se kisi student ko mil chuka hai!', 'danger')
            return redirect(url_for('students.add_student'))

        student = Student(
            institution_id=current_user.institution_id,
            first_name=first_name,
            last_name=last_name,
            admission_number=admission_number,
            class_id=target_class_id,
            gender=gender,
            guardian_name=guardian_name,
            contact_number=contact_number,
            status='Active'
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('students.index', class_id=target_class_id) if target_class_id else url_for('students.index'))

    return render_template('students/add.html', title='Add Student', classes=classes)

@students_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    student = Student.query.filter_by(id=id, institution_id=current_user.institution_id).first_or_404()
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()

    if request.method == 'POST':
        new_class_id = request.form.get('class_id')
        target_class_id = int(new_class_id) if new_class_id else None

        student.first_name = request.form.get('first_name')
        student.last_name = request.form.get('last_name')
        student.gender = request.form.get('gender')
        student.class_id = target_class_id
        student.guardian_name = request.form.get('guardian_name')
        student.contact_number = request.form.get('contact_number')
        student.status = request.form.get('status')

        db.session.commit()
        flash('Student profile updated successfully!', 'success')
        return redirect(url_for('students.index', class_id=target_class_id) if target_class_id else url_for('students.index'))

    return render_template('students/edit.html', title='Edit Student', student=student, classes=classes)

@students_bp.route('/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.filter_by(id=student_id, institution_id=current_user.institution_id).first_or_404()
    redirect_class_id = student.class_id
    
    try:
        # 1. Clean attendance records
        StudentAttendance.query.filter_by(student_id=student.id).delete()
        
        # 2. Clean exam marks
        ExamMark.query.filter_by(student_id=student.id).delete()
        
        # 3. Clean library book issues
        BookIssue.query.filter_by(student_id=student.id).delete()
        
        # 4. Clean transport allocations
        StudentTransport.query.filter_by(student_id=student.id).delete()
        
        # 5. Clean hostel room allocations
        RoomAllocation.query.filter_by(student_id=student.id).delete()
        
        # 6. Clean fee invoices & fee payments
        invoices = FeeInvoice.query.filter_by(student_id=student.id).all()
        for inv in invoices:
            FeePayment.query.filter_by(invoice_id=inv.id).delete()
            db.session.delete(inv)
            
        # 7. Unlink / Delete associated login user account
        if student.user_id:
            user = User.query.get(student.user_id)
            if user:
                db.session.delete(user)
                
        # 8. Delete student record
        student_name = f"{student.first_name} {student.last_name or ''}".strip()
        db.session.delete(student)
        db.session.commit()
        
        flash(f'Student "{student_name}" and all associated records deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'danger')
        
    return redirect(url_for('students.index', class_id=redirect_class_id) if redirect_class_id else url_for('students.index'))
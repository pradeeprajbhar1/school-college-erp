from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.student import CourseClass, Student
from app.models.attendance import StudentAttendance
from app.extensions import db
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/', methods=['GET', 'POST'])
@login_required
def take_attendance():
    # Fetch all classes for the dropdown
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()
    selected_class = None
    students = []
    # Default date aaj ki set rahegi
    selected_date = datetime.today().strftime('%Y-%m-%d')
    attendance_records = {}
    
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        date_str = request.form.get('date')
        
        if class_id and date_str:
            selected_class = CourseClass.query.get(class_id)
            selected_date = date_str
            # Sirf selected class ke active students nikalenge
            students = Student.query.filter_by(class_id=class_id, institution_id=current_user.institution_id, status='Active').all()
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Agar form 'Save Attendance' button se submit hua hai
            if 'save_attendance' in request.form:
                for student in students:
                    status = request.form.get(f'status_{student.id}')
                    if status:
                        # Pehle check karenge ki is din ki attendance pehle se toh nahi lagi
                        record = StudentAttendance.query.filter_by(student_id=student.id, date=date_obj).first()
                        if record:
                            record.status = status # Update purani attendance
                        else:
                            new_record = StudentAttendance(student_id=student.id, date=date_obj, status=status) # Nayi attendance
                            db.session.add(new_record)
                
                db.session.commit()
                flash('Attendance saved successfully!', 'success')
                return redirect(url_for('attendance.take_attendance'))
            
            # Agar sirf "Fetch Students" par click hua hai, toh existing attendance records nikalenge
            else:
                existing_records = StudentAttendance.query.filter(
                    StudentAttendance.student_id.in_([s.id for s in students]),
                    StudentAttendance.date == date_obj
                ).all()
                for record in existing_records:
                    attendance_records[record.student_id] = record.status

    return render_template('attendance/take.html', title='Take Attendance', 
                           classes=classes, selected_class=selected_class, 
                           students=students, selected_date=selected_date,
                           attendance_records=attendance_records)
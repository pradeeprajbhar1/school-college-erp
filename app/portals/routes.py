from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.student import Student
from app.models.hr import Employee, TimetableSlot
from app.models.attendance import StudentAttendance
from app.models.fee import FeeInvoice
from app.models.exam import ExamMark

portals_bp = Blueprint('portals', __name__, url_prefix='/portals')

# ----------------- TEACHER PORTAL -----------------
@portals_bp.route('/teacher')
@login_required
def teacher_dashboard():
    # Verify Teacher role
    if not current_user.has_role('teacher'):
        flash('Unauthorized access to Teacher Portal.', 'danger')
        return redirect(url_for('auth.login'))

    employee = Employee.query.filter_by(user_id=current_user.id).first()
    assigned_slots = []
    if employee:
        assigned_slots = TimetableSlot.query.filter_by(teacher_id=employee.id).all()

    return render_template('portals/teacher.html', title='Teacher Portal', employee=employee, assigned_slots=assigned_slots)


# ----------------- STUDENT PORTAL -----------------
@portals_bp.route('/student')
@login_required
def student_dashboard():
    if not current_user.has_role('student'):
        flash('Unauthorized access to Student Portal.', 'danger')
        return redirect(url_for('auth.login'))

    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Attendance summary
    attendances = StudentAttendance.query.filter_by(student_id=student.id).all()
    total_days = len(attendances)
    present_days = sum(1 for a in attendances if a.status in ['Present', 'Late'])
    attendance_pct = round((present_days / total_days * 100), 1) if total_days > 0 else 0.0

    # Fee Invoices
    invoices = FeeInvoice.query.filter_by(student_id=student.id).all()
    total_due = sum(float(i.amount) - float(i.paid_amount) for i in invoices)

    # Exam Marks
    exam_marks = ExamMark.query.filter_by(student_id=student.id).all()

    return render_template('portals/student.html', title='Student Portal',
                           student=student, attendance_pct=attendance_pct,
                           invoices=invoices, total_due=total_due, exam_marks=exam_marks)


# ----------------- PARENT PORTAL -----------------
@portals_bp.route('/parent')
@login_required
def parent_dashboard():
    if not current_user.has_role('parent'):
        flash('Unauthorized access to Parent Portal.', 'danger')
        return redirect(url_for('auth.login'))

    # Get all children linked to this guardian user
    children = Student.query.filter_by(guardian_user_id=current_user.id).all()

    return render_template('portals/parent.html', title='Parent Portal', children=children)
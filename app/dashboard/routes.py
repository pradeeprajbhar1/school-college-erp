from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.student import Student, CourseClass
from app.models.hr import Employee
from app.models.attendance import StudentAttendance
from app.models.fee import FeeInvoice, FeePayment
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    inst_id = current_user.institution_id

    # 1. Real Database Metrics
    total_students = Student.query.filter_by(institution_id=inst_id, status='Active').count()
    total_teachers = Employee.query.filter_by(institution_id=inst_id, status='Active').count()
    total_classes = CourseClass.query.filter_by(institution_id=inst_id).count()

    # Today's Attendance Percentage Calculation
    today = datetime.today().date()
    today_records = StudentAttendance.query.join(Student).filter(
        Student.institution_id == inst_id,
        StudentAttendance.date == today
    ).all()
    
    total_today = len(today_records)
    present_today = sum(1 for r in today_records if r.status in ['Present', 'Late'])
    attendance_pct = round((present_today / total_today * 100), 1) if total_today > 0 else 0.0

    # Total Fees Collected & Total Pending Dues Calculation
    all_invoices = FeeInvoice.query.join(Student).filter(Student.institution_id == inst_id).all()
    total_assigned_fees = sum(float(inv.amount) for inv in all_invoices)
    total_collected_fees = sum(float(inv.paid_amount) for inv in all_invoices)
    total_pending_fees = total_assigned_fees - total_collected_fees

    # 2. Class-wise Student Count for Chart.js
    classes = CourseClass.query.filter_by(institution_id=inst_id).all()
    class_names = [c.name for c in classes]
    class_student_counts = [Student.query.filter_by(class_id=c.id, status='Active').count() for c in classes]

    # 3. Recent 5 Fee Payments
    recent_payments = FeePayment.query.join(FeeInvoice).join(Student).filter(
        Student.institution_id == inst_id
    ).order_by(FeePayment.created_at.desc()).limit(5).all()

    return render_template('dashboard/index.html',
                           title='Admin Dashboard',
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_classes=total_classes,
                           attendance_pct=attendance_pct,
                           total_collected_fees=total_collected_fees,
                           total_pending_fees=total_pending_fees,
                           class_names=class_names,
                           class_student_counts=class_student_counts,
                           recent_payments=recent_payments)
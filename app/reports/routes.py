from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from app.models.student import Student, CourseClass
from app.models.fee import FeeInvoice
import csv
import io

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/students')
@login_required
def student_report():
    inst_id = current_user.institution_id
    classes = CourseClass.query.filter_by(institution_id=inst_id).all()
    selected_class_id = request.args.get('class_id', type=int)

    query = Student.query.filter_by(institution_id=inst_id)
    if selected_class_id:
        query = query.filter_by(class_id=selected_class_id)

    students = query.all()

    # CSV Export Feature
    if request.args.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Admission No', 'First Name', 'Last Name', 'Gender', 'Class', 'Guardian', 'Contact', 'Status'])

        for s in students:
            writer.writerow([
                s.admission_number,
                s.first_name,
                s.last_name,
                s.gender,
                s.course_class.name if s.course_class else 'N/A',
                s.guardian_name or '',
                s.contact_number or '',
                s.status
            ])

        output.seek(0)
        return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=students_report.csv"})

    return render_template('reports/students.html', title='Student Strength Report', students=students, classes=classes, selected_class_id=selected_class_id)

@reports_bp.route('/fees')
@login_required
def fee_report():
    inst_id = current_user.institution_id
    invoices = FeeInvoice.query.join(Student).filter(Student.institution_id == inst_id).all()

    total_assigned = sum(float(inv.amount) for inv in invoices)
    total_collected = sum(float(inv.paid_amount) for inv in invoices)
    total_pending = total_assigned - total_collected

    # CSV Export Feature
    if request.args.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student Adm No', 'Student Name', 'Class', 'Fee Category', 'Total Amount', 'Paid Amount', 'Pending Amount', 'Status', 'Due Date'])

        for inv in invoices:
            writer.writerow([
                inv.student.admission_number,
                f"{inv.student.first_name} {inv.student.last_name}",
                inv.student.course_class.name if inv.student.course_class else 'N/A',
                inv.category.name,
                inv.amount,
                inv.paid_amount,
                float(inv.amount) - float(inv.paid_amount),
                inv.status,
                inv.due_date.strftime('%Y-%m-%d')
            ])

        output.seek(0)
        return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=fees_report.csv"})

    return render_template('reports/fees.html', title='Fee Collection Report', invoices=invoices, total_assigned=total_assigned, total_collected=total_collected, total_pending=total_pending)
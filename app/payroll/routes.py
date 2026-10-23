from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.hr import Employee
from app.models.payroll import LeaveRequest, Payroll
from app.extensions import db
from app.academic.routes import admin_required
from datetime import datetime

payroll_bp = Blueprint('payroll', __name__, url_prefix='/payroll')

@payroll_bp.route('/leaves', methods=['GET', 'POST'])
@login_required
def manage_leaves():
    is_admin = current_user.has_role('super_admin') or current_user.has_role('institution_admin')
    employee = Employee.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST' and employee:
        leave_type = request.form.get('leave_type')
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        reason = request.form.get('reason')

        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

        new_leave = LeaveRequest(
            employee_id=employee.id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        db.session.add(new_leave)
        db.session.commit()
        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('payroll.manage_leaves'))

    if is_admin:
        leaves = LeaveRequest.query.join(Employee).filter(Employee.institution_id == current_user.institution_id).order_by(LeaveRequest.applied_on.desc()).all()
    else:
        leaves = LeaveRequest.query.filter_by(employee_id=employee.id).order_by(LeaveRequest.applied_on.desc()).all() if employee else []

    return render_template('payroll/leave.html', title='Leave Management', leaves=leaves, is_admin=is_admin, employee=employee)

@payroll_bp.route('/leaves/approve/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_leave(id):
    leave = LeaveRequest.query.get_or_404(id)
    leave.status = 'Approved'
    db.session.commit()
    flash('Leave request approved.', 'success')
    return redirect(url_for('payroll.manage_leaves'))

@payroll_bp.route('/leaves/reject/<int:id>', methods=['POST'])
@login_required
@admin_required
def reject_leave(id):
    leave = LeaveRequest.query.get_or_404(id)
    leave.status = 'Rejected'
    db.session.commit()
    flash('Leave request rejected.', 'info')
    return redirect(url_for('payroll.manage_leaves'))

@payroll_bp.route('/generate', methods=['GET', 'POST'])
@login_required
@admin_required
def generate_payroll():
    employees = Employee.query.filter_by(institution_id=current_user.institution_id, status='Active').all()

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        month_year = request.form.get('month_year')
        basic = float(request.form.get('basic_salary', 0))
        allowances = float(request.form.get('allowances', 0))
        deductions = float(request.form.get('deductions', 0))
        net_salary = basic + allowances - deductions

        new_payroll = Payroll(
            employee_id=employee_id,
            month_year=month_year,
            basic_salary=basic,
            allowances=allowances,
            deductions=deductions,
            net_salary=net_salary,
            payment_date=datetime.today().date(),
            status='Paid'
        )
        db.session.add(new_payroll)
        db.session.commit()
        flash('Salary slip generated & processed successfully!', 'success')
        return redirect(url_for('payroll.generate_payroll'))

    payrolls = Payroll.query.join(Employee).filter(Employee.institution_id == current_user.institution_id).order_by(Payroll.created_at.desc()).all()
    return render_template('payroll/generate.html', title='Payroll & Salary Processing', employees=employees, payrolls=payrolls)

@payroll_bp.route('/payslip/<int:id>')
@login_required
def view_payslip(id):
    payroll = Payroll.query.get_or_404(id)
    if payroll.employee.institution_id != current_user.institution_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('payroll/payslip.html', title='Salary Slip', payroll=payroll)
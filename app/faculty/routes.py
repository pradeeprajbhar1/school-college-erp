from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.hr import Department, Employee
from app.extensions import db
from datetime import datetime

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.route('/')
@login_required
def index():
    employees = Employee.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('faculty/index.html', title='Faculty Directory', employees=employees)

@faculty_bp.route('/departments', methods=['GET', 'POST'])
@login_required
def departments():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_dept = Department(institution_id=current_user.institution_id, name=name)
            db.session.add(new_dept)
            db.session.commit()
            flash('Department added successfully!', 'success')
            return redirect(url_for('faculty.departments'))

    depts = Department.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('faculty/departments.html', title='Manage Departments', departments=depts)

@faculty_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_faculty():
    depts = Department.query.filter_by(institution_id=current_user.institution_id).all()
    if request.method == 'POST':
        code = request.form.get('employee_code')
        if Employee.query.filter_by(employee_code=code, institution_id=current_user.institution_id).first():
            flash('Employee Code already exists!', 'danger')
            return redirect(url_for('faculty.add_faculty'))

        joining_str = request.form.get('joining_date')
        joining_date = datetime.strptime(joining_str, '%Y-%m-%d').date() if joining_str else None

        new_employee = Employee(
            institution_id=current_user.institution_id,
            employee_code=code,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            contact_number=request.form.get('contact_number'),
            department_id=request.form.get('department_id'),
            designation=request.form.get('designation'),
            qualification=request.form.get('qualification'),
            joining_date=joining_date
        )
        db.session.add(new_employee)
        db.session.commit()
        flash('Faculty member added successfully!', 'success')
        return redirect(url_for('faculty.index'))

    return render_template('faculty/add.html', title='Add Faculty Member', departments=depts)
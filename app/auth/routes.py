from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask import current_app, Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.forms import LoginForm, RegistrationForm
from app.models.core import User, Role
from app.models.student import Student
from app.models.hr import Employee
from app.extensions import db
from app.academic.routes import admin_required
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --------------- HELPER FUNCTIONS ---------------

def get_role_redirect_url(user):
    role_names = [r.name for r in user.roles]
    if 'super_admin' in role_names or 'institution_admin' in role_names:
        return url_for('dashboard.index')
    elif 'teacher' in role_names:
        return url_for('portals.teacher_dashboard')
    elif 'student' in role_names:
        return url_for('portals.student_dashboard')
    elif 'parent' in role_names:
        return url_for('portals.parent_dashboard')
    return url_for('dashboard.index')

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except (SignatureExpired, BadTimeSignature):
        return None


# --------------- AUTHENTICATION ROUTES ---------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(get_role_redirect_url(current_user))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_active:
            flash('Your account is pending admin approval. Please contact school administration.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = get_role_redirect_url(user)
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(get_role_redirect_url(current_user))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        role_obj = Role.query.filter_by(name=form.role.data).first()
        if not role_obj:
            flash('Selected role does not exist.', 'danger')
            return redirect(url_for('auth.register'))

        inst_id = 1

        new_user = User(
            username=form.email.data.split('@')[0],
            email=form.email.data,
            institution_id=inst_id,
            is_active=False
        )
        new_user.set_password(form.password.data)
        new_user.roles.append(role_obj)
        db.session.add(new_user)
        db.session.commit()

        code = form.identifier_code.data.strip()
        if form.role.data == 'student':
            student = Student.query.filter_by(admission_number=code).first()
            if student:
                student.user_id = new_user.id
        elif form.role.data == 'parent':
            student = Student.query.filter_by(admission_number=code).first()
            if student:
                student.guardian_user_id = new_user.id
        elif form.role.data == 'teacher':
            employee = Employee.query.filter_by(employee_code=code).first()
            if employee:
                employee.user_id = new_user.id

        db.session.commit()

        flash('Registration request submitted successfully! Your account will be activated once verified by School Admin.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Sign Up', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# --------------- ADMIN APPROVAL ROUTES ---------------

@auth_bp.route('/pending-approvals')
@login_required
@admin_required
def pending_approvals():
    pending_users = User.query.filter_by(is_active=False).all()
    return render_template('auth/pending_approvals.html', title='Pending Registration Requests', users=pending_users)

@auth_bp.route('/approve-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f'Account for {user.email} approved and activated successfully!', 'success')
    return redirect(url_for('auth.pending_approvals'))

@auth_bp.route('/reject-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'Registration request for {user.email} rejected.', 'info')
    return redirect(url_for('auth.pending_approvals'))


# --------------- PASSWORD RESET ROUTES ---------------

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            print(f"\n[PASSWORD RESET LINK] For {user.email}:\n{reset_url}\n" + "-"*50)
            
            flash(f'Password reset link generated successfully! (Check terminal or click: {reset_url})', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Is email address se koi account nahi mila.', 'danger')
            
    return render_template('auth/forgot_password.html', title='Forgot Password')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    email = verify_reset_token(token)
    if not email:
        flash('Password reset link invalid hai ya expire ho chuka hai.', 'danger')
        return redirect(url_for('auth.forgot_password'))
        
    user = User.query.filter_by(email=email).first_or_404()
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Dono passwords match nahi kar rahe hain!', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
            
        user.set_password(new_password)
        db.session.commit()
        flash('Aapka password successfully reset ho gaya hai! Ab naye password se login karein.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', title='Reset Password', token=token)
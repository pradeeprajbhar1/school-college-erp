from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.student import CourseClass, Student
from app.models.hr import TimetableSlot
from app.extensions import db

academic_bp = Blueprint('academic', __name__, url_prefix='/academic')

# Admin Security Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.has_role('super_admin') or current_user.has_role('institution_admin')):
            flash('Access denied! Administrator privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@academic_bp.route('/classes', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_classes():
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        if class_name:
            existing = CourseClass.query.filter_by(name=class_name, institution_id=current_user.institution_id).first()
            if existing:
                flash('Class already exists!', 'danger')
            else:
                new_class = CourseClass(name=class_name, institution_id=current_user.institution_id)
                db.session.add(new_class)
                db.session.commit()
                flash('Class added successfully!', 'success')
        return redirect(url_for('academic.manage_classes'))
    
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('academic/classes.html', title='Manage Classes', classes=classes)

@academic_bp.route('/classes/delete/<int:class_id>', methods=['POST', 'GET'])
@login_required
@admin_required
def delete_class(class_id):
    course_class = CourseClass.query.filter_by(id=class_id, institution_id=current_user.institution_id).first_or_404()
    
    # 1. Check if students are assigned to this class
    student_count = Student.query.filter_by(class_id=course_class.id).count()
    if student_count > 0:
        flash(f'Cannot delete "{course_class.name}" because {student_count} student(s) are assigned to it. Please reassign or remove students first.', 'warning')
        return redirect(url_for('academic.manage_classes'))
        
    try:
        # 2. Delete linked timetable slots first to avoid Foreign Key Integrity Error
        TimetableSlot.query.filter_by(class_id=course_class.id).delete()
        
        # 3. Delete the class
        db.session.delete(course_class)
        db.session.commit()
        flash('Class deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete class because other dependent records (like exams or attendance) exist.', 'danger')
        
    return redirect(url_for('academic.manage_classes'))
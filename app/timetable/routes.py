from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.student import CourseClass
from app.models.hr import Employee, TimetableSlot
from app.extensions import db

timetable_bp = Blueprint('timetable', __name__, url_prefix='/timetable')

@timetable_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage_timetable():
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()
    teachers = Employee.query.filter_by(institution_id=current_user.institution_id, status='Active').all()

    if request.method == 'POST':
        class_id = request.form.get('class_id')
        subject_name = request.form.get('subject_name')
        teacher_id = request.form.get('teacher_id')
        day_of_week = request.form.get('day_of_week')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        room_number = request.form.get('room_number')

        new_slot = TimetableSlot(
            institution_id=current_user.institution_id,
            class_id=class_id,
            teacher_id=teacher_id if teacher_id else None,
            subject_name=subject_name,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room_number=room_number
        )
        db.session.add(new_slot)
        db.session.commit()
        flash('Timetable slot added successfully!', 'success')
        return redirect(url_for('timetable.manage_timetable'))

    slots = TimetableSlot.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('timetable/manage.html', title='Timetable Management', classes=classes, teachers=teachers, slots=slots)

@timetable_bp.route('/view/<int:class_id>')
@login_required
def view_class_timetable(class_id):
    course_class = CourseClass.query.get_or_404(class_id)
    if course_class.institution_id != current_user.institution_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))

    slots = TimetableSlot.query.filter_by(class_id=course_class.id, institution_id=current_user.institution_id).all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # Group slots by day
    timetable_grid = {day: [] for day in days}
    for slot in slots:
        if slot.day_of_week in timetable_grid:
            timetable_grid[slot.day_of_week].append(slot)

    return render_template('timetable/view.html', title=f'Timetable - {course_class.name}', course_class=course_class, timetable_grid=timetable_grid)
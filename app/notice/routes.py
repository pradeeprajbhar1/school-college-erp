from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.notice import Notice, Event
from app.extensions import db
from app.academic.routes import admin_required
from datetime import datetime

notice_bp = Blueprint('notice', __name__, url_prefix='/notice')

@notice_bp.route('/manage', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_notices_events():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # 1. Publish Notice
        if form_type == 'notice':
            title = request.form.get('title')
            content = request.form.get('content')
            target = request.form.get('target_audience')
            expiry_str = request.form.get('expiry_date')
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date() if expiry_str else None

            new_notice = Notice(
                institution_id=current_user.institution_id,
                title=title,
                content=content,
                target_audience=target,
                expiry_date=expiry_date
            )
            db.session.add(new_notice)
            db.session.commit()
            flash('Notice published successfully!', 'success')

        # 2. Add Event
        elif form_type == 'event':
            title = request.form.get('title')
            description = request.form.get('description')
            event_date_str = request.form.get('event_date')
            start_time = request.form.get('start_time')
            venue = request.form.get('venue')

            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()

            new_event = Event(
                institution_id=current_user.institution_id,
                title=title,
                description=description,
                event_date=event_date,
                start_time=start_time,
                venue=venue
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Event added to school calendar!', 'success')

        return redirect(url_for('notice.manage_notices_events'))

    notices = Notice.query.filter_by(institution_id=current_user.institution_id).order_by(Notice.posted_date.desc()).all()
    events = Event.query.filter_by(institution_id=current_user.institution_id).order_by(Event.event_date.asc()).all()

    return render_template('notice/manage.html', title='Manage Notice Board & Events', notices=notices, events=events)

@notice_bp.route('/board')
@login_required
def view_notice_board():
    user_roles = [r.name for r in current_user.roles]
    query = Notice.query.filter_by(institution_id=current_user.institution_id)

    # Filter notices based on user role
    if 'super_admin' in user_roles or 'institution_admin' in user_roles:
        notices = query.order_by(Notice.posted_date.desc()).all()
    elif 'teacher' in user_roles:
        notices = query.filter(Notice.target_audience.in_(['All', 'Teachers'])).order_by(Notice.posted_date.desc()).all()
    elif 'student' in user_roles:
        notices = query.filter(Notice.target_audience.in_(['All', 'Students'])).order_by(Notice.posted_date.desc()).all()
    elif 'parent' in user_roles:
        notices = query.filter(Notice.target_audience.in_(['All', 'Parents'])).order_by(Notice.posted_date.desc()).all()
    else:
        notices = []

    events = Event.query.filter_by(institution_id=current_user.institution_id).order_by(Event.event_date.asc()).all()

    return render_template('notice/board.html', title='Digital Notice Board & Events', notices=notices, events=events)
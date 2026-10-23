from flask import Flask, redirect, url_for
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.students.routes import students_bp
    from app.academic.routes import academic_bp
    from app.attendance.routes import attendance_bp
    from app.fees.routes import fees_bp
    from app.exams.routes import exams_bp
    from app.faculty.routes import faculty_bp
    from app.timetable.routes import timetable_bp
    from app.reports.routes import reports_bp
    from app.portals.routes import portals_bp
    from app.library.routes import library_bp
    from app.transport.routes import transport_bp
    from app.payroll.routes import payroll_bp
    from app.notice.routes import notice_bp
    from app.hostel_lms.routes import hostel_lms_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(fees_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(portals_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(transport_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(notice_bp)
    app.register_blueprint(hostel_lms_bp)

    # Root route - Redirect to dashboard
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.core import User
        return User.query.get(int(user_id))

    return app
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.core import Role, Institution, User

app = create_app()

def seed_data():
    with app.app_context():
        # 1. Create Roles
        roles = ['super_admin', 'institution_admin', 'teacher', 'student']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name, description=f"{role_name.replace('_', ' ').title()} Role")
                db.session.add(role)
        db.session.commit()

        # 2. Create an Institution
        if not Institution.query.filter_by(code='DEMO01').first():
            institute = Institution(
                name='Demo International School',
                code='DEMO01',
                address='123 Education Lane, Tech City'
            )
            db.session.add(institute)
            db.session.commit()
        
        institute = Institution.query.filter_by(code='DEMO01').first()
        admin_role = Role.query.filter_by(name='institution_admin').first()

        # 3. Create Default Admin User
        if not User.query.filter_by(email='admin@school.com').first():
            admin_user = User(
                username='admin',
                email='admin@school.com',
                institution_id=institute.id
            )
            admin_user.set_password('admin123')
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print("Database seeded successfully!")
            print("Login Email: admin@school.com")
            print("Password: admin123")
        else:
            print("Data already exists.")

if __name__ == '__main__':
    seed_data()
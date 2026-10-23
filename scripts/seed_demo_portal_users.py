import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.core import Role, Institution, User
from app.models.student import Student, CourseClass
from app.models.hr import Employee

app = create_app()

def seed_portals():
    with app.app_context():
        inst = Institution.query.filter_by(code='DEMO01').first()
        if not inst:
            print("Run seed_demo_data.py first!")
            return

        # Ensure Roles Exist
        roles = ['teacher', 'student', 'parent']
        for r_name in roles:
            if not Role.query.filter_by(name=r_name).first():
                db.session.add(Role(name=r_name, description=f"{r_name.capitalize()} Role"))
        db.session.commit()

        role_teacher = Role.query.filter_by(name='teacher').first()
        role_student = Role.query.filter_by(name='student').first()
        role_parent = Role.query.filter_by(name='parent').first()

        # 1. Create Teacher User & Employee
        teacher_user = User.query.filter_by(email='teacher@school.com').first()
        if not teacher_user:
            teacher_user = User(username='teacher_john', email='teacher@school.com', institution_id=inst.id)
            teacher_user.set_password('teacher123')
            teacher_user.roles.append(role_teacher)
            db.session.add(teacher_user)
            db.session.commit()

            emp = Employee(
                institution_id=inst.id,
                user_id=teacher_user.id,
                employee_code='EMP-T01',
                first_name='John',
                last_name='Teacher',
                email='teacher@school.com',
                designation='Senior Teacher'
            )
            db.session.add(emp)
            db.session.commit()

        # 2. Create Parent User
        parent_user = User.query.filter_by(email='parent@school.com').first()
        if not parent_user:
            parent_user = User(username='parent_uday', email='parent@school.com', institution_id=inst.id)
            parent_user.set_password('parent123')
            parent_user.roles.append(role_parent)
            db.session.add(parent_user)
            db.session.commit()

        # 3. Create Student User & Link to Student Profile
        student_user = User.query.filter_by(email='student@school.com').first()
        if not student_user:
            student_user = User(username='student_pradeep', email='student@school.com', institution_id=inst.id)
            student_user.set_password('student123')
            student_user.roles.append(role_student)
            db.session.add(student_user)
            db.session.commit()

            # Link existing student or create one
            st = Student.query.filter_by(institution_id=inst.id).first()
            if st:
                st.user_id = student_user.id
                st.guardian_user_id = parent_user.id
                db.session.commit()

        print("Successfully Created Portal Demo Users:")
        print("---------------------------------------")
        print("1. Teacher Login -> Email: teacher@school.com | Pass: teacher123")
        print("2. Student Login -> Email: student@school.com | Pass: student123")
        print("3. Parent Login  -> Email: parent@school.com  | Pass: parent123")

if __name__ == '__main__':
    seed_portals()
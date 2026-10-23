from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.student import CourseClass, Student
from app.models.exam import Exam, ExamMark
from app.extensions import db
from datetime import datetime

exams_bp = Blueprint('exams', __name__, url_prefix='/exams')

@exams_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage_exams():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        new_exam = Exam(
            institution_id=current_user.institution_id,
            name=name,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_exam)
        db.session.commit()
        flash('Exam created successfully!', 'success')
        return redirect(url_for('exams.manage_exams'))
        
    exams = Exam.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('exams/manage.html', title='Manage Exams', exams=exams)

@exams_bp.route('/marks', methods=['GET', 'POST'])
@login_required
def enter_marks():
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()
    exams = Exam.query.filter_by(institution_id=current_user.institution_id).all()
    
    selected_class = None
    selected_exam = None
    subject_name = ''
    max_marks = 100.0
    students = []
    existing_marks = {}
    
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        exam_id = request.form.get('exam_id')
        subject_name = request.form.get('subject_name')
        max_marks = float(request.form.get('max_marks', 100))
        
        if class_id and exam_id and subject_name:
            selected_class = CourseClass.query.get(class_id)
            selected_exam = Exam.query.get(exam_id)
            students = Student.query.filter_by(class_id=class_id, institution_id=current_user.institution_id, status='Active').all()
            
            # Save Marks Submit
            if 'save_marks' in request.form:
                for student in students:
                    mark_val = request.form.get(f'mark_{student.id}')
                    if mark_val is not None and mark_val != '':
                        obtained = float(mark_val)
                        record = ExamMark.query.filter_by(
                            exam_id=exam_id,
                            student_id=student.id,
                            subject_name=subject_name
                        ).first()
                        if record:
                            record.marks_obtained = obtained
                            record.max_marks = max_marks
                        else:
                            new_record = ExamMark(
                                exam_id=exam_id,
                                student_id=student.id,
                                subject_name=subject_name,
                                max_marks=max_marks,
                                marks_obtained=obtained
                            )
                            db.session.add(new_record)
                
                db.session.commit()
                flash('Marks saved successfully!', 'success')
                return redirect(url_for('exams.enter_marks'))
            else:
                # Fetch existing marks for pre-filling
                records = ExamMark.query.filter(
                    ExamMark.exam_id == exam_id,
                    ExamMark.subject_name == subject_name,
                    ExamMark.student_id.in_([s.id for s in students])
                ).all()
                for r in records:
                    existing_marks[r.student_id] = r.marks_obtained

    return render_template('exams/marks.html', title='Marks Entry', 
                           classes=classes, exams=exams, 
                           selected_class=selected_class, selected_exam=selected_exam,
                           subject_name=subject_name, max_marks=max_marks,
                           students=students, existing_marks=existing_marks)

@exams_bp.route('/report-card/<int:student_id>/<int:exam_id>')
@login_required
def report_card(student_id, exam_id):
    student = Student.query.get_or_404(student_id)
    exam = Exam.query.get_or_404(exam_id)
    
    if student.institution_id != current_user.institution_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    marks = ExamMark.query.filter_by(student_id=student.id, exam_id=exam.id).all()
    
    total_obtained = sum(m.marks_obtained for m in marks)
    total_max = sum(m.max_marks for m in marks)
    percentage = (total_obtained / total_max * 100) if total_max > 0 else 0
    
    return render_template('exams/report_card.html', title='Report Card',
                           student=student, exam=exam, marks=marks,
                           total_obtained=total_obtained, total_max=total_max,
                           percentage=round(percentage, 2))
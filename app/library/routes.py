from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.library import Book, BookIssue
from app.models.student import Student
from app.extensions import db
from app.academic.routes import admin_required
from datetime import datetime, timedelta

library_bp = Blueprint('library', __name__, url_prefix='/library')

@library_bp.route('/books', methods=['GET', 'POST'])
@login_required
def books_directory():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        category = request.form.get('category')
        quantity = int(request.form.get('quantity', 1))
        rack_number = request.form.get('rack_number')

        new_book = Book(
            institution_id=current_user.institution_id,
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            quantity=quantity,
            available_qty=quantity,
            rack_number=rack_number
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added to library catalog!', 'success')
        return redirect(url_for('library.books_directory'))

    books = Book.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('library/books.html', title='Library Books Catalog', books=books)

@library_bp.route('/issue', methods=['GET', 'POST'])
@login_required
def issue_book():
    books = Book.query.filter(Book.institution_id == current_user.institution_id, Book.available_qty > 0).all()
    
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        admission_no = request.form.get('admission_number')
        days = int(request.form.get('days', 14))

        student = Student.query.filter_by(admission_number=admission_no, institution_id=current_user.institution_id).first()
        book = Book.query.get(book_id)

        if not student:
            flash('Invalid Student Admission Number!', 'danger')
        elif not book or book.available_qty < 1:
            flash('Selected book is currently unavailable.', 'danger')
        else:
            issue_date = datetime.today().date()
            due_date = issue_date + timedelta(days=days)

            new_issue = BookIssue(
                book_id=book.id,
                student_id=student.id,
                issue_date=issue_date,
                due_date=due_date,
                status='Issued'
            )
            book.available_qty -= 1
            db.session.add(new_issue)
            db.session.commit()
            flash(f'Book "{book.title}" issued to {student.first_name} till {due_date.strftime("%d %b %Y")}.', 'success')
            return redirect(url_for('library.issue_book'))

    issued_records = BookIssue.query.join(Book).filter(Book.institution_id == current_user.institution_id, BookIssue.status == 'Issued').all()
    return render_template('library/issue.html', title='Issue / Return Book', books=books, issued_records=issued_records)

@library_bp.route('/return/<int:issue_id>', methods=['POST'])
@login_required
def return_book(issue_id):
    issue = BookIssue.query.get_or_404(issue_id)
    today = datetime.today().date()
    
    # Calculate Late Fine (e.g., ₹10 per day after due date)
    fine = 0.0
    if today > issue.due_date:
        overdue_days = (today - issue.due_date).days
        fine = float(overdue_days * 10)

    issue.return_date = today
    issue.fine_amount = fine
    issue.status = 'Returned'
    issue.book.available_qty += 1

    db.session.commit()
    flash(f'Book returned successfully. Late fine charged: ₹{fine}', 'info')
    return redirect(url_for('library.issue_book'))
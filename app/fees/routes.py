from app.utils.notification import send_sms_notification, send_whatsapp_notification
import os
import razorpay
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.fee import FeeCategory, FeeInvoice, FeePayment
from app.models.student import Student, CourseClass
from app.extensions import db
from app.academic.routes import admin_required

fees_bp = Blueprint('fees', __name__, url_prefix='/fees')

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_dummy_key')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'dummy_secret')

@fees_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        amount = request.form.get('amount')
        
        if name and amount:
            cat = FeeCategory(
                institution_id=current_user.institution_id,
                name=name,
                description=description,
                default_amount=float(amount)
            )
            db.session.add(cat)
            db.session.commit()
            flash('Fee category created successfully!', 'success')
            return redirect(url_for('fees.categories'))

    categories = FeeCategory.query.filter_by(institution_id=current_user.institution_id).all()
    return render_template('fees/categories.html', title='Fee Categories', categories=categories)

@fees_bp.route('/assign', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_fees():
    categories = FeeCategory.query.filter_by(institution_id=current_user.institution_id).all()
    classes = CourseClass.query.filter_by(institution_id=current_user.institution_id).all()

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        class_id = request.form.get('class_id')
        due_date_str = request.form.get('due_date')
        
        category = FeeCategory.query.get(category_id)
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        students = Student.query.filter_by(class_id=class_id, status='Active').all()
        
        count = 0
        for s in students:
            existing = FeeInvoice.query.filter_by(student_id=s.id, category_id=category.id, status='Unpaid').first()
            if not existing:
                inv = FeeInvoice(
                    student_id=s.id,
                    category_id=category.id,
                    amount=category.default_amount,
                    due_date=due_date
                )
                db.session.add(inv)
                count += 1
        
        db.session.commit()
        flash(f'Fee invoices generated for {count} student(s).', 'success')
        return redirect(url_for('fees.assign_fees'))

    return render_template('fees/assign.html', title='Assign Fees', categories=categories, classes=classes)

@fees_bp.route('/collect', methods=['GET', 'POST'])
@login_required
def collect_fees():
    student = None
    invoices = []
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'search':
            admission_no = request.form.get('admission_number')
            student = Student.query.filter_by(admission_number=admission_no, institution_id=current_user.institution_id).first()
            if student:
                invoices = FeeInvoice.query.filter_by(student_id=student.id).filter(FeeInvoice.status != 'Paid').all()
            else:
                flash('Student not found with this Admission Number.', 'danger')
                
        elif action == 'pay':
            invoice_id = request.form.get('invoice_id')
            payment_amount = float(request.form.get('amount_paid'))
            payment_method = request.form.get('payment_method')
            
            invoice = FeeInvoice.query.get_or_404(invoice_id)
            
            payment = FeePayment(
                invoice_id=invoice.id,
                amount_paid=payment_amount,
                payment_date=datetime.today().date(),
                payment_method=payment_method
            )
            db.session.add(payment)
            
            invoice.paid_amount = float(invoice.paid_amount) + payment_amount
            if invoice.paid_amount >= float(invoice.amount):
                invoice.status = 'Paid'
            else:
                invoice.status = 'Partial'
                
            db.session.commit()
            flash('Payment collected successfully!', 'success')
            return redirect(url_for('fees.print_receipt', payment_id=payment.id))

    return render_template('fees/collect.html', title='Collect Fees', student=student, invoices=invoices)

@fees_bp.route('/receipt/<int:payment_id>')
@login_required
def print_receipt(payment_id):
    payment = FeePayment.query.get_or_404(payment_id)
    return render_template('fees/receipt.html', title='Fee Receipt', payment=payment)

@fees_bp.route('/pay-online/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
def pay_online(invoice_id):
    invoice = FeeInvoice.query.get_or_404(invoice_id)
    amount_due = float(invoice.amount) - float(invoice.paid_amount)
    
    if amount_due <= 0:
        flash('This fee invoice is already fully paid.', 'info')
        return redirect(url_for('portals.student_dashboard'))
        
    order_id = f"order_demo_{invoice.id}_{int(datetime.utcnow().timestamp())}"
    
    # Real Razorpay API Call (Agar valid keys configured hain)
    if RAZORPAY_KEY_ID != 'rzp_test_dummy_key' and RAZORPAY_KEY_SECRET != 'dummy_secret':
        try:
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            order_amount = int(amount_due * 100) # Amount in paise
            order = client.order.create({
                'amount': order_amount,
                'currency': 'INR',
                'payment_capture': '1'
            })
            order_id = order['id']
        except Exception as e:
            print(f"Razorpay API Error: {e}")
            flash('Payment gateway error. Using demo mode for testing.', 'warning')
    
    return render_template('fees/pay_online.html', 
                           title='Pay Fee Online', 
                           invoice=invoice, 
                           amount_due=amount_due,
                           order_id=order_id,
                           razorpay_key=RAZORPAY_KEY_ID)

@fees_bp.route('/payment-callback', methods=['POST'])
@login_required
def payment_callback():
    payment_id = request.form.get('razorpay_payment_id', f'pay_demo_{int(datetime.utcnow().timestamp())}')
    order_id = request.form.get('razorpay_order_id', '')
    signature = request.form.get('razorpay_signature', '')
    invoice_id = request.form.get('invoice_id')
    
    invoice = FeeInvoice.query.get_or_404(invoice_id)
    amount_paid = float(invoice.amount) - float(invoice.paid_amount)
    
    # Verify Signature agar Real API Keys active hain
    if RAZORPAY_KEY_ID != 'rzp_test_dummy_key' and RAZORPAY_KEY_SECRET != 'dummy_secret':
        try:
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
        except Exception as e:
            flash('Payment verification failed. Please try again.', 'danger')
            return redirect(url_for('portals.student_dashboard'))
        
    # Save Payment Record
    new_payment = FeePayment(
        invoice_id=invoice.id,
        amount_paid=amount_paid,
        payment_date=datetime.today().date(),
        payment_method='Razorpay Online',
        reference_number=payment_id,
        razorpay_order_id=order_id,
        razorpay_payment_id=payment_id,
        razorpay_signature=signature
    )
    db.session.add(new_payment)
    
    invoice.paid_amount = invoice.amount
    invoice.status = 'Paid'
    db.session.commit()
    
    flash('Payment successful! Here is your official payment receipt.', 'success')
    return redirect(url_for('fees.print_receipt', payment_id=new_payment.id))

@fees_bp.route('/submit-upi-qr', methods=['POST'])
@login_required
def submit_upi_qr():
    invoice_id = request.form.get('invoice_id')
    utr_number = request.form.get('utr_number')
    
    invoice = FeeInvoice.query.get_or_404(invoice_id)
    amount_due = float(invoice.amount) - float(invoice.paid_amount)
    
    if not utr_number or len(utr_number.strip()) < 6:
        flash('Please enter a valid 12-digit Transaction / UTR Reference Number.', 'danger')
        return redirect(url_for('fees.pay_online', invoice_id=invoice.id))
        
    # Save Fee Payment Record
    new_payment = FeePayment(
        invoice_id=invoice.id,
        amount_paid=amount_due,
        payment_date=datetime.today().date(),
        payment_method='Direct UPI QR Scan',
        reference_number=utr_number.strip()
    )
    db.session.add(new_payment)
    
    invoice.paid_amount = invoice.amount
    invoice.status = 'Paid'
    db.session.commit()
    
    flash('Payment recorded successfully via UPI QR Code! Here is your official receipt.', 'success')
    return redirect(url_for('fees.print_receipt', payment_id=new_payment.id))

@fees_bp.route('/send-reminders', methods=['POST'])
@login_required
@admin_required
def send_fee_reminders():
    unpaid_invoices = FeeInvoice.query.filter_by(status='Unpaid').all()
    count = 0
    
    for inv in unpaid_invoices:
        student = inv.student
        if student and student.contact_number:
            due_amount = float(inv.amount) - float(inv.paid_amount)
            msg = f"Dear Parent, Fee invoice for {student.first_name} ({inv.category.name}) of Rs.{due_amount:.2f} is pending. Due Date: {inv.due_date}. Please pay online via Student Portal."
            
            send_sms_notification(student.contact_number, msg)
            send_whatsapp_notification(student.contact_number, msg)
            count += 1
            
    flash(f'Fee reminder WhatsApp & SMS notifications dispatched to {count} student(s)!', 'success')
    return redirect(url_for('fees.assign_fees'))
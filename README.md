# Enterprise School & College ERP Management System

A production-oriented, centralized platform built with **Python Flask**, **Flask-SQLAlchemy**, **MySQL 8+**, and **Bootstrap 5** for managing academic, administrative, financial, and operational workflows across educational institutions.

---

## Technical Architecture & Stack
- **Backend:** Python 3.10+, Flask (Blueprint Architecture), Flask-SQLAlchemy (ORM), Flask-Login (Authentication), Flask-WTF (CSRF Protection), Flask-Migrate.
- **Frontend:** Responsive HTML5, CSS3, Vanilla JavaScript (Fetch API), Chart.js (Data Analytics), Bootstrap 5.
- **Database:** MySQL 8+ (Normalized Relational Schema with Foreign Keys, Cascading Rules, and Transactions).

---

## Key Modules Included
1. **Multi-Tenant Institution Setup:** Institution profiles, isolation of data per school/college.
2. **Student Management:** Admission directory, student registration, profile editing, and status management.
3. **Academic Configuration:** Class & Section management, Course allocation.
4. **Attendance System:** Daily class-wise student attendance entry (Present/Absent/Late status tracking).
5. **Fees & Finance System:** Fee categories, bulk class invoice generation, fee collection, partial/full payment processing, and printable fee receipts.
6. **Examination & Results:** Exam scheduling, subject-wise marks entry, automatic pass/fail & percentage calculations, and printable student marksheets.
7. **Faculty & HR Management:** Department management, employee/teacher directory, designation and qualification tracking.
8. **Timetable Scheduling:** Weekly day-wise schedule grid generator with subject, room, and assigned teacher allocation.
9. **Analytics & Centralized Reports:** Real-time database metrics dashboard, Chart.js visualizations, and instant CSV/Excel report exports.

---

## Quick Setup Instructions (Windows / Linux)

### 1. Clone & Setup Virtual Environment
```bash
git clone <repository-url>
cd school_college_erp

# Create virtual environment
python -m venv venv

# Activate Virtual Environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
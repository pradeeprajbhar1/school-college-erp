from app.models.core import Institution, Role, User
from app.models.student import CourseClass, Section, Student
from app.models.attendance import StudentAttendance
from app.models.fee import FeeCategory, FeeInvoice, FeePayment
from app.models.exam import Exam, ExamMark
from app.models.hr import Department, Employee, TimetableSlot
from app.models.library import Book, BookIssue
from app.models.transport import TransportVehicle, TransportRoute, StudentTransport
from app.models.payroll import LeaveRequest, Payroll
from app.models.notice import Notice, Event
from app.models.hostel_lms import Hostel, HostelRoom, RoomAllocation, AdmissionInquiry
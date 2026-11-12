from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

EXAM_TYPES = ["Viva", "Practical", "Project Demo", "Assessment"]
EXAM_STATUSES = ["Draft", "Slot Creation", "Booking Open", "Closed", "Completed"]


# One table for everyone. The "role" column says who they are: admin / examiner / student
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # stored as a hash
    role = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=True)  # new examiners start as False
    is_active = db.Column(db.Boolean, default=True)  # False = deactivated by admin
    created_at = db.Column(db.DateTime, default=datetime.now)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Active")  # Active / Inactive

    exams = db.relationship("Exam", backref="course", cascade="all, delete-orphan")


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    exam_type = db.Column(db.String(30), nullable=False)  # one of EXAM_TYPES
    duration = db.Column(db.Integer, nullable=False)  # minutes
    max_marks = db.Column(db.Integer, nullable=False)
    slot_start = db.Column(db.Date, nullable=False)  # examiners create slots in this period
    slot_end = db.Column(db.Date, nullable=False)
    booking_start = db.Column(db.Date, nullable=False)  # students book slots in this period
    booking_end = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default="Draft")  # one of EXAM_STATUSES
    results_published = db.Column(db.Boolean, default=False)

    examiner = db.relationship("User", backref="assigned_exams")
    rubrics = db.relationship("Rubric", backref="exam", cascade="all, delete-orphan")
    slots = db.relationship("Slot", backref="exam", cascade="all, delete-orphan", order_by="Slot.date")


class Rubric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    criterion = db.Column(db.String(150), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    weightage = db.Column(db.Float)  # % of the exam's total marks
    description = db.Column(db.Text)

    marks = db.relationship("Mark", backref="rubric", cascade="all, delete-orphan")


class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Available")  # Available / Full / Cancelled / Completed

    examiner = db.relationship("User")
    bookings = db.relationship("Booking", backref="slot", cascade="all, delete-orphan")


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slot.id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default="Booked")  # Booked / Cancelled / Completed
    total_marks = db.Column(db.Integer)  # filled in by the examiner
    remarks = db.Column(db.Text)

    student = db.relationship("User", backref="bookings")
    exam = db.relationship("Exam")
    marks = db.relationship("Mark", backref="booking", cascade="all, delete-orphan")


# Marks given to one booking for one rubric criterion
class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey("rubric.id"), nullable=False)
    marks = db.Column(db.Integer, nullable=False)

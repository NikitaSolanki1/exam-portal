from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

EXAM_TYPES = ["Viva", "Practical", "Project Demo", "Assessment"]
EXAM_STATUSES = ["Draft", "Slot Creation", "Booking Open", "Closed", "Completed"]

# Each table has a to_dict() method.
# It turns a row into a Python dict, so Flask can send it to Vue as JSON.
# Dates are sent as text like "2026-11-12" and times like "10:30".


# One table for everyone. The "role" column says who they are: admin / examiner / student
class User(db.Model):
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

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "department": self.department,
            "is_approved": self.is_approved,
            "is_active": self.is_active,
            "exam_count": len(self.assigned_exams),  # exams given to an examiner
            "booking_count": len(self.bookings),  # bookings made by a student
        }


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Active")  # Active / Inactive

    exams = db.relationship("Exam", backref="course", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "exam_count": len(self.exams),
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "course_code": self.course.code,
            "course_name": self.course.name,
            "examiner_id": self.examiner_id,
            "examiner_name": self.examiner.name,
            "name": self.name,
            "exam_type": self.exam_type,
            "duration": self.duration,
            "max_marks": self.max_marks,
            "slot_start": self.slot_start.isoformat(),
            "slot_end": self.slot_end.isoformat(),
            "booking_start": self.booking_start.isoformat(),
            "booking_end": self.booking_end.isoformat(),
            "status": self.status,
            "results_published": self.results_published,
            "slot_count": len(self.slots),
        }


class Rubric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    criterion = db.Column(db.String(150), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    weightage = db.Column(db.Float)  # % of the exam's total marks
    description = db.Column(db.Text)

    marks = db.relationship("Mark", backref="rubric", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "criterion": self.criterion,
            "max_marks": self.max_marks,
            "weightage": self.weightage,
            "description": self.description,
        }


class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Available")  # Available / Full / Completed

    examiner = db.relationship("User")
    bookings = db.relationship("Booking", backref="slot", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "exam_name": self.exam.name,
            "course_code": self.exam.course.code,
            "examiner_name": self.examiner.name,
            "date": self.date.isoformat(),
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
            "capacity": self.capacity,
            "available_seats": self.available_seats,
            "status": self.status,
            "has_bookings": len(self.bookings) > 0,
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "student_name": self.student.name,
            "student_email": self.student.email,
            "student_department": self.student.department,
            "exam_id": self.exam_id,
            "exam_name": self.exam.name,
            "exam_type": self.exam.exam_type,
            "course_code": self.exam.course.code,
            "max_marks": self.exam.max_marks,
            "results_published": self.exam.results_published,
            "slot_id": self.slot_id,
            "slot_date": self.slot.date.isoformat(),
            "start_time": self.slot.start_time.strftime("%H:%M"),
            "end_time": self.slot.end_time.strftime("%H:%M"),
            "examiner_name": self.slot.examiner.name,
            "booking_date": self.booking_date.strftime("%Y-%m-%d"),
            "status": self.status,
            "total_marks": self.total_marks,
            "remarks": self.remarks,
            # a student can cancel only until the booking deadline
            "can_cancel": self.status == "Booked" and date.today() <= self.exam.booking_end,
        }


# Marks given to one booking for one rubric criterion
class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey("rubric.id"), nullable=False)
    marks = db.Column(db.Integer, nullable=False)

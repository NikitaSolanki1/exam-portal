from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import current_user, verify_jwt_in_request
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from models import EXAM_STATUSES, EXAM_TYPES, Booking, Course, Exam, Rubric, Slot, User, db

admin = Blueprint("admin", __name__, url_prefix="/api/admin")


# Runs before every route in this file: only a logged-in admin may continue
@admin.before_request
def only_admin():
    if request.method == "OPTIONS":  # the browser's CORS check has no token, let it pass
        return
    verify_jwt_in_request()
    if current_user.role != "admin":
        return {"message": "Please log in as the admin."}, 401


@admin.get("/dashboard")
def dashboard():
    counts = [
        {"label": "Courses", "value": Course.query.count(), "icon": "bi-journal-bookmark"},
        {"label": "Examinations", "value": Exam.query.count(), "icon": "bi-clipboard-check"},
        {"label": "Examiners", "value": User.query.filter_by(role="examiner").count(), "icon": "bi-person-badge"},
        {"label": "Students", "value": User.query.filter_by(role="student").count(), "icon": "bi-people"},
        {"label": "Slots", "value": Slot.query.count(), "icon": "bi-calendar-week"},
        {"label": "Bookings", "value": Booking.query.count(), "icon": "bi-bookmark-check"},
    ]
    pending = User.query.filter_by(role="examiner", is_approved=False).all()
    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()
    return {
        "counts": counts,
        "pending": [user.to_dict() for user in pending],
        "recent_bookings": [b.to_dict() for b in recent_bookings],
    }


# ---------------- Courses ----------------

@admin.get("/courses")
def courses():
    all_courses = Course.query.order_by(Course.code).all()
    return {"courses": [course.to_dict() for course in all_courses]}


@admin.get("/courses/<int:course_id>")
def get_course(course_id):
    course = db.get_or_404(Course, course_id)
    return {"course": course.to_dict()}


# POST adds a new course, PUT edits an old one
@admin.post("/courses")
@admin.put("/courses/<int:course_id>")
def save_course(course_id=None):
    course = db.get_or_404(Course, course_id) if course_id else Course()
    data = request.get_json()
    code = data["code"].strip().upper()
    same_code = Course.query.filter_by(code=code).first()
    if same_code and same_code.id != course.id:
        return {"message": "A course with this code already exists."}, 400

    course.code = code
    course.name = data["name"]
    course.description = data.get("description")
    course.status = data["status"]
    db.session.add(course)
    db.session.commit()
    return {"message": "Course saved."}


@admin.delete("/courses/<int:course_id>")
def delete_course(course_id):
    course = db.get_or_404(Course, course_id)
    db.session.delete(course)  # its exams, slots and bookings are deleted too
    db.session.commit()
    return {"message": "Course deleted."}


# ---------------- Examinations ----------------

@admin.get("/exams")
def exams():
    q = request.args.get("q", "").strip()
    query = Exam.query.join(Course)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Exam.name.ilike(like), Course.name.ilike(like), Course.code.ilike(like), Exam.id == q))
    return {"exams": [exam.to_dict() for exam in query.order_by(Exam.id.desc()).all()]}


# The lists the "add / edit exam" form needs for its drop-downs
@admin.get("/exam-form")
def exam_form_data():
    courses = Course.query.order_by(Course.code).all()
    examiners = User.query.filter_by(role="examiner", is_approved=True, is_active=True).all()
    return {
        "courses": [course.to_dict() for course in courses],
        "examiners": [user.to_dict() for user in examiners],
        "exam_types": EXAM_TYPES,
    }


# Everything the exam page shows: details, rubric, slots and bookings
@admin.get("/exams/<int:exam_id>")
def exam_detail(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    bookings = Booking.query.filter_by(exam_id=exam.id).order_by(Booking.id.desc()).all()
    return {
        "exam": exam.to_dict(),
        "rubrics": [rubric.to_dict() for rubric in exam.rubrics],
        "slots": [slot.to_dict() for slot in exam.slots],
        "bookings": [b.to_dict() for b in bookings],
    }


# POST adds a new exam, PUT edits an old one
@admin.post("/exams")
@admin.put("/exams/<int:exam_id>")
def save_exam(exam_id=None):
    exam = db.get_or_404(Exam, exam_id) if exam_id else Exam()
    data = request.get_json()
    slot_start = date.fromisoformat(data["slot_start"])
    slot_end = date.fromisoformat(data["slot_end"])
    booking_start = date.fromisoformat(data["booking_start"])
    booking_end = date.fromisoformat(data["booking_end"])
    if slot_start > slot_end or booking_start > booking_end:
        return {"message": "Each start date must be on or before its end date."}, 400
    if booking_start < slot_start:
        return {"message": "Booking cannot start before slot creation starts."}, 400

    exam.course_id = int(data["course_id"])
    exam.examiner_id = int(data["examiner_id"])
    exam.name = data["name"]
    exam.exam_type = data["exam_type"]
    exam.duration = int(data["duration"])
    exam.max_marks = int(data["max_marks"])
    exam.slot_start = slot_start
    exam.slot_end = slot_end
    exam.booking_start = booking_start
    exam.booking_end = booking_end
    # If the admin changes the examiner, the old slots move to the new examiner
    for slot in exam.slots:
        slot.examiner_id = exam.examiner_id
    db.session.add(exam)
    db.session.commit()
    return {"message": "Examination saved.", "id": exam.id}


# Open / close slot creation and booking, or mark the exam completed
@admin.put("/exams/<int:exam_id>/status")
def change_exam_status(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    new_status = request.get_json()["status"]
    if new_status not in EXAM_STATUSES:
        return {"message": "Unknown status."}, 400
    if new_status == "Booking Open" and not exam.slots:
        return {"message": "The examiner has not created any slots yet, so booking cannot open."}, 400

    exam.status = new_status
    db.session.commit()
    return {"message": f"Exam status is now: {new_status}."}


@admin.put("/exams/<int:exam_id>/publish")
def publish_results(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    exam.results_published = not exam.results_published
    db.session.commit()
    if exam.results_published:
        return {"message": "Results published to students."}
    return {"message": "Results hidden from students."}


@admin.delete("/exams/<int:exam_id>")
def delete_exam(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    db.session.delete(exam)  # its rubrics, slots and bookings are deleted too
    db.session.commit()
    return {"message": "Examination deleted."}


# ---------------- Rubrics ----------------

@admin.post("/exams/<int:exam_id>/rubrics")
def add_rubric(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    data = request.get_json()
    max_marks = int(data["max_marks"])
    used = sum(rubric.max_marks for rubric in exam.rubrics)
    if max_marks < 1:
        return {"message": "Marks must be at least 1."}, 400
    if used + max_marks > exam.max_marks:
        return {"message": f"Rubric marks cannot go over the exam's {exam.max_marks} marks ({used} already used)."}, 400

    rubric = Rubric(
        exam_id=exam.id,
        criterion=data["criterion"],
        max_marks=max_marks,
        weightage=round(max_marks * 100 / exam.max_marks, 1),
        description=data.get("description"),
    )
    db.session.add(rubric)
    db.session.commit()
    return {"message": "Rubric criterion added."}


@admin.delete("/rubrics/<int:rubric_id>")
def delete_rubric(rubric_id):
    rubric = db.get_or_404(Rubric, rubric_id)
    if rubric.marks:
        return {"message": "This criterion is already used in evaluations, so it cannot be deleted."}, 400
    db.session.delete(rubric)
    db.session.commit()
    return {"message": "Rubric criterion deleted."}


# ---------------- Examiners and students ----------------

@admin.get("/examiners")
def examiners():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="examiner")
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like), User.department.ilike(like), User.id == q))
    return {"examiners": [user.to_dict() for user in query.all()]}


# The admin adds an examiner directly (no approval needed)
@admin.post("/examiners")
def add_examiner():
    data = request.get_json()
    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return {"message": "This email is already registered."}, 400

    user = User(
        name=data["name"],
        email=email,
        password=generate_password_hash(data["password"], method="pbkdf2:sha256"),
        role="examiner",
        phone=data.get("phone"),
        department=data.get("department"),
        is_approved=True,
    )
    db.session.add(user)
    db.session.commit()
    return {"message": "Examiner added."}


@admin.put("/examiners/<int:user_id>/approve")
def approve_examiner(user_id):
    user = db.get_or_404(User, user_id)
    user.is_approved = True
    db.session.commit()
    return {"message": f"{user.name} can now log in."}


# Deactivate or activate an examiner or a student
@admin.put("/users/<int:user_id>/toggle")
def toggle_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.role == "admin":
        return {"message": "The admin cannot be deactivated."}, 400
    user.is_active = not user.is_active
    db.session.commit()
    return {"message": f"{user.name} is now {'active' if user.is_active else 'deactivated'}."}


@admin.get("/students")
def students():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="student")
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like), User.department.ilike(like), User.id == q))
    return {"students": [user.to_dict() for user in query.all()]}


# ---------------- Slots and bookings ----------------

@admin.get("/slots")
def slots():
    all_slots = Slot.query.order_by(Slot.date, Slot.start_time).all()
    return {"slots": [slot.to_dict() for slot in all_slots]}


@admin.get("/bookings")
def bookings():
    q = request.args.get("q", "").strip()
    query = Booking.query.join(User, Booking.student_id == User.id).join(Exam, Booking.exam_id == Exam.id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like), Exam.name.ilike(like), Booking.id == q))
    return {"bookings": [b.to_dict() for b in query.order_by(Booking.id.desc()).all()]}


# The other free slots of the same exam, so the admin can pick one
@admin.get("/bookings/<int:booking_id>/reschedule")
def reschedule_options(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    free_slots = Slot.query.filter(
        Slot.exam_id == booking.exam_id,
        Slot.id != booking.slot_id,
        Slot.status == "Available",
        Slot.available_seats > 0,
    ).order_by(Slot.date, Slot.start_time).all()
    return {"booking": booking.to_dict(), "free_slots": [slot.to_dict() for slot in free_slots]}


# Move a booking to another free slot of the same exam
@admin.put("/bookings/<int:booking_id>/reschedule")
def reschedule(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    new_slot = db.get_or_404(Slot, int(request.get_json()["slot_id"]))
    if booking.status != "Booked":
        return {"message": "Only active bookings can be rescheduled."}, 400
    if new_slot.exam_id != booking.exam_id or new_slot.id == booking.slot_id:
        return {"message": "Please pick another slot of the same exam."}, 400
    if new_slot.status != "Available" or new_slot.available_seats < 1:
        return {"message": "That slot is not free any more."}, 400

    old_slot = booking.slot
    old_slot.available_seats += 1
    old_slot.status = "Available"
    new_slot.available_seats -= 1
    if new_slot.available_seats == 0:
        new_slot.status = "Full"
    booking.slot = new_slot
    db.session.commit()
    return {"message": "Booking rescheduled."}


@admin.put("/bookings/<int:booking_id>/cancel")
def cancel_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.status != "Booked":
        return {"message": "Only active bookings can be cancelled."}, 400
    booking.status = "Cancelled"
    booking.slot.available_seats += 1
    booking.slot.status = "Available"
    db.session.commit()
    return {"message": "Booking cancelled."}

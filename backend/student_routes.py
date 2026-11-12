from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import current_user, verify_jwt_in_request
from sqlalchemy import or_

from models import EXAM_TYPES, Booking, Course, Exam, Slot, db

student = Blueprint("student", __name__, url_prefix="/api/student")


# Runs before every route in this file: only a logged-in, active student may continue
@student.before_request
def only_student():
    if request.method == "OPTIONS":  # the browser's CORS check has no token, let it pass
        return
    verify_jwt_in_request()
    if current_user.role != "student" or not current_user.is_active:
        return {"message": "Please log in as a student."}, 401


@student.get("/dashboard")
def dashboard():
    today = date.today()
    my_bookings = Booking.query.filter_by(student_id=current_user.id).all()
    upcoming = Booking.query.join(Slot).filter(Booking.student_id == current_user.id, Booking.status == "Booked",
                                               Slot.date >= today).order_by(Slot.date, Slot.start_time).all()
    results = [b for b in my_bookings if b.status == "Completed" and b.exam.results_published]
    open_exams = Exam.query.filter_by(status="Booking Open").all()
    free_slots = Slot.query.join(Exam).filter(Exam.status == "Booking Open", Slot.status == "Available",
                                               Slot.date >= today).count()
    booked_count = len([b for b in my_bookings if b.status == "Booked"])
    return {
        "upcoming": [b.to_dict() for b in upcoming],
        "results": [b.to_dict() for b in results],
        "open_exams": [exam.to_dict() for exam in open_exams],
        "free_slots": free_slots,
        "booked_count": booked_count,
    }


# All exams with search and filters
@student.get("/exams")
def exams():
    q = request.args.get("q", "").strip()
    exam_type = request.args.get("type", "")
    course_id = request.args.get("course", "")

    query = Exam.query.join(Course).filter(Exam.status != "Draft")  # draft exams are hidden from students
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Exam.name.ilike(like), Course.name.ilike(like), Course.code.ilike(like)))
    if exam_type:
        query = query.filter(Exam.exam_type == exam_type)
    if course_id:
        query = query.filter(Exam.course_id == int(course_id))

    # ids of exams this student has already booked
    booked_ids = [b.exam_id for b in current_user.bookings if b.status != "Cancelled"]
    return {
        "exams": [exam.to_dict() for exam in query.all()],
        "courses": [course.to_dict() for course in Course.query.all()],
        "exam_types": EXAM_TYPES,
        "booked_ids": booked_ids,
    }


# One exam and its slots
@student.get("/exams/<int:exam_id>")
def exam_slots(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    if exam.status == "Draft":
        return {"message": "This exam is not open yet."}, 404
    my_booking = Booking.query.filter(Booking.student_id == current_user.id, Booking.exam_id == exam.id,
                                      Booking.status != "Cancelled").first()
    return {
        "exam": exam.to_dict(),
        "slots": [slot.to_dict() for slot in exam.slots],
        "my_booking": my_booking.to_dict() if my_booking else None,
        "booking_open": exam.status == "Booking Open" and date.today() <= exam.booking_end,
        "today": date.today().isoformat(),
    }


@student.post("/slots/<int:slot_id>/book")
def book_slot(slot_id):
    slot = db.get_or_404(Slot, slot_id)
    exam = slot.exam
    already_booked = Booking.query.filter(Booking.student_id == current_user.id, Booking.exam_id == exam.id,
                                          Booking.status != "Cancelled").first()
    if exam.status != "Booking Open" or date.today() > exam.booking_end:
        return {"message": "Booking is not open for this exam."}, 400
    if already_booked:
        return {"message": "You already have a booking for this exam. Only one booking per exam is allowed."}, 400
    if slot.date < date.today():
        return {"message": "This slot is already over."}, 400
    if slot.status != "Available" or slot.available_seats < 1:
        return {"message": "Sorry, this slot is full."}, 400

    booking = Booking(student_id=current_user.id, slot_id=slot.id, exam_id=exam.id)
    db.session.add(booking)
    slot.available_seats -= 1
    if slot.available_seats == 0:
        slot.status = "Full"  # close the slot automatically when it is full
    db.session.commit()
    return {"message": "Slot booked! You can see it under My Bookings."}


# Booking history, newest first
@student.get("/bookings")
def bookings():
    my_bookings = Booking.query.filter_by(student_id=current_user.id).order_by(Booking.id.desc()).all()
    result = []
    for b in my_bookings:
        booking_data = b.to_dict()
        if not b.exam.results_published:  # hide marks until the admin publishes them
            booking_data["total_marks"] = None
            booking_data["remarks"] = None
        result.append(booking_data)
    return {"bookings": result}


@student.put("/bookings/<int:booking_id>/cancel")
def cancel_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.student_id != current_user.id or booking.status != "Booked":
        return {"message": "You cannot cancel this booking."}, 400
    if date.today() > booking.exam.booking_end:
        return {"message": "The booking deadline has passed, so this booking cannot be cancelled."}, 400

    booking.status = "Cancelled"
    booking.slot.available_seats += 1
    booking.slot.status = "Available"
    db.session.commit()
    return {"message": "Booking cancelled."}


# Only results that the admin has published, with marks for each criterion
@student.get("/results")
def results():
    my_results = Booking.query.join(Exam, Booking.exam_id == Exam.id).filter(
        Booking.student_id == current_user.id,
        Booking.status == "Completed",
        Exam.results_published == True,
    ).all()

    result = []
    for b in my_results:
        booking_data = b.to_dict()
        booking_data["marks"] = [
            {"criterion": mark.rubric.criterion, "marks": mark.marks, "max_marks": mark.rubric.max_marks}
            for mark in b.marks
        ]
        result.append(booking_data)
    return {"results": result}

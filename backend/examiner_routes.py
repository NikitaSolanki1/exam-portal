from datetime import date, time

from flask import Blueprint, request
from flask_jwt_extended import current_user, verify_jwt_in_request

from models import Booking, Exam, Mark, Slot, db

examiner = Blueprint("examiner", __name__, url_prefix="/api/examiner")


# Runs before every route in this file: only a logged-in, active examiner may continue
@examiner.before_request
def only_examiner():
    if request.method == "OPTIONS":  # the browser's CORS check has no token, let it pass
        return
    verify_jwt_in_request()
    if current_user.role != "examiner" or not current_user.is_active:
        return {"message": "Please log in as an examiner."}, 401


@examiner.get("/dashboard")
def dashboard():
    exams = Exam.query.filter_by(examiner_id=current_user.id).all()
    slot_count = Slot.query.filter_by(examiner_id=current_user.id).count()
    my_bookings = Booking.query.join(Slot).filter(Slot.examiner_id == current_user.id, Booking.status != "Cancelled").all()
    pending = [b for b in my_bookings if b.status == "Booked"]  # booked but not evaluated yet
    return {
        "exams": [exam.to_dict() for exam in exams],
        "slot_count": slot_count,
        "booked_count": len(my_bookings),
        "pending": [b.to_dict() for b in pending],
    }


# One exam: its slots, and the students booked into each slot
@examiner.get("/exams/<int:exam_id>")
def exam_page(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    if exam.examiner_id != current_user.id:
        return {"message": "This exam is not assigned to you."}, 403

    slots = []
    for slot in exam.slots:
        slot_data = slot.to_dict()
        slot_data["bookings"] = [b.to_dict() for b in slot.bookings if b.status != "Cancelled"]
        slots.append(slot_data)

    return {
        "exam": exam.to_dict(),
        "slots": slots,
        # Slots can be created only while the admin has opened slot creation, and before it ends
        "can_create": exam.status == "Slot Creation" and date.today() <= exam.slot_end,
        "today": date.today().isoformat(),
    }


@examiner.post("/exams/<int:exam_id>/slots")
def create_slot(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    data = request.get_json()
    slot_date = date.fromisoformat(data["date"])
    start_time = time.fromisoformat(data["start_time"])
    end_time = time.fromisoformat(data["end_time"])
    capacity = int(data["capacity"])

    if exam.examiner_id != current_user.id:
        return {"message": "This exam is not assigned to you."}, 403
    if exam.status != "Slot Creation" or date.today() > exam.slot_end:
        return {"message": "Slot creation is closed for this exam."}, 400
    if slot_date < date.today():
        return {"message": "The slot date cannot be in the past."}, 400
    if start_time >= end_time:
        return {"message": "The end time must be after the start time."}, 400
    if capacity < 1:
        return {"message": "Capacity must be at least 1."}, 400

    slot = Slot(exam_id=exam.id, examiner_id=current_user.id, date=slot_date, start_time=start_time,
                end_time=end_time, capacity=capacity, available_seats=capacity)
    db.session.add(slot)
    db.session.commit()
    return {"message": "Slot created."}


@examiner.get("/slots/<int:slot_id>")
def get_slot(slot_id):
    slot = db.get_or_404(Slot, slot_id)
    if slot.examiner_id != current_user.id:
        return {"message": "This is not your slot."}, 403
    return {"slot": slot.to_dict()}


# Slots can be changed or removed only before booking starts and if nobody has booked them
@examiner.put("/slots/<int:slot_id>")
def edit_slot(slot_id):
    slot = db.get_or_404(Slot, slot_id)
    data = request.get_json()
    start_time = time.fromisoformat(data["start_time"])
    end_time = time.fromisoformat(data["end_time"])

    if slot.examiner_id != current_user.id:
        return {"message": "This is not your slot."}, 403
    if slot.exam.status not in ["Draft", "Slot Creation"] or slot.bookings:
        return {"message": "Booking has started for this slot, so it cannot be changed."}, 400
    if start_time >= end_time:
        return {"message": "The end time must be after the start time."}, 400
    if int(data["capacity"]) < 1:
        return {"message": "Capacity must be at least 1."}, 400

    slot.date = date.fromisoformat(data["date"])
    slot.start_time = start_time
    slot.end_time = end_time
    slot.capacity = int(data["capacity"])
    slot.available_seats = slot.capacity
    db.session.commit()
    return {"message": "Slot updated."}


@examiner.delete("/slots/<int:slot_id>")
def delete_slot(slot_id):
    slot = db.get_or_404(Slot, slot_id)
    if slot.examiner_id != current_user.id:
        return {"message": "This is not your slot."}, 403
    if slot.exam.status not in ["Draft", "Slot Creation"] or slot.bookings:
        return {"message": "Booking has started for this slot, so it cannot be removed."}, 400

    db.session.delete(slot)
    db.session.commit()
    return {"message": "Slot removed."}


# The evaluation form: the student, the rubric, and any marks given before
@examiner.get("/bookings/<int:booking_id>/evaluate")
def evaluation_form(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    # Examiners can evaluate only students booked into their own slots
    if booking.slot.examiner_id != current_user.id or booking.status == "Cancelled":
        return {"message": "You cannot evaluate this booking."}, 403

    old_marks = {}
    for mark in booking.marks:
        old_marks[mark.rubric_id] = mark.marks
    return {
        "booking": booking.to_dict(),
        "rubrics": [rubric.to_dict() for rubric in booking.exam.rubrics],
        "old_marks": old_marks,
    }


# Save marks for each rubric criterion, plus remarks
@examiner.post("/bookings/<int:booking_id>/evaluate")
def evaluate(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    exam = booking.exam
    data = request.get_json()
    if booking.slot.examiner_id != current_user.id or booking.status == "Cancelled":
        return {"message": "You cannot evaluate this booking."}, 403
    if not exam.rubrics:
        return {"message": "The admin has not added a rubric for this exam yet."}, 400

    for old_mark in booking.marks:  # remove old marks if this is a re-evaluation
        db.session.delete(old_mark)
    total = 0
    for rubric in exam.rubrics:
        marks = int(data["marks"][str(rubric.id)])  # JSON keys are always text
        marks = max(0, min(marks, rubric.max_marks))  # keep marks between 0 and the maximum
        db.session.add(Mark(booking_id=booking.id, rubric_id=rubric.id, marks=marks))
        total += marks
    booking.total_marks = total
    booking.remarks = data["remarks"]
    booking.status = "Completed"
    # The slot is completed when none of its students are left to evaluate
    if not [b for b in booking.slot.bookings if b.status == "Booked"]:
        booking.slot.status = "Completed"
    db.session.commit()
    return {"message": f"Marks saved for {booking.student.name}: {total} / {exam.max_marks}."}

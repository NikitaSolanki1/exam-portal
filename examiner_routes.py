from datetime import date, time

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from models import Booking, Exam, Mark, Slot, db

examiner = Blueprint("examiner", __name__, url_prefix="/examiner")


# Every page in this file is for examiners only
@examiner.before_request
def only_examiner():
    if not current_user.is_authenticated or current_user.role != "examiner":
        flash("Please log in as an examiner.", "warning")
        return redirect(url_for("login"))


@examiner.route("/")
def dashboard():
    exams = Exam.query.filter_by(examiner_id=current_user.id).all()
    my_slots = Slot.query.filter_by(examiner_id=current_user.id).all()
    my_bookings = Booking.query.join(Slot).filter(Slot.examiner_id == current_user.id, Booking.status != "Cancelled").all()
    pending = [b for b in my_bookings if b.status == "Booked"]  # booked but not evaluated yet
    return render_template("examiner/dashboard.html", exams=exams, slot_count=len(my_slots),
                           booked_count=len(my_bookings), pending=pending)


# One exam: create slots and see the students booked into them
@examiner.route("/exams/<int:exam_id>", methods=["GET", "POST"])
def exam_page(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    if exam.examiner_id != current_user.id:
        flash("This exam is not assigned to you.", "danger")
        return redirect(url_for("examiner.dashboard"))

    # Slots can be created only while the admin has opened slot creation, and before it ends
    can_create = exam.status == "Slot Creation" and date.today() <= exam.slot_end

    if request.method == "POST":
        slot_date = date.fromisoformat(request.form["date"])
        start_time = time.fromisoformat(request.form["start_time"])
        end_time = time.fromisoformat(request.form["end_time"])
        capacity = int(request.form["capacity"])
        if not can_create:
            flash("Slot creation is closed for this exam.", "danger")
        elif slot_date < date.today():
            flash("The slot date cannot be in the past.", "danger")
        elif start_time >= end_time:
            flash("The end time must be after the start time.", "danger")
        elif capacity < 1:
            flash("Capacity must be at least 1.", "danger")
        else:
            slot = Slot(exam_id=exam.id, examiner_id=current_user.id, date=slot_date, start_time=start_time,
                        end_time=end_time, capacity=capacity, available_seats=capacity)
            db.session.add(slot)
            db.session.commit()
            flash("Slot created.", "success")
        return redirect(url_for("examiner.exam_page", exam_id=exam.id))

    return render_template("examiner/exam.html", exam=exam, can_create=can_create, today=date.today())


# Slots can be changed or removed only before booking starts and if nobody has booked them
@examiner.route("/slots/<int:slot_id>/edit", methods=["GET", "POST"])
def edit_slot(slot_id):
    slot = db.get_or_404(Slot, slot_id)
    if slot.examiner_id != current_user.id:
        flash("This is not your slot.", "danger")
        return redirect(url_for("examiner.dashboard"))
    if slot.exam.status not in ["Draft", "Slot Creation"] or slot.bookings:
        flash("Booking has started for this slot, so it cannot be changed.", "warning")
        return redirect(url_for("examiner.exam_page", exam_id=slot.exam_id))

    if request.method == "POST":
        start_time = time.fromisoformat(request.form["start_time"])
        end_time = time.fromisoformat(request.form["end_time"])
        if start_time >= end_time:
            flash("The end time must be after the start time.", "danger")
        else:
            slot.date = date.fromisoformat(request.form["date"])
            slot.start_time = start_time
            slot.end_time = end_time
            slot.capacity = int(request.form["capacity"])
            slot.available_seats = slot.capacity
            db.session.commit()
            flash("Slot updated.", "success")
            return redirect(url_for("examiner.exam_page", exam_id=slot.exam_id))
    return render_template("examiner/slot_form.html", slot=slot)


@examiner.route("/slots/<int:slot_id>/delete", methods=["POST"])
def delete_slot(slot_id):
    slot = db.get_or_404(Slot, slot_id)
    exam_id = slot.exam_id
    if slot.examiner_id != current_user.id:
        flash("This is not your slot.", "danger")
    elif slot.exam.status not in ["Draft", "Slot Creation"] or slot.bookings:
        flash("Booking has started for this slot, so it cannot be removed.", "warning")
    else:
        db.session.delete(slot)
        db.session.commit()
        flash("Slot removed.", "success")
    return redirect(url_for("examiner.exam_page", exam_id=exam_id))


# Give marks for each rubric criterion, plus remarks
@examiner.route("/bookings/<int:booking_id>/evaluate", methods=["GET", "POST"])
def evaluate(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    exam = booking.exam
    # Examiners can evaluate only students booked into their own slots
    if booking.slot.examiner_id != current_user.id or booking.status == "Cancelled":
        flash("You cannot evaluate this booking.", "danger")
        return redirect(url_for("examiner.dashboard"))
    if not exam.rubrics:
        flash("The admin has not added a rubric for this exam yet.", "warning")
        return redirect(url_for("examiner.exam_page", exam_id=exam.id))

    if request.method == "POST":
        for old_mark in booking.marks:  # remove old marks if this is a re-evaluation
            db.session.delete(old_mark)
        total = 0
        for rubric in exam.rubrics:
            marks = int(request.form[f"rubric_{rubric.id}"])
            marks = max(0, min(marks, rubric.max_marks))  # keep marks between 0 and the maximum
            db.session.add(Mark(booking_id=booking.id, rubric_id=rubric.id, marks=marks))
            total += marks
        booking.total_marks = total
        booking.remarks = request.form["remarks"]
        booking.status = "Completed"
        # The slot is completed when none of its students are left to evaluate
        if not [b for b in booking.slot.bookings if b.status == "Booked"]:
            booking.slot.status = "Completed"
        db.session.commit()
        flash(f"Marks saved for {booking.student.name}: {total} / {exam.max_marks}.", "success")
        return redirect(url_for("examiner.exam_page", exam_id=exam.id))

    old_marks = {mark.rubric_id: mark.marks for mark in booking.marks}
    return render_template("examiner/evaluate.html", booking=booking, exam=exam, old_marks=old_marks)

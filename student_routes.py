from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import or_

from models import EXAM_TYPES, Booking, Course, Exam, Slot, db

student = Blueprint("student", __name__, url_prefix="/student")


# Every page in this file is for students only
@student.before_request
def only_student():
    if not current_user.is_authenticated or current_user.role != "student":
        flash("Please log in as a student.", "warning")
        return redirect(url_for("login"))


@student.route("/")
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
    return render_template("student/dashboard.html", upcoming=upcoming, results=results, open_exams=open_exams,
                           free_slots=free_slots, booked_count=booked_count)


# All exams with search and filters
@student.route("/exams")
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
    return render_template("student/exams.html", exams=query.all(), courses=Course.query.all(), exam_types=EXAM_TYPES,
                           q=q, exam_type=exam_type, course_id=course_id, booked_ids=booked_ids)


# One exam and its slots
@student.route("/exams/<int:exam_id>")
def exam_slots(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    my_booking = Booking.query.filter(Booking.student_id == current_user.id, Booking.exam_id == exam.id,
                                      Booking.status != "Cancelled").first()
    booking_open = exam.status == "Booking Open" and date.today() <= exam.booking_end
    return render_template("student/exam_slots.html", exam=exam, my_booking=my_booking,
                           booking_open=booking_open, today=date.today())


@student.route("/slots/<int:slot_id>/book", methods=["POST"])
def book_slot(slot_id):
    slot = db.get_or_404(Slot, slot_id)
    exam = slot.exam
    already_booked = Booking.query.filter(Booking.student_id == current_user.id, Booking.exam_id == exam.id,
                                          Booking.status != "Cancelled").first()
    if exam.status != "Booking Open" or date.today() > exam.booking_end:
        flash("Booking is not open for this exam.", "danger")
    elif already_booked:
        flash("You already have a booking for this exam. Only one booking per exam is allowed.", "warning")
    elif slot.date < date.today():
        flash("This slot is already over.", "danger")
    elif slot.status != "Available" or slot.available_seats < 1:
        flash("Sorry, this slot is full.", "danger")
    else:
        booking = Booking(student_id=current_user.id, slot_id=slot.id, exam_id=exam.id)
        db.session.add(booking)
        slot.available_seats -= 1
        if slot.available_seats == 0:
            slot.status = "Full"  # close the slot automatically when it is full
        db.session.commit()
        flash("Slot booked! You can see it under My Bookings.", "success")
    return redirect(url_for("student.exam_slots", exam_id=exam.id))


# Booking history, newest first
@student.route("/bookings")
def bookings():
    my_bookings = Booking.query.filter_by(student_id=current_user.id).order_by(Booking.id.desc()).all()
    return render_template("student/bookings.html", bookings=my_bookings, today=date.today())


@student.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.student_id != current_user.id or booking.status != "Booked":
        flash("You cannot cancel this booking.", "danger")
    elif date.today() > booking.exam.booking_end:
        flash("The booking deadline has passed, so this booking cannot be cancelled.", "danger")
    else:
        booking.status = "Cancelled"
        booking.slot.available_seats += 1
        booking.slot.status = "Available"
        db.session.commit()
        flash("Booking cancelled.", "success")
    return redirect(url_for("student.bookings"))


# Only results that the admin has published
@student.route("/results")
def results():
    my_results = Booking.query.join(Exam, Booking.exam_id == Exam.id).filter(
        Booking.student_id == current_user.id,
        Booking.status == "Completed",
        Exam.results_published == True,
    ).all()
    return render_template("student/results.html", results=my_results)

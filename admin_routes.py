from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from models import EXAM_STATUSES, EXAM_TYPES, Booking, Course, Exam, Rubric, Slot, User, db

admin = Blueprint("admin", __name__, url_prefix="/admin")


# Every page in this file is for the admin only
@admin.before_request
def only_admin():
    if not current_user.is_authenticated or current_user.role != "admin":
        flash("Please log in as the admin.", "warning")
        return redirect(url_for("login"))


@admin.route("/")
def dashboard():
    counts = [
        ("Courses", Course.query.count(), "bi-journal-bookmark"),
        ("Examinations", Exam.query.count(), "bi-clipboard-check"),
        ("Examiners", User.query.filter_by(role="examiner").count(), "bi-person-badge"),
        ("Students", User.query.filter_by(role="student").count(), "bi-people"),
        ("Slots", Slot.query.count(), "bi-calendar-week"),
        ("Bookings", Booking.query.count(), "bi-bookmark-check"),
    ]
    pending = User.query.filter_by(role="examiner", is_approved=False).all()
    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()
    return render_template("admin/dashboard.html", counts=counts, pending=pending, recent_bookings=recent_bookings)


# ---------------- Courses ----------------

@admin.route("/courses")
def courses():
    return render_template("admin/courses.html", courses=Course.query.order_by(Course.code).all())


# The same page is used to add a new course and to edit an old one
@admin.route("/courses/add", methods=["GET", "POST"])
@admin.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
def course_form(course_id=None):
    course = db.get_or_404(Course, course_id) if course_id else Course()
    if request.method == "POST":
        code = request.form["code"].strip().upper()
        same_code = Course.query.filter_by(code=code).first()
        if same_code and same_code.id != course.id:
            flash("A course with this code already exists.", "danger")
        else:
            course.code = code
            course.name = request.form["name"]
            course.description = request.form["description"]
            course.status = request.form["status"]
            db.session.add(course)
            db.session.commit()
            flash("Course saved.", "success")
            return redirect(url_for("admin.courses"))
    return render_template("admin/course_form.html", course=course)


@admin.route("/courses/<int:course_id>/delete", methods=["POST"])
def delete_course(course_id):
    course = db.get_or_404(Course, course_id)
    db.session.delete(course)  # its exams, slots and bookings are deleted too
    db.session.commit()
    flash("Course deleted.", "success")
    return redirect(url_for("admin.courses"))


# ---------------- Examinations ----------------

@admin.route("/exams")
def exams():
    q = request.args.get("q", "").strip()
    query = Exam.query.join(Course)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Exam.name.ilike(like), Course.name.ilike(like), Course.code.ilike(like), Exam.id == q))
    return render_template("admin/exams.html", exams=query.order_by(Exam.id.desc()).all(), q=q)


# The same page is used to add a new exam and to edit an old one
@admin.route("/exams/add", methods=["GET", "POST"])
@admin.route("/exams/<int:exam_id>/edit", methods=["GET", "POST"])
def exam_form(exam_id=None):
    exam = db.get_or_404(Exam, exam_id) if exam_id else Exam()
    if request.method == "POST":
        slot_start = date.fromisoformat(request.form["slot_start"])
        slot_end = date.fromisoformat(request.form["slot_end"])
        booking_start = date.fromisoformat(request.form["booking_start"])
        booking_end = date.fromisoformat(request.form["booking_end"])
        if slot_start > slot_end or booking_start > booking_end:
            flash("Each start date must be on or before its end date.", "danger")
        elif booking_start < slot_start:
            flash("Booking cannot start before slot creation starts.", "danger")
        else:
            exam.course_id = int(request.form["course_id"])
            exam.examiner_id = int(request.form["examiner_id"])
            exam.name = request.form["name"]
            exam.exam_type = request.form["exam_type"]
            exam.duration = int(request.form["duration"])
            exam.max_marks = int(request.form["max_marks"])
            exam.slot_start = slot_start
            exam.slot_end = slot_end
            exam.booking_start = booking_start
            exam.booking_end = booking_end
            # If the admin changes the examiner, the old slots move to the new examiner
            for slot in exam.slots:
                slot.examiner_id = exam.examiner_id
            db.session.add(exam)
            db.session.commit()
            flash("Examination saved.", "success")
            return redirect(url_for("admin.exam_detail", exam_id=exam.id))
    courses = Course.query.order_by(Course.code).all()
    examiners = User.query.filter_by(role="examiner", is_approved=True, is_active=True).all()
    return render_template("admin/exam_form.html", exam=exam, courses=courses, examiners=examiners, exam_types=EXAM_TYPES)


@admin.route("/exams/<int:exam_id>")
def exam_detail(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    bookings = Booking.query.filter_by(exam_id=exam.id).order_by(Booking.id.desc()).all()
    return render_template("admin/exam_detail.html", exam=exam, bookings=bookings)


# Open / close slot creation and booking, or mark the exam completed
@admin.route("/exams/<int:exam_id>/status", methods=["POST"])
def change_exam_status(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    new_status = request.form["status"]
    if new_status == "Booking Open" and not exam.slots:
        flash("The examiner has not created any slots yet, so booking cannot open.", "warning")
    elif new_status in EXAM_STATUSES:
        exam.status = new_status
        db.session.commit()
        flash(f"Exam status is now: {new_status}.", "success")
    return redirect(url_for("admin.exam_detail", exam_id=exam.id))


@admin.route("/exams/<int:exam_id>/publish", methods=["POST"])
def publish_results(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    exam.results_published = not exam.results_published
    db.session.commit()
    flash("Results published to students." if exam.results_published else "Results hidden from students.", "success")
    return redirect(url_for("admin.exam_detail", exam_id=exam.id))


@admin.route("/exams/<int:exam_id>/delete", methods=["POST"])
def delete_exam(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    db.session.delete(exam)  # its rubrics, slots and bookings are deleted too
    db.session.commit()
    flash("Examination deleted.", "success")
    return redirect(url_for("admin.exams"))


# ---------------- Rubrics ----------------

@admin.route("/exams/<int:exam_id>/rubrics/add", methods=["POST"])
def add_rubric(exam_id):
    exam = db.get_or_404(Exam, exam_id)
    max_marks = int(request.form["max_marks"])
    used = sum(rubric.max_marks for rubric in exam.rubrics)
    if used + max_marks > exam.max_marks:
        flash(f"Rubric marks cannot go over the exam's {exam.max_marks} marks ({used} already used).", "danger")
    else:
        rubric = Rubric(
            exam_id=exam.id,
            criterion=request.form["criterion"],
            max_marks=max_marks,
            weightage=round(max_marks * 100 / exam.max_marks, 1),
            description=request.form["description"],
        )
        db.session.add(rubric)
        db.session.commit()
        flash("Rubric criterion added.", "success")
    return redirect(url_for("admin.exam_detail", exam_id=exam.id))


@admin.route("/rubrics/<int:rubric_id>/delete", methods=["POST"])
def delete_rubric(rubric_id):
    rubric = db.get_or_404(Rubric, rubric_id)
    exam_id = rubric.exam_id
    if rubric.marks:
        flash("This criterion is already used in evaluations, so it cannot be deleted.", "danger")
    else:
        db.session.delete(rubric)
        db.session.commit()
        flash("Rubric criterion deleted.", "success")
    return redirect(url_for("admin.exam_detail", exam_id=exam_id))


# ---------------- Examiners and students ----------------

@admin.route("/examiners", methods=["GET", "POST"])
def examiners():
    if request.method == "POST":  # the admin adds an examiner directly
        email = request.form["email"].strip().lower()
        if User.query.filter_by(email=email).first():
            flash("This email is already registered.", "danger")
        else:
            user = User(
                name=request.form["name"],
                email=email,
                password=generate_password_hash(request.form["password"], method="pbkdf2:sha256"),
                role="examiner",
                phone=request.form["phone"],
                department=request.form["department"],
                is_approved=True,
            )
            db.session.add(user)
            db.session.commit()
            flash("Examiner added.", "success")
        return redirect(url_for("admin.examiners"))

    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="examiner")
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like), User.department.ilike(like), User.id == q))
    return render_template("admin/examiners.html", examiners=query.all(), q=q)


@admin.route("/examiners/<int:user_id>/approve", methods=["POST"])
def approve_examiner(user_id):
    user = db.get_or_404(User, user_id)
    user.is_approved = True
    db.session.commit()
    flash(f"{user.name} can now log in.", "success")
    return redirect(request.referrer or url_for("admin.examiners"))


# Deactivate or activate an examiner or a student
@admin.route("/users/<int:user_id>/toggle", methods=["POST"])
def toggle_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.role != "admin":
        user.is_active = not user.is_active
        db.session.commit()
        flash(f"{user.name} is now {'active' if user.is_active else 'deactivated'}.", "success")
    return redirect(request.referrer or url_for("admin.dashboard"))


@admin.route("/students")
def students():
    q = request.args.get("q", "").strip()
    query = User.query.filter_by(role="student")
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like), User.department.ilike(like), User.id == q))
    return render_template("admin/students.html", students=query.all(), q=q)


# ---------------- Slots and bookings ----------------

@admin.route("/slots")
def slots():
    return render_template("admin/slots.html", slots=Slot.query.order_by(Slot.date, Slot.start_time).all())


@admin.route("/bookings")
def bookings():
    q = request.args.get("q", "").strip()
    query = Booking.query.join(User, Booking.student_id == User.id).join(Exam, Booking.exam_id == Exam.id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like), Exam.name.ilike(like), Booking.id == q))
    return render_template("admin/bookings.html", bookings=query.order_by(Booking.id.desc()).all(), q=q)


# Move a booking to another free slot of the same exam
@admin.route("/bookings/<int:booking_id>/reschedule", methods=["GET", "POST"])
def reschedule(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.status != "Booked":
        flash("Only active bookings can be rescheduled.", "warning")
        return redirect(url_for("admin.bookings"))

    free_slots = Slot.query.filter(
        Slot.exam_id == booking.exam_id,
        Slot.id != booking.slot_id,
        Slot.status == "Available",
        Slot.available_seats > 0,
    ).order_by(Slot.date, Slot.start_time).all()

    if request.method == "POST":
        new_slot = db.get_or_404(Slot, int(request.form["slot_id"]))
        if new_slot not in free_slots:
            flash("That slot is not free any more.", "danger")
        else:
            old_slot = booking.slot
            old_slot.available_seats += 1
            old_slot.status = "Available"
            new_slot.available_seats -= 1
            if new_slot.available_seats == 0:
                new_slot.status = "Full"
            booking.slot = new_slot
            db.session.commit()
            flash("Booking rescheduled.", "success")
            return redirect(url_for("admin.bookings"))
    return render_template("admin/reschedule.html", booking=booking, free_slots=free_slots)


@admin.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.status == "Booked":
        booking.status = "Cancelled"
        booking.slot.available_seats += 1
        booking.slot.status = "Available"
        db.session.commit()
        flash("Booking cancelled.", "success")
    return redirect(request.referrer or url_for("admin.bookings"))

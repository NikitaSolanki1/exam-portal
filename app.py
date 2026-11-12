from datetime import date, timedelta

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

# Note: passwords are hashed with method="pbkdf2:sha256" because the Python that comes with macOS has no scrypt

from admin_routes import admin
from examiner_routes import examiner
from models import Course, Exam, Rubric, User, db
from student_routes import student

app = Flask(__name__)
app.config["SECRET_KEY"] = "exam-portal-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exam_portal.db"  # saved in the instance/ folder
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# The pages for each role live in their own file
app.register_blueprint(admin)
app.register_blueprint(examiner)
app.register_blueprint(student)


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for(current_user.role + ".dashboard"))
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"].strip().lower()).first()
        if not user or not check_password_hash(user.password, request.form["password"]):
            flash("Wrong email or password.", "danger")
        elif not user.is_approved:
            flash("Your account is waiting for admin approval.", "warning")
        elif not user.is_active:
            flash("Your account has been deactivated. Please contact the admin.", "danger")
        else:
            login_user(user)
            return redirect(url_for(user.role + ".dashboard"))
    return render_template("login.html")


# Only students and examiners can register. The admin already exists.
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        role = request.form["role"]
        if role not in ["student", "examiner"]:
            flash("Please choose Student or Examiner.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("This email is already registered.", "danger")
        else:
            user = User(
                name=request.form["name"],
                email=email,
                password=generate_password_hash(request.form["password"], method="pbkdf2:sha256"),
                role=role,
                phone=request.form["phone"],
                department=request.form["department"],
                is_approved=(role == "student"),  # examiners wait for the admin
            )
            db.session.add(user)
            db.session.commit()
            if role == "examiner":
                flash("Registered! You can log in after the admin approves your account.", "info")
            else:
                flash("Registered! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# Students and examiners can edit their own profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.name = request.form["name"]
        current_user.phone = request.form["phone"]
        current_user.department = request.form["department"]
        if request.form["password"]:
            current_user.password = generate_password_hash(request.form["password"], method="pbkdf2:sha256")
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html")


# Create the tables and the admin the first time the app runs.
# Also adds a few demo records so the app is not empty.
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        admin_user = User(name="Admin", email="admin@exam.com", password=generate_password_hash("admin123", method="pbkdf2:sha256"),
                          role="admin")
        demo_examiner = User(name="Dr. Meera Rao", email="examiner@exam.com",
                             password=generate_password_hash("examiner123", method="pbkdf2:sha256"),
                             role="examiner", phone="9876500001", department="Computer Science")
        demo_student = User(name="Arjun Sharma", email="student@exam.com",
                            password=generate_password_hash("student123", method="pbkdf2:sha256"),
                            role="student", phone="9876500002", department="Data Science")
        demo_course = Course(code="MAD1", name="Modern Application Development I",
                             description="Web apps with Flask, Jinja2 and SQLite")
        db.session.add_all([admin_user, demo_examiner, demo_student, demo_course])
        db.session.commit()

        demo_exam = Exam(course_id=demo_course.id, examiner_id=demo_examiner.id, name="Project Viva",
                         exam_type="Viva", duration=20, max_marks=20,
                         slot_start=date.today(), slot_end=date.today() + timedelta(days=7),
                         booking_start=date.today(), booking_end=date.today() + timedelta(days=14))
        db.session.add(demo_exam)
        db.session.commit()
        db.session.add_all([
            Rubric(exam_id=demo_exam.id, criterion="Concepts", max_marks=10, weightage=50, description="Explains how the app works"),
            Rubric(exam_id=demo_exam.id, criterion="Code walkthrough", max_marks=10, weightage=50, description="Can change the code live"),
        ])
        db.session.commit()


if __name__ == "__main__":
    # Port 5000 is used by AirPlay on macOS, so we use 5001
    app.run(debug=True, port=5001)

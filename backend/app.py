from datetime import date, timedelta

from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, current_user, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from admin_routes import admin
from examiner_routes import examiner
from models import Course, Exam, Rubric, User, db
from student_routes import student

# Note: passwords are hashed with method="pbkdf2:sha256" because the Python that comes with macOS has no scrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exam_portal.db"  # saved in the instance/ folder
app.config["JWT_SECRET_KEY"] = "exam-portal-jwt-secret-key-for-mad2-project"  # at least 32 characters
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)  # log in again after 12 hours
db.init_app(app)
jwt = JWTManager(app)
CORS(app)  # lets the Vue app (on port 5173) call this API (on port 5001)


# The token only stores the user's id. This tells JWT how to find the user,
# so we can use "current_user" in any route that needs a login.
@jwt.user_lookup_loader
def load_user(jwt_header, jwt_data):
    return db.session.get(User, int(jwt_data["sub"]))


# The API for each role lives in its own file
app.register_blueprint(admin)
app.register_blueprint(examiner)
app.register_blueprint(student)


@app.post("/api/login")
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"].strip().lower()).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return {"message": "Wrong email or password."}, 400
    if not user.is_approved:
        return {"message": "Your account is waiting for admin approval."}, 400
    if not user.is_active:
        return {"message": "Your account has been deactivated. Please contact the admin."}, 400

    token = create_access_token(identity=str(user.id))
    return {"token": token, "user": user.to_dict()}


# Only students and examiners can register. The admin already exists.
@app.post("/api/register")
def register():
    data = request.get_json()
    email = data["email"].strip().lower()
    role = data["role"]
    if role not in ["student", "examiner"]:
        return {"message": "Please choose Student or Examiner."}, 400
    if User.query.filter_by(email=email).first():
        return {"message": "This email is already registered."}, 400

    user = User(
        name=data["name"],
        email=email,
        password=generate_password_hash(data["password"], method="pbkdf2:sha256"),
        role=role,
        phone=data.get("phone"),
        department=data.get("department"),
        is_approved=(role == "student"),  # examiners wait for the admin
    )
    db.session.add(user)
    db.session.commit()
    if role == "examiner":
        return {"message": "Registered! You can log in after the admin approves your account."}
    return {"message": "Registered! Please log in."}


# Any logged-in user can see and edit their own profile
@app.get("/api/profile")
@jwt_required()
def get_profile():
    return {"user": current_user.to_dict()}


@app.put("/api/profile")
@jwt_required()
def update_profile():
    data = request.get_json()
    current_user.name = data["name"]
    current_user.phone = data.get("phone")
    current_user.department = data.get("department")
    if data.get("password"):
        current_user.password = generate_password_hash(data["password"], method="pbkdf2:sha256")
    db.session.commit()
    return {"message": "Profile updated.", "user": current_user.to_dict()}


# Create the tables and the admin the first time the app runs.
# Also adds a few demo records so the app is not empty.
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        admin_user = User(name="Admin", email="admin@exam.com",
                          password=generate_password_hash("admin123", method="pbkdf2:sha256"), role="admin")
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

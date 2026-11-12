# Examination Management Portal

A web app where an **Admin**, **Examiners** and **Students** manage examinations:
courses, exams, rubrics, slots, bookings, marks and results.

## Tech stack

| Part | Used |
| --- | --- |
| Backend | Flask (a JSON REST API) |
| Database | SQLite with Flask-SQLAlchemy |
| Login | Flask-JWT-Extended (token login) |
| Frontend | Vue 3 + Vite, Vue Router, Axios |
| Styling | Bootstrap 5 and Bootstrap Icons |

The Flask API runs on port **5001** and the Vue app on port **5173**.
Flask-CORS lets the Vue app call the API.

## How to run

You need **Python 3** and **Node.js 20 or newer** (from https://nodejs.org).

**1. Start the backend** (first terminal)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**2. Start the frontend** (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173 in your browser.

The database (`backend/instance/exam_portal.db`) is created by the code the first time the backend runs.
To start again with a fresh database, delete the `backend/instance` folder.

## Demo logins

These accounts are created on the first run (see the bottom of `backend/app.py`).

| Role     | Email             | Password    |
| -------- | ----------------- | ----------- |
| Admin    | admin@exam.com    | admin123    |
| Examiner | examiner@exam.com | examiner123 |
| Student  | student@exam.com  | student123  |

## How an exam works

1. **Admin** creates a course, then an exam with its dates, and assigns an examiner. Then admin adds the rubric (marking criteria).
2. **Admin** opens slot creation. The **examiner** creates slots (date, time, number of students).
3. **Admin** opens booking. **Students** book one slot per exam and can cancel before the booking deadline.
   A slot closes automatically when it is full.
4. **Examiner** gives marks for each rubric criterion and writes remarks.
5. **Admin** closes booking, marks the exam completed and publishes results. Students then see their marks and feedback.

The admin can reschedule a booking to another free slot, cancel bookings, and change the examiner at any time.

## How login works

1. The Vue login page sends the email and password to `POST /api/login`.
2. Flask checks them and sends back a **token** (JWT) and the user's details.
3. Vue saves the token in `localStorage`, and `src/api.js` sends it with every request.
4. Each Flask route file checks the token and the user's role before running (`before_request`).

## Project structure

```
backend/
  app.py               app setup, login, register, profile, first-run data
  models.py            database tables (each has a to_dict() to send it as JSON)
  admin_routes.py      admin API      (/api/admin/...)
  examiner_routes.py   examiner API   (/api/examiner/...)
  student_routes.py    student API    (/api/student/...)
  requirements.txt

frontend/
  index.html           loads Bootstrap and the Vue app
  src/main.js          starts Vue
  src/App.vue          navbar, messages, logout
  src/router.js        all the pages, and who can open them
  src/api.js           Axios set up to call Flask with the token
  src/style.css        a few styles on top of Bootstrap
  src/components/StatusBadge.vue   the coloured status labels
  src/views/           the pages (admin/, examiner/, student/)
```

## Database tables

- **User**: admin, examiners and students (the `role` column tells them apart)
- **Course**: code, name, description, status
- **Exam**: course, examiner, type, duration, maximum marks, slot creation and booking dates, status
- **Rubric**: one marking criterion of an exam (maximum marks, weightage)
- **Slot**: a time slot created by the examiner (date, time, capacity, seats left, status)
- **Booking**: a student's booking of a slot (status, total marks, remarks)
- **Mark**: marks for one rubric criterion of one booking

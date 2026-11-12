# Examination Management Portal (MAD-1)

A Flask web app where an **Admin**, **Examiners** and **Students** manage examinations:
courses, exams, rubrics, slots, bookings, marks and results.

Built with Flask, Jinja2, Bootstrap 5 and SQLite. No JavaScript is used.

## How to run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5001 in your browser.

The database (`instance/exam_portal.db`) is created by the code the first time the app runs.
To start again with a fresh database, delete the `instance` folder.

## Demo logins

These accounts are created on the first run (see the bottom of `app.py`).

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

## Project structure

```
app.py               app setup, login, register, profile, first-run data
models.py            database tables
admin_routes.py      admin pages
examiner_routes.py   examiner pages
student_routes.py    student pages
templates/           Jinja2 pages (admin/, examiner/, student/)
static/style.css     a few styles on top of Bootstrap
```

## Database tables

- **User**: admin, examiners and students (the `role` column tells them apart)
- **Course**: code, name, description, status
- **Exam**: course, examiner, type, duration, maximum marks, slot creation and booking dates, status
- **Rubric**: one marking criterion of an exam (maximum marks, weightage)
- **Slot**: a time slot created by the examiner (date, time, capacity, seats left, status)
- **Booking**: a student's booking of a slot (status, total marks, remarks)
- **Mark**: marks for one rubric criterion of one booking

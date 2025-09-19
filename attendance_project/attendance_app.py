from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Initial data
students = ["Aravindh", "Aswin", "Bhavana", "Gokul", "Hariharan", "Meenatchi", "Sivabarathi", "Visalstephenraj"]
courses = ["Software Engineering", "Maths", "Data Structure", "Hindhi", "Information Security", "Frontend Programming", "Mobile Application"]

# Attendance and Homework storage
attendance_history = {}
homework_records = {}

@app.template_filter('dateformat')
def dateformat(value, format="%Y-%m-%d"):
    try:
        return datetime.strptime(value, "%d-%m-%Y").strftime(format)
    except:
        return datetime.now().strftime(format)


# ✅ Redirect "/" and "/registeri" to front page
@app.route("/", methods=["GET", "POST"])
@app.route("/registeri", methods=["GET", "POST"])
def home():
    return redirect(url_for("front"))

# ✅ Welcome front page
@app.route("/front")
def front():
    return render_template("index.html")

# ✅ Attendance marking logic now in this route
@app.route("/mark", methods=["GET", "POST"])
def mark_attendance():
    if request.method == "POST":
        selected_date = request.form.get("date")
        if not selected_date:
            selected_date = datetime.now().strftime("%d-%m-%Y")
        else:
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        
        if selected_date not in attendance_history:
            attendance_history[selected_date] = {}

        for s in students:
            status = request.form.get(s, "A")
            attendance_history[selected_date][s] = status

    else:
        selected_date = datetime.now().strftime("%d-%m-%Y")

    today_attendance = attendance_history.get(selected_date, {})
    present_count = sum(1 for s in today_attendance.values() if s == "P")
    absent_count = sum(1 for s in today_attendance.values() if s == "A")

    return render_template("home.html",
                           students=students,
                           attendance=today_attendance,
                           current_date=selected_date,
                           present_count=present_count,
                           absent_count=absent_count,
                           attendance_history=attendance_history,
                           courses=courses,
                           homework_records=homework_records)


@app.route("/student/<name>")
def student_detail(name):
    records = []
    for date, daily_att in attendance_history.items():
        status = daily_att.get(name, "Not Marked")
        records.append((date, status))

    records.sort(reverse=True)
    total_days = len(records)
    present_count = sum(1 for _, s in records if s == "P")
    absent_count = sum(1 for _, s in records if s == "A")
    percentage = round((present_count / total_days) * 100, 2) if total_days > 0 else 0

    return render_template("student_detail.html",
                           name=name,
                           records=records,
                           total_days=total_days,
                           present_count=present_count,
                           absent_count=absent_count,
                           percentage=percentage)

@app.route("/attendance/<date>")
def view_attendance(date):
    daily_att = attendance_history.get(date, {})
    return render_template("daily_attendance.html",
                           date=date,
                           students=students,
                           attendance=daily_att)

@app.route("/courses", methods=["GET", "POST"])
def manage_courses():
    if request.method == "POST":
        new_course = request.form.get("course_name")
        if new_course and new_course not in courses:
            courses.append(new_course)
        return redirect(url_for("manage_courses"))

    return render_template("courses.html", courses=courses)

@app.route("/students", methods=["GET", "POST"])
def manage_students():
    if request.method == "POST":
        if "delete_student" in request.form:
            student_name = request.form.get("delete_student")
            if student_name in students:
                students.remove(student_name)
                for daily_att in attendance_history.values():
                    daily_att.pop(student_name, None)

        elif "add_student" in request.form:
            new_student = request.form.get("add_student").strip()
            if new_student and new_student not in students:
                students.append(new_student)

        return redirect(url_for("manage_students"))

    return render_template("students.html", students=students)


@app.route("/attendance-records")
def view_attendance_records():
    dates = sorted(attendance_history.keys(), reverse=True)
    return render_template("attendance_records.html", dates=dates)



@app.route("/homework", methods=["GET", "POST"])
def homework():
    global homework_records

    if request.method == "POST":
        selected_date = request.form.get("date")
        selected_course = request.form.get("course")
        description = request.form.get("description", "").strip()

        if selected_date not in homework_records:
            homework_records[selected_date] = {}

        if selected_course not in homework_records[selected_date]:
            homework_records[selected_date][selected_course] = {
                "description": "",
                "marks": {},
                "progress": {}
            }

        # Save description
        if description:
            homework_records[selected_date][selected_course]["description"] = description

        # Save marks and progress
        for student in students:
            mark = request.form.get(f"{student}_marks", "").strip()
            if mark:
                homework_records[selected_date][selected_course]["marks"][student] = mark

            progress = request.form.get(f"{student}_progress", "").strip()
            if progress:
                homework_records[selected_date][selected_course]["progress"][student] = progress

    return render_template(
        "homework.html",
        students=students,
        courses=courses,
        homework_records=homework_records
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

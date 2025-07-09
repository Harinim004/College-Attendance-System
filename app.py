from flask import Flask, render_template, request, redirect, url_for
import pymysql
from config import *

app = Flask(__name__)

# Connect to MySQL database using PyMySQL
conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    port=MYSQL_PORT,
    database=MYSQL_DB,
    cursorclass=pymysql.cursors.Cursor
)
cursor = conn.cursor()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        cursor.execute("INSERT INTO Students (name, email, course) VALUES (%s, %s, %s)", (name, email, course))
        conn.commit()
    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()
    return render_template('students.html', students=students)


@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        cursor.execute("INSERT INTO Subjects (name, code) VALUES (%s, %s)", (name, code))
        conn.commit()
    cursor.execute("SELECT * FROM Subjects")
    subjects = cursor.fetchall()
    return render_template('subjects.html', subjects=subjects)


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        student_id = request.form['student_id']
        subject_id = request.form['subject_id']
        date = request.form['date']
        status = request.form['status']
        cursor.execute("INSERT INTO AttendanceLogs (student_id, subject_id, date, status) VALUES (%s, %s, %s, %s)",
                       (student_id, subject_id, date, status))
        conn.commit()
    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()
    cursor.execute("SELECT * FROM Subjects")
    subjects = cursor.fetchall()
    cursor.execute("""SELECT A.id, S.name, B.name, A.date, A.status
                      FROM AttendanceLogs A
                      JOIN Students S ON A.student_id = S.id
                      JOIN Subjects B ON A.subject_id = B.id""")
    logs = cursor.fetchall()
    return render_template('attendance.html', logs=logs, students=students, subjects=subjects)


@app.route('/reports')
def reports():
    cursor.execute("""
        SELECT S.name, B.name,
        SUM(A.status = 'Present') AS presents,
        COUNT(*) AS total,
        ROUND(SUM(A.status = 'Present') / COUNT(*) * 100, 2) AS percentage
        FROM AttendanceLogs A
        JOIN Students S ON A.student_id = S.id
        JOIN Subjects B ON A.subject_id = B.id
        GROUP BY A.student_id, A.subject_id
    """)
    data = cursor.fetchall()
    return render_template('reports.html', data=data)


@app.route('/defaulters')
def defaulters():
    cursor.execute("""
        SELECT S.name, B.name,
        ROUND(SUM(A.status = 'Present') / COUNT(*) * 100, 2) AS percent
        FROM AttendanceLogs A
        JOIN Students S ON A.student_id = S.id
        JOIN Subjects B ON A.subject_id = B.id
        GROUP BY A.student_id, A.subject_id
        HAVING percent < 75
    """)
    defaulters = cursor.fetchall()
    return render_template('defaulters.html', defaulters=defaulters)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import os
from download_pdf import get_pdf
from class_grades import data_grades

app = Flask(__name__)
socketio = SocketIO(app)

# Import config variables
from config import first_semester_path, second_semester_path, username, password, year, is_printing, download_second_semester, headless, download_first_semester

@app.route('/')
def index():
    return render_template('index.html',
        first_semester_path=first_semester_path,
        second_semester_path=second_semester_path,
        username=username,
        password=password,
        year=year,
        is_printing=is_printing,
        download_second_semester=download_second_semester,
        headless=headless,
        download_first_semester=download_first_semester
        )

@app.route('/calculate-grades')
def calculate_grades():
    if download_second_semester or download_first_semester:
        print("starting")
        socketio.emit('progress', {'message': 'Starting...'}, namespace='/task')
        get_pdf(socketio)
    socketio.emit('progress', {'message': "Calculating Grades"}, namespace='/task')
    grades_result = data_grades()

    return jsonify(grades_result)

@app.route('/update-settings', methods=['POST'])
def update_settings():
    global first_semester_path, second_semester_path, username, password, year, is_printing, download_second_semester, headless, download_first_semester

    settings_data = request.json

    first_semester_path = settings_data.get('firstSemesterPath', first_semester_path)
    second_semester_path = settings_data.get('downloadPath', second_semester_path)
    username = settings_data.get('username', username)
    password = settings_data.get('password', password)
    year = settings_data.get('year', year)
    is_printing = settings_data.get('isPrinting', is_printing) == 'true'  # Convert to boolean
    download_second_semester = settings_data.get('download_second_semester', download_second_semester) == 'true'  # Convert to boolean
    headless = settings_data.get('headless', headless) == 'true'  # Convert to boolean
    download_first_semester = settings_data.get('download_first_semester', download_first_semester) == 'true'  # Convert to boolean

    # Update config.py with new settings
    with open('config.py', 'w') as config_file:
        config_file.write(f"first_semester_path = '{first_semester_path}'\n")
        config_file.write(f"second_semester_path = '{second_semester_path}'\n")
        config_file.write(f"username = '{username}'\n")
        config_file.write(f"password = '{password}'\n")
        config_file.write(f"year = '{year}'\n")
        config_file.write(f"is_printing = {is_printing}\n")
        config_file.write(f"download_second_semester = {download_second_semester}\n")
        config_file.write(f"headless = {headless}\n")
        config_file.write(f"download_first_semester = {download_first_semester}\n")

    return jsonify({'message': 'Settings updated successfully'})

if __name__ == '__main__':
    socketio.run(app, debug=True)


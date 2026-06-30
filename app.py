from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS, cross_origin
import json
import os
import sys
import threading
import webbrowser
import time
import pandas as pd
from datetime import datetime
import io
import pywhatkit

"""
B.E Section (079) 23267546 

1515491072775452

Harshmevada@123



# student login
250893131044.ce24@sltiet.edu.in

sltiet@123

# admin login
principal@sltiet.edu.in
computer@sltiet.edu.in
science@sltiet.edu.in
mechanical@sltiet.edu.in
civil@sltiet.edu.in
electrical@sltiet.edu.in

admin@123

# all accoding

Enroll :- 258903131012 
Password :- GhediyaKhushi@2005
"""

if getattr(sys, 'frozen', False):
    # Path to the directory of the executable
    base_dir = os.path.dirname(sys.executable)
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__, static_folder='static', template_folder='templates')

CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization", "Accept"], "supports_credentials": False}})

# Configuration
UPLOAD_FOLDER = os.path.join(base_dir, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
ATTENDANCE_FILE = os.path.join(base_dir, 'attendance_data.json')
ACADEMIC_FILE = os.path.join(base_dir, 'academic_data.json')
STUDENTS_FILE = os.path.join(base_dir, 'students_data.json')
TEACHERS_FILE = os.path.join(base_dir, 'teachers_data.json')
FEE_RECEIPTS_FILE = os.path.join(base_dir, 'fee_receipts_data.json')
RECEIPT_REQUESTS_FILE = os.path.join(base_dir, 'receipt_requests_data.json')
LEAVES_FILE = os.path.join(base_dir, 'leaves_data.json')
MARKS_FILE = os.path.join(base_dir, 'marks_data.json')
NOTIFICATIONS_FILE = os.path.join(base_dir, 'notifications_data.json')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Custom route to serve uploads from external folder next to the EXE
@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_marks():
    if os.path.exists(MARKS_FILE):
        try:
            with open(MARKS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_marks(data):
    with open(MARKS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_notifications():
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_notifications(data):
    with open(NOTIFICATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_notification(user_id, title, message, student_name='', faculty_name='', subject='', status='', notif_type=''):
    notifs = load_notifications()
    notif_id = int(datetime.now().timestamp() * 1000)
    new_notif = {
        'id': notif_id,
        'user_id': user_id,
        'title': title,
        'message': message,
        'student_name': student_name,
        'faculty_name': faculty_name,
        'subject': subject,
        'status': status,
        'type': notif_type,
        'read': False,
        'created_at': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    notifs.append(new_notif)
    save_notifications(notifs)
    return new_notif

def load_students():
    # 1. Try to load from external students file next to the EXE
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
            
    # 2. Try to load from bundled assets if frozen
    if getattr(sys, 'frozen', False):
        bundled_path = os.path.join(sys._MEIPASS, 'students_data.json')
        if os.path.exists(bundled_path):
            try:
                with open(bundled_path, 'r') as f:
                    data = json.load(f)
                # Try to write it next to the EXE for persistence / editing
                try:
                    with open(STUDENTS_FILE, 'w') as f:
                        json.dump(data, f, indent=4)
                except Exception:
                    pass
                return data
            except Exception:
                pass
    return []

def load_teachers():
    # 1. Try to load from external teachers file next to the EXE
    if os.path.exists(TEACHERS_FILE):
        try:
            with open(TEACHERS_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
            
    # 2. Try to load from bundled assets if frozen
    if getattr(sys, 'frozen', False):
        bundled_path = os.path.join(sys._MEIPASS, 'teachers_data.json')
        if os.path.exists(bundled_path):
            try:
                with open(bundled_path, 'r') as f:
                    data = json.load(f)
                # Try to write it next to the EXE
                try:
                    with open(TEACHERS_FILE, 'w') as f:
                        json.dump(data, f, indent=4)
                except Exception:
                    pass
                return data
            except Exception:
                pass
    
    default_teachers = [
        {"email": "principal@sltiet.edu.in", "password": "admin@123"},
        {"email": "computer@sltiet.edu.in", "password": "admin@123"},
        {"email": "science@sltiet.edu.in", "password": "admin@123"},
        {"email": "mechanical@sltiet.edu.in", "password": "admin@123"},
        {"email": "civil@sltiet.edu.in", "password": "admin@123"},
        {"email": "electrical@sltiet.edu.in", "password": "admin@123"}
    ]
    try:
        with open(TEACHERS_FILE, 'w') as f:
            json.dump(default_teachers, f, indent=4)
    except Exception:
        pass
    return default_teachers

def save_teachers(data):
    with open(TEACHERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def save_students(data):
    with open(STUDENTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_academic_data():
    if os.path.exists(ACADEMIC_FILE):
        with open(ACADEMIC_FILE, 'r') as f:
            return json.load(f)
    return {"timetable": {}, "calendar": None, "syllabus": None}

def save_academic_data(data):
    with open(ACADEMIC_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/role')
def role():
    return render_template('role.html')

@app.route('/logout')
def logout():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/student_management')
def student_management():
    return render_template('student_management.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/faculty_dashboard')
def faculty_dashboard():
    return render_template('teacher.html')

@app.route('/faculty_profile')
def faculty_profile():
    return render_template('faculty_profile.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/teacher/attendance')
def teacher_entry():
    return render_template('teacher_attendance.html')

@app.route('/teacher/fill_attendance')
def fill_attendance():
    date = request.args.get('date')
    slot = request.args.get('slot')
    if not date or not slot:
        return "Missing date or slot", 400
    return render_template('fill_attendance.html', date=date, slot=slot)

@app.route('/mid_exam')
def mid_exam():
    return render_template('mid_exam.html')

@app.route('/F_mid_exam')
def f_mid_exam():
    return render_template('F_mid_exam.html')

@app.route('/fees')
def fees():
    return render_template('fees.html')

@app.route('/fee_receipt')
def fee_receipt():
    return render_template('FeeReceipt.html')

@app.route('/leave_application')
def leave_application():
    return render_template('leave_application.html')

@app.route('/leave_approvals')
def leave_approvals():
    return render_template('leave_approvals.html')

# API for handling attendance
@app.route('/api/attendance', methods=['GET', 'POST'])
def handle_attendance():
    if request.method == 'POST':
        data = request.json
        # Expected format: { "date": "...", "slot": "slot1", "semester": "...", "subject": "...", "attendance": { "roll1": "P" } }
        all_attendance = load_data()
        date = data.get('date')
        slot = data.get('slot')
        semester = data.get('semester', '')
        subject = data.get('subject', '')
        student_attendance = data.get('attendance', {})
        
        if date and slot:
            if date not in all_attendance or not isinstance(all_attendance[date], dict):
                all_attendance[date] = {}
            all_attendance[date][slot] = {
                "attendance": student_attendance,
                "semester": semester,
                "subject": subject
            }
            save_data(all_attendance)
            return jsonify({"status": "success", "message": "Attendance saved successfully"})
        return jsonify({"status": "error", "message": "Missing date or slot"}), 400
    else:
        roll_no = request.args.get('roll_no')
        all_attendance = load_data()
        if roll_no:
            # Filter attendance for one student
            filtered = {}
            for date, day_data in all_attendance.items():
                filtered[date] = []
                # Map back to 5 slots list (as Slot6 is removed)
                for i in range(1, 6):
                    slot_key = f"slot{i}"
                    status = ""
                    if isinstance(day_data, dict):
                        slot_content = day_data.get(slot_key, {})
                        if isinstance(slot_content, dict):
                            if 'attendance' in slot_content:
                                status = slot_content.get('attendance', {}).get(roll_no, "")
                            else:
                                status = slot_content.get(roll_no, "")
                    filtered[date].append(status)
            return jsonify(filtered)
        return jsonify(all_attendance)

@app.route('/api/students', methods=['GET'])
def get_students():
    return jsonify(load_students())

@app.route('/api/delete_student', methods=['POST'])
def delete_student():
    try:
        data = request.json
        roll = data.get('roll')
        if not roll:
            return jsonify({"status": "error", "message": "Missing roll number"}), 400
        
        students = load_students()
        original_count = len(students)
        students = [s for s in students if str(s.get('roll')) != str(roll)]
        
        if len(students) < original_count:
            save_students(students)
            return jsonify({"status": "success", "message": "Student record deleted"})
        else:
            return jsonify({"status": "error", "message": "Student not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/clear_students', methods=['POST'])
def clear_students():
    try:
        save_students([])
        return jsonify({"status": "success", "message": "All student records cleared"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/upload_students', methods=['POST'])
def upload_students():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    try:
        df = pd.read_excel(file)
        # Drop rows where all elements are NaN
        df = df.dropna(how='all')
        
        # Robust Data-Driven Column Detection
        best_roll_col = None
        best_name_col = None
        max_roll_score = 0
        max_name_score = 0

        for col in df.columns:
            col_data = df[col].dropna().astype(str).tolist()
            if not col_data: continue
            
            roll_score = 0
            name_score = 0
            
            for val in col_data:
                val = val.strip()
                if not val or val.lower() == 'nan': continue
                
                # Check if looks like Enrollment Number (long string, mostly digits or specific prefixes)
                if len(val) >= 6 and (val.isdigit() or val.upper().startswith('BE') or val.upper().startswith('ME')):
                    roll_score += 1
                elif len(val) >= 4 and any(c.isdigit() for c in val) and not ' ' in val:
                    roll_score += 0.5
                    
                # Check if looks like Student Name (mostly letters, no numbers, often has spaces)
                if len(val) > 3 and not any(c.isdigit() for c in val):
                    alpha_count = sum(c.isalpha() for c in val)
                    if alpha_count > len(val) * 0.5:
                        name_score += 1 if ' ' in val else 0.5

            if roll_score > max_roll_score:
                max_roll_score = roll_score
                best_roll_col = col
                
            if name_score > max_name_score:
                max_name_score = name_score
                best_name_col = col

        # Fallbacks if extraction totally failed
        if best_roll_col is None and len(df.columns) > 1: best_roll_col = df.columns[1]
        if best_name_col is None and len(df.columns) > 2: best_name_col = df.columns[2]
        if best_name_col is None and len(df.columns) == 2 and best_roll_col == df.columns[0]: best_name_col = df.columns[1]
        
        # for i in range(Stu_ID,Stu_name,Stu_enrollment_no)Keywords to skip (header/title rows getting parsed){coloring:"Teacher",Testing: "Student"}
        skip_words = ['name', 'enroll', 'roll', 'sr', 'no', 'student', 'department', 'list']

        formatted_students = []
        for _, row in df.iterrows():
            roll = str(row[best_roll_col]).strip() if best_roll_col is not None else ""
            name = str(row[best_name_col]).strip() if best_name_col is not None else ""
            
            if roll.lower() == 'nan': roll = ""
            if name.lower() == 'nan': name = ""
            
            if not roll and not name: continue
            
            # Skip rows where the extracted "roll" or "name" is actually a header word
            if any(w in roll.lower() for w in skip_words) or any(w in name.lower() for w in skip_words):
                continue
                
            formatted_students.append({
                    "name": name,
                    "roll": roll,
                    "class": ""
                })
        
        save_students(formatted_students)
        return jsonify({"status": "success", "count": len(formatted_students)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/upload_teachers', methods=['POST'])
def upload_teachers():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    try:
        df = pd.read_excel(file)
        # Expect columns 'Email' and 'Password' (case‑insensitive)
        email_col = None
        password_col = None
        for col in df.columns:
            lc = str(col).lower()
            if 'email' in lc:
                email_col = col
            if 'pass' in lc:
                password_col = col
        if not email_col or not password_col:
            return jsonify({"status": "error", "message": "Required columns not found"}), 400
        teachers = []
        for _, row in df.iterrows():
            email = str(row[email_col]).strip()
            pwd = str(row[password_col]).strip()
            if email and pwd:
                teachers.append({"email": email, "password": pwd})
        save_teachers(teachers)
        return jsonify({"status": "success", "count": len(teachers)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/export_attendance')
def export_attendance():
    date = request.args.get('date')
    slot = request.args.get('slot')
    if not (date and slot):
        return "Missing date or slot", 400
        
    all_attendance = load_data()
    students = load_students()
    
    date_data = all_attendance.get(date, {})
    if not isinstance(date_data, dict):
        # Fallback if old list format exists
        attendance_map = {}
    else:
        attendance_map = date_data.get(slot, {})
        if not isinstance(attendance_map, dict):
            attendance_map = {}
    
    export_data = []
    for s in students:
        status = attendance_map.get(s['roll'], 'R')
        export_data.append({
            "Enrollment No": s['roll'],
            "Name": s['name'],
            "Class": s['class'],
            "Date": date,
            "Slot": slot,
            "Status": status
        })
        
    df = pd.DataFrame(export_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name=f'Attendance_{date}_{slot}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@cross_origin()
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login_api():
    data = request.json
    email = data.get('email')
    password = data.get('pass') or data.get('password')
    
    email = email.strip() if isinstance(email, str) else ''
    password = password.strip() if isinstance(password, str) else ''
    
    # Teacher login - now loaded from teachers_data.json
    teachers = load_teachers()
    # Expected each teacher dict to have 'email' and 'password' keys
    matching_teacher = next((t for t in teachers if t.get('email', '').lower() == email.lower()), None)
    if matching_teacher and matching_teacher.get('password') == password:
        return jsonify({"status": "success", "role": "teacher", "redirect": "/faculty_dashboard"})
    
    enrollment = None
    if email:
        email_lower = email.lower().strip()
        if password == "sltiet@123":
            if "@sltiet.edu.in" in email_lower:
                parts = email_lower.split("@")[0].split(".")
                enrollment = parts[0]
            elif email_lower.isdigit():
                enrollment = email_lower
    if enrollment:
        # Verify enrollment exists in uploaded student records
        try:
            students = load_students()
            # If no students loaded, attempt to load from default Excel file
            if not students:
                try:
                    excel_path = os.path.join(base_dir, 'students.xlsx')
                    if os.path.exists(excel_path):
                        df = pd.read_excel(excel_path)
                        # Reuse existing logic to extract roll and name columns
                        best_roll_col = None
                        best_name_col = None
                        max_roll_score = 0
                        max_name_score = 0
                        for col in df.columns:
                            col_data = df[col].dropna().astype(str).tolist()
                            if not col_data:
                                continue
                            roll_score = 0
                            name_score = 0
                            for val in col_data:
                                val = val.strip()
                                if len(val) >= 6 and (val.isdigit() or val.upper().startswith('BE') or val.upper().startswith('ME')):
                                    roll_score += 1
                                if len(val) > 3 and not any(c.isdigit() for c in val):
                                    name_score += 1 if ' ' in val else 0.5
                            if roll_score > max_roll_score:
                                max_roll_score = roll_score
                                best_roll_col = col
                            if name_score > max_name_score:
                                max_name_score = name_score
                                best_name_col = col
                        formatted_students = []
                        for _, row in df.iterrows():
                            roll = str(row[best_roll_col]).strip() if best_roll_col else ''
                            name = str(row[best_name_col]).strip() if best_name_col else ''
                            if roll and name:
                                formatted_students.append({'roll': roll, 'name': name, 'class': ''})
                        save_students(formatted_students)
                        students = formatted_students
                except Exception as e:
                    print('Failed to load students from Excel:', e)
            
            if not any(str(s.get('roll')) == str(enrollment) for s in students):
                student_record = {
                    "name": f"Student {enrollment}",
                    "roll": str(enrollment),
                    "class": ""
                }
                students.append(student_record)
                save_students(students)
            else:
                student_record = next((s for s in students if str(s.get('roll')) == str(enrollment)), None)
            
            student_name = student_record.get('name') if student_record else f"Student {enrollment}"
        except Exception:
            student_name = f"Student {enrollment}"
        return jsonify({
            "status": "success",
            "role": "student",
            "roll": enrollment,
            "name": student_name,
            "class": student_record.get('class', '') if student_record else '',
            "redirect": "/student"
        })
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/login', methods=['POST'])
def login_post():
    """Handle login POST requests from mobile app and delegate to login_api"""
    return login_api()

@app.route('/api/upload_academic', methods=['POST'])
def upload_academic():
    category = request.form.get('category')
    semester = request.form.get('semester')
    branch = request.form.get('branch')
    subject = request.form.get('subject')
    
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        prefix_parts = [category]
        if branch:
            prefix_parts.append(branch)
        if semester:
            prefix_parts.append(semester)
        if subject:
            prefix_parts.append(subject)
        prefix_parts.append(file.filename)
        filename = "_".join(prefix_parts).replace(' ', '_')
        
        # Clean filename
        filename = filename.replace(' ', '_')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        rel_path = '/static/uploads/' + filename
        academic_data = load_academic_data()
        
        if category in ('timetable', 'calendar', 'syllabus'):
            if category not in academic_data or not isinstance(academic_data[category], dict):
                academic_data[category] = {}
            b = branch if branch else "CSE"
            if b not in academic_data[category]:
                academic_data[category][b] = {}
            academic_data[category][b][semester] = rel_path
        elif category == 'mid_paper':
            if 'mid_papers' not in academic_data:
                academic_data['mid_papers'] = {}
            if semester not in academic_data['mid_papers']:
                academic_data['mid_papers'][semester] = {}
            academic_data['mid_papers'][semester][subject] = rel_path
            
        save_academic_data(academic_data)
        return jsonify({"status": "success", "message": "File uploaded successfully", "path": rel_path})
    
    return jsonify({"status": "error", "message": "File type not allowed"}), 400

@app.route('/api/academic_data', methods=['GET'])
def get_academic_data():
    return jsonify(load_academic_data())

@app.route('/api/save_teacher_profile', methods=['POST'])
def save_teacher_profile():
    data = request.json or {}
    email = data.get('email', '').strip()
    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400
    
    teachers = load_teachers()
    updated = False
    for t in teachers:
        if t.get('email', '').lower() == email.lower():
            t['name'] = data.get('name', '')
            t['dept'] = data.get('dept', '')
            t['designation'] = data.get('designation', '')
            t['phone'] = data.get('phone', '')
            t['qual'] = data.get('qual', '')
            t['subjects'] = data.get('subjects', [])
            updated = True
            break
            
    if not updated:
        # Create a new profile if it doesn't exist
        teachers.append({
            'email': email,
            'password': 'admin@123',
            'name': data.get('name', ''),
            'dept': data.get('dept', ''),
            'designation': data.get('designation', ''),
            'phone': data.get('phone', ''),
            'qual': data.get('qual', ''),
            'subjects': data.get('subjects', [])
        })
    
    save_teachers(teachers)
    return jsonify({'status': 'success', 'message': 'Profile saved successfully'})

@app.route('/api/get_teacher_profile', methods=['GET'])
def get_teacher_profile():
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400
    
    teachers = load_teachers()
    match = next((t for t in teachers if t.get('email', '').lower() == email.lower()), None)
    if match:
        return jsonify(match)
    return jsonify({'status': 'error', 'message': 'Teacher not found'}), 404

@app.route('/api/get_all_teachers', methods=['GET'])
def get_all_teachers():
    teachers = load_teachers()
    # Strip passwords for security
    public_teachers = []
    for t in teachers:
        public_teachers.append({
            'email': t.get('email'),
            'name': t.get('name', t.get('email').split('@')[0].capitalize()),
            'subjects': t.get('subjects', []),
            'dept': t.get('dept', '')
        })
    return jsonify(public_teachers)

@app.route('/api/get_subjects_by_dept_sem', methods=['GET'])
def get_subjects_by_dept_sem():
    dept = request.args.get('dept', '').strip()
    semester = request.args.get('semester', '').strip()
    if not dept or not semester:
        return jsonify([])
    
    teachers = load_teachers()
    subjects_set = set()
    for t in teachers:
        for s in t.get('subjects', []):
            if isinstance(s, dict):
                s_dept = s.get('dept', '')
                s_sem = s.get('semester', '')
                s_name = s.get('subject', '')
                if s_dept.lower() == dept.lower() and s_sem.lower() == semester.lower():
                    subjects_set.add(s_name)
    
    return jsonify(sorted(list(subjects_set)))

# New endpoint to update student profile details
@app.route('/api/update_student', methods=['POST'])
def update_student():
    data = request.json or {}
    roll = data.get('roll')
    name = data.get('name')
    if not roll or not name:
        return jsonify({'status': 'error', 'message': 'Missing roll or name'}), 400
    students = load_students()
    updated = False
    for s in students:
        if str(s.get('roll')) == str(roll):
            s['name'] = name
            s['email'] = data.get('email', '')
            s['phone'] = data.get('phone', '')
            s['class'] = data.get('class', '')
            if data.get('password'):
                s['password'] = data.get('password')
            updated = True
            break
    if updated:
        save_students(students)
        return jsonify({'status': 'success', 'message': 'Student profile updated'})
    else:
        return jsonify({'status': 'error', 'message': 'Student not found'}), 404

# FEE_RECEIPTS_FILE is defined globally at the top

def load_fee_receipts():
    if os.path.exists(FEE_RECEIPTS_FILE):
        with open(FEE_RECEIPTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_fee_receipts(data):
    with open(FEE_RECEIPTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/upload_fee_receipt', methods=['POST'])
def upload_fee_receipt():
    semester = request.form.get('semester')
    branch = request.form.get('branch')
    label = request.form.get('label', '')

    if not semester:
        return jsonify({"status": "error", "message": "Semester is required"}), 400
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        safe_name = file.filename.replace(' ', '_')
        filename = f"fee_receipt_{branch}_{semester}_{safe_name}" if branch else f"fee_receipt_{semester}_{safe_name}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        rel_path = '/static/uploads/' + filename

        receipts = load_fee_receipts()
        receipts.append({
            "branch": branch if branch else "CSE",
            "semester": semester,
            "label": label if label else file.filename,
            "path": rel_path,
            "uploaded_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        save_fee_receipts(receipts)

        # Notify ALL students of that branch & semester
        students = load_students()
        for s in students:
            # Match branch/semester if possible
            s_class = s.get('class') or ''
            if not s_class or branch.lower() in s_class.lower() or semester.lower() in s_class.lower():
                add_notification(
                    user_id=s.get('roll'),
                    title="New Fee Receipt",
                    message=f"A new fee receipt '{label if label else file.filename}' has been uploaded for {semester.replace('sem', 'Sem ')}.",
                    student_name=s.get('name'),
                    faculty_name="Accounts",
                    subject="Fees",
                    status="Uploaded",
                    notif_type="fee_receipt"
                )

        return jsonify({"status": "success", "message": "Fee receipt uploaded successfully", "path": rel_path})

    return jsonify({"status": "error", "message": "Only PDF files are allowed"}), 400

@app.route('/api/fee_receipts', methods=['GET'])
def get_fee_receipts():
    return jsonify(load_fee_receipts())

@app.route('/api/delete_fee_receipt', methods=['POST'])
def delete_fee_receipt():
    data = request.json
    index = data.get('index')
    if index is None:
        return jsonify({"status": "error", "message": "Index required"}), 400
    receipts = load_fee_receipts()
    if 0 <= index < len(receipts):
        removed = receipts.pop(index)
        # Also delete the physical file
        try:
            file_path = removed['path'].lstrip('/')
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        save_fee_receipts(receipts)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid index"}), 400

# ---- Receipt Request Notifications (student requests a semester receipt) ----
# RECEIPT_REQUESTS_FILE is defined globally at the top

def load_receipt_requests():
    if os.path.exists(RECEIPT_REQUESTS_FILE):
        with open(RECEIPT_REQUESTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_receipt_requests(data):
    with open(RECEIPT_REQUESTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/fee_receipts_by_semester', methods=['GET'])
def get_fee_receipts_by_semester():
    """Return receipts filtered by semester and branch."""
    semester = request.args.get('semester', '')
    branch = request.args.get('branch', '')
    receipts = load_fee_receipts()
    if semester:
        receipts = [r for r in receipts if r.get('semester') == semester]
    if branch:
        receipts = [r for r in receipts if r.get('branch') == branch or r.get('branch') is None]
    return jsonify(receipts)

@app.route('/api/notify_receipt_request', methods=['POST'])
def notify_receipt_request():
    """Called when a student selects a semester and tries to download a receipt."""
    data = request.json or {}
    semester = data.get('semester', '')
    roll = data.get('roll', 'Unknown')
    branch = data.get('branch', '')
    if not semester:
        return jsonify({"status": "error", "message": "Semester required"}), 400
    requests_list = load_receipt_requests()
    # Avoid duplicate entries for same roll + semester in same day
    today = datetime.now().strftime("%d/%m/%Y")
    already = any(r['roll'] == roll and r['semester'] == semester and r['date'] == today for r in requests_list)
    if not already:
        requests_list.append({
            "roll": roll,
            "semester": semester,
            "branch": branch if branch else "CSE",
            "date": today,
            "time": datetime.now().strftime("%H:%M"),
            "seen": False
        })
        save_receipt_requests(requests_list)
        
        # Get student name
        student_name = f"Student {roll}"
        try:
            students = load_students()
            match = next((s for s in students if str(s.get('roll')) == str(roll)), None)
            if match:
                student_name = match.get('name')
        except Exception:
            pass
            
        # Notify ALL teachers of that department or general
        teachers = load_teachers()
        for t in teachers:
            add_notification(
                user_id=t.get('email'),
                title="Receipt Request",
                message=f"Roll: {roll} requested fee receipt for {semester.replace('sem', 'Sem ')}.",
                student_name=student_name,
                faculty_name=t.get('name', t.get('email').split('@')[0].capitalize()),
                subject="Fees",
                status="Pending",
                notif_type="receipt_request"
            )
    return jsonify({"status": "success"})

@app.route('/api/receipt_requests', methods=['GET'])
def get_receipt_requests():
    """Faculty reads pending receipt download requests from students."""
    return jsonify(load_receipt_requests())

@app.route('/api/mark_requests_seen', methods=['POST'])
def mark_requests_seen():
    """Mark all receipt requests as seen (faculty acknowledged)."""
    requests_list = load_receipt_requests()
    for r in requests_list:
        r['seen'] = True
    save_receipt_requests(requests_list)
    return jsonify({"status": "success"})

# ════════════════════════════════════════════════════════════════
#  LEAVE APPLICATION — Server-side API
#  All leave data is stored in leaves_data.json so that student
#  submissions are immediately visible to the faculty portal.
# ════════════════════════════════════════════════════════════════

# LEAVES_FILE is defined globally at the top

def load_leaves():
    if os.path.exists(LEAVES_FILE):
        with open(LEAVES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaves(data):
    with open(LEAVES_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/api/submit_leave', methods=['POST'])
def submit_leave():
    """Student submits a leave application → saved server-side."""
    data = request.json or {}
    name   = data.get('name', '').strip()
    roll   = data.get('roll', '').strip()
    from_d = data.get('from', '').strip()
    to_d   = data.get('to', '').strip()
    ltype  = data.get('type', '').strip()
    reason = data.get('reason', '').strip()
    parent = data.get('parentNumber', '').strip()
    semester = data.get('semester', '').strip()
    target_faculty = data.get('targetFaculty', '').strip()

    if not (name and from_d and to_d and ltype and reason and parent):
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    leaves = load_leaves()
    leave_id = int(datetime.now().timestamp() * 1000)   # ms timestamp
    new_leave = {
        'id':           leave_id,
        'name':         name,
        'roll':         roll,
        'from':         from_d,
        'to':           to_d,
        'type':         ltype,
        'reason':       reason,
        'parentNumber': parent,
        'semester':     semester,
        'targetFaculty': target_faculty,
        'status':       'Pending',
        'appliedAt':    datetime.now().strftime('%d/%m/%Y %H:%M'),
        'notified':     False      # True once student has been notified of decision
    }
    leaves.append(new_leave)
    save_leaves(leaves)

    # Unified dynamic notification generation for faculty
    teachers = load_teachers()
    teacher_name = next((t.get('name', t.get('email').split('@')[0].capitalize()) for t in teachers if t.get('email','').lower() == target_faculty.lower()), 'Faculty')
    add_notification(
        user_id=target_faculty,
        title="New Leave Request",
        message=f"Roll: {roll} applied for {ltype} ({from_d} to {to_d}). Reason: {reason}",
        student_name=name,
        faculty_name=teacher_name,
        subject="General",
        status="Pending",
        notif_type="leave_request"
    )

    # ── Send WhatsApp notification to parent ────────────────────────────────────
    try:
        message = f"""
Dear Parent,

Your child {name}
(Roll No: {roll})

has submitted a leave application.

From : {from_d}
To   : {to_d}

Reason:
{reason}

SLTIET
"""
        pywhatkit.sendwhatmsg_instantly(
            f"+{parent}",
            message,
            wait_time=20,
            tab_close=True
        )
    except Exception as wa_err:
        # WhatsApp failure should NOT break the leave submission
        print(f"[WhatsApp] Could not send message: {wa_err}")

    return jsonify({'status': 'success', 'id': leave_id})


@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    """Faculty reads leave applications (optionally filtered by faculty email)."""
    email = request.args.get('email', '').strip()
    leaves = load_leaves()
    if email:
        leaves = [l for l in leaves if l.get('targetFaculty', '').lower() == email.lower()]
    return jsonify(leaves)


@app.route('/api/update_leave_status', methods=['POST'])
def update_leave_status():
    """Faculty approves or declines a leave; sets notified=False so student gets alerted."""
    data      = request.json or {}
    leave_id  = data.get('id')
    status    = data.get('status')          # 'Approved' or 'Declined'

    if leave_id is None or status not in ('Approved', 'Declined'):
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    leaves = load_leaves()
    updated = False
    for lv in leaves:
        if lv.get('id') == leave_id:
            lv['status']   = status
            lv['notified'] = False          # student hasn't seen result yet
            lv['decidedAt'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            updated = True
            
            # Unified dynamic notification generation for student
            student_roll = lv.get('roll')
            student_name = lv.get('name')
            target_faculty = lv.get('targetFaculty')
            ltype = lv.get('type')
            from_d = lv.get('from')
            to_d = lv.get('to')
            
            teachers = load_teachers()
            teacher_name = next((t.get('name', t.get('email').split('@')[0].capitalize()) for t in teachers if t.get('email','').lower() == target_faculty.lower()), 'Faculty')
            
            msg = f"Your leave application ({ltype}, {from_d} → {to_d}) has been {'Approved ✅' if status == 'Approved' else 'Declined ❌'}."
            add_notification(
                user_id=student_roll,
                title="Leave Status Updated",
                message=msg,
                student_name=student_name,
                faculty_name=teacher_name,
                subject="General",
                status=status,
                notif_type="leave_status_update"
            )
            break

    if not updated:
        return jsonify({'status': 'error', 'message': 'Leave not found'}), 404

    save_leaves(leaves)
    return jsonify({'status': 'success'})


# ---- Unified Notifications APIs ----

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    user_id = request.args.get('user_id', '').strip()
    if not user_id:
        return jsonify([])
    notifs = load_notifications()
    user_notifs = [n for n in notifs if str(n.get('user_id')).lower() == user_id.lower()]
    return jsonify(user_notifs)

@app.route('/api/notifications/read', methods=['POST'])
def read_notifications():
    data = request.json or {}
    user_id = data.get('user_id', '').strip()
    notif_id = data.get('id')
    
    notifs = load_notifications()
    updated = False
    for n in notifs:
        if notif_id and n.get('id') == notif_id:
            n['read'] = True
            updated = True
        elif user_id and str(n.get('user_id')).lower() == user_id.lower():
            n['read'] = True
            updated = True
            
    if updated:
        save_notifications(notifs)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Notification not found"}), 404

@app.route('/api/notifications/clear', methods=['POST'])
def clear_notifications():
    data = request.json or {}
    user_id = data.get('user_id', '').strip()
    notif_id = data.get('id')
    
    notifs = load_notifications()
    original_len = len(notifs)
    if notif_id:
        notifs = [n for n in notifs if n.get('id') != notif_id]
    elif user_id:
        notifs = [n for n in notifs if str(n.get('user_id')).lower() != user_id.lower()]
        
    if len(notifs) < original_len:
        save_notifications(notifs)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No notifications cleared"}), 400


# ---- Mid Marks APIs ----

@app.route('/api/save_marks', methods=['POST'])
def save_marks_api():
    try:
        data = request.json or {}
        semester = str(data.get('semester', '')).strip()
        subject = str(data.get('subject', '')).strip()
        marks = data.get('marks', {})
        if not semester or not subject:
            return jsonify({"status": "error", "message": "Semester and Subject are required"}), 400
        
        all_marks = load_marks()
        if semester not in all_marks:
            all_marks[semester] = {}
        
        # Merge or overwrite marks
        if subject not in all_marks[semester]:
            all_marks[semester][subject] = {}
        all_marks[semester][subject].update(marks)
        
        save_marks(all_marks)
        
        # Generate notifications for students who got marks updated
        students = load_students()
        for roll, val in marks.items():
            student_name = next((s.get('name') for s in students if str(s.get('roll')) == str(roll)), f"Student {roll}")
            add_notification(
                user_id=roll,
                title="Marks Updated",
                message=f"Your midterm marks for '{subject}' (Semester {semester}) have been updated to {val}/30.",
                student_name=student_name,
                faculty_name="Faculty",
                subject=subject,
                status="Updated",
                notif_type="marks_update"
            )
            
        return jsonify({"status": "success", "message": "Marks saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get_marks', methods=['GET'])
def get_marks_api():
    try:
        semester = str(request.args.get('semester', '')).strip()
        subject = str(request.args.get('subject', '')).strip()
        roll = str(request.args.get('roll', '')).strip()
        
        all_marks = load_marks()
        
        # If roll is provided, filter for that student
        if roll:
            student_marks = {}
            for sem_id, sem_data in all_marks.items():
                if not semester or sem_id == semester:
                    for sub_name, sub_data in sem_data.items():
                        if not subject or sub_name == subject:
                            if roll in sub_data:
                                if sem_id not in student_marks:
                                    student_marks[sem_id] = {}
                                student_marks[sem_id][sub_name] = sub_data[roll]
            return jsonify(student_marks)
            
        # Otherwise return marks for semester/subject
        if semester:
            sem_data = all_marks.get(semester, {})
            if subject:
                return jsonify(sem_data.get(subject, {}))
            return jsonify(sem_data)
            
        return jsonify(all_marks)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/student_notifications', methods=['GET'])
def student_notifications():
    """Student polls this to see if any of their leaves got decided."""
    roll = request.args.get('roll', '').strip()
    if not roll:
        return jsonify([])

    leaves = load_leaves()
    notifs = []
    for lv in leaves:
        if str(lv.get('roll')) == str(roll) and lv.get('status') in ('Approved', 'Declined') and not lv.get('notified'):
            notifs.append({
                'id':     lv['id'],
                'status': lv['status'],
                'type':   lv.get('type', ''),
                'from':   lv.get('from', ''),
                'to':     lv.get('to', ''),
                'message': (
                    f"Your leave application ({lv.get('type')}, {lv.get('from')} → {lv.get('to')}) "
                    f"has been {'Approved ✅' if lv['status'] == 'Approved' else 'Declined ❌'}."
                ),
                'decidedAt': lv.get('decidedAt', '')
            })
    return jsonify(notifs)


@app.route('/api/mark_leave_notified', methods=['POST'])
def mark_leave_notified():
    """Student marks a leave notification as seen."""
    data = request.json or {}
    leave_id = data.get('id')
    leaves = load_leaves()
    for lv in leaves:
        if lv.get('id') == leave_id:
            lv['notified'] = True
            break
    save_leaves(leaves)
    return jsonify({'status': 'success'})


@app.route('/api/delete_leave', methods=['POST'])
def delete_leave():
    """Faculty permanently deletes a leave application by id."""
    data = request.json or {}
    leave_id = data.get('id')

    if leave_id is None:
        return jsonify({'status': 'error', 'message': 'id is required'}), 400

    leaves = load_leaves()
    original_len = len(leaves)
    leaves = [lv for lv in leaves if lv.get('id') != leave_id]

    if len(leaves) == original_len:
        return jsonify({'status': 'error', 'message': 'Leave not found'}), 404

    save_leaves(leaves)
    return jsonify({'status': 'success', 'message': 'Leave application deleted'})


@cross_origin()
@app.route('/api/proxy_login', methods=['POST', 'OPTIONS'])
def proxy_login():
    """Validate proxy faculty credentials before allowing proxy attendance fill."""
    data = request.json or {}
    email = (data.get('email') or '').strip()
    pwd   = (data.get('pass') or data.get('password') or '').strip()

    if not email or not pwd:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

    teachers = load_teachers()
    match = next((t for t in teachers if t.get('email','').lower() == email.lower()), None)
    if match and match.get('password') == pwd:
        return jsonify({'status': 'success', 'role': 'teacher', 'email': email})

    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    print("SLTIET Attendance Application is running at http://127.0.0.1:5000")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', debug=False, port=5000, use_reloader=False)



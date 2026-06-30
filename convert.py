import os
import shutil
import re

def convert_app():
    templates_dir = "templates"
    static_dir = "static"
    output_dir = "www"

    # 1. Re-create output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # 2. Copy static files (excluding uploads files to keep bundle small, but keep folder)
    shutil.copytree(static_dir, os.path.join(output_dir, "static"), ignore=shutil.ignore_patterns("uploads/*"))
    os.makedirs(os.path.join(output_dir, "static", "uploads"), exist_ok=True)

    # 3. Create config.js
    # Set default local testing server URL to http://localhost:5000 (standard Flask port)
    # The user can easily update this in www/config.js later.
    with open(os.path.join(output_dir, "config.js"), "w") as f:
        f.write("// Capacitor Frontend Configuration\n")
        f.write("const API_BASE_URL = 'http://192.168.1.70:5000';\n")

    # 4. Map server endpoints to relative file names for mobile navigation
    route_mappings = {
        r"'/teacher/fill_attendance'": "'fill_attendance.html'",
        r"\"/teacher/fill_attendance\"": "\"fill_attendance.html\"",
        r"'/teacher/attendance'": "'teacher_attendance.html'",
        r"\"/teacher/attendance\"": "\"teacher_attendance.html\"",
        r"'/student_management'": "'student_management.html'",
        r"\"/student_management\"": "\"student_management.html\"",
        r"'/leave_application'": "'leave_application.html'",
        r"\"/leave_application\"": "\"leave_application.html\"",
        r"'/leave_approvals'": "'leave_approvals.html'",
        r"\"/leave_approvals\"": "\"leave_approvals.html\"",
        r"'/F_mid_exam'": "'F_mid_exam.html'",
        r"\"/F_mid_exam\"": "\"F_mid_exam.html\"",
        r"'/mid_exam'": "'mid_exam.html'",
        r"\"/mid_exam\"": "\"mid_exam.html\"",
        r"'/attendance'": "'attendance.html'",
        r"\"/attendance\"": "\"attendance.html\"",
        r"'/profile'": "'profile.html'",
        r"\"/profile\"": "\"profile.html\"",
        r"'/logout'": "'login.html'",
        r"\"/logout\"": "\"login.html\"",
        r"'/login'": "'login.html'",
        r"\"/login\"": "\"login.html\"",
        r"'/faculty_dashboard'": "'teacher.html'",
        r"\"/faculty_dashboard\"": "\"teacher.html\"",
        r"'/teacher'": "'teacher.html'",
        r"\"/teacher\"": "\"teacher.html\"",
        r"'/student'": "'student.html'",
        r"\"/student\"": "\"student.html\"",
        r"'/role'": "'role.html'",
        r"\"/role\"": "\"role.html\"",
        r"'/fees'": "'fees.html'",
        r"\"/fees\"": "\"fees.html\"",
        r"'/fee_receipt'": "'FeeReceipt.html'",
        r"\"/fee_receipt\"": "\"FeeReceipt.html\"",
        # Also clean up server root paths mapping
        r"window.location.href\s*=\s*'/'": "window.location.href = 'login.html'",
        r"window.location.href\s*=\s*\"/\"": "window.location.href = \"login.html\"",
    }

    # 5. Process each HTML template file
    for filename in os.listdir(templates_dir):
        if not filename.endswith(".html"):
            continue

        src_path = os.path.join(templates_dir, filename)
        dest_path = os.path.join(output_dir, filename)

        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()

        # A. Replace Jinja2 static URLs
        # e.g., {{ url_for('static', filename='style.css') }} -> static/style.css
        content = re.sub(r"\{\{\s*url_for\('static',\s*filename=['\"](.*?)['\"]\)\s*\}\}", r"static/\1", content)

        # B. Inject config.js before any script tags or before closing head
        config_script = '\n    <script src="config.js"></script>\n'
        if "</head>" in content:
            content = content.replace("</head>", config_script + "</head>")
        else:
            content = config_script + content

        # C. Replace route mappings
        for pattern, replacement in route_mappings.items():
            content = re.sub(pattern, replacement, content)

        # D. Prefix API endpoints with API_BASE_URL
        content = content.replace("'/api/", "API_BASE_URL + '/api/")
        content = content.replace('"/api/', 'API_BASE_URL + "/api/')
        content = content.replace('`/api/', 'API_BASE_URL + `/api/')

        # E. Prefix remote asset routes (static files generated on backend) with API_BASE_URL
        # In student.html, documents are opened from data.calendar etc., which are relative.
        # e.g. window.open(data.calendar, '_blank') -> window.open(API_BASE_URL + data.calendar, '_blank')
        content = content.replace("window.open(data.calendar", "window.open(API_BASE_URL + data.calendar")
        content = content.replace("window.open(data.syllabus", "window.open(API_BASE_URL + data.syllabus")
        content = content.replace("window.open(data.timetable", "window.open(API_BASE_URL + data.timetable")

        # F. Special handling for fill_attendance.html page variables
        if filename == "fill_attendance.html":
            # Replace inline Flask date/slot variables
            content = content.replace('const DATE = "{{ date }}";', "const DATE = new URLSearchParams(window.location.search).get('date') || new Date().toISOString().split('T')[0];")
            content = content.replace('const SLOT = "slot{{ slot }}";', "const SLOT = 'slot' + (new URLSearchParams(window.location.search).get('slot') || '1');")
            
            # Replace inline visual slots
            content = content.replace('<span id="display-date">{{ date }}</span>', '<span id="display-date"></span>')
            content = content.replace('<span id="display-slot">Slot {{ slot }}</span>', '<span id="display-slot"></span>')
            
            # Populate visual date/slot inside init()
            init_target = "async function init() {"
            init_replacement = "async function init() {\n            document.getElementById('display-date').textContent = DATE;\n            document.getElementById('display-slot').textContent = 'Slot ' + SLOT.replace('slot', '');"
            content = content.replace(init_target, init_replacement)

        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)

    # G. Copy login.html to index.html as the main web entry point for Capacitor
    shutil.copy(os.path.join(output_dir, "login.html"), os.path.join(output_dir, "index.html"))

    print(f"Successfully converted templates and static assets inside '{output_dir}/' folder.")

if __name__ == "__main__":
    convert_app()


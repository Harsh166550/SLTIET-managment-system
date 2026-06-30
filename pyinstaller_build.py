import PyInstaller.__main__
import os

if __name__ == '__main__':
    print("Starting PyInstaller build process...")
    PyInstaller.__main__.run([
        'app.py',
        '--onefile',
        '--noconsole',
        '--icon=static/images/logo.ico',
        '--add-data=templates;templates',
        '--add-data=static;static',
        '--add-data=students_data.json;.',
        '--add-data=teachers_data.json;.',
        '--name=SLTIET_UMS_Attendance_Portal',
        '--clean'
    ])
    print("Build process finished.")

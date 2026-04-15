import random
import os
from flask import Flask, render_template, redirect, request, session, jsonify, send_from_directory

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

documents = []

# List of 10 Unique Professional IDs for Residents
AVAILABLE_IDS = [
    "UID-992-XQ-2026", "UID-118-BT-7734", "UID-404-NM-8812", 
    "UID-607-TR-1190", "UID-223-KL-5561", "UID-884-PL-0092", 
    "UID-331-VB-4478", "UID-559-QA-3321", "UID-770-MK-6610", 
    "UID-101-ZZ-9943"
]

# Standard Users Mapping: 'username': ['Unique ID', 'Role']
users = {
    'resident_user': ['UID-101-ZZ-9943', 'Resident']
}

# UPDATED: Offices with Specific Local Government Titles and Hard-to-Guess IDs
admins = {
    "brgy_admin": {"unique_id": 'BGY-882-OFF-VAL', "office": "Barangay Officials"},
    "city_mayor": {"unique_id": 'MAYOR-441-CITY-SEC', "office": "City Mayor"},
    "provincial_gov": {"unique_id": 'GOV-110-PROV-AUTH', "office": "Provincial Governor"},
}

# ---------------- SIGNUP / REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        # We ignore the position from the form and force it to "Resident" for public signup
        position = "Resident" 

        if username in users:
            return "Username already taken! <a href='/register'>Try again</a>"

        assigned_id = random.choice(AVAILABLE_IDS)
        users[username] = [assigned_id, position]
        
        # Auto-login after registration
        session['user'] = username
        session['role'] = position

        return f"""
        <div style="font-family: sans-serif; text-align: center; margin-top: 100px;">
            <div style="display: inline-block; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #ddd; max-width: 400px;">
                <h2 style="color: #0300bd;">Registration Successful!</h2>
                <p>Hello, <strong>{username}</strong>. You are registered as a <strong>Resident</strong>.</p>
                <p>Your Professional Unique ID is:</p>
                <h1 style="background: #f0f2f5; padding: 10px; border: 2px dashed #0300bd;">{assigned_id}</h1>
                <p style="color: red; font-size: 13px;"><strong>Save this ID immediately!</strong> You need it to log in next time.</p>
                <br>
                <a href="/userdashboard" style="background: #0300bd; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Go to My Dashboard</a>
            </div>
        </div>
        """
    return render_template('signup.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        provided_id = request.form['password'] 

        # 1. Check Standard Residents
        if username in users and users[username][0] == provided_id:
            session['user'] = username
            session['role'] = users[username][1]
            return redirect('/userdashboard')

        # 2. Check Specific Government Offices
        if username in admins and admins[username]["unique_id"] == provided_id:
            session["user"] = username
            session["role"] = "office"
            session["office"] = admins[username]["office"]
            
            # Map offices to their respective dashboards
            if session["office"] == "Barangay Officials":
                return redirect('/office1')
            elif session["office"] == "City Mayor":
                return redirect('/office2')
            elif session["office"] == "Provincial Governor":
                return redirect('/office3')

        return render_template('login.html', message='Invalid ID or Username')

    return render_template('login.html')

# ---------------- DASHBOARDS ----------------
@app.route('/userdashboard')
def userdashboard():
    if "user" not in session or session.get("role") != "Resident":
        return redirect('/login')
    return render_template('userdashboard.html')

@app.route('/office1') # Barangay Officials
def office1():
    if session.get("office") != "Barangay Officials": return redirect('/login')
    return render_template('admindashboard.html')

@app.route('/office2') # City Mayor
def office2():
    if session.get("office") != "City Mayor": return redirect('/login')
    return render_template('2admindashboard.html')

@app.route('/office3') # Provincial Governor
def office3():
    if session.get("office") != "Provincial Governor": return redirect('/login')
    return render_template('3admindashboard.html')

# (Upload and Process logic remain the same, ensuring 'current_office' 1-3 matches the sequence above)

if __name__ == '__main__':
    app.run(debug=True)
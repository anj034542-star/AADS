import random
import os
from flask import Flask, render_template, redirect, request, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename

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

AVAILABLE_IDS = [
    "UID-992-XQ-2026", "UID-118-BT-7734", "UID-404-NM-8812", 
    "UID-607-TR-1190", "UID-223-KL-5561", "UID-884-PL-0092", 
    "UID-331-VB-4478", "UID-559-QA-3321", "UID-770-MK-6610", 
    "UID-101-ZZ-9943"
]

users = {
    'resident_user': ['UID-101-ZZ-9943', 'Resident']
}

admins = {
    "brgy_admin": {"unique_id": 'BGY-882-OFF-VAL', "office": "Barangay Officials"},
    "city_mayor": {"unique_id": 'MAYOR-441-CITY-SEC', "office": "City Mayor"},
    "provincial_gov": {"unique_id": 'GOV-110-PROV-AUTH', "office": "Provincial Governor"},
}

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        position = "Resident"

        if username in users:
            return "Username already taken! <a href='/register'>Try again</a>"

        assigned_id = random.choice(AVAILABLE_IDS)
        users[username] = [assigned_id, position]

        session['user'] = username
        session['role'] = position

        return f"Registered! Your ID: {assigned_id} <a href='/userdashboard'>Go to dashboard</a>"

    return render_template('sign up.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        provided_id = request.form['password']

        if username in users and users[username][0] == provided_id:
            session['user'] = username
            session['role'] = users[username][1]
            return redirect('/userdashboard')

        if username in admins and admins[username]["unique_id"] == provided_id:
            session["user"] = username
            session["role"] = "office"
            session["office"] = admins[username]["office"]

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

@app.route('/office1')
def office1():
    if session.get("office") != "Barangay Officials":
        return redirect('/login')
    return render_template('admindashboard.html')

# ---------------- 🏛️ OFFICE 2 (CITY MAYOR) ----------------
@app.route('/office2')
def office2():
    if session.get("office") != "City Mayor":
        return redirect('/login')
    return render_template('2admindashboard.html')


@app.route('/office2/documents')
def office2_documents():
    if session.get("office") != "City Mayor":
        return jsonify({"error": "Unauthorized"})

    # Only Barangay-approved documents
    filtered = [doc for doc in documents if doc.get("status") == "APPROVED BY BARANGAY"]
    return jsonify(filtered)


@app.route('/mayor/approve/<filename>', methods=['POST'])
def mayor_approve(filename):
    if session.get("office") != "City Mayor":
        return jsonify({"error": "Unauthorized"})

    for doc in documents:
        if doc["filename"] == filename:
            doc["status"] = "APPROVED BY MAYOR"
            return jsonify({"success": True})

    return jsonify({"error": "Document not found"})


@app.route('/mayor/decline/<filename>', methods=['POST'])
def mayor_decline(filename):
    if session.get("office") != "City Mayor":
        return jsonify({"error": "Unauthorized"})

    for doc in documents:
        if doc["filename"] == filename:
            doc["status"] = "DECLINED BY MAYOR"
            return jsonify({"success": True})

    return jsonify({"error": "Document not found"})


# ---------------- OFFICE 3 ----------------
@app.route('/office3')
def office3():
    if session.get("office") != "Provincial Governor":
        return redirect('/login')
    return render_template('3admindashboard.html')


@app.route('/office3/documents')
def office3_documents():
    if session.get("office") != "Provincial Governor":
        return jsonify({"error": "Unauthorized"})

    # Only Mayor-approved documents are visible here
    filtered = [doc for doc in documents if doc.get("status") == "APPROVED BY MAYOR"]
    return jsonify(filtered)


@app.route('/governor/approve/<filename>', methods=['POST'])
def governor_approve(filename):
    if session.get("office") != "Provincial Governor":
        return jsonify({"error": "Unauthorized"})

    for doc in documents:
        if doc["filename"] == filename:
            doc["status"] = "APPROVED BY GOVERNOR (FINAL)"
            return jsonify({"success": True})

    return jsonify({"error": "Document not found"})


@app.route('/governor/decline/<filename>', methods=['POST'])
def governor_decline(filename):
    if session.get("office") != "Provincial Governor":
        return jsonify({"error": "Unauthorized"})

    for doc in documents:
        if doc["filename"] == filename:
            doc["status"] = "DECLINED BY GOVERNOR"
            return jsonify({"success": True})

    return jsonify({"error": "Document not found"})

# ---------------- FILE UPLOAD ----------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    title = request.form.get('title')
    desc = request.form.get('desc')
    office = request.form.get('office')

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if not title or not desc or not office:
        return jsonify({"error": "Missing form data"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter = 1
        while os.path.exists(filepath):
            name, ext = filename.rsplit('.', 1)
            filename = f"{name}_{counter}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1

        file.save(filepath)

        import random

        tracking_id = f"TRK-{random.randint(10000,99999)}"

        doc = {
            "tracking_id": tracking_id,   
            "title": title,
            "desc": desc,
            "office": office,
            "target_office": office,
            "filename": filename,
            "status": "PENDING"
        }

        documents.append(doc)

        return jsonify(doc)

    return jsonify({"error": "Invalid file type"})

# ---------------- GET DOCUMENTS ----------------
@app.route('/documents')
def get_documents():
    return jsonify(documents)

# ---------------- OFFICE 1 ----------------
@app.route('/office1/documents')
def office1_documents():
    if session.get("office") != "Barangay Officials":
        return jsonify({"error": "Unauthorized"})
    return jsonify(documents)

@app.route('/approve/<filename>', methods=['POST'])
def approve_document(filename):
    if session.get("office") != "Barangay Officials":
        return jsonify({"error": "Unauthorized"})

    for doc in documents:
        if doc["filename"] == filename:
            doc["status"] = "APPROVED BY BARANGAY"
            return jsonify({"success": True})

    return jsonify({"error": "Document not found"})

@app.route('/decline/<filename>', methods=['POST'])
def decline_document(filename):
    if session.get("office") != "Barangay Officials":
        return jsonify({"error": "Unauthorized"})

    for doc in documents:
        if doc["filename"] == filename:
            doc["status"] = "DECLINED BY BARANGAY"
            return jsonify({"success": True})

    return jsonify({"error": "Document not found"})

# ---------------- FILE VIEW ----------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)

import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, session, send_from_directory, jsonify, make_response
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Admin, Document, AVAILABLE_IDS, generate_tracking_id
from utils import allowed_file
import random

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create tables and seed admin accounts (run once)
with app.app_context():
    db.create_all()
    # Seed default admins if not already present
    default_admins = {
        "brgy_admin": {"unique_id": "BGY-882-OFF-VAL", "office": "Barangay Officials"},
        "city_mayor": {"unique_id": "MAYOR-441-CITY-SEC", "office": "City Mayor"},
        "provincial_gov": {"unique_id": "GOV-110-PROV-AUTH", "office": "Provincial Governor"},
    }
    for username, data in default_admins.items():
        if not Admin.query.filter_by(username=username).first():
            admin = Admin(username=username, unique_id=data["unique_id"], office=data["office"])
            db.session.add(admin)
    db.session.commit()

# ------------------- AUTH ROUTES -------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            return "Username already taken! <a href='/register'>Try again</a>"
        assigned_id = random.choice(AVAILABLE_IDS)
        user = User(username=username, unique_id=assigned_id, role='Resident')
        db.session.add(user)
        db.session.commit()
        session['user'] = username
        session['role'] = 'Resident'
        return f"Registered! Your ID: {assigned_id} <a href='/userdashboard'>Go to dashboard</a>"
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        provided_id = request.form['password']

        # Check resident
        user = User.query.filter_by(username=username, unique_id=provided_id).first()
        if user:
            session['user'] = user.username
            session['role'] = user.role
            return redirect('/userdashboard')

        # Check admin
        admin = Admin.query.filter_by(username=username, unique_id=provided_id).first()
        if admin:
            session['user'] = admin.username
            session['role'] = 'office'
            session['office'] = admin.office
            if admin.office == "Barangay Officials":
                return redirect('/office1')
            elif admin.office == "City Mayor":
                return redirect('/office2')
            elif admin.office == "Provincial Governor":
                return redirect('/office3')

        return render_template('login.html', message='Invalid ID or Username')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect('/login?logout=success'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

# ------------------- DASHBOARDS -------------------
@app.route('/userdashboard')
def userdashboard():
    if "user" not in session:
        return redirect('/login')
    return render_template('userdashboard.html')

@app.route('/office1')
def office1():
    if session.get("office") != "Barangay Officials":
        return redirect('/login')
    return render_template('admindashboard.html')

@app.route('/office2')
def office2():
    if session.get("office") != "City Mayor":
        return redirect('/login')
    return render_template('2admindashboard.html')

@app.route('/office3')
def office3():
    if session.get("office") != "Provincial Governor":
        return redirect('/login')
    return render_template('3admindashboard.html')

# ------------------- REPORTS DASHBOARD -------------------
@app.route('/reports')
def reporting_dashboard():
    if "user" not in session:
        return redirect('/login')
    return render_template('DocumentReports.html')

@app.route('/api/all_reports')
def get_all_reports():
    if "user" not in session:
        return jsonify([])
    docs = Document.query.all()
    return jsonify([doc.to_dict() for doc in docs])

# ------------------- DOCUMENT ACTIONS -------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    title = request.form.get('title')
    desc = request.form.get('desc')
    office = request.form.get('office')

    if session.get('role') == 'Resident':
        office = "Office 1"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter = 1
        base_filename = filename
        while os.path.exists(filepath):
            name, ext = base_filename.rsplit('.', 1)
            filename = f"{name}_{counter}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
        file.save(filepath)

        tracking_id = generate_tracking_id()
        doc = Document(
            tracking_id=tracking_id,
            title=title,
            description=desc,
            office=office,
            target_office=office,
            filename=filename,
            status='PENDING',
            uploaded_by=session.get('user')
        )
        db.session.add(doc)
        db.session.commit()
        return jsonify(doc.to_dict())
    return jsonify({"error": "Invalid file type"})

# ---- Office document lists ----
@app.route('/office1/documents')
def office1_documents():
    if session.get("office") != "Barangay Officials":
        return jsonify([])
    docs = Document.query.filter(
        Document.target_office == "Office 1",
        ~Document.status.in_(["APPROVED BY BARANGAY", "DECLINED BY BARANGAY"])
    ).all()
    return jsonify([doc.to_dict() for doc in docs])

@app.route('/office2/documents')
def office2_documents():
    if session.get("office") != "City Mayor":
        return jsonify([])
    docs = Document.query.filter(
        Document.target_office == "Office 2",
        ~Document.status.in_(["APPROVED BY MAYOR", "DECLINED BY MAYOR"])
    ).all()
    return jsonify([doc.to_dict() for doc in docs])

@app.route('/office3/documents')
def office3_documents():
    if session.get("office") != "Provincial Governor":
        return jsonify([])
    docs = Document.query.filter(
        Document.target_office == "Office 3",
        ~Document.status.in_(["APPROVED BY GOVERNOR (FINAL)", "DECLINED BY GOVERNOR"])
    ).all()
    return jsonify([doc.to_dict() for doc in docs])

# ---- Approval routes ----
@app.route('/approve/<filename>', methods=['POST'])
def approve_brgy(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.status = "APPROVED BY BARANGAY"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})

@app.route('/mayor/approve/<filename>', methods=['POST'])
def approve_mayor(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.status = "APPROVED BY MAYOR"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})

@app.route('/governor/approve/<filename>', methods=['POST'])
def approve_gov(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.status = "APPROVED BY GOVERNOR (FINAL)"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})

# ---- Decline routes ----
@app.route('/decline/<filename>', methods=['POST'])
def decline_brgy(filename):
    reason = request.json.get('reason', 'No reason provided')
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.status = "DECLINED BY BARANGAY"
        doc.decline_reason = reason
        doc.declined_by = "Barangay Officials"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})

@app.route('/mayor/decline/<filename>', methods=['POST'])
def decline_mayor(filename):
    reason = request.json.get('reason', 'No reason provided')
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.status = "DECLINED BY MAYOR"
        doc.decline_reason = reason
        doc.declined_by = "City Mayor"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})

@app.route('/governor/decline/<filename>', methods=['POST'])
def decline_gov(filename):
    reason = request.json.get('reason', 'No reason provided')
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.status = "DECLINED BY GOVERNOR"
        doc.decline_reason = reason
        doc.declined_by = "Provincial Governor"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})

# ---- Forwarding routes ----
@app.route('/forward_to_mayor/<tracking_id>', methods=['POST'])
def forward_to_mayor(tracking_id):
    doc = Document.query.filter_by(tracking_id=tracking_id, status="APPROVED BY BARANGAY").first()
    if doc:
        doc.target_office = "Office 2"
        doc.status = "PENDING (MAYOR)"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not eligible for forwarding"})

@app.route('/forward_to_governor/<tracking_id>', methods=['POST'])
def forward_to_governor(tracking_id):
    doc = Document.query.filter_by(tracking_id=tracking_id, status="APPROVED BY MAYOR").first()
    if doc:
        doc.target_office = "Office 3"
        doc.status = "PENDING (GOVERNOR)"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Not eligible for forwarding"})

# ---- File serving ----
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
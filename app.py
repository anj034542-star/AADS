import os
import random
from datetime import datetime
from flask import Flask, render_template, redirect, request, session, send_from_directory, jsonify, make_response
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

# ------------------ CONFIGURATION ------------------
app = Flask(__name__)

# Use /tmp for both database and uploads (Vercel serverless)
tmp_dir = '/tmp'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{tmp_dir}/app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', f'{tmp_dir}/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'doc', 'docx', 'xls', 'xlsx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# ------------------ MODELS (simplified) ------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), default='Resident')

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    office = db.Column(db.String(100), nullable=False)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    office = db.Column(db.String(50))
    target_office = db.Column(db.String(50), default='Office 1')
    filename = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='PENDING')
    decline_reason = db.Column(db.Text, nullable=True)
    declined_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.String(80))

    def to_dict(self):
        return {
            'tracking_id': self.tracking_id,
            'title': self.title,
            'desc': self.description,
            'office': self.office,
            'target_office': self.target_office,
            'filename': self.filename,
            'status': self.status,
            'decline_reason': self.decline_reason,
            'declined_by': self.declined_by,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }

# ------------------ HELPER FUNCTIONS ------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_tracking_id():
    return f"TRK-{random.randint(10000,99999)}"

# ------------------ INITIALIZE DB & ADMINS ------------------
with app.app_context():
    db.create_all()
    # Seed default admins (only if not exists)
    default_admins = {
        "brgy_admin": {"unique_id": "BGY-882-OFF-VAL", "office": "Barangay Officials"},
        "city_mayor": {"unique_id": "MAYOR-441-CITY-SEC", "office": "City Mayor"},
        "provincial_gov": {"unique_id": "GOV-110-PROV-AUTH", "office": "Provincial Governor"},
    }
    for username, data in default_admins.items():
        if not Admin.query.filter_by(username=username).first():
            db.session.add(Admin(username=username, unique_id=data["unique_id"], office=data["office"]))
    db.session.commit()

# ------------------ ALL YOUR ROUTES (unchanged) ------------------
# (Copy your existing routes from the previous app.py – they remain identical)
# The only difference is that the Document model uses SQLAlchemy instead of a list.
# Make sure to replace the old in‑memory `documents` list with database queries.
# I'll include the complete route set from the refactored version I gave earlier.

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            return "Username already taken! <a href='/register'>Try again</a>"
        assigned_id = random.choice(["UID-992-XQ-2026", "UID-118-BT-7734", "UID-404-NM-8812", 
                                     "UID-607-TR-1190", "UID-223-KL-5561", "UID-884-PL-0092", 
                                     "UID-331-VB-4478", "UID-559-QA-3321", "UID-770-MK-6610", 
                                     "UID-101-ZZ-9943"])
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
        user = User.query.filter_by(username=username, unique_id=provided_id).first()
        if user:
            session['user'] = user.username
            session['role'] = user.role
            return redirect('/userdashboard')
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
    return resp

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
        base = filename
        while os.path.exists(filepath):
            name, ext = base.rsplit('.', 1)
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# This is required for Vercel – it looks for a variable named 'app'
# We already have 'app' from Flask(__name__)
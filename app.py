import os
import random
from abc import ABC, abstractmethod
from datetime import datetime
from flask import Flask, render_template, redirect, request, session, send_from_directory, jsonify, make_response, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

# ------------------ CONFIGURATION ------------------
app = Flask(__name__)
tmp_dir = '/tmp'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{tmp_dir}/app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', f'{tmp_dir}/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'doc', 'docx', 'excel', 'xlsx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)


# ========================= OOP LAYER =========================
# 1. ABSTRACT CLASS (Abstraction + Inheritance base)
class BaseEntity(ABC):
    """Abstract base class for all domain entities."""
    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def save(self):
        pass


# 2. ENCAPSULATION: Models with behaviour (getters/setters where needed)
class User(db.Model, BaseEntity):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), default='Resident')
    email = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'username': self.username,
            'unique_id': self.unique_id,
            'role': self.role,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'zip_code': self.zip_code
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class Admin(db.Model, BaseEntity):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    office = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {'username': self.username, 'unique_id': self.unique_id, 'office': self.office}

    def save(self):
        db.session.add(self)
        db.session.commit()


class Document(db.Model, BaseEntity):
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

    def save(self):
        db.session.add(self)
        db.session.commit()

    # Encapsulated state change methods
    def approve_by_brgy(self):
        self.status = "APPROVED BY BARANGAY"
        self.save()

    def approve_by_mayor(self):
        self.status = "APPROVED BY MAYOR"
        self.save()

    def approve_by_governor(self):
        self.status = "APPROVED BY GOVERNOR (FINAL)"
        self.save()

    def decline_by_brgy(self, reason):
        self.status = "DECLINED BY BARANGAY"
        self.decline_reason = reason
        self.declined_by = "Barangay Officials"
        self.save()

    def decline_by_mayor(self, reason):
        self.status = "DECLINED BY MAYOR"
        self.decline_reason = reason
        self.declined_by = "City Mayor"
        self.save()

    def decline_by_governor(self, reason):
        self.status = "DECLINED BY GOVERNOR"
        self.decline_reason = reason
        self.declined_by = "Provincial Governor"
        self.save()

    def forward_to_mayor(self):
        if self.status == "APPROVED BY BARANGAY":
            self.target_office = "Office 2"
            self.status = "PENDING (MAYOR)"
            self.save()
            return True
        return False

    def forward_to_governor(self):
        if self.status == "APPROVED BY MAYOR":
            self.target_office = "Office 3"
            self.status = "PENDING (GOVERNOR)"
            self.save()
            return True
        return False


# 3. SERVICE CLASSES (Encapsulation of business logic)
class TrackingIdGenerator:
    """Encapsulates tracking ID generation."""
    @staticmethod
    def generate():
        return f"TRK-{random.randint(10000, 99999)}"


class FileValidator:
    """Encapsulates file validation logic."""
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def secure_save(file, upload_folder):
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        counter = 1
        base = filename
        while os.path.exists(filepath):
            name, ext = base.rsplit('.', 1)
            filename = f"{name}_{counter}.{ext}"
            filepath = os.path.join(upload_folder, filename)
            counter += 1
        file.save(filepath)
        return filename


class UniqueIdAssigner:
    """Encapsulates the assignment of a random unique ID to new users."""
    _ID_POOL = [
        "UID-992-XQ-2026", "UID-118-BT-7734", "UID-404-NM-8812",
        "UID-607-TR-1190", "UID-223-KL-5561", "UID-884-PL-0092",
        "UID-331-VB-4478", "UID-559-QA-3321", "UID-770-MK-6610",
        "UID-101-ZZ-9943", "UID-778-PK-9031", "UID-501-VN-3158",
        "UID-457-XJ-8213", "UID-182-WP-0492", "UID-839-LK-5740",
        "UID-204-RA-6651", "UID-571-ND-3986", "UID-690-MB-1127",
        "UID-925-CV-9094", "UID-346-QT-2703", "UID-778-BG-4568",
        "UID-013-SF-6245", "UID-462-HU-8819", "UID-508-EY-3307",
        "UID-639-DT-7432", "UID-297-OV-1850", "UID-841-GJ-5623",
        "UID-115-ZM-6974", "UID-674-AP-9081", "UID-430-FX-2746",
        "UID-956-KW-4115", "UID-289-LC-3392", "UID-573-BV-7803",
        "UID-702-NR-2168", "UID-817-JE-0457", "UID-038-HQ-8940",
        "UID-264-SY-5093", "UID-496-UT-6721", "UID-141-WA-9567",
        "UID-685-GP-3084", "UID-329-EC-7835", "UID-954-MZ-4002",
        "UID-470-AH-6378", "UID-613-DJ-1594", "UID-226-RO-2460"
    ]

    @classmethod
    def assign(cls):
        return random.choice(cls._ID_POOL)


# 4. ABSTRACT CLASS + INHERITANCE + POLYMORPHISM for office handlers
class OfficeHandler(ABC):
    """Abstract handler for different government offices."""
    def __init__(self, office_name, target_office_code):
        self._office_name = office_name      # encapsulated
        self._target_office_code = target_office_code

    @abstractmethod
    def get_documents_query(self):
        pass

    @abstractmethod
    def approve(self, document):
        pass

    @abstractmethod
    def decline(self, document, reason):
        pass

    def get_office_name(self):
        return self._office_name


class BarangayHandler(OfficeHandler):
    def __init__(self):
        super().__init__("Barangay Officials", "Office 1")

    def get_documents_query(self):
        return Document.query.filter(
            Document.target_office == self._target_office_code,
            ~Document.status.in_(["APPROVED BY BARANGAY", "DECLINED BY BARANGAY"])
        )

    def approve(self, document):
        document.approve_by_brgy()

    def decline(self, document, reason):
        document.decline_by_brgy(reason)


class MayorHandler(OfficeHandler):
    def __init__(self):
        super().__init__("City Mayor", "Office 2")

    def get_documents_query(self):
        return Document.query.filter(
            Document.target_office == self._target_office_code,
            ~Document.status.in_(["APPROVED BY MAYOR", "DECLINED BY MAYOR"])
        )

    def approve(self, document):
        document.approve_by_mayor()

    def decline(self, document, reason):
        document.decline_by_mayor(reason)


class GovernorHandler(OfficeHandler):
    def __init__(self):
        super().__init__("Provincial Governor", "Office 3")

    def get_documents_query(self):
        return Document.query.filter(
            Document.target_office == self._target_office_code,
            ~Document.status.in_(["APPROVED BY GOVERNOR (FINAL)", "DECLINED BY GOVERNOR"])
        )

    def approve(self, document):
        document.approve_by_governor()

    def decline(self, document, reason):
        document.decline_by_governor(reason)


# 5. SERVICE CLASS FOR USER AUTHENTICATION & REGISTRATION
class UserService:
    @staticmethod
    def register_user(username, email, age, gender, zip_code):
        if User.query.filter_by(username=username).first():
            return None, "Username already taken!"
        assigned_id = UniqueIdAssigner.assign()
        user = User(
            username=username,
            unique_id=assigned_id,
            role='Resident',
            email=email,
            age=int(age),
            gender=gender,
            zip_code=zip_code
        )
        user.save()
        return assigned_id, None

    @staticmethod
    def authenticate_user(username, provided_id):
        user = User.query.filter_by(username=username, unique_id=provided_id).first()
        if user:
            return user, 'user'
        admin = Admin.query.filter_by(username=username, unique_id=provided_id).first()
        if admin:
            return admin, 'admin'
        return None, None


# ===================== ORIGINAL HELPER FUNCTIONS (unchanged signatures) =====================
def allowed_file(filename):
    """Kept exactly as before, now delegates to FileValidator."""
    return FileValidator.allowed_file(filename, app.config['ALLOWED_EXTENSIONS'])


def generate_tracking_id():
    """Kept exactly as before, now delegates to TrackingIdGenerator."""
    return TrackingIdGenerator.generate()


# ------------------ INITIALIZE DB & ADMINS (unchanged behaviour) ------------------
with app.app_context():
    db.create_all()
    default_admins = {
        "brgy_admin": {"unique_id": "BGY-882-OFF-VAL", "office": "Barangay Officials"},
        "city_mayor": {"unique_id": "MAYOR-441-CITY-SEC", "office": "City Mayor"},
        "provincial_gov": {"unique_id": "GOV-110-PROV-AUTH", "office": "Provincial Governor"},
    }
    for username, data in default_admins.items():
        if not Admin.query.filter_by(username=username).first():
            admin = Admin(username=username, unique_id=data["unique_id"], office=data["office"])
            admin.save()


# ===================== EXISTING ROUTE FUNCTIONS (unchanged signatures, internal OOP delegation) =====================
@app.route('/')
def home():
    if 'username' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        zip_code = request.form.get('zip')

        if not all([username, email, age, gender, zip_code]):
            return "All fields are required. <a href='/register'>Go back</a>"

        assigned_id, error = UserService.register_user(username, email, age, gender, zip_code)
        if error:
            return f"{error} <a href='/register'>Try again</a>"

        flash(f'Registration successful! Your Unique ID is: {assigned_id}. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        provided_id = request.form['password']
        user_or_admin, auth_type = UserService.authenticate_user(username, provided_id)

        if auth_type == 'user':
            session['user'] = user_or_admin.username
            session['role'] = user_or_admin.role
            return redirect('/userdashboard')
        elif auth_type == 'admin':
            session['user'] = user_or_admin.username
            session['role'] = 'office'
            session['office'] = user_or_admin.office
            if user_or_admin.office == "Barangay Officials":
                return redirect('/office1')
            elif user_or_admin.office == "City Mayor":
                return redirect('/office2')
            elif user_or_admin.office == "Provincial Governor":
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
        filename = FileValidator.secure_save(file, app.config['UPLOAD_FOLDER'])
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
        doc.save()
        return jsonify(doc.to_dict())
    return jsonify({"error": "Invalid file type"})


@app.route('/office1/documents')
def office1_documents():
    if session.get("office") != "Barangay Officials":
        return jsonify([])
    handler = BarangayHandler()
    docs = handler.get_documents_query().all()
    return jsonify([doc.to_dict() for doc in docs])


@app.route('/office2/documents')
def office2_documents():
    if session.get("office") != "City Mayor":
        return jsonify([])
    handler = MayorHandler()
    docs = handler.get_documents_query().all()
    return jsonify([doc.to_dict() for doc in docs])


@app.route('/office3/documents')
def office3_documents():
    if session.get("office") != "Provincial Governor":
        return jsonify([])
    handler = GovernorHandler()
    docs = handler.get_documents_query().all()
    return jsonify([doc.to_dict() for doc in docs])


@app.route('/approve/<filename>', methods=['POST'])
def approve_brgy(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.approve_by_brgy()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})


@app.route('/mayor/approve/<filename>', methods=['POST'])
def approve_mayor(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.approve_by_mayor()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})


@app.route('/governor/approve/<filename>', methods=['POST'])
def approve_gov(filename):
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.approve_by_governor()
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})


@app.route('/decline/<filename>', methods=['POST'])
def decline_brgy(filename):
    reason = request.json.get('reason', 'No reason provided')
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.decline_by_brgy(reason)
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})


@app.route('/mayor/decline/<filename>', methods=['POST'])
def decline_mayor(filename):
    reason = request.json.get('reason', 'No reason provided')
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.decline_by_mayor(reason)
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})


@app.route('/governor/decline/<filename>', methods=['POST'])
def decline_gov(filename):
    reason = request.json.get('reason', 'No reason provided')
    doc = Document.query.filter_by(filename=filename).first()
    if doc:
        doc.decline_by_governor(reason)
        return jsonify({"success": True})
    return jsonify({"error": "Not found"})


@app.route('/forward_to_mayor/<tracking_id>', methods=['POST'])
def forward_to_mayor(tracking_id):
    doc = Document.query.filter_by(tracking_id=tracking_id, status="APPROVED BY BARANGAY").first()
    if doc and doc.forward_to_mayor():
        return jsonify({"success": True})
    return jsonify({"error": "Not eligible for forwarding"})


@app.route('/forward_to_governor/<tracking_id>', methods=['POST'])
def forward_to_governor(tracking_id):
    doc = Document.query.filter_by(tracking_id=tracking_id, status="APPROVED BY MAYOR").first()
    if doc and doc.forward_to_governor():
        return jsonify({"success": True})
    return jsonify({"error": "Not eligible for forwarding"})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------ END OF FILE ------------------

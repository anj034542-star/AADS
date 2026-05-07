import os
import random
from abc import ABC, abstractmethod
from datetime import datetime
from flask import Flask, render_template, redirect, request, session, send_from_directory, jsonify, make_response, flash, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from zoneinfo import ZoneInfo


# ------------------ ABSTRACT BASE CLASS (Abstraction & Inheritance) ------------------
class BaseDocumentHandler(ABC):
    @abstractmethod
    def approve(self, document):
        pass

    @abstractmethod
    def decline(self, document, reason):
        pass

    @abstractmethod
    def get_office_name(self):
        pass


# ------------------ CONCRETE HANDLERS (Inheritance & Polymorphism) ------------------
class BarangayHandler(BaseDocumentHandler):
    def approve(self, document):
        document.status = "APPROVED BY BARANGAY"
        document.process_end_time = get_ph_time()
        db.session.commit()

    def decline(self, document, reason):
        document.status = "DECLINED BY BARANGAY"
        document.decline_reason = reason
        document.declined_by = "Barangay Officials"
        document.process_end_time = get_ph_time()
        db.session.commit()

    def get_office_name(self):
        return "Barangay Officials"


class MayorHandler(BaseDocumentHandler):
    def approve(self, document):
        document.status = "APPROVED BY MAYOR"
        document.process_end_time = get_ph_time()
        db.session.commit()

    def decline(self, document, reason):
        document.status = "DECLINED BY MAYOR"
        document.decline_reason = reason
        document.declined_by = "City Mayor"
        document.process_end_time = get_ph_time()
        db.session.commit()

    def get_office_name(self):
        return "City Mayor"


class GovernorHandler(BaseDocumentHandler):
    def approve(self, document):
        document.status = "APPROVED BY GOVERNOR (FINAL)"
        document.process_end_time = get_ph_time()
        db.session.commit()

    def decline(self, document, reason):
        document.status = "DECLINED BY GOVERNOR"
        document.decline_reason = reason
        document.declined_by = "Provincial Governor"
        document.process_end_time = get_ph_time()
        db.session.commit()

    def get_office_name(self):
        return "Provincial Governor"


# ------------------ HELPER FUNCTION (remains unchanged) ------------------
def get_ph_time():
    return datetime.now(ZoneInfo('Asia/Manila'))


# ------------------ MAIN APPLICATION CLASS (Encapsulation, Constructor, Object) ------------------
class DocumentTrackingSystem:
    """Main OOP class that encapsulates the entire Flask application."""

    def __init__(self):
        """Constructor: initialises Flask app, configuration, database, and default admins."""
        self.app = Flask(__name__)
        tmp_dir = '/tmp'
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{tmp_dir}/app.db')
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', f'{tmp_dir}/uploads')
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        self.app.config['ALLOWED_EXTENSIONS'] = {'doc', 'docx', 'excel', 'xlsx'}

        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)

        self.db = SQLAlchemy(self.app)

        # ------------------ MODELS (Encapsulation via properties) ------------------
        class BaseModel(self.db.Model):
            __abstract__ = True

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        class User(BaseModel):
            __tablename__ = 'users'
            id = self.db.Column(self.db.Integer, primary_key=True)
            username = self.db.Column(self.db.String(80), unique=True, nullable=False)
            unique_id = self.db.Column(self.db.String(50), unique=True, nullable=False)
            role = self.db.Column(self.db.String(20), default='Resident')
            email = self.db.Column(self.db.String(120), nullable=False)
            age = self.db.Column(self.db.Integer, nullable=False)
            gender = self.db.Column(self.db.String(10), nullable=False)
            zip_code = self.db.Column(self.db.String(10), nullable=False)

            @property
            def full_name(self):
                return self.username

            def __repr__(self):
                return f"<User {self.username}>"

        class Admin(BaseModel):
            __tablename__ = 'admins'
            id = self.db.Column(self.db.Integer, primary_key=True)
            username = self.db.Column(self.db.String(80), unique=True, nullable=False)
            unique_id = self.db.Column(self.db.String(50), unique=True, nullable=False)
            office = self.db.Column(self.db.String(100), nullable=False)

            def __repr__(self):
                return f"<Admin {self.username} ({self.office})>"

        class Document(BaseModel):
            __tablename__ = 'documents'
            id = self.db.Column(self.db.Integer, primary_key=True)
            tracking_id = self.db.Column(self.db.String(20), unique=True, nullable=False)
            title = self.db.Column(self.db.String(200), nullable=False)
            description = self.db.Column(self.db.Text)
            office = self.db.Column(self.db.String(50))
            target_office = self.db.Column(self.db.String(50), default='Office 1')
            filename = self.db.Column(self.db.String(200), nullable=False)
            status = self.db.Column(self.db.String(50), default='PENDING')
            decline_reason = self.db.Column(self.db.Text, nullable=True)
            declined_by = self.db.Column(self.db.String(100), nullable=True)
            created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)
            uploaded_by = self.db.Column(self.db.String(80))
            process_start_time = self.db.Column(self.db.DateTime, nullable=True)
            process_end_time = self.db.Column(self.db.DateTime, nullable=True)

            def to_dict(self):
                duration = None
                if self.process_start_time and self.process_end_time:
                    delta = self.process_end_time - self.process_start_time
                    duration = delta.total_seconds()
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
                    'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
                    'process_start_time': self.process_start_time.strftime('%Y-%m-%d %H:%M:%S') if self.process_start_time else None,
                    'process_end_time': self.process_end_time.strftime('%Y-%m-%d %H:%M:%S') if self.process_end_time else None,
                    'processing_duration_seconds': duration,
                }

        self.User = User
        self.Admin = Admin
        self.Document = Document
        self.BaseModel = BaseModel

        # ------------------ SERVICE CLASSES (Encapsulation) ------------------
        class DocumentService:
            @staticmethod
            def generate_tracking_id():
                return f"TRK-{random.randint(10000, 99999)}"

            @staticmethod
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.app.config['ALLOWED_EXTENSIONS']

            @staticmethod
            def save_upload(file, title, desc, office, username):
                filename = secure_filename(file.filename)
                filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                counter = 1
                base = filename
                while os.path.exists(filepath):
                    name, ext = base.rsplit('.', 1)
                    filename = f"{name}_{counter}.{ext}"
                    filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    counter += 1
                file.save(filepath)
                tracking_id = DocumentService.generate_tracking_id()
                doc = self.Document(
                    tracking_id=tracking_id,
                    title=title,
                    description=desc,
                    office=office,
                    target_office=office,
                    filename=filename,
                    status='PENDING',
                    uploaded_by=username,
                    process_start_time=get_ph_time()
                )
                self.db.session.add(doc)
                self.db.session.commit()
                return doc

            @staticmethod
            def get_documents_by_office(office_name, exclude_statuses):
                if office_name == "Barangay Officials":
                    office_col = "Office 1"
                elif office_name == "City Mayor":
                    office_col = "Office 2"
                elif office_name == "Provincial Governor":
                    office_col = "Office 3"
                else:
                    return []
                return self.Document.query.filter(
                    self.Document.target_office == office_col,
                    ~self.Document.status.in_(exclude_statuses)
                ).all()

            @staticmethod
            def forward_to_next_office(tracking_id, current_status, new_target, new_status):
                doc = self.Document.query.filter_by(tracking_id=tracking_id, status=current_status).first()
                if doc:
                    doc.target_office = new_target
                    doc.status = new_status
                    self.db.session.commit()
                    return True
                return False

        class AuthService:
            @staticmethod
            def register_user(username, email, age, gender, zip_code):
                if self.User.query.filter_by(username=username).first():
                    return None, "Username already taken!"
                assigned_id = random.choice([
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
                ])
                user = self.User(username=username, unique_id=assigned_id, role='Resident',
                                 email=email, age=int(age), gender=gender, zip_code=zip_code)
                self.db.session.add(user)
                self.db.session.commit()
                return assigned_id, None

            @staticmethod
            def login_user(username, unique_id):
                user = self.User.query.filter_by(username=username, unique_id=unique_id).first()
                if user:
                    return user, 'user'
                admin = self.Admin.query.filter_by(username=username, unique_id=unique_id).first()
                if admin:
                    return admin, 'admin'
                return None, None

        self.DocumentService = DocumentService
        self.AuthService = AuthService

        # ------------------ INITIALISE DB & ADMINS ------------------
        with self.app.app_context():
            self.db.create_all()
            default_admins = {
                "brgy_admin": {"unique_id": "BGY-882-OFF-VAL", "office": "Barangay Officials"},
                "city_mayor": {"unique_id": "MAYOR-441-CITY-SEC", "office": "City Mayor"},
                "provincial_gov": {"unique_id": "GOV-110-PROV-AUTH", "office": "Provincial Governor"},
            }
            for username, data in default_admins.items():
                if not self.Admin.query.filter_by(username=username).first():
                    self.db.session.add(self.Admin(username=username, unique_id=data["unique_id"], office=data["office"]))
            self.db.session.commit()

        # ------------------ ROUTES (methods of the class) ------------------
        self._register_routes()

    def _register_routes(self):
        """Register all Flask routes (preserving original functionality)."""

        @self.app.route('/')
        def home():
            if 'username' in session:
                if session.get('role') == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('user_dashboard'))
            return redirect(url_for('login'))

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                age = request.form.get('age')
                gender = request.form.get('gender')
                zip_code = request.form.get('zip')

                if not all([username, email, age, gender, zip_code]):
                    return "All fields are required. <a href='/register'>Go back</a>"

                assigned_id, error = self.AuthService.register_user(username, email, age, gender, zip_code)
                if error:
                    return f"{error} <a href='/register'>Try again</a>"

                flash(f'Registration successful! Your Unique ID is: {assigned_id}. Please log in.', 'success')
                return redirect(url_for('login'))

            return render_template('signup.html')

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                provided_id = request.form['password']
                user_or_admin, role = self.AuthService.login_user(username, provided_id)
                if role == 'user':
                    session['user'] = user_or_admin.username
                    session['role'] = user_or_admin.role
                    return redirect('/userdashboard')
                elif role == 'admin':
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

        @self.app.route('/logout')
        def logout():
            session.clear()
            resp = make_response(redirect('/login?logout=success'))
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return resp

        @self.app.route('/userdashboard')
        def userdashboard():
            if "user" not in session:
                return redirect('/login')
            return render_template('userdashboard.html')

        @self.app.route('/office1')
        def office1():
            if session.get("office") != "Barangay Officials":
                return redirect('/login')
            return render_template('admindashboard.html')

        @self.app.route('/office2')
        def office2():
            if session.get("office") != "City Mayor":
                return redirect('/login')
            return render_template('2admindashboard.html')

        @self.app.route('/office3')
        def office3():
            if session.get("office") != "Provincial Governor":
                return redirect('/login')
            return render_template('3admindashboard.html')

        @self.app.route('/reports')
        def reporting_dashboard():
            if "user" not in session:
                return redirect('/login')
            return render_template('DocumentReports.html')

        @self.app.route('/api/all_reports')
        def get_all_reports():
            if "user" not in session:
                return jsonify([])
            docs = self.Document.query.all()
            return jsonify([doc.to_dict() for doc in docs])

        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                return jsonify({"error": "No file part"})
            file = request.files['file']
            title = request.form.get('title')
            desc = request.form.get('desc')
            office = request.form.get('office')
            if session.get('role') == 'Resident':
                office = "Office 1"
            if file and self.DocumentService.allowed_file(file.filename):
                doc = self.DocumentService.save_upload(file, title, desc, office, session.get('user'))
                return jsonify(doc.to_dict())
            return jsonify({"error": "Invalid file type"})

        @self.app.route('/office1/documents')
        def office1_documents():
            if session.get("office") != "Barangay Officials":
                return jsonify([])
            docs = self.DocumentService.get_documents_by_office("Barangay Officials",
                                                                ["APPROVED BY BARANGAY", "DECLINED BY BARANGAY"])
            return jsonify([doc.to_dict() for doc in docs])

        @self.app.route('/office2/documents')
        def office2_documents():
            if session.get("office") != "City Mayor":
                return jsonify([])
            docs = self.DocumentService.get_documents_by_office("City Mayor",
                                                                ["APPROVED BY MAYOR", "DECLINED BY MAYOR"])
            return jsonify([doc.to_dict() for doc in docs])

        @self.app.route('/office3/documents')
        def office3_documents():
            if session.get("office") != "Provincial Governor":
                return jsonify([])
            docs = self.DocumentService.get_documents_by_office("Provincial Governor",
                                                                ["APPROVED BY GOVERNOR (FINAL)", "DECLINED BY GOVERNOR"])
            return jsonify([doc.to_dict() for doc in docs])

        def get_handler_for_office(office_name):
            if office_name == "Barangay Officials":
                return BarangayHandler()
            elif office_name == "City Mayor":
                return MayorHandler()
            elif office_name == "Provincial Governor":
                return GovernorHandler()
            return None

        @self.app.route('/approve/<filename>', methods=['POST'])
        def approve_brgy(filename):
            doc = self.Document.query.filter_by(filename=filename).first()
            if doc:
                handler = get_handler_for_office("Barangay Officials")
                handler.approve(doc)
                return jsonify({"success": True})
            return jsonify({"error": "Not found"})

        @self.app.route('/mayor/approve/<filename>', methods=['POST'])
        def approve_mayor(filename):
            doc = self.Document.query.filter_by(filename=filename).first()
            if doc:
                handler = get_handler_for_office("City Mayor")
                handler.approve(doc)
                return jsonify({"success": True})
            return jsonify({"error": "Not found"})

        @self.app.route('/governor/approve/<filename>', methods=['POST'])
        def approve_gov(filename):
            doc = self.Document.query.filter_by(filename=filename).first()
            if doc:
                handler = get_handler_for_office("Provincial Governor")
                handler.approve(doc)
                return jsonify({"success": True})
            return jsonify({"error": "Not found"})

        @self.app.route('/decline/<filename>', methods=['POST'])
        def decline_brgy(filename):
            reason = request.json.get('reason', 'No reason provided')
            doc = self.Document.query.filter_by(filename=filename).first()
            if doc:
                handler = get_handler_for_office("Barangay Officials")
                handler.decline(doc, reason)
                return jsonify({"success": True})
            return jsonify({"error": "Not found"})

        @self.app.route('/mayor/decline/<filename>', methods=['POST'])
        def decline_mayor(filename):
            reason = request.json.get('reason', 'No reason provided')
            doc = self.Document.query.filter_by(filename=filename).first()
            if doc:
                handler = get_handler_for_office("City Mayor")
                handler.decline(doc, reason)
                return jsonify({"success": True})
            return jsonify({"error": "Not found"})

        @self.app.route('/governor/decline/<filename>', methods=['POST'])
        def decline_gov(filename):
            reason = request.json.get('reason', 'No reason provided')
            doc = self.Document.query.filter_by(filename=filename).first()
            if doc:
                handler = get_handler_for_office("Provincial Governor")
                handler.decline(doc, reason)
                return jsonify({"success": True})
            return jsonify({"error": "Not found"})

        @self.app.route('/forward_to_mayor/<tracking_id>', methods=['POST'])
        def forward_to_mayor(tracking_id):
            success = self.DocumentService.forward_to_next_office(tracking_id, "APPROVED BY BARANGAY",
                                                                  "Office 2", "PENDING (MAYOR)")
            if success:
                return jsonify({"success": True})
            return jsonify({"error": "Not eligible for forwarding"})

        @self.app.route('/forward_to_governor/<tracking_id>', methods=['POST'])
        def forward_to_governor(tracking_id):
            success = self.DocumentService.forward_to_next_office(tracking_id, "APPROVED BY MAYOR",
                                                                  "Office 3", "PENDING (GOVERNOR)")
            if success:
                return jsonify({"success": True})
            return jsonify({"error": "Not eligible for forwarding"})

        @self.app.route('/uploads/<filename>')
        def uploaded_file(filename):
            return send_from_directory(self.app.config['UPLOAD_FOLDER'], filename)

        # map admin_dashboard for home redirection
        @self.app.route('/admin_dashboard')
        def admin_dashboard():
            return redirect('/office1')

    def run(self, debug=True):
        """Run the Flask application."""
        self.app.run(debug=debug)


# ------------------ MAIN ENTRY POINT (Object Creation) ------------------
if __name__ == '__main__':
    # Create an object of the DocumentTrackingSystem class
    system = DocumentTrackingSystem()
    # Run the application using the object
    system.run(debug=True)

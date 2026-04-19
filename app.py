import os
import random
from flask import Flask, render_template, redirect, request, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# ---------------- CONFIG ----------------
class Config:
    SECRET_KEY = "secret123"
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {'doc', 'docx', 'xls', 'xlsx'}

# ---------------- DOCUMENT MANAGER ----------------
class DocumentManager:
    def __init__(self):
        self.documents = []

    def add_document(self, title, desc, office, filename):
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
        self.documents.append(doc)
        return doc

    def get_all(self):
        return self.documents

    def filter_by_status(self, status):
        return [doc for doc in self.documents if doc.get("status") == status]

    def update_status(self, filename, status):
        for doc in self.documents:
            if doc["filename"] == filename:
                doc["status"] = status
                return True
        return False


# ---------------- USER MANAGER ----------------
class UserManager:
    def __init__(self):
        self.users = {
            'resident_user': ['UID-101-ZZ-9943', 'Resident']
        }
        self.available_ids = [
            "UID-992-XQ-2026", "UID-118-BT-7734", "UID-404-NM-8812",
            "UID-607-TR-1190", "UID-223-KL-5561"
        ]

    def register_user(self, username):
        if username in self.users:
            return None

        assigned_id = random.choice(self.available_ids)
        self.users[username] = [assigned_id, "Resident"]
        return assigned_id

    def validate_user(self, username, uid):
        return username in self.users and self.users[username][0] == uid


# ---------------- ADMIN MANAGER ----------------
class AdminManager:
    def __init__(self):
        self.admins = {
            "brgy_admin": {"unique_id": 'BGY-882-OFF-VAL', "office": "Barangay Officials"},
            "city_mayor": {"unique_id": 'MAYOR-441-CITY-SEC', "office": "City Mayor"},
            "provincial_gov": {"unique_id": 'GOV-110-PROV-AUTH', "office": "Provincial Governor"},
        }

    def validate_admin(self, username, uid):
        if username in self.admins and self.admins[username]["unique_id"] == uid:
            return self.admins[username]["office"]
        return None


# ---------------- APP FACTORY ----------------
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    doc_manager = DocumentManager()
    user_manager = UserManager()
    admin_manager = AdminManager()

    # ---------------- HELPERS ----------------
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    # ---------------- ROUTES ----------------
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')

            assigned_id = user_manager.register_user(username)
            if not assigned_id:
                return "Username already taken!"

            session['user'] = username
            session['role'] = "Resident"

            return f"Registered! ID: {assigned_id}"

        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            uid = request.form['password']

            if user_manager.validate_user(username, uid):
                session['user'] = username
                session['role'] = "Resident"
                return redirect('/userdashboard')

            office = admin_manager.validate_admin(username, uid)
            if office:
                session['user'] = username
                session['role'] = "office"
                session['office'] = office

                if office == "Barangay Officials":
                    return redirect('/office1')
                elif office == "City Mayor":
                    return redirect('/office2')
                elif office == "Provincial Governor":
                    return redirect('/office3')

            return "Invalid login"

        return render_template('login.html')

    # ---------------- FILE UPLOAD ----------------
    @app.route('/upload', methods=['POST'])
    def upload():
        file = request.files.get('file')
        title = request.form.get('title')
        desc = request.form.get('desc')
        office = request.form.get('office')

        if not file or file.filename == '':
            return jsonify({"error": "No file"})

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"})

        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

        counter = 1
        while os.path.exists(filepath):
            name, ext = filename.rsplit('.', 1)
            filename = f"{name}_{counter}.{ext}"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            counter += 1

        file.save(filepath)

        doc = doc_manager.add_document(title, desc, office, filename)
        return jsonify(doc)

    # ---------------- DOCUMENT ROUTES ----------------
    @app.route('/documents')
    def documents():
        return jsonify(doc_manager.get_all())

    @app.route('/approve/<filename>', methods=['POST'])
    def approve(filename):
        if doc_manager.update_status(filename, "APPROVED BY BARANGAY"):
            return jsonify({"success": True})
        return jsonify({"error": "Not found"})

    @app.route('/mayor/documents')
    def mayor_docs():
        return jsonify(doc_manager.filter_by_status("APPROVED BY BARANGAY"))

    @app.route('/governor/documents')
    def governor_docs():
        return jsonify(doc_manager.filter_by_status("APPROVED BY MAYOR"))

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    return app


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
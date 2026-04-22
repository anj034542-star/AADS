# 📂 AADS: Automated Approval & Document System
**"Streamlining Governance through Digital Transparency"**

AADS is a centralized web-based platform designed to automate the manual paperwork trail within local government units. By digitizing the document lifecycle—from resident submission to provincial approval—AADS eliminates bottlenecks, ensures accountability, and provides real-time tracking for every stakeholder.

---

### 👨‍💻 **Development Team (BSCS-1B)**
| Name | Role |
| :--- | :--- |
| **Alcoy, Mirht Ruther N.** | Lead Developer / Backend Logic |
| **Anam-anam, John Rhey M.** | UI/UX Designer / Documentation |
| **Decosto, Heroditus** | System Analyst / Quality Assurance |
| **Sarigumba, Prince Stephen** | Database Management / Integration |

---

### 🚀 **Core System Features**

* **Tiered Approval Pipeline:** A sequential workflow requiring verification from **Barangay**, **City**, and **Provincial** levels.
* **UID Authentication:** Replaces vulnerable passwords with a **Unique Professional ID** system for both residents and officials.
* **Multi-Role Dashboards:** Custom interfaces tailored specifically to the needs of Residents and Office Administrators.
* **File Integrity:** Strict enforcement of allowed file types (`.doc`, `.docx`, `.excel`, `.xlsx`) to prevent system vulnerabilities.
* **Transparent Feedback Loop:** If a document is denied, the system captures and displays the specific "Reason for Rejection," allowing for efficient revisions.

---

## Prerequisites

List of tools or software needed before installation.

- **Python 3.8+**  
- **pip** (Python package installer)  
- **SQLite** (built-in, no extra install) – the app uses `/tmp/app.db` by default  
- **Git** (optional, for cloning)  

Required Python packages (install via `pip`):

```bash
Flask
Flask-SQLAlchemy
Werkzeug
```

> The code uses only `flask`, `flask_sqlalchemy`, `werkzeug`, plus Python standard libraries (`os`, `random`, `datetime`).

---

## Installation

Specific commands to get the project running.

1. **Clone or create the project folder**  
   ```bash
   mkdir document_tracker && cd document_tracker
   ```

2. **Save the provided code as `app.py`**  
   (Copy the entire code into a file named `app.py`)

3. **Create a `templates/` folder** with the required HTML files:  
   - `signup.html`  
   - `login.html`  
   - `userdashboard.html`  
   - `admindashboard.html`  
   - `2admindashboard.html`  
   - `3admindashboard.html`  
   - `DocumentReports.html`  

   *(Minimal examples are not shown here – you can create simple placeholders.)*

4. **Install dependencies**  
   ```bash
   pip install flask flask-sqlalchemy
   ```

5. **Set environment variables (optional)**  
   ```bash
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="sqlite:////tmp/app.db"   # or any path
   export UPLOAD_FOLDER="/tmp/uploads"
   ```

6. **Run the application**  
   ```bash
   flask run
   # or
   python app.py
   ```

   The app will start at `http://127.0.0.1:5000`.

> **Note for Vercel deployment**: The code already uses `/tmp` for database and uploads, and the `app` object is exposed for serverless environments.

---

## Usage

Examples of how to use the software, often with code blocks.

### 1. User Registration
**Endpoint:** `POST /register`  
**Form data:** `username`  
**Response:** Assigns a random unique ID and logs the user in.

```bash
curl -X POST http://localhost:5000/register -d "username=juan"
```

### 2. User Login
**Endpoint:** `POST /login`  
**Form data:** `username`, `password` (the unique ID)  
**Redirects** to `/userdashboard` on success.

```bash
curl -X POST http://localhost:5000/login -d "username=juan&password=UID-992-XQ-2026"
```

### 3. Upload a Document (Resident or Admin)
**Endpoint:** `POST /upload`  
**Form data (multipart):**  
- `file` (allowed: .doc, .docx, .excel, .xlsx)  
- `title`  
- `desc` (description)  
- `office` (ignored for Residents – forced to "Office 1")

```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@report.docx" \
  -F "title=Annual Report" \
  -F "desc=Q1 financials" \
  -F "office=Office 1" \
  -b "session_cookie"
```

**Response (JSON):**
```json
{
  "tracking_id": "TRK-12345",
  "title": "Annual Report",
  "status": "PENDING",
  "filename": "report.docx"
}
```

### 4. Barangay Officials – View Pending Documents
**Endpoint:** `GET /office1/documents`  
**Requires** session with `office="Barangay Officials"`.

```bash
curl http://localhost:5000/office1/documents -b "session_cookie"
```

### 5. Approve a Document (Barangay)
**Endpoint:** `POST /approve/<filename>`  

```bash
curl -X POST http://localhost:5000/approve/report.docx -b "session_cookie"
```

### 6. Decline a Document (with reason)
**Endpoint:** `POST /decline/<filename>`  
**JSON body:** `{"reason": "Missing signature"}`

```bash
curl -X POST http://localhost:5000/decline/report.docx \
  -H "Content-Type: application/json" \
  -d '{"reason": "Missing signature"}' \
  -b "session_cookie"
```

### 7. Forward Approved Document to Mayor
**Endpoint:** `POST /forward_to_mayor/<tracking_id>`  
**Condition:** document status must be `APPROVED BY BARANGAY`.

```bash
curl -X POST http://localhost:5000/forward_to_mayor/TRK-12345 -b "session_cookie"
```

### 8. Final Approval by Governor
**Endpoint:** `POST /governor/approve/<filename>`

```bash
curl -X POST http://localhost:5000/governor/approve/report.docx -b "session_cookie"
```

### 9. Download Uploaded File
**Endpoint:** `GET /uploads/<filename>`  

```bash
curl http://localhost:5000/uploads/report.docx -O
```

### 10. View All Reports (JSON)
**Endpoint:** `GET /api/all_reports`  

```bash
curl http://localhost:5000/api/all_reports -b "session_cookie"
```

### 11. Logout
**Endpoint:** `GET /logout`  
Clears session and redirects to `/login`.

```bash
curl http://localhost:5000/logout -b "session_cookie"
```

---

## Additional Notes from the Code

- **Default admin accounts** are seeded automatically:
  - `brgy_admin` / `BGY-882-OFF-VAL` → Barangay Officials  
  - `city_mayor` / `MAYOR-441-CITY-SEC` → City Mayor  
  - `provincial_gov` / `GOV-110-PROV-AUTH` → Provincial Governor  

- **Document workflow**  
  Resident upload → Barangay (Office 1) approve/decline → forward to Mayor (Office 2) → approve/decline → forward to Governor (Office 3) → final approve/decline.

- **Tracking ID format:** `TRK-` + 5 random digits.

- **Allowed file extensions:** `.doc`, `.docx`, `.excel`, `.xlsx` (max 16 MB).

### **Modules**

Module 1:We have finished creating the user dashboard. When a user clicks 'Upload Document,' a form will appear. First, the user must enter a title and a description. Next, they select 'Select Office' and choose 'Office 1' to initiate the routing process through the three office options. The user can then select a file; we currently support Word, Excel, and DOC formats. Once the file is uploaded, a 'Pending' status will display, and the document will automatically appear on the Office 1 dashboard.

Module 2:We are creating a dashboard for Office 1, Office 2, and Office 3. Each dashboard will feature options to Download Document, Approve, and Decline. If a user at any office selects 'Decline,' they must provide a reason. While Offices 1 and 2 share the same functionality, Office 3 acts as the final approval stage. The process begins when a user uploads a document; only then will the download and approval options become visible on the office dashboards."

Module 3:We have finished creating the module 3. while the offices making there feedback, user can track the document progres, user can see the current approval stage, where if it's approve or denied at the offices or in other wise its pending. the status updates after every action. if the office have the make the feed back it will display the last apdate, date, time, and the reason, the history connot be edited, if what the office feedback it will be record to the history of the file. also can view the approval history. 

Module 4:We added a tracking ID to the user dashboard to help users quickly find their documents. By using the tracking ID provided by the system, users can easily search for their files. However, if the user enters an incorrect tracking ID—even with just one wrong letter or number—the system will display a message indicating that no tracking ID was found.

Module 5:In this module, we created a new admin dashboard. Unlike the office dashboards, this does not include approval or decline functionality. Instead, it provides filtering options such as Date, Status, and User. It also can generate reports and export them in PDF or Excel format, this can also act as a inventory since it can see all the document that the users upload to the offices.

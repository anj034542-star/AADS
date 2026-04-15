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
* **File Integrity:** Strict enforcement of allowed file types (`.doc`, `.docx`, `.xls`, `.xlsx`) to prevent system vulnerabilities.
* **Transparent Feedback Loop:** If a document is denied, the system captures and displays the specific "Reason for Rejection," allowing for efficient revisions.

---

### 🛠️ **Prerequisites & Technical Stack**

* **Framework:** Flask (Python-based Web Framework)
* **Language:** Python 3.8+
* **Storage:** Localized File System (Uploads folder)
* **Security:** Session-based Authentication & UID Mapping

---

### 📥 **Installation & Deployment**

1.  **Environment Setup:**
    Ensure Python is installed, then install the Flask dependency:
    ```bash
    pip install flask
    ```
2.  **File Configuration:**
    Ensure your directory structure looks like this:
    ```text
    /AADS_Project
    ├── app.py
    ├── uploads/
    └── templates/
        ├── signup.html
        ├── login.html
        └── [dashboards].html
    ```
3.  **Initialization:**
    Run the server via terminal:
    ```bash
    python app.py
    ```
4.  **Network Access:**
    Open your browser and navigate to: `http://127.0.0.1:5000`

---

### 🔄 **The AADS Workflow (User Journey)**

#### **Step 1: Registration & ID Allocation**
Residents register through the portal. The system dynamically assigns a **Unique Professional ID** (e.g., `UID-992-XQ-2026`). **Note:** This ID is required for all future logins.

#### **Step 2: Document Submission**
The resident uploads a document via their dashboard. The file is stored securely in the server's `uploads/` directory and enters the "Pending" queue for the first office.

#### **Step 3: Sequential Review**
The document moves through the **Government Hierarchy**:
1.  **Barangay Officials:** Verify local residency and basic requirements.
2.  **City Mayor:** Conducts executive review and alignment.
3.  **Provincial Governor:** Provides the final statutory approval.

#### **Step 4: Tracking & Finalization**
At any stage, the resident can view the **Live Status Monitor**. Once the Provincial Governor approves, the document is marked as "Fully Processed" and ready for official use.

---

### 📊 **Admin Monitoring & Oversight**
Administrators have elevated privileges to:
* **Audit** all incoming documents within their specific jurisdiction.
* **Execute Decisions:** Approve or Reject with mandatory feedback.
* **System Logs:** Track which office handled which document and at what time.

---

### **Modules**

Module 1: We have finished creating the user dashboard. When a user clicks 'Upload Document,a form will appear. First, the user must enter a Title and a Description. Next, they should click 'Select Office' and choose Office 1 as a starting of passing your document on those 3 offices options. Then a user can select a file; we currently support Word, Excel, and DOC formats. Once uploaded, the file will automatically appear on the Office 1 dashboard.

Module 2:"We are creating a dashboard for Office 1, Office 2, and Office 3. Each dashboard will feature options to Download Document, Approve, and Decline. If a user at any office selects 'Decline,' they must provide a reason. While Offices 1 and 2 share the same functionality, Office 3 acts as the final approval stage. The process begins when a user uploads a document; only then will the download and approval options become visible on the office dashboards."

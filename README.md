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

> **Security Warning:** The `app.secret_key` and **Admin UIDs** should be changed before deploying the system to a production environment to ensure maximum data protection.

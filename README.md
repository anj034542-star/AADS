#  AADS - DOCUMENT TRACKING AND APPROVAL SYSTEM

**AADS**- This is a system for approving documents through three responders. Each responder must approve the document before it can be sent to the specific receiver online.
While waiting for approval, you can check the status to see if it was approved or denied by a responder, and also see the reason if it was denied.


**AADS** (Automated Approval and Document System) is a modern solution designed to streamline document tracking and approval processes within organizations. In today’s fast-paced digital environment, managing documents efficiently is essential to ensure accuracy, accountability, and timely decision-making.

___________________________________________________________

# **Developer (BSCS-1B)**

Alcoy, Mirht Ruther N.

Anam-anam, John Rhey M.

Decosto, Heroditus

Sarigumba, Prince Stephen
____________________________________________________________

# **Project Discription**

**Document Submission:** Easily upload and manage documents.

**Tracking System:** Monitor document status in real-time (pending, approved, rejected).

**Approval Workflow:** Route documents to the appropriate personnel for review.

**Notifications:** Get updates on document progress and decisions.

**Data Management:** Securely store and organize all documents in one place.

______________________________________________________________


# **Prerequisites**

Befor running the project, ensure you have the following installed.

**Python 3.8+** (python --version)

**Pip** (Python package manager)

**Code Editor** (VS Code recommended)

**Modern Web Browser** (Chrome, Edge, or Firefox)

________________________________________________________________
# **Installation & Setup**

1. Clone or Create the Project Folder Place the billing system folder in your desired directory.

2. Install Flask Open your terminal and run

       pip install flask

3. Save the code: Save the Python code as app.py in your folder.

4. Run the Application: python app.py The system will be live at http://127.0.0.1:5000

_________________________________________________________________


# **Usage Guide**

The Document Tracking and Approval System is used to manage, monitor, and process documents across different offices or departments.It ensures that documents are properly tracked, reviewed, approved, and stored in an organized and efficient way.



👤 **1. User Login**

The system begins when the authorized user 

(Admin or Staff) logs in.
Only registered users can access the system.

Each user has specific roles (e.g., Admin, Office Staff).




📤**2. Document Submission**

The user uploads or creates a document in the 
system.

Required details are entered, such as:

Document Title

Description

Date Submitted

Destination Office




🔍 **3. Document Tracking**

Each document is assigned a tracking number.

Users can monitor the document status in real-

time:

Pending

Under Review

Approved

Rejected





🏢 **4. Routing to Offices**

The document is automatically forwarded to the 
assigned office.

Example flow:

Office 1 → Office 2 → Office 3

Each office reviews the document before passing it to the next.





✅ **5. Approval Process**

Each office can:

Approve the document

Reject the document

Request revisions

If approved, the document moves to the next 

office automatically.





**6. Notifications**

The system notifies users about updates:

Approval status

Rejection messages

Pending actions





📁 **7. Document Storage**

Approved documents are stored in the system database.

Users can retrieve past documents anytime.





📊**8. Admin Monitoring**

The Admin can:

Track all documents

View system logs

Manage users

Generate reports



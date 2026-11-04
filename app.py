import os
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-development-secret")

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "sachin@2005"),
    "database": os.getenv("MYSQL_DATABASE", "citizen_registration_db"),
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def query_all(sql, params=()):
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def execute(sql, params=()):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid, cur.rowcount
    finally:
        cur.close()
        conn.close()

@app.template_filter("date_display")
def date_display(value):
    return value.strftime("%d-%m-%Y") if hasattr(value, "strftime") and value else (value or "")

@app.route("/")
def dashboard():
    try:
        stats = {
            "citizens": query_all("SELECT COUNT(*) AS n FROM CITIZEN")[0]["n"],
            "departments": query_all("SELECT COUNT(*) AS n FROM DEPARTMENT")[0]["n"],
            "officers": query_all("SELECT COUNT(*) AS n FROM OFFICER")[0]["n"],
            "applications": query_all("SELECT COUNT(*) AS n FROM REGISTRATION_APPLICATION")[0]["n"],
            "verifications": query_all("SELECT COUNT(*) AS n FROM VERIFICATION")[0]["n"],
            "documents": query_all("SELECT COUNT(*) AS n FROM IDENTITY_DOCUMENT")[0]["n"],
        }
        recent = query_all("""SELECT Citizen_ID, Full_Name, Mobile_Number, Email
                              FROM CITIZEN ORDER BY Citizen_ID DESC LIMIT 8""")
        db_error = None
    except Error as e:
        stats, recent, db_error = {}, [], str(e)
    return render_template("dashboard.html", stats=stats, recent=recent, db_error=db_error)

# Generic list/create/edit/delete pages. All table names and columns are fixed here;
# user-provided values are always passed as SQL parameters.
TABLES = {
    "citizens": {
        "title": "Citizens", "table": "CITIZEN", "pk": "Citizen_ID",
        "columns": ["Citizen_ID", "Full_Name", "Date_of_Birth", "Gender", "Mobile_Number", "Email",],
        "fields": [
            ("Full_Name", "Full name", "text", True),
            ("Date_of_Birth", "Date of birth", "date", False),
            ("Gender", "Gender", "select", False, ["Male", "Female", "Other"]),
            ("Mobile_Number", "Mobile number", "text", False),
            ("Email", "Email", "email", False),
        ],
    },
    "addresses": {
        "title": "Addresses", "table": "ADDRESS", "pk": "Address_ID",
        "columns": ["Address_ID", "Citizen_ID", "House_Number", "Street", "Village_or_City", "District", "State", "PIN_Code"],
        "fields": [
            ("Citizen_ID", "Citizen", "fk_citizen", True),
            ("House_Number", "House number", "text", False), ("Street", "Street", "text", False),
            ("Village_or_City", "Village / City", "text", True), ("District", "District", "text", True),
            ("State", "State", "text", False), ("PIN_Code", "PIN code", "text", False),
        ],
    },
    "departments": {
        "title": "Departments", "table": "DEPARTMENT", "pk": "Department_ID",
        "columns": ["Department_ID", "Department_Name", "Office_Address", "Contact_Number"],
        "fields": [("Department_Name", "Department name", "text", True),
                   ("Office_Address", "Office address", "text", False),
                   ("Contact_Number", "Contact number", "text", False)],
    },
    "officers": {
        "title": "Officers", "table": "OFFICER", "pk": "Officer_ID",
        "columns": ["Officer_ID", "Department_ID", "Officer_Name", "Designation", "Extension", "Status", "Joining_Date", "Email"],
        "fields": [("Department_ID", "Department", "fk_department", False),
                   ("Officer_Name", "Officer name", "text", True), ("Designation", "Designation", "text", False),
                   ("Extension", "Extension", "text", False), ("Status", "Status", "text", False),
                   ("Joining_Date", "Joining date", "date", False), ("Email", "Email", "email", False)],
    },
    "applications": {
        "title": "Registration applications", "table": "REGISTRATION_APPLICATION", "pk": "Application_ID",
        "columns": ["Application_ID", "Citizen_ID", "Application_Date", "Application_Type", "Application_Status", "Remarks"],
        "fields": [("Citizen_ID", "Citizen", "fk_citizen", True), ("Application_Date", "Application date", "date", False),
                   ("Application_Type", "Application type", "text", True),
                   ("Application_Status", "Application status", "select", True, ["Pending", "Under Review", "Approved", "Rejected"]),
                   ("Remarks", "Remarks", "textarea", False)],
    },
    "verifications": {
        "title": "Verifications", "table": "VERIFICATION", "pk": "Verification_ID",
        "columns": ["Verification_ID", "Application_ID", "Verification_Date", "Verification_Result", "Verification_Stage", "Action_Required", "Comments", "Officer_ID"],
        "fields": [("Application_ID", "Application", "fk_application", True), ("Verification_Date", "Verification date", "date", False),
                   ("Verification_Result", "Verification result", "text", False), ("Verification_Stage", "Verification stage", "text", False),
                   ("Action_Required", "Action required", "textarea", False), ("Comments", "Comments", "textarea", False),
                   ("Officer_ID", "Officer", "fk_officer", False)],
    },
    "documents": {
        "title": "Identity documents", "table": "IDENTITY_DOCUMENT", "pk": "Document_ID",
        "columns": ["Document_ID", "Citizen_ID", "Document_Type", "Document_Number"],
        "fields": [("Citizen_ID", "Citizen", "fk_citizen", True), ("Document_Type", "Document type", "text", True),
                   ("Document_Number", "Document number", "text", True)],
    },
}

FK_OPTIONS = {
    "fk_citizen": ("SELECT Citizen_ID AS id, Full_Name AS label FROM CITIZEN ORDER BY Full_Name",),
    "fk_department": ("SELECT Department_ID AS id, Department_Name AS label FROM DEPARTMENT ORDER BY Department_Name",),
    "fk_application": ("SELECT Application_ID AS id, CONCAT('Application #', Application_ID) AS label FROM REGISTRATION_APPLICATION ORDER BY Application_ID DESC",),
    "fk_officer": ("SELECT Officer_ID AS id, Officer_Name AS label FROM OFFICER ORDER BY Officer_Name",),
}

def form_options(config):
    options = {}
    for field in config["fields"]:
        if field[2] in FK_OPTIONS:
            options[field[0]] = query_all(FK_OPTIONS[field[2]][0])
    return options

@app.route("/<resource>")
def list_records(resource):
    config = TABLES.get(resource)
    if not config:
        return "Not found", 404
    try:
        rows = query_all(f"SELECT {', '.join(config['columns'])} FROM {config['table']} ORDER BY {config['pk']} DESC")
        return render_template("records.html", resource=resource, config=config, rows=rows)
    except Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("dashboard"))

@app.route("/<resource>/new", methods=["GET", "POST"])
def create_record(resource):
    config = TABLES.get(resource)
    if not config:
        return "Not found", 404
    if request.method == "POST":
        fields = [f[0] for f in config["fields"]]
        values = [request.form.get(name) or None for name in fields]
        placeholders = ", ".join(["%s"] * len(fields))
        try:
            execute(f"INSERT INTO {config['table']} ({', '.join(fields)}) VALUES ({placeholders})", values)
            flash(f"{config['title']} record saved successfully.", "success")
            return redirect(url_for("list_records", resource=resource))
        except Error as e:
            flash(f"Could not save record: {e}", "error")
    try:
        options = form_options(config)
    except Error as e:
        options = {}
        flash(f"Could not load dropdown options: {e}", "error")
    return render_template("form.html", resource=resource, config=config, record={}, options=options, mode="Add")

@app.route("/<resource>/<int:record_id>/edit", methods=["GET", "POST"])
def edit_record(resource, record_id):
    config = TABLES.get(resource)
    if not config:
        return "Not found", 404
    if request.method == "POST":
        fields = [f[0] for f in config["fields"]]
        values = [request.form.get(name) or None for name in fields]
        assignments = ", ".join(f"{name}=%s" for name in fields)
        try:
            execute(f"UPDATE {config['table']} SET {assignments} WHERE {config['pk']}=%s", values + [record_id])
            flash(f"{config['title']} record updated.", "success")
            return redirect(url_for("list_records", resource=resource))
        except Error as e:
            flash(f"Could not update record: {e}", "error")
    rows = query_all(f"SELECT * FROM {config['table']} WHERE {config['pk']}=%s", (record_id,))
    if not rows:
        return "Record not found", 404
    options = form_options(config)
    return render_template("form.html", resource=resource, config=config, record=rows[0], options=options, mode="Edit")

@app.route("/<resource>/<int:record_id>/delete", methods=["POST"])
def delete_record(resource, record_id):
    config = TABLES.get(resource)
    if not config:
        return "Not found", 404
    try:
        execute(f"DELETE FROM {config['table']} WHERE {config['pk']}=%s", (record_id,))
        flash("Record deleted (subject to the table's foreign-key rules).", "success")
    except Error as e:
        flash(f"Could not delete record: {e}", "error")
    return redirect(url_for("list_records", resource=resource))

@app.route("/health")
def health():
    try:
        query_all("SELECT 1")
        return {"status": "ok", "database": DB_CONFIG["database"]}
    except Error as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    print("Citizen Registration System: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

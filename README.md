# Citizen Registration System — Flask + MySQL

This VS Code project connects a browser-based frontend to your existing MySQL database through Flask. It manages the seven tables:
`CITIZEN`, `ADDRESS`, `DEPARTMENT`, `OFFICER`, `REGISTRATION_APPLICATION`, `VERIFICATION`, and `IDENTITY_DOCUMENT`.
There is no Complaints entity.

## 1. Requirements
- Python 3.10 or newer
- MySQL Server 8.x running
- VS Code (recommended)

## 2. Check your database
You said you have already created `citizen_registration_db` and its seven tables. In MySQL Workbench run:
```sql
USE citizen_registration_db;
SHOW TABLES;
DESCRIBE CITIZEN;
```
The application expects the exact table and column names in `database.sql`. In particular it expects  in `CITIZEN`, matching the earlier schema script. If your actual column has a different spelling, adjust the `CITIZEN` table or the corresponding field in `app.py` to match it.

## 3. Open in VS Code
Extract this ZIP. In VS Code choose **File → Open Folder** and select `Citizen_Registration_System`.

Open Terminal → New Terminal and run:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## 4. Set your MySQL connection
In the same PowerShell terminal, set your actual MySQL credentials:
```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="YOUR_ACTUAL_MYSQL_PASSWORD"
$env:MYSQL_DATABASE="citizen_registration_db"
$env:FLASK_SECRET_KEY="change-this-to-a-long-random-value"
```
Do not type the password into public code or upload it to GitHub. If your MySQL root account has no password, use `$env:MYSQL_PASSWORD=""`.

## 5. Run
```powershell
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## 6. Use the website
Use the left menu to add, view, edit, and delete records in each of the seven tables.
For child records, create the parent first:
1. Create a Citizen before adding their Address, Application, or Identity Document.
2. Create a Department before assigning an Officer to it.
3. Create an Application and an Officer before adding a Verification.

## 7. Verify records in MySQL Workbench
For example:
```sql
USE citizen_registration_db;
SELECT * FROM CITIZEN;
SELECT * FROM ADDRESS;
SELECT * FROM DEPARTMENT;
SELECT * FROM OFFICER;
SELECT * FROM REGISTRATION_APPLICATION;
SELECT * FROM VERIFICATION;
SELECT * FROM IDENTITY_DOCUMENT;
```

## Notes
- Browser forms submit to Flask; Flask connects to MySQL. Never put MySQL credentials in HTML or JavaScript.
- The app uses parameterized SQL for entered values.
- Deleting a citizen/application may cascade to dependent records according to the foreign-key rules you created.
- If you see `Unknown column` or `Table doesn't exist`, compare your actual MySQL schema with `database.sql`; do not blindly drop or recreate your existing database.

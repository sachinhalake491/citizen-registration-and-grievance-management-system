-- Run this ONLY if you have not already created the seven tables.
-- If your database already exists, compare its columns with this schema first.
CREATE DATABASE IF NOT EXISTS citizen_registration_db;
USE citizen_registration_db;

CREATE TABLE IF NOT EXISTS CITIZEN (
    Citizen_ID INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name VARCHAR(100) NOT NULL,
    Date_of_Birth DATE,
    Gender VARCHAR(20),
    Mobile_Number VARCHAR(15),
    Email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS ADDRESS (
    Address_ID INT AUTO_INCREMENT PRIMARY KEY,
    Citizen_ID INT,
    House_Number VARCHAR(30),
    Street VARCHAR(100),
    Village_or_City VARCHAR(100),
    District VARCHAR(100),
    State VARCHAR(100),
    PIN_Code VARCHAR(10),
    FOREIGN KEY (Citizen_ID) REFERENCES CITIZEN(Citizen_ID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS DEPARTMENT (
    Department_ID INT AUTO_INCREMENT PRIMARY KEY,
    Department_Name VARCHAR(100) NOT NULL,
    Office_Address VARCHAR(255),
    Contact_Number VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS OFFICER (
    Officer_ID INT AUTO_INCREMENT PRIMARY KEY,
    Department_ID INT,
    Officer_Name VARCHAR(100) NOT NULL,
    Designation VARCHAR(100),
    Extension VARCHAR(20),
    Status VARCHAR(30),
    Joining_Date DATE,
    Email VARCHAR(100),
    FOREIGN KEY (Department_ID) REFERENCES DEPARTMENT(Department_ID)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS REGISTRATION_APPLICATION (
    Application_ID INT AUTO_INCREMENT PRIMARY KEY,
    Citizen_ID INT,
    Application_Date DATE,
    Application_Type VARCHAR(100),
    Application_Status VARCHAR(50),
    Remarks TEXT,
    FOREIGN KEY (Citizen_ID) REFERENCES CITIZEN(Citizen_ID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS VERIFICATION (
    Verification_ID INT AUTO_INCREMENT PRIMARY KEY,
    Application_ID INT,
    Verification_Date DATE,
    Verification_Result VARCHAR(100),
    Verification_Stage VARCHAR(100),
    Action_Required TEXT,
    Comments TEXT,
    Officer_ID INT,
    FOREIGN KEY (Application_ID) REFERENCES REGISTRATION_APPLICATION(Application_ID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (Officer_ID) REFERENCES OFFICER(Officer_ID)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS IDENTITY_DOCUMENT (
    Document_ID INT AUTO_INCREMENT PRIMARY KEY,
    Citizen_ID INT,
    Document_Type VARCHAR(100),
    Document_Number VARCHAR(100),
    FOREIGN KEY (Citizen_ID) REFERENCES CITIZEN(Citizen_ID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

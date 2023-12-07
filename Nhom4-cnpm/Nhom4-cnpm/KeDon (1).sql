CREATE DATABASE KeDon
use KeDon

CREATE TABLE Patient (
    patient_id int PRIMARY KEY,
    Patient_name VARCHAR(50),
);
CREATE TABLE Doctor (
    doctor_id int PRIMARY KEY,
    Doctor_name VARCHAR(50),
);
CREATE TABLE Prescription (
    prescription_id int PRIMARY KEY,
    patient_id int,
    doctor_id int,
    date_prescribed DATE,
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);
CREATE TABLE Medication (
    medication_id int PRIMARY KEY, 
    medication_name VARCHAR(100),
    dosageMin INT,
	dosageMax INT,
	singleDoseMin INT,
	singleDoseMax INT,
	frequency INT
);
CREATE TABLE Prescription_Detail (
    prescription_detail_id int PRIMARY KEY,
    prescription_id int,
    medication_id int,
    Dose int,
	frequency int,
	singleDose int
    FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id),
    FOREIGN KEY (medication_id) REFERENCES Medication(medication_id)
);

insert into Doctor values ('001','Tuan Hai')
insert into Doctor values ('002','Anh Hao')

insert into Patient values ('001','Trung Hieu')
insert into Patient values ('002','Phan Cuong')
insert into Patient values ('003','Phuc Thinh')

insert into Medication values ('001','Paracetamol',1300,2600, 325,625,4)
insert into Medication values ('002','Aspirin',300,4000,300,900,4)




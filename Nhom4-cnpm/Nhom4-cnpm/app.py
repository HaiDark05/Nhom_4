from flask import Flask, render_template, redirect, url_for, request,flash
import pymssql
app = Flask(__name__)
app.secret_key = 'aaa'
app.config['SQL_SERVER'] = 'localhost:1433'
app.config['SQL_DATABASE'] = 'KeDon'
app.config['SQL_USERNAME'] = 'sa'
app.config['SQL_PASSWORD'] = '123456'

def kiem_tra_id_ct_unique(ds_prescriptions, new_id):
    for prescription_detail_id in ds_prescriptions:
        if prescription_detail_id == new_id:
            return False
    return True

def kiem_tra_id_unique(ds_prescriptions, new_id):
    for prescription_id in ds_prescriptions:
        if prescription_id == new_id:
            return False
    return True

def query_database(query, params=None):
    result = []
    with pymssql.connect(server=app.config['SQL_SERVER'],
                        user=app.config['SQL_USERNAME'],
                        password=app.config['SQL_PASSWORD'],
                        database=app.config['SQL_DATABASE']) as conn:
        with conn.cursor(as_dict=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Ke_don.html', methods=['GET', 'POST'])
def create_prescription():
    if request.method == 'POST':
        prescription_id = request.form.get('prescription_id')
        patient_id = request.form.get('patient_id')
        doctor_id = request.form.get('doctor_id')
        prescription_detail_id = request.form.get('prescription_id')
        medication_id = request.form.get('medication_id')
        dose = int(request.form.get('dose'))
        frequency = int(request.form.get('frequency'))
        single_dose = int(request.form.get('single_dose'))
        date_prescribed = request.form.get('date_prescribed')

        if not kiem_tra_lieu_luong_thuoc(medication_id, dose, single_dose,frequency):
            flash(f"Liều lượng thuốc vượt quá giới hạn cho loại thuốc này. Vui lòng kiểm tra lại.", 'error')
            return redirect(url_for('create_prescription'))

        if kiem_tra_id_unique(get_prescription(), prescription_id):
            add_prescription(prescription_id, patient_id, doctor_id, date_prescribed)
            add_prescription_detail(prescription_detail_id,prescription_id, medication_id, dose, frequency, single_dose)
        else:
            add_prescription_detail(prescription_detail_id,prescription_id, medication_id, dose, frequency, single_dose)

        if not kiem_tra_id_ct_unique(get_prescription_detail(), prescription_detail_id):
            flash(f"Prescription Detail ID {prescription_detail_id} đã tồn tại. Vui lòng nhập lại.", 'error')
            return redirect(url_for('create_prescription'))
        # Tiếp tục tạo đơn thuốc
        flash("Đã tạo đơn thuốc thành công.", 'success')
        return redirect(url_for('index'))
        # ...

    patients = get_patients()
    doctors = get_doctors()
    medications = get_medications()

    return render_template('Ke_don.html', patients=patients, doctors=doctors, medications=medications)

@app.route('/xem.html')
def view_prescription():
    prescription_id = request.args.get('prescription_id', type=int)
    prescription_info = get_prescription_info(prescription_id)
    return render_template('xem.html', prescription_info=prescription_info)

def get_prescription_info(prescription_id):
    if not prescription_id:
        return None

    prescription_query = "SELECT * FROM Prescription WHERE prescription_id = %s;"
    prescription_result = query_database(prescription_query, (prescription_id,))
    prescription_info = prescription_result[0] if prescription_result else None

    if prescription_info:
        detail_query = "SELECT * FROM Prescription_Detail WHERE prescription_id = %s;"
        detail_result = query_database(detail_query, (prescription_id,))
        prescription_info['details'] = detail_result if detail_result else []

    return prescription_info

def add_prescription(prescription_id, patient_id, doctor_id, date_prescribed):
    query = "INSERT INTO Prescription (prescription_id, patient_id, doctor_id, date_prescribed) VALUES (%s, %s, %s, %s);"
    with pymssql.connect(server=app.config['SQL_SERVER'],
                        user=app.config['SQL_USERNAME'],
                        password=app.config['SQL_PASSWORD'],
                        database=app.config['SQL_DATABASE']) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (prescription_id, patient_id, doctor_id, date_prescribed))
            conn.commit()
    return

def add_prescription_detail(prescription_detail_id,prescription_id, medication_id, dose, frequency, single_dose):
    query = "INSERT INTO Prescription_Detail (prescription_detail_id, prescription_id, medication_id, Dose, frequency, singleDose) VALUES (%s, %s, %s, %s, %s, %s)"
    with pymssql.connect(server=app.config['SQL_SERVER'],
                        user=app.config['SQL_USERNAME'],
                        password=app.config['SQL_PASSWORD'],
                        database=app.config['SQL_DATABASE']) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (prescription_detail_id,prescription_id, medication_id, dose, frequency, single_dose))
            conn.commit()
    return

def kiem_tra_lieu_luong_thuoc(medication_id, dose, single_dose,frequency):
    medication_info = get_medication_info(medication_id)

    if not medication_info:
        flash(f"Không tìm thấy thông tin về thuốc có ID {medication_id}. Vui lòng kiểm tra lại.", 'error')
        return False

    if 'dosageMax' in medication_info and 'singleDoseMax' in medication_info:
        max_dosage = medication_info['dosageMax']
        max_single_dose = medication_info['singleDoseMax']
        frequencyM = medication_info['frequency']

        if dose > max_dosage or single_dose > max_single_dose or frequency > frequencyM:
            return False

    return True

def get_medication_info(medication_id):
    query = "SELECT * FROM Medication WHERE medication_id = %s;"
    with pymssql.connect(server=app.config['SQL_SERVER'],
                        user=app.config['SQL_USERNAME'],
                        password=app.config['SQL_PASSWORD'],
                        database=app.config['SQL_DATABASE']) as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute(query, (medication_id,))
            result = cursor.fetchone()

    return result

def get_prescription():
    query = "SELECT prescription_id FROM Prescription;"
    return [result['prescription_id'] for result in query_database(query)]

def get_prescription_detail():
    query = "SELECT prescription_detail_id FROM Prescription_Detail;"
    return [result['prescription_detail_id'] for result in query_database(query)]

def get_patients():
    query = "SELECT * FROM Patient "
    return query_database(query)

def get_doctors():
    query = "SELECT * FROM Doctor "
    return query_database(query)

def get_medications():
    query = "SELECT * FROM Medication "
    return query_database(query)

if __name__ == '__main__':
    app.run(debug=True)
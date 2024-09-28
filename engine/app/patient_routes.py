from flask_login import current_user, login_user, logout_user, login_required
from flask import request, jsonify, session, redirect, url_for
from .helper import role_required, create_user_folder, save_file
from datetime import datetime
from app import app, db
from .models import Users, Patients, Appointments, Doctors, Red_cross, Prescriptions
from sqlalchemy.exc import IntegrityError



@app.route('/patient/register', methods=['POST'])
@login_required
@role_required('patient')
def register_patient():
    if not current_user.is_authenticated:
            return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    try:
        data = request.form.to_dict()
        if not data['first_name'] or not data['last_name'] or not data['gender'] \
            or not data['date_of_birth'] or not data['phone']\
                or not data['address'] or not data['zip_code']:
            return jsonify({'message': 'Missing data'}), 400
        
        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        
        profile_picture = None
        if 'profile_picture' in request.files and not Patients.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['profile_picture']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                profile_picture = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        banner_picture = None
        if 'banner_picture' in request.files and not Patients.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['banner_picture']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                banner_picture = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
        
        patient = Patients (
            user_id=current_user.user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data['gender'],
            date_of_birth= date_of_birth,
            phone=data['phone'],
            address=data['address'],
            zip_code=data['zip_code'],
            profile_picture=profile_picture,
            banner_picture=banner_picture
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Patient registered'}), 201
    except IntegrityError:
        return jsonify({'message': 'Patient already registered'}), 400
    

@app.route('/patient/update', methods=['PUT'])
@login_required
@role_required('patient')
def update_patient():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    data = request.form.to_dict()
    try:
        patient = Patients.query.filter_by(user_id=current_user.user_id).first()
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        
        if 'first_name' in data and data['first_name'].strip():
            patient.first_name = data.get('first_name')
        if 'last_name' in data and data['last_name'].strip():
            patient.last_name = data.get('last_name')
        if 'gender' in data and data['gender'].strip():
            gender = data.get('gender')
            if gender and gender not in ['male', 'female']:
                return jsonify({'message': 'Only male or female is allowed'}), 400

        if 'date_of_birth' in data and data['date_of_birth'].strip():
            date_of_birth_str = data.get('date_of_birth')
            if date_of_birth_str:
                try:
                    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                    patient.date_of_birth = date_of_birth
                except ValueError:
                    return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        if 'phone' in data and data['phone'].strip():
            patient.phone = data.get('phone')
        if 'address' in data and data['address'].strip():
            patient.address = data.get('address')
        if 'zip_code' in data and data['zip_code'].strip():
            patient.zip_code = data.get('zip_code')

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                patient.profile_picture = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        if 'banner_picture' in request.files:
            file = request.files['banner_picture']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                patient.banner_picture = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
        
        db.session.commit()
        return jsonify({'message': 'Patient updated'}), 200
    
    except IntegrityError:
        return jsonify({'message': 'Patient already registered'}), 400
    

@app.route('/patient/profile/<string:username>', methods=['GET'])
@login_required
def patient_profile(username):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    patient = Patients.query.join(Users).filter(Users.username == username).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    if patient.is_deleted == True:
        return jsonify({'message': 'Patient not found'}), 404
    
    return jsonify({
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'gender': patient.gender,
        'date_of_birth': patient.date_of_birth,
        'phone': patient.phone,
        'address': patient.address,
        'zip_code': patient.zip_code,
        'is_active': patient.user.is_active
    }), 200


# @app.route('/patient/appointments', methods=['GET'])
# @login_required
# @role_required('patient')
# def list_patient_appointments():
#     if not current_user.is_authenticated:
#         return jsonify({'message': 'You must be logged in to access this page'}), 401

#     patient = Patients.query.filter_by(user_id=current_user.user_id).first()
#     if not patient:
#         return jsonify({'message': 'Patient not found'}), 404

#     appointments = Appointments.query.filter_by(patient_id=patient.patient_id).all()
#     if not appointments:
#         return jsonify({'message': 'No appointments found'}), 404

#     appointment_list = []
#     for appointment in appointments:
#         appointment_list.append({
#             'appointment_name': appointment.appointment_name,
#             'appointment_type': appointment.appointment_type,
#             'appointment_description': appointment.appointment_description,
#             'appointment_date': appointment.appointment_date,
#             'appointment_time': appointment.appointment_time,
#             'is_active': appointment.is_active
#         })
#     return jsonify(appointment_list), 200

@app.route('/patient/appointments', methods=['GET'])
@login_required
@role_required('patient')
def list_patient_appointments():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    patient = Patients.query.filter_by(user_id=current_user.user_id).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    appointments = Appointments.query.filter_by(patient_id=patient.patient_id).all()
    if not appointments:
        return jsonify({'message': 'No appointments found'}), 404

    appointment_list = []
    for appointment in appointments:
        first_name = last_name = red_cross_name = middle_name = 'Unknown'
        if appointment.doctor_id:
            doctor = Doctors.query.filter_by(doctor_id=appointment.doctor_id).first()
            source = 'doctor'
            if doctor:
                first_name = doctor.first_name
                middle_name = doctor.middle_name
                last_name = doctor.last_name

        else:
            red_cross = Red_cross.query.filter_by(red_cross_id=appointment.red_cross_id).first()
            source = 'red cross'
            if red_cross:
                red_cross_name = red_cross.red_cross_name

        appointment_list.append({
            'appointment_name': appointment.appointment_name,
            'appointment_type': appointment.appointment_type,
            'appointment_description': appointment.appointment_description,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'is_active': appointment.is_active,
            'source': source,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'red_cross_name': red_cross_name
        })
    return jsonify(appointment_list), 200


@app.route('/patient/prescriptions' , methods=['GET'])
@login_required
@role_required('patient')
def list_patient_prescriptions():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    patient = Patients.query.filter_by(user_id=current_user.user_id).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    prescriptions = Prescriptions.query.filter_by(patient_id=patient.patient_id).all()
    if not prescriptions:
        return jsonify({'message': 'No prescriptions found'}), 404

    prescription_list = []
    for prescription in prescriptions:
        first_name = last_name = red_cross_name = middle_name = 'Unknown'
        if prescription.doctor_id:
            doctor = Doctors.query.filter_by(doctor_id=prescription.doctor_id).first()
            source = 'doctor'
            if doctor:
                first_name = doctor.first_name
                middle_name = doctor.middle_name
                last_name = doctor.last_name

        else:
            red_cross = Red_cross.query.filter_by(red_cross_id=prescription.red_cross_id).first()
            source = 'red cross'
            if red_cross:
                red_cross_name = red_cross.red_cross_name

        prescription_list.append({
            'created_at': prescription.created_at,
            'prescription_name': prescription.prescription_name,
            'prescription_description': prescription.prescription_description,
            'source': source,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'prescription_doc': prescription.prescription_doc,
            'red_cross_name': red_cross_name
        })
    return jsonify(prescription_list), 200
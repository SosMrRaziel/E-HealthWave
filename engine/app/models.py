from app import db
from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import sqlalchemy as sa
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    """ Users model """
    __tablename__ = 'users'
    user_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(25), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(sa.Enum('patient', 'doctor', 'red cross'))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    _is_active = db.Column(db.Boolean, default=True)

    doctor = db.relationship('Doctors', uselist=False, back_populates='user')
    patient = db.relationship('Patients', uselist=False, back_populates='user')
    red_cross = db.relationship('Red_cross', uselist=False, back_populates='user')

    sent_messages = db.relationship('Messages', foreign_keys='Messages.sender_id', back_populates='sender', lazy='dynamic')
    received_messages = db.relationship('Messages', foreign_keys='Messages.receiver_id', back_populates='receiver', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_role(self, role):
        if role in ['patient', 'doctor']:
            self.role = role
        else:
            raise ValueError('Invalid role')
        
    def has_role(self, role):
        return self.role == role
    
    def get_id(self):
        return self.user_id


    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'last_login': self.last_login,
            'created_at': self.created_at,
            'is_active': self.is_active
        }

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Doctors(db.Model):
    """ Doctors model """
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), unique=True)
    first_name = db.Column(db.String(25), index=True)
    middle_name = db.Column(db.String(25), index=True)
    last_name = db.Column(db.String(25), index=True)
    gender = db.Column(sa.Enum('male', 'female'))
    date_of_birth = db.Column(db.DateTime)
    # email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(15), index=True, unique=True)
    specialty = db.Column(db.String(100), index=True)
    license_number = db.Column(db.String(50), index=True)
    qualification = db.Column(db.String(200), index=True)
    address = db.Column(db.String(120), index=True)
    city = db.Column(db.String(25), index=True)
    state = db.Column(db.String(25), index=True)
    zip_code = db.Column(db.String(10), index=True)
    bio = db.Column(db.String(255), index=True)
    profile_picture = db.Column(db.String(255), index=True)
    banner_picture = db.Column(db.String(255), index=True)
    # is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='doctor')
    certificate = db.relationship('Certificates', back_populates='doctor')
    Working_days = db.relationship('Working_days', uselist=False, back_populates='doctor')
    chat_rooms = db.relationship('ChatRoom', back_populates='doctor')
    appointment = db.relationship('Appointments', back_populates='doctor')
    document = db.relationship('Documents', back_populates='doctor')
    prescription = db.relationship('Prescriptions', back_populates='doctor')
    medical_history = db.relationship('MedicalHistory', back_populates='doctor')

    def to_dict(self):
        return {
            'doctor_id': self.doctor_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'email': self.email,
            'phone': self.phone,
            'specialty': self.specialty,
            'license_number': self.license_number,
            'qualification': self.qualification,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'banner_picture': self.banner_picture,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return '<Doctor {}>'.format(self.first_name)
    
class Red_cross(db.Model):
    """ Red Cross model """
    __tablename__ = 'red_cross'
    red_cross_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), unique=True)
    red_cross_name = db.Column(db.String(100), index=True)
    red_cross_address = db.Column(db.String(120), index=True)
    red_cross_city = db.Column(db.String(25), index=True)
    red_cross_state = db.Column(db.String(25), index=True)
    red_cross_zip_code = db.Column(db.String(10), index=True)
    red_cross_phone = db.Column(db.String(15), index=True, unique=True)
    red_cross_email = db.Column(db.String(120), index=True, unique=True)
    red_cross_website = db.Column(db.String(255), index=True)
    red_cross_logo = db.Column(db.String(255), index=True)
    red_cross_banner = db.Column(db.String(255), index=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='red_cross')
    certificate = db.relationship('Certificates', back_populates='red_cross')
    Working_days = db.relationship('Working_days', uselist=False, back_populates='red_cross')
    appointment = db.relationship('Appointments', back_populates='red_cross')
    document = db.relationship('Documents', back_populates='red_cross')
    prescription = db.relationship('Prescriptions', back_populates='red_cross')
    medical_history = db.relationship('MedicalHistory', back_populates='red_cross')


    def to_dict(self):
        return {
            'red_cross_id': self.red_cross_id,
            'red_cross_name': self.red_cross_name,
            'red_cross_address': self.red_cross_address,
            'red_cross_city': self.red_cross_city,
            'red_cross_state': self.red_cross_state,
            'red_cross_zip_code': self.red_cross_zip_code,
            'red_cross_phone': self.red_cross_phone,
            'red_cross_email': self.red_cross_email,
            'red_cross_website': self.red_cross_website,
            'red_cross_logo': self.red_cross_logo,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return '<Red_cross {}>'.format(self.red_cross_name)

    
class Patients(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), unique=True)
    first_name = db.Column(db.String(25), index=True)
    middle_name = db.Column(db.String(25), index=True)
    last_name = db.Column(db.String(25), index=True)
    gender = db.Column(sa.Enum('male', 'female'))
    date_of_birth = db.Column(db.DateTime)
    # email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(15), index=True, unique=True)
    address = db.Column(db.String(120), index=True)
    city = db.Column(db.String(25), index=True)
    state = db.Column(db.String(25), index=True)
    zip_code = db.Column(db.String(10), index=True)
    about_me = db.Column(db.String(255), index=True)
    profile_picture = db.Column(db.String(255), index=True)
    banner_picture = db.Column(db.String(255), index=True)
    # is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='patient')
    chat_rooms = db.relationship('ChatRoom', back_populates='patient')
    appointment = db.relationship('Appointments', back_populates='patient')
    document = db.relationship('Documents', back_populates='patient')
    prescription = db.relationship('Prescriptions', back_populates='patient')
    medical_history = db.relationship('MedicalHistory', back_populates='patient')


    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'about_me': self.about_me,
            'profile_picture': self.profile_picture,
            'banner_picture': self.banner_picture,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }

    
    def __repr__(self):
        return '<Patient {}>'.format(self.first_name)
    
class Certificates(db.Model):
    __tablename__ = 'certificates'
    certificate_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    red_cross_id = db.Column(db.String(60), db.ForeignKey('red_cross.red_cross_id'))
    certificate_name = db.Column(db.String(100), index=True)
    certificate_number = db.Column(db.String(50), index=True)
    issue_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.DateTime)
    certificate_picture = db.Column(db.String(255), index=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    doctor = db.relationship('Doctors', back_populates='certificate')
    red_cross = db.relationship('Red_cross', back_populates='certificate')    

    def to_dict(self):
        return {
            'certificate_id': self.certificate_id,
            'doctor_id': self.doctor_id,
            'certificate_name': self.certificate_name,
            'certificate_number': self.certificate_number,
            'issue_date': self.issue_date,
            'expiry_date': self.expiry_date,
            'certificate_picture': self.certificate_picture,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return '<Certificates {}>'.format(self.certificate_name)
    
class Working_days(db.Model):
    __tablename__ = 'working_days'
    working_day_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    red_cross_id = db.Column(db.String(60), db.ForeignKey('red_cross.red_cross_id'))
    day = db.Column(sa.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
    start_time = db.Column(db.Time, index=True)
    end_time = db.Column(db.Time, index=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    doctor = db.relationship('Doctors', back_populates='Working_days')
    red_cross = db.relationship('Red_cross', back_populates='Working_days')

    def to_dict(self):
        return {
            'working_day_id': self.working_day_id,
            'doctor_id': self.doctor_id,
            'day': self.day,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }

    def __repr__(self):
        return '<Working_days {}>'.format(self.day)
    
class Appointments(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    red_cross_id = db.Column(db.String(60), db.ForeignKey('red_cross.red_cross_id'))
    appointment_type = db.Column(sa.Enum('in person', 'telemedicine'), default='in-person')
    appointment_name = db.Column(db.String(100), index=True)
    appointment_description = db.Column(db.String(500), index=True)
    appointment_date = db.Column(db.DateTime)
    appointment_time = db.Column(db.String(10), index=True)
    appointment_status = db.Column(sa.Enum('scheduled', 'cancelled', 'completed'), default='scheduled')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    document = db.relationship('Documents', back_populates='appointment')
    patient = db.relationship('Patients', back_populates='appointment')
    doctor = db.relationship('Doctors', back_populates='appointment')
    red_cross = db.relationship('Red_cross', back_populates='appointment')
    prescriptions = db.relationship('Prescriptions', back_populates='appointment')

    def to_dict(self):
        return {
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'red_cross_id': self.red_cross_id,
            'appointment_type': self.appointment_type,
            'appointment_name': self.appointment_name,
            'appointment_description': self.appointment_description,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'appointment_status': self.appointment_status,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return '<Appointment {}>'.format(self.appointment_id)
    
class Documents(db.Model):
    __tablename__ = 'documents'
    document_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    appointment_id = db.Column(db.String(60), db.ForeignKey('appointments.appointment_id'))
    doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    red_cross_id = db.Column(db.String(60), db.ForeignKey('red_cross.red_cross_id'))
    patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
    document_name = db.Column(db.String(100), index=True)
    document_type = db.Column(db.String(50), index=True)
    document_description = db.Column(db.String(255), index=True)
    document_file = db.Column(db.String(255), index=True)
    document_url = db.Column(db.String(255), index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    doctor = db.relationship('Doctors', back_populates='document')
    red_cross = db.relationship('Red_cross', back_populates='document')
    patient = db.relationship('Patients', back_populates='document')
    appointment = db.relationship('Appointments', back_populates='document')

    def to_dict(self):
        return {
            'document_id': self.document_id,
            'appointment_id': self.appointment_id,
            'document_name': self.document_name,
            'document_description': self.document_description,
            'document_file': self.document_file,
            'document_type': self.document_type,
            'document_url': self.document_url,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return '<Document {}>'.format(self.document_name)
    
class Prescriptions(db.Model):
    __tablename__ = 'prescriptions'
    prescription_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    appointment_id = db.Column(db.String(60), db.ForeignKey('appointments.appointment_id'))
    patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    red_cross_id = db.Column(db.String(60), db.ForeignKey('red_cross.red_cross_id'))
    prescription_name = db.Column(db.String(100), index=True)
    prescription_type = db.Column(db.String(50), index=True)
    prescription_description = db.Column(db.String(255), index=True)
    prescription_doc = db.Column(db.String(255), index=True)
    # prescription_url = db.Column(db.String(255), index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    patient = db.relationship('Patients', back_populates='prescription')
    doctor = db.relationship('Doctors', back_populates='prescription')
    red_cross = db.relationship('Red_cross', back_populates='prescription')
    appointment = db.relationship('Appointments', back_populates='prescriptions')

    def to_dict(self):
        return {
            'prescription_id': self.prescription_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'prescription_name': self.prescription_name,
            'prescription_type': self.prescription_type,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'prescription_doc': self.prescription_doc,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return '<Prescription {}>'.format(self.prescription_name)
    
class MedicalHistory(db.Model):
    __tablename__ = 'medical_history'
    medical_history_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    red_cross_id = db.Column(db.String(60), db.ForeignKey('red_cross.red_cross_id'))
    medical_history_name = db.Column(db.String(100), index=True)
    medical_history_type = db.Column(db.String(50), index=True)
    medical_history_file = db.Column(db.String(255), index=True)
    allergies = db.Column(sa.JSON)
    medications = db.Column(sa.JSON)
    surgeries = db.Column(sa.JSON)
    medical_conditions = db.Column(sa.JSON)
    past_illnesses = db.Column(sa.JSON)
    immunizations = db.Column(sa.JSON)
    smoking_status = db.Column(sa.Enum('never smoked', 'current smoker', 'former smoker'))
    alcohol_use = db.Column(sa.Enum('never', 'social drinker', 'heavy drinker'))
    exercise_frequency = db.Column(sa.Enum('none', 'light', 'moderate', 'heavy'))
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    patient = db.relationship('Patients', back_populates='medical_history')
    doctor = db.relationship('Doctors', back_populates='medical_history')
    red_cross = db.relationship('Red_cross', back_populates='medical_history')
    

    def to_dict(self):
        return {
            'medical_history_id': self.medical_history_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'Red_cross_id': self.Red_cross_id,
            'medical_history_name': self.medical_history_name,
            'medical_history_type': self.medical_history_type,
            'medical_history_file': self.medical_history_url,
            'allergies': self.allergies,
            'medications': self.medications,
            'surgeries': self.surgeries,
            'medical_conditions': self.medical_conditions,
            'past_illnesses': self.past_illnesses,
            'immunizations': self.immunizations,
            'smoking_status': self.smoking_status,
            'alcohol_use': self.alcohol_use,
            'exercise_frequency': self.exercise_frequency,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }

# class Notifications(db.Model):
    # __tablename__ = 'notifications'
#     notification_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     notification_type = db.Column(db.String(50), index=True)
#     notification_message = db.Column(db.String(255), index=True)
#     notification_url = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     user = db.relationship('Users', backref='notification')

#     def to_dict(self):
#         return {
#             'notification_id': self.notification_id,
#             'user_id': self.user_id,
#             'notification_type': self.notification_type,
#             'notification_message': self.notification_message,
#             'notification_url': self.notification_url,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Notification {}>'.format(self.notification_id)

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    room_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    doctor = db.relationship('Doctors', back_populates='chat_rooms')
    patient = db.relationship('Patients', back_populates='chat_rooms')
    messages = db.relationship('Messages', back_populates='chat_room')

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'created_at': self.created_at,
            'is_active': self.is_active
        }

    def __repr__(self):
        return '<ChatRoom {}>'.format(self.room_id)
    
class Messages(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    chat_room_id = db.Column(db.String(60), db.ForeignKey('chat_rooms.room_id'))
    sender_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
    receiver_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
    message = db.Column(db.String(255), index=True)
    message_type = db.Column(db.String(50), index=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)

    chat_room = db.relationship('ChatRoom', back_populates='messages')
    sender = db.relationship('Users', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('Users', foreign_keys=[receiver_id], back_populates='received_messages')

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'chat_room_id': self.chat_room_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message': self.message,
            'message_type': self.message_type,
            'is_active': self.is_active,
            'updated_at': self.updated_at,
            'is_deleted': self.is_deleted
        }

    def __repr__(self):
        return '<Message {}>'.format(self.message_id)

# class Posts(db.Model):
    # __tablename__ = 'posts'
#     post_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     post = db.Column(db.String(255), index=True)
#     post_type = db.Column(db.String(50), index=True)
#     post_url = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     user = db.relationship('Users', backref='post')

#     def to_dict(self):
#         return {
#             'post_id': self.post_id,
#             'user_id': self.user_id,
#             'post': self.post,
#             'post_type': self.post_type,
#             'post_url': self.post_url,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Post {}>'.format(self.post_id)
    
# class Post_likes(db.Model):
    # __tablename__ = 'post_likes'
#     post_like_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     post_id = db.Column(db.String(60), db.ForeignKey('posts.post_id'))
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     post = db.relationship('Posts', backref='post_like')
#     user = db.relationship('Users', backref='post_like')

#     def to_dict(self):
#         return {
#             'post_like_id': self.post_like_id,
#             'post_id': self.post_id,
#             'user_id': self.user_id,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<PostLike {}>'.format(self.post_like_id)
    
# class Comments(db.Model):
    # __tablename__ = 'comments'
#     comment_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     post_id = db.Column(db.String(60), db.ForeignKey('posts.post_id'))
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     comment = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     post = db.relationship('Posts', backref='comment')
#     user = db.relationship('Users', backref='comment')

#     def to_dict(self):
#         return {
#             'comment_id': self.comment_id,
#             'post_id': self.post_id,
#             'user_id': self.user_id,
#             'comment': self.comment,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Comment {}>'.format(self.comment_id)

# class Comment_likes(db.Model):
    # __tablename__ = 'comment_likes'
#     comment_like_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     comment_id = db.Column(db.String(60), db.ForeignKey('comments.comment_id'))
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     comment = db.relationship('Comments', backref='comment_like')
#     user = db.relationship('Users', backref='comment_like')

#     def to_dict(self):
#         return {
#             'comment_like_id': self.comment_like_id,
#             'comment_id': self.comment_id,
#             'user_id': self.user_id,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<CommentLike {}>'.format(self.comment_like_id)

# class user_IP(db.Model):
    # __tablename__ = 'user_ip'
#     user_ip_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
    # user_ip = db.Column(db.String(60), index=True, unique=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     user = db.relationship('Users', backref='user_ip')

#     def to_dict(self):
#         return {
#             'user_ip_id': self.user_ip_id,
#             'user_id': self.user_id,
#             'user_ip': self.user_ip,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<UserIP {}>'.format(self.user_ip_id)
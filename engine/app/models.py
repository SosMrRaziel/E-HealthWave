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
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), unique=True)
    user = db.relationship('Users', back_populates='doctor')
    Certificate = db.relationship('Certificates', backref='doctor', lazy='dynamic')
    Working_days = db.relationship('Working_days', uselist=False, back_populates='doctor')

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
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), unique=True)
    user = db.relationship('Users', back_populates='red_cross')
    Certificate = db.relationship('Certificates', backref='red_cross', lazy='dynamic')
    Working_days = db.relationship('Working_days', uselist=False, back_populates='red_cross')


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
        return '<RedCross {}>'.format(self.red_cross_name)

    
class Patients(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
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
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), unique=True)
    user = db.relationship('Users', back_populates='patient')
    

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
    # doctor = db.relationship('Doctors', backref='certificate', lazy='dynamic')

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
    document = db.relationship('Documents', backref='appointment', lazy='dynamic')
    # patient = db.relationship('Patients', backref='appointment', lazy='dynamic')
    # doctor = db.relationship('Doctors', backref='appointment', lazy='dynamic')
    # Red_cross = db.relationship('Red_cross', backref='appointment', lazy='dynamic')

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
    # patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
    # doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
    document_name = db.Column(db.String(100), index=True)
    document_type = db.Column(db.String(50), index=True)
    document_description = db.Column(db.String(255), index=True)
    document_file = db.Column(db.String(255), index=True)
    document_url = db.Column(db.String(255), index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    # patient = db.relationship('Patients', backref='document', lazy='dynamic')
    # doctor = db.relationship('Doctors', backref='document', lazy='dynamic')

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
    
# class Prescriptions(db.Model):
#     __tablename__ = 'prescriptions'
#     prescription_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
#     doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
#     prescription_name = db.Column(db.String(100), index=True)
#     prescription_type = db.Column(db.String(50), index=True)
#     prescription_url = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     patient = db.relationship('Patients', backref='prescription', lazy='dynamic')
#     doctor = db.relationship('Doctors', backref='prescription', lazy='dynamic')

#     def to_dict(self):
#         return {
#             'prescription_id': self.prescription_id,
#             'patient_id': self.patient_id,
#             'doctor_id': self.doctor_id,
#             'prescription_name': self.prescription_name,
#             'prescription_type': self.prescription_type,
#             'prescription_url': self.prescription_url,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Prescription {}>'.format(self.prescription_name)
    
# class MedicalHistory(db.Model):
#     __tablename__ = 'medical_history'
#     medical_history_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
#     doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
#     medical_history_name = db.Column(db.String(100), index=True)
#     medical_history_type = db.Column(db.String(50), index=True)
#     medical_history_url = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     patient = db.relationship('Patients', backref='medical_history', lazy='dynamic')
#     doctor = db.relationship('Doctors', backref='medical_history', lazy='dynamic')

#     def to_dict(self):
#         return {
#             'medical_history_id': self.med,
#             'patient_id': self.patient_id,
#             'doctor_id': self.doctor_id,
#             'medical_history_name': self.medical_history_name,
#             'medical_history_type': self.medical_history_type,
#             'medical_history_url': self.medical_history_url,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<MedicalHistory {}>'.format(self.medical_history_name)

# class Notifications(db.Model):
#     __tablename__ = 'notifications'
#     notification_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     notification_type = db.Column(db.String(50), index=True)
#     notification_message = db.Column(db.String(255), index=True)
#     notification_url = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     user = db.relationship('Users', backref='notification', lazy='dynamic')

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
    
# class Messages(db.Model):
#     __tablename__ = 'messages'
#     message_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     sender_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     receiver_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     message = db.Column(db.String(255), index=True)
#     message_type = db.Column(db.String(50), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     sender = db.relationship('Users', backref='message', lazy='dynamic')
#     receiver = db.relationship('Users', backref='message', lazy='dynamic')

#     def to_dict(self):
#         return {
#             'message_id': self.message_id,
#             'sender_id': self.sender_id,
#             'receiver_id': self.receiver_id,
#             'message': self.message,
#             'message_type': self.message_type,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Message {}>'.format(self.message_id)

# class Posts(db.Model):
#     __tablename__ = 'posts'
#     post_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     post = db.Column(db.String(255), index=True)
#     post_type = db.Column(db.String(50), index=True)
#     post_url = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     user = db.relationship('Users', backref='post', lazy='dynamic')

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
#     __tablename__ = 'post_likes'
#     post_like_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     post_id = db.Column(db.String(60), db.ForeignKey('posts.post_id'))
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     post = db.relationship('Posts', backref='post_like', lazy='dynamic')
#     user = db.relationship('Users', backref='post_like', lazy='dynamic')

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
#     __tablename__ = 'comments'
#     comment_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     post_id = db.Column(db.String(60), db.ForeignKey('posts.post_id'))
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     comment = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     post = db.relationship('Posts', backref='comment', lazy='dynamic')
#     user = db.relationship('Users', backref='comment', lazy='dynamic')

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
#     __tablename__ = 'comment_likes'
#     comment_like_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     comment_id = db.Column(db.String(60), db.ForeignKey('comments.comment_id'))
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     comment = db.relationship('Comments', backref='comment_like', lazy='dynamic')
#     user = db.relationship('Users', backref='comment_like', lazy='dynamic')

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
#     __tablename__ = 'user_ip'
#     user_ip_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
    # user_ip = db.Column(db.String(60), index=True, unique=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     user = db.relationship('Users', backref='user_ip', lazy='dynamic')

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
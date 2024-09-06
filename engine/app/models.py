from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import sqlalchemy as sa
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(25), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(sa.Enum('patient', 'doctor'))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    _is_active = db.Column(db.Boolean, default=True)
    doctor = db.relationship('Doctors', backref='user', uselist=False)
    patient = db.relationship('Patients', backref='user', uselist=False)

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
    
    # @property
    # def is_authenticated(self):
    #     return True
    
    # @property
    # def is_anonymous(self):
    #     return False
    
    # @property
    # def is_active(self):
    #     return self._is_active

    
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
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    first_name = db.Column(db.String(25), index=True)
    middle_name = db.Column(db.String(25), index=True)
    last_name = db.Column(db.String(25), index=True)
    gender = db.Column(sa.Enum('male', 'female'))
    date_of_birth = db.Column(db.DateTime)
    email = db.Column(db.String(120), index=True, unique=True)
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
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), nullable=False)

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
    
class Patients(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'))
    first_name = db.Column(db.String(25), index=True)
    middle_name = db.Column(db.String(25), index=True)
    last_name = db.Column(db.String(25), index=True)
    gender = db.Column(sa.Enum('male', 'female'))
    email = db.Column(db.String(120), index=True, unique=True)
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
    user_id = db.Column(db.String(60), db.ForeignKey('users.user_id'), nullable=False)

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
    
# class Certificates(db.Model):
#     __tablename__ = 'certificates'
#     certificate_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
#     certificate_name = db.Column(db.String(100), index=True)
#     certificate_number = db.Column(db.String(50), index=True)
#     issue_date = db.Column(db.DateTime)
#     expiry_date = db.Column(db.DateTime)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     doctor = db.relationship('Doctors', backref='certificate', lazy='dynamic')

#     def to_dict(self):
#         return {
#             'certificate_id': self.certificate_id,
#             'doctor_id': self.doctor_id,
#             'certificate_name': self.certificate_name,
#             'certificate_number': self.certificate_number,
#             'issue_date': self.issue_date,
#             'expiry_date': self.expiry_date,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Certificate {}>'.format(self.certificate_name)
    
# class Appointments(db.Model):
#     __tablename__ = 'appointments'
#     appointment_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
#     doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
#     appointment_date = db.Column(db.DateTime)
#     appointment_time = db.Column(db.String(10), index=True)
#     appointment_type = db.Column(sa.Enum('in-person', 'telemedicine'), default='in-person')
#     appointment_status = db.Column(sa.Enum('scheduled', 'cancelled', 'completed'), default='scheduled')
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     patient = db.relationship('Patients', backref='appointment', lazy='dynamic')
#     doctor = db.relationship('Doctors', backref='appointment', lazy='dynamic')

#     def to_dict(self):
#         return {
#             'appointment_id': self.appointment_id,
#             'patient_id': self.patient_id,
#             'doctor_id': self.doctor_id,
#             'appointment_date': self.appointment_date,
#             'appointment_time': self.appointment_time,
#             'appointment_type': self.appointment_type,
#             'appointment_status': self.appointment_status,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Appointment {}>'.format(self.appointment_id)
    
# class Documents(db.Model):
#     __tablename__ = 'documents'
#     document_id = db.Column(db.String(60), default=lambda: str(uuid.uuid4()), primary_key=True)
#     patient_id = db.Column(db.String(60), db.ForeignKey('patients.patient_id'))
#     doctor_id = db.Column(db.String(60), db.ForeignKey('doctors.doctor_id'))
#     document_name = db.Column(db.String(100), index=True)
#     picture = db.Column(db.String(160), index=True)
#     document_type = db.Column(db.String(50), index=True)
#     document_url = db.Column(db.String(255), index=True)
#     is_active = db.Column(db.Boolean, default=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow)
#     is_deleted = db.Column(db.Boolean, default=False)
#     patient = db.relationship('Patients', backref='document', lazy='dynamic')
#     doctor = db.relationship('Doctors', backref='document', lazy='dynamic')

#     def to_dict(self):
#         return {
#             'document_id': self.document_id,
#             'patient_id': self.patient_id,
#             'doctor_id': self.doctor_id,
#             'document_name': self.document_name,
#             'picture': self.picture,
#             'document_type': self.document_type,
#             'document_url': self.document_url,
#             'is_active': self.is_active,
#             'updated_at': self.updated_at,
#             'is_deleted': self.is_deleted
#         }
    
#     def __repr__(self):
#         return '<Document {}>'.format(self.document_name)
    
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
#     user_ip = db.Column(db.String(60), index=True)
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


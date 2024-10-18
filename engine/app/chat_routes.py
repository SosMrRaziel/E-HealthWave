from flask import request, jsonify
from app import app ,db, socketio
from app.models import ChatRoom, Messages, Doctors, Patients, Users
from flask_login import current_user, login_required
from .helper import role_required
from flask_socketio import emit, join_room, leave_room
import logging



@app.route('/chat/create', methods=['POST'])
@login_required
@role_required("doctor")
def create_chat_room():
    
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'message': 'Patient ID is required'}), 400

    # Check if the current user is a valid doctor
    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Invalid doctor ID'}), 400

    # Check if the patient exists
    patient = db.session.query(Patients).join(Users).filter(Users.username == username).first()
    print(patient)
    if not patient:
        return jsonify({'message': 'Invalid patient ID'}), 400

    chat_room = ChatRoom(doctor_id=doctor.doctor_id, patient_id=patient.patient_id)
    db.session.add(chat_room)
    db.session.commit()

    socketio.emit('chat_room_created', {'room_id': chat_room.room_id, 'doctor_id': doctor.doctor_id, 'patient_id': patient.patient_id})

    return jsonify(chat_room.to_dict()), 201


@app.route('/chat/<room_id>/messages', methods=['POST'])
@login_required
def send_message(room_id):
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'message': 'Message content is required'}), 400

    chat_room = ChatRoom.query.get(room_id)
    if not chat_room:
        return jsonify({'message': 'Invalid room ID'}), 400
    
        # Debug logging
    # logging.debug(f"Current user ID: {current_user.user_id}")
    # logging.debug(f"Chat room doctor ID: {chat_room.doctor_id}")
    # logging.debug(f"Chat room patient ID: {chat_room.patient_id}")

    # if chat_room.doctor_id != current_user.user_id and chat_room.patient_id != current_user.user_id:
    #     return jsonify({'message': 'You are not a part of this chat room'}), 401

    new_message = Messages(chat_room_id=room_id, sender_id=current_user.user_id, message=message)
    db.session.add(new_message)
    db.session.commit()
    # new_message = Messages(room_id=room_id, sender_id=current_user.user_id, message=message)
    # db.session.add(new_message)
    # db.session.commit()

    sender = Users.query.get(current_user.user_id)

    socketio.emit('new_message', {
        'room_id': room_id,
        'message': message,
        'sender_id': current_user.user_id,
        'sender_username': sender.username  # Assuming the Users model has a username field
    }, room=room_id)

    return jsonify({
        # 'message_id': new_message.message_id,
        # 'chat_room_id': new_message.chat_room_id,
        # 'sender_id': new_message.sender_id,
        'sender_username': sender.username,  # Include sender's username in the response
        'message': new_message.message,
        # 'message_type': new_message.message_type,
        # 'is_active': new_message.is_active,
        # 'updated_at': new_message.updated_at,
        # 'is_deleted': new_message.is_deleted,
        'is_read': new_message.is_read
    }), 201


@socketio.on('join')
def on_join(data):
    room_id = data['room_id']
    join_room(room_id)
    emit('status', {'msg': f'{current_user.username} has entered the room.'}, room=room_id)

@socketio.on('leave')
def on_leave(data):
    room_id = data['room_id']
    leave_room(room_id)
    emit('status', {'msg': f'{current_user.username} has left the room.'}, room=room_id)

@app.route('/chat/<room_id>/messages', methods=['GET'])
@login_required
def get_messages(room_id):
    chat_room = ChatRoom.query.get(room_id)
    if not chat_room:
        return jsonify({'message': 'Invalid room ID'}), 400

    messages = Messages.query.filter_by(chat_room_id=room_id).all()
    messages_list = [message.to_dict() for message in messages]

    return jsonify(messages_list), 200
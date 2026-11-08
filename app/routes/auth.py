from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, CustomerProfile, OwnerProfile
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    full_name = data.get('full_name', '').strip()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()
    role = data.get('role', 'customer').lower() # 'customer' or 'owner'

    if not email or not full_name or not password:
        return jsonify({'error': 'Name, email and password are required'}), 400

    if role not in ['customer', 'owner']:
        role = 'customer'

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 400

    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role == 'customer':
        profile = CustomerProfile(
            user_id=user.id,
            city=data.get('city', ''),
            state=data.get('state', '')
        )
        db.session.add(profile)
    elif role == 'owner':
        profile = OwnerProfile(
            user_id=user.id,
            business_name=data.get('business_name', f"{full_name}'s Venues"),
            business_registration_no=data.get('business_registration_no', '')
        )
        db.session.add(profile)

    db.session.commit()

    # Create token - in PyJWT identity should be a string
    token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account has been deactivated. Please contact support.'}), 403

    token = create_access_token(identity=str(user.id))

    profile_data = {}
    if user.role == 'customer' and user.customer_profile:
        profile_data = user.customer_profile.to_dict()
    elif user.role == 'owner' and user.owner_profile:
        profile_data = user.owner_profile.to_dict()

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict(),
        'profile': profile_data
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile_data = {}
    if user.role == 'customer' and user.customer_profile:
        profile_data = user.customer_profile.to_dict()
    elif user.role == 'owner' and user.owner_profile:
        profile_data = user.owner_profile.to_dict()

    return jsonify({
        'user': user.to_dict(),
        'profile': profile_data
    })

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip()

    if user.role == 'customer':
        if not user.customer_profile:
            user.customer_profile = CustomerProfile(user_id=user.id)
        if 'city' in data:
            user.customer_profile.city = data['city']
        if 'state' in data:
            user.customer_profile.state = data['state']
        if 'address' in data:
            user.customer_profile.address = data['address']
        if 'preferred_event_type' in data:
            user.customer_profile.preferred_event_type = data['preferred_event_type']

    elif user.role == 'owner':
        if not user.owner_profile:
            user.owner_profile = OwnerProfile(user_id=user.id, business_name=user.full_name)
        if 'business_name' in data:
            user.owner_profile.business_name = data['business_name']
        if 'business_registration_no' in data:
            user.owner_profile.business_registration_no = data['business_registration_no']
        if 'bank_account_no' in data:
            user.owner_profile.bank_account_no = data['bank_account_no']
        if 'ifsc_code' in data:
            user.owner_profile.ifsc_code = data['ifsc_code']

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()})

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'})

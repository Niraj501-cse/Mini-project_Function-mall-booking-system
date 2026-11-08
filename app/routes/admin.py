from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    User, FunctionHall, Booking, BookingPackage, EventCategory, 
    Review, ContactMessage, WebsiteSetting, Payment
)
from app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def check_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    user_id = int(get_jwt_identity())
    if not check_admin(user_id):
        return jsonify({'error': 'Admin authorization required'}), 403

    total_customers = User.query.filter_by(role='customer').count()
    total_owners = User.query.filter_by(role='owner').count()
    total_halls = FunctionHall.query.count()
    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status='Confirmed').count()
    pending_bookings = Booking.query.filter_by(status='Pending Approval').count()
    awaiting_payment = Booking.query.filter_by(status='Awaiting Payment').count()
    cancelled_bookings = Booking.query.filter_by(status='Cancelled').count()

    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='Success').scalar() or 0.0

    return jsonify({
        'total_customers': total_customers,
        'total_owners': total_owners,
        'total_halls': total_halls,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'awaiting_payment': awaiting_payment,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue
    })

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    user_id = int(get_jwt_identity())
    if not check_admin(user_id):
        return jsonify({'error': 'Admin authorization required'}), 403

    role = request.args.get('role')
    query = User.query
    if role:
        query = query.filter_by(role=role)

    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])

@admin_bp.route('/halls', methods=['GET'])
@jwt_required()
def list_halls():
    user_id = int(get_jwt_identity())
    if not check_admin(user_id):
        return jsonify({'error': 'Admin authorization required'}), 403

    halls = FunctionHall.query.order_by(FunctionHall.created_at.desc()).all()
    return jsonify([h.to_dict() for h in halls])

@admin_bp.route('/halls/<int:hall_id>/toggle-approval', methods=['PATCH'])
@jwt_required()
def toggle_hall_approval(hall_id):
    user_id = int(get_jwt_identity())
    if not check_admin(user_id):
        return jsonify({'error': 'Admin authorization required'}), 403

    hall = FunctionHall.query.get(hall_id)
    if not hall:
        return jsonify({'error': 'Hall not found'}), 404

    hall.is_approved = not hall.is_approved
    db.session.commit()
    return jsonify({'message': f"Hall approval set to {hall.is_approved}", 'hall': hall.to_dict()})

@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
def list_all_bookings():
    user_id = int(get_jwt_identity())
    if not check_admin(user_id):
        return jsonify({'error': 'Admin authorization required'}), 403

    status = request.args.get('status')
    query = Booking.query
    if status:
        query = query.filter_by(status=status)

    bookings = query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])

@admin_bp.route('/packages', methods=['GET', 'POST'])
@jwt_required()
def manage_packages():
    user_id = int(get_jwt_identity())
    if not check_admin(user_id):
        return jsonify({'error': 'Admin authorization required'}), 403

    if request.method == 'GET':
        packages = BookingPackage.query.order_by(BookingPackage.id.desc()).all()
        return jsonify([p.to_dict() for p in packages])

    data = request.get_json() or {}
    pkg = BookingPackage(
        category_id=int(data.get('category_id')),
        name=data.get('name'),
        tier=data.get('tier', 'Standard'),
        description=data.get('description', ''),
        base_price=float(data.get('base_price', 50000.0)),
        guest_capacity=int(data.get('guest_capacity', 200)),
        price_per_plate_veg=float(data.get('price_per_plate_veg', 450.0)),
        price_per_plate_nonveg=float(data.get('price_per_plate_nonveg', 650.0)),
        food_menu_summary=data.get('food_menu_summary', ''),
        decoration_details=data.get('decoration_details', ''),
        is_popular=bool(data.get('is_popular', False)),
        is_active=True
    )
    db.session.add(pkg)
    db.session.commit()
    return jsonify({'message': 'Package created successfully', 'package': pkg.to_dict()}), 201

@admin_bp.route('/packages/<int:pkg_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_package(pkg_id):
    user_id = int(get_jwt_identity())
    if not check_admin(user_id):
        return jsonify({'error': 'Admin authorization required'}), 403

    pkg = BookingPackage.query.get(pkg_id)
    if not pkg:
        return jsonify({'error': 'Package not found'}), 404

    if request.method == 'DELETE':
        db.session.delete(pkg)
        db.session.commit()
        return jsonify({'message': 'Package deleted'})

    data = request.get_json() or {}
    if 'name' in data: pkg.name = data['name']
    if 'tier' in data: pkg.tier = data['tier']
    if 'description' in data: pkg.description = data['description']
    if 'base_price' in data: pkg.base_price = float(data['base_price'])
    if 'guest_capacity' in data: pkg.guest_capacity = int(data['guest_capacity'])
    if 'is_active' in data: pkg.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({'message': 'Package updated successfully', 'package': pkg.to_dict()})

@admin_bp.route('/settings', methods=['GET', 'POST'])
def manage_settings():
    if request.method == 'GET':
        settings = WebsiteSetting.query.all()
        return jsonify({s.key: s.value for s in settings})

    data = request.get_json() or {}
    for k, v in data.items():
        s = WebsiteSetting.query.filter_by(key=k).first()
        if s:
            s.value = str(v)
        else:
            s = WebsiteSetting(key=k, value=str(v))
            db.session.add(s)
    db.session.commit()
    return jsonify({'message': 'Settings saved successfully'})

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, OwnerProfile, FunctionHall, HallImage, Booking, Payment, Notification
from app import db
from datetime import datetime, timedelta
import re

owner_bp = Blueprint('owner', __name__)

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

@owner_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_owner_stats():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'owner':
        return jsonify({'error': 'Unauthorized. Hall owner access required.'}), 403

    owner = user.owner_profile
    if not owner:
        return jsonify({'error': 'Owner profile not found'}), 404

    hall_ids = [h.id for h in owner.halls]

    bookings = Booking.query.filter(Booking.hall_id.in_(hall_ids)).all() if hall_ids else []
    total_revenue = sum(b.advance_paid for b in bookings if b.status == 'Confirmed')
    pending_requests = sum(1 for b in bookings if b.status == 'Pending Approval')
    confirmed_bookings = sum(1 for b in bookings if b.status == 'Confirmed')

    return jsonify({
        'total_halls': len(owner.halls),
        'total_bookings': len(bookings),
        'pending_requests': pending_requests,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'business_name': owner.business_name
    })

@owner_bp.route('/halls', methods=['GET'])
@jwt_required()
def get_owner_halls():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'owner' or not user.owner_profile:
        return jsonify({'error': 'Unauthorized'}), 403

    halls = FunctionHall.query.filter_by(owner_id=user.owner_profile.id).all()
    return jsonify([h.to_dict() for h in halls])

@owner_bp.route('/halls', methods=['POST'])
@jwt_required()
def add_hall():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'owner' or not user.owner_profile:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Hall name is required'}), 400

    slug = slugify(name)
    base_slug = slug
    idx = 1
    while FunctionHall.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{idx}"
        idx += 1

    hall = FunctionHall(
        owner_id=user.owner_profile.id,
        name=name,
        slug=slug,
        tagline=data.get('tagline', 'Magnificent event venue'),
        description=data.get('description', 'Spacious luxury hall for all special occasions.'),
        city=data.get('city', 'Hyderabad'),
        area=data.get('area', 'Main City'),
        full_address=data.get('full_address', ''),
        min_capacity=int(data.get('min_capacity', 100)),
        max_capacity=int(data.get('max_capacity', 800)),
        base_rent_price=float(data.get('base_rent_price', 75000.0)),
        advance_payment_percentage=float(data.get('advance_payment_percentage', 25.0)),
        facilities=data.get('facilities', 'Central AC, Parking, Bridal Room, Generator Backup'),
        supported_event_types=data.get('supported_event_types', 'wedding,reception,birthday,engagement'),
        is_approved=True,
        is_active=True
    )
    db.session.add(hall)
    db.session.flush()

    # Add images if provided
    images = data.get('images', [])
    if not images:
        images = ["https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1200&q=80"]

    for order, img_url in enumerate(images):
        h_img = HallImage(
            hall_id=hall.id,
            image_url=img_url,
            is_primary=(order == 0),
            display_order=order
        )
        db.session.add(h_img)

    db.session.commit()
    return jsonify({'message': 'Function hall added successfully!', 'hall': hall.to_dict()}), 201

@owner_bp.route('/halls/<int:hall_id>', methods=['PUT'])
@jwt_required()
def edit_hall(hall_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    hall = FunctionHall.query.get(hall_id)
    if not hall or hall.owner_id != user.owner_profile.id:
        return jsonify({'error': 'Hall not found or unauthorized'}), 403

    data = request.get_json() or {}
    if 'name' in data: hall.name = data['name']
    if 'tagline' in data: hall.tagline = data['tagline']
    if 'description' in data: hall.description = data['description']
    if 'city' in data: hall.city = data['city']
    if 'area' in data: hall.area = data['area']
    if 'full_address' in data: hall.full_address = data['full_address']
    if 'min_capacity' in data: hall.min_capacity = int(data['min_capacity'])
    if 'max_capacity' in data: hall.max_capacity = int(data['max_capacity'])
    if 'base_rent_price' in data: hall.base_rent_price = float(data['base_rent_price'])
    if 'advance_payment_percentage' in data: hall.advance_payment_percentage = float(data['advance_payment_percentage'])
    if 'facilities' in data: hall.facilities = data['facilities']
    if 'supported_event_types' in data: hall.supported_event_types = data['supported_event_types']

    db.session.commit()
    return jsonify({'message': 'Hall details updated successfully', 'hall': hall.to_dict()})

@owner_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_owner_bookings():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'owner' or not user.owner_profile:
        return jsonify({'error': 'Unauthorized'}), 403

    hall_ids = [h.id for h in user.owner_profile.halls]
    status = request.args.get('status')

    query = Booking.query.filter(Booking.hall_id.in_(hall_ids))
    if status:
        query = query.filter_by(status=status)

    bookings = query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])

@owner_bp.route('/bookings/<int:booking_id>/action', methods=['POST'])
@jwt_required()
def action_booking(booking_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    booking = Booking.query.get(booking_id)

    if not booking or booking.hall.owner_id != user.owner_profile.id:
        return jsonify({'error': 'Booking not found or unauthorized'}), 403

    data = request.get_json() or {}
    action = data.get('action') # 'approve' or 'reject'
    reason = data.get('reason', '')

    if action == 'approve':
        booking.status = 'Awaiting Payment'
        booking.approval_timestamp = datetime.utcnow()
        booking.payment_hold_expiry = datetime.utcnow() + timedelta(hours=24) # 24hr hold

        notif = Notification(
            user_id=booking.customer_id,
            title="Booking Request Approved! 🎉",
            message=f"Hall owner approved your booking for {booking.hall.name} on {booking.event_date}. Please complete the advance payment of ₹{booking.advance_required:,.2f} within 24 hours.",
            link=f"/dashboard/bookings/{booking.id}"
        )
        db.session.add(notif)
        db.session.commit()
        return jsonify({'message': 'Booking request approved and set to Awaiting Payment', 'booking': booking.to_dict()})

    elif action == 'reject':
        booking.status = 'Rejected'
        booking.cancellation_reason = reason or "Declined by hall owner due to schedule conflict."

        notif = Notification(
            user_id=booking.customer_id,
            title="Booking Request Declined",
            message=f"Your booking for {booking.hall.name} was declined: {booking.cancellation_reason}",
            link=f"/dashboard/bookings/{booking.id}"
        )
        db.session.add(notif)
        db.session.commit()
        return jsonify({'message': 'Booking request declined', 'booking': booking.to_dict()})

    return jsonify({'error': 'Invalid action. Specify approve or reject.'}), 400

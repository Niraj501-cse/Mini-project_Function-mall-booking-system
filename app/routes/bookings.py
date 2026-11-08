from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Booking, FunctionHall, BookingPackage, User, Notification
from app import db
from datetime import datetime, timedelta
import random

bookings_bp = Blueprint('bookings', __name__)

def generate_booking_code():
    year = datetime.utcnow().year
    rand = random.randint(1000, 9999)
    return f"FM-{year}-{rand}"

@bookings_bp.route('/', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    hall_id = data.get('hall_id')
    package_id = data.get('package_id')
    event_date_str = data.get('event_date')
    event_slot = data.get('event_slot', 'Full Day')
    expected_guests = data.get('expected_guests', 200)
    event_type = data.get('event_type', 'Wedding / Marriage')
    food_choice = data.get('food_choice', 'Both Veg and Non-Veg')
    notes = data.get('notes', '')

    if not hall_id or not event_date_str:
        return jsonify({'error': 'Hall ID and Event Date are required'}), 400

    try:
        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

    hall = FunctionHall.query.get(hall_id)
    if not hall:
        return jsonify({'error': 'Hall not found'}), 404

    # Backend Validation: Prevent double booking
    existing = Booking.query.filter(
        Booking.hall_id == hall_id,
        Booking.event_date == event_date,
        Booking.status.in_(['Confirmed', 'Awaiting Payment'])
    ).first()
    if existing:
        return jsonify({'error': f"This venue is already reserved on {event_date_str}. Please select another date."}), 409

    # Financial calculations
    hall_rent = hall.base_rent_price
    package_cost = 0.0
    catering_cost = 0.0

    if package_id:
        pkg = BookingPackage.query.get(package_id)
        if pkg:
            package_cost = pkg.base_price
            plate_price = pkg.price_per_plate_veg if food_choice == 'Pure Veg' else pkg.price_per_plate_nonveg
            catering_cost = plate_price * expected_guests

    subtotal = hall_rent + package_cost + catering_cost
    tax_amount = round(subtotal * 0.18, 2)
    total_amount = round(subtotal + tax_amount, 2)
    advance_pct = hall.advance_payment_percentage or 25.0
    advance_required = round(total_amount * (advance_pct / 100.0), 2)

    code = generate_booking_code()
    while Booking.query.filter_by(booking_code=code).first():
        code = generate_booking_code()

    booking = Booking(
        booking_code=code,
        customer_id=user.id,
        hall_id=hall.id,
        package_id=package_id,
        event_date=event_date,
        event_slot=event_slot,
        expected_guests=expected_guests,
        event_type=event_type,
        hall_rent=hall_rent,
        package_cost=package_cost,
        catering_cost=catering_cost,
        tax_amount=tax_amount,
        total_amount=total_amount,
        advance_required=advance_required,
        advance_paid=0.0,
        balance_amount=total_amount,
        status='Pending Approval',
        food_choice=food_choice,
        notes=notes
    )

    db.session.add(booking)
    db.session.flush()

    # Create notification for customer
    notif = Notification(
        user_id=user.id,
        title="Booking Request Submitted",
        message=f"Your booking request for {hall.name} on {event_date_str} has been received and is pending owner approval.",
        link=f"/dashboard/bookings/{booking.id}"
    )
    db.session.add(notif)

    # Notify hall owner
    if hall.owner and hall.owner.user_id:
        owner_notif = Notification(
            user_id=hall.owner.user_id,
            title="New Booking Request Received",
            message=f"New booking request {booking.booking_code} for {hall.name} from {user.full_name}.",
            link="/owner/bookings"
        )
        db.session.add(owner_notif)

    db.session.commit()

    return jsonify({
        'message': 'Booking request submitted successfully! Awaiting hall owner approval.',
        'booking': booking.to_dict()
    }), 201

@bookings_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(customer_id=user_id).order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])

@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking_details(booking_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    # Permission check: customer, hall owner, or admin
    is_owner = (booking.hall.owner and booking.hall.owner.user_id == user_id)
    if booking.customer_id != user_id and not is_owner and user.role != 'admin':
        return jsonify({'error': 'Unauthorized to view this booking'}), 403

    return jsonify(booking.to_dict())

@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get(booking_id)
    if not booking or booking.customer_id != user_id:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.status in ['Completed', 'Cancelled']:
        return jsonify({'error': f"Cannot cancel booking with status '{booking.status}'"}), 400

    data = request.get_json() or {}
    reason = data.get('reason', 'Customer requested cancellation')

    booking.status = 'Cancelled'
    booking.cancellation_reason = reason
    db.session.commit()

    return jsonify({'message': 'Booking has been cancelled', 'booking': booking.to_dict()})

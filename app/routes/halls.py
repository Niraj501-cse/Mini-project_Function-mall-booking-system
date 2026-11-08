from flask import Blueprint, request, jsonify
from app.models import FunctionHall, Availability, Review, Booking
from app import db
from datetime import datetime

halls_bp = Blueprint('halls', __name__)

@halls_bp.route('/', methods=['GET'])
def get_halls():
    query = FunctionHall.query.filter_by(is_approved=True, is_active=True)

    city = request.args.get('city')
    if city:
        query = query.filter(FunctionHall.city.ilike(f'%{city}%'))

    event_type = request.args.get('event_type')
    if event_type:
        query = query.filter(FunctionHall.supported_event_types.ilike(f'%{event_type}%'))

    min_guests = request.args.get('min_guests', type=int)
    if min_guests:
        query = query.filter(FunctionHall.max_capacity >= min_guests)

    min_price = request.args.get('min_price', type=float)
    if min_price:
        query = query.filter(FunctionHall.base_rent_price >= min_price)

    max_price = request.args.get('max_price', type=float)
    if max_price:
        query = query.filter(FunctionHall.base_rent_price <= max_price)

    facility = request.args.get('facility')
    if facility:
        query = query.filter(FunctionHall.facilities.ilike(f'%{facility}%'))

    # Sort
    sort_by = request.args.get('sort', 'popular')
    if sort_by == 'price_low':
        query = query.order_by(FunctionHall.base_rent_price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(FunctionHall.base_rent_price.desc())
    elif sort_by == 'rating':
        query = query.order_by(FunctionHall.rating.desc())
    elif sort_by == 'capacity':
        query = query.order_by(FunctionHall.max_capacity.desc())
    else:
        query = query.order_by(FunctionHall.is_featured.desc(), FunctionHall.rating.desc())

    halls = query.all()
    return jsonify([h.to_dict() for h in halls])

@halls_bp.route('/<int:hall_id>', methods=['GET'])
def get_hall_details(hall_id):
    hall = FunctionHall.query.get(hall_id)
    if not hall or not hall.is_active or not hall.is_approved:
        return jsonify({'error': 'Hall not found'}), 404

    data = hall.to_dict()
    # Add approved reviews
    reviews = Review.query.filter_by(hall_id=hall.id, is_approved=True).order_by(Review.created_at.desc()).all()
    data['reviews_list'] = [r.to_dict() for r in reviews]
    return jsonify(data)

@halls_bp.route('/<int:hall_id>/check-availability', methods=['GET'])
def check_hall_availability(hall_id):
    date_str = request.args.get('date')
    slot = request.args.get('slot', 'Full Day')

    if not date_str:
        return jsonify({'error': 'Date is required'}), 400

    try:
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

    # Check confirmed or held bookings
    booked = Booking.query.filter(
        Booking.hall_id == hall_id,
        Booking.event_date == check_date,
        Booking.status.in_(['Confirmed', 'Awaiting Payment'])
    ).first()

    is_available = (booked is None)

    return jsonify({
        'hall_id': hall_id,
        'date': date_str,
        'slot': slot,
        'is_available': is_available,
        'message': 'Date is available for booking' if is_available else 'This date is currently reserved or awaiting payment completion.'
    })

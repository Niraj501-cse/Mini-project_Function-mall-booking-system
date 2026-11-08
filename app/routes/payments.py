from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Booking, Payment, User, Notification
from app import db
from datetime import datetime
import uuid

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_payment_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    payment_type = data.get('payment_type', 'Advance') # 'Advance' or 'Remaining'

    booking = Booking.query.get(booking_id)
    if not booking or booking.customer_id != user_id:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.status not in ['Approved', 'Awaiting Payment', 'Confirmed']:
        return jsonify({'error': f"Payment not permitted for booking status: {booking.status}"}), 400

    # Determine amount
    if payment_type == 'Advance':
        amount = booking.advance_required
    else:
        amount = booking.balance_amount

    if amount <= 0:
        return jsonify({'error': 'No balance payment pending for this booking'}), 400

    # Simulate Razorpay Order ID for test mode
    mock_order_id = f"order_FM_test_{uuid.uuid4().hex[:12]}"

    return jsonify({
        'order_id': mock_order_id,
        'amount': amount,
        'currency': 'INR',
        'key_id': 'rzp_test_MallMockDemo2025',
        'booking_code': booking.booking_code,
        'hall_name': booking.hall.name,
        'is_test_mode': True
    })

@payments_bp.route('/verify-payment', methods=['POST'])
@jwt_required()
def verify_payment():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    booking_id = data.get('booking_id')
    order_id = data.get('order_id')
    payment_id = data.get('payment_id') or f"pay_FM_test_{uuid.uuid4().hex[:12]}"
    payment_type = data.get('payment_type', 'Advance')
    payment_method = data.get('payment_method', 'Razorpay Test Mode (UPI / Cards)')

    booking = Booking.query.get(booking_id)
    if not booking or booking.customer_id != user_id:
        return jsonify({'error': 'Booking not found'}), 404

    # Calculate payable amount
    if payment_type == 'Advance':
        amount = booking.advance_required
        booking.advance_paid += amount
        booking.balance_amount = max(0.0, booking.total_amount - booking.advance_paid)
        booking.status = 'Confirmed'
    else:
        amount = booking.balance_amount
        booking.advance_paid += amount
        booking.balance_amount = 0.0

    payment = Payment(
        transaction_id=payment_id,
        booking_id=booking.id,
        user_id=user_id,
        amount=amount,
        payment_type=payment_type,
        payment_method=payment_method,
        gateway_order_id=order_id,
        gateway_payment_id=payment_id,
        status='Success',
        is_test_mode=True,
        receipt_url=f"/api/payments/receipt/{payment_id}"
    )
    db.session.add(payment)

    # Customer notification
    notif = Notification(
        user_id=user_id,
        title="Payment Successful & Booking Confirmed! 🎉",
        message=f"Advance payment of ₹{amount:,.2f} verified for booking {booking.booking_code}. Your venue is officially confirmed!",
        link=f"/dashboard/bookings/{booking.id}"
    )
    db.session.add(notif)

    # Hall Owner notification
    if booking.hall.owner and booking.hall.owner.user_id:
        owner_notif = Notification(
            user_id=booking.hall.owner.user_id,
            title="Advance Payment Received",
            message=f"Customer paid ₹{amount:,.2f} for booking {booking.booking_code} at {booking.hall.name}.",
            link="/owner/bookings"
        )
        db.session.add(owner_notif)

    db.session.commit()

    return jsonify({
        'message': 'Payment successfully verified and booking confirmed!',
        'payment': payment.to_dict(),
        'booking': booking.to_dict()
    }), 200

@payments_bp.route('/history', methods=['GET'])
@jwt_required()
def payment_history():
    user_id = int(get_jwt_identity())
    payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
    return jsonify([p.to_dict() for p in payments])

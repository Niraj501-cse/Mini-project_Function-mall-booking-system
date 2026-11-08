from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import ContactMessage, Review, Notification, User, FunctionHall
from app import db

common_bp = Blueprint('common', __name__)

@common_bp.route('/contact', methods=['POST'])
def submit_contact():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not full_name or not email or not message:
        return jsonify({'error': 'Name, email and message are required.'}), 400

    msg = ContactMessage(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject or 'General Inquiry',
        message=message
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'message': 'Thank you! Your enquiry has been received. Our team will contact you shortly.'}), 201

@common_bp.route('/reviews', methods=['POST'])
@jwt_required()
def submit_review():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    hall_id = data.get('hall_id')
    rating = int(data.get('rating', 5))
    title = data.get('title', '')
    comment = data.get('comment', '').strip()

    if not hall_id or not comment:
        return jsonify({'error': 'Hall ID and comment are required'}), 400

    review = Review(
        user_id=user_id,
        hall_id=hall_id,
        rating=max(1, min(5, rating)),
        title=title,
        comment=comment,
        is_approved=True
    )
    db.session.add(review)

    # Update hall average rating
    hall = FunctionHall.query.get(hall_id)
    if hall:
        existing_revs = Review.query.filter_by(hall_id=hall_id, is_approved=True).all()
        ratings = [r.rating for r in existing_revs] + [rating]
        hall.rating = round(sum(ratings) / len(ratings), 1)
        hall.review_count = len(ratings)

    db.session.commit()
    return jsonify({'message': 'Review submitted successfully!', 'review': review.to_dict()}), 201

@common_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(20).all()
    return jsonify([n.to_dict() for n in notifs])

@common_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@jwt_required()
def mark_read(notif_id):
    user_id = int(get_jwt_identity())
    n = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if n:
        n.is_read = True
        db.session.commit()
    return jsonify({'message': 'Marked read'})

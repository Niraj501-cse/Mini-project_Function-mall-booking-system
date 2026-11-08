from flask import Blueprint, request, jsonify
from app.models import BookingPackage, EventCategory
from app import db

packages_bp = Blueprint('packages', __name__)

@packages_bp.route('/', methods=['GET'])
def get_packages():
    category_slug = request.args.get('category')
    query = BookingPackage.query.filter_by(is_active=True)

    if category_slug:
        cat = EventCategory.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    tier = request.args.get('tier')
    if tier:
        query = query.filter(BookingPackage.tier.ilike(f'%{tier}%'))

    packages = query.all()
    return jsonify([p.to_dict() for p in packages])

@packages_bp.route('/<int:package_id>', methods=['GET'])
def get_package(package_id):
    pkg = BookingPackage.query.get(package_id)
    if not pkg or not pkg.is_active:
        return jsonify({'error': 'Package not found'}), 404
    return jsonify(pkg.to_dict())

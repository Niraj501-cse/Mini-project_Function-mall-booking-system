from flask import Blueprint, request, jsonify
from app.models import EventCategory
from app import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    categories = EventCategory.query.filter_by(is_active=True).order_by(EventCategory.display_order).all()
    return jsonify([cat.to_dict() for cat in categories])

@categories_bp.route('/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    category = EventCategory.query.filter_by(slug=slug, is_active=True).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    return jsonify(category.to_dict(include_packages=True))

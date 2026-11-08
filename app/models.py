from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer') # 'customer', 'owner', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    customer_profile = db.relationship('CustomerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    owner_profile = db.relationship('OwnerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='customer', foreign_keys='Booking.customer_id', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan')
    favourites = db.relationship('Favourite', backref='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    preferred_event_type = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'preferred_event_type': self.preferred_event_type
        }

class OwnerProfile(db.Model):
    __tablename__ = 'owner_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    business_name = db.Column(db.String(150), nullable=False)
    business_registration_no = db.Column(db.String(100), nullable=True)
    bank_account_no = db.Column(db.String(50), nullable=True)
    ifsc_code = db.Column(db.String(30), nullable=True)
    is_verified = db.Column(db.Boolean, default=True)

    # Relationships
    halls = db.relationship('FunctionHall', backref='owner', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'business_registration_no': self.business_registration_no,
            'is_verified': self.is_verified,
            'halls_count': len(self.halls) if self.halls else 0
        }

class EventCategory(db.Model):
    __tablename__ = 'event_categories'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.String(200), nullable=True)
    icon_name = db.Column(db.String(50), default='Sparkles')
    cover_image = db.Column(db.String(500), nullable=False)
    gallery_image_1 = db.Column(db.String(500), nullable=False)
    gallery_image_2 = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)

    # Relationships
    packages = db.relationship('BookingPackage', backref='category', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_packages=False):
        data = {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'tagline': self.tagline,
            'icon_name': self.icon_name,
            'cover_image': self.cover_image,
            'gallery_image_1': self.gallery_image_1,
            'gallery_image_2': self.gallery_image_2,
            'gallery': [self.cover_image, self.gallery_image_1, self.gallery_image_2],
            'is_active': self.is_active,
            'display_order': self.display_order,
            'packages_count': len(self.packages)
        }
        if include_packages:
            data['packages'] = [pkg.to_dict() for pkg in self.packages if pkg.is_active]
        return data

class FunctionHall(db.Model):
    __tablename__ = 'function_halls'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner_profiles.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.String(250), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    full_address = db.Column(db.Text, nullable=False)
    map_location_url = db.Column(db.String(500), nullable=True)
    
    # Capacity & Pricing
    min_capacity = db.Column(db.Integer, default=50)
    max_capacity = db.Column(db.Integer, default=1000)
    base_rent_price = db.Column(db.Float, default=50000.0) # Base hall rent per slot
    advance_payment_percentage = db.Column(db.Float, default=25.0) # e.g. 25% advance
    
    # Facilities / Amenities (stored as JSON/comma string)
    facilities = db.Column(db.Text, nullable=False) # e.g. "AC, Valet Parking, Bridal Room, Power Backup, DJ Stage, Dining Hall"
    supported_event_types = db.Column(db.Text, nullable=False) # e.g. "wedding,reception,birthday,engagement"
    
    # Rating & Stats
    rating = db.Column(db.Float, default=4.8)
    review_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True) # Admin approval
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    images = db.relationship('HallImage', backref='hall', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='hall', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='hall', cascade='all, delete-orphan')
    availabilities = db.relationship('Availability', backref='hall', cascade='all, delete-orphan')

    def to_dict(self):
        image_urls = [img.image_url for img in self.images] if self.images else [
            "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1200&q=80"
        ]
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'tagline': self.tagline,
            'city': self.city,
            'area': self.area,
            'full_address': self.full_address,
            'map_location_url': self.map_location_url,
            'min_capacity': self.min_capacity,
            'max_capacity': self.max_capacity,
            'base_rent_price': self.base_rent_price,
            'advance_payment_percentage': self.advance_payment_percentage,
            'facilities': [f.strip() for f in self.facilities.split(',') if f.strip()],
            'supported_event_types': [t.strip() for t in self.supported_event_types.split(',') if t.strip()],
            'rating': self.rating,
            'review_count': self.review_count,
            'is_featured': self.is_featured,
            'is_approved': self.is_approved,
            'is_active': self.is_active,
            'images': image_urls,
            'cover_image': image_urls[0] if image_urls else None,
            'owner_business': self.owner.business_name if self.owner else None
        }

class HallImage(db.Model):
    __tablename__ = 'hall_images'

    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey('function_halls.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(150), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

class BookingPackage(db.Model):
    __tablename__ = 'booking_packages'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('event_categories.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    tier = db.Column(db.String(50), default='Standard') # Standard, Premium, Luxury, Royal, Budget, etc.
    description = db.Column(db.Text, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    guest_capacity = db.Column(db.Integer, default=250)
    price_per_plate_veg = db.Column(db.Float, default=450.0)
    price_per_plate_nonveg = db.Column(db.Float, default=650.0)
    food_menu_summary = db.Column(db.Text, nullable=True)
    decoration_details = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    is_popular = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    features = db.relationship('PackageFeature', backref='package', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'category_slug': self.category.slug if self.category else None,
            'name': self.name,
            'tier': self.tier,
            'description': self.description,
            'base_price': self.base_price,
            'guest_capacity': self.guest_capacity,
            'price_per_plate_veg': self.price_per_plate_veg,
            'price_per_plate_nonveg': self.price_per_plate_nonveg,
            'food_menu_summary': self.food_menu_summary,
            'decoration_details': self.decoration_details,
            'image_url': self.image_url,
            'is_popular': self.is_popular,
            'is_active': self.is_active,
            'features': [f.feature_text for f in self.features]
        }

class PackageFeature(db.Model):
    __tablename__ = 'package_features'

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('booking_packages.id', ondelete='CASCADE'), nullable=False)
    feature_text = db.Column(db.String(255), nullable=False)

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(30), unique=True, nullable=False, index=True) # e.g. FM-2025-0812
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey('function_halls.id', ondelete='CASCADE'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('booking_packages.id', ondelete='SET NULL'), nullable=True)
    
    # Event dates & slot
    event_date = db.Column(db.Date, nullable=False, index=True)
    event_slot = db.Column(db.String(50), default='Full Day') # 'Morning (8AM - 3PM)', 'Evening (5PM - 11PM)', 'Full Day'
    expected_guests = db.Column(db.Integer, nullable=False, default=200)
    event_type = db.Column(db.String(100), nullable=False) # category name e.g. Wedding
    
    # Financial breakdown
    hall_rent = db.Column(db.Float, default=0.0)
    package_cost = db.Column(db.Float, default=0.0)
    catering_cost = db.Column(db.Float, default=0.0)
    decoration_addon = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    advance_required = db.Column(db.Float, nullable=False)
    advance_paid = db.Column(db.Float, default=0.0)
    balance_amount = db.Column(db.Float, default=0.0)
    
    # Statuses
    # Status flow: 'Pending Approval' -> 'Approved' (or 'Rejected') -> 'Awaiting Payment' -> 'Confirmed' -> 'Completed' (or 'Cancelled')
    status = db.Column(db.String(50), default='Pending Approval', index=True)
    approval_timestamp = db.Column(db.DateTime, nullable=True)
    payment_hold_expiry = db.Column(db.DateTime, nullable=True) # Temporary hold expiry (e.g., 24 hours after approval)
    cancellation_reason = db.Column(db.Text, nullable=True)
    
    # Special instructions & requirements
    notes = db.Column(db.Text, nullable=True)
    food_choice = db.Column(db.String(50), default='Both Veg and Non-Veg') # 'Pure Veg', 'Non-Veg', 'Both'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    package = db.relationship('BookingPackage', backref='bookings')
    payments = db.relationship('Payment', backref='booking', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'booking_code': self.booking_code,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else 'Guest',
            'customer_email': self.customer.email if self.customer else None,
            'customer_phone': self.customer.phone if self.customer else None,
            'hall_id': self.hall_id,
            'hall_name': self.hall.name if self.hall else 'Unknown Hall',
            'hall_city': self.hall.city if self.hall else None,
            'hall_cover': self.hall.images[0].image_url if self.hall and self.hall.images else None,
            'package_id': self.package_id,
            'package_name': self.package.name if self.package else 'Custom Package',
            'package_tier': self.package.tier if self.package else None,
            'event_date': self.event_date.strftime('%Y-%m-%d') if self.event_date else None,
            'event_slot': self.event_slot,
            'expected_guests': self.expected_guests,
            'event_type': self.event_type,
            'hall_rent': self.hall_rent,
            'package_cost': self.package_cost,
            'catering_cost': self.catering_cost,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'advance_required': self.advance_required,
            'advance_paid': self.advance_paid,
            'balance_amount': self.balance_amount,
            'status': self.status,
            'approval_timestamp': self.approval_timestamp.isoformat() if self.approval_timestamp else None,
            'payment_hold_expiry': self.payment_hold_expiry.isoformat() if self.payment_hold_expiry else None,
            'cancellation_reason': self.cancellation_reason,
            'notes': self.notes,
            'food_choice': self.food_choice,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'payments': [p.to_dict() for p in self.payments]
        }

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True) # e.g. pay_FM_test_123456
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50), default='Advance') # 'Advance', 'Remaining', 'Full', 'Security'
    payment_method = db.Column(db.String(50), default='Razorpay Test Mode (UPI/Card)')
    gateway_order_id = db.Column(db.String(100), nullable=True)
    gateway_payment_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), default='Success') # 'Success', 'Pending', 'Failed', 'Refunded'
    is_test_mode = db.Column(db.Boolean, default=True)
    receipt_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'booking_id': self.booking_id,
            'booking_code': self.booking.booking_code if self.booking else None,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'payment_method': self.payment_method,
            'gateway_order_id': self.gateway_order_id,
            'gateway_payment_id': self.gateway_payment_id,
            'status': self.status,
            'is_test_mode': self.is_test_mode,
            'receipt_url': self.receipt_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Availability(db.Model):
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey('function_halls.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    slot = db.Column(db.String(50), default='Full Day') # 'Morning', 'Evening', 'Full Day'
    status = db.Column(db.String(50), default='Booked') # 'Booked', 'Blocked', 'Maintenance'
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='SET NULL'), nullable=True)

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey('function_halls.id', ondelete='CASCADE'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='SET NULL'), nullable=True)
    rating = db.Column(db.Integer, nullable=False, default=5) # 1 - 5
    title = db.Column(db.String(150), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Verified Guest',
            'hall_id': self.hall_id,
            'hall_name': self.hall.name if self.hall else None,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%b %d, %Y') if self.created_at else None
        }

class Favourite(db.Model):
    __tablename__ = 'favourites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey('function_halls.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    hall = db.relationship('FunctionHall')

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }

class WebsiteSetting(db.Model):
    __tablename__ = 'website_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    @classmethod
    def get_val(cls, key, default=''):
        item = cls.query.filter_by(key=key).first()
        return item.value if item else default

from datetime import datetime, timezone
from pathlib import Path
from flask import has_request_context, url_for, current_app
from app.extensions import db


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False, index=True)
    condition = db.Column(db.String(30), default='Good', nullable=False)  # New, Like New, Good, Fair, Poor
    listing_type = db.Column(db.String(20), default='borrow', nullable=False, index=True)  # borrow, sell, both

    # Sale specific attributes
    selling_price = db.Column(db.Float, nullable=True)
    negotiable = db.Column(db.Boolean, default=False, nullable=False)
    sale_status = db.Column(db.String(20), default='available', nullable=False, index=True)  # available, reserved, sold

    # Borrow specific attributes
    borrowing_fee = db.Column(db.Float, default=0.0, nullable=False)  # Daily fee
    deposit = db.Column(db.Float, default=0.0, nullable=False)
    borrowing_duration_max_days = db.Column(db.Integer, default=7, nullable=False)
    borrowing_rules = db.Column(db.Text, nullable=True)

    # General & Location
    location = db.Column(db.String(150), default='Main Campus', nullable=False)
    availability_status = db.Column(db.String(20), default='available', nullable=False, index=True)  # available, borrowed, reserved, unavailable
    tags = db.Column(db.String(255), nullable=True)
    views_count = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    owner = db.relationship('User', back_populates='items', foreign_keys=[owner_id])
    category = db.relationship('Category', back_populates='items')
    images = db.relationship('ItemImage', back_populates='item', cascade='all, delete-orphan', order_by='desc(ItemImage.is_primary)')
    availabilities = db.relationship('ItemAvailability', back_populates='item', cascade='all, delete-orphan')
    borrow_requests = db.relationship('BorrowRequest', back_populates='item', cascade='all, delete-orphan')
    borrow_transactions = db.relationship('BorrowTransaction', back_populates='item', cascade='all, delete-orphan')
    purchase_requests = db.relationship('PurchaseRequest', back_populates='item', cascade='all, delete-orphan')
    offers = db.relationship('Offer', back_populates='item', cascade='all, delete-orphan')
    sales = db.relationship('Sale', back_populates='item', cascade='all, delete-orphan')
    wishlists = db.relationship('Wishlist', back_populates='item', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='item')

    @property
    def primary_image_url(self) -> str:
        """Get the primary image URL or fallback placeholder."""
        if self.images:
            img = next((i for i in self.images if i.is_primary), self.images[0])
            if img:
                return img.image_url
        if has_request_context():
            return url_for('static', filename='images/item_placeholder.svg')
        return '/static/images/item_placeholder.svg'

    @property
    def has_image(self) -> bool:
        """Check if item has an actual valid image file on disk or valid URL."""
        if not self.images:
            return False
        img = next((i for i in self.images if i.is_primary), self.images[0])
        return img.exists_on_disk if img else False

    @property
    def is_available_for_borrow(self) -> bool:
        """Determine if item can currently be requested for borrowing."""
        return (
            self.listing_type in ('borrow', 'both') and
            self.availability_status == 'available' and
            self.sale_status != 'sold'
        )

    @property
    def is_available_for_sale(self) -> bool:
        """Determine if item can currently be purchased/offered."""
        return (
            self.listing_type in ('sell', 'both') and
            self.sale_status == 'available' and
            self.availability_status != 'borrowed'
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.name if self.category else None,
            'condition': self.condition,
            'listing_type': self.listing_type,
            'selling_price': self.selling_price,
            'negotiable': self.negotiable,
            'borrowing_fee': self.borrowing_fee,
            'deposit': self.deposit,
            'location': self.location,
            'availability_status': self.availability_status,
            'sale_status': self.sale_status,
            'primary_image_url': self.primary_image_url,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'owner_trust_score': self.owner.trust_score if self.owner else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<Item {self.id}: '{self.title}' ({self.listing_type})>"


class ItemImage(db.Model):
    __tablename__ = 'item_images'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = db.relationship('Item', back_populates='images')

    @property
    def relative_static_path(self) -> str:
        """Normalize stored image_path into a relative path inside app/static/."""
        if not self.image_path:
            return 'images/item_placeholder.svg'
        path = self.image_path.strip().replace('\\', '/')
        if path.startswith(('http://', 'https://')):
            return path
        if path.startswith('/static/'):
            path = path[len('/static/'):]
        elif path.startswith('static/'):
            path = path[len('static/'):]
        
        if not path.startswith('uploads/'):
            if path.startswith('items/'):
                path = f"uploads/{path}"
            elif path.startswith('images/'):
                pass
            else:
                path = f"uploads/items/{path}"
        return path

    @property
    def exists_on_disk(self) -> bool:
        """Check if image file physically exists in the static folder."""
        rel_path = self.relative_static_path
        if rel_path.startswith(('http://', 'https://')):
            return True
        try:
            from flask import current_app
            base_dir = Path(current_app.root_path) if current_app else Path(__file__).resolve().parent.parent
            disk_path = base_dir / 'static' / rel_path
            return disk_path.is_file()
        except Exception:
            return False

    @property
    def image_url(self) -> str:
        """Resolve the accessible static or external URL for this image."""
        rel_path = self.relative_static_path
        if rel_path.startswith(('http://', 'https://')):
            return rel_path
        
        # If not found on disk, gracefully return placeholder
        if not self.exists_on_disk:
            if has_request_context():
                return url_for('static', filename='images/item_placeholder.svg')
            return '/static/images/item_placeholder.svg'

        if has_request_context():
            return url_for('static', filename=rel_path)
        return f"/static/{rel_path}"

    def __repr__(self) -> str:
        return f"<ItemImage {self.image_path} (Primary: {self.is_primary})>"


class ItemAvailability(db.Model):
    """Tracks blocked periods, reservations, or maintenance on an item."""
    __tablename__ = 'item_availabilities'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    reason = db.Column(db.String(50), default='booking', nullable=False)  # booking, maintenance, owner_blocked
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    item = db.relationship('Item', back_populates='availabilities')

    def __repr__(self) -> str:
        return f"<ItemAvailability item={self.item_id} from {self.start_date} to {self.end_date}>"

from datetime import datetime, timezone
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    college_or_community = db.Column(db.String(120), default='Main Campus', nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    contact_preference = db.Column(db.String(20), default='in_app', nullable=False)  # in_app, email, phone
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default='user', nullable=False)  # user, admin
    trust_score = db.Column(db.Float, default=100.0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    items = db.relationship('Item', back_populates='owner', cascade='all, delete-orphan', foreign_keys='Item.owner_id')
    borrow_requests = db.relationship('BorrowRequest', back_populates='borrower', foreign_keys='BorrowRequest.borrower_id')
    borrow_transactions_borrower = db.relationship('BorrowTransaction', back_populates='borrower', foreign_keys='BorrowTransaction.borrower_id')
    borrow_transactions_lender = db.relationship('BorrowTransaction', back_populates='lender', foreign_keys='BorrowTransaction.lender_id')
    purchase_requests_buyer = db.relationship('PurchaseRequest', back_populates='buyer', foreign_keys='PurchaseRequest.buyer_id')
    purchase_requests_seller = db.relationship('PurchaseRequest', back_populates='seller', foreign_keys='PurchaseRequest.seller_id')
    offers_made = db.relationship('Offer', back_populates='buyer', foreign_keys='Offer.buyer_id')
    offers_received = db.relationship('Offer', back_populates='seller', foreign_keys='Offer.seller_id')
    sales_as_seller = db.relationship('Sale', back_populates='seller', foreign_keys='Sale.seller_id')
    sales_as_buyer = db.relationship('Sale', back_populates='buyer', foreign_keys='Sale.buyer_id')
    wishlists = db.relationship('Wishlist', back_populates='user', cascade='all, delete-orphan')
    reviews_given = db.relationship('Review', back_populates='reviewer', foreign_keys='Review.reviewer_id')
    reviews_received = db.relationship('Review', back_populates='target_user', foreign_keys='Review.target_user_id')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan', order_by='Notification.created_at.desc()')
    reports_submitted = db.relationship('Report', back_populates='reporter', foreign_keys='Report.reporter_id')

    def set_password(self, password: str) -> None:
        """Hash and store user password."""
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password: str) -> bool:
        """Verify given password against stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == 'admin'

    def get_reset_token(self, expires_sec: int = 1800) -> str:
        """Generate a secure timed password reset token."""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token: str, expires_sec: int = 1800):
        """Verify reset token and return User instance if valid."""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except (SignatureExpired, BadTimeSignature, Exception):
            return None
        return db.session.get(User, data.get('user_id'))

    @property
    def avatar_url(self) -> str:
        """Return path to profile image or default avatar."""
        if self.profile_image:
            return f"/static/uploads/profiles/{self.profile_image}"
        return "/static/images/default_avatar.svg"

    @property
    def unread_notifications_count(self) -> int:
        """Return count of unread notifications."""
        return sum(1 for n in self.notifications if not n.is_read)

    def to_dict(self) -> dict:
        """Safe user dictionary representation."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'college_or_community': self.college_or_community,
            'contact_preference': self.contact_preference,
            'role': self.role,
            'trust_score': round(self.trust_score, 1),
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<User {self.username} (Role: {self.role})>"

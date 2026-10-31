from datetime import datetime, timezone
from app.extensions import db


class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'item_id', name='uq_user_item_wishlist'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='wishlists')
    item = db.relationship('Item', back_populates='wishlists')

    def __repr__(self) -> str:
        return f"<Wishlist user={self.user_id} item={self.item_id}>"


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='SET NULL'), nullable=True)
    borrow_transaction_id = db.Column(db.Integer, db.ForeignKey('borrow_transactions.id', ondelete='SET NULL'), nullable=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id', ondelete='SET NULL'), nullable=True)

    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, nullable=False)
    review_type = db.Column(db.String(30), nullable=False)  # borrower_to_lender, lender_to_borrower, buyer_to_seller, seller_to_buyer
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    reviewer = db.relationship('User', back_populates='reviews_given', foreign_keys=[reviewer_id])
    target_user = db.relationship('User', back_populates='reviews_received', foreign_keys=[target_user_id])
    item = db.relationship('Item', back_populates='reviews')
    borrow_transaction = db.relationship('BorrowTransaction', back_populates='reviews')
    sale = db.relationship('Sale', back_populates='reviews')

    def __repr__(self) -> str:
        return f"<Review #{self.id}: rating={self.rating} from={self.reviewer_id} to={self.target_user_id}>"


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    notification_type = db.Column(db.String(50), default='info', nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = db.relationship('User', back_populates='notifications')

    def __repr__(self) -> str:
        return f"<Notification #{self.id} for user={self.user_id} (read={self.is_read})>"


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reported_item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='SET NULL'), nullable=True)
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, reviewed, dismissed, action_taken
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    reporter = db.relationship('User', back_populates='reports_submitted', foreign_keys=[reporter_id])

    def __repr__(self) -> str:
        return f"<Report #{self.id} status={self.status}>"

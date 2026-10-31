from datetime import datetime, timezone
from app.extensions import db


class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    proposed_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, accepted, rejected, cancelled, completed
    message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    item = db.relationship('Item', back_populates='purchase_requests')
    buyer = db.relationship('User', back_populates='purchase_requests_buyer', foreign_keys=[buyer_id])
    seller = db.relationship('User', back_populates='purchase_requests_seller', foreign_keys=[seller_id])
    sale = db.relationship('Sale', back_populates='purchase_request', uselist=False)

    def __repr__(self) -> str:
        return f"<PurchaseRequest #{self.id}: item={self.item_id} buyer={self.buyer_id} ({self.status})>"


class Offer(db.Model):
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    offer_amount = db.Column(db.Float, nullable=False)
    counter_amount = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, accepted, rejected, countered, cancelled
    message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    item = db.relationship('Item', back_populates='offers')
    buyer = db.relationship('User', back_populates='offers_made', foreign_keys=[buyer_id])
    seller = db.relationship('User', back_populates='offers_received', foreign_keys=[seller_id])

    def __repr__(self) -> str:
        return f"<Offer #{self.id}: item={self.item_id} amount={self.offer_amount} ({self.status})>"


class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id', ondelete='SET NULL'), nullable=True)

    agreed_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='reserved', nullable=False, index=True)  # reserved, completed, cancelled
    notes = db.Column(db.Text, nullable=True)

    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    item = db.relationship('Item', back_populates='sales')
    buyer = db.relationship('User', back_populates='sales_as_buyer', foreign_keys=[buyer_id])
    seller = db.relationship('User', back_populates='sales_as_seller', foreign_keys=[seller_id])
    purchase_request = db.relationship('PurchaseRequest', back_populates='sale')
    reviews = db.relationship('Review', back_populates='sale')

    def __repr__(self) -> str:
        return f"<Sale #{self.id}: item={self.item_id} price={self.agreed_price} ({self.status})>"

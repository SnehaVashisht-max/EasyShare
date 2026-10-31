from datetime import datetime, timezone
from app.extensions import db


class BorrowRequest(db.Model):
    __tablename__ = 'borrow_requests'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_fee = db.Column(db.Float, default=0.0, nullable=False)
    deposit = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, accepted, rejected, cancelled
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    item = db.relationship('Item', back_populates='borrow_requests')
    borrower = db.relationship('User', back_populates='borrow_requests', foreign_keys=[borrower_id])
    transaction = db.relationship('BorrowTransaction', back_populates='borrow_request', uselist=False)

    @property
    def duration_days(self) -> int:
        if self.start_date and self.end_date:
            return max(1, (self.end_date - self.start_date).days + 1)
        return 1

    def __repr__(self) -> str:
        return f"<BorrowRequest #{self.id}: item={self.item_id} by user={self.borrower_id} ({self.status})>"


class BorrowTransaction(db.Model):
    __tablename__ = 'borrow_transactions'

    id = db.Column(db.Integer, primary_key=True)
    borrow_request_id = db.Column(db.Integer, db.ForeignKey('borrow_requests.id', ondelete='SET NULL'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False, index=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    actual_return_date = db.Column(db.Date, nullable=True)

    # Statuses: accepted -> active (handover complete) -> return_pending -> completed -> overdue -> cancelled
    status = db.Column(db.String(20), default='accepted', nullable=False, index=True)
    handover_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    borrow_request = db.relationship('BorrowRequest', back_populates='transaction')
    item = db.relationship('Item', back_populates='borrow_transactions')
    borrower = db.relationship('User', back_populates='borrow_transactions_borrower', foreign_keys=[borrower_id])
    lender = db.relationship('User', back_populates='borrow_transactions_lender', foreign_keys=[lender_id])
    qr_verifications = db.relationship('QRVerification', back_populates='borrow_transaction', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='borrow_transaction')

    @property
    def is_overdue(self) -> bool:
        if self.status in ('active', 'return_pending') and self.end_date:
            return datetime.now(timezone.utc).date() > self.end_date
        return False

    def __repr__(self) -> str:
        return f"<BorrowTransaction #{self.id}: item={self.item_id} borrower={self.borrower_id} ({self.status})>"

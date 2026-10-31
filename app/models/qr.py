from datetime import datetime, timezone
from app.extensions import db


class QRVerification(db.Model):
    __tablename__ = 'qr_verifications'

    id = db.Column(db.Integer, primary_key=True)
    borrow_transaction_id = db.Column(db.Integer, db.ForeignKey('borrow_transactions.id', ondelete='CASCADE'), nullable=False, index=True)
    action_type = db.Column(db.String(20), nullable=False)  # 'handover' or 'return'
    token_hash = db.Column(db.String(256), nullable=False, index=True)
    is_used = db.Column(db.Boolean, default=False, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    borrow_transaction = db.relationship('BorrowTransaction', back_populates='qr_verifications')
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])

    @property
    def is_expired(self) -> bool:
        now_utc = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            return now_utc.replace(tzinfo=None) > self.expires_at
        return now_utc > self.expires_at

    def __repr__(self) -> str:
        return f"<QRVerification #{self.id} for tx={self.borrow_transaction_id} type={self.action_type} used={self.is_used}>"

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import desc

from app.extensions import db
from app.models.category import Category
from app.models.item import Item
from app.models.user import User
from app.models.interaction import Notification, Wishlist
from app.models.borrow import BorrowRequest, BorrowTransaction
from app.models.sale import PurchaseRequest, Offer, Sale

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    categories = Category.query.order_by(Category.name.asc()).all()
    recent_items = Item.query.order_by(Item.created_at.desc()).limit(8).all()
    user_count = User.query.count()
    item_count = Item.query.count()
    borrow_count = BorrowTransaction.query.count() + BorrowRequest.query.count()

    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = {w.item_id for w in current_user.wishlists}

    return render_template(
        'index.html',
        categories=categories,
        recent_items=recent_items,
        user_count=user_count,
        item_count=item_count,
        borrow_count=borrow_count,
        user_wishlist_ids=user_wishlist_ids
    )


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User Activity Dashboard."""
    my_items = Item.query.filter_by(owner_id=current_user.id).order_by(desc(Item.created_at)).all()
    my_borrow_requests = BorrowRequest.query.filter_by(borrower_id=current_user.id).order_by(desc(BorrowRequest.created_at)).all()
    incoming_borrow_requests = BorrowRequest.query.join(Item).filter(Item.owner_id == current_user.id).order_by(desc(BorrowRequest.created_at)).all()
    
    my_purchase_requests = PurchaseRequest.query.filter_by(buyer_id=current_user.id).order_by(desc(PurchaseRequest.created_at)).all()
    incoming_purchase_requests = PurchaseRequest.query.filter_by(seller_id=current_user.id).order_by(desc(PurchaseRequest.created_at)).all()
    
    my_offers = Offer.query.filter_by(buyer_id=current_user.id).order_by(desc(Offer.created_at)).all()
    incoming_offers = Offer.query.filter_by(seller_id=current_user.id).order_by(desc(Offer.created_at)).all()
    
    wishlist_items = [w.item for w in current_user.wishlists if w.item is not None]

    return render_template(
        'dashboard.html',
        my_items=my_items,
        my_borrow_requests=my_borrow_requests,
        incoming_borrow_requests=incoming_borrow_requests,
        my_purchase_requests=my_purchase_requests,
        incoming_purchase_requests=incoming_purchase_requests,
        my_offers=my_offers,
        incoming_offers=incoming_offers,
        wishlist_items=wishlist_items,
        title=f"{current_user.full_name}'s Dashboard"
    )


@main_bp.route('/notifications')
@login_required
def notifications():
    """View all in-app notifications."""
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(desc(Notification.created_at)).all()
    return render_template(
        'notifications.html',
        notifications=user_notifications,
        title="My Notifications"
    )


@main_bp.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notice = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notice.is_read = True
    db.session.commit()
    if notice.link:
        return redirect(notice.link)
    return redirect(url_for('main.notifications'))


@main_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash("All notifications marked as read.", "info")
    return redirect(url_for('main.notifications'))


@main_bp.route('/about')
def about():
    return render_template('about.html')

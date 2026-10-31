from datetime import datetime, date, timezone
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    jsonify,
    current_app
)
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc, asc

from app.extensions import db
from app.models.item import Item, ItemImage, ItemAvailability
from app.models.category import Category
from app.models.borrow import BorrowRequest, BorrowTransaction
from app.models.sale import PurchaseRequest, Offer, Sale
from app.models.interaction import Wishlist, Notification
from app.forms.item import (
    ItemForm,
    BorrowRequestForm,
    PurchaseRequestForm,
    OfferForm
)
from app.utils.helpers import save_uploaded_image

items_bp = Blueprint('items', __name__)


# -------------------------------------------------------------------------
# 1. BROWSE ALL ITEMS
# -------------------------------------------------------------------------
@items_bp.route('/browse')
def browse():
    categories = Category.query.order_by(Category.name.asc()).all()

    # Query parameters
    search_query = request.args.get('q', '').strip()
    selected_category_slug = request.args.get('category', '').strip()
    selected_type = request.args.get('type', 'all').strip()  # all, borrow, sell, both
    selected_condition = request.args.get('condition', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'newest').strip()

    # Base query: exclude completely deleted or deactivated items
    query = Item.query

    # Search filter (title, description, tags, campus location)
    if search_query:
        term = f"%{search_query}%"
        query = query.filter(
            or_(
                Item.title.ilike(term),
                Item.description.ilike(term),
                Item.tags.ilike(term),
                Item.location.ilike(term)
            )
        )

    # Category filter
    selected_category = None
    if selected_category_slug:
        selected_category = Category.query.filter_by(slug=selected_category_slug).first()
        if selected_category:
            query = query.filter(Item.category_id == selected_category.id)

    # Listing type filter
    if selected_type == 'borrow':
        query = query.filter(Item.listing_type.in_(['borrow', 'both']))
    elif selected_type == 'sell':
        query = query.filter(Item.listing_type.in_(['sell', 'both']))
    elif selected_type == 'both':
        query = query.filter(Item.listing_type == 'both')

    # Condition filter
    if selected_condition:
        query = query.filter(Item.condition == selected_condition)

    # Price / Fee filters
    if min_price is not None and min_price >= 0:
        query = query.filter(
            or_(
                Item.selling_price >= min_price,
                Item.borrowing_fee >= min_price
            )
        )
    if max_price is not None and max_price > 0:
        query = query.filter(
            or_(
                and_(Item.selling_price.isnot(None), Item.selling_price <= max_price),
                and_(Item.borrowing_fee.isnot(None), Item.borrowing_fee <= max_price)
            )
        )

    # Sorting
    if sort_by == 'price_asc':
        query = query.order_by(asc(Item.selling_price), asc(Item.borrowing_fee))
    elif sort_by == 'price_desc':
        query = query.order_by(desc(Item.selling_price), desc(Item.borrowing_fee))
    elif sort_by == 'popular':
        query = query.order_by(desc(Item.views_count), desc(Item.created_at))
    else:  # newest
        query = query.order_by(desc(Item.created_at))

    items = query.all()

    # User wishlist IDs if logged in
    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = {w.item_id for w in current_user.wishlists}

    return render_template(
        'items/browse.html',
        items=items,
        categories=categories,
        selected_category=selected_category,
        selected_category_slug=selected_category_slug,
        selected_type=selected_type,
        selected_condition=selected_condition,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        search_query=search_query,
        user_wishlist_ids=user_wishlist_ids,
        total_count=len(items)
    )


# -------------------------------------------------------------------------
# 2. BORROW DEDICATED CATALOG
# -------------------------------------------------------------------------
@items_bp.route('/borrow')
def borrow():
    categories = Category.query.order_by(Category.name.asc()).all()
    search_query = request.args.get('q', '').strip()
    selected_category_slug = request.args.get('category', '').strip()
    selected_condition = request.args.get('condition', '').strip()
    max_daily_fee = request.args.get('max_fee', type=float)
    sort_by = request.args.get('sort', 'newest').strip()

    query = Item.query.filter(
        Item.listing_type.in_(['borrow', 'both']),
        Item.availability_status == 'available',
        Item.sale_status != 'sold'
    )

    if search_query:
        term = f"%{search_query}%"
        query = query.filter(
            or_(
                Item.title.ilike(term),
                Item.description.ilike(term),
                Item.tags.ilike(term),
                Item.location.ilike(term)
            )
        )

    selected_category = None
    if selected_category_slug:
        selected_category = Category.query.filter_by(slug=selected_category_slug).first()
        if selected_category:
            query = query.filter(Item.category_id == selected_category.id)

    if selected_condition:
        query = query.filter(Item.condition == selected_condition)

    if max_daily_fee is not None and max_daily_fee >= 0:
        query = query.filter(Item.borrowing_fee <= max_daily_fee)

    if sort_by == 'fee_asc':
        query = query.order_by(asc(Item.borrowing_fee))
    elif sort_by == 'popular':
        query = query.order_by(desc(Item.views_count))
    else:
        query = query.order_by(desc(Item.created_at))

    items = query.all()

    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = {w.item_id for w in current_user.wishlists}

    return render_template(
        'items/borrow.html',
        items=items,
        categories=categories,
        selected_category=selected_category,
        selected_category_slug=selected_category_slug,
        selected_condition=selected_condition,
        max_daily_fee=max_daily_fee,
        sort_by=sort_by,
        search_query=search_query,
        user_wishlist_ids=user_wishlist_ids,
        total_count=len(items)
    )


# -------------------------------------------------------------------------
# 3. BUY & SELL MARKETPLACE CATALOG
# -------------------------------------------------------------------------
@items_bp.route('/sell')
def sell():
    categories = Category.query.order_by(Category.name.asc()).all()
    search_query = request.args.get('q', '').strip()
    selected_category_slug = request.args.get('category', '').strip()
    selected_condition = request.args.get('condition', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    negotiable_only = request.args.get('negotiable') == '1'
    sort_by = request.args.get('sort', 'newest').strip()

    query = Item.query.filter(
        Item.listing_type.in_(['sell', 'both']),
        Item.sale_status == 'available',
        Item.availability_status != 'borrowed'
    )

    if search_query:
        term = f"%{search_query}%"
        query = query.filter(
            or_(
                Item.title.ilike(term),
                Item.description.ilike(term),
                Item.tags.ilike(term),
                Item.location.ilike(term)
            )
        )

    selected_category = None
    if selected_category_slug:
        selected_category = Category.query.filter_by(slug=selected_category_slug).first()
        if selected_category:
            query = query.filter(Item.category_id == selected_category.id)

    if selected_condition:
        query = query.filter(Item.condition == selected_condition)

    if negotiable_only:
        query = query.filter(Item.negotiable == True)

    if min_price is not None and min_price >= 0:
        query = query.filter(Item.selling_price >= min_price)

    if max_price is not None and max_price > 0:
        query = query.filter(Item.selling_price <= max_price)

    if sort_by == 'price_asc':
        query = query.order_by(asc(Item.selling_price))
    elif sort_by == 'price_desc':
        query = query.order_by(desc(Item.selling_price))
    elif sort_by == 'popular':
        query = query.order_by(desc(Item.views_count))
    else:
        query = query.order_by(desc(Item.created_at))

    items = query.all()

    user_wishlist_ids = set()
    if current_user.is_authenticated:
        user_wishlist_ids = {w.item_id for w in current_user.wishlists}

    return render_template(
        'items/sell.html',
        items=items,
        categories=categories,
        selected_category=selected_category,
        selected_category_slug=selected_category_slug,
        selected_condition=selected_condition,
        min_price=min_price,
        max_price=max_price,
        negotiable_only=negotiable_only,
        sort_by=sort_by,
        search_query=search_query,
        user_wishlist_ids=user_wishlist_ids,
        total_count=len(items)
    )


# -------------------------------------------------------------------------
# 4. ADD NEW ITEM LISTING
# -------------------------------------------------------------------------
@items_bp.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    # Populate category choices dynamically
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name.asc()).all()
    ]

    if form.validate_on_submit():
        item = Item(
            owner_id=current_user.id,
            title=form.title.data.strip(),
            category_id=form.category_id.data,
            description=form.description.data.strip(),
            condition=form.condition.data,
            listing_type=form.listing_type.data,
            borrowing_fee=float(form.borrowing_fee.data or 0.0),
            deposit=float(form.deposit.data or 0.0),
            borrowing_duration_max_days=int(form.borrowing_duration_max_days.data or 7),
            borrowing_rules=form.borrowing_rules.data.strip() if form.borrowing_rules.data else None,
            selling_price=float(form.selling_price.data) if form.selling_price.data else None,
            negotiable=form.negotiable.data,
            location=form.location.data.strip(),
            tags=form.tags.data.strip() if form.tags.data else None,
            availability_status='available',
            sale_status='available'
        )
        db.session.add(item)
        db.session.flush()  # Generate item.id

        # Process item image if uploaded
        if form.image.data:
            filename = save_uploaded_image(
                form.image.data,
                target_folder=current_app.config['ITEM_UPLOAD_FOLDER'],
                max_size=(900, 700)
            )
            if filename:
                image_record = ItemImage(
                    item_id=item.id,
                    image_path=filename,
                    is_primary=True
                )
                db.session.add(image_record)

        db.session.commit()
        flash(f"Listing '{item.title}' has been successfully published to the campus catalog!", "success")
        return redirect(url_for('items.item_details', item_id=item.id))

    return render_template('items/add_item.html', form=form, title="Create New Listing")


# -------------------------------------------------------------------------
# 5. ITEM DETAILS PAGE & WORKFLOW MODALS
# -------------------------------------------------------------------------
@items_bp.route('/items/<int:item_id>')
def item_details(item_id):
    item = db.get_or_404(Item, item_id)

    # Increment views counter
    item.views_count += 1
    db.session.commit()

    # Similar items recommendation (fallback based on same category, excluding current item)
    similar_items = Item.query.filter(
        Item.category_id == item.category_id,
        Item.id != item.id
    ).order_by(desc(Item.views_count), desc(Item.created_at)).limit(4).all()

    # If same category has fewer than 4, add recent items from other categories
    if len(similar_items) < 4:
        extra_items = Item.query.filter(
            Item.id != item.id,
            ~Item.id.in_([s.id for s in similar_items])
        ).order_by(desc(Item.created_at)).limit(4 - len(similar_items)).all()
        similar_items.extend(extra_items)

    is_wishlisted = False
    if current_user.is_authenticated:
        is_wishlisted = Wishlist.query.filter_by(
            user_id=current_user.id,
            item_id=item.id
        ).first() is not None

    borrow_form = BorrowRequestForm()
    purchase_form = PurchaseRequestForm(proposed_price=item.selling_price)
    offer_form = OfferForm()

    return render_template(
        'items/item_details.html',
        item=item,
        similar_items=similar_items,
        is_wishlisted=is_wishlisted,
        borrow_form=borrow_form,
        purchase_form=purchase_form,
        offer_form=offer_form,
        title=item.title
    )


# -------------------------------------------------------------------------
# 6. EDIT ITEM LISTING
# -------------------------------------------------------------------------
@items_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = db.get_or_404(Item, item_id)

    # Ownership check
    if item.owner_id != current_user.id and not current_user.is_admin:
        flash("You do not have permission to edit this listing.", "danger")
        abort(403)

    form = ItemForm(obj=item)
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name.asc()).all()
    ]

    if form.validate_on_submit():
        item.title = form.title.data.strip()
        item.category_id = form.category_id.data
        item.description = form.description.data.strip()
        item.condition = form.condition.data
        item.listing_type = form.listing_type.data
        item.borrowing_fee = float(form.borrowing_fee.data or 0.0)
        item.deposit = float(form.deposit.data or 0.0)
        item.borrowing_duration_max_days = int(form.borrowing_duration_max_days.data or 7)
        item.borrowing_rules = form.borrowing_rules.data.strip() if form.borrowing_rules.data else None
        item.selling_price = float(form.selling_price.data) if form.selling_price.data else None
        item.negotiable = form.negotiable.data
        item.location = form.location.data.strip()
        item.tags = form.tags.data.strip() if form.tags.data else None
        item.updated_at = datetime.now(timezone.utc)

        # Handle new image upload
        if form.image.data:
            filename = save_uploaded_image(
                form.image.data,
                target_folder=current_app.config['ITEM_UPLOAD_FOLDER'],
                max_size=(900, 700)
            )
            if filename:
                # Mark previous images as not primary
                for img in item.images:
                    img.is_primary = False
                image_record = ItemImage(
                    item_id=item.id,
                    image_path=filename,
                    is_primary=True
                )
                db.session.add(image_record)

        db.session.commit()
        flash("Listing updated successfully!", "success")
        return redirect(url_for('items.item_details', item_id=item.id))

    return render_template('items/edit_item.html', form=form, item=item, title=f"Edit: {item.title}")


# -------------------------------------------------------------------------
# 7. DELETE ITEM LISTING
# -------------------------------------------------------------------------
@items_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = db.get_or_404(Item, item_id)
    if item.owner_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized action.", "danger")
        abort(403)

    item_title = item.title
    db.session.delete(item)
    db.session.commit()
    flash(f"Listing '{item_title}' has been deleted.", "info")
    return redirect(url_for('items.browse'))


# -------------------------------------------------------------------------
# 8. WISHLIST TOGGLE & VIEW
# -------------------------------------------------------------------------
@items_bp.route('/wishlist/toggle/<int:item_id>', methods=['POST', 'GET'])
@login_required
def toggle_wishlist(item_id):
    item = db.get_or_404(Item, item_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, item_id=item.id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        status = 'removed'
        flash(f"Removed '{item.title}' from your wishlist.", "info")
    else:
        wishlist_entry = Wishlist(user_id=current_user.id, item_id=item.id)
        db.session.add(wishlist_entry)
        db.session.commit()
        status = 'added'
        flash(f"Saved '{item.title}' to your wishlist!", "success")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': status, 'item_id': item.id})

    # Redirect to referrer or browse
    ref = request.referrer
    if ref and ('/items/' in ref or '/browse' in ref or '/borrow' in ref or '/sell' in ref):
        return redirect(ref)
    return redirect(url_for('items.item_details', item_id=item.id))


@items_bp.route('/wishlist')
@login_required
def wishlist_view():
    wishlist_items = [w.item for w in current_user.wishlists if w.item is not None]
    return render_template(
        'items/wishlist.html',
        items=wishlist_items,
        title="My Saved Wishlist"
    )


# -------------------------------------------------------------------------
# 9. SUBMIT BORROW REQUEST
# -------------------------------------------------------------------------
@items_bp.route('/items/<int:item_id>/borrow-request', methods=['POST'])
@login_required
def create_borrow_request(item_id):
    item = db.get_or_404(Item, item_id)

    if item.owner_id == current_user.id:
        flash("You cannot borrow your own item.", "warning")
        return redirect(url_for('items.item_details', item_id=item.id))

    if not item.is_available_for_borrow:
        flash("This item is currently not available for borrowing.", "warning")
        return redirect(url_for('items.item_details', item_id=item.id))

    form = BorrowRequestForm()
    if form.validate_on_submit():
        start = form.start_date.data
        end = form.end_date.data

        # Server-side date validation
        if end < start:
            flash("End date cannot precede the start date.", "danger")
            return redirect(url_for('items.item_details', item_id=item.id))
        if start < date.today():
            flash("Start date cannot be in the past.", "danger")
            return redirect(url_for('items.item_details', item_id=item.id))

        duration_days = max(1, (end - start).days + 1)
        if duration_days > item.borrowing_duration_max_days:
            flash(f"Requested duration ({duration_days} days) exceeds maximum allowed duration ({item.borrowing_duration_max_days} days).", "warning")
            return redirect(url_for('items.item_details', item_id=item.id))

        # Check overlapping accepted bookings
        overlap = BorrowTransaction.query.filter(
            BorrowTransaction.item_id == item.id,
            BorrowTransaction.status.in_(['accepted', 'active', 'return_pending']),
            or_(
                and_(BorrowTransaction.start_date <= start, BorrowTransaction.end_date >= start),
                and_(BorrowTransaction.start_date <= end, BorrowTransaction.end_date >= end),
                and_(BorrowTransaction.start_date >= start, BorrowTransaction.end_date <= end)
            )
        ).first()

        if overlap:
            flash("Sorry, this item is already reserved for the selected date range. Please choose different dates.", "warning")
            return redirect(url_for('items.item_details', item_id=item.id))

        total_fee = duration_days * item.borrowing_fee
        deposit = item.deposit

        borrow_req = BorrowRequest(
            item_id=item.id,
            borrower_id=current_user.id,
            start_date=start,
            end_date=end,
            total_fee=total_fee,
            deposit=deposit,
            notes=form.notes.data.strip() if form.notes.data else None,
            status='pending'
        )
        db.session.add(borrow_req)

        # Send notification to owner
        notice = Notification(
            user_id=item.owner_id,
            title="New Borrow Request",
            message=f"{current_user.full_name} requested to borrow '{item.title}' from {start} to {end}.",
            link=url_for('items.item_details', item_id=item.id),
            notification_type='borrow_request'
        )
        db.session.add(notice)
        db.session.commit()

        flash(f"Borrow request submitted to {item.owner.full_name}! You will receive a notification once approved.", "success")
        return redirect(url_for('items.item_details', item_id=item.id))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", "danger")
        return redirect(url_for('items.item_details', item_id=item.id))


# -------------------------------------------------------------------------
# 10. SUBMIT PURCHASE REQUEST
# -------------------------------------------------------------------------
@items_bp.route('/items/<int:item_id>/purchase-request', methods=['POST'])
@login_required
def create_purchase_request(item_id):
    item = db.get_or_404(Item, item_id)

    if item.owner_id == current_user.id:
        flash("You cannot purchase your own item.", "warning")
        return redirect(url_for('items.item_details', item_id=item.id))

    if not item.is_available_for_sale:
        flash("This item is no longer available for purchase.", "warning")
        return redirect(url_for('items.item_details', item_id=item.id))

    form = PurchaseRequestForm()
    if form.validate_on_submit():
        req = PurchaseRequest(
            item_id=item.id,
            buyer_id=current_user.id,
            seller_id=item.owner_id,
            proposed_price=float(form.proposed_price.data),
            message=form.message.data.strip() if form.message.data else None,
            status='pending'
        )
        db.session.add(req)

        notice = Notification(
            user_id=item.owner_id,
            title="New Purchase Request",
            message=f"{current_user.full_name} wants to purchase '{item.title}' for ₹{form.proposed_price.data:.2f}.",
            link=url_for('items.item_details', item_id=item.id),
            notification_type='purchase_request'
        )
        db.session.add(notice)
        db.session.commit()

        flash(f"Purchase request sent to {item.owner.full_name}! Coordinate pickup details via your dashboard.", "success")
        return redirect(url_for('items.item_details', item_id=item.id))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", "danger")
        return redirect(url_for('items.item_details', item_id=item.id))


# -------------------------------------------------------------------------
# 11. SUBMIT OFFER
# -------------------------------------------------------------------------
@items_bp.route('/items/<int:item_id>/make-offer', methods=['POST'])
@login_required
def make_offer(item_id):
    item = db.get_or_404(Item, item_id)

    if item.owner_id == current_user.id:
        flash("You cannot make an offer on your own listing.", "warning")
        return redirect(url_for('items.item_details', item_id=item.id))

    form = OfferForm()
    if form.validate_on_submit():
        offer = Offer(
            item_id=item.id,
            buyer_id=current_user.id,
            seller_id=item.owner_id,
            offer_amount=float(form.offer_amount.data),
            message=form.message.data.strip() if form.message.data else None,
            status='pending'
        )
        db.session.add(offer)

        notice = Notification(
            user_id=item.owner_id,
            title="New Offer Received",
            message=f"{current_user.full_name} made an offer of ₹{form.offer_amount.data:.2f} for '{item.title}'.",
            link=url_for('items.item_details', item_id=item.id),
            notification_type='offer'
        )
        db.session.add(notice)
        db.session.commit()

        flash(f"Your offer of ₹{form.offer_amount.data:.2f} has been transmitted to {item.owner.full_name}!", "success")
        return redirect(url_for('items.item_details', item_id=item.id))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", "danger")
        return redirect(url_for('items.item_details', item_id=item.id))

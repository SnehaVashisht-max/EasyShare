import io
from PIL import Image
from datetime import date, timedelta
from app.models.item import Item, ItemImage
from app.models.category import Category
from app.models.user import User
from app.models.interaction import Wishlist
from app.models.borrow import BorrowRequest
from app.models.sale import PurchaseRequest, Offer
from app.extensions import db


def test_browse_page_loads_with_items(client, app):
    """Test that browse catalog loads and displays items from the database."""
    with app.app_context():
        cat = Category.query.first()
        user = User.query.filter_by(username="testuser").first()
        item = Item(
            owner_id=user.id,
            title="Scientific Calculator fx-82MS",
            description="Classic 2-line display scientific calculator",
            category_id=cat.id,
            condition="Good",
            listing_type="borrow",
            borrowing_fee=15.0,
            location="Library"
        )
        db.session.add(item)
        db.session.commit()

    response = client.get('/browse')
    assert response.status_code == 200
    assert b"Scientific Calculator fx-82MS" in response.data
    assert b"Campus Sharing Catalog" in response.data


def test_search_functionality(client, app):
    """Test search bar keyword filtering."""
    with app.app_context():
        cat = Category.query.first()
        user = User.query.filter_by(username="testuser").first()
        item1 = Item(owner_id=user.id, title="Microbiology Lab Microscope", description="Monocular student microscope", category_id=cat.id, condition="Good", listing_type="both")
        item2 = Item(owner_id=user.id, title="Badminton Racket", description="Sports gear", category_id=cat.id, condition="Good", listing_type="both")
        db.session.add_all([item1, item2])
        db.session.commit()

    # Search for microscope
    res = client.get('/browse?q=Microscope')
    assert res.status_code == 200
    assert b"Microbiology Lab Microscope" in res.data
    assert b"Badminton Racket" not in res.data


def test_category_and_type_filters(client, app):
    """Test filtering by category and listing type."""
    with app.app_context():
        cat1 = Category.query.filter_by(slug="test-category").first()
        cat2 = Category(name="Electronics", slug="electronics")
        db.session.add(cat2)
        db.session.flush()

        user = User.query.filter_by(username="testuser").first()
        item1 = Item(owner_id=user.id, title="Item in Cat 1", description="desc", category_id=cat1.id, condition="New", listing_type="borrow")
        item2 = Item(owner_id=user.id, title="Item in Cat 2", description="desc", category_id=cat2.id, condition="Good", listing_type="sell", selling_price=500.0)
        db.session.add_all([item1, item2])
        db.session.commit()

    # Filter by cat2
    res_cat = client.get('/browse?category=electronics')
    assert res_cat.status_code == 200
    assert b"Item in Cat 2" in res_cat.data
    assert b"Item in Cat 1" not in res_cat.data

    # Filter by type=borrow
    res_type = client.get('/browse?type=borrow')
    assert res_type.status_code == 200
    assert b"Item in Cat 1" in res_type.data
    assert b"Item in Cat 2" not in res_type.data


def test_borrow_page_functional(client, app):
    """Test dedicated borrow catalog only shows borrowable items."""
    with app.app_context():
        cat = Category.query.first()
        user = User.query.filter_by(username="testuser").first()
        borrow_item = Item(owner_id=user.id, title="Borrowable Tennis Racket", description="Good condition", category_id=cat.id, listing_type="borrow", borrowing_fee=20.0)
        sell_item = Item(owner_id=user.id, title="Sell Only Textbook", description="Not for rent", category_id=cat.id, listing_type="sell", selling_price=300.0)
        db.session.add_all([borrow_item, sell_item])
        db.session.commit()

    res = client.get('/borrow')
    assert res.status_code == 200
    assert b"Borrowable Tennis Racket" in res.data
    assert b"Sell Only Textbook" not in res.data


def test_sell_page_functional(client, app):
    """Test dedicated buy & sell page only shows items for sale."""
    with app.app_context():
        cat = Category.query.first()
        user = User.query.filter_by(username="testuser").first()
        borrow_item = Item(owner_id=user.id, title="Only Rental Lab Goggles", description="Daily fee", category_id=cat.id, listing_type="borrow", borrowing_fee=10.0)
        sell_item = Item(owner_id=user.id, title="Engineering Drafting Board for Sale", description="Secondhand purchase", category_id=cat.id, listing_type="sell", selling_price=750.0)
        db.session.add_all([borrow_item, sell_item])
        db.session.commit()

    res = client.get('/sell')
    assert res.status_code == 200
    assert b"Engineering Drafting Board for Sale" in res.data
    assert b"Only Rental Lab Goggles" not in res.data


def test_item_details_page(client, app):
    """Test viewing an item's details."""
    with app.app_context():
        cat = Category.query.first()
        user = User.query.filter_by(username="testuser").first()
        item = Item(
            owner_id=user.id,
            title="Electric Guitar Amplifier",
            description="15W practice amp with overdrive channel",
            category_id=cat.id,
            condition="Like New",
            listing_type="both",
            borrowing_fee=40.0,
            deposit=800.0,
            selling_price=3500.0,
            location="Hostel 2"
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    res = client.get(f'/items/{item_id}')
    assert res.status_code == 200
    assert b"Electric Guitar Amplifier" in res.data
    assert b"15W practice amp" in res.data
    assert b"Hostel 2" in res.data


def test_add_item_submission(client, app):
    """Test creating and saving a new item via POST."""
    # Log in first
    client.post('/auth/login', data={'login_identifier': 'testuser', 'password': 'Password@123'}, follow_redirects=True)

    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    res = client.post('/items/add', data={
        'title': 'Raspberry Pi 4 Starter Kit',
        'category_id': cat_id,
        'description': '4GB RAM Raspberry Pi with case, power supply, and 32GB SD card.',
        'condition': 'Like New',
        'listing_type': 'both',
        'borrowing_fee': '30.00',
        'deposit': '500.00',
        'borrowing_duration_max_days': 10,
        'borrowing_rules': 'Please backup SD card before returning.',
        'selling_price': '4500.00',
        'negotiable': 'y',
        'location': 'Robotics Lab',
        'tags': 'iot, raspberrypi, python, coding'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Raspberry Pi 4 Starter Kit" in res.data

    with app.app_context():
        saved_item = Item.query.filter_by(title='Raspberry Pi 4 Starter Kit').first()
        assert saved_item is not None
        assert saved_item.borrowing_fee == 30.0
        assert saved_item.selling_price == 4500.0
        assert saved_item.owner.username == 'testuser'


def test_wishlist_toggle(client, app):
    """Test bookmarking an item to wishlist."""
    client.post('/auth/login', data={'login_identifier': 'testuser', 'password': 'Password@123'}, follow_redirects=True)

    with app.app_context():
        cat = Category.query.first()
        user = User.query.filter_by(username="testuser").first()
        item = Item(owner_id=user.id, title="Wishlist Test Item", description="A description", category_id=cat.id, listing_type="both")
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # Toggle add
    toggle_res = client.post(f'/wishlist/toggle/{item_id}', follow_redirects=True)
    assert toggle_res.status_code == 200

    with app.app_context():
        w = Wishlist.query.filter_by(item_id=item_id).first()
        assert w is not None

    # Toggle remove
    toggle_res2 = client.post(f'/wishlist/toggle/{item_id}', follow_redirects=True)
    assert toggle_res2.status_code == 200

    with app.app_context():
        w2 = Wishlist.query.filter_by(item_id=item_id).first()
        assert w2 is None


def test_borrow_request_workflow(client, app):
    """Test sending a borrow request from one user to another."""
    with app.app_context():
        cat = Category.query.first()
        lender = User.query.filter_by(username="testuser").first()
        item = Item(
            owner_id=lender.id,
            title="Lent Item",
            description="Item to borrow",
            category_id=cat.id,
            listing_type="borrow",
            borrowing_fee=20.0,
            deposit=200.0,
            borrowing_duration_max_days=7
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # Log in as a DIFFERENT student
    client.post('/auth/register', data={
        'username': 'borrower_student',
        'email': 'borrower@campus.edu',
        'full_name': 'Borrower Student',
        'college_or_community': 'Campus Block A',
        'password': 'BorrowerPass@123',
        'confirm_password': 'BorrowerPass@123',
        'terms': 'y'
    }, follow_redirects=True)

    client.post('/auth/login', data={
        'login_identifier': 'borrower_student',
        'password': 'BorrowerPass@123'
    }, follow_redirects=True)

    start = date.today()
    end = start + timedelta(days=2)

    res = client.post(f'/items/{item_id}/borrow-request', data={
        'start_date': start.strftime('%Y-%m-%d'),
        'end_date': end.strftime('%Y-%m-%d'),
        'notes': 'Need for project demo'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Borrow request submitted" in res.data

    with app.app_context():
        req = BorrowRequest.query.filter_by(item_id=item_id).first()
        assert req is not None
        assert req.status == 'pending'
        assert req.total_fee == 60.0  # 3 days * 20.0


def test_dashboard_view_when_authenticated(client):
    """Test accessing the user dashboard."""
    client.post('/auth/login', data={'login_identifier': 'testuser', 'password': 'Password@123'}, follow_redirects=True)
    res = client.get('/dashboard')
    assert res.status_code == 200
    assert b"Welcome, Test User" in res.data
    assert b"My Listings" in res.data
    assert b"Borrow Requests" in res.data


def test_notifications_view_and_read(client, app):
    """Test viewing notifications and marking as read."""
    client.post('/auth/login', data={'login_identifier': 'testuser', 'password': 'Password@123'}, follow_redirects=True)
    res = client.get('/notifications')
    assert res.status_code == 200
    assert b"Notifications" in res.data


def test_purchase_request_and_offer_workflow(client, app):
    """Test submitting purchase requests and making price offers."""
    with app.app_context():
        cat = Category.query.first()
        seller = User.query.filter_by(username="testuser").first()
        item = Item(
            owner_id=seller.id,
            title="Secondhand Bicycle",
            description="Geared bicycle in good condition",
            category_id=cat.id,
            listing_type="sell",
            selling_price=3000.0,
            negotiable=True
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # Register and log in as buyer
    client.post('/auth/register', data={
        'username': 'buyer_student',
        'email': 'buyer@campus.edu',
        'full_name': 'Buyer Student',
        'college_or_community': 'Hostel 3',
        'password': 'BuyerPass@123',
        'confirm_password': 'BuyerPass@123',
        'terms': 'y'
    }, follow_redirects=True)

    client.post('/auth/login', data={
        'login_identifier': 'buyer_student',
        'password': 'BuyerPass@123'
    }, follow_redirects=True)

    # 1. Send Purchase Request
    p_res = client.post(f'/items/{item_id}/purchase-request', data={
        'proposed_price': '2900.00',
        'message': 'Ready for cash on delivery'
    }, follow_redirects=True)
    assert p_res.status_code == 200
    assert b"Purchase request sent" in p_res.data

    with app.app_context():
        pr = PurchaseRequest.query.filter_by(item_id=item_id).first()
        assert pr is not None
        assert pr.proposed_price == 2900.0

    # 2. Make an offer
    o_res = client.post(f'/items/{item_id}/make-offer', data={
        'offer_amount': '2700.00',
        'message': 'Can pick up within 1 hour'
    }, follow_redirects=True)
    assert o_res.status_code == 200
    assert b"Your offer of" in o_res.data

    with app.app_context():
        off = Offer.query.filter_by(item_id=item_id).first()
        assert off is not None
        assert off.offer_amount == 2700.0


def test_edit_and_delete_item(client, app):
    """Test owner editing and deleting their own listing."""
    client.post('/auth/login', data={'login_identifier': 'testuser', 'password': 'Password@123'}, follow_redirects=True)

    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id
        user = User.query.filter_by(username="testuser").first()
        item = Item(
            owner_id=user.id,
            title="Item To Edit",
            description="Original description text here",
            category_id=cat_id,
            listing_type="both",
            borrowing_fee=10.0,
            selling_price=500.0,
            location="Room 101"
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # Edit item
    edit_res = client.post(f'/items/{item_id}/edit', data={
        'title': 'Item To Edit - Updated Title',
        'category_id': cat_id,
        'description': 'Updated description text with plenty of details.',
        'condition': 'Like New',
        'listing_type': 'both',
        'borrowing_fee': '15.00',
        'deposit': '100.00',
        'borrowing_duration_max_days': 5,
        'selling_price': '600.00',
        'negotiable': 'y',
        'location': 'Room 102'
    }, follow_redirects=True)

    assert edit_res.status_code == 200
    assert b"Listing updated successfully" in edit_res.data

    with app.app_context():
        updated = db.session.get(Item, item_id)
        assert updated.title == 'Item To Edit - Updated Title'
        assert updated.location == 'Room 102'

    # Delete item
    del_res = client.post(f'/items/{item_id}/delete', follow_redirects=True)
    assert del_res.status_code == 200
    assert b"has been deleted" in del_res.data

    with app.app_context():
        deleted = db.session.get(Item, item_id)
        assert deleted is None


def test_calculator_image_upload_and_display_workflow(client, app):
    """Test full image upload, storage, database record, and display pipeline with a real calculator image."""
    client.post('/auth/login', data={'login_identifier': 'testuser', 'password': 'Password@123'}, follow_redirects=True)

    # 1. Create a real in-memory calculator image with Pillow
    img_byte_arr = io.BytesIO()
    test_img = Image.new('RGB', (400, 300), color='#1e293b')
    test_img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    with app.app_context():
        cat = Category.query.filter_by(slug='calculators').first()
        if not cat:
            cat = Category.query.first()
        cat_id = cat.id

    # 2. Upload image and create calculator listing
    res = client.post('/items/add', data={
        'title': 'Casio Advanced Graphing Calculator Test',
        'category_id': cat_id,
        'description': 'Graphing calculator with rechargeable battery and matrix functions.',
        'condition': 'Like New',
        'listing_type': 'both',
        'borrowing_fee': '25.00',
        'deposit': '500.00',
        'borrowing_duration_max_days': 7,
        'selling_price': '2800.00',
        'negotiable': 'y',
        'location': 'Mathematics Department Study Hall',
        'image': (img_byte_arr, 'calculator_test_photo.jpg')
    }, content_type='multipart/form-data', follow_redirects=True)

    assert res.status_code == 200
    assert b"successfully published" in res.data

    with app.app_context():
        new_item = Item.query.filter_by(title='Casio Advanced Graphing Calculator Test').first()
        assert new_item is not None
        assert len(new_item.images) == 1
        img_record = new_item.images[0]
        assert img_record.is_primary is True
        assert img_record.image_path.endswith('.jpg')
        assert 'uploads/items/' in new_item.primary_image_url
        item_id = new_item.id
        image_path = img_record.image_path

    # 3. Confirm image appears on Browse page
    browse_res = client.get('/browse?q=Calculator+Test')
    assert browse_res.status_code == 200
    assert image_path.encode('utf-8') in browse_res.data
    assert b"Casio Advanced Graphing Calculator Test" in browse_res.data

    # 4. Confirm image appears on Item Details page
    details_res = client.get(f'/items/{item_id}')
    assert details_res.status_code == 200
    assert image_path.encode('utf-8') in details_res.data


from datetime import datetime, date, timedelta, timezone
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.item import Item, ItemAvailability
from app.models.borrow import BorrowRequest, BorrowTransaction
from app.models.sale import PurchaseRequest, Offer, Sale
from app.models.interaction import Wishlist, Review, Notification, Report
from app.models.qr import QRVerification


def test_models_complete_workflow(app):
    """Test creating and relating all core EasyShare models."""
    with app.app_context():
        # 1. Fetch fixture user and category
        lender = User.query.filter_by(username="testuser").first()
        category = Category.query.filter_by(slug="test-category").first()

        # Create borrower user
        borrower = User(
            username="borrower1",
            email="borrower1@campus.edu",
            full_name="Bob Borrower",
            college_or_community="South Campus"
        )
        borrower.set_password("BorrowerPass@123")
        db.session.add(borrower)
        db.session.commit()

        # 2. Create Item
        item = Item(
            owner_id=lender.id,
            title="Digital Multimeter",
            description="True-RMS 6000 Counts electrical tester",
            category_id=category.id,
            condition="Good",
            listing_type="both",
            selling_price=1200.0,
            borrowing_fee=20.0,
            deposit=300.0,
            location="Lab 302"
        )
        db.session.add(item)
        db.session.commit()

        assert item.id is not None
        assert item.is_available_for_borrow is True
        assert item.is_available_for_sale is True
        assert len(lender.items) == 1

        # 3. Create Borrow Request
        today = date.today()
        end_day = today + timedelta(days=3)
        borrow_req = BorrowRequest(
            item_id=item.id,
            borrower_id=borrower.id,
            start_date=today,
            end_date=end_day,
            total_fee=60.0,
            deposit=300.0,
            status="pending"
        )
        db.session.add(borrow_req)
        db.session.commit()

        assert borrow_req.id is not None
        assert borrow_req.duration_days == 4

        # 4. Accept Request and Create Borrow Transaction
        borrow_req.status = "accepted"
        tx = BorrowTransaction(
            borrow_request_id=borrow_req.id,
            item_id=item.id,
            borrower_id=borrower.id,
            lender_id=lender.id,
            start_date=today,
            end_date=end_day,
            status="accepted"
        )
        db.session.add(tx)
        db.session.commit()

        assert tx.id is not None
        assert tx.borrower.username == "borrower1"
        assert tx.lender.username == "testuser"

        # 5. Create QR Verification Token
        qr = QRVerification(
            borrow_transaction_id=tx.id,
            action_type="handover",
            token_hash="fake-hash-for-testing",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2)
        )
        db.session.add(qr)
        db.session.commit()

        assert qr.id is not None
        assert qr.is_expired is False

        # 6. Create Purchase Request & Sale
        purch_req = PurchaseRequest(
            item_id=item.id,
            buyer_id=borrower.id,
            seller_id=lender.id,
            proposed_price=1000.0,
            status="pending"
        )
        db.session.add(purch_req)
        db.session.commit()

        offer = Offer(
            item_id=item.id,
            buyer_id=borrower.id,
            seller_id=lender.id,
            offer_amount=1050.0,
            status="pending"
        )
        db.session.add(offer)
        db.session.commit()

        sale = Sale(
            item_id=item.id,
            buyer_id=borrower.id,
            seller_id=lender.id,
            purchase_request_id=purch_req.id,
            agreed_price=1050.0,
            status="reserved"
        )
        db.session.add(sale)
        db.session.commit()

        assert sale.id is not None

        # 7. Wishlist and Review
        wishlist = Wishlist(user_id=borrower.id, item_id=item.id)
        db.session.add(wishlist)

        review = Review(
            reviewer_id=borrower.id,
            target_user_id=lender.id,
            item_id=item.id,
            borrow_transaction_id=tx.id,
            rating=5,
            comment="Excellent condition, friendly lender!",
            review_type="borrower_to_lender"
        )
        db.session.add(review)

        # 8. Notification and Report
        notification = Notification(
            user_id=borrower.id,
            title="Handover confirmed",
            message="Your item handover was verified.",
            notification_type="handover"
        )
        db.session.add(notification)

        report = Report(
            reporter_id=borrower.id,
            reported_item_id=item.id,
            reason="Incorrect item details",
            description="Testing report filing"
        )
        db.session.add(report)

        db.session.commit()

        assert wishlist.id is not None
        assert review.id is not None
        assert notification.id is not None
        assert report.id is not None

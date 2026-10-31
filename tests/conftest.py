import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.category import Category


@pytest.fixture
def app():
    """Create and configure a clean testing app instance."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()

        # Seed basic category
        cat = Category(
            name="Test Category",
            slug="test-category",
            description="Testing category",
            icon="bi-tag"
        )
        db.session.add(cat)

        # Seed basic test user
        user = User(
            username="testuser",
            email="testuser@example.com",
            full_name="Test User",
            college_or_community="Engineering Campus",
            phone="+91 99999 11111",
            contact_preference="in_app",
            role="user",
            trust_score=100.0
        )
        user.set_password("Password@123")
        db.session.add(user)

        # Seed admin user
        admin = User(
            username="adminuser",
            email="adminuser@example.com",
            full_name="Admin User",
            college_or_community="Campus Admin",
            role="admin",
            trust_score=100.0
        )
        admin.set_password("AdminPassword@123")
        db.session.add(admin)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for app's CLI commands."""
    return app.test_cli_runner()

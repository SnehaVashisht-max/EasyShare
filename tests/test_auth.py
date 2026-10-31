from app.models.user import User
from app.extensions import db


def test_password_hashing(app):
    """Test that passwords are encrypted and checked securely."""
    with app.app_context():
        u = User(username="cipher", email="cipher@test.com", full_name="Cipher Test")
        u.set_password("Secret123")
        assert u.password_hash != "Secret123"
        assert u.check_password("Secret123") is True
        assert u.check_password("WrongPassword") is False


def test_password_reset_token(app):
    """Test generating and verifying password reset tokens."""
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        token = user.get_reset_token()
        assert token is not None

        # Valid token
        verified_user = User.verify_reset_token(token)
        assert verified_user is not None
        assert verified_user.id == user.id

        # Invalid token
        assert User.verify_reset_token("invalid-garbage-token") is None


def test_admin_role_checking(app):
    """Test admin verification logic."""
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        admin = User.query.filter_by(username="adminuser").first()

        assert user.is_admin is False
        assert admin.is_admin is True


def test_register_page_loads(client):
    """Test that registration page loads successfully."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b"Join the Reuse Movement" in response.data


def test_register_successful(client, app):
    """Test registering a new student account."""
    response = client.post('/auth/register', data={
        'username': 'newstudent',
        'email': 'newstudent@college.edu',
        'full_name': 'New Student',
        'college_or_community': 'Science Block',
        'phone': '+91 91234 56789',
        'contact_preference': 'in_app',
        'password': 'StrongPassword@123',
        'confirm_password': 'StrongPassword@123',
        'terms': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(username='newstudent').first()
        assert user is not None
        assert user.email == 'newstudent@college.edu'
        assert user.check_password('StrongPassword@123') is True
        assert user.trust_score == 100.0


def test_register_duplicate_username(client):
    """Test that registering duplicate username is blocked."""
    response = client.post('/auth/register', data={
        'username': 'testuser',  # already in fixture
        'email': 'different@college.edu',
        'full_name': 'Another User',
        'college_or_community': 'Engineering',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'terms': 'y'
    })
    assert response.status_code == 200
    assert b"This username is already taken" in response.data


def test_register_duplicate_email(client):
    """Test that registering duplicate email is blocked."""
    response = client.post('/auth/register', data={
        'username': 'unique_user',
        'email': 'testuser@example.com',  # already in fixture
        'full_name': 'Unique User',
        'college_or_community': 'Engineering',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'terms': 'y'
    })
    assert response.status_code == 200
    assert b"An account with this email address already exists" in response.data


def test_login_successful_with_email(client):
    """Test login via email."""
    response = client.post('/auth/login', data={
        'login_identifier': 'testuser@example.com',
        'password': 'Password@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Test User!" in response.data


def test_login_successful_with_username(client):
    """Test login via username."""
    response = client.post('/auth/login', data={
        'login_identifier': 'testuser',
        'password': 'Password@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Test User!" in response.data


def test_login_invalid_password(client):
    """Test login rejection on wrong password."""
    response = client.post('/auth/login', data={
        'login_identifier': 'testuser',
        'password': 'WrongPassword@999'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email/username or password" in response.data


def test_logout(client):
    """Test logging out an authenticated session."""
    # First log in
    client.post('/auth/login', data={
        'login_identifier': 'testuser',
        'password': 'Password@123'
    }, follow_redirects=True)

    # Then log out
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been successfully signed out" in response.data


def test_profile_requires_login(client):
    """Test that accessing profile without login redirects to sign in."""
    response = client.get('/auth/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_profile_view_and_edit_when_authenticated(client, app):
    """Test authenticated user viewing profile and updating details."""
    # Log in
    client.post('/auth/login', data={
        'login_identifier': 'testuser',
        'password': 'Password@123'
    }, follow_redirects=True)

    # View profile
    response = client.get('/auth/profile')
    assert response.status_code == 200
    assert b"Test User" in response.data
    assert b"TrustScore Breakdown" in response.data

    # Edit profile details
    update_res = client.post('/auth/profile', data={
        'full_name': 'Test User Updated',
        'college_or_community': 'South Campus Labs',
        'phone': '+91 88888 22222',
        'contact_preference': 'email',
        'submit_profile': 'Save Changes'
    }, follow_redirects=True)

    assert update_res.status_code == 200
    assert b"Your profile has been updated successfully" in update_res.data

    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user.full_name == 'Test User Updated'
        assert user.college_or_community == 'South Campus Labs'
        assert user.contact_preference == 'email'


def test_change_password_flow(client, app):
    """Test password update when authenticated."""
    # Log in
    client.post('/auth/login', data={
        'login_identifier': 'testuser',
        'password': 'Password@123'
    }, follow_redirects=True)

    # Attempt with incorrect current password
    fail_res = client.post('/auth/change-password', data={
        'current_password': 'IncorrectCurrentPassword',
        'new_password': 'BrandNewPassword@456',
        'confirm_new_password': 'BrandNewPassword@456'
    }, follow_redirects=True)
    assert b"Incorrect current password" in fail_res.data

    # Attempt with valid credentials
    success_res = client.post('/auth/change-password', data={
        'current_password': 'Password@123',
        'new_password': 'BrandNewPassword@456',
        'confirm_new_password': 'BrandNewPassword@456'
    }, follow_redirects=True)
    assert b"Your password has been changed successfully" in success_res.data

    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user.check_password('BrandNewPassword@456') is True
        assert user.check_password('Password@123') is False


# EasyShare – Borrow. Lend. Sell. Reuse.
*(ShareShelf AI)*

A modern, responsive, AI-powered campus and community sharing platform designed to help students and community members borrow, lend, and sell reusable items instead of purchasing new ones.

---

## Technology Stack

- **Backend**: Python 3.14 / 3.11+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug, itsdangerous
- **Database**: SQLite (default for development; structured with SQLAlchemy ORM for seamless PostgreSQL migration)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Google Fonts (Inter)
- **Imaging & Utilities**: Pillow, qrcode, APScheduler
- **Testing**: pytest

---

## Project Structure

```text
EasyShare/
├── app/
│   ├── __init__.py            # Flask application factory (create_app)
│   ├── extensions.py          # Shared extensions (db, login_manager, csrf)
│   ├── forms/
│   │   ├── __init__.py
│   │   └── auth.py            # WTForms (Registration, Login, Reset, Profile, Password)
│   ├── models/
│   │   ├── __init__.py        # Exports all 15 database models
│   │   ├── user.py            # User model with authentication, TrustScore & roles
│   │   ├── category.py        # Categories (Books, Electronics, Calculators, etc.)
│   │   ├── item.py            # Item, ItemImage, ItemAvailability (Smart Calendar)
│   │   ├── borrow.py          # BorrowRequest and BorrowTransaction
│   │   ├── sale.py            # PurchaseRequest, Offer, and Sale
│   │   ├── interaction.py     # Wishlist, Review, Notification, Report
│   │   └── qr.py              # Single-use QR verification protocol
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication, registration, password reset, profile
│   │   └── main.py            # Homepage, about, navigation placeholders
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Emerald & slate theme, responsive cards & layout
│   │   ├── images/
│   │   │   ├── default_avatar.svg
│   │   │   └── item_placeholder.svg
│   │   ├── js/
│   │   │   └── main.js        # Alerts, tooltips, validation helpers
│   │   └── uploads/
│   │       ├── items/         # Uploaded item listing pictures
│   │       └── profiles/      # Uploaded user avatars
│   ├── templates/
│   │   ├── base.html          # Responsive navbar, flash alerts, footer layout
│   │   ├── index.html         # Hero, category grid, workflow & community metrics
│   │   ├── about.html         # Mission, TrustScore philosophy, campus honor code
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── reset_request.html
│   │   │   ├── reset_password.html
│   │   │   └── profile.html   # Overview, TrustScore breakdown, edit profile, security
│   │   └── errors/
│   │       ├── 403.html
│   │       ├── 404.html
│   │       ├── 413.html
│   │       └── 500.html
│   └── utils/
│       ├── __init__.py
│       └── helpers.py         # Image optimization, admin decorator, currency formatter
├── instance/
│   └── easyshare.db           # SQLite database
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest test fixtures
│   ├── test_auth.py           # 14 authentication and security tests
│   └── test_models.py         # Full model lifecycle and relationship tests
├── config.py                  # Dev, Testing, and Production configurations
├── requirements.txt           # Python dependencies
├── seed_data.py               # Database seeder (categories, admin, student, sample item)
├── run.py                     # Entry point & CLI runner
├── .env.example               # Environment variables template
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ installed
- Git (optional)

### 2. Clone or Open Project
```powershell
cd c:\Users\DELL\OneDrive\Desktop\EasyShare
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Initialize Database & Seed Demo Data
Run the seeding script to create database tables and populate standard categories, an administrator account, a student account, and initial sample listings:
```powershell
python seed_data.py
```

### 5. Run the Application
```powershell
python run.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## Default Demo Accounts

For testing, presentation, and grading:

| Role | Username / Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` / `admin@easyshare.local` | `Admin@123` | Full admin privileges, TrustScore: 100.0 |
| **Student** | `alex_student` / `student@easyshare.local` | `Student@123` | Standard user, North Campus Engineering |

You can also register any number of new student accounts directly via the `/auth/register` interface.

---

## Running Automated Tests

Run the full pytest suite with verbose output:
```powershell
pytest -v
```

All 15 automated test cases verify:
1. Password hashing security (scrypt salt, non-plaintext)
2. Password reset token generation and timed validation
3. Administrator role authorization checks
4. Registration form rendering and successful student onboarding
5. Duplicate username prevention
6. Duplicate email prevention
7. Login via registered email address
8. Login via registered username
9. Rejection of invalid credentials
10. Session logout and teardown
11. Authentication protection on profile routes
12. Profile details updates (name, community, contact preferences)
13. Password change security with current password validation
14. Database relationships (User, Category, Item, BorrowRequest, BorrowTransaction, PurchaseRequest, Offer, Sale, Wishlist, Review, Notification, QRVerification)
15. QR token expiration and timezone-safe comparison

---

## Phase 1 Status

- [x] Flask Application Factory (`create_app`) & Configuration (`config.py`)
- [x] Complete SQLAlchemy Database Schema (all 15 tables)
- [x] User Authentication & Session Management (Flask-Login, Werkzeug hashing)
- [x] Timed Password Reset workflow
- [x] CSRF Protection on all forms (Flask-WTF)
- [x] User Profile View with TrustScore breakdown & Profile Edit
- [x] Responsive layout with Bootstrap 5.3 & custom styling
- [x] Database seeder script (`seed_data.py`)
- [x] Automated test suite passing with 100% success rate

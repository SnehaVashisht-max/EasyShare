"""
EasyShare - Database Seeder Script
Initializes categories, demo admin, sample students, and a rich set of 14 campus listings.
"""
from app import create_app
from app.extensions import db
from app.models.category import Category
from app.models.user import User
from app.models.item import Item, ItemImage
from app.models.interaction import Notification


DEFAULT_CATEGORIES = [
    {
        "name": "Books",
        "slug": "books",
        "description": "Textbooks, reference guides, lecture notes, and novels",
        "icon": "bi-book"
    },
    {
        "name": "Electronics",
        "slug": "electronics",
        "description": "Headphones, chargers, cables, power banks, and adapters",
        "icon": "bi-plug"
    },
    {
        "name": "Calculators",
        "slug": "calculators",
        "description": "Scientific, financial, and graphing calculators for exams",
        "icon": "bi-calculator"
    },
    {
        "name": "Laptops & Accessories",
        "slug": "laptops-accessories",
        "description": "Laptop stands, keyboards, mice, external drives, and monitors",
        "icon": "bi-laptop"
    },
    {
        "name": "Sports Equipment",
        "slug": "sports-equipment",
        "description": "Badminton rackets, footballs, gym gear, and cycling accessories",
        "icon": "bi-trophy"
    },
    {
        "name": "Lab Equipment",
        "slug": "lab-equipment",
        "description": "Lab coats, safety goggles, breadboards, and multimeter kits",
        "icon": "bi-radioactive"
    },
    {
        "name": "Stationery",
        "slug": "stationery",
        "description": "Drafting tools, T-squares, art supplies, and binders",
        "icon": "bi-pencil-square"
    },
    {
        "name": "Musical Instruments",
        "slug": "musical-instruments",
        "description": "Guitars, keyboards, ukuleles, and audio accessories",
        "icon": "bi-music-note-beamed"
    },
    {
        "name": "Clothing",
        "slug": "clothing",
        "description": "Formal wear for presentations, winter jackets, and lab aprons",
        "icon": "bi-bag"
    },
    {
        "name": "Other",
        "slug": "other",
        "description": "Dorm essentials, umbrellas, tools, and miscellaneous campus gear",
        "icon": "bi-box-seam"
    }
]

PRODUCT_IMAGE_MAP = {
    "TI-84 Plus CE Graphing Calculator": "ti84_ce_calc.jpg",
    "TI-84 Plus Graphing Calculator": "ti84_ce_calc.jpg",
    "Casio fx-991EX ClassWiz Scientific Calculator": "casio_classwiz.jpg",
    "Higher Engineering Mathematics (B.S. Grewal 44th Edition)": "math_grewal.jpg",
    "Organic Chemistry (Paula Bruice 8th Global Edition)": "bruice_organic_chem.jpg",
    "Concepts of Physics (H.C. Verma Vol 1 & Vol 2)": "hc_verma_physics.jpg",
    "Cotton White Lab Coat & UV Safety Goggles Set (Size M)": "lab_coat_goggles.jpg",
    "Digital Multimeter with Test Probes & 9V Battery": "multimeter.jpg",
    "Yonex Nanoray Carbon Fiber Badminton Racket Pair": "badminton_racket.jpg",
    "Spalding NBA Official Grip Basketball (Size 7)": "basketball.jpg",
    "Logitech MX Master 2S Wireless Bluetooth Mouse": "mouse.jpg",
    "Foldable Aluminum Laptop Cooling Stand": "laptop_stand.jpg",
    "Yamaha F280 Acoustic Folk Guitar with Padded Gig Bag": "acoustic_guitar.jpg",
    "Rotring Rapid Pro Technical Drafting Pen (0.5mm)": "drafting_pen.jpg",
    "Anker 20000mAh PowerCore 20W Fast Power Bank": "powerbank.jpg",
    "mobile phone": "mobile_phone.jpg",
    "Earbuds": "earbuds.jpg"
}

SAMPLE_LISTINGS = [
    {
        "title": "TI-84 Plus CE Graphing Calculator",
        "category_slug": "calculators",
        "condition": "Like New",
        "listing_type": "both",
        "borrowing_fee": 30.0,
        "deposit": 600.0,
        "borrowing_duration_max_days": 7,
        "selling_price": 3200.0,
        "negotiable": True,
        "location": "North Campus Library, 2nd Floor",
        "tags": "calculator, math, calculus, exams, engineering",
        "description": "Color screen rechargeable TI-84 Plus CE. Battery lasts 2+ weeks. Preloaded with periodic table and polymath apps. Ideal for AP Calculus, Linear Algebra, and Engineering exams."
    },
    {
        "title": "Casio fx-991EX ClassWiz Scientific Calculator",
        "category_slug": "calculators",
        "condition": "Good",
        "listing_type": "borrow",
        "borrowing_fee": 15.0,
        "deposit": 300.0,
        "borrowing_duration_max_days": 10,
        "selling_price": None,
        "negotiable": False,
        "location": "Engineering Block C, Ground Floor",
        "tags": "calculator, casio, scientific, engineering",
        "description": "High-resolution 552 functions calculator. Matrix calculations, equation solving, spreadsheet view. Permitted in university semester exams."
    },
    {
        "title": "Higher Engineering Mathematics (B.S. Grewal 44th Edition)",
        "category_slug": "books",
        "condition": "Good",
        "listing_type": "both",
        "borrowing_fee": 10.0,
        "deposit": 200.0,
        "borrowing_duration_max_days": 14,
        "selling_price": 480.0,
        "negotiable": True,
        "location": "Central Campus Library Entrance",
        "tags": "textbook, math, grewal, engineering, sem1",
        "description": "Standard textbook for 1st & 2nd year engineering mathematics. Clean pages, no missing chapters. Minor corner creasing on front cover."
    },
    {
        "title": "Organic Chemistry (Paula Bruice 8th Global Edition)",
        "category_slug": "books",
        "condition": "Fair",
        "listing_type": "sell",
        "borrowing_fee": 0.0,
        "deposit": 0.0,
        "borrowing_duration_max_days": 7,
        "selling_price": 550.0,
        "negotiable": True,
        "location": "Science Department Lawn",
        "tags": "chemistry, organic, bruice, pre-med, textbook",
        "description": "Hardcover edition. Very helpful reaction mechanism diagrams. Some pencil annotations in chapters 4 through 8, but fully legible."
    },
    {
        "title": "Concepts of Physics (H.C. Verma Vol 1 & Vol 2)",
        "category_slug": "books",
        "condition": "Like New",
        "listing_type": "borrow",
        "borrowing_fee": 12.0,
        "deposit": 350.0,
        "borrowing_duration_max_days": 21,
        "selling_price": None,
        "negotiable": False,
        "location": "Hostel 4 Common Room",
        "tags": "physics, hc verma, mechanics, optics",
        "description": "Both volumes in like-new condition. Perfect for clearing conceptual physics and practicing classic mechanics problems."
    },
    {
        "title": "Cotton White Lab Coat & UV Safety Goggles Set (Size M)",
        "category_slug": "lab-equipment",
        "condition": "Like New",
        "listing_type": "both",
        "borrowing_fee": 15.0,
        "deposit": 250.0,
        "borrowing_duration_max_days": 5,
        "selling_price": 380.0,
        "negotiable": False,
        "location": "Chemistry Lab 101 Entrance",
        "tags": "lab coat, goggles, chemistry, biology, safety",
        "description": "100% thick cotton knee-length white lab coat with snap buttons. Washed and sanitized. Includes anti-fog splash-proof safety goggles."
    },
    {
        "title": "Digital Multimeter with Test Probes & 9V Battery",
        "category_slug": "lab-equipment",
        "condition": "Good",
        "listing_type": "borrow",
        "borrowing_fee": 20.0,
        "deposit": 400.0,
        "borrowing_duration_max_days": 7,
        "selling_price": None,
        "negotiable": False,
        "location": "Electrical Workshop Block",
        "tags": "multimeter, electronics, tester, arduino, circuits",
        "description": "Digital multimeter measuring AC/DC voltage, DC current, resistance, and continuity buzzer. Fresh battery installed."
    },
    {
        "title": "Yonex Nanoray Carbon Fiber Badminton Racket Pair",
        "category_slug": "sports-equipment",
        "condition": "Good",
        "listing_type": "both",
        "borrowing_fee": 35.0,
        "deposit": 500.0,
        "borrowing_duration_max_days": 3,
        "selling_price": 1350.0,
        "negotiable": True,
        "location": "Campus Sports Complex Court 2",
        "tags": "badminton, yonex, racket, sports, weekend",
        "description": "Set of two lightweight Yonex Nanoray rackets with fresh BG-65 strings and padded covers. Includes a 3-pack of nylon shuttlecocks."
    },
    {
        "title": "Spalding NBA Official Grip Basketball (Size 7)",
        "category_slug": "sports-equipment",
        "condition": "Fair",
        "listing_type": "borrow",
        "borrowing_fee": 15.0,
        "deposit": 200.0,
        "borrowing_duration_max_days": 4,
        "selling_price": None,
        "negotiable": False,
        "location": "Basketball Court B",
        "tags": "basketball, spalding, ball, court, sports",
        "description": "Composite leather indoor/outdoor ball. Holds air pressure perfectly. Good pebbled grip."
    },
    {
        "title": "Logitech MX Master 2S Wireless Bluetooth Mouse",
        "category_slug": "laptops-accessories",
        "condition": "Good",
        "listing_type": "sell",
        "borrowing_fee": 0.0,
        "deposit": 0.0,
        "borrowing_duration_max_days": 7,
        "selling_price": 2400.0,
        "negotiable": True,
        "location": "Computer Center Cafeteria",
        "tags": "logitech, mouse, mx master, bluetooth, coding",
        "description": "Ergonomic wireless mouse with speed-adaptive scroll wheel, thumb wheel, and multi-device cross-computer control. Includes micro-USB charging cable."
    },
    {
        "title": "Foldable Aluminum Laptop Cooling Stand",
        "category_slug": "laptops-accessories",
        "condition": "Like New",
        "listing_type": "both",
        "borrowing_fee": 15.0,
        "deposit": 250.0,
        "borrowing_duration_max_days": 14,
        "selling_price": 600.0,
        "negotiable": True,
        "location": "Library Study Hall 3",
        "tags": "laptop stand, aluminum, ergonomic, posture",
        "description": "6-level adjustable height ventilated riser compatible with all 10-15.6 inch laptops. Folds flat into included velvet sleeve."
    },
    {
        "title": "Yamaha F280 Acoustic Folk Guitar with Padded Gig Bag",
        "category_slug": "musical-instruments",
        "condition": "Good",
        "listing_type": "both",
        "borrowing_fee": 60.0,
        "deposit": 1200.0,
        "borrowing_duration_max_days": 7,
        "selling_price": 5200.0,
        "negotiable": True,
        "location": "Music Club Auditorium",
        "tags": "guitar, acoustic, yamaha, music, jam",
        "description": "Natural wood finish acoustic guitar with spruce top and rosewood fretboard. Warm, resonant tone. Strung with D'Addario strings. Includes strap, capo, and picks."
    },
    {
        "title": "Rotring Rapid Pro Technical Drafting Pen (0.5mm)",
        "category_slug": "stationery",
        "condition": "Like New",
        "listing_type": "sell",
        "borrowing_fee": 0.0,
        "deposit": 0.0,
        "borrowing_duration_max_days": 7,
        "selling_price": 750.0,
        "negotiable": False,
        "location": "Architecture Studio Wing",
        "tags": "rotring, drafting, pen, architecture, drawing",
        "description": "Solid matte metal body with knurled grip and cushioning mechanism for precision technical drafting and sketching. In original blister box."
    },
    {
        "title": "Anker 20000mAh PowerCore 20W Fast Power Bank",
        "category_slug": "electronics",
        "condition": "Good",
        "listing_type": "both",
        "borrowing_fee": 25.0,
        "deposit": 500.0,
        "borrowing_duration_max_days": 5,
        "selling_price": 1200.0,
        "negotiable": True,
        "location": "Student Activity Center",
        "tags": "powerbank, anker, fast charge, usb-c, phone",
        "description": "Heavy-duty 20,000mAh dual-port battery pack. Charges an iPhone or Galaxy 4-5 times over. Great for campus hackathons and long study sessions.",
        "image_path": "powerbank.jpg"
    },
    {
        "title": "mobile phone",
        "category_slug": "electronics",
        "condition": "Good",
        "listing_type": "sell",
        "borrowing_fee": 0.0,
        "deposit": 0.0,
        "borrowing_duration_max_days": 7,
        "selling_price": 7500.0,
        "negotiable": True,
        "location": "North Campus Engineering Block",
        "tags": "phone, mobile, smartphone, android, electronics",
        "description": "Good condition mobile phone is available. 64GB storage, crisp AMOLED display, fully functional with original charger.",
        "image_path": "mobile_phone.jpg"
    },
    {
        "title": "Earbuds",
        "category_slug": "electronics",
        "condition": "Good",
        "listing_type": "sell",
        "borrowing_fee": 0.0,
        "deposit": 0.0,
        "borrowing_duration_max_days": 7,
        "selling_price": 1200.0,
        "negotiable": True,
        "location": "Hostel Block A Entrance",
        "tags": "earbuds, audio, wireless, bluetooth, music",
        "description": "Good condition earbuds available. True wireless stereo with magnetic charging case and USB-C fast charging.",
        "image_path": "earbuds.jpg"
    }
]


def seed_database():
    app = create_app('development')
    with app.app_context():
        print("[*] Initializing EasyShare database tables...")
        db.create_all()

        # 1. Seed Categories
        print("[*] Checking categories...")
        cat_map = {}
        for cat_data in DEFAULT_CATEGORIES:
            category = Category.query.filter_by(slug=cat_data["slug"]).first()
            if not category:
                category = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    icon=cat_data["icon"]
                )
                db.session.add(category)
                print(f"   + Added category: {cat_data['name']}")
            cat_map[cat_data["slug"]] = category
        db.session.commit()

        # Refresh map after commit
        for slug in cat_map:
            cat_map[slug] = Category.query.filter_by(slug=slug).first()

        # 2. Seed Administrator User
        admin_user = User.query.filter_by(email="admin@easyshare.local").first()
        if not admin_user:
            print("[*] Creating default Administrator...")
            admin_user = User(
                username="admin",
                email="admin@easyshare.local",
                full_name="System Administrator",
                college_or_community="Campus Admin Office",
                phone="+91 99999 00001",
                contact_preference="in_app",
                role="admin",
                trust_score=100.0
            )
            admin_user.set_password("Admin@123")
            db.session.add(admin_user)
            db.session.flush()

            notice = Notification(
                user_id=admin_user.id,
                title="System Initialized",
                message="EasyShare admin account created. You have full oversight on listings, reports, and users.",
                link="/",
                notification_type="system"
            )
            db.session.add(notice)
            print("   + Created admin: admin@easyshare.local / Admin@123")
        else:
            print("   [OK] Admin user already exists.")

        # 3. Seed Sample Student 1 (Alex)
        student_alex = User.query.filter_by(email="student@easyshare.local").first()
        if not student_alex:
            print("[*] Creating sample Student account: Alex Johnson...")
            student_alex = User(
                username="alex_student",
                email="student@easyshare.local",
                full_name="Alex Johnson",
                college_or_community="North Campus Engineering",
                phone="+91 98765 43210",
                contact_preference="in_app",
                role="user",
                trust_score=98.5
            )
            student_alex.set_password("Student@123")
            db.session.add(student_alex)
            db.session.flush()

            notice = Notification(
                user_id=student_alex.id,
                title="Welcome to EasyShare!",
                message="Your student profile is active. Check out items to borrow or list your own reusable gear.",
                link="/",
                notification_type="system"
            )
            db.session.add(notice)
            print("   + Created student: student@easyshare.local / Student@123")
        else:
            print("   [OK] Student Alex already exists.")

        # 4. Seed Sample Student 2 (Priya)
        student_priya = User.query.filter_by(email="priya@easyshare.local").first()
        if not student_priya:
            print("[*] Creating sample Student account: Priya Sharma...")
            student_priya = User(
                username="priya_sharma",
                email="priya@easyshare.local",
                full_name="Priya Sharma",
                college_or_community="Science & Biotechnology Block",
                phone="+91 98111 22334",
                contact_preference="in_app",
                role="user",
                trust_score=99.0
            )
            student_priya.set_password("Student@123")
            db.session.add(student_priya)
            db.session.flush()

            notice = Notification(
                user_id=student_priya.id,
                title="Welcome to EasyShare!",
                message="Your student profile is active. Start sharing and reusing campus gear.",
                link="/",
                notification_type="system"
            )
            db.session.add(notice)
            print("   + Created student: priya@easyshare.local / Student@123")
        else:
            print("   [OK] Student Priya already exists.")

        db.session.commit()

        # 5. Seed Diverse Sample Items and Attach Images
        print("[*] Seeding sample campus listings and images...")
        students = [student_alex, student_priya]
        for i, item_data in enumerate(SAMPLE_LISTINGS):
            item = Item.query.filter_by(title=item_data["title"]).first()
            if not item:
                owner = students[i % len(students)]
                category = cat_map.get(item_data["category_slug"])
                if category:
                    item = Item(
                        owner_id=owner.id,
                        title=item_data["title"],
                        category_id=category.id,
                        description=item_data["description"],
                        condition=item_data["condition"],
                        listing_type=item_data["listing_type"],
                        borrowing_fee=item_data["borrowing_fee"],
                        deposit=item_data["deposit"],
                        borrowing_duration_max_days=item_data["borrowing_duration_max_days"],
                        selling_price=item_data["selling_price"],
                        negotiable=item_data["negotiable"],
                        location=item_data["location"],
                        tags=item_data["tags"],
                        availability_status="available",
                        sale_status="available",
                        views_count=(i + 1) * 7
                    )
                    db.session.add(item)
                    db.session.flush()
                    print(f"   + Added listing: '{item.title}' ({item.listing_type})")

            # Check if item needs an image
            if item and not item.images:
                img_name = item_data.get("image_path") or PRODUCT_IMAGE_MAP.get(item.title)
                if img_name:
                    image_record = ItemImage(
                        item_id=item.id,
                        image_path=img_name,
                        is_primary=True
                    )
                    db.session.add(image_record)
                    print(f"   + Attached image '{img_name}' to '{item.title}'")

        # 6. Ensure ALL existing database items have suitable product images
        for db_item in Item.query.all():
            if not db_item.images:
                matched_img = None
                for key, img_name in PRODUCT_IMAGE_MAP.items():
                    if key.lower() in db_item.title.lower() or db_item.title.lower() in key.lower():
                        matched_img = img_name
                        break
                if not matched_img:
                    t_lower = db_item.title.lower()
                    if 'phone' in t_lower or 'mobile' in t_lower:
                        matched_img = 'mobile_phone.jpg'
                    elif 'earbud' in t_lower or 'audio' in t_lower:
                        matched_img = 'earbuds.jpg'
                    elif 'calc' in t_lower:
                        matched_img = 'ti84_ce_calc.jpg'
                    elif 'math' in t_lower:
                        matched_img = 'math_grewal.jpg'
                    elif 'chem' in t_lower:
                        matched_img = 'bruice_organic_chem.jpg'
                    elif 'physic' in t_lower:
                        matched_img = 'hc_verma_physics.jpg'
                    elif 'racket' in t_lower or 'badminton' in t_lower:
                        matched_img = 'badminton_racket.jpg'
                    elif 'ball' in t_lower or 'basket' in t_lower:
                        matched_img = 'basketball.jpg'
                    elif 'mouse' in t_lower:
                        matched_img = 'mouse.jpg'
                    elif 'stand' in t_lower:
                        matched_img = 'laptop_stand.jpg'
                    elif 'guitar' in t_lower:
                        matched_img = 'acoustic_guitar.jpg'
                    elif 'pen' in t_lower or 'draft' in t_lower:
                        matched_img = 'drafting_pen.jpg'
                    elif 'power' in t_lower or 'bank' in t_lower:
                        matched_img = 'powerbank.jpg'
                    elif 'coat' in t_lower or 'goggle' in t_lower:
                        matched_img = 'lab_coat_goggles.jpg'
                    elif 'meter' in t_lower or 'probe' in t_lower:
                        matched_img = 'multimeter.jpg'

                if matched_img:
                    image_record = ItemImage(
                        item_id=db_item.id,
                        image_path=matched_img,
                        is_primary=True
                    )
                    db.session.add(image_record)
                    print(f"   + Attached image '{matched_img}' to item #{db_item.id}: '{db_item.title}'")

        db.session.commit()

        print("[OK] Database seeding complete! All sample items and accounts are ready.")


if __name__ == '__main__':
    seed_database()

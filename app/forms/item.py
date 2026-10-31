from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SelectChoice,
    DecimalField,
    IntegerField,
    BooleanField,
    DateField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError
)
from datetime import date


class ItemForm(FlaskForm):
    title = StringField(
        'Item Title',
        validators=[
            DataRequired(message="Item title is required."),
            Length(min=3, max=150, message="Title must be between 3 and 150 characters.")
        ],
        render_kw={"placeholder": "e.g. TI-84 Plus CE Graphing Calculator"}
    )
    category_id = SelectField(
        'Category',
        coerce=int,
        validators=[DataRequired(message="Please select a category.")]
    )
    description = TextAreaField(
        'Item Description',
        validators=[
            DataRequired(message="Please provide a clear description of the item."),
            Length(min=10, max=2500, message="Description must be between 10 and 2500 characters.")
        ],
        render_kw={"rows": 4, "placeholder": "Describe condition, edition, accessories included, pickup availability..."}
    )
    condition = SelectField(
        'Item Condition',
        choices=[
            SelectChoice('New', 'New (Unused / In original packaging)'),
            SelectChoice('Like New', 'Like New (Barely used, pristine condition)'),
            SelectChoice('Good', 'Good (Minor cosmetic wear, fully functional)'),
            SelectChoice('Fair', 'Fair (Noticeable wear, functions properly)'),
            SelectChoice('Poor', 'Poor (Heavy wear, functional with flaws)')
        ],
        default='Good'
    )
    listing_type = SelectField(
        'Listing Type',
        choices=[
            SelectChoice('both', 'Both (Available to Borrow & for Secondhand Sale)'),
            SelectChoice('borrow', 'Borrow Only (Lend temporarily to peers)'),
            SelectChoice('sell', 'Sell Only (Permanent secondhand purchase)')
        ],
        default='both'
    )

    # Borrow Settings
    borrowing_fee = DecimalField(
        'Daily Rental Fee (₹)',
        places=2,
        default=0.0,
        validators=[Optional(), NumberRange(min=0, message="Fee cannot be negative.")],
        render_kw={"placeholder": "0.00 (Enter 0 for free borrowing)"}
    )
    deposit = DecimalField(
        'Refundable Security Deposit (₹)',
        places=2,
        default=0.0,
        validators=[Optional(), NumberRange(min=0, message="Deposit cannot be negative.")],
        render_kw={"placeholder": "0.00 (Optional safety deposit)"}
    )
    borrowing_duration_max_days = IntegerField(
        'Maximum Borrowing Duration (Days)',
        default=7,
        validators=[Optional(), NumberRange(min=1, max=90, message="Duration must be between 1 and 90 days.")],
        render_kw={"placeholder": "7"}
    )
    borrowing_rules = TextAreaField(
        'Borrowing Rules / Expectations (Optional)',
        validators=[Optional(), Length(max=1000)],
        render_kw={"rows": 2, "placeholder": "e.g. Please do not highlight pages; return with full battery."}
    )

    # Sale Settings
    selling_price = DecimalField(
        'Selling Price (₹)',
        places=2,
        validators=[Optional(), NumberRange(min=0, message="Selling price cannot be negative.")],
        render_kw={"placeholder": "e.g. 1500.00"}
    )
    negotiable = BooleanField('Price is open to offers / negotiation', default=True)

    # General
    location = StringField(
        'Pickup Location on Campus',
        validators=[
            DataRequired(message="Pickup location is required."),
            Length(min=2, max=150)
        ],
        default='Campus Central Library',
        render_kw={"placeholder": "e.g. Main Library, North Campus Engineering, Hostel Block B"}
    )
    tags = StringField(
        'Tags (Keywords separated by commas)',
        validators=[Optional(), Length(max=255)],
        render_kw={"placeholder": "e.g. math, engineering, exam, TI84"}
    )
    image = FileField(
        'Item Photo',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (.jpg, .jpeg, .png, .webp)')
        ]
    )
    submit = SubmitField('Publish Listing')

    def validate_image(self, field):
        if field.data and hasattr(field.data, 'filename') and field.data.filename:
            filename = field.data.filename.lower().strip()
            allowed = {'jpg', 'jpeg', 'png', 'webp'}
            if '.' not in filename or filename.rsplit('.', 1)[1] not in allowed:
                raise ValidationError("Allowed image formats: JPG, JPEG, PNG, WEBP.")
            
            try:
                field.data.seek(0, 2)
                size = field.data.tell()
                field.data.seek(0)
                if size > 16 * 1024 * 1024:
                    raise ValidationError("Image file size must be less than 16 MB.")
                if size == 0:
                    raise ValidationError("Uploaded image file is empty.")
            except Exception:
                field.data.seek(0)

    def validate(self, extra_validators=None):
        initial_validation = super().validate(extra_validators=extra_validators)
        if not initial_validation:
            return False

        # Validate that if listing includes sale, selling price is set
        if self.listing_type.data in ('sell', 'both'):
            if self.selling_price.data is None or self.selling_price.data <= 0:
                self.selling_price.errors.append("Selling price is required for items available for sale.")
                return False

        return True


class BorrowRequestForm(FlaskForm):
    start_date = DateField(
        'Start Date',
        validators=[DataRequired(message="Start date is required.")],
        default=date.today
    )
    end_date = DateField(
        'End Date',
        validators=[DataRequired(message="End date is required.")],
        default=date.today
    )
    notes = TextAreaField(
        'Message to Lender (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 3, "placeholder": "Introduce yourself, explain when you plan to pick up, and your purpose..."}
    )
    submit = SubmitField('Send Borrow Request')

    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data:
            if end_date.data < self.start_date.data:
                raise ValidationError("End date cannot be earlier than start date.")
            if self.start_date.data < date.today():
                raise ValidationError("Start date cannot be in the past.")


class PurchaseRequestForm(FlaskForm):
    proposed_price = DecimalField(
        'Offered Purchase Price (₹)',
        places=2,
        validators=[
            DataRequired(message="Please specify your proposed price."),
            NumberRange(min=1, message="Price must be greater than 0.")
        ]
    )
    message = TextAreaField(
        'Message to Seller (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 3, "placeholder": "Confirm preferred pickup time/place or payment preference..."}
    )
    submit = SubmitField('Send Purchase Request')


class OfferForm(FlaskForm):
    offer_amount = DecimalField(
        'Your Offer Amount (₹)',
        places=2,
        validators=[
            DataRequired(message="Offer amount is required."),
            NumberRange(min=1, message="Offer must be greater than 0.")
        ]
    )
    message = TextAreaField(
        'Note with Offer (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 2, "placeholder": "Why this offer? (e.g. Ready for immediate cash pickup today)"}
    )
    submit = SubmitField('Submit Offer')

import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    SelectChoice,
    TextAreaField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    Optional,
    Regexp
)
from app.models.user import User


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=30, message="Username must be between 3 and 30 characters."),
            Regexp(r'^[a-zA-Z0-9_.]+$', message="Username can only contain letters, numbers, dots, and underscores.")
        ],
        render_kw={"placeholder": "e.g. alex_student"}
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email address.")
        ],
        render_kw={"placeholder": "name@campus.edu or your@email.com"}
    )
    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message="Full name is required."),
            Length(min=2, max=100, message="Full name must be between 2 and 100 characters.")
        ],
        render_kw={"placeholder": "e.g. Alex Johnson"}
    )
    college_or_community = StringField(
        'College / Campus / Community',
        validators=[
            DataRequired(message="Please specify your college or community."),
            Length(min=2, max=120)
        ],
        default='Main Campus',
        render_kw={"placeholder": "e.g. North Campus, Engineering Block"}
    )
    phone = StringField(
        'Phone Number (Optional)',
        validators=[
            Optional(),
            Length(max=20, message="Phone number is too long.")
        ],
        render_kw={"placeholder": "e.g. +91 98765 43210"}
    )
    contact_preference = SelectField(
        'Preferred Contact Method',
        choices=[
            SelectChoice('in_app', 'In-App Notifications (Recommended)'),
            SelectChoice('email', 'Email Notifications'),
            SelectChoice('phone', 'Direct Phone / WhatsApp')
        ],
        default='in_app'
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, max=128, message="Password must be at least 6 characters.")
        ],
        render_kw={"placeholder": "At least 6 characters"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ],
        render_kw={"placeholder": "Re-enter password"}
    )
    terms = BooleanField(
        'I agree to the EasyShare Community Honor Code & Terms of Use',
        validators=[DataRequired(message="You must agree to the community rules to register.")]
    )
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.strip().lower()).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('An account with this email address already exists.')


class LoginForm(FlaskForm):
    login_identifier = StringField(
        'Username or Email',
        validators=[DataRequired(message="Please enter your username or email.")],
        render_kw={"placeholder": "Username or email address"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Please enter your password.")],
        render_kw={"placeholder": "Enter your password"}
    )
    remember_me = BooleanField('Remember me on this device')
    submit = SubmitField('Sign In')


class RequestResetForm(FlaskForm):
    email = StringField(
        'Registered Email Address',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email address.")
        ],
        render_kw={"placeholder": "Enter your registered email"}
    )
    submit = SubmitField('Send Password Reset Link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message="New password is required."),
            Length(min=6, max=128, message="Password must be at least 6 characters.")
        ],
        render_kw={"placeholder": "Enter new password"}
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo('password', message="Passwords must match.")
        ],
        render_kw={"placeholder": "Re-enter new password"}
    )
    submit = SubmitField('Reset Password')


class ProfileEditForm(FlaskForm):
    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message="Full name is required."),
            Length(min=2, max=100)
        ]
    )
    college_or_community = StringField(
        'College / Campus / Community',
        validators=[
            DataRequired(message="College or community is required."),
            Length(min=2, max=120)
        ]
    )
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Length(max=20)
        ]
    )
    contact_preference = SelectField(
        'Preferred Contact Method',
        choices=[
            SelectChoice('in_app', 'In-App Notifications'),
            SelectChoice('email', 'Email Notifications'),
            SelectChoice('phone', 'Direct Phone / WhatsApp')
        ]
    )
    profile_image = FileField(
        'Profile Picture',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (.jpg, .jpeg, .png, .webp)')
        ]
    )
    submit = SubmitField('Save Profile Changes')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired(message="Please enter your current password.")]
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message="Please enter a new password."),
            Length(min=6, max=128, message="Password must be at least 6 characters.")
        ]
    )
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo('new_password', message="New passwords must match.")
        ]
    )
    submit = SubmitField('Change Password')

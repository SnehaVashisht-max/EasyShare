from urllib.parse import urlparse
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models.user import User
from app.models.interaction import Notification
from app.forms.auth import (
    RegistrationForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    ProfileEditForm,
    ChangePasswordForm
)
from app.utils.helpers import save_uploaded_image

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def is_safe_redirect_url(target):
    """Ensure redirect URL is local to prevent open redirect vulnerabilities."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('', 'http', 'https') and (test_url.netloc == '' or test_url.netloc == ref_url.netloc)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip().lower(),
            email=form.email.data.strip().lower(),
            full_name=form.full_name.data.strip(),
            college_or_community=form.college_or_community.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            contact_preference=form.contact_preference.data,
            role='user',
            trust_score=current_app.config.get('INITIAL_TRUST_SCORE', 100.0)
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # Get user.id for notification

        # Create welcome notification
        welcome_notice = Notification(
            user_id=user.id,
            title="Welcome to EasyShare!",
            message="Thank you for joining our campus community. Start by exploring items to borrow or listing items you no longer need.",
            link=url_for('main.index'),
            notification_type='system'
        )
        db.session.add(welcome_notice)
        db.session.commit()

        flash("Account created successfully! You can now sign in with your credentials.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title="Create an Account")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.login_identifier.data.strip().lower()
        # Allow login via username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact support or an administrator.", "danger")
                return render_template('auth/login.html', form=form, title="Sign In")

            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.full_name}!", "success")

            next_page = request.args.get('next')
            if next_page and is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash("Invalid email/username or password. Please try again.", "danger")

    return render_template('auth/login.html', form=form, title="Sign In")


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("You have been successfully signed out.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RequestResetForm()
    simulated_link = None

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            token = user.get_reset_token()
            reset_url = url_for('auth.reset_token', token=token, _external=True)
            # In development/local mode, provide link directly on page for seamless verification
            simulated_link = reset_url
            current_app.logger.info(f"Password reset link for {user.email}: {reset_url}")
            flash(f"Password reset link generated for {user.email}.", "info")
        else:
            flash("If that email exists in our system, a password reset link has been generated.", "info")

    return render_template('auth/reset_request.html', form=form, title="Reset Password", simulated_link=simulated_link)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired reset link. Please request a new one.", "warning")
        return redirect(url_for('auth.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Your password has been successfully updated! You can now sign in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form, title="Enter New Password")


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileEditForm(obj=current_user)
    password_form = ChangePasswordForm()

    if form.validate_on_submit() and 'submit_profile' in request.form:
        current_user.full_name = form.full_name.data.strip()
        current_user.college_or_community = form.college_or_community.data.strip()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        current_user.contact_preference = form.contact_preference.data

        # Handle profile image upload
        if form.profile_image.data:
            filename = save_uploaded_image(
                form.profile_image.data,
                target_folder=current_app.config['PROFILE_UPLOAD_FOLDER'],
                max_size=(400, 400)
            )
            if filename:
                current_user.profile_image = filename

        current_user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Your profile has been updated successfully!", "success")
        return redirect(url_for('auth.profile'))

    return render_template(
        'auth/profile.html',
        form=form,
        password_form=password_form,
        title=f"{current_user.full_name} - Profile"
    )


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    password_form = ChangePasswordForm()
    if password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash("Incorrect current password. Please try again.", "danger")
        else:
            current_user.set_password(password_form.new_password.data)
            current_user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            flash("Your password has been changed successfully!", "success")
    else:
        for field, errors in password_form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", "danger")

    return redirect(url_for('auth.profile'))

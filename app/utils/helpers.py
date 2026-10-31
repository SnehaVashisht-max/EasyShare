import os
import uuid
from functools import wraps
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
from flask import current_app, abort, flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has an allowed extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp'})


def save_uploaded_image(file_storage, target_folder: Path, max_size=(900, 700)) -> str:
    """
    Safely validate, process, resize, and save an uploaded image.
    Generates a unique collision-resistant filename and saves as jpg, png, or webp.
    Returns the filename if successful, or None if invalid.
    """
    if not file_storage or not getattr(file_storage, 'filename', None):
        return None

    filename = file_storage.filename.strip()
    if not filename or '.' not in filename:
        return None

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in {'jpg', 'jpeg', 'png', 'webp'}:
        return None

    target_folder = Path(target_folder)
    target_folder.mkdir(parents=True, exist_ok=True)

    # Standardize extension (normalize jpeg to jpg)
    save_ext = 'jpg' if ext in ('jpg', 'jpeg') else ext
    unique_filename = f"{uuid.uuid4().hex}.{save_ext}"
    destination = target_folder / unique_filename

    try:
        file_storage.seek(0)
        img = Image.open(file_storage)
        img.verify()  # Check for corruption

        # Re-open stream after verify()
        file_storage.seek(0)
        img = Image.open(file_storage)

        # Handle color modes
        if save_ext == 'jpg':
            if img.mode in ('RGBA', 'LA', 'P'):
                # Composite transparent images onto a clean white background
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                alpha_mask = img.split()[3] if img.mode == 'RGBA' else None
                bg.paste(img, mask=alpha_mask)
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
        elif save_ext == 'png':
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')
        elif save_ext == 'webp':
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')

        # Resize proportionally with high-quality resampling
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save with format-specific optimizations
        if save_ext == 'jpg':
            img.save(destination, format='JPEG', quality=88, optimize=True)
        elif save_ext == 'webp':
            img.save(destination, format='WEBP', quality=88, method=6)
        else:
            img.save(destination, format='PNG', optimize=True)

        return unique_filename
    except Exception as e:
        current_app.logger.error(f"Failed to process and save image '{filename}': {e}")
        return None


def admin_required(f):
    """Decorator to require administrator role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Administrator access required for this action.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def format_currency(value, currency='₹') -> str:
    """Format numeric value as currency."""
    if value is None:
        return f"{currency}0.00"
    try:
        val = float(value)
        return f"{currency}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{currency}{value}"

import os
from pathlib import Path
from flask import Flask, render_template
from flask_login import current_user

from config import config_by_name
from app.extensions import db, login_manager, csrf


def create_app(config_name: str = 'development') -> Flask:
    """Application factory for EasyShare."""
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Ensure required directories exist
    upload_profiles = Path(app.config['PROFILE_UPLOAD_FOLDER'])
    upload_items = Path(app.config['ITEM_UPLOAD_FOLDER'])
    instance_dir = Path(app.root_path).parent / 'instance'

    upload_profiles.mkdir(parents=True, exist_ok=True)
    upload_items.mkdir(parents=True, exist_ok=True)
    instance_dir.mkdir(parents=True, exist_ok=True)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.items import items_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(items_bp)

    # Context processors for templates
    @app.context_processor
    def inject_global_vars():
        unread_count = 0
        if current_user.is_authenticated:
            try:
                unread_count = current_user.unread_notifications_count
            except Exception:
                unread_count = 0
        return {
            'site_name': app.config.get('SITE_NAME', 'EasyShare'),
            'site_tagline': app.config.get('SITE_TAGLINE', 'Borrow. Lend. Sell. Reuse.'),
            'unread_notifications_count': unread_count
        }

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    return app

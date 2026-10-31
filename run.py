import os
from app import create_app
from app.extensions import db
from seed_data import seed_database

env_mode = os.environ.get('FLASK_ENV', 'development')
app = create_app(env_mode)


@app.cli.command("init-db")
def init_db_command():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        print("Initialized database tables.")


@app.cli.command("seed-db")
def seed_db_command():
    """Populate database with default categories, admin, and test users."""
    seed_database()


if __name__ == '__main__':
    # Initialize tables if not already present
    with app.app_context():
        db.create_all()
    print("=======================================================")
    print("  EasyShare / ShareShelf AI Server Starting...")
    print(f"  Mode: {env_mode.capitalize()}")
    print("  Local URL: http://127.0.0.1:5000")
    print("=======================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)

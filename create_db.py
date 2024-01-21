from app import app, db

# Push an application context
with app.app_context():
    db.create_all()

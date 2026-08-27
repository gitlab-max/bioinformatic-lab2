from flask import Flask
from config import Config
from extensions import db, login_manager, mail
from routes.admin import admin


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"

    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.auth import auth
    from routes.main import main
    from routes.admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        # create admin if not exists
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(
                username="admin",
                email="bibimedicin@gmail.com",
                password=generate_password_hash("123456"),
                role="Admin",
                status="Active",
                email_verified=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin created: admin / 123456")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
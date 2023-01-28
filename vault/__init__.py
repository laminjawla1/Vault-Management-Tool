from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from  flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from vault.config import Config


app = Flask(__name__)
db = SQLAlchemy()
bcrypt = Bcrypt()
Login_manager = LoginManager()
Login_manager.login_view = '_users.login'
Login_manager.login_message_category = 'info'
migrate = Migrate(db)
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    Login_manager.init_app(app)
    migrate.init_app(app)
    mail.init_app(app)

    from accounts.routes import _accounts
    from branches.routes import _branches
    from deposits.routes import _deposits
    from main.routes import _main
    from reports.routes import _reports
    from users.routes import _users
    from withdrawals.routes import _withdrawals
    from zones.routes import _zones
    from errors.handlers import _errors


    app.register_blueprint(_accounts)
    app.register_blueprint(_branches)
    app.register_blueprint(_deposits)
    app.register_blueprint(_main)
    app.register_blueprint(_reports)
    app.register_blueprint(_users)
    app.register_blueprint(_withdrawals)
    app.register_blueprint(_zones)
    app.register_blueprint(_errors)

    return app
    
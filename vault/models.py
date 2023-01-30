from vault import db, Login_manager, migrate
from datetime import datetime, timedelta
from flask_login import UserMixin

@Login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    zone = db.Column(db.String(30))
    branch = db.Column(db.String(30))
    is_super_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_supervisor = db.Column(db.Boolean, default=False, nullable=False)
    is_cashier = db.Column(db.Boolean, default=False, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    cash = db.Column(db.Float, nullable=False, default=0.0)
    add_cash = db.Column(db.Float, nullable=False, default=0.0)
    opening_cash = db.Column(db.Float, nullable=False, default=0.0)
    additional_cash = db.Column(db.Float, nullable=False, default=0.0)
    closing_balance = db.Column(db.Float, nullable=False, default=0.0)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    agent_code = db.Column(db.String(20), unique=True, nullable=False)
    reports = db.relationship('MainVault', backref='reporter', lazy=True)
    daily_reports = db.relationship('ZoneVault', backref='reporter', lazy=True)
    withdraws = db.relationship('Withdraw', backref='withdrawer', lazy=True)
    manager = db.relationship('Zone', backref='manager', lazy=True)
    teller = db.relationship('Branch', backref='teller', lazy=True)
    deposits = db.relationship('Deposit', backref='deposit', lazy=True)


# Main Valut
class MainVault(db.Model):
    # User info
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    zone = db.Column(db.String(100))

    opening_cash = db.Column(db.Float, nullable=False)
    additional_cash = db.Column(db.Float, nullable=False)

    # Currencies
    euro = db.Column(db.Integer, nullable=False, default=0)
    us_dollar = db.Column(db.Integer, nullable=False, default=0)
    gbp_pound = db.Column(db.Integer, nullable=False, default=0)
    swiss_krona = db.Column(db.Integer, nullable=False, default=0)
    nor_krona = db.Column(db.Integer, nullable=False, default=0)
    swiss_franck = db.Column(db.Integer, nullable=False, default=0)
    cfa = db.Column(db.Integer, nullable=False, default=0)
    denish_krona = db.Column(db.Integer, nullable=False, default=0)
    cad_dollar = db.Column(db.Integer, nullable=False, default=0)

    # closing
    closing_balance = db.Column(db.Float, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"MainVault('{self.opening_cash}', '{self.date}')"


# Account
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(100), unique=True, nullable=False)
    owner = db.Column(db.String(100))
    balance = db.Column(db.Float, nullable=False, default=0)

    def __repr__(self):
        return f"Account('{self.name}' '{self.balance}')"


# Zone Valut
class ZoneVault(db.Model):
    # User info
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    branch = db.Column(db.String(100))

    opening_cash = db.Column(db.Float, nullable=False)
    additional_cash = db.Column(db.Float, nullable=False)

    # Currencies
    euro = db.Column(db.Integer, nullable=False, default=0)
    us_dollar = db.Column(db.Integer, nullable=False, default=0)
    gbp_pound = db.Column(db.Integer, nullable=False, default=0)
    swiss_krona = db.Column(db.Integer, nullable=False, default=0)
    nor_krona = db.Column(db.Integer, nullable=False, default=0)
    swiss_franck = db.Column(db.Integer, nullable=False, default=0)
    cfa = db.Column(db.Integer, nullable=False, default=0)
    denish_krona = db.Column(db.Integer, nullable=False, default=0)
    cad_dollar = db.Column(db.Integer, nullable=False, default=0)

    # closing
    closing_balance = db.Column(db.Float, nullable=False)
    approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ZoneVault('{self.opening_cash}', '{self.date}')"


# Zone 
class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deposit_type = db.Column(db.String(60), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account = db.Column(db.String(60))
    approved = db.Column(db.Boolean, default=False)
    branch = db.Column(db.Boolean, default=False)
    zone = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __str__(self):
        return f"{self.amount}"


# Zone 
class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __str__(self):
        return f"{self.name}"

# Branch 
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __str__(self):
        return f"{self.name}"


class Withdraw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    account = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Withdraw('{self.amount}', '{self.date}')"


class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

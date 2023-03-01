from vault.models import User, Zone, Branch, Deposit, Account, Movement, MainVault, ZoneVault
from flask import render_template, url_for, redirect, request, abort, Blueprint, current_app, session
from vault import db
from datetime import timedelta
from flask_login import current_user, login_required
from main.utils import gmd
from .utils import get_opening_and_additional, get_todays_withdrawals, get_todays_deposits


_main = Blueprint('_main', __name__)


@_main.before_request
def make_session_permanent():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(minutes=5)

@_main.before_app_first_request
def create_tables():
    try:
        current_app.app_context().push()
        db.create_all()
    except:
        pass

@_main.route("/admin/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)
    account = Account.query.filter_by(name='Main Vault').first()
    opening_cash, additional_cash = get_opening_and_additional(Deposit.query.order_by(Deposit.date.desc()).all())
    users = len(User.query.all())
    zone_cnt = len(Zone.query.all())
    page = request.args.get('page', 1, type=int)
    zones = Zone.query.order_by(Zone.name).paginate(per_page=3, page=page)
    branches = len(Branch.query.all())
    withdrawals, amount = get_todays_withdrawals()
    deposits, deposit_amount = get_todays_deposits()
    reports = len(MainVault.query.all()) + len(ZoneVault.query.all())
    return render_template("dashboard.html", gmd=gmd, account=account, opening_cash=opening_cash, additional_cash=additional_cash,
                             users=users, zone_cnt=zone_cnt, branches=branches, withdrawals=withdrawals, amount=amount, deposits=deposits,
                             deposit_amount=deposit_amount, zones=zones, reports=reports)

@_main.route("/")
@login_required
def home():
    if current_user.is_admin:
        return redirect(url_for('_main.dashboard'))
    else:
        return redirect(url_for('_users.reports'))


@_main.route("/admin/movements")
@login_required
def movements():
    page = request.args.get('page', 1, type=int)
    movements = Movement.query.order_by(Movement.date.desc()).paginate(per_page=10, page=page)
    return render_template("movements.html", movements=movements)


@_main.route("/admin/agents")
@login_required
def agents():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    agents = User.query.order_by(User.first_name).paginate(per_page=10, page=page)
    return render_template("agents.html", agents=agents, gmd=gmd)
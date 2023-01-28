from vault.models import User, Deposit, Account, Movement
from flask import render_template, url_for, redirect, flash, request, abort, Blueprint
from .forms import (CashierDepositForm, CashierUpdateDepositForm, SupervisorDepositForm, 
                        SupervisorUpdateDepositForm, RefundForm)
from flask_mail import Message
from vault import db, mail
from flask_login import current_user, login_required
from main.utils import gmd


_deposits = Blueprint('_deposits', __name__, url_prefix='/deposits')


@_deposits.route("/admin/cashier_deposits")
@login_required
def cashier_deposits():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    deposits = Deposit.query.order_by(Deposit.date.desc()).filter_by(branch=True).paginate(per_page=8, page=page)
    return render_template("cashier_deposits.html", title="Cashier Deposits", deposits=deposits, gmd=gmd)

@_deposits.route("/admin/supervisor_deposits")
@login_required
def supervisor_deposits():
    page = request.args.get('page', 1, type=int)
    deposits = Deposit.query.filter_by(zone=True).order_by(Deposit.date.desc()).paginate(per_page=8, page=page)
    return render_template("supervisor_deposits.html", title="Supervisor Deposits", deposits=deposits, gmd=gmd)

@_deposits.route("/admin/credit_supervisor_account", methods=['GET', 'POST'])
@login_required
def credit_supervisor_account():
    if not current_user.is_admin:
        abort(403)
    deposit_types = ['Opening Cash', 'Additional Cash']
    agents = User.query.filter_by(is_supervisor=True).all()
    supervisors = []
    for supervisor in agents:
        supervisors.append(
            f'{supervisor.agent_code} - {supervisor.zone} - {supervisor.first_name} {supervisor.last_name}')
    form = SupervisorDepositForm()
    form.supervisor.choices = supervisors
    form.deposit_type.choices = deposit_types
    accounts = [account.name for account in Account.query.all()]
    form.account.choices = accounts

    if form.validate_on_submit():
        if not form.deposit_type.data in deposit_types:
            flash("Invalid deposit type")
            return render_template("credit_supervisor_account.html", form= form, legend="Credit Supervisor Account")
        if not form.account.data in accounts:
            flash("Invalid deposit type")
            return render_template("credit_supervisor_account.html", form= form, legend="Credit Supervisor Account")
        account = Account.query.filter_by(name=form.account.data).first()
        if not account:
            flash("Invalid Account", "danger")
            return render_template("credit_supervisor_account.html", form= form, legend="Credit Supervisor Account")

        if account.balance - form.amount.data < 0:
            flash("Insufficient Amount", "danger")
            return render_template("credit_supervisor_account.html", form= form, legend="Credit Supervisor Account")

        user = User.query.filter_by(agent_code=form.supervisor.data[:7]).first()
        if not user:
            flash("Unrecognized Agent")
            return render_template("credit_supervisor_account.html",form= form, legend="Credit Supervisor Account")
        user.closing_balance = 0
        deposit = Deposit(deposit_type=form.deposit_type.data, amount=form.amount.data, account=form.account.data, deposit=user, zone=True)
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Credited {user.username}'s account with {gmd(form.amount.data)}")
        db.session.add(movement)
        db.session.add(deposit)
        db.session.commit()

        flash(f"Supervisor's account credited successfully", "success")
        return redirect(url_for('_zones.zones'))
    return render_template("credit_supervisor_account.html", form=form, legend="Credit Supervisor Account")


@_deposits.route("/supervisor/credit_cashier_account", methods=['GET', 'POST'])
@login_required
def credit_cashier_account():
    if not current_user.is_admin and not current_user.is_supervisor:
        abort(403)
    deposit_types = ['Opening Cash', 'Additional Cash']
    agents = User.query.filter_by(is_cashier=True).all()
    cashiers = []
    for cashier in agents:
        if cashier.zone == current_user.zone:
            cashiers.append(f'{cashier.agent_code} - {cashier.branch} - {cashier.first_name} {cashier.last_name}')
    form = CashierDepositForm()
    form.cashier.choices = cashiers
    form.deposit_type.choices = deposit_types

    if form.validate_on_submit():
        if not form.deposit_type.data in deposit_types:
            flash("Invalid deposit type")
            return render_template("credit_cashier_account.html", form= form, legend="Credit Cashier Account")

        user = User.query.filter_by(agent_code=form.cashier.data[:7]).first()
        if not user:
            flash("Unrecognized Agent")
            return render_template("credit_cashier_account.html",form= form, legend="Credit Cashier Account")

        deposit = Deposit(deposit_type=form.deposit_type.data, amount=form.amount.data, deposit=user, branch=True)
        if deposit.deposit_type == "Opening Cash":
            current_user.cash -= deposit.amount
        else:
            current_user.add_cash -= deposit.amount
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Credited {cashier.username}'s account")
        db.session.add(movement)
        db.session.add(deposit)
        db.session.commit()
        flash(f"Cashier's account credited successfully", "success")
        return redirect(url_for("_users.my_branches"))
    return render_template("credit_cashier_account.html", form=form, legend="Credit Cashier Account")


@_deposits.route("/admin/cashier_deposit/<int:deposit_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_cashier_deposit(deposit_id):
    if not current_user.is_admin:
        abort(403)
    deposit_types = ['Opening Cash', 'Additional Cash']
    agents = User.query.filter_by(is_cashier=True).all()
    cashiers = []
    for cashier in agents:
        cashiers.append(f'{cashier.agent_code} - {cashier.branch} - {cashier.first_name} {cashier.last_name}')
    form = CashierUpdateDepositForm()
    form.cashier.choices = cashiers
    form.deposit_type.choices = deposit_types

    deposit = Deposit.query.get_or_404(deposit_id)

    if form.validate_on_submit():
        if not form.deposit_type.data in deposit_types:
            flash("Invalid deposit type")
            return render_template("credit_cashier_account.html", form= form, 
                        legend="Edit Cashier Deposit")

        user = User.query.filter_by(agent_code=form.cashier.data[:7]).first()
        if not user:
            flash("Unrecognized Agent")
            return render_template("credit_cashier_account.html",form= form, 
                                    legend="Edit Cashier Deposit")

        deposit.deposit = user
        deposit.amount = form.amount.data
        deposit.deposit_type=form.deposit_type.data
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Edited {user.username}'s Deposit")
        db.session.add(movement)
        db.session.commit()
        flash(f"Cashier's account updated successfully", "success")
        return redirect(url_for("_branches.branches"))
    elif request.method == "GET":
        form.cashier.data = deposit.deposit
        form.deposit_type.data = deposit.deposit_type
        form.amount.data = deposit.amount
    return render_template("credit_cashier_account.html", form=form, legend="Edit Cashier Deposit")

@_deposits.route("/admin/supervisor_deposit/<int:deposit_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_supervisor_deposit(deposit_id):
    if not current_user.is_admin:
        abort(403)
    deposit_types = ['Opening Cash', 'Additional Cash']
    agents = User.query.filter_by(is_supervisor=True).all()
    supervisors = []
    for supervisor in agents:
        supervisors.append(f'{supervisor.agent_code} - {supervisor.zone} - {supervisor.first_name} {supervisor.last_name}')
    form = SupervisorUpdateDepositForm()
    form.supervisor.choices = supervisors
    form.deposit_type.choices = deposit_types
    accounts = [account.name for account in Account.query.all()]
    form.account.choices = accounts

    deposit = Deposit.query.get_or_404(deposit_id)

    if form.validate_on_submit():
        if not form.deposit_type.data in deposit_types:
            flash("Invalid deposit type")
            return render_template("credit_supervisor_account.html", form= form, legend="Edit Supervisor Deposit")

        user = User.query.filter_by(agent_code=form.supervisor.data[:7]).first()
        if not user:
            flash("Unrecognized Agent")
            return render_template("credit_supervisor_account.html", form= form, legend="Credit Supervisor Deposit")

        deposit.deposit = user
        deposit.amount = form.amount.data
        deposit.deposit_type=form.deposit_type.data
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Edited {user.username}'s Deposit")
        db.session.add(movement)
        db.session.commit()
        flash(f"Supervisor's account updated successfully", "success")
        return redirect(url_for("_zones.zones"))
    elif request.method == "GET":
        form.supervisor.data = deposit.deposit
        form.deposit_type.data = deposit.deposit_type
        form.amount.data = deposit.amount
    return render_template("credit_supervisor_account.html", form=form, legend="Edit Supervisor Deposit")

@_deposits.route("/admin/cashier/deposit/approve", methods=["GET", "POST"])
@login_required
def approve_cashier_deposit():
    if request.method == "POST":
        id = request.form.get("id")
        deposit = Deposit.query.get_or_404(id)
        deposit.approved = True
        if deposit.deposit_type == "Opening Cash":
            deposit.deposit.cash += deposit.amount
            deposit.deposit.opening_cash += deposit.amount
        else:
            deposit.deposit.additional_cash += deposit.amount
            deposit.deposit.add_cash += deposit.amount
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Approved {deposit.deposit.username}'s deposit of {gmd(deposit.amount)}")
        db.session.add(movement)
        db.session.commit()
        # send to agent
        msg = Message(f"Cashier Deposit Approved", sender='ljawla462@gmail.com', recipients=[deposit.deposit.email])
        msg.body = f"Your account has been credited with an amount of  {gmd(deposit.amount)}"
        mail.send(msg)

        flash("Deposit Approved", "success")
        return redirect(url_for("_deposits.cashier_deposits"))

@_deposits.route("/admin/supervisor/deposit/approve", methods=["GET", "POST"])
@login_required
def approve_supervisor_deposit():
    if request.method == "POST":
        id = request.form.get("id")
        deposit = Deposit.query.get_or_404(id)
        deposit.approved = True
        if deposit.deposit_type == "Opening Cash":
            deposit.deposit.cash += deposit.amount
            deposit.deposit.opening_cash += deposit.amount
        else:
            deposit.deposit.additional_cash += deposit.amount
            deposit.deposit.add_cash += deposit.amount
        

        account = Account.query.filter_by(name=deposit.account).first()
        if not account:
            flash("Invalid Account")
            return render_template("accounts.html", title="Accounts")

        account.balance -= deposit.amount
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Approved {deposit.deposit.username}'s deposit of {gmd(deposit.amount)}")
        db.session.add(movement)
        db.session.commit()
        # send to agent
        msg = Message(
            f"Supervisor Deposit Approved", sender='ljawla462@gmail.com', recipients=[deposit.deposit.email])
        msg.body = f"Your account has been credited with an amount of  {gmd(deposit.amount)}"
        mail.send(msg)
        flash("Deposit Approved", "success")
        return redirect(url_for("_deposits.supervisor_deposits"))


@_deposits.route("/admin/refund_agent", methods=['GET', 'POST'])
@login_required
def refund():
    if not current_user.is_admin:
        abort(403)
    deposit_types = ['Add to Opening Cash',
                     'Add to Additional Cash',
                     'Deduct from Opening Cash',
                     'Deduct from Additional Cash'
    ]

    agents = []
    for agent in User.query.all():
        if agent.is_supervisor:
            agents.append(
                f'{agent.agent_code} - {agent.zone} - {agent.first_name} {agent.last_name}')
        elif agent.is_cashier:
            agents.append(
                f'{agent.agent_code} - {agent.branch} - {agent.first_name} {agent.last_name}')
    form = RefundForm()
    form.agent.choices = agents
    form.deposit_type.choices = deposit_types

    if form.validate_on_submit():
        if not form.deposit_type.data in deposit_types:
            flash("Invalid deposit type")
            return render_template("refund.html", form= form, legend="Refund Agent Account")

        user = User.query.filter_by(agent_code=form.agent.data[:7]).first()
        if not user:
            flash("Unrecognized Agent")
            return render_template("refund.html",form= form, legend="Refund Agent Account")

        if form.deposit_type.data == "Add to Opening Cash":
            user.cash += form.amount.data
        elif form.deposit_type.data == "Add to Additional Cash":
            user.add_cash += form.amount.data
        elif form.deposit_type.data == "Deduct from Opening Cash":
            if user.cash - form.amount.data >= 0:
                user.cash -= form.amount.data
            else:
                flash(f"The amount is not available in the agents account", "danger")
                return redirect(url_for("_deposits.refund"))
        else:
            if user.add_cash - form.amount.data >= 0:
                user.add_cash -= form.amount.data
            else:
                flash(f"The amount is not available in the agents account", "danger")
                return redirect(url_for("_deposits.refund"))

        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Refunded {user.username}'s account with a deposit type of '{form.deposit_type.data}' - {gmd(form.amount.data)}")
        db.session.add(movement)
        db.session.commit()
        # send to agent
        msg = Message(f"Refund Agent Account", sender='ljawla462@gmail.com', recipients=[user.email])
        msg.body = f"Your account has been refunded with an amount of  {gmd(form.amount.data)}"
        mail.send(msg)
        flash(f"Agent's account refunded successfully", "success")
        return redirect(url_for("_main.dashboard"))
    return render_template("refund.html", form=form, legend="Refund Agent Account")


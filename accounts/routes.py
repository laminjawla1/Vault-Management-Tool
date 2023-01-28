from vault.models import Account, Movement
from flask import render_template, url_for, redirect, flash, request, abort, Blueprint, send_from_directory
from .forms import BankAccountForm, BankAccountUpdateForm
from vault import db
from main.utils import gmd
from flask_login import current_user


_accounts = Blueprint('_accounts', __name__, url_prefix='/accounts')

@_accounts.route('/admin/accounts', methods=['GET', 'POST'])
def accounts():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    accounts = Account.query.order_by(Account.date.desc()).paginate(per_page=5, page=page)
    return render_template('vault_accounts.html', accounts=accounts, gmd=gmd, title="Accounts")

@_accounts.route('/admin/accounts/new', methods=['GET', 'POST'])
def create_account():
    if not current_user.is_super_admin:
        flash("Call IT Department to help you with that", "danger")
        return redirect(url_for('_accounts.accounts'))
    
    form = BankAccountForm()
    if form.validate_on_submit():
        account = Account(name=form.name.data, owner=form.owner.data)
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Created a new account - '{form.name.data}'")
        db.session.add(movement)
        db.session.add(account)
        db.session.commit()
        flash("Account created successfully", "success")
        return redirect(url_for('_accounts.accounts'))
    return render_template('create_vault_account.html', form=form, title="Create Account", legend="Create Account")

@_accounts.route('/admin/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
def edit_account(account_id):
    if not current_user.is_super_admin:
        flash("Call IT Department to help you with that", "danger")
        return redirect(url_for('_accounts.accounts'))
    
    form = BankAccountUpdateForm()
    account = Account.query.get_or_404(account_id)
    if form.validate_on_submit():
        account.name = form.name.data
        account.owner = form.owner.data
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Edited the account - '{form.name.data}'")
        db.session.add(movement)
        db.session.commit()
        flash("Account updated successfully", "success")
        return redirect(url_for('_accounts.accounts'))
    elif request.method == "GET":
        form.name.data = account.name
        form.owner.data = account.owner
    return render_template('create_vault_account.html', form=form, title="Edit Account", legend="Edit Account")


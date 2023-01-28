from vault.models import Withdraw, Account, Movement
from flask import render_template, url_for, redirect, flash, request, abort, Blueprint
from .forms import WithdrawForm
from flask_mail import Message
from vault import db, mail
from flask_login import current_user, login_required
from main.utils import gmd


_withdrawals = Blueprint('_withdrawals', __name__, url_prefix='/withdrawals')


@_withdrawals.route("/supervisors/withdraw/", methods=['GET', 'POST'])
@login_required
def withdraw_cash():
    if current_user.is_admin or current_user.is_super_admin or current_user.is_supervisor:
        form = WithdrawForm()
        accounts = [account.name for account in Account.query.all()]
        form.account.choices = accounts
        if form.validate_on_submit():
            if form.account.data not in accounts:
                flash("Select a valid account to deposit")
                return render_template("withdraw_cash.html", title="Withdraw Cash", form=form, legend="Withdraw Cash")
                                
            withdraw = Withdraw(amount=form.amount.data, withdrawer=current_user, account=form.account.data)
            movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Sent a withdrawal request of {gmd(form.amount.data)}")
            db.session.add(movement)
            db.session.add(withdraw)
            db.session.commit()

            # send to admin
            msg = Message(f"Cash Withdrawal Request", sender='ljawla462@gmail.com', recipients=['ljawla@yonnaforexbureau.com'])
            msg.body = f"""{current_user.first_name} {current_user.last_name} sent a withdrawal request of {gmd(form.amount.data)} 
Click on the link below to approve or reject the withdrawal request: {url_for('_withdrawals.withdrawals', _external=True)}"""
            mail.send(msg)

            flash("Withdrawal request sent successfully", "success")
            return redirect(url_for("_withdrawals.withdraws"))
        return render_template("withdraw_cash.html", title="Withdraw Cash", form=form, legend="Withdraw Cash")
    abort(403)

@_withdrawals.route("/supervisors/withdraw/history")
@login_required
def withdraws():
    page = request.args.get('page', 1, type=int)
    withdraw = Withdraw.query.filter_by(user_id=current_user.id).order_by(Withdraw.date.desc()).paginate(per_page=8, page=page)
    return render_template("withdraws.html", title="History", withdraw=withdraw, gmd=gmd)

@_withdrawals.route("/admin/withdrawals")
@login_required
def withdrawals():
    page = request.args.get('page', 1, type=int)
    withdraw = Withdraw.query.order_by(Withdraw.date.desc()).paginate(per_page=8, page=page)
    return render_template("daily_withdrawals.html", title="Withdrawals", withdraw=withdraw, gmd=gmd)



@_withdrawals.route("/admin/withdraw/approve", methods=["GET", "POST"])
@login_required
def approve_withdraw():
    if request.method == "POST":
        id = request.form.get("id")
        withdraw = Withdraw.query.get_or_404(id)
        withdraw.approved = True
        account = Account.query.filter_by(name=withdraw.account).first()
        if account:
            account.balance += withdraw.amount
            movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Approved {withdraw.withdrawer.username}'s withdrawal request of {gmd(withdraw.amount)}")
            db.session.add(movement)
            db.session.commit()
            msg = Message(f"Withdrawal Approved", sender='ljawla462@gmail.com', recipients=['ljawla@yonnaforexbureau.com', withdraw.withdrawer.email])
            msg.body = f"Your withdrawal request has been accepted"
            mail.send(msg)
            flash("Withdrawal Approved 😊", "success")
            return redirect(url_for("_withdrawals.withdrawals"))
        else:
            flash("Invalid Account", "danger")
            return redirect(url_for("_withdrawals.withdrawals"))


@_withdrawals.route("/admin/withdraw/disapprove", methods=["GET", "POST"])
@login_required
def disapprove_withdraw():
    if request.method == "POST":
        id = request.form.get("id")
        withdraw = Withdraw.query.get_or_404(id)
        db.session.delete(withdraw)
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Rejected {withdraw.withdrawer.username}'s withdrawal request of {gmd(withdraw.amount)}")
        db.session.add(movement)
        msg = Message(f"Withdrawal Disapproved", sender='ljawla462@gmail.com', recipients=['ljawla@yonnaforexbureau.com', current_user.email])
        msg.body = f"Your withdrawal request has been rejected"
        mail.send(msg)
        db.session.commit()
        flash("Withdrawal Rejected 😔", "success")
        return redirect(url_for("_withdrawals.withdrawals"))
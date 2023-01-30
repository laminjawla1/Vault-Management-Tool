from vault.models import User, MainVault, Zone, Branch, ZoneVault, Movement
from flask import render_template, url_for, redirect, flash, request, abort, Blueprint
from .forms import (RegistrationForm, LoginForm, UpdateAccountForm, UpdateAccountFormAdmin, RequestResetForm, 
                    ResetPasswordForm)
from vault import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from main.utils import gmd
from .utils import *


_users = Blueprint('_users', __name__, url_prefix='/users')


@_users.route("/admin/agents/new", methods=["GET", "POST"])
# @login_required
def register():
    # if not current_user.is_super_admin:
    #     flash("Call IT Department to help you with that", "danger")
    #     return redirect(url_for('agents'))

    form = RegistrationForm()
    zones = Zone.query.all()
    branches = Branch.query.all()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        while True:
            try:
                user = User(first_name=form.first_name.data, last_name=form.last_name.data, 
                            zone=form.zone.data, branch=form.branch.data, is_super_admin=form.is_super_admin.data, is_admin=form.is_admin.data, is_supervisor=form.is_supervisor.data,
                            is_cashier=form.is_cashier.data,
                            username=form.username.data, email=form.email.data, password=hashed_password, agent_code=generate_agent_code())
                break
            except:
                pass
        # movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
        #                     action=f"Registered the user - '{form.username.data}'")
        # db.session.add(movement)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for("_main.agents"))
    return render_template("register.html", title="Register", form=form, zones=zones, branches=branches)


@_users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!", "success")
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        else:
            if user.is_cashier or user.is_supervisor:
                return redirect(url_for("_users.reports"))
            else:
                return redirect(url_for("_main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Welcome, {user.username}!", "success")
            if next_page:
                return redirect(next_page)
            else:
                if user.is_cashier or user.is_supervisor:
                    return redirect(url_for("_users.reports"))
                else:
                    return redirect(url_for("_main.dashboard"))
        else:
            flash("Login Unsuccessful. Please check username or password. If you've forgotten your password, click on the forgot password link to reset your password", 'danger')
    return render_template("login.html", title="Login", form=form)


@_users.route("/logout")
def logout():
        logout_user()
        flash("You are now logged out!", "success")
        return redirect(url_for("_users.login"))

@_users.route("/me/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account Updated Successfully", "success")
        return redirect(url_for('_users.account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, gmd=gmd)

@_users.route("/admin/user/<int:user_id>/modify", methods=['GET', 'POST'])
@login_required
def user(user_id):
    if not current_user.is_super_admin:
        abort(403)
    form = UpdateAccountFormAdmin()
    user = User.query.get_or_404(user_id)
    zones = Zone.query.all()
    branches = Branch.query.all()
    form.zone.choices = sorted([zone.name for zone in zones])
    form.branch.choices = sorted([branch.name for branch in branches])
    form.zone.choices.append("-")
    form.branch.choices.append("-")

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        # Chech username does not belong to someone else
        sample_user = User.query.filter_by(username=form.username.data).first()
        if sample_user:
            if user.id != sample_user.id:
                flash("The provided username belong to someone.", "danger")
                return render_template('agent.html', title=f"{user.first_name} {user.last_name}", form=form, user=user)
        user.username = form.username.data

        # Chech email does not belong to someone else
        sample_user = User.query.filter_by(email=form.email.data).first()
        if sample_user:
            if user.id != sample_user.id:
                flash("The provided email belong to someone.", "danger")
                return render_template('agent.html', title=f"{user.first_name} {user.last_name}", form=form, user=user)
        user.email = form.email.data

        user.zone = form.zone.data
        user.branch = form.branch.data
        user.is_super_admin = form.is_super_admin.data
        user.is_admin = form.is_admin.data
        user.is_supervisor = form.is_supervisor.data
        user.is_cashier = form.is_cashier.data
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Updated the user - '{form.username.data}'")
        db.session.add(movement)
        db.session.commit()
        flash("Account Updated Successfully", "success")
        return redirect(url_for('_main.agents'))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.username.data = user.username
        form.email.data = user.email
        form.zone.choices = zones
        form.is_super_admin.data = user.is_super_admin
        form.is_admin.data = user.is_admin
        form.is_supervisor.data = user.is_supervisor
    return render_template('agent.html', title=f"{user.first_name} {user.last_name}", form=form, user=user)

@_users.route("/supervisors/report/history")
@login_required
def reports():
    if current_user.is_supervisor or current_user.is_cashier:
        if current_user.is_supervisor:
            page = request.args.get('page', 1, type=int)
            reports = MainVault.query.filter_by(user_id=current_user.id).order_by(MainVault.date.desc()).paginate(per_page=8, page=page)
        else:
            page = request.args.get('page', 1, type=int)
            reports = ZoneVault.query.filter_by(user_id=current_user.id).order_by(ZoneVault.date.desc()).paginate(per_page=8, page=page)
        return render_template("reports.html", title="History", reports=reports, gmd=gmd)
    abort(403)


@_users.route("/admin/daily_supervisor_reports/<string:username>/reports")
@login_required
def supervisor_reports(username):
    if not current_user.is_admin:
        abort(403)

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    reports = MainVault.query.filter_by(user_id=user.id).order_by(MainVault.date.desc()).paginate(per_page=8, page=page)
    return render_template("supervisor_reports.html", title=f"{user.username}'s Reports", reports=reports, 
                            gmd=gmd, reported=f"{user.first_name} {user.last_name}'s Reports", user=user)


@_users.route("/admin/daily_cashier_reports/<string:username>/reports")
@login_required
def cashier_reports(username):
    if not current_user.is_admin:
        abort(403)

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    reports = ZoneVault.query.filter_by(user_id=user.id).order_by(ZoneVault.date.desc()).paginate(per_page=8, page=page)
    return render_template("cashier_reports.html", title=f"{user.username}'s Reports", reports=reports, 
                            gmd=gmd, reported=f"{user.first_name} {user.last_name}'s Reports", user=user)

@_users.route("/admin/user/<int:user_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_super_admin:
        flash("Call IT Department to help you with that", "danger")
        return redirect(url_for('_main.agents'))

    user = User.query.get_or_404(user_id)
    movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Deleted {user.first_name} {user.last_name}")
    db.session.add(movement)
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.first_name} {user.last_name} Deleted!', 'success')
    return redirect(url_for('_main.agents'))

@_users.route("/admin/agents/<username>/reset_password", methods=['GET', 'POST'])
def reset_password(username):
    if not current_user.is_super_admin:
        flash("Call IT department to help you with that", "danger")
        return redirect(url_for('_main.home'))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Unrecognize agent', 'warning')
        return redirect(url_for('_users.user'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password has been updated!', 'success')
        return redirect(url_for('_main.agents'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@_users.route("/supervisor/my_branches")
@login_required
def my_branches():
    if not current_user.is_supervisor:
        abort(403)
    page = request.args.get('page', 1, type=int)
    branches = Branch.query.order_by(Branch.name).paginate(per_page=10, page=page)
    
    return render_template("my_branches.html", branches=branches, gmd=gmd)

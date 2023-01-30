from vault.models import User, Branch, Movement
from flask import render_template, url_for, redirect, flash, request, abort, Blueprint
from .forms import BranchCreationForm, BranchUpdateForm
from vault import db
from main.utils import gmd
from flask_login import current_user, login_required


_branches = Blueprint('_branches', __name__, url_prefix='/branches')

@_branches.route("/admin/branches")
@login_required
def branches():
    if not current_user.is_admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    branches = Branch.query.order_by(Branch.name).paginate(per_page=10, page=page)
    return render_template("branches.html", branches=branches, gmd=gmd)

@_branches.route("/admin/branches/new", methods=["GET", "POST"])
@login_required
def create_branch():
    if not current_user.is_super_admin:
        flash("Call IT Department to help you with that", "danger")
        return redirect(url_for('_main.home'))

    form = BranchCreationForm()
    agents = User.query.filter_by(is_cashier=True).all()

    tellers = []

    for teller in agents:
        tellers.append(
            f"{teller.agent_code} - {teller.first_name} {teller.last_name}")

    tellers.insert(0, "")
    form.teller.choices = sorted(tellers)

    if form.validate_on_submit():
        name = form.name.data
        teller = form.teller.data
             
        if teller:
            user = User.query.filter_by(agent_code=teller[:7]).first()
            if not user:
                flash("Unrecognize Teller")
                return render_template("create_branch.html", form=form, legend="Create Branch", title="Create Branch")
            branch = Branch(name=name, teller=user)
        else:
            branch = Branch(name=name)
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Created the branch - '{form.name.data}'")
        db.session.add(movement)
        db.session.add(branch)
        db.session.commit()
        flash("Branch Created Successfully", "success")
        return redirect(url_for("_branches.branches"))

    return render_template("create_branch.html", form=form, legend="Create Branch", title="Create Branch")

@_branches.route("/admin/branches/<int:branch_id>/edit", methods=["GET", "POST"])
@login_required
def edit_branch(branch_id):
    if not current_user.is_super_admin:
        flash("Call IT Department to help you with that", "danger")
        return redirect(url_for('main.routes.main.home'))
    form = BranchUpdateForm()

    agents = User.query.filter_by(is_cashier=True).all()
    tellers = []

    for teller in agents:
        tellers.append(
            f"{teller.agent_code} - {teller.first_name} {teller.last_name}")

    form.teller.choices = sorted(tellers)
    branch = Branch.query.get_or_404(branch_id)

    if form.validate_on_submit():
        branch.name = form.name.data
        if form.teller.data:
            user = User.query.filter_by(agent_code=form.teller.data[:7]).first()
            if not user:
                flash("Unrecognize Teller")
                return render_template("create_branch.html", legend="Edit Branch",  title="Edit Branch", form=form)
            branch.teller = user
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Edited the branch - '{form.name.data}'")
        db.session.add(movement)
        db.session.commit()
        flash('Branch Updated', 'success')
        return redirect(url_for('_branches.branches'))

    elif request.method == 'GET':
        form.name.data = branch.name
    return render_template("create_branch.html", legend="Edit Branch", title="Edit Branch", form=form)

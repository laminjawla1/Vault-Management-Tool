from vault.models import User, Zone, Movement
from flask import render_template, url_for, redirect, flash, request, abort, Blueprint
from .forms import ZoneCreationForm, ZoneUpdateForm
from vault import db
from flask_login import current_user, login_required
from main.utils import gmd


_zones = Blueprint('_zones', __name__, url_prefix='/zones')

@_zones.route("/admin/zones/<int:zone_id>/edit", methods=["GET", "POST"])
@login_required
def edit_zone(zone_id):
    if not current_user.is_super_admin:
        flash("Call IT Department to help you with that", "danger")
        return redirect(url_for('_main.home'))

    form = ZoneUpdateForm()

    agents = User.query.filter_by(is_supervisor=True).all()
    supervisors = []

    for supervisor in agents:
        supervisors.append(
            f"{supervisor.agent_code} - {supervisor.first_name} {supervisor.last_name}")

    supervisors.insert(0, "")
    form.supervisor.choices = sorted(supervisors)
    zone = Zone.query.get_or_404(zone_id)

    if form.validate_on_submit():
        zone.name = form.name.data
        if form.supervisor.data:
            user = User.query.filter_by(agent_code=form.supervisor.data[:7]).first()
            if not user:
                flash("Unrecognize Supervisor")
                return render_template("create_zone.html", legend="Edit Zone", title="Edit Zone", form=form)
            zone.manager = user
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Edited the zone - '{form.name.data}'")
        db.session.add(movement)
        db.session.commit()
        flash('Zone Updated', 'success')
        return redirect(url_for('_zones.zones'))

    elif request.method == 'GET':
        form.name.data = zone.name
    return render_template("create_zone.html", legend="Edit Zone", title="Edit Zone", form=form)


@_zones.route("/admin/zones/new", methods=["GET", "POST"])
@login_required
def create_zone():
    if not current_user.is_super_admin:
        flash("Call IT Department to help you with that", "danger")
        return redirect(url_for('_main.home'))

    form = ZoneCreationForm()
    agents = User.query.filter_by(is_supervisor=True).all()

    supervisors = []

    for supervisor in agents:
        supervisors.append(
            f"{supervisor.agent_code} - {supervisor.first_name} {supervisor.last_name}")

    supervisors.insert(0, "")
    form.supervisor.choices = sorted(supervisors)

    if form.validate_on_submit():
        name = form.name.data
        supervisor = form.supervisor.data
             
        if supervisor:
            user = User.query.filter_by(agent_code=supervisor[:7]).first()
            if not user:
                flash("Unrecognize Supervisor")
                return render_template("create_zone.html", form=form, legend="Create Zone", title="Create Zone")
            zone = Zone(name=name, manager=user)
        else:
            zone = Zone(name=name)
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Created the zone - '{form.name.data}'")
        db.session.add(movement)
        db.session.add(zone)
        db.session.commit()
        flash("Zone Created Successfully", "success")
        return redirect(url_for("_zones.zones"))
    return render_template("create_zone.html", form=form, legend="Create Zone", title="Create Zone")

@_zones.route("/admin/zones")
@login_required
def zones():
    if not current_user.is_admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    zones = Zone.query.order_by(Zone.name).paginate(per_page=5, page=page)
    return render_template("zones.html", zones=zones, gmd=gmd)
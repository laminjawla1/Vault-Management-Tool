from vault.models import MainVault, ZoneVault, Account, Movement, Deposit, Withdraw
from flask import render_template, url_for, redirect, flash, request, abort, Blueprint, send_from_directory, current_app, Response
from .forms import DailyReportForm, DailyReportFormUpdate
from flask_mail import Message
from vault import db, mail
from flask_login import current_user, login_required
from main.utils import gmd
from datetime import datetime
import csv
import io


_reports = Blueprint('_reports', __name__, url_prefix='/reports')

@_reports.route("/supervisors/report/new", methods=['GET', 'POST'])
@login_required
def send_report():
    form = DailyReportForm()
    if form.validate_on_submit():
        report = MainVault(zone=current_user.zone, opening_cash=float(form.opening_cash.data),
        additional_cash=float(form.additional_cash.data), euro=int(form.euro.data), 
        us_dollar=int(form.us_dollar.data), gbp_pound=int(form.gbp_pound.data), 
        cfa=int(form.cfa.data), swiss_krona=int(form.swiss_krona.data), nor_krona=int(form.nor_krona.data), swiss_franck=int(form.swiss_franck.data), denish_krona=int(form.denish_krona.data), 
        cad_dollar=int(form.cad_dollar.data), closing_balance=float(form.closing_balance.data),
        reporter=current_user, approved=False)
        current_user.closing_balance = form.closing_balance.data
        db.session.add(report)
        db.session.commit()

        msg = Message(f"Daily Report", sender='ljawla462@gmail.com', recipients=['ljawla@yonnaforexbureau.com'])
        msg.body = f"{current_user.first_name} {current_user.last_name} sent his daily report"
        mail.send(msg)
        flash("Report sent successfully", "success")
        return redirect(url_for("_users.reports"))
    return render_template("send_report.html", title="Send Report", form=form, legend="Send Report")

@_reports.route("/cashiers/report/new", methods=['GET', 'POST'])
@login_required
def send_report_to_supervisor():
    form = DailyReportForm()
    if form.validate_on_submit():
        if form.opening_cash.data  != current_user.cash:
            flash("Unable to send report. Make sure your opening balance is correct", "danger")
            return render_template("send_report.html", title="Send Report", form=form, legend="Send Report")

        if form.additional_cash.data  != current_user.add_cash:
            flash("Unable to send report. Make sure your additional cash is correct", "danger")
            return render_template("send_report.html", title="Send Report", form=form, legend="Send Report")

        report = ZoneVault(branch=current_user.branch, opening_cash=float(form.opening_cash.data),
        additional_cash=float(form.additional_cash.data), euro=int(form.euro.data), 
        us_dollar=int(form.us_dollar.data), gbp_pound=int(form.gbp_pound.data), 
        cfa=int(form.cfa.data), swiss_krona=int(form.swiss_krona.data), nor_krona=int(form.nor_krona.data), swiss_franck=int(form.swiss_franck.data), denish_krona=int(form.denish_krona.data), 
        cad_dollar=int(form.cad_dollar.data), closing_balance=float(form.closing_balance.data),
        reporter=current_user, approved=False)

        current_user.closing_balance = form.closing_balance.data

        db.session.add(report)
        db.session.commit()

        msg = Message(f"Daily Report", sender='ljawla462@gmail.com', recipients=['ljawla@yonnaforexbureau.com'])
        msg.body = f"{current_user.first_name} {current_user.last_name} sent his daily report"
        mail.send(msg)

        flash("Report sent successfully", "success")
        return redirect(url_for("_users.reports"))
    return render_template("send_report.html", title="Send Report", form=form, legend="Send Report")

@_reports.route("/admin/daily_supervisor_reports")
@login_required
def daily_reports():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    reports = MainVault.query.order_by(MainVault.date.desc()).paginate(per_page=8, page=page)
    return render_template("daily_reports.html", title="Daily Reports", reports=reports, gmd=gmd, reported="Daily supervisor Reports")



@_reports.route("/admin/daily_cashier_reports")
@login_required
def daily_cashier_reports():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    reports = ZoneVault.query.order_by(ZoneVault.date.desc()).paginate(per_page=8, page=page)
    return render_template("daily_cashier_reports.html", title="Daily Reports", reports=reports, gmd=gmd, reported="Daily Cashier Reports")

@_reports.route("/admin/report/approve", methods=["GET", "POST"])
@login_required
def approve_report():
    if request.method == "POST":
        id = request.form.get("id")
        report = MainVault.query.get_or_404(id)
        report.approved = True
        report.reporter.cash = 0
        report.reporter.add_cash = 0
        report.reporter.opening_cash = 0
        report.reporter.additional_cash = 0
        account = Account.query.filter_by(name='Main Vault').first()
        if not account:
            flash("Main Vault account not ready", "danger")
            return redirect(url_for("daily_reports"))
        account.balance += report.closing_balance
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Approved {report.reporter.username}'s report")
        db.session.add(movement)
        db.session.commit()
        flash("Report Approved", "success")
        return redirect(url_for("_reports.daily_reports"))

@_reports.route("/admin/cashier/report/approve", methods=["GET", "POST"])
@login_required
def approve_cashier_report():
    if request.method == "POST":
        id = request.form.get("id")
        report = ZoneVault.query.get_or_404(id)
        report.approved = True
        report.reporter.cash = 0
        report.reporter.add_cash = 0
        db.session.commit()
        flash("Report Approved", "success")
        return redirect(url_for("_reports.daily_cashier_reports"))


@_reports.route("/admin/report/<int:report_id>/delete", methods=["GET", "POST"])
@login_required
def delete_report(report_id):
    if not current_user.is_admin:
        abort(403)

    report = MainVault.query.get_or_404(report_id)
    movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Deleted {report.reporter.username}'s report")
    db.session.add(movement)
    db.session.delete(report)
    db.session.commit()
    flash("Report Deleted", "success")
    return redirect(url_for("_reports.daily_reports"))

@_reports.route("/admin/report/<int:report_id>/edit", methods=["GET", "POST"])
@login_required
def edit_report(report_id):
    if not current_user.is_admin:
        abort(403)

    report = MainVault.query.get_or_404(report_id)
    form = DailyReportFormUpdate()

    if form.validate_on_submit():
        report.opening_cash = form.opening_cash.data
        report.additional_cash = form.additional_cash.data
        report.euro = form.euro.data
        report.us_dollar = form.us_dollar.data
        report.gbp_pound = form.gbp_pound.data
        report.cfa = form.cfa.data
        report.closing_balance = form.closing_balance.data
        db.session.commit()
        flash('Report Updated', 'success')
        movement = Movement(agent_code=current_user.agent_code, name=f'{current_user.first_name} {current_user.last_name}',
                            action=f"Updated {report.reporter.username}'s report")
        db.session.add(movement)
        return redirect(url_for('_reports.daily_reports'))

    elif request.method == 'GET':
        form.opening_cash.data = report.opening_cash
        form.additional_cash.data = report.additional_cash
        form.euro.data = report.euro
        form.us_dollar.data = report.us_dollar
        form.gbp_pound.data = report.gbp_pound
        form.cfa.data = report.cfa
        form.closing_balance.data = report.closing_balance
    return render_template("edit_report.html", title="Edit Report", legend="Edit Report", form=form, report=report)

@_reports.route('/admin/cashier/reports/generate')
def generate_cashier_report():
    if not current_user.is_admin:
        abort(403)
    cr = ZoneVault.query.order_by(ZoneVault.date.desc()).all()
    for c in cr:
        if c.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"): 
            flash("No Cashier Reports Available For Export", "danger")
            return redirect(url_for("_main.dashboard"))
        break

    headers  =["ZONE", "BRANCH", "TELLER", "OPENING CASH", "ADDITIONAL CASH", "TOTAL", "CLOSING BALANCE", "EURO", 
               "USD", "GBP", "CFA", "Swiss Krona", "Nor Krona", "Swiss Franck", "Denish Krona", "Cad Dollar", "DATE"]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in cr:
        if r.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"):
            break
        writer.writerow((r.reporter.zone, r.reporter.branch, f'{r.reporter.first_name} {r.reporter.last_name}',
                                r.opening_cash, r.additional_cash, r.opening_cash + r.additional_cash, r.closing_balance,
                                r.euro, r.us_dollar, r.gbp_pound, r.cfa, r.swiss_krona, r.nor_krona, r.swiss_franck, r.denish_krona, 
                                r.cad_dollar, r.date.strftime("%Y-%m-%d")))
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=daily_cashier_reports.csv"})

@_reports.route('/admin/supervisor/reports/generate')
def generate_supervisor_report():
    if not current_user.is_admin:
        abort(403)
    cr = MainVault.query.order_by(MainVault.date.desc()).all()
    for c in cr:
        if c.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"): 
            flash("No Supervisor Reports Available For Export", "danger")
            return redirect(url_for("_main.dashboard"))
        break
    headers  =["ZONE", "SUPERVISOR", "OPENING CASH", "ADDITIONAL CASH", "TOTAL", "CLOSING BALANCE", "EURO", 
               "USD", "GBP", "CFA", "Swiss Krona", "Nor Krona", "Swiss Franck", "Denish Krona", "Cad Dollar", "DATE"]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in cr:
        if r.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"):
            break
        writer.writerow((r.reporter.zone, f'{r.reporter.first_name} {r.reporter.last_name}',
                                r.opening_cash, r.additional_cash, r.opening_cash + r.additional_cash, r.closing_balance,
                                r.euro, r.us_dollar, r.gbp_pound, r.cfa, r.swiss_krona, r.nor_krona, r.swiss_franck, r.denish_krona, 
                                r.cad_dollar, r.date.strftime("%Y-%m-%d")))
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=daily_supervisor_reports.csv"})

@_reports.route('/admin/withdrawal/generate')
def generate_withdrawal_report():
    if not current_user.is_admin:
        abort(403)
    dw = Withdraw.query.order_by(Withdraw.date.desc()).all()
    for c in dw:
        if c.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"): 
            flash("No withdrawal Reports Available For Export", "danger")
            return redirect(url_for("_main.dashboard"))
        break
    headers  =["AGENT CODE", "AGENT FULLNAME", "ZONE", "AMOUNT","STATUS", "DATE"]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for w in dw:
        if w.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"):
            break
        writer.writerow((w.withdrawer.agent_code, f'{w.withdrawer.first_name} {w.withdrawer.last_name}', w.withdrawer.zone,
                          w.amount, w.approved, w.date.strftime("%Y-%m-%d")))
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=daily_withdrawals.csv"})

@_reports.route('/admin/cashier/deposits/generate')
def generate_cashier_deposit_report():
    if not current_user.is_admin:
        abort(403)
    cd = Deposit.query.filter_by(branch=True).order_by(Deposit.date.desc()).all()
    for c in cd:
        if c.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"): 
            flash("No Cashier Deposit Reports Available For Export", "danger")
            return redirect(url_for("_main.dashboard"))
        break
    headers  =["ZONE", "BRANCH", "TELLER", "AMOUNT", "DEPOSIT TYPE", "DATE"]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for d in cd:
        if d.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"):
            break
        writer.writerow((d.deposit.zone, d.deposit.branch, f'{d.deposit.first_name} {d.deposit.last_name}',
                         d.amount, d.deposit_type, d.date.strftime("%Y-%m-%d")))
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=daily_cashier_deposits.csv"})

@_reports.route('/admin/supervisor/deposits/generate')
def generate_supervisor_deposit_report():
    if not current_user.is_admin:
        abort(403)
    cd = Deposit.query.filter_by(zone=True).order_by(Deposit.date.desc()).all()
    for c in cd:
        if c.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"): 
            flash("No Supervisor Deposit Reports Available For Export", "danger")
            return redirect(url_for("_main.dashboard"))
        break
    headers  =["ZONE", "SUPERVISOR", "AMOUNT", "DEPOSIT TYPE", "DATE"]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for d in cd:
        if d.date.strftime("%Y-%m-%d") != datetime.utcnow().strftime("%Y-%m-%d"):
            break
        writer.writerow((d.deposit.zone, f'{d.deposit.first_name} {d.deposit.last_name}', d.amount, d.deposit_type, 
                         d.date.strftime("%Y-%m-%d")))
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=daily_supervisor_deposits.csv"})
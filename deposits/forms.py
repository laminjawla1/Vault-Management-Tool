from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired


class CashierDepositForm(FlaskForm):
    cashier = SelectField('Cashier', choices=[], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    deposit_type = SelectField('Deposit Type', choices=[], validators=[DataRequired()])

    submit = SubmitField('Credit')


class CashierUpdateDepositForm(FlaskForm):
    cashier = SelectField('Cashier', choices=[], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    deposit_type = SelectField('Deposit Type', choices=[], validators=[DataRequired()])

    submit = SubmitField('Update')


class SupervisorDepositForm(FlaskForm):
    supervisor = SelectField('Supervisor', choices=[], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    deposit_type = SelectField('Deposit Type', choices=[], validators=[DataRequired()])
    account = SelectField('From', choices=[], validators=[DataRequired()])

    submit = SubmitField('Credit')


class SupervisorUpdateDepositForm(FlaskForm):
    supervisor = SelectField('Supervisor', choices=[], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    deposit_type = SelectField('Deposit Type', choices=[], validators=[DataRequired()])
    account = SelectField('From', choices=[], validators=[DataRequired()])

    submit = SubmitField('Update')


class RefundForm(FlaskForm):
    agent = SelectField('Agents', choices=[], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    deposit_type = SelectField('Deposit Type', choices=[], validators=[DataRequired()])

    submit = SubmitField('Refund')
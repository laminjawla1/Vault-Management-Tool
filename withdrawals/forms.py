from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired

class WithdrawForm(FlaskForm):
    amount =FloatField('Amount', validators=[DataRequired()])
    account = SelectField('To', choices=[], validators=[DataRequired()])
    submit = SubmitField('Withdraw')
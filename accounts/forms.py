from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from vault.models import Account



class BankAccountForm(FlaskForm):
    name = StringField('Account Name', validators= [DataRequired()])
    owner = StringField('Owner', validators= [DataRequired()])
    submit = SubmitField('Create')

    def validate_name(self, name):

        account = Account.query.filter_by(name=name.data).first()

        if account:
            raise ValidationError('Account name taken. Choose a different one.')

class BankAccountUpdateForm(FlaskForm):
    name = StringField('Account Name', validators= [DataRequired()])
    owner = StringField('Owner', validators= [DataRequired()])
    submit = SubmitField('Update')
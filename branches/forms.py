from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class BranchCreationForm(FlaskForm):
    name = StringField('Branch Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    teller = SelectField('Teller', choices=[])


    submit = SubmitField('Create')


class BranchUpdateForm(FlaskForm):
    name = StringField('Branch Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    teller = SelectField('Teller', choices=[])


    submit = SubmitField('Update')  
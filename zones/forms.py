from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from wtforms.validators import DataRequired, Length

class ZoneCreationForm(FlaskForm):
    name = StringField('Zone Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    supervisor = SelectField('Supervisor', choices=[])


    submit = SubmitField('Create')


class ZoneUpdateForm(FlaskForm):
    name = StringField('Zone Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    supervisor = SelectField('Supervisor', choices=[])


    submit = SubmitField('Update')
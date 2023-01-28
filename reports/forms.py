from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, InputRequired

class DailyReportForm(FlaskForm):
    opening_cash = FloatField('Opening Cash', validators=[DataRequired()])
    additional_cash = FloatField('Additional Cash', validators=[InputRequired("If you were not given an additional cash, enter 0")])

    euro = IntegerField('Euro', default=0)
    us_dollar = IntegerField('US Dollar', default=0)
    gbp_pound = IntegerField('GBP Pound', default=0)
    cfa = IntegerField('CFA', default=0)
    swiss_krona = IntegerField('Swiss Krona', default=0)
    nor_krona = IntegerField('Nor Krona', default=0)
    swiss_franck = IntegerField('Swiss Franck', default=0)
    denish_krona = IntegerField('Denish Krona', default=0)
    cad_dollar = IntegerField('Cad Dollar', default=0)
    
    closing_balance = FloatField('Closing Balance', validators=[DataRequired()])


    submit = SubmitField('Send')

class DailyReportFormUpdate(FlaskForm):
    opening_cash = FloatField('Opening Cash', validators=[DataRequired()])
    additional_cash = FloatField('Additional Cash')

    euro = IntegerField('Euro', default=0)
    us_dollar = IntegerField('US Dollar', default=0)
    gbp_pound = IntegerField('GBP Pound', default=0)
    cfa = IntegerField('CFA', default=0)
    swiss_krona = IntegerField('Swiss Krona', default=0)
    nor_krona = IntegerField('Nor Krona', default=0)
    swiss_franck = IntegerField('Swiss Franck', default=0)
    denish_krona = IntegerField('Denish Krona', default=0)
    cad_dollar = IntegerField('Cad Dollar', default=0)
    
    closing_balance = FloatField('Closing Balance', validators=[DataRequired()])

    submit = SubmitField('Update')

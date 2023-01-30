from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from vault.models import User


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    zone = StringField('Zone')
    branch = StringField('Branch')
    is_super_admin = BooleanField('Super Admin')
    is_admin = BooleanField('Admin')
    is_supervisor = BooleanField('Supervisor')
    is_cashier = BooleanField('Cashier')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), 
                                        EqualTo('password'), Length(min=8, max=16)])
    submit = SubmitField('Add User')  

    def validate_username(self, username):

        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username Taken. Choose a different one.')

    def validate_email(self, email):

        email = User.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('Email Taken. Choose a different one.')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username Taken. Choose a different one.')


    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email Taken. Choose a different one.')


class UpdateAccountFormAdmin(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', 
                            validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    zone = SelectField('Zone', choices=[])
    branch = SelectField('Branch', choices=[])
    is_super_admin = BooleanField('Super Admin')
    is_admin = BooleanField('Admin')
    is_supervisor = BooleanField('Supervisor')
    is_cashier = BooleanField('Cashier')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):

        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError('Request unsuccessful. No account with that email exists.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

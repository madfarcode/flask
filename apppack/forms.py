from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from apppack.models import User


class RegistrationForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

''' Validation of the disponibilities of inputs the user want to use '''
    
def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
        raise ValidationError('That username already exist')
    
def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError('That email already exist')

class UpdateAccountForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Profile picture', validators=[FileAllowed(['jpg'], ['png'])])
    submit = SubmitField('Update')

''' Validation of the disponibilities of inputs the user want to use '''
    
def validate_username(self, username):
    if username.data != current_user.username:
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exist')
    else : 
        raise ValidationError("Your new User name should be different from your current User name")
    
def validate_email(self, email):
    if email.data != current_user.email:
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exist')
    else : 
        raise ValidationError("Your new Email should be different from your current Email")


class LoginForm(FlaskForm):
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me ?')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class RequestRestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired])
    submit = SubmitField('Request Passwor Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Sorry we cannot found any trace of this email in our database")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequierd()])
    confirm_password = PasswordField('ConfirmPassword', validators=[DataRequired(), equalTo('password')])
    submit = SubmitField('Reset Password')
    



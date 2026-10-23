from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models.core import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    role = SelectField('Account Type', choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher / Faculty'),
        ('parent', 'Parent / Guardian')
    ], validators=[DataRequired()])
    
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    
    # Identifier (Admission Number for Student/Parent OR Employee Code for Teacher)
    identifier_code = StringField('Admission No / Employee Code', validators=[DataRequired()])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match!')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please login or use a different email.')
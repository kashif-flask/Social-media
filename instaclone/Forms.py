from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,EqualTo,Email

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')

class RegistrationForm(FlaskForm):
      username=StringField('Username',validators=[DataRequired(),Length(min=4,max=20)])
      email=StringField('Email',validators=[DataRequired(),Email()])
      name=StringField('Name',validators=[DataRequired(),Length(min=4,max=24)])
      password=PasswordField('Password',validators=[DataRequired()])
      confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
      submit=SubmitField('Register')
class Verify(FlaskForm):
      email=StringField('Email',validators=[DataRequired(),Email()])
      submit=SubmitField('Verify')


class Change(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Change Password')

class Search(FlaskForm):
    search=StringField('Search',validators=[DataRequired()])
    submit=SubmitField('Search')

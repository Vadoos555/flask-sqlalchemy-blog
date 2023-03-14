from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Enter')


class RegisterForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_new_user(self):
        username = self.username.data
        email = self.email.data

        user_by_username = User.query.filter_by(username=username).first()
        if user_by_username is not None:
            raise ValidationError('Пользователь с таким именем уже зарегистрирован!')

        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email is not None:
            raise ValidationError('Пользователь с таким email уже зарегистрирован!')

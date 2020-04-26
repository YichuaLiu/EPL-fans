from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already existed")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already existed")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
    remember = BooleanField("Remember")
    submit = SubmitField('Sign In')

class PasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email not exists')

class ResetPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')

class PostForm(FlaskForm):
    text = TextAreaField('Say something...', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Post')

class UplaodForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')

class CompetitionForm(FlaskForm):
    home_team = SelectField('Home_team', validators=[DataRequired()],
                            choices=[(1, 'Arsenal'), (2, 'Burnley'),(3, 'Leicester'),
                                     (4, 'Liverpool'), (5, 'Manchester United'), (6, 'Newcastle United'),
                                     (7, 'Queens Park Rangers'), (8, 'Stoke'), (9, 'West Bromwich Albion'),
                                     (10, 'West Ham'), (11, 'Aston Villa'), (12, 'Chelsea'),
                                     (13, 'Crystal Palace'), (14, 'Everton'), (15, 'Hull'),
                                     (16, 'Manchester City'), (17, 'Southampton'), (18, 'Sunderland'),
                                     (19, 'Swansea'), (20, 'Tottenham'), (21, 'Boumemouth'), (22, 'Norwich'),
                                     (23, 'Watford'), (24, 'Middlesbrough'), (25, 'Brighton'), (26, 'Huddersfield')
    ], coerce=int)
    away_team = SelectField('Away_team',
                            validators=[DataRequired()],
                            choices=[(1, 'Aresenal'), (2, 'Burnley'), (3, 'Leicester'),
                                     (4, 'Liverpool'), (5, 'Mancherster United'), (6, 'Newcastle United'),
                                     (7, 'Queens Park Rangers'), (8, 'Stoke'), (9, 'West Bromwich Albion'),
                                     (10, 'West Ham'), (11, 'Aston Villa'), (12, 'Chelsea'),
                                     (13, 'Crystal Palace'), (14, 'Everton'), (15, 'Hull'),
                                     (16, 'Manchester City'), (17, 'Southampton'), (18, 'Sunderland'),
                                     (19, 'Swansea'), (20, 'Tottenham'), (21, 'Boumenouth'), (22, 'Norwich'),
                                     (23, 'Watford'), (24, 'Middlesbrough'), (25, 'Brighton'), (26, 'Huddersfield')
                                     ], coerce=int)
    submit = SubmitField('Compare')


class ClubForm(FlaskForm):
    club = SelectField('club', validators=[DataRequired()],
                            choices=[(1, 'Arsenal'), (2, 'Burnley'), (3, 'Leicester'),
                                     (4, 'Liverpool'), (5, 'Manchester United'), (6, 'Newcastle United'),
                                     (7, 'Queens Park Rangers'), (8, 'Stoke'), (9, 'West Bromwich Albion'),
                                     (10, 'West Ham'), (11, 'Aston Villa'), (12, 'Chelsea'),
                                     (13, 'Crystal Palace'), (14, 'Everton'), (15, 'Hull'),
                                     (16, 'Manchester City'), (17, 'Southampton'), (18, 'Sunderland'),
                                     (19, 'Swansea'), (20, 'Tottenham'), (21, 'Boumemouth'), (22, 'Norwich'),
                                     (23, 'Watford'), (24, 'Middlesbrough'), (25, 'Brighton'), (26, 'Huddersfield')
                                     ], coerce=int)
    submit = SubmitField('Search')

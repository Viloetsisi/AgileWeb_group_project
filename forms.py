# forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, IntegerField,
    TextAreaField, DateField, FileField, SelectField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.validators import ValidationError

# ------------- Signup -------------
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')

# ------------- Login -------------
class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

# ------------- Forgot Password -------------
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send reset link')

# ------------- Reset Password -------------
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Update password')

# ------------- Profile (Edit Profile) -------------
class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[Optional()])
    birth_date = DateField('Birth Date', format='%Y-%m-%d', validators=[Optional()])
    education = SelectField('Highest Education', choices=[
        ('', 'Choose…'), ('Diploma', 'Diploma'), ('Bachelor', 'Bachelor'), ('Master', 'Master'), ('PhD', 'PhD')
    ], validators=[DataRequired()])
    gpa = SelectField('GPA', choices=[
        ('', 'Choose…'), ('P', 'P'), ('CR', 'CR'), ('D', 'D'), ('HD', 'HD')
    ], validators=[DataRequired()])
    coding_c = BooleanField('C')
    coding_cpp = BooleanField('C++')
    coding_java = BooleanField('Java')
    coding_sql = BooleanField('SQL')
    coding_python = BooleanField('Python')
    communication_skill = SelectField('Communication Skill', choices=[
        ('', 'Choose…'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ], validators=[DataRequired()])
    working_experience = SelectField('Working Experience', choices=[
        ('', 'Choose…'), ('1', '1 year'), ('2', '2 years'), ('3', '3 years'),
        ('4', '4 years'), ('5', '5+ years')
    ], validators=[DataRequired()])
    school = StringField('School / University', validators=[Optional()])
    graduation_date = DateField('Graduation Date', format='%Y-%m-%d', validators=[Optional()])
    career_goal = StringField('Career Goal', validators=[Optional()])
    self_description = TextAreaField('Self Description', validators=[Optional()])
    internship_experience = TextAreaField('Internship Experience', validators=[Optional()])
    is_shared = BooleanField('Make my profile shareable')
    submit = SubmitField('Save Profile')

# ------------- Document Upload -------------
class DocumentUploadForm(FlaskForm):
    data_file = FileField('Upload Document', validators=[DataRequired()])
    submit = SubmitField('Upload Document')

# ------------- Job History -------------
class JobHistoryForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    position = StringField('Position/Role', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    salary = IntegerField('Salary', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Submit')

    def validate_end_date(self, field):
        if field.data and self.start_date.data:
            if field.data < self.start_date.data:
                raise ValidationError('End Date must be later than Start Date.')


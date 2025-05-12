# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

class JobHistoryForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    position = StringField('Position/Role', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    salary = StringField('Salary', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Submit')

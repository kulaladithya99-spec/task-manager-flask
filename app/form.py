from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    priority = SelectField(
        'Priority',
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        validators=[DataRequired()]
    )
    due_date = DateField('Due Date', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Task')
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Length


class NewCourseForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=1, max=30)]
    )
    password = StringField(
        "Password", validators=[DataRequired(), Length(min=8, max=30)]
    )
    submit = SubmitField("Go")

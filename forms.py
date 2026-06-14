from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length


class NewCourseForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=1, max=30)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=32)]
    )
    submit = SubmitField("Go")

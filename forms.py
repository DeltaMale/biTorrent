from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length


class NewCourseForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=1, max=30)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=64)]
    )
    submit = SubmitField("Go")


class MagnetForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    file = FileField("File", validators=[FileRequired()])
    description = TextAreaField("Description (optional)", validators=[Length(max=500)])
    submit = SubmitField("Create Magnet Link")

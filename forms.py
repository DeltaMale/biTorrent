from flask_wtf import FlaskForm
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
    magnet_uri = TextAreaField(
        "Magnet Link", validators=[DataRequired(), Length(max=2000)]
    )
    description = TextAreaField("Description (optional)", validators=[Length(max=500)])
    file_size = StringField("File Size (optional)", validators=[Length(max=20)])
    submit = SubmitField("Share Magnet Link")

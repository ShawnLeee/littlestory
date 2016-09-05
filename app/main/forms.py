from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class PostForm(Form):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')
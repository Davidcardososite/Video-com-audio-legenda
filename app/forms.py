# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class VideoForm(FlaskForm):
    text = StringField(
        'Texto para o Vídeo', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Digite aqui o texto para gerar o vídeo"}
    )


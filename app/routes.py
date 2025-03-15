# routes.py
from flask import Blueprint, render_template, request, send_file, current_app
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from .forms import VideoForm  # Importar o formulário
from transformers import  VitsTokenizer, VitsModel, set_seed
import scipy
import os
import torch
import whisper

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    form = VideoForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            text = form.text.data.strip()

            if not text:
                raise ValueError("O texto não pode estar vazio.")
            # usar gpu ou cpu
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # Defina os caminhos de saída dentro do contexto do aplicativo
            audio_file = os.path.join(current_app.root_path, 'uploads', 'audio.wav')
            video_file = os.path.join(current_app.root_path, 'output', 'video_com_audio_e_legenda.mp4')
            video_path = os.path.join(current_app.root_path, 'uploads', 'video_existente.mp4')


            from app.funcoes import check_create_dir
            # Garantir que os diretórios existam
            check_create_dir(os.path.join(current_app.root_path, 'uploads'))
            check_create_dir(os.path.join(current_app.root_path, 'output'))

            tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-por")
            print(tokenizer.is_uroman)
            model = VitsModel.from_pretrained("facebook/mms-tts-por").to(device)


            # Gera o áudio a partir do texto
            inputs = tokenizer(text=text, return_tensors="pt")

            # tornar determinístico
            set_seed(555)

            # torna a fala mais rápida e barulhenta
            model.speaking_rate = 1.0 
            model.noise_scale = 0.5

            with torch.no_grad():
                outputs = model(**inputs)
            waveform = outputs.waveform[0]
            scipy.io.wavfile.write(audio_file, rate=model.config.sampling_rate, data=waveform.numpy())


            # Carrega o vídeo existente
            video = VideoFileClip(video_path)

            # Carrega o modelo whisper
            model = whisper.load_model("base")

            # carrega o áudio whisper
            load_audio = whisper.load_audio(audio_file)
            result = model.transcribe(load_audio)

            # carrega o áudio 
            audio = AudioFileClip(audio_file)

            # imprime o texto reconhecido
            print(f'texto do áudio: {result["text"]}')

            texto_audio = result["text"]

            # Dividir o texto em palavras
            words = texto_audio.split()

            # Duração por palavra (aqui assumimos 0.5 segundos por palavra, ajustável conforme necessário)
            word_duration = audio.duration / len(words)

            # Criar legendas para cada palavra
            subtitles = []
            start_time = 0
            for word in words:
                end_time = start_time + word_duration
                subtitle = TextClip(word,
                                    font='Impact',# Uso da fonte personalizada
                                    fontsize=70,
                                    color='white',
                                    size=(700, 700),
                                    stroke_color='black',
                                    stroke_width=1,
                                    method='caption',
                                    transparent=True)
                subtitle = subtitle.set_position('bottom').set_start(start_time).set_end(end_time)
                subtitles.append(subtitle)
                start_time = end_time

            # Adiciona transições suaves às legendas
            subtitles = [sub.crossfadein(0.1).crossfadeout(0.1) for sub in subtitles]

            # Combina o áudio com o vídeo existente
            video = video.set_audio(audio)

            # Combina o vídeo com as legendas
            final_video = CompositeVideoClip([video] + subtitles)

            # Salva o vídeo final
            final_video.write_videofile(video_file, fps=24)

            # Retorna o vídeo final para o usuário fazer o download
            return send_file(video_file, as_attachment=True)

        except Exception as e:
             # Mostra mensagem de erro na página
            return render_template('index.html', form=form, error=str(e))

    return render_template('index.html', form=form)

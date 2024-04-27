from docx import Document
import html
from .models import FrequencyAudio
import soundfile as sf
import numpy as np
from pydub import AudioSegment, effects
import os
from django.conf import settings
import uuid

import pdfplumber

def get_languages():
    from iso639 import ALL_LANGUAGES
    language_names = [lang.name for lang in ALL_LANGUAGES]
    return language_names


def get_mostspoken_language():
    return[
        'Assamese', 'Bengali', 'Bodo', 'Dogri', 'English', 'Gujarati', 'Hindi',
        'Kannada', 'Kashmiri', 'Konkani', 'Maithili', 'Malayalam', 'Marathi',
        'Meitei', 'Nepali', 'Odia', 'Punjabi', 'Sanskrit', 'Santali', 'Sindhi',
        'Tamil', 'Telugu', 'Urdu', 'Mandarin Chinese', 'Spanish', 'Arabic',
        'Portuguese', 'Russian', 'Japanese', 'German', 'French', 'Indonesian',
        'Swahili', 'Turkish', 'Korean', 'Italian'
    ]


def get_genres():
    return [
        "Fiction",
        "Non-fiction",
        "Mystery",
        "Thriller",
        "Romance",
        "Science fiction (Sci-Fi)",
        "Fantasy",
        "Horror",
        "Historical fiction",
        "Biography",
        "Autobiography",
        "Self-help",
        "Poetry",
        "Drama",
        "Adventure",
        "Comedy",
        "Action and adventure",
        "Crime and detective",
        "Dystopian",
        "Young adult (YA)"
    ]


def freqeuncy_manipulator(main_audio, frequency):
    resultant_audios = {}

    if str(main_audio).endswith('.mp3'):
        path = f'{main_audio}_converted'
        converted_file_path = os.path.join(settings.MEDIA_ROOT, path + '.wav')
        print(f'main_Audio:{main_audio}')
        print(f'output_file_path : {converted_file_path}')
        try:
            converted_audio = AudioSegment.from_file(main_audio, format='mp3')

        except:
            converted_audio = AudioSegment.from_file(main_audio, format='mp4')

        converted_audio = converted_audio.export(converted_file_path, format="wav")
        print(f'converted audio : {converted_audio}')
        main_audio_instance = AudioSegment.from_file(converted_audio, format="wav")

    else:

        main_audio_instance = AudioSegment.from_file(main_audio, format="wav")

    for keys in frequency:
        bg_freq = frequency[keys]
        output_file = f'{main_audio}_{keys}'

        background_audio = AudioSegment.from_file(bg_freq, format="wav")

        while len(main_audio_instance) > len(background_audio):
            background_audio = background_audio * 2

        if len(main_audio_instance) != len(background_audio):
            bg_freq_audio = background_audio[:len(main_audio_instance)]

        else:

            bg_freq_audio = background_audio

        main_audio_instance_normalized = effects.normalize(main_audio_instance + 25)
        bg_freq_audio_normalized = effects.normalize(bg_freq_audio - 45)

        merged_audio = bg_freq_audio_normalized.overlay(main_audio_instance_normalized, position=0)

        output_file_path = os.path.join(settings.MEDIA_ROOT, output_file + '.wav')

        merged_audio.export(output_file_path, format="wav")

        resultant_audios[keys] = output_file_path

    return resultant_audios


def audio_manipulator(audio):

    frequency = FrequencyAudio.objects.get(id=1)

    frequency_audios = {
        'hz174': frequency.hz174,
        'hz285': frequency.hz285,
        'hz396': frequency.hz396,
        'hz417': frequency.hz417,
        'hz528': frequency.hz528,
        'hz639': frequency.hz639,
        'hz741': frequency.hz741,
        'hz852': frequency.hz852,
        'hz963': frequency.hz963,
    }
    generated_audio = freqeuncy_manipulator(audio,frequency_audios)
    return generated_audio


def convert_to_html(document_path):
    text_content = ""
    _, file_extension = os.path.splitext(document_path)
    if file_extension.lower() == '.pdf':
        # Convert PDF to HTML
        with pdfplumber.open(document_path) as pdf:

            for page in pdf.pages:
                text_content += f"<p>{page.extract_text()}</p>"


        html_content = "".join(text_content)
    elif file_extension.lower() == '.docx':
        # Convert Word document to HTML
        doc = Document(document_path)

        html_content = ""
        for paragraph in doc.paragraphs:

            html_content += f"<p>{paragraph.text}</p>"

    else:
        html_content = "<p>Unsupported file format</p>"

    return doc,html_content


LANGUAGES = get_languages()
MOST_SPOKEN_LANGUAGES = get_mostspoken_language()
GENRES = get_genres()

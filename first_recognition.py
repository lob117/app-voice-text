import speech_recognition as sr
from pydub import AudioSegment
import os

# Ruta del archivo original (puede ser .wav, .mp3, etc.)
audio_file_path = "ejemplo_oficina_mejor.wav"

# Convertir a WAV compatible con speech_recognition
# Necesita ffmpeg instalado y agregado al PATH
audio = AudioSegment.from_wav(audio_file_path)
audio.export("temp_audio.wav", format="wav")

r = sr.Recognizer()
with sr.AudioFile("temp_audio.wav") as source:
    audio_data = r.record(source)  # leer el archivo de audio completo
    try:
        text = r.recognize_google(audio_data, language='es-ES')
        print(text)
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
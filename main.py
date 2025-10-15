import ffmpeg
import openai
from pydub import AudioSegment
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Pocięcie pliku MOV na fragmenty
input_file = "test.mov"
duration_per_chunk = 100  # sekundy

# Pobierz całkowitą długość wideo
probe = ffmpeg.probe(input_file)
total_duration = float(probe['format']['duration'])

num_chunks = int(total_duration // duration_per_chunk) + 1

# wyczyszczenie pliku z transkrypcją
with open("transkrypcja.txt", "w", encoding="utf-8") as f:
    pass

for i in range(num_chunks):
    start_time = i * duration_per_chunk
    wav_file = f"chunk_{i}.wav"
    ffmpeg.input(input_file, ss=start_time, t=duration_per_chunk).output(wav_file).run(overwrite_output=True)

    # Wysyłka fragmentu do Whisper
    with open(wav_file, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        with open("transkrypcja.txt", "a", encoding="utf-8") as f:
            f.write(f"Plik {i}: \n" + transcript.text + "\n\n")



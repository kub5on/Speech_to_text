import streamlit as st
import ffmpeg
import openai
from pathlib import Path
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Transkrypcja superwizji")

# uploaded_file = st.file_uploader("Wybierz plik MOV", type=["mov", "wav"])
# duration_per_chunk = 100  # sekundy
#
# if uploaded_file is not None:
#     # Zapisz plik tymczasowo
#     input_file = Path("temp_input.mov")
#     with open(input_file, "wb") as f:
#         f.write(uploaded_file.read())
#
#     # Wyczyszczenie pliku transkrypcji
#     transcript_file = Path("transkrypcja.txt")
#     transcript_file.write_text("", encoding="utf-8")
#
#     # Pobranie długości wideo
#     probe = ffmpeg.probe(str(input_file))
#     total_duration = float(probe['format']['duration'])
#     num_chunks = int(total_duration // duration_per_chunk) + 1
#
#     full_text = ""
#     progress_bar = st.progress(0)  # inicjalizacja paska postępu
#
#     for i in range(num_chunks):
#         start_time = i * duration_per_chunk
#         wav_file = Path(f"chunk_{i}.wav")
#
#         # Konwersja fragmentu do WAV
#         ffmpeg.input(str(input_file), ss=start_time, t=duration_per_chunk).output(str(wav_file)).run(overwrite_output=True)
#
#         # Wysyłka do Whisper
#         with open(wav_file, "rb") as audio_file:
#             transcript = openai.audio.transcriptions.create(
#                 model="whisper-1",
#                 file=audio_file
#             )
#
#         text = f"Fragment {i}:\n{transcript.text}\n\n"
#         full_text += text
#
#         # Dopisanie do pliku
#         with open(transcript_file, "a", encoding="utf-8") as f:
#             f.write(text)
#
#         # Aktualizacja paska postępu
#         progress_bar.progress((i + 1) / num_chunks)
#
#     st.subheader("Transkrypcja:")
#     st.text(full_text)
#     st.success("Transkrypcja zakończona!")
